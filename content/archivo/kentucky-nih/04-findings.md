---
title: "Findings"
weight: 40
description: "Deeper analytical queries using window functions and common table expressions to surface multi-year patterns, institutional rankings, and the funding shifts visible across two decades of NIH research grants awarded in Kentucky."
summary: "Phase 4: Window functions and CTEs"
tags: ["sql", "sqlite", "window-functions", "ctes", "datasette"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Window functions, CTEs, and the patterns that emerge when twenty-one years of grants get cross-cut by institute, organization, and time.
{{< /lead >}}

## At a Glance

The exploration phase gave the shape of the data: two-decade pattern in annual funding, two-institution dominance, a recognizable category mix, the 2009 ARRA spike. Phase 04 reaches for the SQL constructs that show how things change across dimensions. Window functions for moving averages. Common table expressions for multi-step aggregations. Decade-over-decade comparisons that reveal what stayed steady and what shifted underneath.

This is the [findings phase](/biblioteca/#the-phased-walkthrough) the case study philosophy describes: where descriptive analytical claims live, paired with their caveats. Each finding here names what the data supports and what it does not. Where the result of a query produces a number that requires external context to interpret correctly (the NCRR rename, the IDeA program affecting P20 frequency), that context is supplied or the claim is held back.

Every SQL block in this phase has a [Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite) link below it so the reader can re-run the query and verify the result. The expected output shown alongside each query is the actual output from the live database.

## Smoothing The Annual Series

Phase 03's annual funding chart is dominated by one artifact: the 2009 ARRA spike. The spike is real and explained, but it compresses the visible variation across the other twenty years into a narrower band. A 5-year centered moving average smooths the spike and reveals the underlying trajectory:

\\[\overline{f}_{t} = \dfrac{1}{5}\sum_{i=t-2}^{t+2} f_i\\]

where \\(\overline{f}_{t}\\) is the 5-year centered moving average at fiscal year \\(t\\), \\(f_i\\) is the actual annual NIH funding total to Kentucky institutions in fiscal year \\(i\\), and the sum runs over the five-year window centered on \\(t\\) (the year itself plus the two years before and the two years after). For years near the edges of the window (2005-2006 and 2024-2025), the SQL query's `ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING` clause produces a truncated window with fewer years; the average for those years is mathematically valid but covers fewer years than the interior values.

```sql
-- Annual funding with a 5-year centered moving average overlay.
-- The CTE first computes annual totals (one row per fiscal year).
-- The outer query then applies AVG() OVER ROWS BETWEEN 2 PRECEDING AND
-- 2 FOLLOWING to compute a centered 5-year moving average for each year.
-- Years near the edges (2005-2006, 2024-2025) get truncated windows
-- because there are not yet 2 preceding or 2 following years available;
-- the moving average for those years is mathematically valid but covers
-- fewer years than the interior values.
WITH annual AS (
    SELECT
        p.fiscal_year,
        SUM(f.total_cost_ic) AS total_funding
    FROM projects p
    JOIN project_funders f USING (application_id)
    GROUP BY p.fiscal_year
)
SELECT
    CAST(fiscal_year AS INTEGER)                AS "Fiscal Year",
    ROUND(total_funding / 1e6, 1)               AS "Actual ($M)",
    ROUND(AVG(total_funding) OVER (
        ORDER BY fiscal_year
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ) / 1e6, 1)                                 AS "5-yr Avg ($M)"
FROM annual
ORDER BY fiscal_year;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=WITH+annual+AS+%28SELECT+p.fiscal_year%2C+SUM%28f.total_cost_ic%29+AS+total_funding+FROM+projects+p+JOIN+project_funders+f+USING+%28application_id%29+GROUP+BY+p.fiscal_year%29+SELECT+CAST%28fiscal_year+AS+INTEGER%29+AS+%22Fiscal+Year%22%2C+ROUND%28total_funding+%2F+1e6%2C+1%29+AS+%22Actual+%28%24M%29%22%2C+ROUND%28AVG%28total_funding%29+OVER+%28ORDER+BY+fiscal_year+ROWS+BETWEEN+2+PRECEDING+AND+2+FOLLOWING%29+%2F+1e6%2C+1%29+AS+%225-yr+Avg+%28%24M%29%22+FROM+annual+ORDER+BY+fiscal_year%3B)

Result:

```text
Fiscal Year   Actual ($M)   5-yr Avg ($M)
       2005         198.5           182.9
       2006         175.6           183.2
       2007         174.5           196.1
       2008         184.1           203.2
       2009         248.0           206.5
       2010         233.8           211.4
       2011         192.1           211.3
       2012         199.0           201.4
       2013         183.6           194.5
       2014         198.5           191.2
       2015         199.2           190.8
       2016         175.8           197.1
       2017         196.7           204.9
       2018         215.4           216.0
       2019         237.3           233.1
       2020         254.9           242.3
       2021         260.9           246.8
       2022         243.0           247.6
       2023         237.7           243.7
       2024         241.6           239.4
       2025         235.2           238.1
```

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">The smoothed series shows two distinct phases: a flat 2005-2014 period around $190-210M, and a steady climb from 2015 onward.</p>
<p class="pgbd-case-chart-sub">Annual NIH funding to Kentucky (blue) with 5-year centered moving average (gold dashed). The smoothing flattens the 2009 ARRA spike and reveals the underlying twenty-one-year trajectory more clearly.</p>
{{< chart >}}
type: 'line',
data: {
  labels: [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
  datasets: [
    {
      label: 'Annual (actual)',
      data: [198.5, 175.6, 174.5, 184.1, 248.0, 233.8, 192.1, 199.0, 183.6, 198.5, 199.2, 175.8, 196.7, 215.4, 237.3, 254.9, 260.9, 243.0, 237.7, 241.6, 235.2],
      borderColor: '#0969DA',
      backgroundColor: 'rgba(9, 105, 218, 0.10)',
      borderWidth: 2,
      fill: false,
      tension: 0.2,
      pointRadius: 2,
      pointHoverRadius: 5,
    },
    {
      label: '5-year moving average',
      data: [182.9, 183.2, 196.1, 203.2, 206.5, 211.4, 211.3, 201.4, 194.5, 191.2, 190.8, 197.1, 204.9, 216.0, 233.1, 242.3, 246.8, 247.6, 243.7, 239.4, 238.1],
      borderColor: '#BF8700',
      backgroundColor: 'rgba(191, 135, 0, 0.0)',
      borderWidth: 2.5,
      fill: false,
      tension: 0.3,
      pointRadius: 2,
      pointHoverRadius: 5,
      borderDash: [4, 3],
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'bottom' },
    tooltip: {
      callbacks: {
        label: function(context) {
          return context.dataset.label + ': $' + context.parsed.y.toFixed(1) + 'M';
        }
      }
    }
  },
  scales: {
    x: {
      title: { display: true, text: 'Fiscal Year' },
      ticks: { maxRotation: 0, autoSkip: true, autoSkipPadding: 12 }
    },
    y: {
      title: { display: true, text: 'Millions USD' },
      beginAtZero: false,
      ticks: {
        callback: function(value) { return '$' + value + 'M'; }
      }
    }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The smoothed series tells a different story than the raw annual numbers. The 2009 spike disappears into a slowly rising plateau through the early 2010s. The mid-2010s dip becomes a real slowdown rather than a single low year. The 2018-2021 climb shows up as the strongest sustained growth period in the dataset, with the moving average reaching $246.8M in 2021. The 2022-2025 plateau holds the gains rather than retreating. The bottom line: Kentucky NIH funding genuinely grew from a $190-210M decade-one band to a $230-250M decade-two band, a real institutional expansion that the 2009 spike obscures in the raw chart.

## UK vs U of L Across Twenty-One Years

The University of Kentucky and the University of Louisville together account for 87 percent of all Kentucky NIH funding ([phase 03 finding](/archivo/kentucky-nih/03-exploration/#top-institutions)). The natural follow-up question is whether they grew in lockstep or diverged. A side-by-side annual comparison:

```sql
-- Annual funding for UK and U of L over the full window. Returns one
-- row per (institution, fiscal_year) pair so the result can be pivoted
-- into a side-by-side line chart in any visualization tool that
-- handles two-series time-series. CAST drops the .0 from fiscal_year;
-- ROUND keeps millions to one decimal place.
SELECT
    CAST(p.fiscal_year AS INTEGER)             AS "Fiscal Year",
    p.organization_name                        AS "Institution",
    ROUND(SUM(f.total_cost_ic) / 1e6, 1)       AS "Funding ($M)"
FROM projects p
JOIN project_funders f USING (application_id)
WHERE p.organization_name IN (
    'UNIVERSITY OF KENTUCKY',
    'UNIVERSITY OF LOUISVILLE'
)
GROUP BY p.fiscal_year, p.organization_name
ORDER BY p.fiscal_year, p.organization_name;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+CAST%28p.fiscal_year+AS+INTEGER%29+AS+%22Fiscal+Year%22%2C+p.organization_name+AS+%22Institution%22%2C+ROUND%28SUM%28f.total_cost_ic%29+%2F+1e6%2C+1%29+AS+%22Funding+%28%24M%29%22+FROM+projects+p+JOIN+project_funders+f+USING+%28application_id%29+WHERE+p.organization_name+IN+%28%27UNIVERSITY+OF+KENTUCKY%27%2C+%27UNIVERSITY+OF+LOUISVILLE%27%29+GROUP+BY+p.fiscal_year%2C+p.organization_name+ORDER+BY+p.fiscal_year%2C+p.organization_name%3B)

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">UK climbed from $87M in 2005 to $177M in 2021 while U of L oscillated in a $47-75M band, never approaching UK's growth.</p>
<p class="pgbd-case-chart-sub">Annual NIH funding for the University of Kentucky and the University of Louisville, FY 2005 through FY 2025. Both institutions show the 2009 ARRA spike, but UK's longer-term trajectory diverged sharply from U of L's flat baseline starting around 2015.</p>
{{< chart >}}
type: 'line',
data: {
  labels: [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
  datasets: [
    {
      label: 'University of Kentucky',
      data: [87.2, 89.6, 86.4, 93.2, 118.7, 118.5, 92.2, 91.9, 85.4, 99.7, 103.6, 105.0, 120.0, 139.2, 163.1, 168.1, 177.3, 160.6, 157.1, 158.0, 149.1],
      borderColor: '#0969DA',
      backgroundColor: 'rgba(9, 105, 218, 0.10)',
      borderWidth: 2,
      fill: false,
      tension: 0.2,
      pointRadius: 2,
      pointHoverRadius: 5,
    },
    {
      label: 'University of Louisville',
      data: [76.5, 51.2, 51.8, 54.4, 68.6, 64.4, 53.5, 51.3, 47.3, 46.8, 53.0, 55.2, 62.8, 64.0, 61.5, 74.8, 69.3, 65.5, 67.1, 66.4, 72.0],
      borderColor: '#BF3989',
      backgroundColor: 'rgba(191, 57, 137, 0.10)',
      borderWidth: 2,
      fill: false,
      tension: 0.2,
      pointRadius: 2,
      pointHoverRadius: 5,
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'bottom' },
    tooltip: {
      callbacks: {
        label: function(context) {
          return context.dataset.label + ': $' + context.parsed.y.toFixed(1) + 'M';
        }
      }
    }
  },
  scales: {
    x: {
      title: { display: true, text: 'Fiscal Year' },
      ticks: { maxRotation: 0, autoSkip: true, autoSkipPadding: 12 }
    },
    y: {
      title: { display: true, text: 'Millions USD' },
      beginAtZero: false,
      ticks: {
        callback: function(value) { return '$' + value + 'M'; }
      }
    }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The two institutions tracked a similar shape through 2014. Both showed the 2009 ARRA spike (UK at $118.7M, U of L at $68.6M). Both had soft years in 2013. Then they diverged. UK climbed steadily from $99.7M in 2014 to a peak of $177.3M in 2021 and held above $149M through 2025. U of L oscillated in a $47-75M band across the entire window, with no comparable growth phase. By 2024, UK was funding nearly 2.4 times what U of L was; the same ratio in 2005 was closer to 1.1 to 1.

The divergence has structural explanations beyond what this dataset shows. UK opened its [Markey Cancer Center](https://ukhealthcare.uky.edu/markey-cancer-center) which received NCI Comprehensive Cancer Center designation in 2013 and built out research infrastructure during the same window. The funding data shows the result of those institutional dynamics; the dataset alone does not show their cause, and any narrative about "why" requires sources outside this case study.

## Cross-IC Funding Patterns Across Decades

Each grant has an administering Institute or Center within NIH (NCI for Cancer, NIMH for Mental Health, NIDA for Drug Abuse, etc.). The mix of ICs that fund Kentucky research is itself a signal about what kinds of work the state's research community pursues. Decade-over-decade comparison surfaces shifts:

```sql
-- IC funding mix, comparing 2005-2014 against 2015-2024.
-- The CTE buckets each project's funding into one of two decades based
-- on fiscal_year. The outer query then pivots: for each Funding IC,
-- show first-decade total, second-decade total, and percent change.
-- 2025 is excluded so the comparison is decade-vs-decade rather than
-- contaminated by a partial-window edge effect. ROUND keeps millions
-- to one decimal place; the percent column is rounded to whole numbers.
WITH ic_decade AS (
    SELECT
        f.funding_ic,
        CASE
            WHEN p.fiscal_year BETWEEN 2005 AND 2014 THEN '2005-2014'
            WHEN p.fiscal_year BETWEEN 2015 AND 2024 THEN '2015-2024'
        END AS decade,
        SUM(f.total_cost_ic) AS funding
    FROM projects p
    JOIN project_funders f USING (application_id)
    WHERE p.fiscal_year BETWEEN 2005 AND 2024
    GROUP BY f.funding_ic, decade
)
SELECT
    funding_ic                                                              AS "Institute",
    ROUND(SUM(CASE WHEN decade = '2005-2014' THEN funding END) / 1e6, 1)    AS "First Decade ($M)",
    ROUND(SUM(CASE WHEN decade = '2015-2024' THEN funding END) / 1e6, 1)    AS "Second Decade ($M)",
    ROUND(
        100.0 *
        (SUM(CASE WHEN decade = '2015-2024' THEN funding END) -
         SUM(CASE WHEN decade = '2005-2014' THEN funding END)) /
        NULLIF(SUM(CASE WHEN decade = '2005-2014' THEN funding END), 0),
        0
    )                                                                       AS "Change (%)"
FROM ic_decade
GROUP BY funding_ic
ORDER BY "Second Decade ($M)" DESC NULLS LAST
LIMIT 12;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=WITH+ic_decade+AS+%28SELECT+f.funding_ic%2C+CASE+WHEN+p.fiscal_year+BETWEEN+2005+AND+2014+THEN+%272005-2014%27+WHEN+p.fiscal_year+BETWEEN+2015+AND+2024+THEN+%272015-2024%27+END+AS+decade%2C+SUM%28f.total_cost_ic%29+AS+funding+FROM+projects+p+JOIN+project_funders+f+USING+%28application_id%29+WHERE+p.fiscal_year+BETWEEN+2005+AND+2024+GROUP+BY+f.funding_ic%2C+decade%29+SELECT+funding_ic+AS+%22Institute%22%2C+ROUND%28SUM%28CASE+WHEN+decade+%3D+%272005-2014%27+THEN+funding+END%29+%2F+1e6%2C+1%29+AS+%22First+Decade+%28%24M%29%22%2C+ROUND%28SUM%28CASE+WHEN+decade+%3D+%272015-2024%27+THEN+funding+END%29+%2F+1e6%2C+1%29+AS+%22Second+Decade+%28%24M%29%22%2C+ROUND%28100.0+%2A+%28SUM%28CASE+WHEN+decade+%3D+%272015-2024%27+THEN+funding+END%29+-+SUM%28CASE+WHEN+decade+%3D+%272005-2014%27+THEN+funding+END%29%29+%2F+NULLIF%28SUM%28CASE+WHEN+decade+%3D+%272005-2014%27+THEN+funding+END%29%2C+0%29%2C+0%29+AS+%22Change+%28%25%29%22+FROM+ic_decade+GROUP+BY+funding_ic+ORDER+BY+%22Second+Decade+%28%24M%29%22+DESC+NULLS+LAST+LIMIT+12%3B)

Result:

```text
Institute   First Decade ($M)   Second Decade ($M)   Change (%)
NIGMS                    99.1                254.4         +157
NIDA                    148.6                239.5          +61
NCI                     168.8                226.9          +34
NIA                     115.5                226.1          +96
NHLBI                   211.7                185.1          -13
NIAID                   102.7                139.2          +36
NIEHS                    60.3                136.1         +126
NINDS                   118.2                136.0          +15
OD                       39.9                103.6         +159
NIDDK                    74.7                 93.6          +25
NIAAA                    51.7                 86.2          +67
NIDCR                    43.8                 54.8          +25
```

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">OD and NIGMS led growth at +159% and +157%; NHLBI was the only major IC to contract, declining 13%.</p>
<p class="pgbd-case-chart-sub">Decade-over-decade percent change in NIH funding to Kentucky by Institute or Center, 2005-2014 vs 2015-2024. Bars sorted by change descending; the diverging axis makes contraction easy to spot at a glance.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: ['OD', 'NIGMS', 'NIEHS', 'NIA', 'NIAAA', 'NIDA', 'NIAID', 'NCI', 'NIDDK', 'NIDCR', 'NINDS', 'NHLBI'],
  datasets: [
    {
      label: 'Change (%)',
      data: [159, 157, 126, 96, 67, 61, 36, 34, 25, 25, 15, -13],
      backgroundColor: function(context) {
        var value = context.dataset.data[context.dataIndex];
        return value < 0 ? 'rgba(191, 57, 137, 0.7)' : 'rgba(9, 105, 218, 0.7)';
      },
      borderColor: function(context) {
        var value = context.dataset.data[context.dataIndex];
        return value < 0 ? '#BF3989' : '#0969DA';
      },
      borderWidth: 1.5,
    }
  ]
},
options: {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: function(context) {
          var v = context.parsed.x;
          return (v >= 0 ? '+' : '') + v + '%';
        }
      }
    }
  },
  scales: {
    x: {
      title: { display: true, text: 'Change (%)' },
      ticks: {
        callback: function(value) { return (value >= 0 ? '+' : '') + value + '%'; }
      },
      grid: {
        color: function(context) {
          return context.tick.value === 0 ? 'rgba(0,0,0,0.4)' : 'rgba(0,0,0,0.1)';
        },
        lineWidth: function(context) {
          return context.tick.value === 0 ? 1.5 : 1;
        }
      }
    },
    y: {
      title: { display: true, text: 'Institute' }
    }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

Five findings worth surfacing.

NIGMS (the National Institute of General Medical Sciences) grew 157 percent decade-over-decade, from $99M to $254M, the largest growth rate of any major IC funding Kentucky research. NIGMS is the IC most associated with the IDeA program ([phase 03's P20 finding](/archivo/kentucky-nih/03-exploration/#the-arra-spike)), and Kentucky's IDeA designation makes it eligible for NIGMS-administered capacity-building awards that scaled up across this window.

NIDA (the National Institute on Drug Abuse) grew 61 percent decade-over-decade, from $149M to $240M. That tracks the [phase 03 observation](/archivo/kentucky-nih/03-exploration/#nih-spending-categories) about Substance Misuse appearing as a top-eleven category. Kentucky's documented role as a focal point for opioid response research is visible here as a real funding shift, not a flat baseline that just happens to rank.

NIA (the National Institute on Aging) grew 96 percent, from $116M to $226M. The framing on the [case study landing page](/archivo/kentucky-nih/) about Kentucky's demographic profile shows up here too: aging research nearly doubled across the window. NIEHS (Environmental Health) grew 126 percent on a $60M base, more than doubling to $136M.

OD (Office of the Director) grew 159 percent, the largest percentage change in the table, from $40M to $104M. The OD funds [trans-NIH initiatives](https://www.nih.gov/institutes-nih/list-nih-institutes-centers-offices) that span multiple institutes rather than a single research domain, including the Common Fund, the IDeA Programs Office, and various cross-institute collaborative initiatives. The growth tracks the same IDeA-program story as NIGMS and consistent with Kentucky's IDeA-state designation. A reader who saw OD jump from $40M to $104M without understanding what OD does might assume it represented direct research funding to a single Institute; in fact it represents the Office that coordinates initiatives flowing through multiple Institutes, which is itself a structural finding worth surfacing.

NHLBI (Heart, Lung, and Blood) is the one major IC that contracted, declining 13 percent. Most other ICs grew; NHLBI shrunk. The dataset shows the contraction; it does not show the cause, and any explanation would require external sources (institutional research priority shifts, NIH-wide budget reallocations, retirements of UK PIs in cardiovascular research, all plausible).

One more observation worth surfacing through review rather than calculation: NCRR (the National Center for Research Resources) does not appear in the top twelve. NCRR was [dissolved by NIH in December 2011](https://www.nih.gov/news-events/news-releases/nih-establishes-national-center-advancing-translational-sciences) and its functions were absorbed into the new National Center for Advancing Translational Sciences (NCATS) and several other institutes. NCRR funding existed in the first decade and was reorganized under different IC labels in subsequent years; a reader who saw NCRR's absence from the second decade might conclude that NCRR-funded work stopped happening, which is wrong.

This is the [reproducibility-is-the-floor, review-is-the-ceiling](/biblioteca/#reproducibility-is-the-floor-review-is-the-ceiling) principle in concrete form. Anyone running this query reproduces these numbers. A reviewer is the one who would ask "wait, what happened to NCRR?" and prompt the rename investigation that turns a chart artifact into a defensible finding.

## What This Doesn't Tell You

A short, honest section closing out the analytical work. SQL on grant data tells you about awarded research dollars and the institutional structure of who receives them. It does not tell you about research outcomes, publication impact, patient outcomes, the lived experience of the communities the research is supposedly serving, or the quality of the science itself. The data is administrative.

A grant in NIH RePORTER is a contract, not a result. A high-funding department is not necessarily a high-impact department; a low-funding department is not necessarily a low-impact one. The data this case study queries is the *paperwork* of biomedical research in Kentucky, not the research itself. Any portfolio reader using this case study to evaluate how good Kentucky's biomedical research is would be reading the wrong dataset for that question.

This is the analytical equivalent of the "I am not a lawyer" disclaimer: useful framing for a reader who might otherwise infer more than the data supports. The case study philosophy treats this kind of explicit boundary-setting as part of the deliverable, not an afterthought.

## Closing

Four phases. The source phase pulled one CSV from NIH RePORTER and surfaced the seven structural quirks the loader had to handle. The schema phase verified the co-funding invariant on every project in the dataset and produced a three-table normalized SQLite database with foreign keys and indexes ready to query. The exploration phase ran the breadth-before-depth queries that gave the shape of the data: the two-decade pattern, the two-institution dominance, the ARRA spike, the recognizable category mix. This phase reached for window functions, common table expressions, and decade-over-decade comparisons to surface the patterns that emerge when dimensions cross.

The schema design from phase 02 turned out to be the load-bearing piece for everything else. Without the co-funding invariant verified, every aggregate query in phases 03 and 04 would have silently double-counted. Without the missing-cost pattern documented, queries would have either deflated averages or excluded a quarter of the dataset by accident. Without the multi-valued category column exploded into its own table, the category-trajectory work in this phase would have required slow `LIKE '%substance%'` substring matches against a denormalized field. Reproducibility is the floor; the schema work made the rest of the case study possible.

The database is at [`https://pgbd.casa/data/kentucky-nih.sqlite`](https://pgbd.casa/data/kentucky-nih.sqlite) for direct download. The build script is at [`tools/build_kentucky_nih.py`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/build_kentucky_nih.py) on GitHub. The full case study is structured to invite re-running and disagreement: clone the SQLite, modify the queries, follow your own questions. Every claim here was verified by a query you can run yourself. That is what the [case study philosophy](/biblioteca/) calls reproducibility-as-the-floor; what makes it a case study and not just a chart deck is that the reasoning behind each query is visible alongside the result.
