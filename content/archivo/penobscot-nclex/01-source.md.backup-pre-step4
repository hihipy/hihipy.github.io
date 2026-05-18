---
title: "Source"
weight: 10
description: "Where the data came from, why it is synthetic, what the nine source columns hold, and the 21-point campus spread that surfaces in a single GROUP BY query."
summary: "Phase 1: Synthetic source, de-identification, and the first thread"
tags: ["nclex", "nursing-education", "csv", "public-data", "data-quality"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
The data is synthetic. It is derived from a real engagement with every identifier randomized and every outcome value perturbed so no row matches a real student or a real institutional figure.
{{< /lead >}}

## At a Glance

This case study takes a 7,635-attempt slice of synthetic NCLEX-RN data covering two years of testing (winter 2024 through fall 2025) at a multi-campus nursing college. The slice represents 6,819 unique students across 19 campuses in five regions. Source columns: student identifier, region, campus, program code, starting cohort, graduating cohort, testing cohort, attempt number, and a binary pass/fail result. Nothing else: no demographics, no academic readiness scores, no test-section breakdowns. The full nine-column schema is what was available in the source engagement, and what is published here is a randomized version of it.

```sql
-- Three-table row count summary used in the At a Glance section.
-- UNION ALL stacks the count of each table into a single result set.
-- The 6,819-student count, 7,635 attempts, and 52 cohort terms together
-- describe the database shape: fewer students than attempts because some
-- students retake; fewer cohort terms than the calendar suggests because
-- the source data does not include every quarter in the 21-year window.
SELECT
    'attempts'   AS "Table",
    COUNT(*)     AS "Rows"
FROM attempts
UNION ALL
SELECT
    'students',
    COUNT(*)
FROM students
UNION ALL
SELECT
    'term_order',
    COUNT(*)
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

## Why The Data Is Synthetic

NCLEX-RN performance data at the institution level is sensitive. State boards of nursing publish school-level pass rates annually, but the row-level data behind those rates is the kind of detail that institutions hold internally and do not release. The dataset published here is a randomized version of a real one: regions, campuses, program codes, and student identifiers have been replaced, and a small amount of noise has been applied to outcomes. The analytical patterns the data shows are preserved. No row, no aggregate, and no headline number matches any specific institution's published figures.

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

The four-letter term codes resolve to a four-quarter academic year: `WIQ` (winter), `SPQ` (spring), `SUQ` (summer), `FAQ` (fall). The within-year ordering is `WIQ < SPQ < SUQ < FAQ`, validated empirically by chasing single-student attempt sequences in the source data. Phase 02 introduces the `term_order` lookup table that makes this ordering queryable with a single `JOIN` instead of forcing every term-math query to embed a `CASE WHEN` clause.

The program codes are dot-separated path strings encoding degree level, pathway, and credential type. `ADN.2YR.AS` is an Associate Degree in Nursing, traditional two-year track, Associate of Science credential. `ADN.BRDG.AAS` is the same degree level via a bridge pathway (LPN-to-RN), Associate of Applied Science credential. `BSN.PRE.BSN` is a prelicensure Bachelor of Science in Nursing. The pathway distinctions matter for phase 03's program-level analysis because bridge students have meaningfully different first-time pass rates than traditional-track students.

## Structural Quirks Worth Documenting

Six patterns in the source data require deliberate handling and are worth surfacing before the schema phase decides how to model around them.

**Left-censored students.** Of 6,819 distinct students in the data, 114 have no Attempt 1 row visible. Their first appearance in the published data is Attempt 2, 3, or later. The explanation is that these students took their first attempt before the window opens in winter 2024, failed, and only their retakes appear in the window. The number is small (1.7 percent of the cohort) but real, and phase 02 surfaces it as a `first_visible_attempt > 1` flag on the `students` table so the case study can either include or exclude this group depending on the question being asked.

**Multimodal time-from-graduation-to-test distribution.** A natural derived metric is the number of terms between a student's graduating cohort and their first testing cohort. Computing it across all students produces a distribution with three clear modes: a large group at minus three terms (students who tested before their recorded graduating cohort), a larger group at plus one term, and a third group at plus five terms. The negative-mode group is the surprise. The most likely explanation is that the `Graduating Cohort` field is set at enrollment time as an expected graduation date and is not always updated when actual graduation slips later, so students appear to test before they "graduated." Phase 03 develops this further; phase 01 only flags it.

**Long retake tails.** Attempt numbers run from 1 to 19. The distribution is heavily concentrated at attempt 1 (6,705 of 7,635 rows) and falls quickly through 2 (675 rows), 3 (162), 4 (56). Three students appear at attempt 9, one each at 17, 18, and 19. The long tail is preserved in the randomization because it carries real analytical signal: students who retake many times tell a different story than students who pass on attempt one or two.

**Binary outcome, no score detail.** The `Result` column is binary. The actual NCLEX-RN scoring system is more nuanced (the computerized adaptive test reports passing as a confidence boundary in logit units, with detailed section feedback for failures), but the source data exposes only the binary outcome. The case study's predictive modeling discussion in phase 04 names this as the primary data-richness ceiling on what any model could achieve.

**No demographic data.** The dataset has no age, sex, race, ethnicity, prior degree, or socioeconomic indicator. The schema is institution-centric: it answers questions about campus, program, and cohort, but cannot answer questions about which students within a campus or program are at higher or lower risk. This is a real limitation, and the predictive modeling discussion treats it as the most important one.

**Term gaps in the cohort sequence.** The `term_order` table built in phase 02 has 52 rows, covering cohort terms from 2005 through 2026. The source data does not include every quarter in that 21-year window. A student with a `Starting/Readmitted Cohort` of `2008WIQ` exists in the data, but the next earliest cohort observed is `2010WIQ`, two years later. The gaps are presumably real reporting gaps in the source institution's data and not artifacts of the synthesis. They matter for term-ordinal math because computing an ordinal as "number of quarters since some base" requires the base to be defined and the gaps to be acknowledged.

## The Scope Decision

The window is two years of testing (eight quarters from `2024FAQ` through `2025WIQ`) for students whose starting cohorts span back to 2005. The two-year testing slice is not arbitrary: it covers the period immediately after the [Next Generation NCLEX (NGN)](https://www.ncsbn.org/exams/next-generation-nclex.page) format launched in April 2023, which is the most consequential structural change to the exam in two decades. Pre-NGN cohorts are not in the window; the NGN-era cohorts are. The case study takes the post-launch period as given and asks how the institution performed in it.

The institution-level scope (multi-campus, five regions, 19 campuses) lets a campus-spread thread emerge that a single-campus scope could not. Campus is the highest-resolution categorical variable in the data, and as the next section shows, it is also where the most interesting variation lives.

## The 21-Point Campus Spread

The first analytical thread surfaces from a single `GROUP BY campus` query. First-time pass rate by campus, sorted ascending:

```sql
-- First-time pass rate by campus across the full two-year testing window.
-- Filters to attempt_number = 1 because the question is about first-time
-- performance specifically; retakes are a separate question phase 04
-- develops. Pass rate is AVG(result) since result is 0/1. Ordering
-- ascending puts the lowest-performing campuses at the top so the
-- 21-point spread between highest and lowest is the first thing visible.
SELECT
    campus                          AS "Campus",
    COUNT(*)                        AS "First Attempts",
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
| NEW | 45 | 73.33 |
| POU | 235 | 73.62 |
| SPR | 335 | 75.52 |
| LOW | 267 | 81.27 |
| MAN | 11 | 81.82 |
| HAR | 376 | 84.57 |
| BOS | 1,514 | 85.07 |
| NHV | 271 | 85.24 |
| BRI | 76 | 85.53 |
| SCR | 341 | 85.63 |
| ALL | 848 | 85.85 |
| WTB | 68 | 86.76 |
| WOR | 456 | 87.72 |
| POR | 36 | 88.89 |
| ALB | 708 | 89.83 |
| KIN | 291 | 90.03 |
| REA | 246 | 91.46 |
| SCH | 387 | 92.51 |
| BTH | 194 | 94.33 |

A 21-point spread from `NEW` at 73.33 percent to `BTH` at 94.33 percent. For comparison, the spread between the highest and lowest U.S. states in published NCLEX-RN pass rates over this same period was roughly 10 to 15 percentage points. The within-institution spread is larger than the cross-state spread.

That ratio is the thread phase 04 develops most thoroughly. It also frames how the case study reasons about the data. Cohort effects, program-pathway effects, and regional effects all exist in this dataset and all matter, but none of them comes close to the campus-level variation. Whatever explains the gap between `NEW` and `BTH` is the lever the analysis is trying to surface.

The two lowest campuses, `NEW` (45 attempts) and `POU` (235 attempts), are small relative to `BTH` (194) but `POU` is comparable in size to the top performers and still bottom-ranked. The campus spread is not a small-sample artifact.

This is how an analytical thread emerges from data. Not from a research question imposed on the data, but from a `GROUP BY` whose ordered output asks a question the reader did not already have.

## Looking Ahead

[Phase 02 (Schema)](/archivo/penobscot-nclex/02-schema/) documents the three-table normalization that turns the flat CSV into a queryable database: the per-attempt `attempts` table that mirrors the source, the per-student `students` table that derives twelve aggregates including `eventually_passed` and `total_attempts`, and the `term_order` lookup that makes term-quarter math a one-line `JOIN` instead of an embedded `CASE WHEN`.

[Phase 03 (Exploration)](/archivo/penobscot-nclex/03-exploration/) covers the orientation queries: campus first-time pass rates with confidence intervals computed inline in SQL, program-level breakdowns by pathway, cohort-level trends across the two-year window, and the time-from-graduation-to-test distribution that surfaces the multimodal pattern the source phase flagged.

[Phase 04 (Findings)](/archivo/penobscot-nclex/04-findings/) develops the three threads worth following: the campus spread and what it implies for intervention targeting; the post-NGN cohort decline running roughly twice the national rate; and the retake conversion rate that runs about nine percentage points above the [NCSBN](https://www.ncsbn.org/) national benchmark, reframing the retake problem as one of engagement rather than conversion. The predictive-modeling discussion at the end of phase 04 names the data gaps that would lift any model's discriminative power and switches briefly to R for the logistic regression and AUC discussion where SQL hits its analytical ceiling.

The case study philosophy lives at the [biblioteca](/biblioteca/). The reproducibility-is-the-floor commitment holds: anyone can re-run any query in this case study, change the parameters, and ask their own questions against the same database the prose cites.
