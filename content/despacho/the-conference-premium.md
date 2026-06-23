---
title: "The Conference Premium"
weight: 30
description: "Five major leagues sorted into conferences and divisions, scored by integer programming against the geographic optimum, to measure how many miles each league spends honoring a conference boundary that was drawn for history rather than distance."
summary: "The travel cost of conferences"
tags: ["data-essay", "sports", "optimization", "operations-research", "combinatorics", "python", "data-visualization"]
showDate: false
showReadingTime: true
showAuthor: false
showTableOfContents: true
---

{{< katex >}}

{{< lead >}}
The conference premium is the travel a league spends honoring a conference line that geography would not have drawn. Here is what each of five major leagues pays.
{{< /lead >}}

> **TL;DR.** The conference premium is the share of a league's in-division travel that exists only because of where it drew its conference line, the miles it could erase by ignoring that line and regrouping its teams on geography alone. To put a number on it, score three versions of each league by total within-division great-circle miles: the actual league \( A \), the same conferences with the divisions redrawn \( B \), and a free geographic redraw \( C \). The premium is \( (B - C)/A \). Baseball pays 28.87% and football 19.66%, because their conferences are boundaries kept from a rival-league merger, not maps. The NBA, the NHL, and MLS pay 0.00%, because their conferences already are the map, or there is no division layer beneath them to redraw. The premium tracks one piece of history: whether a league that merged with a rival kept the old line as a brand or dissolved it into geography. The exception proves it. Add two western expansion clubs to the NBA, unbalancing a conference geography had balanced, and a 9.07% premium appears out of nowhere.

***

<style>
  .cp-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0; }
  @media (max-width: 768px) { .cp-kpis { grid-template-columns: repeat(2, 1fr); } }
  .cp-kpi { border: 1px solid #d0d7de; border-radius: 8px; padding: 1.25rem; }
  html.dark .cp-kpi { border-color: #30363d; }
  .cp-kpi-value { font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; margin: 0; font-variant-numeric: tabular-nums; }
  .cp-kpi-label { font-size: 0.85rem; opacity: 0.75; margin: 0.5rem 0 0; }
  .cp-kpi-sub { font-size: 0.75rem; opacity: 0.6; font-style: italic; margin: 0.25rem 0 0; }
  table { width: fit-content !important; max-width: 100% !important; margin-left: auto !important; margin-right: auto !important; }
  table th, table td { text-align: center !important; }
</style>

<div class="cp-kpis">
<div class="cp-kpi">
<p class="cp-kpi-value">28.87%</p>
<p class="cp-kpi-label">MLB conference premium</p>
<p class="cp-kpi-sub">The steepest bill</p>
</div>
<div class="cp-kpi">
<p class="cp-kpi-value">19.66%</p>
<p class="cp-kpi-label">NFL conference premium</p>
<p class="cp-kpi-sub">History over geography</p>
</div>
<div class="cp-kpi">
<p class="cp-kpi-value">4 of 5</p>
<p class="cp-kpi-label">Merged with a rival league</p>
<p class="cp-kpi-sub">Only the two that kept the old line still pay</p>
</div>
<div class="cp-kpi">
<p class="cp-kpi-value">9.07%</p>
<p class="cp-kpi-label">NBA expansion what-if</p>
<p class="cp-kpi-sub">Adding Seattle and Las Vegas</p>
</div>
</div>

Every major North American league sorts its teams the same way. First into two conferences, then into divisions inside each conference, and a team plays its own division far more than anyone else. That nesting has a price measured in miles. A team locked into the wrong half of the country flies past closer rivals to reach the ones it is scheduled against. The question here is narrow and answerable: of all the travel a league spends inside its divisions, how much is the cost of where it drew the conference line, and how much is the unavoidable cost of geography? That first part is what this essay calls the conference premium: the travel a league could erase by forgetting its conference line and grouping teams on geography alone. It runs from nearly a third of all in-division miles down to zero, and which end a league lands on turns out to be a question of history.

## The Scoreboard

| League | Actual In-Division Travel (Mi) | Recovered By Reseeding Divisions | Recovered By The Full Optimum | Conference Premium |
| --- | ---: | ---: | ---: | ---: |
| MLB | 35,727.63 | 1.39% | 30.26% | 28.87% |
| NFL | 27,324.58 | 16.57% | 36.23% | 19.66% |
| NBA[^nbarow] | 25,571.22 | 2.61% | 2.61% | 0.00% |
| NHL | 68,797.66 | 5.92% | 5.92% | 0.00% |
| MLS | 168,085.75 | 0.00% | 0.00% | 0.00% |

> *A boundary drawn for a league merger in 1970, or a rival circuit that folded a century ago, still routes a team's bus today. The premium is the fare.*

The rest of this essay builds that number one step at a time, then walks each league with its own maps, top of the table to bottom.

## How the Number Is Built

The method climbs in four steps, each one plain first and then exact.

**Step one: what a division costs.** Start as simply as possible. A division's travel cost is the total distance between the teams in it. A division whose teams all sit near each other is cheap; one stretched across the country is expensive. Add that up over every division and you have the league's score, where lower is tighter. Written out, with the set of divisions called \( \mathcal{P} \),

\[ \mathrm{DIV}(\mathcal{P}) = \sum_{D \in \mathcal{P}} \; \sum_{\{i, j\} \subseteq D} d_{ij} \]

- \( \mathcal{P} \): one way of splitting the teams into divisions
- \( D \): a single division within that split
- \( d_{ij} \): the distance between teams \( i \) and \( j \)
- \( \mathrm{DIV}(\mathcal{P}) \): the league's score, every teammate pair's distance added up

The only ingredient is \( d_{ij} \), the distance between two teams, taken as the great-circle distance across the surface of the earth rather than a straight line on a flat map. The haversine formula gives it from latitude \( \phi \) and longitude \( \lambda \):

\[ d_{ij} = 2R \arcsin\sqrt{\sin^2\!\frac{\phi_j - \phi_i}{2} + \cos\phi_i \cos\phi_j \sin^2\!\frac{\lambda_j - \lambda_i}{2}} \]

- \( R \): the earth's radius, 3,958.8 miles
- \( \phi_i, \phi_j \): the two teams' latitudes
- \( \lambda_i, \lambda_j \): the two teams' longitudes
- \( d_{ij} \): the great-circle distance the formula returns

with \( R = 3{,}958.8 \) miles. Every pairwise distance is computed once into a matrix, so scoring any partition is a sum of lookups:

```python
def haversine_miles(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a.lat, a.lon, b.lat, b.lon))
    d_lat, d_lon = lat2 - lat1, lon2 - lon1
    h = (math.sin(d_lat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2)
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(h))

def distance_matrix(teams):
    idx = list(teams)
    return {a: {b: haversine_miles(teams[a], teams[b]) for b in idx}
            for a in idx}
```

**Step two: drawing the best divisions.** The easiest way to picture this is brute force: list every way to sort the teams into groups of the right sizes, score each arrangement, and keep the cheapest. That is the answer we want; the catch is that the number of arrangements explodes, so a solver finds the same answer without trying all of them, and proves it found the best. The model is a set-partition. Treat every group of teams of an allowed size as a candidate division with a cost equal to its own within-group travel, \( c_g = \sum_{\{i,j\} \subseteq g} d_{ij} \), then pick a set of candidates that covers every team exactly once and costs the least. With a yes-or-no variable \( z_g \in \{0,1\} \) for whether candidate \( g \) is chosen,

\[ \min_{z} \; \sum_{g} c_g \, z_g \quad \text{subject to} \quad \sum_{g \ni i} z_g = 1 \;\; \forall i, \qquad \sum_{g : |g| = s} z_g = n_s \;\; \forall s \]

- \( g \): a candidate division, any group of teams of an allowed size
- \( c_g \): that group's own within-group distance
- \( z_g \): 1 if the group is chosen as a division, 0 if not
- first constraint: every team \( i \) sits in exactly one chosen division
- second constraint: the chosen divisions match the league's shape, \( n_s \) of them at each size \( s \)

The first constraint is the partition: every team in exactly one chosen division. The second fixes the shape, exactly \( n_s \) divisions of each size \( s \), so the model matches a league whose divisions are not all the same size.

```python
def partition(members, sizes, distances):
    cand = [g for s in set(sizes)
              for g in itertools.combinations(members, s)]
    cost = [sum(distances[a][b] for a, b in itertools.combinations(g, 2))
            for g in cand]
    solver = pywraplp.Solver.CreateSolver("CBC")
    z = [solver.BoolVar(f"z_{k}") for k in range(len(cand))]
    for i in members:                                  # cover: one division each
        solver.Add(sum(z[k] for k, g in enumerate(cand) if i in g) == 1)
    for s, n_s in Counter(sizes).items():              # shape: n_s divisions of size s
        solver.Add(sum(z[k] for k, g in enumerate(cand) if len(g) == s) == n_s)
    solver.Minimize(sum(cost[k] * z[k] for k in range(len(cand))))
    solver.Solve()
    return [cand[k] for k in range(len(cand)) if z[k].solution_value() > 0.5]
```

For a conference of fifteen or sixteen teams the candidate list is small enough to enumerate in full, so the result is exact. For the whole league at once the count is too large, so the same program runs over a candidate set restricted to each team's nearest neighbors, which keeps the partition optimal against a strong field.

**Step three: three versions of each league.** Score each league three ways. \( A \) is the league as it stands today. \( B \) keeps the real conferences but redraws the divisions inside them for minimum travel, at the real sizes. \( C \) throws out the conference line, redraws every division across the whole league, then splits the result back into two halves by longitude. The conference premium is how much worse the conference-bound best is than the free best, against what the league spends now:

\[ \mathrm{premium} = \frac{B - C}{A}, \qquad \mathrm{recover}_B = \frac{A - B}{A}, \qquad \mathrm{recover}_C = \frac{A - C}{A} \]

- \( A \): the actual divisions' within-division distance
- \( B \): the same conferences, divisions redrawn for least travel
- \( C \): the free redraw with the conference line erased
- \( \mathrm{premium} \): the gap \( B - C \) as a share of \( A \); \( \mathrm{recover}_B \) and \( \mathrm{recover}_C \) are how much each redraw saves

If a league's conferences are nothing but a clean east and west cut, \( B \) and \( C \) land together and the premium is zero. If the conferences follow some other logic, the premium is what that logic costs.

**Step four: the schedule does not change the answer.** Teams play division rivals most, so it is fair to worry the best partition by raw distance is not the best by miles flown. It is the same partition. Let \( g_\bullet, g_\circ, g_\times \) be games per opponent against a division rival, a non-division conference team, and a cross-conference team, and group the season's pair-distances into \( \mathrm{DIV} \), \( \mathrm{CONF} \), and \( \mathrm{CROSS} \). Season trip-miles are

\[ W = g_\bullet \, \mathrm{DIV} + g_\circ (\mathrm{CONF} - \mathrm{DIV}) + g_\times \, \mathrm{CROSS} = g_\times \, \mathrm{CROSS} + g_\circ \, \mathrm{CONF} + (g_\bullet - g_\circ)\, \mathrm{DIV} \]

- \( \mathrm{DIV}, \mathrm{CONF}, \mathrm{CROSS} \): season distance against division, conference, and cross-conference opponents
- \( g_\bullet, g_\circ, g_\times \): games played per division, conference, and cross-conference opponent
- \( W \): total season trip-miles; rearranged, only the \( \mathrm{DIV} \) term moves with the partition

For a fixed conference split, \( \mathrm{CROSS} \) and \( \mathrm{CONF} \) are constants, so only \( \mathrm{DIV} \) moves with the partition. Since \( g_\bullet \ge g_\circ \), minimizing \( W \) is the same as minimizing \( \mathrm{DIV} \), for any schedule at all. This argument holds the conference split fixed, so it licenses the conferences-kept redraw \( B \) directly; the premium's other half, the free optimum \( C \), erases the conference line, so it is treated as a pure-distance construct with no schedule attached, and the premium compares distance against distance throughout. The weighting only matters when comparing how finely to divide, through the frozen-cross rates:

\[ g_\circ = \frac{S - (n - c)\,g_\times}{(s - 1)\,\rho + (c - s)}, \qquad g_\bullet = \rho \, g_\circ \]

- \( S \): total games on the schedule
- \( n, c, s \): teams in the league, in a conference, and in a division
- \( \rho \): how many times more a team plays division rivals than other conference teams
- \( g_\circ, g_\bullet \): the per-opponent conference and division game counts these fix

```python
def schedule_games(division_size, conference_size, n_teams, ratio):
    g_cross = 2.0
    inconf_budget = SEASON_GAMES - (n_teams - conference_size) * g_cross
    n_div  = division_size - 1                  # division rivals
    n_conf = conference_size - division_size     # other conference teams
    g_conf = inconf_budget / (n_div * ratio + n_conf)
    g_div  = ratio * g_conf
    return g_div, g_conf, g_cross
```

With the method in hand, the walk goes top of the scoreboard to bottom, one league at a time, each map followed by what it shows: the current divisions, the same conferences with the divisions redrawn, and the full geographic optimum.

## MLB, the Steepest Bill

Start with the league as it stands: thirty teams, two leagues, three divisions each, the divisions cut so close rivals share one.

{{< realign league="mlb" panel="A" >}}

These are the actual divisions, and they cost 35,727.63 miles of within-division travel, the figure every later map is measured against. The clusters look tidy because the American and National Leagues are each already a compact set of teams; whatever slack exists is inside them, in how the divisions are drawn.

Every division has a geographic heart, the average position of its teams. Reverse-geocode that point and you land on a real, usually very small American town. Here is the center of each current division, with 2020 Census populations.

| Division | Center | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| AL East | Croom, Maryland | 2,720 | The Croom Crows | A rural crossroads of tobacco barns and woodlots in Prince George's County, near Mount Calvert, the county seat before 1792, on the Patuxent River. |
| AL Central | Addison, Illinois | 35,702 | The Addison Aviators | A Chicago suburb on Salt Creek that was farmland until the 1960s and once home to the Adventureland amusement park. |
| AL West | Chinle, Arizona | 4,573 | The Chinle Canyoneers | A Navajo Nation community and the gateway to Canyon de Chelly, a national monument that sits entirely on tribal land. |
| NL East | Spring Hope, North Carolina | 1,309 | The Spring Hope Pumpkins | A Nash County town that throws the National Pumpkin Festival every autumn. |
| NL Central | Grissom Air Reserve Base, Indiana | 3,009 | The Grissom Bombers | A former Strategic Air Command bomber field named for the Hoosier astronaut Gus Grissom, now home to the largest KC-135 tanker wing in the Air Force Reserve. |
| NL West | Boulder City, Nevada | 14,885 | The Boulder City Hardhats | Built from nothing by the federal government in the 1930s to house the men pouring Hoover Dam, and one of only two places in Nevada where casino gambling is illegal. |

In plain terms, the solver tries every legal way to cut the teams into divisions of the right size and keeps the one with the least total within-division distance. Keeping the leagues means re-cutting each fifteen into three fives; dropping them means re-cutting all thirty into six:

\[ B:\ 15 \to 3 \times 5 \ \text{per league} \qquad C:\ 30 \to 6 \times 5 \]

- \( B \): keep the two leagues, cut each 15-team league into 3 divisions of 5
- \( C \): drop the league line, cut all 30 teams into 6 divisions of 5

{{< realign league="mlb" panel="B" >}}

Keep the two leagues exactly as they are and redraw only the divisions inside them, and almost nothing moves. The two West divisions do not change at all; the only shuffling is between East and Central, where the Braves slide over to sit with the four Central clubs and the Pirates cross the other way, with the Rays and Guardians making the mirror-image swap in the American League. That is the whole difference, and it recovers a rounding error, 1.39%, because each league is already locally tight.

And the hearts of those same divisions once the conferences are kept but the lines inside them are redrawn for least travel:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Boulder City, Nevada | Diamondbacks, Dodgers, Giants, Padres, Rockies | 14,885 | The Boulder City Hardhats | Built from nothing by the federal government in the 1930s to house the men pouring Hoover Dam, and one of only two places in Nevada where casino gambling is illegal. |
| Middlebury, Indiana | Braves, Brewers, Cardinals, Cubs, Reds | 3,466 | The Middlebury Buggies | A northern Indiana town in Amish country and the heart of the state's recreational-vehicle building corridor. |
| Prince George, Virginia | Marlins, Mets, Nationals, Phillies, Pirates | 2,315 | The Prince George Quartermasters | A county seat just east of Petersburg, next to the Army's logistics post at Fort Gregg-Adams. |
| Chinle, Arizona | Angels, Astros, Athletics, Mariners, Rangers | 4,573 | The Chinle Canyoneers | A Navajo Nation community and the gateway to Canyon de Chelly, a national monument that sits entirely on tribal land. |
| Greenup, Illinois | Rays, Royals, Tigers, Twins, White Sox | 1,365 | The Greenup Porchmen | A Cumberland County village on the old National Road, nicknamed the Village of Porches for its covered wooden sidewalks. |
| Laporte, Pennsylvania | Blue Jays, Guardians, Orioles, Red Sox, Yankees | 314 | The Laporte Loggers | The tiny seat of Sullivan County, perched high on the Allegheny Plateau in the Endless Mountains, among the smallest county seats in the state. |

{{< realign league="mlb" panel="C" >}}

Now erase the American and National line and redraw across all thirty teams, and every single division turns mixed. The Yankees, Red Sox, and Orioles share a group with the Mets and Phillies; the Dodgers and Giants join the Angels and Athletics; geography pays no attention to which league a team plays in. Travel drops 30.26%, and the gap between that and the 1.39% above is the premium: 28.87%, the steepest bill in the study. Almost the entire cost is the league line itself.

That gap, as a share of the actual travel:

\[ \text{premium} = \frac{B - C}{A} = \frac{35{,}232.75 - 24{,}916.65}{35{,}727.63} = 28.87\% \]

- \( A = 35{,}727.63 \): the actual divisions' within-division miles
- \( B = 35{,}232.75 \): conferences kept, divisions redrawn
- \( C = 24{,}916.65 \): conference line erased, free redraw
- \( (B - C)/A \): the gap as a share of actual travel, the premium

And once the conference line is erased and every division is drawn from scratch:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Rosamond, California | Angels, Athletics, Dodgers, Giants, Padres | 20,961 | The Rosamond Test Pilots | A Mojave Desert town in the Antelope Valley beside Edwards Air Force Base and its dry lakebeds. |
| Laramie, Wyoming | Diamondbacks, Mariners, Rockies, Royals, Twins | 31,407 | The Laramie Cowboys | A high-plains railroad town between the Laramie and Snowy ranges, home to the University of Wyoming. |
| Dauphin Island, Alabama | Astros, Braves, Marlins, Rangers, Rays | 1,778 | The Dauphin Island Mariners | A barrier island at the mouth of Mobile Bay, guarded by the brick ramparts of Fort Gaines and lined by a long fishing pier. |
| Sheldon, Illinois | Brewers, Cardinals, Cubs, Reds, White Sox | 965 | The Sheldon Threshers | A small village in Iroquois County in the flat grain country of eastern Illinois. |
| Stoneboro, Pennsylvania | Blue Jays, Guardians, Nationals, Pirates, Tigers | 946 | The Stoneboro Fairgoers | A small Mercer County borough known for its long-running Stoneboro Fair. |
| Bayonne, New Jersey | Mets, Orioles, Phillies, Red Sox, Yankees | 71,686 | The Bayonne Bridgemen | A peninsula city wedged between Newark Bay and New York Bay, known for its oil terminals and the steel arch of the Bayonne Bridge to Staten Island. |

The reason is history, not geography. The National League dates to 1876 and the American League to 1901, and the two ran as separate businesses for nearly a century before merging into a single organization in 2000.[^mlb] The split down the middle of the sport was never about longitude, and the 162-game season multiplies every extra mile. Division count matters too: across one to three divisions per conference the travel swings 6.61%, and the optimum lands on three, which is what the league already runs.

## NFL, History Over Geography

Football runs eight divisions across thirty-two teams. The first map is the league as it plays today.

{{< realign league="nfl" panel="A" >}}

The actual divisions cost 27,324.58 miles. The four-team groups are looser than baseball's, with several that reach across a time zone, so there is real slack to recover here before the conference line even comes up.

The center of each division, with its 2020 Census population:

| Division | Center | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| AFC East | Crisfield, Maryland | 2,475 | The Crisfield Crabbers | The self-styled Crab Capital of the World out on Tangier Sound, with parts of the town built on a foundation of discarded oyster shells from its packing-house heyday. |
| AFC North | Martins Ferry, Ohio | 6,260 | The Martins Ferry Ferrymen | The oldest European settlement in Ohio, sitting on the Ohio River across from Wheeling. |
| AFC South | Carbon Hill, Alabama | 1,769 | The Carbon Hill Coalers | A Walker County coal town that incorporated on Valentine's Day and hoped to be known as the Village of Love and Luck. |
| AFC West | Mancos, Colorado | 1,196 | The Mancos Mustangs | A small ranching town in the southwest corner of Colorado, just up the road from Mesa Verde. |
| NFC East | Rainelle, West Virginia | 1,190 | The Rainelle Lumberjacks | Once home to the largest hardwood mill on earth, and still home to the world's largest building made entirely of American chestnut. |
| NFC North | Newburg, Wisconsin | 1,142 | The Newburg Holsteins | A mill village on the Milwaukee River in the heart of Wisconsin dairy country. |
| NFC South | Dawson, Georgia | 4,414 | The Dawson Goobers | A market town in the southwest Georgia peanut belt, where goober is the old word for peanut, and the birthplace of Otis Redding. |
| NFC West | Hawthorne, Nevada | 3,118 | The Hawthorne Detonators | A desert town all but surrounded by the Hawthorne Army Depot, one of the largest ammunition stores in the world. |

The same idea on a looser grid. With conferences kept, each sixteen is re-cut into four fours; with the line gone, all thirty-two into eight fours:

\[ B:\ 16 \to 4 \times 4 \ \text{per conference} \qquad C:\ 32 \to 8 \times 4 \]

- \( B \): keep the two conferences, cut each 16-team conference into 4 divisions of 4
- \( C \): drop the conference line, cut all 32 teams into 8 divisions of 4

{{< realign league="nfl" panel="B" >}}

Hold the AFC and NFC fixed and redraw their divisions, and the loose four-team groups tighten. The two West divisions hold, but elsewhere teams trade places: the Cowboys leave the NFC East to sit with the southern clubs while the Panthers take their spot, and on the AFC side the Colts join the old Browns and Steelers grouping while the Ravens slide east. Travel falls 16.57%, and this part of the bill is the league's own division-drawing, not its conference line.

And the hearts of those same divisions once the conferences are kept but the lines inside them are redrawn for least travel:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Hawthorne, Nevada | 49ers, Cardinals, Rams, Seahawks | 3,118 | The Hawthorne Detonators | A desert town all but surrounded by the Hawthorne Army Depot, one of the largest ammunition stores in the world. |
| Leakesville, Mississippi | Buccaneers, Cowboys, Falcons, Saints | 3,775 | The Leakesville Pinerunners | The Greene County seat in the piney woods of southeast Mississippi, on the Chickasawhay River. |
| Newburg, Wisconsin | Bears, Lions, Packers, Vikings | 1,142 | The Newburg Holsteins | A mill village on the Milwaukee River in the heart of Wisconsin dairy country. |
| Croom, Maryland | Commanders, Eagles, Giants, Panthers | 2,720 | The Croom Crows | A rural crossroads of tobacco barns and woodlots in Prince George's County, near Mount Calvert, the county seat before 1792, on the Patuxent River. |
| Mancos, Colorado | Broncos, Chargers, Chiefs, Raiders | 1,196 | The Mancos Mustangs | A small ranching town in the southwest corner of Colorado, just up the road from Mesa Verde. |
| Freeport, Florida | Dolphins, Jaguars, Texans, Titans | 5,861 | The Freeport Oystermen | A Panhandle town in Walton County at the head of the Choctawhatchee Bay estuary. |
| Powell, Ohio | Bengals, Browns, Colts, Steelers | 14,163 | The Powell Zookeepers | A fast-growing Columbus suburb in Delaware County, home to the Columbus Zoo and Aquarium. |
| Mountainhome, Pennsylvania | Bills, Jets, Patriots, Ravens | 1,202 | The Mountainhome Resorters | A Pocono Mountains community in Monroe County, long resort country. |

{{< realign league="nfl" panel="C" >}}

Drop the conference line and redraw freely, and every division mixes the two conferences. The Raiders and Chargers join the Rams and 49ers in an all-California group; the Patriots and Jets pair with the Giants and Eagles in the northeast. Travel falls 36.23%, and the difference from the conference-bound redraw is the premium: 19.66%, second only to baseball.

The same subtraction:

\[ \text{premium} = \frac{B - C}{A} = \frac{22{,}798.07 - 17{,}424.84}{27{,}324.58} = 19.66\% \]

- \( A = 27{,}324.58 \): the actual divisions' within-division miles
- \( B = 22{,}798.07 \): conferences kept, divisions redrawn
- \( C = 17{,}424.84 \): conference line erased, free redraw
- \( (B - C)/A \): the gap as a share of actual travel, the premium

And once the conference line is erased and every division is drawn from scratch:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Golden Hills, California | 49ers, Chargers, Raiders, Rams | 9,578 | The Golden Hills Windmillers | A community in the Tehachapi Mountains of Kern County, ringed by some of the country's oldest wind farms. |
| Rock Springs, Wyoming | Broncos, Cardinals, Seahawks, Vikings | 23,526 | The Rock Springs Fifty-Sixers | A southwest Wyoming railroad and coal town on the Union Pacific, which called itself Home of 56 Nationalities for its mining-immigrant past. |
| Jefferson, Texas | Chiefs, Cowboys, Saints, Texans | 1,875 | The Jefferson Riverboats | A preserved nineteenth-century riverport on Big Cypress Bayou near Caddo Lake, once a steamboat gateway into East Texas. |
| Nashville, Michigan | Bears, Browns, Lions, Packers | 1,537 | The Nashville Thornapples | A village in Barry County on the Thornapple River, in south-central Michigan farm country. |
| Lancaster, Kentucky | Bengals, Colts, Panthers, Titans | 3,899 | The Lancaster Bluegrass | The Garrard County seat in the Bluegrass region south of Lexington. |
| Citra, Florida | Buccaneers, Dolphins, Falcons, Jaguars | Unincorporated, no 2020 Census count | The Citra Grovers | An unincorporated citrus community in Marion County north of Ocala, long tied to the old Pineapple orange. |
| McConnellstown, Pennsylvania | Bills, Commanders, Ravens, Steelers | 1,208 | The McConnellstown Ridgemen | A small community in Huntingdon County among the long ridges of central Pennsylvania. |
| Glen Cove, New York | Eagles, Giants, Jets, Patriots | 28,365 | The Glen Cove Gilders | A small city on Long Island's North Shore, part of the old Gold Coast of Gilded Age estates. |

The AFC and NFC are a fossil. The American Football League launched in 1960 to challenge the NFL, the two agreed to merge in 1966, and to balance the new conferences three old NFL clubs crossed over to join the ten AFL teams for the 1970 season.[^nfl] So like baseball, the boundary is a brand, not a map. Football is also the league where division count matters most: across one to four divisions per conference the travel swings 14.50%, and the optimum prefers two divisions per conference against the four the league runs, because tight local rivalries are worth more to it than miles.

## NBA, Geographic After All

Here is the twist. Modeled at the thirty teams it actually has, the NBA pays a premium of 0.00%. Keep its East and West and redraw the divisions, or erase the conference line and redraw from scratch, and the optimizer returns the same partition either way: turned loose on all thirty teams, it never once puts an Eastern and a Western team in the same division. Reseeding saves 2.61%, the free redraw saves the same 2.61%, and the line itself costs nothing. The NBA's conferences already are the line a map would draw, exactly like the NHL below.

Both redraws land on the same total, so the gap is nothing:

\[ \text{premium} = \frac{B - C}{A} = \frac{24{,}903.11 - 24{,}903.11}{25{,}571.22} = 0.00\% \]

- \( A = 25{,}571.22 \): the actual divisions' within-division miles, real 30 teams
- \( B = 24{,}903.11 \): conferences kept, divisions redrawn
- \( C = 24{,}903.11 \): conference line erased, free redraw
- \( B = C \): the two redraws tie, so the premium is zero

The optimization runs on the real thirty teams, re-cut into six fives either way; the maps below add the two expansion clubs and re-cut thirty-two:

\[ B:\ 15 \to 3 \times 5 \ \text{per conference} \qquad C:\ 30 \to 6 \times 5 \]

- \( B \): keep the two conferences, cut each 15-team conference into 3 divisions of 5
- \( C \): drop the conference line, cut all 30 teams into 6 divisions of 5

So why give it three maps? Because the NBA is widely expected to grow. In March 2026 its Board of Governors voted unanimously to explore adding two franchises, a revived Seattle SuperSonics and a new Las Vegas team, both of which would sit in the West, with play targeted to begin in 2028.[^nbaexp] The maps below model that projected thirty-two-team league, not the thirty that play today, because adding two western clubs is the only thing that turns the premium from zero into something.

{{< realign league="nba" panel="A" >}}

This is the projected thirty-two-team league: today's six divisions with Seattle and Las Vegas slotted into the West, which now carries seventeen teams to the East's fifteen. The western divisions have to stretch to hold them.

The heart of each division in the modeled league, with its 2020 Census population:

| Division | Center | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Atlantic | Port Jervis, New York | 8,775 | The Port Jervis Railers | An old Erie Railroad division hub at the point where New York, New Jersey, and Pennsylvania meet. |
| Central | LaGrange, Indiana | 2,715 | The LaGrange Drafthorses | The seat of the third-largest Amish settlement in the country, in a county named for Lafayette's château outside Paris. |
| Southeast | Laurel Bay, South Carolina | 5,082 | The Laurel Bay Leathernecks | A Marine Corps housing community for the families stationed at the air station in Beaufort and at Parris Island. |
| Northwest | Lander, Wyoming | 7,546 | The Lander Wranglers | A ranching town at the foot of the Wind River Range and the mouth of Sinks Canyon. |
| Pacific | Inyokern, California | 988 | The Inyokern Dust Devils | A wind-scoured speck in the Mojave next to the China Lake weapons range. |
| Southwest | San Augustine, Texas | 1,920 | The San Augustine Lumberjacks | One of the oldest towns in Texas, deep in the East Texas Piney Woods, with roots in a Spanish mission of 1717. |

{{< realign league="nba" panel="B" >}}

Keep the conferences and redraw the divisions, and the lopsided seventeen-team West sorts into tighter groups while the East does a small shuffle, the Raptors dropping in with the Central teams and the Wizards sliding up to the Atlantic. Travel falls 9.67%.

And the hearts of those same divisions once the conferences are kept but the lines inside them are redrawn for least travel:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Inyokern, California | Clippers, Kings, Lakers, Las Vegas, Suns, Warriors | 988 | The Inyokern Dust Devils | A wind-scoured speck in the Mojave next to the China Lake weapons range. |
| Henderson, Texas | Grizzlies, Mavericks, Pelicans, Rockets, Spurs, Thunder | 13,271 | The Henderson Derrickmen | The Rusk County seat in the piney woods and oil country of East Texas. |
| Driggs, Idaho | Jazz, Nuggets, SuperSonics, Timberwolves, Trail Blazers | 1,984 | The Driggs Tetons | The seat of Teton County on the quiet western side of the Teton Range, in the high farming basin of Teton Valley. |
| Pinckney, Michigan | Bucks, Bulls, Cavaliers, Pistons, Raptors | 2,415 | The Pinckney Trailblazers | A village in Livingston County beside the lakes and trails of the Pinckney Recreation Area. |
| Wrightsville, Georgia | Hawks, Heat, Hornets, Magic, Pacers | 3,449 | The Wrightsville Sandhillers | The Johnson County seat in the sandhills of middle Georgia. |
| Perth Amboy, New Jersey | 76ers, Celtics, Knicks, Nets, Wizards | 55,436 | The Perth Amboy Colonials | An old port city where the Raritan River meets the Arthur Kill, once the colonial capital of East Jersey. |

{{< realign league="nba" panel="C" >}}

Erase the conference line and redraw freely, and the optimizer relieves the imbalance by pulling exactly two teams across the old line: the Timberwolves and the Pelicans, both nominally Western, land in eastern divisions. Travel falls 18.74%, and those two crossings are the entire 9.07% premium. It is not a brand boundary like baseball's; it is the arithmetic cost of unbalancing a conference that geography had balanced.

\[ \text{premium}_{+2} = \frac{B - C}{A} = \frac{28{,}785.36 - 25{,}895.43}{31{,}866.89} = 9.07\% \]

- \( A = 31{,}866.89 \): within-division miles with the two expansion clubs added
- \( B = 28{,}785.36 \): conferences kept, divisions redrawn
- \( C = 25{,}895.43 \): conference line erased, free redraw
- \( (B - C)/A \): the premium the two western clubs introduce

And once the conference line is erased and every division is drawn from scratch:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Lakeview, Oregon | Jazz, Kings, SuperSonics, Trail Blazers, Warriors | 2,418 | The Lakeview Hang Gliders | The Lake County seat in the high desert, billed as the Tallest Town in Oregon at roughly 4,800 feet, with hot springs and gliding ridges nearby. |
| New Kingman-Butler, Arizona | Clippers, Lakers, Las Vegas, Nuggets, Suns | 12,907 | The New Kingman-Butler Mother Roaders | A community beside Kingman on historic Route 66, in the Mojave high desert. |
| Van, Texas | Grizzlies, Mavericks, Rockets, Spurs, Thunder | 2,664 | The Van Wildcatters | A small Van Zandt County town that struck oil in the late 1920s with the Van Oilfield. |
| Saint Joseph, Michigan | Bucks, Bulls, Cavaliers, Pacers, Pistons, Timberwolves | 7,856 | The Saint Joseph Lightkeepers | A Lake Michigan resort town at the mouth of the St. Joseph River, with bluff-top beaches and a pier lighthouse. |
| Madison, Florida | Hawks, Heat, Hornets, Magic, Pelicans | 2,912 | The Madison Cottoneers | The Madison County seat in the rolling hills of north Florida near the Georgia line. |
| Saw Creek, Pennsylvania | 76ers, Celtics, Knicks, Nets, Raptors, Wizards | 4,118 | The Saw Creek Black Bears | A gated resort community in the Poconos of Pike County. |

The real league carries no such scar, because of how it grew. The American Basketball Association ran from 1967 to 1976, and when the NBA absorbed four of its teams it spread them across existing divisions rather than keeping an ABA bloc, then drew its conferences around geography in the mid-2000s.[^nba] A merger only leaves a premium if the absorbed teams are never re-sorted by map; the NBA re-sorted, so at its real roster it sits with the geographic leagues.

## NHL, Geography Already

Hockey is the clean case the NBA's real roster resembles. Here is the league as it stands.

{{< realign league="nhl" panel="A" >}}

The actual divisions cost 68,797.66 miles, the second-highest raw total in the study, because hockey simply covers a lot of ground, from Florida to western Canada. Raw miles and premium are different things, though, as the next two maps show.

The center of each division anyway, with its 2020 Census population:

| Division | Center | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Atlantic | Martinsburg, West Virginia | 18,777 | The Martinsburg Orchardmen | The apple-country seat of West Virginia's eastern panhandle, where the 1877 Great Railroad Strike, the first nationwide industrial walkout, began. |
| Metropolitan | Westminster, Maryland | 20,126 | The Westminster Terriers | The Carroll County seat, where a Union cavalry charge in 1863 briefly tangled with Stuart's troopers and slowed them on the road to Gettysburg. |
| Central | Syracuse, Nebraska | 1,941 | The Syracuse Combines | A farm town in the rolling cropland of southeastern Nebraska. |
| Pacific | Burns, Oregon | 2,730 | The Burns Buckaroos | The seat of high-desert cattle country in Harney County, which is larger than six U.S. states. |

With conferences kept, each sixteen is re-cut into two eights; with the line gone, all thirty-two into four eights:

\[ B:\ 16 \to 2 \times 8 \ \text{per conference} \qquad C:\ 32 \to 4 \times 8 \]

- \( B \): keep the two conferences, cut each 16-team conference into 2 divisions of 8
- \( C \): drop the conference line, cut all 32 teams into 4 divisions of 8

{{< realign league="nhl" panel="B" >}}

Keep the conferences and redraw the divisions, and only the East changes: the optimizer splits the sixteen eastern teams north and south rather than along the old Atlantic and Metropolitan line, while the West stays exactly as it is. Travel falls 5.92%, all of it the league's own division-drawing.

And the hearts of those same divisions once the conferences are kept but the lines inside them are redrawn for least travel:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Burns, Oregon | Canucks, Ducks, Flames, Golden Knights, Kings, Kraken, Oilers, Sharks | 2,730 | The Burns Buckaroos | The seat of high-desert cattle country in Harney County, which is larger than six U.S. states. |
| Syracuse, Nebraska | Avalanche, Blackhawks, Blues, Jets, Mammoth, Predators, Stars, Wild | 1,941 | The Syracuse Combines | A farm town in the rolling cropland of southeastern Nebraska. |
| Floyd, Virginia | Blue Jackets, Capitals, Hurricanes, Lightning, Panthers, Penguins, Red Wings, Sabres | 448 | The Floyd Fiddlers | A tiny Blue Ridge town known for old-time mountain music, the Friday Night Jamboree at the Floyd Country Store, and the FloydFest gathering. |
| Stamford, New York | Bruins, Canadiens, Devils, Flyers, Islanders, Maple Leafs, Rangers, Senators | 1,040 | The Stamford Mountaineers | A Catskills village in Delaware County beneath Mount Utsayantha, an old summer-resort town. |

{{< realign league="nhl" panel="C" >}}

Erase the conference line and redraw freely, and the same two camps rebuild themselves: not one division mixes an Eastern and a Western team. Travel falls by exactly the same 5.92%, so the premium is 0.00%. The line was already where a map would put it.

The two optimal maps tie, so the subtraction vanishes:

\[ \text{premium} = \frac{B - C}{A} = \frac{64{,}726.97 - 64{,}726.97}{68{,}797.66} = 0.00\% \]

- \( A = 68{,}797.66 \): the actual divisions' within-division miles
- \( B = 64{,}726.97 \): conferences kept, divisions redrawn
- \( C = 64{,}726.97 \): conference line erased, free redraw
- \( B = C \): the redraws tie, so the premium is zero

And once the conference line is erased and every division is drawn from scratch:

| Center | Teams | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Burns, Oregon | Canucks, Ducks, Flames, Golden Knights, Kings, Kraken, Oilers, Sharks | 2,730 | The Burns Buckaroos | The seat of high-desert cattle country in Harney County, which is larger than six U.S. states. |
| Syracuse, Nebraska | Avalanche, Blackhawks, Blues, Jets, Mammoth, Predators, Stars, Wild | 1,941 | The Syracuse Combines | A farm town in the rolling cropland of southeastern Nebraska. |
| Floyd, Virginia | Blue Jackets, Capitals, Hurricanes, Lightning, Panthers, Penguins, Red Wings, Sabres | 448 | The Floyd Fiddlers | A tiny Blue Ridge town known for old-time mountain music, the Friday Night Jamboree at the Floyd Country Store, and the FloydFest gathering. |
| Stamford, New York | Bruins, Canadiens, Devils, Flyers, Islanders, Maple Leafs, Rangers, Senators | 1,040 | The Stamford Mountaineers | A Catskills village in Delaware County beneath Mount Utsayantha, an old summer-resort town. |

When the NHL absorbed four teams from the World Hockey Association in 1979, it placed the survivors by geography rather than keeping a rival bloc, and its conferences have followed the map since.[^nhl] Division count is nearly irrelevant here, a 1.10% swing, and the optimum agrees with the two divisions per conference the league uses.

## MLS, Nothing to Recover

Soccer has only two maps, because there is no division layer beneath its conferences to redraw.

{{< realign league="mls" panel="A" >}}

This is the league as it stands: thirty teams split fifteen and fifteen into an Eastern and a Western Conference, and nothing finer.

Even a conference has a center, with its 2020 Census population:

| Division | Center | 2020 Pop. | Team | Note |
| --- | --- | --- | --- | --- |
| Eastern Conference | Warm Springs, Virginia | 121 | The Warm Springs Soakers | Home of the Jefferson Pools, warm mineral baths in a pair of historic wooden bathhouses where Thomas Jefferson soaked in 1818, in a county with no incorporated towns at all. |
| Western Conference | Delta, Colorado | 9,035 | The Delta Drovers | A Western Slope town at the delta where the Uncompahgre River meets the Gunnison, grown up from an 1820s trading post in old cattle-drive country. |

There is only one cut to make, the split itself, because no divisions sit beneath it:

\[ C:\ 30 \to 2 \times 15 \quad (\text{no } B) \]

- \( C \): the only cut is the split itself, 30 teams into 2 conferences of 15
- no \( B \): there is no division layer beneath the conferences to redraw

{{< realign league="mls" panel="C" >}}

Solve for the best fifteen and fifteen split and the optimizer hands back the identical two lists; not one team changes conference. The premium is 0.00%, but it is a different zero from hockey's. Hockey earns its zero, since the optimizer would draw that same line. Soccer's is structural: with no divisions to redraw, there is nothing to recover.

With no division layer there is no \( B \) to compute; the best conference split just equals the actual one:

\[ \text{recover}_C = \frac{A - C}{A} = \frac{168{,}085.75 - 168{,}085.75}{168{,}085.75} = 0.00\% \]

- \( A = 168{,}085.75 \): the actual split's within-conference miles
- \( C = 168{,}085.75 \): the best split returns the identical miles
- \( A = C \): the optimal split is the actual one, so nothing is recovered

The optimal split returns the same two conferences, so the centers do not move: the East stays centered on Warm Springs and the West on Delta.

Major League Soccer was built from scratch in the 1990s rather than from a merger, and it has never carried a division layer beneath its two geographic conferences.[^mls] There is simply no historical line for a premium to hide in.

## The Spectrum, or the Lack of One

Laid end to end, the five leagues do not fall on a tidy gradient. They fall into two groups, and the split tracks one piece of history: what each league did with a rival it absorbed. Baseball and football kept the old boundary as a brand and pay for it, 28.87 and 19.66%. The NBA and the NHL absorbed rivals too, then re-sorted them by geography, so at their real rosters they pay nothing. Soccer never merged and never drew a division layer, so its zero is structural. The premium is a single subtraction, but it sorts the leagues by whether a merged league kept its old line or dissolved it into the map.

The NBA is the proof rather than the exception. Its real thirty-team conferences already are the map, which is why it pays zero; the only way to make a premium appear is to add two western expansion clubs and unbalance a conference geography had balanced, and even then the 9.07% is arithmetic, not history. A line drawn by distance can be made to cost miles only by breaking the distance that drew it.

## What This Does Not Mean

The premium is a geographic accounting, not a proposal, and a few limits keep it honest.

It measures dispersion, not itineraries. Each arena is a single point, and the score is the spread of teams within a division, not a literal flight schedule with road trips, layovers, and charter logistics. Two leagues with the same premium can fly very different real routes.

The headline NBA number is the real thirty-team league, which pays nothing. The maps, the centroid towns, and the 9.07% figure in that section all model a projected thirty-two-team league with Seattle and Las Vegas added, an expansion the league voted in March 2026 to explore but has not yet approved. It illustrates what unbalancing a conference would cost; it is not the baseline.

The full-league optimum is strong, not provably global. Where exact enumeration is infeasible, \( C \) is solved over a nearest-neighbor candidate pool, so it is optimal against a high-quality field rather than proven best across all partitions for the largest leagues.

And it prices only miles. Conferences carry rivalry, television markets, history, and competitive balance that no distance matrix can see. A high premium is not a verdict that a league is wrong, only a measure of what its line costs in travel.

## Methods and Sources

Coordinates for every team, including the two presumptive NBA expansion clubs, live in one shared file, and every distance is the haversine great-circle mile computed once into a matrix. Each optimal alignment is the exact minimum of a set-partition integer program (CBC, via OR-Tools or PuLP) where the enumeration is tractable, and the same program over a nearest-neighbor candidate set where it is not. The schedule weighting uses each league's real division, conference, and cross-conference game ratios under the frozen-cross model, which the identity above proves leaves the partition untouched.

The centroid towns are a flourish, not analysis: each is the nearest populated place to the average position of a real division, found by reverse-geocoding the centroid, and the populations are 2020 US Census counts where a count exists. The maps follow the page's light or dark mode, and every premium, recovery figure, and panel reads from the one coordinate file and the one solve.

```python
def centroid(teams_in_division):
    lat = sum(t.lat for t in teams_in_division) / len(teams_in_division)
    lon = sum(t.lon for t in teams_in_division) / len(teams_in_division)
    return lat, lon
```

Sources and data. Team coordinates are arena locations compiled by hand; populations are 2020 United States Census counts where a count exists. Distances are haversine great-circle miles, and each optimal alignment is the exact minimum of a set-partition integer program solved with CBC through PuLP. The league histories are cited in the notes below.

The reasoning is the deliverable: the premium only means something once you have seen the maps, the distance metric, the integer program that picks the divisions, and the schedule argument that makes the comparison fair.


[^mlb]: The National League dates to 1876 and the American League to 1901. The two made peace in 1903 and began staging the World Series, but kept separate offices, umpires, and even rules, including the American League's designated hitter, until they were folded into a single Major League Baseball organization in 2000 and the league presidencies were eliminated. Sources: [American League](https://en.wikipedia.org/wiki/American_League), Wikipedia; [Did MLB Exist Before the Year 2000?](https://sabr.org/journal/article/did-mlb-exist-before-the-year-2000/), Society for American Baseball Research.
[^nfl]: The American Football League began in 1960 to rival the NFL. The leagues agreed to merge in June 1966 and combined fully for the 1970 season; to balance the new conferences at thirteen teams each, three NFL clubs, the Colts, Browns, and Steelers, joined the ten former AFL teams in the American Football Conference. Source: [AFL-NFL merger](https://en.wikipedia.org/wiki/AFL%E2%80%93NFL_merger), Wikipedia.
[^nba]: The American Basketball Association operated from 1967 to 1976, when the NBA absorbed four of its teams, the Nuggets, Pacers, Spurs, and Nets, and spread them across existing divisions rather than keeping a bloc. The NBA's current East and West alignment, drawn around geography, dates to the mid-2000s. Source: [ABA-NBA merger](https://en.wikipedia.org/wiki/ABA%E2%80%93NBA_merger), Wikipedia.
[^nhl]: The World Hockey Association challenged the NHL from 1972 to 1979, when the NHL took in four survivors, the Oilers, Whalers, Nordiques, and Jets, and placed them by geography. Its conferences have tracked the map since. Source: [1979 NHL expansion](https://en.wikipedia.org/wiki/1979_NHL_expansion), Wikipedia.
[^mls]: Major League Soccer was founded in 1993 and began play in 1996, built new rather than from a merger. It splits into Eastern and Western Conferences with no division layer beneath them. Source: [Major League Soccer](https://en.wikipedia.org/wiki/Major_League_Soccer), Wikipedia.
[^nbarow]: The real thirty-team league, which pays nothing. The 9.07% what-if and the NBA-section maps model a projected thirty-two-team league with Seattle and Las Vegas added; see the note in that section.
[^nbaexp]: A projection, not the current league. On March 24 and 25, 2026, the NBA Board of Governors voted unanimously to explore expansion to Seattle, reviving the SuperSonics, and Las Vegas, with new teams targeted to begin play in 2028; the league has stressed that expansion is not yet certain. Sources: [NBA to explore expansion in Seattle and Las Vegas](https://www.nba.com/news/nba-commissioner-adam-silver-on-leagues-plan-to-explore-expansion-in-seattle-and-las-vegas), NBA.com; [Expansion of the NBA](https://en.wikipedia.org/wiki/Expansion_of_the_NBA), Wikipedia.
