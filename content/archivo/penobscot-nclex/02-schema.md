---
title: "Schema"
weight: 20
description: "Three normalized tables: a per-attempt mirror of the source, a per-student derivation with twelve aggregates, and a term-order lookup that makes academic-quarter math a single JOIN. The decisions that shape the schema, with SQL the reader can run to verify each one."
summary: "Three tables, twelve derived columns, one lookup"
tags: ["etl", "python", "schema-design", "sql", "sqlite"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Three tables. One mirrors the source CSV. One derives per-student aggregates the analysis will need. One handles academic-quarter ordering so it doesn't have to be fought in every query.
{{< /lead >}}

## At a Glance

The source phase produced the anonymized CSV (7,635 rows, nine columns, no missingness) and the first analytical thread to follow (a 21-point first-time pass rate spread between campuses). This phase walks through the schema design that turned the CSV into a queryable SQLite database: why three tables rather than one, what derived columns earn a place in the per-student table, what the term-order lookup does that an inlined `CASE WHEN` cannot, and what readers can run to verify the schema design themselves.

The schema is three tables, each with a different grain. The query that documents the design is also the query that verifies it: every row in every table either fits one of these three grains or there is a build-script bug.

```sql
-- Verify the row counts in each of the three tables. The grain of
-- each table is named in the second column for documentation.
-- Phase 02's prose claims about the schema all reduce to these
-- three numbers.
SELECT
    'attempts'                                  AS "Table",
    'one row per (student_id, attempt_number)'  AS "Grain",
    COUNT(*)                                    AS "Rows"
FROM attempts
UNION ALL
SELECT
    'students',
    'one row per student_id',
    COUNT(*)
FROM students
UNION ALL
SELECT
    'term_order',
    'one row per cohort string',
    COUNT(*)
FROM term_order;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++%27attempts%27++++++++++++++++++++++++++++++++++AS+%22Table%22%2C%0A++++%27one+row+per+%28student_id%2C+attempt_number%29%27++AS+%22Grain%22%2C%0A++++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++AS+%22Rows%22%0AFROM+attempts%0AUNION+ALL%0ASELECT%0A++++%27students%27%2C%0A++++%27one+row+per+student_id%27%2C%0A++++COUNT%28%2A%29%0AFROM+students%0AUNION+ALL%0ASELECT%0A++++%27term_order%27%2C%0A++++%27one+row+per+cohort+string%27%2C%0A++++COUNT%28%2A%29%0AFROM+term_order%3B)

Result:

| Table | Grain | Rows |
|---|---|---:|
| `attempts` | One Row per (student_id, attempt_number) | 7,635 |
| `students` | One Row per student_id | 6,819 |
| `term_order` | One Row per Cohort String | 52 |

## The Three-Table Schema

The `attempts` table mirrors the source CSV with snake_case column names. Nine columns, one row per (student, attempt). This is the transactional grain: every NCLEX sitting that appears in the window has exactly one row. Aggregates against this table answer per-attempt questions (pass rate by campus, attempt-count distributions, retake outcomes).

The `students` table is derived at build time from `attempts`. Twelve columns, one row per student. Per-student fields that are constant across a student's attempts (region, campus, program, starting and graduating cohorts) appear once each; the rest are aggregates (`total_attempts`, `eventually_passed`, `first_visible_attempt`, `first_testing_cohort`, `last_testing_cohort`, `terms_grad_to_first_test`). Aggregates against this table answer per-student questions (how many students ever pass, how long they take, who never retakes).

The `term_order` table is a lookup, one row per cohort string. Five columns: the cohort string itself (`2024FAQ`), the year, the term suffix, an index `0..3` for the term position within a year, and a monotonic `ordinal` across the full 21-year window. Joins against this table convert cohort strings to a number that supports arithmetic.

{{< mermaid >}}
erDiagram
    STUDENTS ||--o{ ATTEMPTS : "takes"
    TERM_ORDER ||--o{ ATTEMPTS : "cohort lookup"

    STUDENTS {
        int    student_id PK
        string region
        string campus
        string program
        string starting_cohort
        string graduating_cohort
        int    total_attempts "visible in window"
        int    eventually_passed "0 or 1"
        int    first_visible_attempt "1 unless left-censored"
        string first_testing_cohort
        string last_testing_cohort
        int    terms_grad_to_first_test "via term_order ordinal"
    }

    ATTEMPTS {
        int    student_id PK,FK
        int    attempt_number PK
        string region
        string campus
        string program
        string starting_cohort
        string graduating_cohort
        string testing_cohort
        int    result "0 or 1"
    }

    TERM_ORDER {
        string cohort PK "e.g. 2024FAQ"
        int    year
        string term "SPQ/SUQ/FAQ/WIQ"
        int    term_idx "1-4"
        int    ordinal "monotonic"
    }
{{< /mermaid >}}

The alternative to three tables would be one denormalized table with all per-student aggregates carried on every attempt row. That design is fine for read-only single-query analysis but breaks down in two ways. Per-student aggregates would be redundantly stored on every attempt row, with no enforcement that the aggregates stay consistent across a student's rows. And term ordering would still need a `CASE WHEN` translation in every query that does term math, because the cohort strings themselves do not sort chronologically (`2024FAQ` sorts before `2024SUQ` lexically but comes after it chronologically). Three tables with one grain each is the cleaner shape and is what the schema commits to.

## Why The Students Table Exists

The `students` table earns its place because the most useful per-student questions are expensive to ask from the `attempts` table alone. A query like "what percentage of students with three or more attempts eventually pass" requires a self-aggregation (`HAVING COUNT(*) >= 3`) plus a `MAX(result)` per student. Computing those at query time means recomputing them every time. Computing them once at build time means a faster query and a clearer query.

The twelve columns on `students` were chosen by the same rule the column pruning in [college-scorecard-fl](/archivo/college-scorecard-fl/02-schema/#the-column-pruning) followed: a column earns retention if it answers a question the case study will ask. The aggregates split into three groups:

- **Per-student constants from `attempts`**: `region`, `campus`, `program`, `starting_cohort`, `graduating_cohort`. These do not vary across a student's attempts in this dataset, but they get carried onto `students` anyway because joining `students` to `attempts` to answer "what campus did this student attend" would be a wasted join.
- **Aggregates over `attempts`**: `total_attempts` (count of rows), `eventually_passed` (`MAX(result)`), `first_visible_attempt` (`MIN(attempt_number)`), `first_testing_cohort` (cohort of the minimum-numbered attempt), `last_testing_cohort` (cohort of the maximum-numbered attempt).
- **Cross-table derivations**: `terms_grad_to_first_test`, computed at build time as `term_order.ordinal(first_testing_cohort) - term_order.ordinal(graduating_cohort)`. This is the only column that requires both `attempts` and `term_order` to compute, and pre-computing it means phase 03 can query it directly without doing the JOIN math every time.

A faithful per-student derivation has to satisfy one obvious check: the count of attempt rows summed across all students equals the count of attempt rows in the `attempts` table, or the derivation has dropped or duplicated a row somewhere.

```sql
-- SUM(students.total_attempts) must equal COUNT(*) from attempts,
-- since every attempt row is counted on exactly one student. If
-- the two numbers differ, the per-student derivation has dropped
-- or duplicated a row somewhere.
SELECT
    (SELECT SUM(total_attempts) FROM students)  AS "Sum of total_attempts",
    (SELECT COUNT(*) FROM attempts)             AS "Count of attempts rows",
    (SELECT SUM(total_attempts) FROM students)
        - (SELECT COUNT(*) FROM attempts)       AS "Difference";
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++%28SELECT+SUM%28total_attempts%29+FROM+students%29++AS+%22Sum+of+total_attempts%22%2C%0A++++%28SELECT+COUNT%28%2A%29+FROM+attempts%29+++++++++++++AS+%22Count+of+attempts+rows%22%2C%0A++++%28SELECT+SUM%28total_attempts%29+FROM+students%29%0A++++++++-+%28SELECT+COUNT%28%2A%29+FROM+attempts%29+++++++AS+%22Difference%22%3B)

Result:

| Sum of total_attempts | Count of Attempts Rows | Difference |
|---:|---:|---:|
| 7,635 | 7,635 | 0 |

One detail worth naming before phase 03 builds on it. The `total_attempts` column counts visible attempts in the window, not lifetime attempts. A student whose only row in the data is `Attempt Number = 19` has `total_attempts = 1` because the schema sees one attempt in the testing window even though that student took eighteen earlier attempts before the window opened. The cleanest way to read `total_attempts` is "attempts in this two-year slice," and phase 04's predictive-modeling discussion notes that this windowing is a real ceiling on what any model could infer about lifetime retake propensity.

## The Term-Order Lookup

Academic terms in the source data are encoded as three-letter suffixes attached to a four-digit year: `SPQ` for spring, `SUQ` for summer, `FAQ` for fall, `WIQ` for winter. The within-year ordering is `SPQ < SUQ < FAQ < WIQ`, validated empirically by a 24-permutation search across all possible orderings of the four codes: the winning ordering produces only 4 row-level constraint violations across 7,635 rows; the next-best ordering produces over 1,500. A three-orders-of-magnitude separation makes this an empirical finding rather than an assumption. The lexical ordering of the cohort strings does not match the chronological ordering: `2024FAQ` sorts before `2024SPQ` lexically (because `F` precedes `S`) but comes after it chronologically. Any query that orders by cohort string directly will produce wrong results.

Two ways to handle this. The first is to inline the translation in every query that does term math, with a `CASE WHEN` clause that converts the term suffix to a number `0..3` and combines it with the year to get a monotonic ordinal. The second is to do that translation once at build time and store the ordinal in a lookup table, then JOIN against the lookup wherever term math is needed.

The two approaches are equivalent in result. The lookup version is significantly easier to read. Side by side, asking the same question (distribution of terms between graduation and first test, top ten buckets):

```sql
-- Time from graduation to first test, using the term_order lookup.
-- Two joins, one for the testing cohort, one for the graduating
-- cohort. Subtracting their ordinals gives the term difference.
SELECT
    t.ordinal - g.ordinal AS "Terms (grad to test)",
    COUNT(*)              AS "Students"
FROM students s
JOIN term_order t ON t.cohort = s.first_testing_cohort
JOIN term_order g ON g.cohort = s.graduating_cohort
GROUP BY t.ordinal - g.ordinal
ORDER BY t.ordinal - g.ordinal
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++t.ordinal+-+g.ordinal+AS+%22Terms+%28grad+to+test%29%22%2C%0A++++COUNT%28%2A%29++++++++++++++AS+%22Students%22%0AFROM+students+s%0AJOIN+term_order+t+ON+t.cohort+%3D+s.first_testing_cohort%0AJOIN+term_order+g+ON+g.cohort+%3D+s.graduating_cohort%0AGROUP+BY+t.ordinal+-+g.ordinal%0AORDER+BY+t.ordinal+-+g.ordinal%0ALIMIT+10%3B)

The same question without the lookup, with the term translation inlined twice:

```sql
-- Same question without term_order. The CASE WHEN translation
-- has to appear twice, once for the testing cohort and once for
-- the graduating cohort. Returns the same result.
SELECT
    (CAST(substr(first_testing_cohort,1,4) AS INTEGER) -
     CAST(substr(graduating_cohort,1,4)    AS INTEGER)) * 4
    + (CASE substr(first_testing_cohort,5,3)
        WHEN 'WIQ' THEN 0 WHEN 'SPQ' THEN 1
        WHEN 'SUQ' THEN 2 WHEN 'FAQ' THEN 3 END)
    - (CASE substr(graduating_cohort,5,3)
        WHEN 'WIQ' THEN 0 WHEN 'SPQ' THEN 1
        WHEN 'SUQ' THEN 2 WHEN 'FAQ' THEN 3 END)  AS "Terms (grad to test)",
    COUNT(*)                                      AS "Students"
FROM students
GROUP BY 1
ORDER BY 1
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++%28CAST%28substr%28first_testing_cohort%2C1%2C4%29+AS+INTEGER%29+-%0A+++++CAST%28substr%28graduating_cohort%2C1%2C4%29++++AS+INTEGER%29%29+%2A+4%0A++++%2B+%28CASE+substr%28first_testing_cohort%2C5%2C3%29%0A++++++++WHEN+%27WIQ%27+THEN+0+WHEN+%27SPQ%27+THEN+1%0A++++++++WHEN+%27SUQ%27+THEN+2+WHEN+%27FAQ%27+THEN+3+END%29%0A++++-+%28CASE+substr%28graduating_cohort%2C5%2C3%29%0A++++++++WHEN+%27WIQ%27+THEN+0+WHEN+%27SPQ%27+THEN+1%0A++++++++WHEN+%27SUQ%27+THEN+2+WHEN+%27FAQ%27+THEN+3+END%29++AS+%22Terms+%28grad+to+test%29%22%2C%0A++++COUNT%28%2A%29++++++++++++++++++++++++++++++++++++++AS+%22Students%22%0AFROM+students%0AGROUP+BY+1%0AORDER+BY+1%0ALIMIT+10%3B)

Both queries return:

| Terms (Grad to Test) | Students |
|---:|---:|
| −3 | 1 |
| −1 | 2 |
| 0 | 443 |
| +1 | 6,014 |
| +2 | 226 |
| +3 | 41 |
| +4 | 21 |
| +5 | 7 |
| +6 | 8 |
| +7 | 6 |

The shape of the distribution is the same in both. The query that produced it is much easier to read in the first version. The case study takes term_order as a hard prerequisite for the rest of phase 03's term math.

The distribution is heavily concentrated at one quarter post-graduation: 6,014 students (88.19 percent of the cohort) tested exactly one quarter after their recorded graduating cohort. Another 443 (6.50 percent) tested in the same quarter as graduation, and 226 (3.31 percent) tested two quarters later. The remaining 136 students scatter across a thin tail running from three to forty-four quarters out. Only three students show a negative gap, testing in a term before their recorded graduating cohort, which under the validated term ordering reduces to a small handful of data-entry quirks rather than a structural pattern. Phase 03 develops the delay-distribution analysis with regional and campus breakdowns.

## Left-Censored Students: A Flag, Not An Exclusion

The window opens in winter 2024 and closes in fall 2025. Some students in the data failed their first NCLEX attempt before winter 2024, retook in the window, and so appear with `Attempt Number = 2` or higher as their earliest row. They are left-censored: their first attempt is not visible.

A naive schema would exclude these students, on the reasoning that "first-time pass rate analysis needs visible first attempts." A more careful schema flags them and lets each analysis decide what to do.

```sql
-- Left-censored students: those whose earliest visible attempt is
-- not Attempt 1. The minority are 114 of 6,819, but they are real
-- students whose first attempts simply happened before the window.
SELECT
    SUM(CASE WHEN first_visible_attempt = 1 THEN 1 ELSE 0 END) AS "First Attempt Visible",
    SUM(CASE WHEN first_visible_attempt > 1 THEN 1 ELSE 0 END) AS "Left-Censored",
    ROUND(100.0 * SUM(CASE WHEN first_visible_attempt > 1 THEN 1 ELSE 0 END)
                / COUNT(*), 2)                                AS "% Left-Censored"
FROM students;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/penobscot-nclex.sqlite#/penobscot-nclex?sql=SELECT%0A++++SUM%28CASE+WHEN+first_visible_attempt+%3D+1+THEN+1+ELSE+0+END%29+AS+%22First+Attempt+Visible%22%2C%0A++++SUM%28CASE+WHEN+first_visible_attempt+%3E+1+THEN+1+ELSE+0+END%29+AS+%22Left-Censored%22%2C%0A++++ROUND%28100.0+%2A+SUM%28CASE+WHEN+first_visible_attempt+%3E+1+THEN+1+ELSE+0+END%29%0A++++++++++++++++%2F+COUNT%28%2A%29%2C+2%29++++++++++++++++++++++++++++++++AS+%22%25+Left-Censored%22%0AFROM+students%3B)

Result:

| First Attempt Visible | Left-Censored | % Left-Censored |
|---:|---:|---:|
| 6,705 | 114 | 1.67 |

114 students of 6,819 are left-censored, 1.67 percent of the population. The number is small but real. Phase 03's first-time pass rate analysis filters them out (`WHERE first_visible_attempt = 1`); phase 04's retake analysis includes them, because their retake patterns are real even if their first-attempt failures predate the window. Flagging rather than excluding is what lets each phase make the call rather than forcing one decision at build time.

## Looking Ahead

[Phase 03 (Exploration)](/archivo/penobscot-nclex/03-exploration/) takes the schema as given and runs the orientation queries: first-time pass rates by region, campus, program, and cohort, with confidence intervals computed inline in SQL using the standard `1.96 * SQRT(p * (1 - p) / n)` formula. The campus spread phase 01 surfaced gets its first full breakdown with sample-size context. The cohort trend across the two-year window gets its first visualization. The retake-attempt distribution and the time-from-graduation-to-test concentration at one quarter get their first development.

[Phase 04 (Findings)](/archivo/penobscot-nclex/04-findings/) develops the three threads worth following at depth: the 21-point campus spread and what its size implies about where intervention should focus, the post-NGN cohort decline that tracks the national rate at a similar pace while sitting two to three points below national throughout, and the retake conversion rate that runs more than twenty percentage points above the [NCSBN](https://www.ncsbn.org/) national benchmark for repeat NCLEX-RN takers. The predictive-modeling discussion at the end of phase 04 switches briefly to R for the logistic regression and AUC discussion, where SQL hits its analytical ceiling.

