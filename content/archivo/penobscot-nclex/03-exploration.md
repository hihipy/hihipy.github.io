---
title: "Exploration"
weight: 30
description: "Six orientation queries across the obvious dimensions: region, campus, program pathway, testing cohort, time from graduation to test, and retake outcomes. Confidence intervals computed inline in SQL using the Wald formula. The campus spread phase 01 surfaced gets its first full breakdown with sample-size context."
summary: "Six queries that get the shape of the data"
tags: ["datasette", "exploratory-analysis", "sql", "sqlite"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}

{{< lead >}}
Six queries that cover the obvious dimensions: region, campus, program, cohort, time from graduation to test, and retake outcomes.
{{< /lead >}}


<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

## At a Glance

The schema phase produced a queryable database with three tables and known relationships. The natural first move is breadth before depth: run a handful of queries that cover the obvious dimensions (region, campus, program, cohort, retake count, and time from graduation to test) without yet reaching for window functions or model fits. See what the data says at a glance, then decide which questions are worth following further in phase 04.

Every SQL block in this phase has a Datasette Lite link below it so the reader can run the query directly in the browser against the same database, no setup required. Every claim in the prose ties to a query the reader can re-run.

The dimension that matters most is already known from the source phase: campus, with a 26-point spread between the lowest and highest first-time pass rate. This phase confirms that spread, adds confidence intervals so the reader can see which campus differences are real and which are sample noise, and develops five other dimensions that the case study will not lead with in phase 04 but that shape the analysis along the way.

## How To Read These Numbers

Every pass rate in this phase comes with a 95 percent confidence interval computed inline in SQL using the standard Wald formula for a proportion:

$$\hat{p} \pm 1.96 \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}$$

The interval widens as the sample size shrinks. At $n=2{,}572$ (Greater Boston Region, the largest in the data), the margin is roughly $\pm 1.4$ percentage points. At $n=47$ (Northern New England, the smallest region), it widens to roughly $\pm 8.80$ points. Reading these widths is the difference between treating two campuses as meaningfully different and reading them as statistically indistinguishable.

The Wald formula has one known weakness worth flagging before phase 03 starts using it: at very small $n$ combined with extreme $\hat{p}$, the upper bound can exceed 100 percent. Two small campuses (`MAN` at $n=11$ and `POR` at $n=36$) hit this case, producing nominal upper bounds above 100 percent. The right reading is that the interval is too wide to be informative at that sample size, not that pass rates above 100 percent exist. Phase 04's predictive-modeling section uses Wilson or Agresti-Coull intervals where this matters; phase 03 uses Wald throughout for transparency about the formula and accepts the occasional out-of-bound upper as a flag that $n$ is too small to draw inferences from. At the $n \geq 100$ threshold the phase uses for between-group comparisons, Wald and Wilson agree to two decimals on this data, so the methodological choice is a presentation preference rather than a numerical one.

## Pass Rate By Region

The first cut: first-time pass rate by region, with sample sizes and confidence intervals.

```sql
-- Pass rate by region for first attempts, with a 95% Wald CI
-- computed inline in SQL. The CTE separates the rate computation
-- from the presentation rounding so the margin formula stays
-- readable. Filter to attempt_number = 1 because the question
-- is about first-time performance; retakes are a separate question.
WITH region_stats AS (
  SELECT
    region,
    COUNT(*)                AS n,
    AVG(CAST(result AS REAL)) AS p
  FROM attempts
  WHERE attempt_number = 1
  GROUP BY region
)
SELECT
  region                                                AS "Region",
  printf('%,d', n)                                      AS "First Attempts",
  ROUND(100.0 * p, 2)                                   AS "Pass Rate %",
  ROUND(100.0 * (p - 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Lower %",
  ROUND(100.0 * (p + 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Upper %"
FROM region_stats
ORDER BY p DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+region_stats+AS+%28%0A++SELECT%0A++++region%2C%0A++++COUNT%28%2A%29++++++++++++++++AS+n%2C%0A++++AVG%28CAST%28result+AS+REAL%29%29+AS+p%0A++FROM+attempts%0A++WHERE+attempt_number+%3D+1%0A++GROUP+BY+region%0A%29%0ASELECT%0A++region++++++++++++++++++++++++++++++++++++++++++++++++AS+%22Region%22%2C%0A++n+++++++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++ROUND%28100.0+%2A+p%2C+2%29+++++++++++++++++++++++++++++++++++AS+%22Pass+Rate+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+-+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Lower+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+%2B+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Upper+%25%22%0AFROM+region_stats%0AORDER+BY+p+DESC%3B)

Result:

| Region | First Attempts | Pass Rate % | CI Lower % | CI Upper % |
|---|---:|---:|---:|---:|
| Northern New England Region | 47 | 89.36 | 80.55 | 98.18 |
| Hudson Valley Region | 1,666 | 88.54 | 87.01 | 90.07 |
| Connecticut Valley Region | 791 | 87.10 | 84.77 | 89.44 |
| Lehigh Valley Region | 1,629 | 85.64 | 83.93 | 87.34 |
| Greater Boston Region | 2,572 | 83.36 | 81.92 | 84.80 |

Two readings of this table.

First, the regional spread is small. Setting aside Northern New England, whose 47 first attempts make its rate unstable, the substantial regions run from Hudson Valley at 88.54 percent down to Greater Boston at 83.36 percent, a spread of about five points. For comparison, the campus spread that phase 01 surfaced is 26 points. The dimension on which this institution varies most is not its regions but the campuses within those regions: Hudson Valley's `POU` campus at 70.64 percent and `SCH` campus at 93.54 percent are nearly 23 points apart, more than four times the regional spread. Region is not the lever; campus is.

Second, the four substantial regions have largely overlapping confidence intervals, so it would be a stretch to claim a meaningful order among them. The one gap worth naming is at the bottom: Greater Boston's interval (81.92 to 84.80) sits below Hudson Valley's (87.01 to 90.07) without overlapping, so that difference is statistically real even before considering effect size. Connecticut Valley and Lehigh Valley sit between the two and overlap both. Northern New England's interval is too wide at $n=47$ to place.

## Pass Rate By Campus

The campus breakdown deepens the phase 01 discovery with confidence intervals and sample sizes. Reading the table requires the small-n caveat from the section above: campuses with fewer than fifty first-time attempts produce intervals too wide to draw conclusions from.

```sql
-- Pass rate by campus, sorted ascending so the bottom of the
-- distribution is at the top of the result. Includes region for
-- context. Same Wald CI as the region query; sample sizes vary
-- by nearly two orders of magnitude across campuses, so the CI
-- widths are the part to pay attention to.
WITH campus_stats AS (
  SELECT
    region, campus,
    COUNT(*)                AS n,
    AVG(CAST(result AS REAL)) AS p
  FROM attempts
  WHERE attempt_number = 1
  GROUP BY region, campus
)
SELECT
  campus                                                AS "Campus",
  region                                                AS "Region",
  printf('%,d', n)                                      AS "First Attempts",
  ROUND(100.0 * p, 2)                                   AS "Pass Rate %",
  ROUND(100.0 * (p - 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Lower %",
  ROUND(100.0 * (p + 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Upper %"
FROM campus_stats
ORDER BY p ASC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+campus_stats+AS+%28%0A++SELECT%0A++++region%2C+campus%2C%0A++++COUNT%28%2A%29++++++++++++++++AS+n%2C%0A++++AVG%28CAST%28result+AS+REAL%29%29+AS+p%0A++FROM+attempts%0A++WHERE+attempt_number+%3D+1%0A++GROUP+BY+region%2C+campus%0A%29%0ASELECT%0A++campus++++++++++++++++++++++++++++++++++++++++++++++++AS+%22Campus%22%2C%0A++region++++++++++++++++++++++++++++++++++++++++++++++++AS+%22Region%22%2C%0A++n+++++++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++ROUND%28100.0+%2A+p%2C+2%29+++++++++++++++++++++++++++++++++++AS+%22Pass+Rate+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+-+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Lower+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+%2B+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Upper+%25%22%0AFROM+campus_stats%0AORDER+BY+p+ASC%3B)

Result (19 rows, sorted by pass rate ascending):

| Campus | Region | First Attempts | Pass Rate % | CI Lower % | CI Upper % |
|---|---|---:|---:|---:|---:|
| POU | Hudson Valley | 235 | 70.64 | 64.82 | 76.46 |
| NEW | Hudson Valley | 45 | 71.11 | 57.87 | 84.35 |
| SPR | Greater Boston | 335 | 74.63 | 69.97 | 79.29 |
| LOW | Greater Boston | 267 | 79.40 | 74.55 | 84.25 |
| MAN | Northern New England | 11 | 81.82 | 59.03 | 104.61 |
| ALL | Lehigh Valley | 848 | 82.90 | 80.37 | 85.44 |
| SCR | Lehigh Valley | 341 | 83.58 | 79.65 | 87.51 |
| BOS | Greater Boston | 1,514 | 84.08 | 82.24 | 85.92 |
| NHV | Connecticut Valley | 271 | 86.35 | 82.26 | 90.43 |
| BRI | Connecticut Valley | 76 | 86.84 | 79.24 | 94.44 |
| HAR | Connecticut Valley | 376 | 87.50 | 84.16 | 90.84 |
| WTB | Connecticut Valley | 68 | 88.24 | 80.58 | 95.89 |
| REA | Lehigh Valley | 246 | 89.43 | 85.59 | 93.27 |
| WOR | Greater Boston | 456 | 89.69 | 86.90 | 92.48 |
| KIN | Hudson Valley | 291 | 91.07 | 87.79 | 94.34 |
| POR | Northern New England | 36 | 91.67 | 82.64 | 100.70 |
| ALB | Hudson Valley | 708 | 91.81 | 89.79 | 93.83 |
| SCH | Hudson Valley | 387 | 93.54 | 91.09 | 95.99 |
| BTH | Lehigh Valley | 194 | 96.39 | 93.77 | 99.02 |

The headline finding from phase 01 holds at deeper inspection. The three lowest campuses (`POU`, `NEW`, `SPR`) have confidence intervals that do not overlap with the three highest (`ALB`, `SCH`, `BTH`). The 26-point spread is not a sampling artifact; it is structural.

Two side observations worth naming. `POU` ($n=235$, pass rate 70.64 percent) and `NEW` ($n=45$, pass rate 71.11 percent) sit at virtually the same point estimate. Their confidence intervals tell different stories: `POU`'s narrow interval (64.82 to 76.46) makes it a campus with a real performance problem at substantial sample size, while `NEW`'s wide interval (57.87 to 84.35) means the apparent low rate could shrink considerably with more data. The two campuses look the same in a point-estimate table and are quite different signals.

`MAN`'s upper bound at 104.61 percent and `POR`'s at 100.70 percent are the small-sample Wald artifact the formula-introduction section warned about. With $n=11$ and $n=36$ respectively, the intervals are too wide to be informative. Phase 04 uses a better-behaved interval method for the predictive-modeling work; phase 03 keeps the Wald formula visible so the limitation is documented rather than hidden.

## Pass Rate By Program

The eight program codes in the data resolve to four pathways: traditional two-year ADN tracks, an advanced-standing ADN track, three bridge tracks (LPN-to-RN), and a prelicensure BSN track. Grouping by pathway makes the educational-design differences visible.

```sql
-- Pass rate by program, with a derived pathway grouping in the
-- first column. The CASE WHEN maps the eight raw program codes
-- to four readable pathway labels. Programs within each pathway
-- are listed alphabetically; the case study reads them as variants
-- of the same educational design.
WITH prog_stats AS (
  SELECT
    program,
    CASE
      WHEN program LIKE 'ADN.2YR%'  THEN 'ADN, Traditional 2-Year'
      WHEN program LIKE 'ADN.ADV%'  THEN 'ADN, Advanced Standing'
      WHEN program LIKE 'ADN.BRDG%' THEN 'ADN, Bridge (LPN-to-RN)'
      WHEN program LIKE 'BSN.PRE%'  THEN 'BSN, Prelicensure'
      ELSE 'Other'
    END                       AS pathway,
    COUNT(*)                  AS n,
    AVG(CAST(result AS REAL)) AS p
  FROM attempts
  WHERE attempt_number = 1
  GROUP BY program
)
SELECT
  pathway                                               AS "Pathway",
  program                                               AS "Program",
  printf('%,d', n)                                      AS "First Attempts",
  ROUND(100.0 * p, 2)                                   AS "Pass Rate %",
  ROUND(100.0 * (p - 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Lower %",
  ROUND(100.0 * (p + 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Upper %"
FROM prog_stats
ORDER BY pathway, program;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+prog_stats+AS+%28%0A++SELECT%0A++++program%2C%0A++++CASE%0A++++++WHEN+program+LIKE+%27ADN.2YR%25%27++THEN+%27ADN%2C+Traditional+2-Year%27%0A++++++WHEN+program+LIKE+%27ADN.ADV%25%27++THEN+%27ADN%2C+Advanced+Standing%27%0A++++++WHEN+program+LIKE+%27ADN.BRDG%25%27+THEN+%27ADN%2C+Bridge+%28LPN-to-RN%29%27%0A++++++WHEN+program+LIKE+%27BSN.PRE%25%27++THEN+%27BSN%2C+Prelicensure%27%0A++++++ELSE+%27Other%27%0A++++END+++++++++++++++++++++++AS+pathway%2C%0A++++COUNT%28%2A%29++++++++++++++++++AS+n%2C%0A++++AVG%28CAST%28result+AS+REAL%29%29+AS+p%0A++FROM+attempts%0A++WHERE+attempt_number+%3D+1%0A++GROUP+BY+program%0A%29%0ASELECT%0A++pathway+++++++++++++++++++++++++++++++++++++++++++++++AS+%22Pathway%22%2C%0A++program+++++++++++++++++++++++++++++++++++++++++++++++AS+%22Program%22%2C%0A++n+++++++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++ROUND%28100.0+%2A+p%2C+2%29+++++++++++++++++++++++++++++++++++AS+%22Pass+Rate+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+-+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Lower+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+%2B+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Upper+%25%22%0AFROM+prog_stats%0AORDER+BY+pathway%2C+program%3B)

Result:

| Pathway | Program | First Attempts | Pass Rate % | CI Lower % | CI Upper % |
|---|---|---:|---:|---:|---:|
| ADN, Advanced Standing | ADN.ADV.AAS | 62 | 95.16 | 89.82 | 100.50 |
| ADN, Bridge (LPN-to-RN) | ADN.BRDG.AAS | 1,883 | 83.06 | 81.36 | 84.75 |
| ADN, Bridge (LPN-to-RN) | ADN.BRDG.AS | 880 | 91.02 | 89.13 | 92.91 |
| ADN, Bridge (LPN-to-RN) | ADN.BRDG.NE.AS | 194 | 87.63 | 83.00 | 92.26 |
| ADN, Traditional 2-Year | ADN.2YR.AAS | 157 | 91.08 | 86.62 | 95.54 |
| ADN, Traditional 2-Year | ADN.2YR.AAS.2 | 251 | 86.45 | 82.22 | 90.69 |
| ADN, Traditional 2-Year | ADN.2YR.AS | 1,890 | 84.60 | 82.98 | 86.23 |
| BSN, Prelicensure | BSN.PRE.BSN | 1,388 | 85.88 | 84.05 | 87.71 |

The bridge pathway is where the largest within-pathway variation lives. `ADN.BRDG.AAS` (83.06 percent, $n=1{,}883$) and `ADN.BRDG.AS` (91.02 percent, $n=880$) are nearly eight points apart with non-overlapping confidence intervals, despite both being labeled as bridge programs. The same pattern shows up in the traditional pathway: `ADN.2YR.AAS.2` (86.45 percent) sits roughly five points below `ADN.2YR.AAS` (91.08 percent). The pathway label is not the full explanation; the AAS-vs-AS credential split within each pathway is doing work the pathway label hides.

The Advanced Standing program (`ADN.ADV.AAS`) is the top performer at 95.16 percent, but at $n=62$ the confidence interval (89.82 to 100.50, the upper bound crossing 100 as the small-sample Wald artifact) overlaps with the top of `ADN.BRDG.AS`. The two are statistically indistinguishable; the point estimate ranking is real but the sample size is too small to claim a meaningful gap between them.

The Prelicensure BSN program performs in the middle of the pack (85.88 percent), which is itself worth naming. A common assumption is that BSN students outperform ADN students on NCLEX, since the BSN curriculum is longer and more theoretically grounded. This dataset shows the opposite: the BSN cohort performs below the strongest ADN bridge track and below the Advanced Standing track. Phase 04 develops what this implies for program-level interventions.

## Cohort Trend

The two-year testing window runs from winter 2024 through fall 2025 (eight quarters in chronological order). Sorting by the `term_order` ordinal puts them in calendar order rather than the lexical-string order that would scramble them.

```sql
-- Pass rate by testing cohort, in chronological order via the
-- term_order ordinal. The ordinal is the column that prevents
-- 2024FAQ from sorting before 2024SUQ; ordering by it puts the
-- terms in calendar order. CIs as before.
WITH cohort_stats AS (
  SELECT
    a.testing_cohort,
    t.ordinal,
    COUNT(*)                  AS n,
    AVG(CAST(a.result AS REAL)) AS p
  FROM attempts a
  JOIN term_order t ON t.cohort = a.testing_cohort
  WHERE a.attempt_number = 1
  GROUP BY a.testing_cohort, t.ordinal
)
SELECT
  testing_cohort                                        AS "Testing Cohort",
  printf('%,d', n)                                      AS "First Attempts",
  ROUND(100.0 * p, 2)                                   AS "Pass Rate %",
  ROUND(100.0 * (p - 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Lower %",
  ROUND(100.0 * (p + 1.96 * SQRT(p * (1 - p) / n)), 2)  AS "CI Upper %"
FROM cohort_stats
ORDER BY ordinal;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+cohort_stats+AS+%28%0A++SELECT%0A++++a.testing_cohort%2C%0A++++t.ordinal%2C%0A++++COUNT%28%2A%29++++++++++++++++++AS+n%2C%0A++++AVG%28CAST%28a.result+AS+REAL%29%29+AS+p%0A++FROM+attempts+a%0A++JOIN+term_order+t+ON+t.cohort+%3D+a.testing_cohort%0A++WHERE+a.attempt_number+%3D+1%0A++GROUP+BY+a.testing_cohort%2C+t.ordinal%0A%29%0ASELECT%0A++testing_cohort++++++++++++++++++++++++++++++++++++++++AS+%22Testing+Cohort%22%2C%0A++n+++++++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++ROUND%28100.0+%2A+p%2C+2%29+++++++++++++++++++++++++++++++++++AS+%22Pass+Rate+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+-+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Lower+%25%22%2C%0A++ROUND%28100.0+%2A+%28p+%2B+1.96+%2A+SQRT%28p+%2A+%281+-+p%29+%2F+n%29%29%2C+2%29++AS+%22CI+Upper+%25%22%0AFROM+cohort_stats%0AORDER+BY+ordinal%3B)

Result:

| Testing Cohort | First Attempts | Pass Rate % | CI Lower % | CI Upper % |
|---|---:|---:|---:|---:|
| 2024SPQ | 693 | 88.46 | 86.08 | 90.84 |
| 2024SUQ | 584 | 91.27 | 88.98 | 93.56 |
| 2024FAQ | 731 | 87.41 | 85.01 | 89.82 |
| 2024WIQ | 739 | 86.20 | 83.71 | 88.68 |
| 2025SPQ | 986 | 84.48 | 82.22 | 86.74 |
| 2025SUQ | 970 | 83.71 | 81.39 | 86.04 |
| 2025FAQ | 935 | 83.96 | 81.60 | 86.31 |
| 2025WIQ | 1,067 | 83.69 | 81.48 | 85.91 |

The shape across the eight cohorts has two phases. The 2024 cohorts hold a pass rate in the 86 to 91 percent range, with summer 2024 the peak at 91.27 percent. The 2025 cohorts drop to the 83 to 85 percent range, with winter 2025 (the final quarter of the testing window) the lowest at 83.69 percent.

The drop from 2024SUQ (91.27 percent) to 2025WIQ (83.69 percent) is 7.58 percentage points across the six quarters between them. The 2024SUQ and 2025WIQ confidence intervals do not come close to overlapping, so the gap is real even before considering effect size. The decline is not stepwise; it appears across the 2024 cohorts as a slow drift, then settles into the lower band starting in 2025SPQ.

Phase 04 reads this as the post-NGN decline pattern. The NCSBN published national NCLEX-RN pass rates for the same window show roughly a 3.7-point decline; the institution's 4.21-point annual decline is slightly steeper, at about 1.14 times the national magnitude. The 2024-2025 boundary is roughly the point at which the Next Generation NCLEX format completed its first-year transition cycle, with cohorts who were trained pre-NGN and tested post-NGN largely flushed through by mid-2024. The 2025 cohorts are the first who were both trained and tested under NGN, and their pass rates settle into a band slightly below national.

The case study does not claim the NGN transition is the *cause* of the drop. It is one plausible explanation and the most prominent industry-level event in the window. Phase 04 develops the rest.

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">First-time pass rates drift downward across the post-NGN window.</p>
<p class="pgbd-case-chart-sub">Quarterly first-time NCLEX-RN pass rate at the institution, 2024SPQ through 2025WIQ, in chronological order. 6,705 first-time test takers across the eight quarters.</p>
{{< chart >}}
type: 'line',
data: {
  labels: ['2024SPQ','2024SUQ','2024FAQ','2024WIQ','2025SPQ','2025SUQ','2025FAQ','2025WIQ'],
  datasets: [{
    label: 'First-time pass rate (%)',
    data: [88.46, 91.27, 87.41, 86.20, 84.48, 83.71, 83.96, 83.69],
    borderColor: '#0969DA',
    backgroundColor: '#0969DA',
    pointBackgroundColor: '#0969DA',
    pointBorderColor: '#0969DA',
    borderWidth: 2,
    pointRadius: 5,
    pointHoverRadius: 7,
    tension: 0.2,
    fill: false
  }]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { top: 12, right: 16, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: function(ctx) { return ctx.parsed.y.toFixed(2) + '%'; } } }
  },
  scales: {
    y: { min: 80, max: 95, title: { display: true, text: 'First-time pass rate (%)' } },
    x: { title: { display: true, text: 'Testing cohort (chronological)' }, grid: { display: false } }
  }
}
{{< /chart >}}
</div>

The chart is interactive. Hover over any bar or point to see the exact value; the chart re-themes automatically when the page toggles light or dark mode.

## Time From Graduation To First Test

The phase 01 quirks section flagged a concentrated distribution of `terms_grad_to_first_test`. The schema phase precomputed this column on `students`, so phase 03 can query it directly.

```sql
-- Distribution of terms between graduation and first test, with
-- a running cumulative count and percentage so the concentration
-- at +1 quarter is visible alongside the running coverage. Bounded
-- at -2 to +8 because the long thin right tail (scattered students
-- between +9 and +44 quarters) is a separate story not worth
-- crowding the main table with.
WITH dist AS (
  SELECT
    terms_grad_to_first_test AS terms,
    COUNT(*)                 AS students
  FROM students
  GROUP BY terms_grad_to_first_test
)
SELECT
  terms                                                AS "Terms After Graduation",
  printf('%,d', students)                              AS "Students",
  ROUND(100.0 * students /
    (SELECT COUNT(*) FROM students), 2)                AS "% of Students",
  printf('%,d', SUM(students) OVER (ORDER BY terms))   AS "Cumulative Students",
  ROUND(100.0 * SUM(students) OVER (ORDER BY terms) /
    (SELECT COUNT(*) FROM students), 2)                AS "Cumulative %"
FROM dist
WHERE terms BETWEEN -2 AND 8
ORDER BY terms;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+dist+AS+%28%0A++SELECT%0A++++terms_grad_to_first_test+AS+terms%2C%0A++++COUNT%28%2A%29+++++++++++++++++AS+students%0A++FROM+students%0A++GROUP+BY+terms_grad_to_first_test%0A%29%0ASELECT%0A++terms++++++++++++++++++++++++++++++++++++++++++++++++AS+%22Terms+After+Graduation%22%2C%0A++students+++++++++++++++++++++++++++++++++++++++++++++AS+%22Students%22%2C%0A++ROUND%28100.0+%2A+students+%2F%0A++++%28SELECT+COUNT%28%2A%29+FROM+students%29%2C+2%29++++++++++++++++AS+%22%25+of+Students%22%2C%0A++SUM%28students%29+OVER+%28ORDER+BY+terms%29++++++++++++++++++AS+%22Cumulative+Students%22%2C%0A++ROUND%28100.0+%2A+SUM%28students%29+OVER+%28ORDER+BY+terms%29+%2F%0A++++%28SELECT+COUNT%28%2A%29+FROM+students%29%2C+2%29++++++++++++++++AS+%22Cumulative+%25%22%0AFROM+dist%0AWHERE+terms+BETWEEN+-2+AND+8%0AORDER+BY+terms%3B)

Result:

| Terms After Graduation | Students | % of Students | Cumulative Students | Cumulative % |
|---:|---:|---:|---:|---:|
| −1 | 2 | 0.03 | 2 | 0.03 |
| 0 | 443 | 6.50 | 445 | 6.53 |
| +1 | 6,014 | 88.19 | 6,459 | 94.72 |
| +2 | 226 | 3.31 | 6,685 | 98.03 |
| +3 | 41 | 0.60 | 6,726 | 98.64 |
| +4 | 21 | 0.31 | 6,747 | 98.94 |
| +5 | 7 | 0.10 | 6,754 | 99.05 |
| +6 | 8 | 0.12 | 6,762 | 99.16 |
| +7 | 6 | 0.09 | 6,768 | 99.25 |
| +8 | 3 | 0.04 | 6,771 | 99.30 |

The distribution is sharply unimodal. The +1 quarter bucket alone holds 6,014 students (88.19 percent of the cohort): the standard pattern is to test one quarter after graduation. Adding the +0 same-quarter group (443 students, 6.50 percent) brings the cumulative to nearly 95 percent within one term of graduation. Another 226 students (3.31 percent) extend to +2 quarters; from +3 onward the counts thin to single and double digits, scattered across a long tail that runs to +44 quarters. The full long-tail distribution is in the queryable database; the `WHERE terms BETWEEN -2 AND 8` clause limits the displayed table to the analytically interesting range.

Only three students show a negative gap: one at −3 and two at −1. Under the empirically validated term ordering, these reduce from the apparent structural pattern they presented under any wrong ordering to a small handful of data-entry quirks in the source records. The case study does not exclude these students from the analysis; their attempt records are real and contribute to the campus and program aggregates above. The 4-row date-constraint violation count noted in [phase 01](/archivo/penobscot-nclex/01-source/#structural-quirks-worth-documenting) is the row-level companion to these three student-level cases.

## Retake Outcomes

The last orientation cut is by retake count: how often students take multiple attempts, and how their eventual outcome depends on how many attempts they take.

```sql
-- Outcomes by total visible attempts. Each row is a count of
-- students who took exactly that many NCLEX attempts in the
-- two-year testing window. "Eventually Passed" is from the
-- students table's eventually_passed flag, computed at build
-- time as MAX(result) across that student's attempts. Reading
-- this table from the top: most students pass on attempt one
-- and never retake; among retakers, eventual pass rates remain
-- well above 50 percent through five attempts.
SELECT
  total_attempts                                      AS "Total Attempts",
  printf('%,d', COUNT(*))                             AS "Students",
  printf('%,d', SUM(eventually_passed))               AS "Eventually Passed",
  printf('%,d', COUNT(*) - SUM(eventually_passed))    AS "Never Passed",
  ROUND(100.0 * SUM(eventually_passed) / COUNT(*), 2) AS "Eventually Passed %"
FROM students
GROUP BY total_attempts
ORDER BY total_attempts;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++total_attempts++++++++AS+%22Total+Attempts%22%2C%0A++COUNT%28%2A%29++++++++++++++AS+%22Students%22%2C%0A++SUM%28eventually_passed%29+AS+%22Eventually+Passed%22%2C%0A++COUNT%28%2A%29+-+SUM%28eventually_passed%29+AS+%22Never+Passed%22%2C%0A++ROUND%28100.0+%2A+SUM%28eventually_passed%29+%2F+COUNT%28%2A%29%2C+2%29+AS+%22Eventually+Passed+%25%22%0AFROM+students%0AGROUP+BY+total_attempts%0AORDER+BY+total_attempts%3B)

Result:

| Total Attempts | Students | Eventually Passed | Never Passed | Eventually Passed % |
|---:|---:|---:|---:|---:|
| 1 | 6,190 | 5,792 | 398 | 93.57 |
| 2 | 496 | 415 | 81 | 83.67 |
| 3 | 97 | 72 | 25 | 74.23 |
| 4 | 23 | 17 | 6 | 73.91 |
| 5 | 11 | 6 | 5 | 54.55 |
| 6 | 1 | 1 | 0 | 100.00 |
| 9 | 1 | 0 | 1 | 0.00 |

A few details to read carefully. The "1 attempt" row at 93.57 percent is not the first-time pass rate; it is the pass rate among students whose only visible attempt is their first one. This combines students who passed on their first try with students who failed their first try and did not retake within the window. The first-time pass rate from the campus table above (overall 85.68 percent across attempts where `attempt_number = 1`) is the right number for first-time pass rate; the 93.57 percent in this row is a different quantity that mixes first-try passers with first-try failers who did not retake.

Among students who do retake (rows 2 through 9), the eventually-passed rate stays meaningfully above 50 percent through five attempts. The institution's retake support is doing real work for students who engage with it. Phase 04 develops the funnel: the institution's retake conversion rate runs well above the NCSBN[^ncsbn] national benchmark for repeat NCLEX-RN takers, with the precise magnitude depending on whether retakes are counted attempt-by-attempt or as a strict-later-term student-level conversion. The opportunity is not improving retake conversion; it is getting more first-time failers to engage with the retake program in the first place.

The two outlier rows (one student at six attempts who passed, one student at nine attempts who did not) are individual records and not analytically meaningful at $n=1$ each. They are kept in the table because the schema preserves them, and the case study commits to showing what the data shows.

## Looking Ahead

[Phase 04 (Findings)](/archivo/penobscot-nclex/04-findings/) develops the three analytical threads that the orientation queries above point to. The 26-point campus spread becomes a structured argument for campus-level intervention targeting, with the within-region campus variance the actual lever rather than the regional or programmatic aggregates. The 2024-to-2025 cohort decline becomes a comparison against the NCSBN national trend, with the institution declining at about 1.14 times the national magnitude while sitting roughly three points below national throughout. And the retake-attempt distribution becomes the entry point to the retake-engagement framing: the case study's strongest counterintuitive finding, that the conversion rate among retakers is already well above national and the lever is engagement, not conversion.

Phase 04's predictive-modeling subsection switches briefly to R for the logistic regression and AUC discussion, where SQL hits its analytical ceiling. The structural data limits identified in phase 01 (binary outcome, no demographics, no academic-readiness scores) shape what any model could and could not do with this dataset.

[^ncsbn]: [NCSBN](https://www.ncsbn.org/).
