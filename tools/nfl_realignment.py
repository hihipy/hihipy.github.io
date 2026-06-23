"""Geographic realignment optimizer for the National Football League.

Same three-lens method as the NBA and MLB scripts. The NFL is the third
non-geographic-conference league: AFC and NFC are historical, so honoring them
carries a real travel premium, but the 17-game schedule is the steepest in
sports per opponent (2 division games vs 0.5 conference games), which makes
division structure consequential.

Alignments (unweighted, total within-division great-circle miles):
    (A) ACTUAL       real AFC/NFC conferences and divisions
    (B) CONF_FIXED   best divisions keeping the current AFC/NFC conferences
    (C) EAST_WEST    best alignment with no conference constraint (geographic)

(B) - (C) is the conference premium: travel locked in purely by the AFC/NFC
boundary.

Schedule-weighted metric (frozen-cross model)
---------------------------------------------
Expected season trip-miles = sum over team pairs of (games that season) x
(distance). Redrawing divisions inside a conference cannot change how often you
play the other conference, so interconference games are frozen at the real rate
(0.3125/opp, i.e. 5 games spread over 16 opponents); only the fixed
in-conference budget is split between division rivals and the rest of the
conference, in the real division:conference ratio (2.0 : 0.5 = 4.0). The
comparison statistic is average trip-miles per game.

Theoretical note, steepness robustness curve, and min-max equity objective are
all exactly as in the NBA script; see that file's header for the rationale.

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

# --- season schedule emphasis (NFL 17-game formula, verified) --------------
# 6 division games (3 rivals x 2); 6 same-conference non-division games (one
# full division of 4, plus 2 standings-based) over 12 opponents -> 0.5/opp;
# 5 interconference games (one full division of 4, plus the 17th game) over 16
# opponents -> 0.3125/opp. 6 + 6 + 5 = 17.
SEASON_GAMES = 17
TIER_RATIO = {"division": 2.0, "conference": 0.5, "cross": 0.3125}
# Base division:conference emphasis grid; the league's true ratio (4.0) is
# auto-inserted. Extended upward to capture the NFL's steep regime.
STEEPNESS_GRID = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_DATA_DIR = os.path.join(_REPO_ROOT, "static", "data")
OUTPUT_JSON = os.path.join(_DATA_DIR, "nfl_realignment.json")

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
    conference: str
    division: str


# 32 teams with current stadium coordinates. Co-located pairs are real: Rams and
# Chargers share SoFi Stadium; Jets and Giants share MetLife (identical coords).
TEAMS: list[Team] = [
    Team("Bills", 42.774, -78.787, "AFC", "East"),
    Team("Dolphins", 25.958, -80.239, "AFC", "East"),
    Team("Jets", 40.814, -74.074, "AFC", "East"),
    Team("Patriots", 42.091, -71.264, "AFC", "East"),
    Team("Bengals", 39.095, -84.516, "AFC", "North"),
    Team("Browns", 41.506, -81.7, "AFC", "North"),
    Team("Ravens", 39.278, -76.623, "AFC", "North"),
    Team("Steelers", 40.447, -80.016, "AFC", "North"),
    Team("Colts", 39.76, -86.164, "AFC", "South"),
    Team("Jaguars", 30.324, -81.637, "AFC", "South"),
    Team("Texans", 29.685, -95.411, "AFC", "South"),
    Team("Titans", 36.166, -86.771, "AFC", "South"),
    Team("Broncos", 39.744, -105.02, "AFC", "West"),
    Team("Chargers", 33.953, -118.339, "AFC", "West"),
    Team("Chiefs", 39.049, -94.484, "AFC", "West"),
    Team("Raiders", 36.091, -115.184, "AFC", "West"),
    Team("Commanders", 38.908, -76.864, "NFC", "East"),
    Team("Cowboys", 32.748, -97.093, "NFC", "East"),
    Team("Eagles", 39.901, -75.168, "NFC", "East"),
    Team("Giants", 40.814, -74.074, "NFC", "East"),
    Team("Bears", 41.862, -87.617, "NFC", "North"),
    Team("Lions", 42.34, -83.046, "NFC", "North"),
    Team("Packers", 44.501, -88.062, "NFC", "North"),
    Team("Vikings", 44.974, -93.258, "NFC", "North"),
    Team("Buccaneers", 27.976, -82.503, "NFC", "South"),
    Team("Falcons", 33.755, -84.401, "NFC", "South"),
    Team("Panthers", 35.226, -80.853, "NFC", "South"),
    Team("Saints", 29.951, -90.081, "NFC", "South"),
    Team("49ers", 37.403, -121.97, "NFC", "West"),
    Team("Cardinals", 33.528, -112.263, "NFC", "West"),
    Team("Rams", 33.953, -118.339, "NFC", "West"),
    Team("Seahawks", 47.595, -122.332, "NFC", "West"),
]

DIVISION_SIZE = 4


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


def optimal_divisions(members, group_size, distances, label="divisions"):
    """Minimum total within-division distance, exact (set-partition ILP)."""
    members = list(members)
    n = len(members)
    if n % group_size != 0:
        raise ValueError(f"{label}: {n} not divisible by {group_size}")
    if group_size == n:
        return [members]
    cand = list(itertools.combinations(members, group_size))
    cost = [sum(round(distances[a][b] * DISTANCE_SCALE)
                for a, b in itertools.combinations(g, 2)) for g in cand]
    solver = _new_solver(label)
    z = [solver.BoolVar(f"z_{k}") for k in range(len(cand))]
    cover = {i: [] for i in members}
    for k, g in enumerate(cand):
        for i in g:
            cover[i].append(z[k])
    for i in members:
        solver.Add(solver.Sum(cover[i]) == 1)
    solver.Minimize(solver.Sum(cost[k] * z[k] for k in range(len(cand))))
    if solver.Solve() not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise RuntimeError(f"{label}: no solution")
    return [list(cand[k]) for k in range(len(cand)) if z[k].solution_value() > 0.5]


def minmax_divisions(members, group_size, distances, base, weight, label="minmax"):
    """Minimize the worst team's total: base[i] + weight * (own within-division
    distance). ``base`` is each team's fixed travel (cross + non-division
    conference); only the division tier is chosen here."""
    members = list(members)
    n = len(members)
    if group_size == n:
        return [members]
    cand = list(itertools.combinations(members, group_size))
    selfcost = {(k, i): sum(distances[i][j] for j in g if j != i)
                for k, g in enumerate(cand) for i in g}
    solver = _new_solver(label)
    z = [solver.BoolVar(f"z_{k}") for k in range(len(cand))]
    worst = solver.NumVar(0.0, solver.infinity(), "worst")
    cover = {i: [] for i in members}
    for k, g in enumerate(cand):
        for i in g:
            cover[i].append(z[k])
    for i in members:
        solver.Add(solver.Sum(cover[i]) == 1)
        solver.Add(base[i] + weight * solver.Sum(
            selfcost[(k, i)] * z[k] for k, g in enumerate(cand) if i in g) <= worst)
    solver.Minimize(worst)
    if solver.Solve() not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise RuntimeError(f"{label}: no solution")
    divs = [list(cand[k]) for k in range(len(cand)) if z[k].solution_value() > 0.5]
    return divs, worst.solution_value()


def within_group_travel(group, distances):
    return sum(distances[a][b] for a, b in itertools.combinations(group, 2))


def within_division_travel(divisions, distances):
    return sum(within_group_travel(d, distances) for d in divisions)


def centroid_longitude(group, teams):
    return sum(teams[i].lon for i in group) / len(group)


def split_into_conferences(divisions, teams):
    ordered = sorted(divisions, key=lambda d: centroid_longitude(d, teams))
    half = len(ordered) // 2
    return ordered[:half], ordered[half:]


def schedule_games(division_size, conference_size, n_teams, ratio=None):
    """Frozen-cross per-opponent games. ``ratio`` overrides the division:
    conference emphasis (defaults to the real value)."""
    if ratio is None:
        ratio = TIER_RATIO["division"] / TIER_RATIO["conference"]
    g_cross = TIER_RATIO["cross"]
    inconf_budget = SEASON_GAMES - (n_teams - conference_size) * g_cross
    n_div = division_size - 1
    n_conf = conference_size - division_size
    if n_conf <= 0:
        return (inconf_budget / n_div if n_div else 0.0), 0.0, g_cross
    g_conf = inconf_budget / (n_div * ratio + n_conf)
    return ratio * g_conf, g_conf, g_cross


def validate_teams(teams, division_size):
    if len(teams) % division_size != 0:
        raise ValueError(f"{len(teams)} teams not divisible by {division_size}")
    names = [t.name for t in teams]
    dupes = {x for x in names if names.count(x) > 1}
    if dupes:
        raise ValueError(f"duplicate names: {sorted(dupes)}")


def divisions_as_rows(divisions, teams):
    return [[{"name": teams[i].name, "lat": teams[i].lat, "lon": teams[i].lon}
             for i in d] for d in divisions]


def main():
    log(f"Python {platform.python_version()}, OR-Tools {ortools_version()}, {BACKEND}")
    teams = TEAMS
    validate_teams(teams, DIVISION_SIZE)
    n = len(teams)
    distances = distance_matrix(teams)

    # (A) actual
    actual = {}
    for i, t in enumerate(teams):
        actual.setdefault((t.conference, t.division), []).append(i)
    travel_a = within_division_travel(list(actual.values()), distances)

    # (B) conference-fixed where divisible (AFC and NFC are both 16 -> 4 divisions)
    conf_fixed, conf_fixed_defined = [], True
    for conf in sorted({t.conference for t in teams}):
        members = [i for i, t in enumerate(teams) if t.conference == conf]
        if len(members) % DIVISION_SIZE:
            conf_fixed_defined = False
            continue
        conf_fixed += optimal_divisions(members, DIVISION_SIZE, distances, f"{conf}")

    # (C) full optimum, split into geographic conferences
    log("full league optimum")
    optimal = optimal_divisions(list(range(n)), DIVISION_SIZE, distances, "full")
    travel_c = within_division_travel(optimal, distances)
    west, east = split_into_conferences(optimal, teams)
    travel_b = within_division_travel(conf_fixed, distances) if conf_fixed_defined else travel_c

    # fixed geometry for the sweeps
    west_m = [i for d in west for i in d]
    east_m = [i for d in east for i in d]
    conf_size = len(west_m)
    TOTAL = within_group_travel(list(range(n)), distances)
    CONF = within_group_travel(west_m, distances) + within_group_travel(east_m, distances)
    CROSS = TOTAL - CONF
    league_games = n * SEASON_GAMES / 2.0
    feasible = [s for s in range(2, conf_size + 1) if conf_size % s == 0]
    real_ratio = TIER_RATIO["division"] / TIER_RATIO["conference"]

    # min-sum partitions and DIV(s) for each division size
    log("sweeping division counts")
    part, DIV = {}, {}
    for s in feasible:
        part[s] = optimal_divisions(west_m, s, distances, f"W/{s}") \
            + optimal_divisions(east_m, s, distances, f"E/{s}")
        DIV[s] = within_division_travel(part[s], distances)

    def weighted_total(s, ratio=None):
        gd, gc, gx = schedule_games(s, conf_size, n, ratio)
        return gx * CROSS + gd * DIV[s] + gc * (CONF - DIV[s])

    # primary schedule-weighted sweep (real ratio)
    sweep = []
    for s in feasible:
        gd, gc, gx = schedule_games(s, conf_size, n)
        w = weighted_total(s)
        sweep.append({"divisions_per_conference": conf_size // s, "division_size": s,
                      "unweighted_within_division_mi": round(DIV[s], 1),
                      "expected_trip_mi": round(w, 1),
                      "avg_trip_mi_per_game": round(w / league_games, 2),
                      "games_per_opponent": {"division": round(gd, 2),
                                             "conference": round(gc, 2), "cross": round(gx, 2)}})
    best = min(sweep, key=lambda r: r["avg_trip_mi_per_game"])
    for r in sweep:
        r["most_efficient"] = (r is best)
    sweep_spread = (max(r["avg_trip_mi_per_game"] for r in sweep)
                    - min(r["avg_trip_mi_per_game"] for r in sweep)) \
        / min(r["avg_trip_mi_per_game"] for r in sweep) * 100

    # steepness robustness curve
    log("steepness robustness curve")
    grid = sorted(set(STEEPNESS_GRID) | {round(real_ratio, 4)})
    steepness = []
    for r in grid:
        vals = {s: weighted_total(s, r) for s in feasible}
        lo, hi = min(vals.values()), max(vals.values())
        bs = min(feasible, key=lambda s: vals[s])
        spread = (hi - lo) / lo * 100
        steepness.append({"ratio": r,
                          "optimal_divisions_per_conference": conf_size // bs,
                          "optimal_division_size": bs,
                          "spread_pct": round(spread, 2),
                          "indifferent": spread < 0.05,
                          "is_real_ratio": abs(r - real_ratio) < 1e-3})

    # min-max equity sweep
    log("min-max equity sweep")
    minmax = []
    for s in feasible:
        gd, gc, gx = schedule_games(s, conf_size, n)
        w = gd - gc
        base = {}
        for mem, other in ((west_m, east_m), (east_m, west_m)):
            for i in mem:
                base[i] = gx * sum(distances[i][j] for j in other) \
                    + gc * sum(distances[i][j] for j in mem if j != i)
        if s == conf_size:
            worst = max(base[i] + w * sum(distances[i][j] for j in (west_m if i in west_m else east_m) if j != i)
                        for i in range(n))
        else:
            _, tw = minmax_divisions(west_m, s, distances, base, w, f"mmW/{s}")
            _, te = minmax_divisions(east_m, s, distances, base, w, f"mmE/{s}")
            worst = max(tw, te)
        minmax.append({"divisions_per_conference": conf_size // s, "division_size": s,
                       "worst_team_trip_mi": round(worst, 1)})
    mm_best = min(minmax, key=lambda r: r["worst_team_trip_mi"])
    for r in minmax:
        r["most_equitable"] = (r is mm_best)

    # ---------------- report ----------------
    print("\n" + "=" * 72)
    print(f"NFL realignment   ({n} teams, canonical divisions of {DIVISION_SIZE})")
    print("=" * 72)
    for label, t in (("(A) actual", travel_a), ("(B) conferences kept", travel_b),
                     ("(C) full geographic", travel_c)):
        rec = (travel_a - t) / travel_a * 100
        tail = "" if label.startswith("(A)") else f"   recovers {rec:4.1f}%"
        print(f"  {label:<22}{t:>9,.0f} mi (unweighted){tail}")
    print(f"\n  conference premium (B - C): {travel_b - travel_c:,.0f} mi "
          f"({(travel_b - travel_c) / travel_a * 100:.1f}% of actual) "
          f"-- travel locked in by the AFC/NFC boundary\n")

    print("Schedule-weighted sweep (real ratio, interconference frozen):")
    for r in sweep:
        f = "  <- most efficient" if r["most_efficient"] else ""
        print(f"   {r['divisions_per_conference']:>2} div/conf (size {r['division_size']:>2})"
              f"   {r['avg_trip_mi_per_game']:>8.2f} avg trip/game{f}")
    print(f"   spread across counts: {sweep_spread:.2f}%\n")

    print("Steepness robustness (optimal division count vs schedule ratio):")
    for r in steepness:
        tag = "  [real]" if r["is_real_ratio"] else ""
        ind = "  indifferent" if r["indifferent"] else ""
        print(f"   r={r['ratio']:>5.3f} -> {r['optimal_divisions_per_conference']} div/conf "
              f"(spread {r['spread_pct']:.2f}%){ind}{tag}")
    print()
    print("Min-max equity sweep (worst team's expected season trip-miles):")
    for r in minmax:
        f = "  <- most equitable" if r["most_equitable"] else ""
        print(f"   {r['divisions_per_conference']:>2} div/conf (size {r['division_size']:>2})"
              f"   {r['worst_team_trip_mi']:>10,.0f}{f}")

    verdict = ("division count is essentially irrelevant"
               if sweep_spread < 2 else "division count materially affects travel")
    print(f"\n  VERDICT: {verdict} (weighted spread {sweep_spread:.2f}%); "
          f"min-sum best = {best['divisions_per_conference']} div/conf, "
          f"min-max best = {mm_best['divisions_per_conference']} div/conf.\n")

    print("Optimal geographic alignment (westernmost first):")
    for lbl, half in (("WEST", west), ("EAST", east)):
        print(f"  {lbl}")
        for d in sorted(half, key=lambda d: centroid_longitude(d, teams)):
            print("    " + ", ".join(sorted(teams[i].name for i in d)))

    if OUTPUT_JSON:
        os.makedirs(_DATA_DIR, exist_ok=True)
        ws = sorted(west, key=lambda d: centroid_longitude(d, teams))
        es = sorted(east, key=lambda d: centroid_longitude(d, teams))
        result = {
            "league": "NFL",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "ortools_version": ortools_version(),
            "teams": n,
            "division_size": DIVISION_SIZE,
            "metric": "total within-division great-circle miles",
            "alignments": {
                "actual": {"travel_mi": round(travel_a, 1)},
                "conference_fixed": {"travel_mi": round(travel_b, 1),
                                     "recovered_pct": round((travel_a - travel_b) / travel_a * 100, 1),
                                     "well_defined": conf_fixed_defined},
                "east_west": {"travel_mi": round(travel_c, 1),
                              "recovered_pct": round((travel_a - travel_c) / travel_a * 100, 1)},
            },
            "conference_premium_mi": round(travel_b - travel_c, 1),
            "conference_premium_pct": round((travel_b - travel_c) / travel_a * 100, 1),
            "schedule": {"season_games": SEASON_GAMES, "tier_ratio_per_opponent": TIER_RATIO,
                         "model": "frozen-cross",
                         "weighted_metric": "expected season trip-miles = sum over team pairs of games*distance",
                         "invariance_note": ("for a fixed conference split the minimum-weighted-travel "
                                             "partition equals the minimum within-division-distance "
                                             "partition for any weights; weights only affect the "
                                             "cross-count comparison")},
            "division_sweep": sweep,
            "division_sweep_spread_pct": round(sweep_spread, 2),
            "steepness_robustness": steepness,
            "minmax_equity_sweep": minmax,
            "conclusions": {
                "min_sum_optimal_divisions_per_conference": best["divisions_per_conference"],
                "min_max_optimal_divisions_per_conference": mm_best["divisions_per_conference"],
                "weighted_spread_pct": round(sweep_spread, 2),
                "verdict": verdict,
            },
            "optimal_east_west": {"west": divisions_as_rows(ws, teams),
                                  "east": divisions_as_rows(es, teams)},
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