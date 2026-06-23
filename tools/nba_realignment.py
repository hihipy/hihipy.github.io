"""Geographic realignment optimizer for the National Basketball Association.

The NBA modeled here is the 32-team league: the 30 current franchises plus the
two presumptive expansion clubs (a returning Seattle SuperSonics and a Las Vegas
team), both Western markets. That makes the conferences uneven, West 17 and East
15, with three divisions each at the real sizes (West 6/6/5, East 5/5/5). Every
lens below is built to respect those uneven sizes rather than forcing an equal
split.

Coordinates, conference, and division for all 32 teams are read from the shared
``teams.json`` so this script, the aggregate solver, and the figure renderer all
draw from a single source.

Alignments (unweighted, total within-division great-circle miles):
    (A) ACTUAL       divisions as really assigned
    (B) CONF_FIXED   best divisions keeping the real conferences, at real sizes
    (C) EAST_WEST    best divisions with no conference constraint, re-split E/W

The conference premium (B - C) is the travel the real conference assignment
costs beyond what redrawing divisions alone can recover. B uses the actual
per-conference division sizes, so it is always well defined; there is no
divisibility fallback.

Schedule-weighted metric (frozen-cross model)
---------------------------------------------
Expected season trip-miles = sum over team pairs of (games that season) x
(distance). Redrawing divisions inside a conference cannot change how often you
play the other conference, so cross games are frozen at the real rate
(2/opponent); only the fixed in-conference budget is split between division
rivals and the rest, at the real division:conference emphasis (4 : 3.6). The
within-division miles are computed on the real uneven divisions; the per-opponent
game rates are taken at a nominal symmetric conference of 16, since with 17/15 a
single per-opponent rate cannot stay symmetric across both conferences. By the
invariance below, that nominal rate only affects which division count is ranked
best, never the partition itself.

Theoretical note. For a fixed conference split, expected trip-miles equal
  g_cross*CROSS + g_conf*CONF + (g_div - g_conf)*DIV,
where CROSS and CONF are fixed and only DIV depends on the division partition.
Since g_div >= g_conf, minimizing expected trip-miles is equivalent to
minimizing within-division distance for ANY weights. One exact partition solve
per division count is globally optimal under every schedule; weights only matter
for comparing counts.

Division-count sweep, steepness curve, min-max equity
-----------------------------------------------------
The sweep holds the real conferences and splits each into k geographically
optimal, near-equal divisions for k = 1..5. The steepness curve re-weights those
precomputed partitions to find the division count that wins at each schedule
emphasis. The min-max objective minimizes the worst team's expected season travel
instead of the league total. If the count verdict is stable across all three, it
is robust.

Output is written into the repo at static/data/.

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
from collections import Counter
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

# --- season schedule emphasis (NBA, verified) ------------------------------
# 4 games vs each division rival; 3.6 avg vs the rest of the conference; 2 vs
# each other-conference team -> 82.
SEASON_GAMES = 82
TIER_RATIO = {"division": 4.0, "conference": 3.6, "cross": 2.0}
STEEPNESS_GRID = [1.0, 1.11, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
# division counts per conference to sweep (real NBA = 3)
DIVISION_COUNTS = [1, 2, 3, 4, 5]
# neighbour-pool width for the full-league optimum, matching the figures pipeline
POOL_K = 16
SETPART_MAX = 200000

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_DATA_DIR = os.path.join(_REPO_ROOT, "static", "data")
TEAMS_JSON = os.path.join(_SCRIPT_DIR, "teams.json")
OUTPUT_JSON = os.path.join(_DATA_DIR, "nba_realignment.json")

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


def load_teams(path: str) -> list[Team]:
    with open(path, encoding="utf-8") as fh:
        nba = json.load(fh)["nba"]
    teams = [Team(name, rec["lat"], rec["lon"], rec["conf"], rec["div"])
             for name, rec in nba.items()]
    names = [t.name for t in teams]
    dupes = {x for x in names if names.count(x) > 1}
    if dupes:
        raise ValueError(f"duplicate names in teams.json: {sorted(dupes)}")
    return teams


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


def near_equal_sizes(m: int, k: int) -> list[int]:
    """Split m teams into k near-equal division sizes (largest first)."""
    base, extra = divmod(m, k)
    return [base + 1] * extra + [base] * (k - extra)


def _new_solver(label):
    solver = pywraplp.Solver.CreateSolver(BACKEND)
    if solver is None:
        raise RuntimeError(f"OR-Tools backend '{BACKEND}' is not available")
    if SOLVER_LOG:
        solver.EnableOutput()
    if TIME_LIMIT_S > 0:
        solver.SetTimeLimit(int(TIME_LIMIT_S * 1000))
    return solver


def _solve_or_die(solver, label):
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        return
    if status == pywraplp.Solver.FEASIBLE:
        log(f"WARNING {label}: feasible but not proven optimal (time limit hit)")
        return
    raise RuntimeError(f"{label}: no solution (status {status})")


def _candidates(members, sizes, distances):
    """All team subsets whose size appears in the requested multiset. For a
    single size that is every combination of that size; for several sizes it is
    their union. Falls back to a nearest-neighbour pool if the full enumeration
    would be too large."""
    members = list(members)
    distinct = sorted(set(sizes))
    total = sum(math.comb(len(members), s) for s in distinct)
    if total <= SETPART_MAX:
        return [g for s in distinct for g in itertools.combinations(members, s)]
    pool = set()
    for seed in members:
        near = sorted((j for j in members if j != seed), key=lambda j: distances[seed][j])[:POOL_K]
        for s in distinct:
            for c in itertools.combinations(near, s - 1):
                pool.add(tuple(sorted((seed,) + c)))
    return [g for g in pool]


def partition(members, sizes, distances, label="partition"):
    """Minimum total within-division distance, partitioning ``members`` into
    divisions whose sizes match the multiset ``sizes`` exactly."""
    members = list(members)
    if len(members) != sum(sizes):
        raise ValueError(f"{label}: {len(members)} teams != sum(sizes) {sum(sizes)}")
    if len(sizes) == 1:
        return [members]
    cand = _candidates(members, sizes, distances)
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
    for s, cnt in Counter(sizes).items():
        solver.Add(solver.Sum(z[k] for k, g in enumerate(cand) if len(g) == s) == cnt)
    solver.Minimize(solver.Sum(cost[k] * z[k] for k in range(len(cand))))
    _solve_or_die(solver, label)
    return [list(cand[k]) for k in range(len(cand)) if z[k].solution_value() > 0.5]


def minmax_partition(members, sizes, distances, base, weight, label="minmax"):
    """Minimize the worst team's total base[i] + weight*(own within-division
    distance), partitioning ``members`` into divisions of the given sizes."""
    members = list(members)
    if len(sizes) == 1:
        return [members], max(base[i] + weight * sum(distances[i][j] for j in members if j != i)
                              for i in members)
    cand = _candidates(members, sizes, distances)
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
    for s, cnt in Counter(sizes).items():
        solver.Add(solver.Sum(z[k] for k, g in enumerate(cand) if len(g) == s) == cnt)
    solver.Minimize(worst)
    _solve_or_die(solver, label)
    divs = [list(cand[k]) for k in range(len(cand)) if z[k].solution_value() > 0.5]
    return divs, worst.solution_value()


def within_group_travel(group, distances):
    return sum(distances[a][b] for a, b in itertools.combinations(group, 2))


def within_division_travel(divisions, distances):
    return sum(within_group_travel(d, distances) for d in divisions)


def centroid_longitude(group, teams):
    return sum(teams[i].lon for i in group) / len(group)


def schedule_games(division_size, conference_size, n_teams, ratio=None):
    """Frozen-cross per-opponent games at a nominal symmetric conference."""
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


def divisions_as_rows(divisions, teams):
    return [[{"name": teams[i].name, "lat": teams[i].lat, "lon": teams[i].lon}
             for i in d] for d in divisions]


def main():
    log(f"Python {platform.python_version()}, OR-Tools {ortools_version()}, {BACKEND}")
    teams = load_teams(TEAMS_JSON)
    n = len(teams)
    distances = distance_matrix(teams)
    nominal_conf = n // 2  # 16; symmetric stand-in for the schedule weighting

    # actual conferences and divisions
    actual_div = {}
    for i, t in enumerate(teams):
        actual_div.setdefault((t.conference, t.division), []).append(i)
    travel_a = within_division_travel(list(actual_div.values()), distances)

    confs = sorted({t.conference for t in teams},
                   key=lambda c: sum(teams[i].lon for i, t in enumerate(teams) if t.conference == c)
                   / sum(1 for t in teams if t.conference == c))
    conf_members = {c: [i for i, t in enumerate(teams) if t.conference == c] for c in confs}
    real_sizes = {c: sorted((len(v) for (cc, d), v in actual_div.items() if cc == c), reverse=True)
                  for c in confs}

    # (B) conference-fixed: keep real conferences, optimize at real sizes
    log("conference-fixed optimum (real sizes)")
    conf_fixed = []
    for c in confs:
        conf_fixed += partition(conf_members[c], real_sizes[c], distances, f"B/{c}")
    travel_b = within_division_travel(conf_fixed, distances)

    # (C) full optimum at the real league division sizes, re-split into two conferences
    log("full league optimum")
    league_sizes = sorted((len(v) for v in actual_div.values()), reverse=True)
    full = partition(list(range(n)), league_sizes, distances, "C/full")
    travel_c = within_division_travel(full, distances)
    full_sorted = sorted(full, key=lambda d: centroid_longitude(d, teams))
    half = len(full_sorted) // 2
    west_opt, east_opt = full_sorted[:half], full_sorted[half:]

    # fixed geometry for the lenses: the real conferences
    west_m, east_m = conf_members[confs[0]], conf_members[confs[1]]
    CONF = within_group_travel(west_m, distances) + within_group_travel(east_m, distances)
    TOTAL = within_group_travel(list(range(n)), distances)
    CROSS = TOTAL - CONF
    league_games = n * SEASON_GAMES / 2.0

    # min-sum partitions and DIV(k) for each division count
    log("sweeping division counts")
    part, DIV = {}, {}
    for k in DIVISION_COUNTS:
        wsz, esz = near_equal_sizes(len(west_m), k), near_equal_sizes(len(east_m), k)
        part[k] = partition(west_m, wsz, distances, f"W/{k}") \
            + partition(east_m, esz, distances, f"E/{k}")
        DIV[k] = within_division_travel(part[k], distances)

    def weighted_total(k, ratio=None):
        gd, gc, gx = schedule_games(nominal_conf / k, nominal_conf, n, ratio)
        return gx * CROSS + gd * DIV[k] + gc * (CONF - DIV[k])

    sweep = []
    for k in DIVISION_COUNTS:
        gd, gc, gx = schedule_games(nominal_conf / k, nominal_conf, n)
        w = weighted_total(k)
        sweep.append({"divisions_per_conference": k,
                      "division_size": round(nominal_conf / k, 2),
                      "unweighted_within_division_mi": round(DIV[k], 1),
                      "expected_trip_mi": round(w, 1),
                      "avg_trip_mi_per_game": round(w / league_games, 2),
                      "games_per_opponent": {"division": round(gd, 2),
                                             "conference": round(gc, 2),
                                             "cross": round(gx, 2)}})
    best = min(sweep, key=lambda r: r["avg_trip_mi_per_game"])
    for r in sweep:
        r["most_efficient"] = (r is best)
    lo = min(r["avg_trip_mi_per_game"] for r in sweep)
    hi = max(r["avg_trip_mi_per_game"] for r in sweep)
    sweep_spread = (hi - lo) / lo * 100

    # steepness robustness (re-weight precomputed partitions; no solving)
    log("steepness robustness curve")
    steepness = []
    real_ratio = TIER_RATIO["division"] / TIER_RATIO["conference"]
    for r in STEEPNESS_GRID:
        vals = {k: weighted_total(k, r) for k in DIVISION_COUNTS}
        rlo, rhi = min(vals.values()), max(vals.values())
        bk = min(DIVISION_COUNTS, key=lambda k: vals[k])
        steepness.append({"ratio": r,
                          "optimal_divisions_per_conference": bk,
                          "spread_pct": round((rhi - rlo) / rlo * 100, 2),
                          "indifferent": (rhi - rlo) / rlo * 100 < 0.05,
                          "is_real_ratio": abs(r - real_ratio) < 0.01})

    # min-max equity sweep
    log("min-max equity sweep")
    minmax = []
    for k in DIVISION_COUNTS:
        gd, gc, gx = schedule_games(nominal_conf / k, nominal_conf, n)
        w = gd - gc
        base = {}
        for mem, other in ((west_m, east_m), (east_m, west_m)):
            for i in mem:
                base[i] = gx * sum(distances[i][j] for j in other) \
                    + gc * sum(distances[i][j] for j in mem if j != i)
        wsz, esz = near_equal_sizes(len(west_m), k), near_equal_sizes(len(east_m), k)
        _, tw = minmax_partition(west_m, wsz, distances, base, w, f"mmW/{k}")
        _, te = minmax_partition(east_m, esz, distances, base, w, f"mmE/{k}")
        minmax.append({"divisions_per_conference": k, "worst_team_trip_mi": round(max(tw, te), 1)})
    mm_best = min(minmax, key=lambda r: r["worst_team_trip_mi"])
    for r in minmax:
        r["most_equitable"] = (r is mm_best)

    premium = travel_b - travel_c
    verdict = ("division count is essentially irrelevant"
               if sweep_spread < 2 else "division count materially affects travel")

    # ---------------- report ----------------
    print("\n" + "=" * 72)
    print(f"NBA realignment   ({n} teams: West {len(west_m)}, East {len(east_m)})")
    print("=" * 72)
    for label, t in (("(A) actual", travel_a), ("(B) conferences kept", travel_b),
                     ("(C) full east-west", travel_c)):
        rec = (travel_a - t) / travel_a * 100
        tail = "" if label.startswith("(A)") else f"   recovers {rec:4.1f}%"
        print(f"  {label:<22}{t:>9,.0f} mi (unweighted){tail}")
    print(f"\n  conference premium (B - C): {premium:,.0f} mi "
          f"({premium / travel_a * 100:.1f}% of actual)\n")
    print("Schedule-weighted sweep (real ratio, cross frozen):")
    for r in sweep:
        f = "  <- most efficient" if r["most_efficient"] else ""
        print(f"   {r['divisions_per_conference']} div/conf"
              f"   {r['avg_trip_mi_per_game']:>8.2f} avg trip/game{f}")
    print(f"   spread across counts: {sweep_spread:.2f}%\n")
    print(f"  VERDICT: {verdict} (weighted spread {sweep_spread:.2f}%); "
          f"min-sum best = {best['divisions_per_conference']} div/conf, "
          f"min-max best = {mm_best['divisions_per_conference']} div/conf.")

    if OUTPUT_JSON:
        os.makedirs(_DATA_DIR, exist_ok=True)
        ws = sorted(west_opt, key=lambda d: centroid_longitude(d, teams))
        es = sorted(east_opt, key=lambda d: centroid_longitude(d, teams))
        result = {
            "league": "NBA",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "ortools_version": ortools_version(),
            "teams": n,
            "division_size": 5,
            "division_sizes": {confs[0]: real_sizes[confs[0]], confs[1]: real_sizes[confs[1]]},
            "structure": (f"two uneven conferences ({confs[0]} {len(west_m)}, {confs[1]} {len(east_m)}) "
                          "including the Seattle and Las Vegas expansion clubs; three divisions each"),
            "metric": "total within-division great-circle miles",
            "alignments": {
                "actual": {"travel_mi": round(travel_a, 1)},
                "conference_fixed": {"travel_mi": round(travel_b, 1),
                                     "recovered_pct": round((travel_a - travel_b) / travel_a * 100, 1),
                                     "well_defined": True},
                "east_west": {"travel_mi": round(travel_c, 1),
                              "recovered_pct": round((travel_a - travel_c) / travel_a * 100, 1)},
            },
            "conference_premium_mi": round(premium, 1),
            "conference_premium_pct": round(premium / travel_a * 100, 1),
            "schedule": {"season_games": SEASON_GAMES, "tier_ratio_per_opponent": TIER_RATIO,
                         "model": "frozen-cross",
                         "weighted_metric": "expected season trip-miles = sum over team pairs of games*distance",
                         "nominal_conference_note": (f"per-opponent game rates use a nominal symmetric "
                                                     f"conference of {nominal_conf}; within-division miles use "
                                                     "the real uneven divisions"),
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