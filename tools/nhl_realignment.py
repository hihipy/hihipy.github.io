"""Geographic realignment optimizer for the National Hockey League.

Same three-lens method as the NBA, MLB, and NFL scripts, with one engine
change forced by the NHL's structure. NHL divisions hold 8 teams, so the
full-league optimum would enumerate C(32,8) ~ 10.5 million candidate divisions,
which is intractable. This script instead solves an exact pairwise
clique-partition ILP: a binary same[i][j] for every pair (do i and j share a
division), transitivity constraints to force clean groups, and a degree
constraint to fix the size. That has C(n,2) variables, not C(n,8), and returns
the same global optimum.

Unlike the AL/NL and AFC/NFC, the NHL's Eastern and Western conferences are
genuinely geographic, so the conference premium is expected to be near zero, and
the 82-game schedule is shallow per opponent (3.71 division vs 3.0 conference),
so division count should matter little. This is the NBA's flat-null twin, the
counterweight to MLB and the NFL.

Alignments (unweighted, total within-division great-circle miles):
    (A) ACTUAL       real conferences and divisions
    (B) CONF_FIXED   best divisions keeping the current conferences intact
    (C) EAST_WEST    best alignment with no conference constraint

Schedule-weighted metric (frozen-cross model), the steepness robustness curve,
the min-max equity objective, and the partition-invariance theorem are all as in
the NBA script; see that file's header for the rationale.

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
TIME_LIMIT_S = 600   # the full-league size-8 clique partition is the heavy solve

# --- season schedule emphasis (NHL 82-game format, verified) ---------------
# 26 division games over 7 opponents (3.71/opp: four vs five rivals, three vs
# two); 24 intra-conference non-division games over 8 opponents (3.0/opp); 32
# interconference games over 16 opponents (2.0/opp). 26 + 24 + 32 = 82.
SEASON_GAMES = 82
TIER_RATIO = {"division": 3.71, "conference": 3.0, "cross": 2.0}
# Base division:conference emphasis grid; the league's true ratio (~1.237) is
# auto-inserted.
STEEPNESS_GRID = [1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_DATA_DIR = os.path.join(_REPO_ROOT, "static", "data")
OUTPUT_JSON = os.path.join(_DATA_DIR, "nhl_realignment.json")

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
    conference: str   # East / West
    division: str


# 32 teams with current arena coordinates (Utah Mammoth in the Central).
TEAMS: list[Team] = [
    Team("Bruins", 42.366, -71.062, "East", "Atlantic"),
    Team("Canadiens", 45.496, -73.569, "East", "Atlantic"),
    Team("Lightning", 27.943, -82.452, "East", "Atlantic"),
    Team("Maple Leafs", 43.643, -79.379, "East", "Atlantic"),
    Team("Panthers", 26.158, -80.326, "East", "Atlantic"),
    Team("Red Wings", 42.341, -83.055, "East", "Atlantic"),
    Team("Sabres", 42.875, -78.876, "East", "Atlantic"),
    Team("Senators", 45.297, -75.927, "East", "Atlantic"),
    Team("Blue Jackets", 39.969, -83.006, "East", "Metropolitan"),
    Team("Capitals", 38.898, -77.021, "East", "Metropolitan"),
    Team("Devils", 40.734, -74.171, "East", "Metropolitan"),
    Team("Flyers", 39.901, -75.172, "East", "Metropolitan"),
    Team("Hurricanes", 35.803, -78.722, "East", "Metropolitan"),
    Team("Islanders", 40.711, -73.723, "East", "Metropolitan"),
    Team("Penguins", 40.439, -79.989, "East", "Metropolitan"),
    Team("Rangers", 40.75, -73.993, "East", "Metropolitan"),
    Team("Avalanche", 39.749, -105.008, "West", "Central"),
    Team("Blackhawks", 41.881, -87.674, "West", "Central"),
    Team("Blues", 38.627, -90.203, "West", "Central"),
    Team("Jets", 49.893, -97.144, "West", "Central"),
    Team("Mammoth", 40.768, -111.901, "West", "Central"),
    Team("Predators", 36.159, -86.778, "West", "Central"),
    Team("Stars", 32.79, -96.81, "West", "Central"),
    Team("Wild", 44.945, -93.101, "West", "Central"),
    Team("Canucks", 49.278, -123.109, "West", "Pacific"),
    Team("Ducks", 33.808, -117.877, "West", "Pacific"),
    Team("Flames", 51.038, -114.052, "West", "Pacific"),
    Team("Golden Knights", 36.103, -115.178, "West", "Pacific"),
    Team("Kings", 34.043, -118.267, "West", "Pacific"),
    Team("Kraken", 47.622, -122.354, "West", "Pacific"),
    Team("Oilers", 53.547, -113.498, "West", "Pacific"),
    Team("Sharks", 37.333, -121.901, "West", "Pacific"),
]

DIVISION_SIZE = 8


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


def _build_clique_model(members, group_size, label):
    """Pairwise clique-partition model: same[a][b] = do local teams a,b share a
    division. Transitivity makes it an equivalence relation; the degree
    constraint forces every division to hold exactly ``group_size`` teams."""
    solver = _new_solver(label)
    m = len(members)
    same = {}
    for a in range(m):
        for b in range(a + 1, m):
            same[(a, b)] = solver.BoolVar(f"s_{a}_{b}")

    def sm(a, b):
        return same[(a, b)] if a < b else same[(b, a)]

    for a in range(m):
        solver.Add(solver.Sum(sm(a, b) for b in range(m) if b != a) == group_size - 1)
    for a in range(m):
        for b in range(a + 1, m):
            for c in range(b + 1, m):
                solver.Add(sm(a, b) + sm(b, c) - sm(a, c) <= 1)
                solver.Add(sm(a, b) + sm(a, c) - sm(b, c) <= 1)
                solver.Add(sm(a, c) + sm(b, c) - sm(a, b) <= 1)
    return solver, same, sm


def _recover_groups(members, same):
    m = len(members)
    adj = {a: set() for a in range(m)}
    for (a, b), v in same.items():
        if v.solution_value() > 0.5:
            adj[a].add(b)
            adj[b].add(a)
    seen, groups = set(), []
    for a in range(m):
        if a in seen:
            continue
        comp = {a} | adj[a]
        seen |= comp
        groups.append([members[i] for i in sorted(comp)])
    return groups


def optimal_divisions(members, group_size, distances, label="divisions"):
    """Minimum total within-division distance, exact, via the pairwise clique-
    partition ILP (C(n,2) variables rather than C(n,8) candidate divisions)."""
    members = list(members)
    m = len(members)
    if m % group_size != 0:
        raise ValueError(f"{label}: {m} not divisible by {group_size}")
    if group_size == m:
        return [members]
    solver, same, _ = _build_clique_model(members, group_size, label)
    solver.Minimize(solver.Sum(
        round(distances[members[a]][members[b]] * DISTANCE_SCALE) * same[(a, b)]
        for a in range(m) for b in range(a + 1, m)))
    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise RuntimeError(f"{label}: no solution")
    if status != pywraplp.Solver.OPTIMAL:
        log(f"{label}: WARNING optimality not proven; raise TIME_LIMIT_S")
    return _recover_groups(members, same)


def minmax_divisions(members, group_size, distances, base, weight, label="minmax"):
    """Minimize the worst team's total: base[i] + weight * (own within-division
    distance). Same clique-partition engine as optimal_divisions."""
    members = list(members)
    m = len(members)
    if group_size == m:
        return [members], None
    solver, same, sm = _build_clique_model(members, group_size, label)
    worst = solver.NumVar(0.0, solver.infinity(), "worst")
    for a in range(m):
        solver.Add(base[members[a]] + weight * solver.Sum(
            distances[members[a]][members[b]] * sm(a, b) for b in range(m) if b != a) <= worst)
    solver.Minimize(worst)
    if solver.Solve() not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise RuntimeError(f"{label}: no solution")
    return _recover_groups(members, same), worst.solution_value()


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

    # (B) conference-fixed where divisible (East and West are both 16 -> 2 divisions)
    conf_fixed, conf_fixed_defined = [], True
    for conf in sorted({t.conference for t in teams}):
        members = [i for i, t in enumerate(teams) if t.conference == conf]
        if len(members) % DIVISION_SIZE:
            conf_fixed_defined = False
            continue
        conf_fixed += optimal_divisions(members, DIVISION_SIZE, distances, f"{conf}")

    # (C) full optimum, split into geographic conferences
    log("full league optimum (32 teams, divisions of 8; clique partition)")
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
    print(f"NHL realignment   ({n} teams, canonical divisions of {DIVISION_SIZE})")
    print("=" * 72)
    for label, t in (("(A) actual", travel_a), ("(B) conferences kept", travel_b),
                     ("(C) full geographic", travel_c)):
        rec = (travel_a - t) / travel_a * 100
        tail = "" if label.startswith("(A)") else f"   recovers {rec:4.1f}%"
        print(f"  {label:<22}{t:>9,.0f} mi (unweighted){tail}")
    print(f"\n  conference premium (B - C): {travel_b - travel_c:,.0f} mi "
          f"({(travel_b - travel_c) / travel_a * 100:.1f}% of actual) "
          f"-- the Eastern/Western boundary is already geographic\n")

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
            "league": "NHL",
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