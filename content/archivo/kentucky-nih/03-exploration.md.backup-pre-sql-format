---
title: "Exploration"
weight: 30
description: "First-pass queries against the database to see what twenty-one years of NIH funding in Kentucky actually looks like, including yearly trends, the institutional concentration, and the ARRA stimulus visible in the 2009 data."
summary: "Phase 3: First-pass queries"
tags: ["sql", "sqlite", "exploratory-analysis", "datasette"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
First-pass queries to see what the data says, and the questions worth following further.
{{< /lead >}}

## At a Glance

The schema phase produced a queryable database with three tables and known invariants. The natural first move is breadth before depth: run a handful of queries that cover the obvious dimensions (time, organization, category, funding mechanism) without yet reaching for window functions or CTEs. See what the data says at a glance, then decide which questions are worth following further.

This is the [exploration phase](/biblioteca/#the-phased-walkthrough) the case study philosophy describes: not the analysis, but the orientation. Findings live in the next phase. The four queries below are the act of getting bearings, the moments of "what does this dataset actually contain" that shape every deeper question that comes later.

Every SQL block in this phase has a [Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite) link below it so the reader can run the query directly in the browser against the same database, no setup required. The expected output shown alongside each query is the actual output from the live database: anyone running the query gets the same numbers shown here, or this case study fails its own [reproducibility-is-the-floor](/biblioteca/#reproducibility-is-the-floor-review-is-the-ceiling) test.

## Funding By Year

The first query, and the one that anchors most of the later analysis. Annual NIH funding totals across the twenty-one fiscal years in the dataset:

```sql
-- Annual NIH funding to Kentucky, fiscal years 2005 through 2025.
-- Joins through project_funders so the 25 percent of projects without
-- disclosed cost data are excluded automatically (see phase 02).
-- CAST(fiscal_year AS INTEGER) drops the .0 from the float storage;
-- ROUND on millions keeps the displayed precision consistent.
SELECT
    CAST(p.fiscal_year AS INTEGER)             AS "Fiscal Year",
    -- Sum total_cost_ic (the per-funder split), not total_cost (which
    -- is identical across co-funded rows and would double-count). The
    -- co-funding invariant verified in phase 02 is what makes this safe.
    ROUND(SUM(f.total_cost_ic) / 1e6, 1)       AS "Funding ($M)"
FROM projects p
JOIN project_funders f USING (application_id)
GROUP BY p.fiscal_year
ORDER BY p.fiscal_year;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+CAST%28p.fiscal_year+AS+INTEGER%29+AS+%22Fiscal+Year%22%2C+ROUND%28SUM%28f.total_cost_ic%29+%2F+1e6%2C+1%29+AS+%22Funding+%28%24M%29%22+FROM+projects+p+JOIN+project_funders+f+USING+%28application_id%29+GROUP+BY+p.fiscal_year+ORDER+BY+p.fiscal_year%3B)

Result:

```text
Fiscal Year   Funding ($M)
       2005          198.5
       2006          175.6
       2007          174.5
       2008          184.1
       2009          248.0
       2010          233.8
       2011          192.1
       2012          199.0
       2013          183.6
       2014          198.5
       2015          199.2
       2016          175.8
       2017          196.7
       2018          215.4
       2019          237.3
       2020          254.9
       2021          260.9
       2022          243.0
       2023          237.7
       2024          241.6
       2025          235.2
```

Two things to call out about the query itself. First, the join goes through `project_funders` so the 3,580 zero-disclosure rows from [phase 02](/archivo/kentucky-nih/02-schema/#the-25-percent-missing-cost-pattern) are automatically excluded. Asking the same question against `projects` directly with `SUM(total_cost)` would double-count the co-funded projects. The schema makes the right answer the easy answer.

Second, summing `total_cost_ic` (the per-funder split) rather than `total_cost` (the project-level total) is what the [co-funding invariant](/archivo/kentucky-nih/02-schema/#verifying-the-co-funding-invariant) entitles you to do. The schema phase verified that the splits sum to the totals; this query relies on that verification.

The shape is two distinct phases. The first decade (2005-2014) sits in a band roughly between $174M and $248M, with the 2009 ARRA spike as the obvious outlier. The second decade (2015-2025) shifts upward, climbing from a 2016 dip of $175.8M to a peak of $260.9M in 2021 and holding above $235M through 2025. The decade-over-decade growth is a real story; the deeper analysis of where that growth concentrated is in the next phase.

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Kentucky NIH funding peaked at $260.9M in FY 2021, with the 2009 ARRA stimulus visible as the early-decade spike.</p>
<p class="pgbd-case-chart-sub">Annual NIH funding awarded to Kentucky institutions, FY 2005 through FY 2025. The full window spans two distinct decade-shaped phases: a 2005-2014 band roughly between $175M and $248M, and a 2015-2025 climb to a sustained $230M+ baseline.</p>
{{< chart >}}
type: 'line',
data: {
  labels: [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
  datasets: [
    {
      label: 'Annual funding ($M)',
      data: [198.5, 175.6, 174.5, 184.1, 248.0, 233.8, 192.1, 199.0, 183.6, 198.5, 199.2, 175.8, 196.7, 215.4, 237.3, 254.9, 260.9, 243.0, 237.7, 241.6, 235.2],
      borderColor: '#0969DA',
      backgroundColor: 'rgba(9, 105, 218, 0.10)',
      borderWidth: 2,
      fill: true,
      tension: 0.2,
      pointRadius: 2.5,
      pointHoverRadius: 5,
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: function(context) {
          return '$' + context.parsed.y.toFixed(1) + 'M';
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

The chart is interactive. Hover over any point to see the exact dollar amount; the chart re-themes automatically when the page toggles light or dark mode.

A line chart is the right shape per the [chart selection guidance](/mirador/#chart-selection): a single time series with twenty-one observations and a continuous trend reads cleanly as a line. A bar chart would compete with the eye for the question "what's the trend"; the line answers it directly. The chart uses the same Chart.js infrastructure the [taller dashboard](/taller/) uses, so it handles light and dark mode automatically.

## Top Institutions

The second obvious cut: who actually does this research?

```sql
-- Top ten Kentucky institutions by project count across the full window.
-- COUNT(*) on projects (one row per Application ID) is the right unit:
-- a project is a project regardless of how many funders co-funded it.
-- Display-friendly aliases keep the result readable.
SELECT
    organization_name AS "Institution",
    COUNT(*)          AS "Projects"
FROM projects
GROUP BY organization_name
ORDER BY COUNT(*) DESC
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+organization_name+AS+%22Institution%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+projects+GROUP+BY+organization_name+ORDER+BY+COUNT%28*%29+DESC+LIMIT+10%3B)

Result:

```text
Institution                                         Projects
UNIVERSITY OF KENTUCKY                                 7,835
UNIVERSITY OF LOUISVILLE                               4,279
KY ST CABINET/HEALTH/FAMILY SERVICES                     380
VA MEDICAL CENTER - LEXINGTON, KY                        137
LOUISVILLE VA MEDICAL MEDICAL CENTER                      65
NAPROGENIX, INC                                           51
MURRAY STATE UNIVERSITY                                   46
KENTUCKY STATE ADMINISTRATIVE OFFICE OF THE COURTS        44
NORTHERN KENTUCKY UNIVERSITY                              33
WESTERN KENTUCKY UNIVERSITY                               32
```

The University of Kentucky and the University of Louisville together account for 12,114 of the 13,876 projects, just over 87 percent of the dataset. The Kentucky NIH funding picture is substantially the picture of two large public research universities. The long tail is small but interesting: a state public-health cabinet (380 projects), the Lexington and Louisville VA medical centers, a small biotech (Naprogenix), and three of the state's regional public universities (Murray State, Northern Kentucky, Western Kentucky) at the bottom of the top ten.

The duplicate "MEDICAL" in "LOUISVILLE VA MEDICAL MEDICAL CENTER" is real, not a transcription error. RePORTER's organization-name field is unnormalized: institutions appear with whatever exact text the grant submitter entered, including typos. Phase 04's institutional comparisons treat this case carefully (the Louisville VA may show up in two distinct organization spellings across the dataset).

The build script in [phase 02](/archivo/kentucky-nih/02-schema/#the-build-script) deliberately does NOT normalize organization names. The decision was: an analyst who wants to roll up VA medical center variants under a single canonical entity can write a `CASE WHEN` or a `LIKE` clause in their query; an analyst who wants to keep the variants distinct (because they may represent different organizational units, different decades of naming convention, or different administrative structures) can do that without first having to undo a normalization the build script imposed. Trusting the analyst to make the right call for their question keeps the data faithful to what RePORTER published. The cost is that any reader running aggregations against `organization_name` should double-check whether duplicate entries with similar spellings actually represent the same institution or two distinct ones — a five-second `GROUP BY organization_name LIKE '%LOUISVILLE VA%'` query answers it.

This is a Kentucky-specific finding rather than a generalizable claim about state-level NIH funding. A state with three or four roughly equal research universities (Texas, North Carolina, Massachusetts) would produce a flatter distribution. Kentucky's bimodal one-and-a-half-institution shape is particular to its higher-education landscape, and the next phase looks at how UK and U of L diverge in what they fund.

## NIH Spending Categories

The category breakdown across the full twenty-one-year window. The schema phase exploded the multi-valued NIH Spending Categorization field into its own table; that work pays off here, where asking "what topics does the funding cluster around" is a clean indexed group-by:

```sql
-- Top ten NIH spending categories across all Kentucky projects.
-- Filters out 'No NIH Category available' (the literal placeholder for
-- projects that predate categorization or have not yet been tagged); it
-- would otherwise crowd the top of the list with non-information.
SELECT
    c.category  AS "Category",
    COUNT(*)    AS "Projects"
FROM project_categories c
WHERE c.category != 'No NIH Category available'
GROUP BY c.category
ORDER BY COUNT(*) DESC
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+c.category+AS+%22Category%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+project_categories+c+WHERE+c.category+%21%3D+%27No+NIH+Category+available%27+GROUP+BY+c.category+ORDER+BY+COUNT%28*%29+DESC+LIMIT+10%3B)

Result:

```text
Category                          Projects
Neurosciences                        2,505
Clinical Research                    2,492
Prevention                           1,998
Cancer                               1,796
Genetics                             1,760
Brain Disorders                      1,731
Biotechnology                        1,373
Behavioral and Social Science        1,352
Aging                                1,323
Nutrition                            1,242
```

This is a recognizably general-research portrait dominated by Neurosciences and Clinical Research nearly tied at the top, followed by a tight cluster of Prevention, Cancer, Genetics, and Brain Disorders. Two follow-up questions are worth answering directly with one more query, since intuition might predict different topics for Kentucky:

```sql
-- Where do Kentucky-relevant categories actually rank?
-- Substance Misuse, Rural Health, and Tobacco are the topics intuition
-- might predict for the state given its demographic and agricultural
-- profile. The query checks their actual project counts.
SELECT
    c.category  AS "Category",
    COUNT(*)    AS "Projects"
FROM project_categories c
WHERE c.category IN (
    'Substance Misuse',
    'Rural Health',
    'Tobacco',
    'Tobacco Smoke and Health'
)
GROUP BY c.category
ORDER BY COUNT(*) DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+c.category+AS+%22Category%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+project_categories+c+WHERE+c.category+IN+%28%27Substance+Misuse%27%2C+%27Rural+Health%27%2C+%27Tobacco%27%2C+%27Tobacco+Smoke+and+Health%27%29+GROUP+BY+c.category+ORDER+BY+COUNT%28*%29+DESC%3B)

Result:

```text
Category                  Projects
Substance Misuse             1,125
Rural Health                   530
Tobacco                        158
Tobacco Smoke and Health       147
```

Substance Misuse sits at 1,125 projects, just below the top ten cutoff but a substantial cluster reflecting Kentucky's documented role in opioid response research. Rural Health at 530 is meaningful but smaller than the headline categories. Tobacco research is genuinely modest given the state's agricultural history (158 projects), and Tobacco Smoke and Health adds another 147. The Appalachian-region research footprint that frames the case-study landing page is real but more diffuse than the framing might imply: it shows up across many categories rather than concentrating in a few state-specific ones.

## The ARRA Spike

The annual funding query surfaced one number that does not fit the surrounding pattern: 2009 sits well above its 2007-2011 neighbors at $248.0 million, the highest year of the first decade. The reason is the [American Recovery and Reinvestment Act](https://en.wikipedia.org/wiki/American_Recovery_and_Reinvestment_Act_of_2009), signed into law in February 2009, which directed roughly $10.4 billion in stimulus funding to NIH for distribution across two fiscal years.

The grant count tells the story more clearly than the dollar total. 2009 had 896 distinct projects against neighbors of 720-780:

```sql
-- Project counts for the years immediately surrounding the 2009 ARRA spike.
-- The 2007-2011 window shows two pre-ARRA baseline years, the 2009 spike,
-- the 2010 ARRA-extended year (supplements often spanned two fiscal years),
-- and the 2011 return to baseline. Five rows is enough to see the shape.
SELECT
    CAST(fiscal_year AS INTEGER)  AS "Fiscal Year",
    COUNT(*)                      AS "Projects"
FROM projects
WHERE fiscal_year BETWEEN 2007 AND 2011
GROUP BY fiscal_year
ORDER BY fiscal_year;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+CAST%28fiscal_year+AS+INTEGER%29+AS+%22Fiscal+Year%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+projects+WHERE+fiscal_year+BETWEEN+2007+AND+2011+GROUP+BY+fiscal_year+ORDER+BY+fiscal_year%3B)

Result:

```text
Fiscal Year   Projects
       2007        746
       2008        732
       2009        896
       2010        782
       2011        721
```

The 896 in 2009 is roughly 150 projects above the 720-746 baseline range surrounding it. The 2010 count of 782 is also somewhat elevated, consistent with ARRA supplements often spanning two fiscal years. By 2011 the count returned to baseline. Looking at activity codes (the NIH grant-mechanism identifier) for 2009 specifically:

```sql
-- Activity-code breakdown for the 2009 spike year. The activity code
-- is NIH's grant-mechanism identifier. R01 is the standard research
-- grant; P-series codes are program-project and center mechanisms;
-- H79 is a CDC cooperative agreement; F-series codes are training
-- fellowships. The mix of codes shows whether 2009 was organic growth
-- or stimulus-driven; an unusual frequency of supplemental mechanisms
-- (P-series, R03, R21) signals stimulus.
SELECT
    activity_code  AS "Activity Code",
    COUNT(*)       AS "Grants"
FROM projects
WHERE fiscal_year = 2009
GROUP BY activity_code
ORDER BY COUNT(*) DESC
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+activity_code+AS+%22Activity+Code%22%2C+COUNT%28*%29+AS+%22Grants%22+FROM+projects+WHERE+fiscal_year+%3D+2009+GROUP+BY+activity_code+ORDER+BY+COUNT%28*%29+DESC+LIMIT+10%3B)

Result:

```text
Activity Code   Grants
R01                345
P20                130
H79                 55
R21                 52
P01                 39
R03                 24
P30                 23
P50                 13
F31                 13
P42                 12
```

The R01 (the standard NIH research grant) leads as it does every year. The unexpected entry is P20 at 130 grants, the second-most-common code in 2009. P20 is a [center grant mechanism](https://grants.nih.gov/grants/funding/funding_program.htm) often used for IDeA program awards (Institutional Development Awards) that build research capacity in states with historically lower NIH funding. Kentucky has long been an IDeA state, and the P20 surge in 2009 likely reflects ARRA-era IDeA expansion rather than a single-year random fluctuation.

The presence of multiple P-series codes in the top ten (P20, P01, P30, P50, P42 — five of the top ten) plus the small-grant supplement mechanisms (R21, R03) is the supplement-heavy mix consistent with stimulus-era funding patterns. Standard R01 grants dominate every year; the unusual signal is the breadth of the rest of the distribution. The 2009 ARRA spike is a real artifact of policy, not a data error or organic growth in Kentucky research capacity. Documenting it explicitly here matters because every later analysis that includes a year-over-year comparison has to decide whether to include or exclude 2009-2010.

## What's Worth Following Further

The first-pass queries give the shape of the data, but they answer single-dimension questions: how much funding by year, how many projects by institution, how many projects by category, what happened in 2009. The interesting questions mostly live at intersections, where two dimensions meet and the cross-tabulation surfaces patterns that neither dimension alone shows.

Three threads worth pulling in [phase 04](/archivo/kentucky-nih/04-findings/):

How have UK and U of L diverged across the twenty-one-year window? Both institutions account for ~87 percent of the data combined, but their per-year trajectories tell different stories. UK climbed from $87M in 2005 to a peak of $177M in 2021. U of L stayed in the $50-75M band across the same window, never approaching UK's growth. The slope chart that [the dashboard philosophy room](/mirador/#chart-selection) recommends for two-point comparisons would extend cleanly to a multi-year UK-vs-U-of-L visualization.

Which Institutes show real decade-over-decade shifts? The IC-by-decade comparison answers questions about which corners of NIH grew their Kentucky funding and which contracted. The answer involves a substantial NIDA growth story (drug abuse research up 61 percent decade-over-decade), an even larger NIGMS story (general medical sciences up 157 percent), and one apparent disappearance that turns out to be a structural artifact: NCRR was dissolved in 2011 and folded into the new NCATS plus several other institutes. Phase 04's query catches the rename, which a reader who saw only second-decade numbers would miss.

What does annual funding look like with the ARRA spike smoothed out? A 5-year centered moving average gives the underlying trend without the policy-shock artifact dominating the shape. Window functions handle this in one query.

These are the questions phase 04 reaches for, with window functions and common table expressions doing the work that group-bys alone cannot.
