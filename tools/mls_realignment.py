"""Geographic realignment optimizer for Major League Soccer.

MLS is the structural outlier in this series: 30 clubs in two conferences of 15
with NO sub-divisions. With only one structural tier, the division-count sweep
and steepness curve from the other four scripts do not apply, there is nothing
to count. The live questions are how good the current East/West split is and
whether an equity objective would draw the line differently.

Because the only structure is the conference boundary itself, the right model is
a balanced two-way partition (balanced max-cut): split the 30 clubs into two
groups of 15 that minimize total within-conference distance, equivalently
maximize the cross-conference cut. No transitivity constraints are needed (a
two-way split is automatically a valid partition), so this is leaner than the
clique-partition used for the NHL.

Alignments (unweighted, total within-conference great-circle miles):
    (A) ACTUAL    real Eastern/Western conferences
    (C) OPTIMAL   best balanced 15/15 split

The conference-assignment premium (A - C) is how much travel the current
conference assignment costs versus the optimal balanced split. For MLS this is
the headline number; there is no division layer beneath it.

Schedule-weighted metric. Each club plays its 14 conference opponents twice
(2.0/opponent) and six of the 15 cross-conference clubs once (0.4/opponent
averaged). Expected season trip-miles = 2.0*CONF + 0.4*CROSS. Since the
conference rate exceeds the cross rate, the weighted-optimal split is identical
to the distance-optimal split; the weighting only scales magnitude.

Min-max equity objective. A second, genuinely different optimization: minimize
the worst club's expected season travel rather than the league total. If it
draws the same line as the aggregate optimum, the split is robust across
objectives.

Output is written directly into the repo at static/data/.

Requires Python 3.9+ and ortools (``pip install ortools``); CBC ships inside it.
"""

from __future__ import annotations

import datetime
import itertools
import json
import math
import os
import platform
import sys
import time
from dataclasses import dataclass

try:
    from ortools.linear_solver import pywraplp
except ModuleNotFoundError:
    sys.exit(
        "ortools is not installed in THIS interpreter.\n"
        "Install it into the same Python that runs this file:\n"
        "    python -m pip install ortools"
    )

EARTH_RADIUS_MI = 3958.8
DISTANCE_SCALE = 1
BACKEND = "CBC"
SOLVER_LOG = False
TIME_LIMIT_S = 300

# --- season schedule emphasis (MLS 2025 format, verified) ------------------
# 34 games: 14 conference opponents twice (28, so 2.0/opp); six of the 15
# cross-conference clubs once (6, so 0.4/opp averaged over all cross clubs).
SEASON_GAMES = 34
CONFERENCE_SIZE = 15
TIER_GAMES = {"conference": 2.0, "cross": 0.4}

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_DATA_DIR = os.path.join(_REPO_ROOT, "static", "data")
OUTPUT_JSON = os.path.join(_DATA_DIR, "mls_realignment.json")

_START = time.perf_counter()


def log(message: str) -> None:
    print(f"[{time.perf_counter() - _START:6.1f}s] {message}", flush=True)


def ortools_version() -> str:
    try:
        import ortools
        return getattr(ortools, "__version__", "unknown")
    except Exception:  # noqa: BLE001
        return "unknown"


@dataclass(frozen=True)
class Team:
    name: str
    lat: float
    lon: float
    conference: str   # East / West (no division tier in MLS)


# 30 clubs with current venue coordinates (three Canadian clubs: Toronto and
# Montreal in the East, Vancouver in the West).
TEAMS: list[Team] = [
    Team("Atlanta United", 33.755, -84.401, "East"),
    Team("CF Montreal", 45.563, -73.552, "East"),
    Team("Charlotte FC", 35.226, -80.853, "East"),
    Team("Chicago Fire", 41.862, -87.617, "East"),
    Team("Columbus Crew", 39.969, -83.017, "East"),
    Team("DC United", 38.868, -77.013, "East"),
    Team("FC Cincinnati", 39.111, -84.522, "East"),
    Team("Inter Miami", 26.193, -80.161, "East"),
    Team("NY Red Bulls", 40.737, -74.15, "East"),
    Team("NYCFC", 40.829, -73.926, "East"),
    Team("Nashville SC", 36.131, -86.766, "East"),
    Team("New England", 42.091, -71.264, "East"),
    Team("Orlando City", 28.541, -81.389, "East"),
    Team("Philadelphia Union", 39.832, -75.378, "East"),
    Team("Toronto FC", 43.633, -79.418, "East"),
    Team("Austin FC", 30.388, -97.719, "West"),
    Team("Colorado Rapids", 39.806, -104.892, "West"),
    Team("FC Dallas", 33.155, -96.835, "West"),
    Team("Houston Dynamo", 29.752, -95.352, "West"),
    Team("LA Galaxy", 33.864, -118.261, "West"),
    Team("LAFC", 34.013, -118.285, "West"),
    Team("Minnesota United", 44.953, -93.165, "West"),
    Team("Portland Timbers", 45.522, -122.692, "West"),
    Team("Real Salt Lake", 40.583, -111.893, "West"),
    Team("San Diego FC", 32.783, -117.119, "West"),
    Team("San Jose", 37.351, -121.925, "West"),
    Team("Seattle Sounders", 47.595, -122.332, "West"),
    Team("Sporting KC", 39.121, -94.824, "West"),
    Team("St. Louis City", 38.629, -90.211, "West"),
    Team("Vancouver", 49.277, -123.112, "West"),
]


def haversine_miles(a: Team, b: Team) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a.lat, a.lon, b.lat, b.lon))
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    h = (math.sin(d_lat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2)
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(h))


def distance_matrix(teams):
    n = len(teams)
    return [[haversine_miles(teams[i], teams[j]) for j in range(n)] for i in range(n)]


def _new_solver(label):
    solver = pywraplp.Solver.CreateSolver(BACKEND)
    if solver is None:
        raise RuntimeError(f"OR-Tools backend '{BACKEND}' is not available")
    if SOLVER_LOG:
        solver.EnableOutput()
    if TIME_LIMIT_S > 0:
        solver.SetTimeLimit(int(TIME_LIMIT_S * 1000))
    return solver


def balanced_partition(distances, n, group_size, objective="minsum",
                       g_conf=None, g_cross=None, label="partition"):
    """Split n teams into two groups, one of exactly ``group_size``, via balanced
    max-cut. minsum maximizes cross-conference distance (= minimizes within-
    conference distance). minmax minimizes the worst team's weighted travel."""
    solver = _new_solver(label)
    x = [solver.BoolVar(f"x_{i}") for i in range(n)]   # 1 = West group
    cut = {}
    for i in range(n):
        for j in range(i + 1, n):
            c = solver.BoolVar(f"c_{i}_{j}")
            solver.Add(c <= x[i] + x[j])
            solver.Add(c <= 2 - x[i] - x[j])
            solver.Add(c >= x[i] - x[j])
            solver.Add(c >= x[j] - x[i])
            cut[(i, j)] = c
    solver.Add(solver.Sum(x) == group_size)

    def cut_ij(i, j):
        return cut[(i, j)] if i < j else cut[(j, i)]

    if objective == "minsum":
        solver.Maximize(solver.Sum(round(distances[i][j] * DISTANCE_SCALE) * cut[(i, j)]
                                   for i in range(n) for j in range(i + 1, n)))
    else:  # minmax: weighted_i = g_conf*all_i - (g_conf-g_cross)*cross_i
        worst = solver.NumVar(0.0, solver.infinity(), "worst")
        w = g_conf - g_cross
        for i in range(n):
            all_i = sum(distances[i][j] for j in range(n) if j != i)
            cross_i = solver.Sum(distances[i][j] * cut_ij(i, j) for j in range(n) if j != i)
            solver.Add(g_conf * all_i - w * cross_i <= worst)
        solver.Minimize(worst)

    if solver.Solve() not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise RuntimeError(f"{label}: no solution")
    west = [i for i in range(n) if x[i].solution_value() > 0.5]
    east = [i for i in range(n) if x[i].solution_value() <= 0.5]
    return west, east


def within_group_travel(group, distances):
    return sum(distances[a][b] for a, b in itertools.combinations(group, 2))


def centroid_longitude(group, teams):
    return sum(teams[i].lon for i in group) / len(group)


def weighted_trip_miles(groups, distances, total):
    conf = sum(within_group_travel(g, distances) for g in groups)
    cross = total - conf
    return TIER_GAMES["conference"] * conf + TIER_GAMES["cross"] * cross


def worst_team_weighted(groups, distances, n):
    member_of = {i: g for g in groups for i in g}
    gc, gx = TIER_GAMES["conference"], TIER_GAMES["cross"]
    out = 0.0
    for i in range(n):
        within = sum(distances[i][j] for j in member_of[i] if j != i)
        cross = sum(distances[i][j] for j in range(n) if j != i) - within
        out = max(out, gc * within + gx * cross)
    return out


def rows(group, teams):
    return [{"name": teams[i].name, "lat": teams[i].lat, "lon": teams[i].lon} for i in group]


def main():
    log(f"Python {platform.python_version()}, OR-Tools {ortools_version()}, {BACKEND}")
    teams = TEAMS
    n = len(teams)
    if n != 2 * CONFERENCE_SIZE:
        raise ValueError(f"expected {2 * CONFERENCE_SIZE} teams, got {n}")
    distances = distance_matrix(teams)
    total = within_group_travel(list(range(n)), distances)
    league_games = n * SEASON_GAMES / 2.0
    gc, gx = TIER_GAMES["conference"], TIER_GAMES["cross"]

    # (A) actual conferences
    actual = {}
    for i, t in enumerate(teams):
        actual.setdefault(t.conference, []).append(i)
    actual_groups = list(actual.values())
    travel_a = sum(within_group_travel(g, distances) for g in actual_groups)

    # (C) optimal balanced split (min-sum)
    log("optimal balanced split (min-sum, balanced max-cut)")
    cw, ce = balanced_partition(distances, n, CONFERENCE_SIZE, "minsum", label="minsum")
    opt_groups = [cw, ce]
    travel_c = sum(within_group_travel(g, distances) for g in opt_groups)

    # min-max equity split
    log("min-max equity split")
    mw, me = balanced_partition(distances, n, CONFERENCE_SIZE, "minmax", gc, gx, "minmax")
    mm_groups = [mw, me]

    # which clubs the optimal split moves vs the current assignment
    actual_west = set(teams[i].name for i in (actual.get("West") or []))
    opt_by_lon = sorted(opt_groups, key=lambda g: centroid_longitude(g, teams))
    opt_west = set(teams[i].name for i in opt_by_lon[0])
    moved = sorted(actual_west ^ opt_west)

    premium = travel_a - travel_c
    ms_worst = worst_team_weighted(opt_groups, distances, n)
    mm_worst = worst_team_weighted(mm_groups, distances, n)

    # ---------------- report ----------------
    print("\n" + "=" * 72)
    print(f"MLS realignment   ({n} clubs, two conferences of {CONFERENCE_SIZE}, no divisions)")
    print("=" * 72)
    print(f"  (A) actual conferences  : {travel_a:9,.0f} mi within-conference")
    print(f"  (C) optimal 15/15 split : {travel_c:9,.0f} mi within-conference"
          f"   recovers {premium / travel_a * 100:4.1f}%")
    print(f"\n  conference-assignment premium (A - C): {premium:,.0f} mi "
          f"({premium / travel_a * 100:.1f}% of actual)")
    if not moved:
        print("  the current Eastern/Western split is already the optimal balanced partition.\n")
    else:
        print(f"  clubs the optimum reassigns: {', '.join(moved)}\n")

    print("Schedule-weighted travel (conference 2.0 / cross 0.4 per opponent):")
    print(f"  actual  : {weighted_trip_miles(actual_groups, distances, total) / league_games:7.2f} avg trip-miles/game")
    print(f"  optimal : {weighted_trip_miles(opt_groups, distances, total) / league_games:7.2f} avg trip-miles/game\n")

    print("Min-max equity (worst club's expected season trip-miles):")
    print(f"  min-sum optimal split : {ms_worst:9,.0f}")
    print(f"  min-max optimal split : {mm_worst:9,.0f}   "
          f"({(ms_worst - mm_worst) / ms_worst * 100:.1f}% better for the worst club)\n")

    print("Lenses not applicable: division-count sweep and steepness curve need a")
    print("division tier; MLS has only the conference tier.\n")

    print("Optimal conferences (westernmost first):")
    for g in opt_by_lon:
        print("  " + ", ".join(sorted(teams[i].name for i in g)))

    if OUTPUT_JSON:
        os.makedirs(_DATA_DIR, exist_ok=True)
        west_sorted = opt_by_lon[0]
        east_sorted = opt_by_lon[1]
        result = {
            "league": "MLS",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "ortools_version": ortools_version(),
            "teams": n,
            "structure": "two conferences of 15, no sub-divisions",
            "metric": "total within-conference great-circle miles",
            "alignments": {
                "actual": {"within_conference_mi": round(travel_a, 1)},
                "optimal": {"within_conference_mi": round(travel_c, 1),
                            "recovered_pct": round(premium / travel_a * 100, 1)},
            },
            "conference_assignment_premium_mi": round(premium, 1),
            "conference_assignment_premium_pct": round(premium / travel_a * 100, 1),
            "current_split_is_optimal": (not moved),
            "clubs_reassigned_by_optimum": moved,
            "schedule": {"season_games": SEASON_GAMES, "tier_games_per_opponent": TIER_GAMES,
                         "weighted_metric": "expected season trip-miles = sum over team pairs of games*distance",
                         "note": ("conference opponents twice (2.0/opp), six of fifteen cross-conference "
                                  "clubs once (0.4/opp averaged); no division tier")},
            "weighted": {
                "actual_avg_trip_mi_per_game": round(weighted_trip_miles(actual_groups, distances, total) / league_games, 2),
                "optimal_avg_trip_mi_per_game": round(weighted_trip_miles(opt_groups, distances, total) / league_games, 2),
            },
            "minmax_equity": {
                "min_sum_worst_team_mi": round(ms_worst, 1),
                "min_max_worst_team_mi": round(mm_worst, 1),
                "worst_team_improvement_pct": round((ms_worst - mm_worst) / ms_worst * 100, 2),
            },
            "lenses_not_applicable": ("division-count sweep and steepness curve require a division "
                                      "tier; MLS has only the conference tier"),
            "optimal_east_west": {"west": rows(west_sorted, teams), "east": rows(east_sorted, teams)},
        }
        with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        log(f"wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        log(f"FAILED: {type(error).__name__}: {error}")
        raise