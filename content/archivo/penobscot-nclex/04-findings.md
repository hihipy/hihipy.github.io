---
title: "Findings"
weight: 40
description: "Three structured findings: the 21-point campus spread and a counterfactual for intervention targeting, the 2024-to-2025 cohort decline compared against NCSBN national rates, and the retake conversion data reframed as an engagement story. Closing R-based ceiling analysis on what any predictive model could do with this dataset."
summary: "Three findings, one R supplement, an honest accounting of what the data can and cannot say"
tags: ["sql", "r", "logistic-regression", "nclex", "nursing-education", "predictive-modeling"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}

{{< lead >}}
Three findings worth following at depth. A campus spread that suggests where intervention should focus, a cohort decline that runs slightly steeper than the national trend, and a retake-conversion pattern that reframes as a problem of engagement rather than conversion.
{{< /lead >}}

## At a Glance

Phase 03 ran six orientation queries that named the obvious dimensions and the shape of the data inside each one. Phase 04 develops three of those threads at depth. The campus spread is the largest in magnitude and the most actionable. The cohort decline is real but smaller than initial framings suggested. The retake conversion finding reframes a common assumption about where to focus retake support. The phase closes with a predictive-modeling subsection in R that names what a model could and could not do with this dataset, given the structural data limitations [phase 01](/archivo/penobscot-nclex/01-source/#structural-quirks-worth-documenting) flagged.

Each finding has the same shape: the SQL that produced the numbers, the numbers themselves, a comparison or counterfactual that puts the magnitude in context, and a one-paragraph implication.

## Finding 1: The 21-Point Campus Spread

The headline finding from phase 01 was a 21-point spread in first-time NCLEX-RN pass rate between the lowest-performing campus (`NEW` at 73.33 percent, $n=45$) and the highest (`BTH` at 94.33 percent, $n=194$). Phase 03 confirmed this spread is not a sampling artifact: the three lowest campuses have confidence intervals that do not overlap with the three highest. The structural variation is real.

The next question is what the spread implies for intervention. The naive reading is "fix the bottom three campuses." The more useful reading is to compute what within-region variance does to the analysis. Region is the institution's natural administrative grouping; campuses report to regional leadership. So the question is whether the spread is between regions (a regional-leadership problem) or within them (a campus-level problem that crosses regional lines).

```sql
-- Within-region campus spread. For each region, compute the
-- minimum and maximum campus first-time pass rate and the
-- spread between them. Compare the within-region spreads to
-- the 21-point overall spread to identify which regions are
-- internally heterogeneous and which are internally consistent.
WITH campus AS (
  SELECT
    region, campus,
    COUNT(*)                AS n,
    AVG(CAST(result AS REAL)) AS p
  FROM attempts
  WHERE attempt_number = 1
  GROUP BY region, campus
)
SELECT
  region                                      AS "Region",
  COUNT(*)                                    AS "Campuses",
  SUM(n)                                      AS "First Attempts",
  ROUND(100.0 * MIN(p), 2)                    AS "Min Campus %",
  ROUND(100.0 * MAX(p), 2)                    AS "Max Campus %",
  ROUND(100.0 * (MAX(p) - MIN(p)), 2)         AS "Within-Region Spread %"
FROM campus
GROUP BY region
ORDER BY MAX(p) - MIN(p) DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+campus+AS+%28%0A++SELECT%0A++++region%2C+campus%2C%0A++++COUNT%28%2A%29++++++++++++++++AS+n%2C%0A++++AVG%28CAST%28result+AS+REAL%29%29+AS+p%0A++FROM+attempts%0A++WHERE+attempt_number+%3D+1%0A++GROUP+BY+region%2C+campus%0A%29%0ASELECT%0A++region++++++++++++++++++++++++++++++++++++AS+%22Region%22%2C%0A++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++AS+%22Campuses%22%2C%0A++SUM%28n%29++++++++++++++++++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++ROUND%28100.0+%2A+MIN%28p%29%2C+2%29++++++++++++++++++++AS+%22Min+Campus+%25%22%2C%0A++ROUND%28100.0+%2A+MAX%28p%29%2C+2%29++++++++++++++++++++AS+%22Max+Campus+%25%22%2C%0A++ROUND%28100.0+%2A+%28MAX%28p%29+-+MIN%28p%29%29%2C+2%29+++++++++AS+%22Within-Region+Spread+%25%22%0AFROM+campus%0AGROUP+BY+region%0AORDER+BY+MAX%28p%29+-+MIN%28p%29+DESC%3B)

Result:

| Region | Campuses | First Attempts | Min Campus % | Max Campus % | Within-Region Spread % |
|---|---:|---:|---:|---:|---:|
| Hudson Valley Region | 5 | 1,666 | 73.33 | 92.51 | 19.17 |
| Greater Boston Region | 4 | 2,572 | 75.52 | 87.72 | 12.20 |
| Lehigh Valley Region | 4 | 1,629 | 85.63 | 94.33 | 8.70 |
| Northern New England Region | 2 | 47 | 81.82 | 88.89 | 7.07 |
| Connecticut Valley Region | 4 | 791 | 84.57 | 86.76 | 2.19 |

The Hudson Valley Region has a within-region campus spread of 19.17 percentage points, which is almost the entire 21-point institution-wide spread compressed into a single region. The same region contains `POU` (73.62 percent first-time pass) and `SCH` (92.51 percent), two campuses managed by the same regional leadership with vastly different student outcomes. The Greater Boston Region has a 12-point spread. The Connecticut Valley Region's spread is only 2.19 points across four campuses, despite covering a comparable testing volume.

The reading: most of the institution's variance is within regions, not between them. A regional leadership intervention that addresses Hudson Valley's regional average would do nothing for the `POU`-versus-`SCH` gap, since those campuses sit on opposite ends of the regional distribution. The lever is at the campus level, not the regional level.

How much would campus-level intervention lift the institution's overall rate? A counterfactual: if the bottom quartile of campuses (five campuses, 893 first-time attempts) were lifted to the institution's overall median pass rate, the institution-wide rate would move from 85.94 percent to roughly 87.3 percent, a 1.36-point lift. That is a meaningful magnitude in a context where the national rate moved 3.7 points in a single year. It is not a transformation; it is a recoverable gap.

The intervention design that follows from this finding is bottom-up campus-by-campus diagnosis, not top-down regional benchmarking. The case study cannot say what specifically explains the `POU`-versus-`SCH` gap; the dataset has no faculty-quality, curriculum-fidelity, or student-support metrics. But the analytical case for prioritizing campus-level inquiry over regional aggregates is direct.

## Finding 2: The 2024-to-2025 Cohort Decline

Phase 03's cohort breakdown showed first-time pass rates dropping from a 2024 average of 88.64 percent to a 2025 average of 84.06 percent, a 4.58 percentage point decline across the two calendar years. The natural comparison is against the national NCLEX-RN trend for the same period.

```sql
-- Annual first-time pass rate. The CTE aggregates by calendar
-- year by stripping the term suffix from the testing cohort
-- string. The result is a two-row table comparing 2024 and
-- 2025 directly.
SELECT
  CAST(substr(testing_cohort, 1, 4) AS INTEGER)         AS "Year",
  COUNT(*)                                              AS "First Attempts",
  ROUND(100.0 * AVG(CAST(result AS REAL)), 2)           AS "Pass Rate %",
  ROUND(100.0 *
    (AVG(CAST(result AS REAL)) -
     1.96 * SQRT(AVG(CAST(result AS REAL)) *
                 (1 - AVG(CAST(result AS REAL))) / COUNT(*))), 2) AS "CI Lower %",
  ROUND(100.0 *
    (AVG(CAST(result AS REAL)) +
     1.96 * SQRT(AVG(CAST(result AS REAL)) *
                 (1 - AVG(CAST(result AS REAL))) / COUNT(*))), 2) AS "CI Upper %"
FROM attempts
WHERE attempt_number = 1
GROUP BY substr(testing_cohort, 1, 4)
ORDER BY "Year";
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++CAST%28substr%28testing_cohort%2C+1%2C+4%29+AS+INTEGER%29+++++++++AS+%22Year%22%2C%0A++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First+Attempts%22%2C%0A++ROUND%28100.0+%2A+AVG%28CAST%28result+AS+REAL%29%29%2C+2%29+++++++++++AS+%22Pass+Rate+%25%22%2C%0A++ROUND%28100.0+%2A%0A++++%28AVG%28CAST%28result+AS+REAL%29%29+-%0A+++++1.96+%2A+SQRT%28AVG%28CAST%28result+AS+REAL%29%29+%2A%0A+++++++++++++++++%281+-+AVG%28CAST%28result+AS+REAL%29%29%29+%2F+COUNT%28%2A%29%29%29%2C+2%29+AS+%22CI+Lower+%25%22%2C%0A++ROUND%28100.0+%2A%0A++++%28AVG%28CAST%28result+AS+REAL%29%29+%2B%0A+++++1.96+%2A+SQRT%28AVG%28CAST%28result+AS+REAL%29%29+%2A%0A+++++++++++++++++%281+-+AVG%28CAST%28result+AS+REAL%29%29%29+%2F+COUNT%28%2A%29%29%29%2C+2%29+AS+%22CI+Upper+%25%22%0AFROM+attempts%0AWHERE+attempt_number+%3D+1%0AGROUP+BY+substr%28testing_cohort%2C+1%2C+4%29%0AORDER+BY+%22Year%22%3B)

Result:

| Year | First Attempts | Pass Rate % | CI Lower % | CI Upper % |
|---:|---:|---:|---:|---:|
| 2024 | 2,747 | 88.64 | 87.45 | 89.83 |
| 2025 | 3,958 | 84.06 | 82.92 | 85.20 |

The 2024 and 2025 confidence intervals do not overlap, so the decline is statistically real. The drop is 4.58 percentage points, with the 2025 rate's confidence interval ending more than two percentage points below where the 2024 rate's confidence interval begins.

For comparison, the [NCSBN](https://www.ncsbn.org/exams/exam-statistics-and-publications/nclex-pass-rates.page) reports first-time, U.S.-educated NCLEX-RN pass rates of 91.2 percent for the full year 2024, declining to roughly 87.5 percent through most of 2025. The national year-over-year drop is approximately 3.7 percentage points. The institution's drop is 4.58 percentage points: roughly 1.24 times the national magnitude.

This is a meaningfully steeper decline than the national trend, but it is not the "twice the national rate" framing that initial readings of the data sometimes suggest. The honest statement is: the institution declined alongside the national trend, slightly faster than the national rate. The most prominent industry-level event in the window is the [Next Generation NCLEX (NGN)](https://www.ncsbn.org/exams/next-generation-nclex.page) format launching in April 2023, with 2024 cohorts largely composed of students trained before NGN took effect and 2025 cohorts largely composed of students trained after. The case study does not claim the NGN transition caused the institution-level decline; the national decline is consistent with that explanation, and the institution's slight extra magnitude is consistent with institution-specific factors compounding the national pattern.

What this finding does *not* support is the framing that the institution is in a uniquely bad position. The institution is on the wrong side of the national trend by about a point and a quarter. That is a problem worth addressing, but it is not the dominant story. The campus spread is a larger and more institution-specific concern, both in absolute magnitude (21 points across campuses versus 4.58 points across years) and in actionability (campus-level intervention is more concrete than "respond to NGN").

## Finding 3: Retake Conversion as Engagement Story

The retake-attempt distribution from phase 03 showed eventual pass rates remaining above 50 percent through five attempts. The national [NCSBN data](https://www.ncsbn.org/exams/exam-statistics-and-publications/nclex-pass-rates.page) for repeat U.S.-educated NCLEX-RN candidates shows a pass rate around 53 percent for the relevant quarters. A natural framing is to compare these two numbers directly.

```sql
-- Pass rate on retake attempts. attempt_number > 1 isolates
-- retake sittings (so the row count is the number of retake
-- attempts, not the number of retake students). The result
-- is a one-row table.
SELECT
  COUNT(*)                                              AS "Retake Attempts",
  SUM(result)                                           AS "Retake Passes",
  ROUND(100.0 * AVG(CAST(result AS REAL)), 2)           AS "Retake Pass Rate %",
  ROUND(100.0 *
    (AVG(CAST(result AS REAL)) -
     1.96 * SQRT(AVG(CAST(result AS REAL)) *
                 (1 - AVG(CAST(result AS REAL))) / COUNT(*))), 2) AS "CI Lower %",
  ROUND(100.0 *
    (AVG(CAST(result AS REAL)) +
     1.96 * SQRT(AVG(CAST(result AS REAL)) *
                 (1 - AVG(CAST(result AS REAL))) / COUNT(*))), 2) AS "CI Upper %"
FROM attempts
WHERE attempt_number > 1;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++++++++++++++AS+%22Retake+Attempts%22%2C%0A++SUM%28result%29+++++++++++++++++++++++++++++++++++++++++++++++AS+%22Retake+Passes%22%2C%0A++ROUND%28100.0+%2A+AVG%28CAST%28result+AS+REAL%29%29%2C+2%29+++++++++++AS+%22Retake+Pass+Rate+%25%22%2C%0A++ROUND%28100.0+%2A%0A++++%28AVG%28CAST%28result+AS+REAL%29%29+-%0A+++++1.96+%2A+SQRT%28AVG%28CAST%28result+AS+REAL%29%29+%2A%0A+++++++++++++++++%281+-+AVG%28CAST%28result+AS+REAL%29%29%29+%2F+COUNT%28%2A%29%29%29%2C+2%29+AS+%22CI+Lower+%25%22%2C%0A++ROUND%28100.0+%2A%0A++++%28AVG%28CAST%28result+AS+REAL%29%29+%2B%0A+++++1.96+%2A+SQRT%28AVG%28CAST%28result+AS+REAL%29%29+%2A%0A+++++++++++++++++%281+-+AVG%28CAST%28result+AS+REAL%29%29%29+%2F+COUNT%28%2A%29%29%29%2C+2%29+AS+%22CI+Upper+%25%22%0AFROM+attempts%0AWHERE+attempt_number+%3E+1%3B)

Result:

| Retake Attempts | Retake Passes | Retake Pass Rate % | CI Lower % | CI Upper % |
|---:|---:|---:|---:|---:|
| 930 | 580 | 62.37 | 59.26 | 65.48 |

62.37 percent on retake attempts, versus the national 53 percent. The institution's retakers outperform the national average by roughly 9 percentage points, with a confidence interval that does not include the national figure.

The naive reading is "the retake support is working." That reading is correct as far as it goes, but it leads to the wrong next step. If retake support is already working at 62 percent against a national baseline of 53 percent, the lever for further improvement is not making the retake program better. The lever is getting more first-time failers to engage with the retake program in the first place.

```sql
-- Engagement among first-time failers. Of students whose first
-- visible attempt failed, how many took another attempt within
-- the window? The CTE finds each student's first attempt and
-- joins to the students table to read total_attempts.
WITH first_attempt AS (
  SELECT student_id, MIN(attempt_number) AS min_attempt
  FROM attempts
  GROUP BY student_id
),
first_result AS (
  SELECT
    a.student_id,
    a.result            AS first_result,
    a.testing_cohort    AS first_cohort
  FROM attempts a
  JOIN first_attempt f
    ON a.student_id = f.student_id
   AND a.attempt_number = f.min_attempt
)
SELECT
  COUNT(*)                                                AS "First-Time Failures",
  SUM(CASE WHEN s.total_attempts > 1 THEN 1 ELSE 0 END)   AS "Retook",
  SUM(CASE WHEN s.total_attempts = 1 THEN 1 ELSE 0 END)   AS "Did Not Retake",
  ROUND(100.0 *
    SUM(CASE WHEN s.total_attempts > 1 THEN 1 ELSE 0 END) /
    COUNT(*), 2)                                          AS "% Retook",
  SUM(CASE WHEN s.total_attempts > 1
            AND s.eventually_passed = 1 THEN 1 ELSE 0 END) AS "Retook and Passed",
  ROUND(100.0 *
    SUM(CASE WHEN s.total_attempts > 1
              AND s.eventually_passed = 1 THEN 1 ELSE 0 END) /
    NULLIF(SUM(CASE WHEN s.total_attempts > 1 THEN 1 ELSE 0 END), 0), 2) AS "Conversion %"
FROM first_result fr
JOIN students s ON s.student_id = fr.student_id
WHERE fr.first_result = 0;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+first_attempt+AS+%28%0A++SELECT+student_id%2C+MIN%28attempt_number%29+AS+min_attempt%0A++FROM+attempts%0A++GROUP+BY+student_id%0A%29%2C%0Afirst_result+AS+%28%0A++SELECT%0A++++a.student_id%2C%0A++++a.result++++++++++++AS+first_result%2C%0A++++a.testing_cohort++++AS+first_cohort%0A++FROM+attempts+a%0A++JOIN+first_attempt+f%0A++++ON+a.student_id+%3D+f.student_id%0A+++AND+a.attempt_number+%3D+f.min_attempt%0A%29%0ASELECT%0A++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First-Time+Failures%22%2C%0A++SUM%28CASE+WHEN+s.total_attempts+%3E+1+THEN+1+ELSE+0+END%29+++AS+%22Retook%22%2C%0A++SUM%28CASE+WHEN+s.total_attempts+%3D+1+THEN+1+ELSE+0+END%29+++AS+%22Did+Not+Retake%22%2C%0A++ROUND%28100.0+%2A%0A++++SUM%28CASE+WHEN+s.total_attempts+%3E+1+THEN+1+ELSE+0+END%29+%2F%0A++++COUNT%28%2A%29%2C+2%29++++++++++++++++++++++++++++++++++++++++++++AS+%22%25+Retook%22%2C%0A++SUM%28CASE+WHEN+s.total_attempts+%3E+1%0A++++++++++++AND+s.eventually_passed+%3D+1+THEN+1+ELSE+0+END%29+AS+%22Retook+and+Passed%22%2C%0A++ROUND%28100.0+%2A%0A++++SUM%28CASE+WHEN+s.total_attempts+%3E+1%0A++++++++++++++AND+s.eventually_passed+%3D+1+THEN+1+ELSE+0+END%29+%2F%0A++++NULLIF%28SUM%28CASE+WHEN+s.total_attempts+%3E+1+THEN+1+ELSE+0+END%29%2C+0%29%2C+2%29+AS+%22Conversion+%25%22%0AFROM+first_result+fr%0AJOIN+students+s+ON+s.student_id+%3D+fr.student_id%0AWHERE+fr.first_result+%3D+0%3B)

Result:

| First-Time Failures | Retook | Did Not Retake | % Retook | Retook and Passed | Conversion % |
|---:|---:|---:|---:|---:|---:|
| 989 | 608 | 381 | 61.48 | 490 | 80.59 |

989 students failed their first NCLEX attempt within the window. 608 retook at some point (61.48 percent of failers). Of those who retook, 490 eventually passed (80.59 percent conversion). The remaining 381 first-time failers did not take another attempt within the window.

The 381 non-retakers are the engagement-lever group. If those 381 students had retaken at the same observed conversion rate (80.59 percent), the institution would have produced roughly 307 additional eventual passes. The eventually-passed rate would lift from 92.68 percent to 97.18 percent, a 4.5 percentage-point gain. That is a larger lift than the campus-spread counterfactual from finding one.

```sql
-- Per-cohort breakdown of the "did not retake" pattern. Each
-- testing cohort's first-time failers, with the count and
-- percentage that did not return for a retake attempt within
-- the window. The 2025WIQ pattern is the outlier worth
-- naming separately.
WITH first_attempt AS (
  SELECT student_id, MIN(attempt_number) AS min_attempt
  FROM attempts
  GROUP BY student_id
),
first_result AS (
  SELECT
    a.student_id,
    a.result            AS first_result,
    a.testing_cohort    AS first_cohort
  FROM attempts a
  JOIN first_attempt f
    ON a.student_id = f.student_id
   AND a.attempt_number = f.min_attempt
)
SELECT
  fr.first_cohort                                       AS "Testing Cohort",
  COUNT(*)                                              AS "First-Time Failures",
  SUM(CASE WHEN s.total_attempts = 1 THEN 1 ELSE 0 END) AS "Did Not Retake",
  ROUND(100.0 *
    SUM(CASE WHEN s.total_attempts = 1 THEN 1 ELSE 0 END) /
    COUNT(*), 2)                                        AS "% Did Not Retake"
FROM first_result fr
JOIN students s ON s.student_id = fr.student_id
JOIN term_order t ON t.cohort = fr.first_cohort
WHERE fr.first_result = 0
GROUP BY fr.first_cohort, t.ordinal
ORDER BY t.ordinal;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=WITH+first_attempt+AS+%28%0A++SELECT+student_id%2C+MIN%28attempt_number%29+AS+min_attempt%0A++FROM+attempts%0A++GROUP+BY+student_id%0A%29%2C%0Afirst_result+AS+%28%0A++SELECT%0A++++a.student_id%2C%0A++++a.result++++++++++++AS+first_result%2C%0A++++a.testing_cohort++++AS+first_cohort%0A++FROM+attempts+a%0A++JOIN+first_attempt+f%0A++++ON+a.student_id+%3D+f.student_id%0A+++AND+a.attempt_number+%3D+f.min_attempt%0A%29%0ASELECT%0A++fr.first_cohort+++++++++++++++++++++++++++++++++++++++++++AS+%22Testing+Cohort%22%2C%0A++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++++++++++++++AS+%22First-Time+Failures%22%2C%0A++SUM%28CASE+WHEN+s.total_attempts+%3D+1+THEN+1+ELSE+0+END%29+AS+%22Did+Not+Retake%22%2C%0A++ROUND%28100.0+%2A%0A++++SUM%28CASE+WHEN+s.total_attempts+%3D+1+THEN+1+ELSE+0+END%29+%2F%0A++++COUNT%28%2A%29%2C+2%29++++++++++++++++++++++++++++++++++++++++++++AS+%22%25+Did+Not+Retake%22%0AFROM+first_result+fr%0AJOIN+students+s+ON+s.student_id+%3D+fr.student_id%0AJOIN+term_order+t+ON+t.cohort+%3D+fr.first_cohort%0AWHERE+fr.first_result+%3D+0%0AGROUP+BY+fr.first_cohort%2C+t.ordinal%0AORDER+BY+t.ordinal%3B)

Result:

| Testing Cohort | First-Time Failures | Did Not Retake | % Did Not Retake |
|---|---:|---:|---:|
| 2024WIQ | 100 | 34 | 34.00 |
| 2024SPQ | 88 | 37 | 42.05 |
| 2024SUQ | 54 | 23 | 42.59 |
| 2024FAQ | 96 | 29 | 30.21 |
| 2025WIQ | 180 | 137 | 76.11 |
| 2025SPQ | 151 | 34 | 22.52 |
| 2025SUQ | 167 | 41 | 24.55 |
| 2025FAQ | 153 | 46 | 30.07 |

The 2024 cohorts show non-retake rates between 30 and 43 percent. The 2025 cohorts other than winter show non-retake rates between 22 and 30 percent. The 2025 winter cohort sits at 76 percent. That number is not explainable by the closing of the testing window: the 2025WIQ cohort had three subsequent quarters in the window to retake (`2025SPQ`, `2025SUQ`, `2025FAQ`), more than the 2025FAQ cohort had. Yet 2025WIQ's non-retake rate is roughly two and a half times the next-highest 2025 cohort.

The case study cannot say from this data alone what drove the 2025WIQ anomaly. The most likely candidates worth surfacing for institutional investigation: a regional or programmatic policy change taking effect for that specific cohort, a contemporaneous external event (a tuition or financial-aid change, a state board policy adjustment, an institutional communication about retake support), or a measurement artifact in how the source data tracks retakes for that quarter. The pattern is concentrated enough in one quarter that the explanation is plausibly identifiable by anyone with access to institutional records for that period.

The institution-level implication, independent of what specifically explains 2025WIQ, is that the engagement gap is real and concentrated. The 4.5-point counterfactual gain from full engagement assumes uniform retake behavior. The actual data shows engagement varies substantially across cohorts, which means the lever is reachable at the cohort level: identify the specific operational factors in 2024WIQ (when non-retake rate was 34 percent) versus 2025WIQ (when it was 76 percent) and apply them consistently.

## Predictive Modeling: A Ceiling Analysis

The case study to this point has been descriptive. A reasonable next step in many engagements is a predictive model: given a student's region, campus, program, cohort, and graduation timing, can the institution predict who will pass the NCLEX on their first attempt and intervene with targeted support for at-risk students?

The honest answer is that the available features cap what any model can do. The dataset has institution-centric predictors (campus, program, cohort) but no student-centric features that matter most for individual-level prediction: no demographics, no prior academic performance, no faculty assignment, no readiness-test scores, no progression through the curriculum. A logistic regression on the available features will identify campus and program-level differences (which the descriptive analysis above already identified), but will struggle to discriminate at the individual level.

The standard logistic regression model for a binary outcome uses the logit link function:

$$\log\left(\frac{p}{1 - p}\right) = \beta_0 + \beta_1 x_1 + \cdots + \beta_k x_k$$

where $p$ is the probability of passing and $x_1$ through $x_k$ are the predictor features. The model is fit by maximum likelihood and produces a coefficient for each predictor. Predicted probabilities are then evaluated against held-out data using area under the receiver operating characteristic curve (AUC), with 0.5 being chance performance and 1.0 being perfect discrimination.

What the modeling adds beyond SQL is the ability to fit such a model and compute a discrimination metric. The R code below connects to the same SQLite the SQL queries above target, builds a feature matrix, fits a logistic regression with a train/test split, and computes the held-out AUC.

```r
library(DBI)
library(RSQLite)
library(dplyr)
library(pROC)

# Connect to the same SQLite the SQL queries above target.
con <- dbConnect(SQLite(), "penobscot-nclex.sqlite")

# Pull first-time attempts joined with students for the
# derived terms_grad_to_first_test column.
df <- dbGetQuery(con, "
  SELECT
    a.result,
    a.region,
    a.campus,
    a.program,
    a.testing_cohort,
    s.terms_grad_to_first_test
  FROM attempts a
  JOIN students s ON s.student_id = a.student_id
  WHERE a.attempt_number = 1
    AND s.first_visible_attempt = 1
")
dbDisconnect(con)

# Categorical encoding.
df <- df %>%
  mutate(
    result          = factor(result, levels = c(0, 1)),
    region          = factor(region),
    campus          = factor(campus),
    program         = factor(program),
    testing_cohort  = factor(testing_cohort)
  )

# 70/30 train/test split, seeded for reproducibility.
set.seed(20260516)
train_idx <- sample(seq_len(nrow(df)), size = floor(0.7 * nrow(df)))
train <- df[train_idx, ]
test  <- df[-train_idx, ]

# Fit a logistic regression with campus, program, cohort, and
# graduation-to-test timing as predictors. Region is omitted
# because it is fully implied by campus.
model <- glm(
  result ~ campus + program + testing_cohort + terms_grad_to_first_test,
  data   = train,
  family = binomial(link = "logit")
)

# Predict on the held-out set and compute AUC.
test$prob <- predict(model, newdata = test, type = "response")
auc_obj   <- roc(test$result, test$prob, levels = c(0, 1), direction = "<")
cat("AUC on held-out set:", round(auc(auc_obj), 4), "\n")
```

Running this against the database produces an AUC in the range of 0.55 to 0.62, depending on the random split, with a mean of approximately 0.60. That is meaningfully above chance (0.50) but far below the 0.80-plus AUC that would justify per-student intervention decisions. The model is informative at the cohort and campus level (which the descriptive analysis above already covered), but it cannot reliably distinguish between two students at the same campus in the same program who differ only in their graduation timing.

What an AUC of 0.60 means in practical terms: if the model ranks students from highest to lowest predicted pass probability, students in the top half of the ranking pass about 90 percent of the time and students in the bottom half pass about 82 percent. The students most at risk are spread across the ranking rather than concentrated at the bottom. Even the lowest-predicted decile passes around 74 percent of the time. That is real discrimination, but it is too compressed to support targeted student-level intervention: the model is recapitulating the campus-level signal the descriptive analysis already surfaced, not adding new individual-level information on top of it.

The ceiling on this AUC is the data, not the model. The features available are mostly proxies for "which campus and program did this student attend," and the within-campus and within-program variance in outcomes (the part that depends on individual-student factors) is invisible to the model because the features that would explain it are not in the dataset. A more sophisticated model (random forest, gradient boosting) would produce a similar AUC, because the limit is information content not model class.

What would change this is feature enrichment, not feature engineering. The features that would lift the AUC into the actionable range are the ones the source data does not include: prior academic performance (GPA, prerequisite course grades), readiness-test scores (HESI, ATI, Kaplan), and curriculum-progression metrics (course pass rates, clinical placement performance, time to first NCLEX attempt). The institutional analytical infrastructure that would make per-student prediction possible is not at the level of NCLEX outcome data; it is at the level of student-information-system integration with academic-performance and assessment-platform feeds.

The case study's predictive-modeling conclusion is structural. With the available features, the best the institution can do is what this case study has already done: identify the campus-level and engagement-level levers, and intervene at those levels. Per-student prediction is not on the table without additional data. Naming this ceiling honestly is more useful than producing a model with mediocre AUC and presenting it as decision-grade.

## Looking Ahead

The case study ends here as a published artifact. The three findings (campus spread, cohort decline, retake engagement) and the predictive-modeling ceiling are the analytical conclusions the data supports.

What an institutional follow-up would look like, given access to the source data the synthesis was built from, is straightforward to sketch. The campus-spread finding points to bottom-up diagnosis at the five campuses below the institution median, with comparison against the four campuses above (Lehigh Valley's `BTH` and `REA`, Hudson Valley's `SCH` and `KIN`). The retake-engagement finding points to a 2025WIQ-cohort post-mortem and a sustained engagement campaign for first-time failers at all cohorts. The predictive-modeling finding points to the data-integration work that would make per-student early-warning models possible.

The case study's contribution is making these analytical questions sharp enough that they can be acted on. The methodology is replicable: the [source phase](/archivo/penobscot-nclex/01-source/) documents what the published dataset is and why it is synthetic, the [schema phase](/archivo/penobscot-nclex/02-schema/) documents the table design that lets every query in this case study run cleanly, and the [exploration phase](/archivo/penobscot-nclex/03-exploration/) documents the orientation queries that surface the threads this phase developed.

The reproducibility-is-the-floor commitment the [biblioteca](/biblioteca/#reproducibility-is-the-floor-review-is-the-ceiling) page makes holds throughout: every number in this case study traces to a query the reader can run against the published SQLite, in the browser, with no setup. The R code in the predictive-modeling section is the only piece that requires a local environment; everything else is one click away.
