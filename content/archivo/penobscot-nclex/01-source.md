---
title: "Source"
weight: 10
description: "Where the data came from, why the outcomes are synthetic, what the nine source columns hold, and the 26-point campus spread that surfaces in a single GROUP BY query."
summary: "Phase 1: Synthetic outcomes, real structure, and the first thread"
tags: ["csv", "data-quality", "nclex", "nursing-education", "public-data"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
The institution is anonymized and the outcome values are synthetic. The structure is real: every campus, cohort, program, and retake path comes from a real multi-campus engagement, with the pass and fail outcomes perturbed so that no published rate matches a real reported figure. The analytical patterns survive the perturbation, and every number in this case study is computed from and verifiable against the published database.
{{< /lead >}}


<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

## At a Glance

This case study takes a 7,635-attempt slice of NCLEX-RN data covering two academic years (eight quarters from 2024SPQ through 2025WIQ) at a multi-campus nursing college. The slice represents 6,819 unique students across 19 campuses in five regions. Source columns: student identifier, region, campus, program code, starting cohort, graduating cohort, testing cohort, attempt number, and a binary pass/fail result. Nothing else: no demographics, no academic readiness scores, no test-section breakdowns. The full nine-column schema is what was available in the source engagement. What is published here is a privacy-preserving version of it: the institution name (Penobscot College of Nursing), region names, and one program-code suffix are replaced, and the pass and fail outcomes are synthetic, perturbed so that no published campus rate matches a real reported figure. The structure is intact: every campus, cohort, program, attempt count, and retake path is real, the analytical patterns are preserved, and every number in the prose is computed from and verifiable against the published database.

```sql
-- Three-table row count summary used in the At a Glance section.
-- UNION ALL stacks the count of each table into a single result set.
-- The 6,819-student count, 7,635 attempts, and 52 cohort terms together
-- describe the database shape: fewer students than attempts because some
-- students retake; fewer cohort terms than the calendar suggests because
-- the source data does not include every quarter in the 21-year window.
SELECT
    'attempts'                  AS "Table",
    printf('%,d', COUNT(*))     AS "Rows"
FROM attempts
UNION ALL
SELECT
    'students',
    printf('%,d', COUNT(*))
FROM students
UNION ALL
SELECT
    'term_order',
    printf('%,d', COUNT(*))
FROM term_order;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++%27attempts%27+++AS+%22Table%22%2C%0A++++COUNT%28%2A%29+++++AS+%22Rows%22%0AFROM+attempts%0AUNION+ALL%0ASELECT%0A++++%27students%27%2C%0A++++COUNT%28%2A%29%0AFROM+students%0AUNION+ALL%0ASELECT%0A++++%27term_order%27%2C%0A++++COUNT%28%2A%29%0AFROM+term_order%3B)

Result:

| Table | Rows |
|---|---:|
| attempts | 7,635 |
| students | 6,819 |
| term_order | 52 |

The deliverable is a 1.7 MB SQLite file at [pgbd.casa/data/penobscot-nclex.sqlite](https://pgbd.casa/data/penobscot-nclex.sqlite), queryable directly in the browser via [Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite). Every query in this case study runs against that file. Every claim in the prose ties to a query the reader can re-run. The same reproducibility floor the other case studies set applies here: a reader who lands on a number in the prose and wants to verify it can click through to the query and watch the database produce it.

## Why The Outcomes Are Synthetic

NCLEX-RN performance data at the institution level is sensitive. State boards of nursing publish school-level pass rates annually, and an institution's real per-campus rates are matchable against those public figures, so publishing the real outcome values would re-identify the institution even with its name removed. This case study keeps the real structure and synthesizes the outcomes. Four things are changed: the institution name is replaced with "Penobscot College of Nursing"; the five region names are replaced with regional placeholders that preserve geographic plausibility but not identity; one program-code suffix (`.VA` for the institution's state-specific bridge program) is replaced with a neutral `.NE` suffix; and the binary pass and fail outcomes are perturbed at the campus level so that no published rate matches a real reported figure. Every other field, every count, every sample size, and the full retake structure are real and unchanged.

The perturbation is deliberately minimal and structure-preserving. Only individual pass and fail values move, and only enough to shift each campus rate off its real figure; sample sizes, group memberships, cohort sequence, and the entire retake architecture are untouched. The analytical signal this case study develops (campus-level variation, the post-NGN cohort decline, the retake conversion above national benchmarks) lives in that preserved structure, so the findings hold on the published data exactly as they held on the source. The case study's value is in the methodology and the reasoning, both of which are fully reproducible against the published database.

## What's In The File

The published CSV is one file at `data/penobscot-nclex.csv`, 7,635 rows plus a header row, nine columns of mixed types. Field meanings:

| Column | Type | Description |
|---|---|---|
| `Student` | int | Permuted student identifier, 1 to 6,819. One value per student; appears in multiple rows if the student took multiple attempts. |
| `Region` | text | One of five regions: Greater Boston, Hudson Valley, Lehigh Valley, Connecticut Valley, Northern New England. |
| `Campus` | text | One of 19 three-letter campus codes nested within the five regions. |
| `Program` | text | One of eight program codes encoding (degree level × pathway × credential type). |
| `Starting/Readmitted Cohort` | text | Term code of the student's enrollment cohort. Format: four-digit year + three-letter term (`2022WIQ`, `2023SUQ`). |
| `Graduating Cohort` | text | Term code of the student's expected or actual graduating cohort. Format same as starting cohort. |
| `Testing Cohort` | text | Term code of the quarter the NCLEX attempt was taken in. |
| `Attempt Number` | int | 1 for first attempt, 2 for second, and so on. Maximum observed: 19. |
| `Result` | int | 0 for fail, 1 for pass. |

The three-letter term codes resolve to a four-quarter academic year: `SPQ` (spring), `SUQ` (summer), `FAQ` (fall), `WIQ` (winter). The within-year ordering is `SPQ < SUQ < FAQ < WIQ`, validated empirically by a 24-permutation search over all possible orderings of the four codes: the winning ordering produces only 4 row-level constraint violations across 7,635 rows; the next-best ordering produces over 1,500. A three-orders-of-magnitude separation makes this an empirical finding rather than an assumption. Phase 02 documents the validation and introduces the `term_order` lookup table that makes the ordering queryable with a single `JOIN` instead of forcing every term-math query to embed a `CASE WHEN` clause.

The program codes are dot-separated path strings encoding degree level, pathway, and credential type. `ADN.2YR.AS` is an Associate Degree in Nursing, traditional two-year track, Associate of Science credential. `ADN.BRDG.AAS` is the same degree level via a bridge pathway (LPN-to-RN), Associate of Applied Science credential. `BSN.PRE.BSN` is a prelicensure Bachelor of Science in Nursing. The pathway distinctions matter for phase 03's program-level analysis because bridge students have meaningfully different first-time pass rates than traditional-track students. One program code (`ADN.BRDG.NE.AS`) carries an anonymized regional suffix; the original encodes a state-specific bridge variant whose disclosure would identify the institution.

## Structural Quirks Worth Documenting

Seven patterns in the source data require deliberate handling and are worth surfacing before the schema phase decides how to model around them.

**Left-censored students.** Of 6,819 distinct students in the data, 114 have no Attempt 1 row visible. Their first appearance in the published data is Attempt 2, 3, or later. The explanation is that these students took their first attempt before the window opens in 2024SPQ, failed, and only their retakes appear in the window. The number is small (1.7 percent of the cohort) but real, and phase 02 surfaces it as a `first_visible_attempt > 1` flag on the `students` table so the case study can either include or exclude this group depending on the question being asked.

**Concentrated time-from-graduation-to-test distribution.** A natural derived metric is the number of quarters between a student's graduating cohort and their first testing cohort. Under the empirically validated term ordering (phase 02), the distribution across 6,819 students is heavily concentrated at one quarter: 6,014 students (88.2 percent) test exactly one quarter after their recorded graduating cohort. 443 students (6.5 percent) test in the same quarter as graduation. 226 (3.3 percent) test two quarters later. The remaining 136 scatter across a thin tail running from three quarters out to forty-four. Only three students show a negative gap, testing in a term before their recorded graduating cohort, which under correct term ordering reduces to a small handful of data-entry quirks rather than a structural pattern. Phase 03 develops the delay-distribution analysis further; phase 01 only flags the shape.

**Date-constraint violations under correct term ordering.** Even under the validated term ordering, four attempt rows have impossible date sequences: one row where the starting term is later than the graduating term, three rows where the graduating term is later than the testing term. These are data-entry quirks in the source records, not analysis artifacts. They are preserved as-published in the database rather than silently dropped (the alternative would hide them) and they materially affect no aggregate. The 4-row count is the number that survives after the term-ordering validation, down from the 1,500-plus that any wrong ordering would produce.

**Long retake tails.** Attempt numbers run from 1 to 19. The distribution is heavily concentrated at attempt 1 (6,705 of 7,635 rows) and falls quickly through 2 (675 rows), 3 (162), 4 (56). Three students appear at attempt 9, one each at 17, 18, and 19. The long tail is preserved as-published because it carries real analytical signal: students who retake many times tell a different story than students who pass on the first or second try.

**Binary outcome, no score detail.** The `Result` column is binary. The actual NCLEX-RN scoring system is more nuanced (the computerized adaptive test reports passing as a confidence boundary in logit units, with detailed section feedback for failures), but the source data exposes only the binary outcome. The case study's predictive modeling discussion in phase 04 names this as the primary data-richness ceiling on what any model could achieve.

**No demographic data.** The dataset has no age, sex, race, ethnicity, prior degree, or socioeconomic indicator. The schema is institution-centric: it answers questions about campus, program, and cohort, but cannot answer questions about which students within a campus or program are at higher or lower risk. This is a real limitation, and the predictive modeling discussion treats it as the most important one.

**Term gaps in the cohort sequence.** The `term_order` table built in phase 02 has 52 rows, covering cohort terms from 2005 through 2026. The source data does not include every quarter in that 21-year window. A student with a `Starting/Readmitted Cohort` of `2008WIQ` exists in the data, but the next earliest cohort observed is `2010FAQ`, roughly two years later. The gaps are real reporting gaps in the source institution's data, not artifacts of anonymization. They matter for term-ordinal math because computing an ordinal as "number of quarters since some base" requires the base to be defined and the gaps to be acknowledged.

## The Scope Decision

The window is two academic years of testing (eight quarters from `2024SPQ` through `2025WIQ`) for students whose starting cohorts span back to 2005. The two-year testing slice is not arbitrary: it covers the period immediately after the Next Generation NCLEX (NGN)[^next-generation-nclex-ngn] format launched in April 2023, which is the most consequential structural change to the exam in two decades. Pre-NGN cohorts are not in the window; the NGN-era cohorts are. The case study takes the post-launch period as given and asks how the institution performed in it.

The institution-level scope (multi-campus, five regions, 19 campuses) lets a campus-spread thread emerge that a single-campus scope could not. Campus is the highest-resolution categorical variable in the data, and as the next section shows, it is also where the most interesting variation lives.

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Nineteen campuses, a 26-point spread in first-time pass rates.</p>
<p class="pgbd-case-chart-sub">First-time NCLEX-RN pass rate by campus, eight quarters from 2024SPQ through 2025WIQ. Sorted descending. Sample sizes on the y-axis labels.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: ['BTH (n=194)','SCH (n=387)','ALB (n=708)','POR (n=36)','KIN (n=291)','WOR (n=456)','REA (n=246)','WTB (n=68)','HAR (n=376)','BRI (n=76)','NHV (n=271)','BOS (n=1,514)','SCR (n=341)','ALL (n=848)','MAN (n=11)','LOW (n=267)','SPR (n=335)','NEW (n=45)','POU (n=235)'],
  datasets: [{
    label: 'First-time pass rate (%)',
    data: [96.39, 93.54, 91.81, 91.67, 91.07, 89.69, 89.43, 88.24, 87.50, 86.84, 86.35, 84.08, 83.58, 82.90, 81.82, 79.40, 74.63, 71.11, 70.64],
    backgroundColor: '#0969DA',
    borderColor: '#0969DA',
    pointBackgroundColor: '#0969DA',
    pointBorderColor: '#0969DA',
    borderWidth: 0
  }]
},
options: {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { top: 8, right: 16, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: function(ctx) { return ctx.parsed.x.toFixed(2) + '%'; } } }
  },
  scales: {
    x: { min: 60, max: 100, title: { display: true, text: 'First-time pass rate (%)' } },
    y: { ticks: { autoSkip: false }, grid: { display: false } }
  }
}
{{< /chart >}}
</div>

The chart is interactive. Hover over any bar or point to see the exact value; the chart re-themes automatically when the page toggles light or dark mode.

## The 26-Point Campus Spread

The first analytical thread surfaces from a single `GROUP BY campus` query. First-time pass rate by campus, sorted ascending:

```sql
-- First-time pass rate by campus across the full two-year testing window.
-- Filters to attempt_number = 1 because the question is about first-time
-- performance specifically; retakes are a separate question phase 04
-- develops. Pass rate is AVG(result) since result is 0/1. Ordering
-- ascending puts the lowest-performing campuses at the top so the
-- 26-point spread between highest and lowest is the first thing visible.
SELECT
    campus                          AS "Campus",
    printf('%,d', COUNT(*))         AS "First Attempts",
    ROUND(100.0 * AVG(result), 2)   AS "Pass Rate %"
FROM attempts
WHERE attempt_number = 1
GROUP BY campus
ORDER BY AVG(result) ASC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++campus+++++++++++++++++++++++++AS+%22Campus%22%2C%0A++++COUNT%28%2A%29+++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++++ROUND%28100.0+%2A+AVG%28result%29%2C+2%29+++AS+%22Pass+Rate+%25%22%0AFROM+attempts%0AWHERE+attempt_number+%3D+1%0AGROUP+BY+campus%0AORDER+BY+AVG%28result%29+ASC%3B)

Result:

| Campus | First Attempts | Pass Rate % |
|---|---:|---:|
| POU | 235 | 70.64 |
| NEW | 45 | 71.11 |
| SPR | 335 | 74.63 |
| LOW | 267 | 79.40 |
| MAN | 11 | 81.82 |
| ALL | 848 | 82.90 |
| SCR | 341 | 83.58 |
| BOS | 1,514 | 84.08 |
| NHV | 271 | 86.35 |
| BRI | 76 | 86.84 |
| HAR | 376 | 87.50 |
| WTB | 68 | 88.24 |
| REA | 246 | 89.43 |
| WOR | 456 | 89.69 |
| KIN | 291 | 91.07 |
| POR | 36 | 91.67 |
| ALB | 708 | 91.81 |
| SCH | 387 | 93.54 |
| BTH | 194 | 96.39 |

A 26-point spread from `POU` at 70.64 percent to `BTH` at 96.39 percent. For comparison, the spread between the highest and lowest U.S. states in published NCLEX-RN pass rates over this same period was roughly 10 to 15 percentage points. The within-institution spread is larger than the cross-state spread.

That ratio is the thread phase 04 develops most thoroughly. It also frames how the case study reasons about the data. Cohort effects, program-pathway effects, and regional effects all exist in this dataset and all matter, but none of them comes close to the campus-level variation. Whatever explains the gap between `NEW` and `BTH` is the lever the analysis is trying to surface.

The two lowest campuses, `POU` (235 attempts) and `NEW` (45 attempts), sit at nearly the same rate, but `POU` is the more telling case: at 235 first attempts it is comparable in size to the top performers and still near the bottom, so the campus spread is not a small-sample artifact.

This is how an analytical thread emerges from data. Not from a research question imposed on the data, but from a `GROUP BY` whose ordered output asks a question the reader did not already have.

## Looking Ahead

[Phase 02 (Schema)](/archivo/penobscot-nclex/02-schema/) documents the three-table normalization that turns the flat CSV into a queryable database: the per-attempt `attempts` table that mirrors the source, the per-student `students` table that derives twelve aggregates including `eventually_passed` and `total_attempts`, and the `term_order` lookup that makes term-quarter math a one-line `JOIN` instead of an embedded `CASE WHEN`.

[Phase 03 (Exploration)](/archivo/penobscot-nclex/03-exploration/) covers the orientation queries: campus first-time pass rates with confidence intervals computed inline in SQL, program-level breakdowns by pathway, cohort-level trends across the two-year window, and the time-from-graduation-to-test distribution that surfaces the concentrated pattern the source phase flagged.

[Phase 04 (Findings)](/archivo/penobscot-nclex/04-findings/) develops the three threads worth following: the 26-point campus spread and what it implies for intervention targeting; the post-NGN cohort decline that tracks the national rate at a similar pace while sitting roughly three points below national throughout; and the retake conversion rate that runs more than twenty percentage points above the NCSBN[^ncsbn] national benchmark for repeat NCLEX-RN takers, reframing the retake problem as one of engagement rather than conversion. The predictive-modeling discussion at the end of phase 04 names the data gaps that would lift any model's discriminative power and switches briefly to R for the logistic regression and AUC discussion where SQL hits its analytical ceiling.

The case study philosophy lives at the [biblioteca](/biblioteca/). The reproducibility-is-the-floor commitment holds: anyone can re-run any query in this case study, change the parameters, and ask their own questions against the same database the prose cites.

[^next-generation-nclex-ngn]: [Next Generation NCLEX (NGN)](https://www.ncsbn.org/exams/next-generation-nclex.page), NCSBN.
[^ncsbn]: [NCSBN](https://www.ncsbn.org/).
