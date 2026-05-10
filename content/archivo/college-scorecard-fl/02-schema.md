---
title: "Schema"
weight: 20
description: "The schema design phase. Three normalized tables (institutions, annual_metrics, field_of_study), the column-pruning logic that took 3,308 columns down to ~70, the privacy-suppression handling, and the build script as a documented artifact."
summary: "Three tables, seventy columns, and a build script that verifies itself"
tags: ["sql", "sqlite", "schema-design", "python", "etl"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
A 3.6 GB raw download becomes a 30 MB queryable database. The decisions that shrink it without losing the analytical questions.
{{< /lead >}}

## At a Glance

The source phase produced a scope and a starting point: 112 Florida four-year institutions across the decade, the data lives in 39 CSV files spread across three subdirectories, each MERGED file has 3,308 columns. The raw data on disk is 3.6 gigabytes. Most of that is column bloat (demographic disaggregations of every metric, separate columns for Pell-recipient vs non-Pell-recipient earnings, same metric repeated under multiple statistical aggregations). The analytical questions phase 03 and phase 04 will ask need maybe seventy of those 3,308 columns.

This phase walks through the schema design that took the raw download and produced a queryable SQLite database (the actual file is at `https://pgbd.casa/data/college-scorecard-fl.sqlite` for direct download). Three normalized tables, deliberate column selection, explicit privacy-suppression handling, and five verification invariants the build script checks before it claims success. The build script itself is at [`tools/build_florida_scorecard.py`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/build_florida_scorecard.py) on GitHub: roughly 560 lines documenting every decision the schema makes.

## The Three-Table Schema

The first decision: do not put all the data in one table. The College Scorecard MERGED file is denormalized by design (institution metadata, year-varying metrics, and aggregate program data all sit in one wide row), and a one-table copy would either repeat institution metadata across every cohort year (bloat) or strip it out entirely (loss). Three tables, normalized along the dimensions that vary, keeps both.

The schema:

| Table | Grain | Rows |
|---|---|---|
| `institutions` | One row per UNITID | 112 |
| `annual_metrics` | One row per (UNITID, cohort_year) | 920 |
| `field_of_study` | One row per (UNITID, cohort_year, CIPCODE, CREDLEV) | 36,610 |

```sql
-- Verify the row counts in each of the three tables produced by
-- the build script. The grain of each table is named in the second
-- column for documentation. Phase 02's prose claims about the
-- schema all reduce to these three numbers.
SELECT
    'institutions'                                          AS "Table",
    'one row per UNITID'                                    AS "Grain",
    COUNT(*)                                                AS "Rows"
FROM institutions
UNION ALL
SELECT
    'annual_metrics',
    'one row per (UNITID, cohort_year)',
    COUNT(*)
FROM annual_metrics
UNION ALL
SELECT
    'field_of_study',
    'one row per (UNITID, cohort_year, CIPCODE, CREDLEV)',
    COUNT(*)
FROM field_of_study;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT+%27institutions%27+AS+table_name%2C+COUNT%28*%29+AS+rows+FROM+institutions+UNION+ALL+SELECT+%27annual_metrics%27%2C+COUNT%28*%29+FROM+annual_metrics+UNION+ALL+SELECT+%27field_of_study%27%2C+COUNT%28*%29+FROM+field_of_study%3B)

The `institutions` table holds stable metadata: institution name, location, accreditation agency, Carnegie classifications, minority-serving institution flags, the derived `sector` column (one of "public", "private_nonprofit", "for_profit") and two derived columns (`first_year_in_data`, `last_year_in_data`) that mark when each UNITID first appeared and last appeared in the window. Those last two are essential for the closure-wave analysis in phase 04 and would be expensive to compute at runtime.

The `annual_metrics` table holds year-varying metrics: enrollment by demographic, cost (in-state and out-of-state tuition, average net price by sector), aid (Pell percentage, federal loan percentage), debt (median completer debt, median withdrawal debt, ten-year debt), completion rates (150 percent of normal time, 200 percent of normal time), median earnings at six, eight, and ten years post-entry, and repayment outcomes (three-year repayment rate, two-year and three-year cohort default rates). Roughly thirty-five columns of year-varying metrics per (institution, year).

The `field_of_study` table holds program-level outcomes: median debt at completion and median earnings at one, two, and three years post-completion, broken out by CIP code (academic discipline) and credential level (bachelor's, master's, doctoral, etc.). 36,610 rows because Florida four-year institutions collectively offer hundreds of distinct (CIP code, credential level) combinations, each reported across multiple cohort years.

## The Scope Filter

The second decision: what counts as a "Florida four-year institution"?

The filter applied in the build script is `STABBR = 'FL'` AND `PREDDEG IN (3, 4)`. The first clause restricts to Florida by U.S. Postal Service state abbreviation. The second restricts to institutions whose predominant degree (PREDDEG) is bachelor's (code 3) or graduate (code 4). This excludes:

- Two-year institutions where the predominant degree is associate (code 2)
- Certificate-only institutions (code 1)
- Institutions with no predominant degree designation (code 0)

The State College System four-year bachelor programs ARE included, since institutions that offer some bachelor degrees (Miami Dade College, Broward College, etc.) have PREDDEG = 3 once they cross the threshold of awarding mostly bachelor's credentials.

Sector breakdown after filtering:

```sql
-- Florida four-year institutions by sector across the full window.
-- COUNT(*) on institutions (one row per UNITID) is the right unit:
-- a UNITID is a UNITID regardless of how many years it reported.
-- Sectors derived during build from the CONTROL code:
-- 1=public, 2=private nonprofit, 3=for-profit.
SELECT
    sector       AS "Sector",
    COUNT(*)     AS "Institutions"
FROM institutions
GROUP BY sector
ORDER BY COUNT(*) DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT+sector%2C+COUNT%28*%29+AS+institutions+FROM+institutions+GROUP+BY+sector+ORDER+BY+institutions+DESC%3B)

Result:

| Sector | Institutions |
|---|---:|
| private_nonprofit | 61 |
| for_profit | 36 |
| public | 15 |

Florida's public four-year sector is small (the State University System has twelve members, plus a handful of UNITIDs that capture institutional substructure like UF Online and the pre-2020 USF satellite campuses). The private nonprofit sector is large and stable. The for-profit sector is volatile: 36 distinct institutions across the decade, but as phase 04 will show, fewer than half of those survived all ten years.

## The Column Pruning

The third decision: how many of the 3,308 MERGED columns to keep.

Each MERGED file's 3,308 columns are a Cartesian product of: the base metric (cost, completion, debt, earnings, etc.), demographic disaggregation (all, by gender, by race, by Pell status), aggregation method (count, mean, median), and time horizon (six years post-entry, eight years, ten years). The full matrix gives immense statistical power for population-level analysis but is wildly more granular than any single case study needs.

The build script keeps roughly seventy columns: the headline metric for each analytical category (median earnings, not the demographic breakdown; median debt, not the count-of-borrowers split), the institution metadata for joins, and the cohort-year identifier. The retained set covers the questions phase 04 will ask: cost trajectories by sector, completion rate distributions, debt-to-earnings ratios, the closure wave forensics. The 3,238 unretained columns are not deleted from the source (a future analyst with a different question can re-run the build script with a different column list); they are simply not in this case study's database.

The decision rule: a column earns retention if it is the headline metric for an analytical question phase 03 or phase 04 will ask. A column does not earn retention if it is a demographic disaggregation of a column already retained, since the disaggregation can be re-derived if needed by re-running the build with that column added.

## Privacy Suppression as a First-Class Citizen

The fourth decision: how to handle the College Scorecard's two missing-data conventions.

College Scorecard uses two distinct strings to indicate missing data:

- `"PrivacySuppressed"` (literal string, no quotes in the file): the value exists but the cell size is below the privacy threshold (small cohorts get suppressed to prevent re-identification of individual students)
- `"NULL"` (literal string): the value does not exist for some other reason (the institution did not report, the metric does not apply to this institution type, the data was not collected for this cohort)

A naive parser treats both as strings and the column types come out as TEXT instead of REAL. SQL aggregates against TEXT columns produce errors or wrong results. The build script coerces both literal strings to Python `None` at load time, which becomes SQL `NULL`, which behaves correctly in `IS NULL` checks and is automatically excluded from `AVG()`, `SUM()`, and similar aggregates.

The cost of this collapsing: the database loses the ability to distinguish "data was suppressed for privacy" from "data was not reported" at query time. The build script documents this as a deliberate tradeoff in its decision log; an analyst who needs the distinction can re-run the build with a separate column tracking the original missing-data category.

The privacy-suppression pattern is not uniform. Different metrics get suppressed at very different rates:

```sql
-- Fill-rate audit: how often is each headline metric actually
-- populated, given that College Scorecard suppresses small-cohort
-- values for privacy and reports some metrics on multi-year cycles?
-- COUNT(*) is the row total (920 institution-years); COUNT(col)
-- on a numeric column counts non-NULL values. The ratio is the
-- percentage of rows where the metric is actually present.
-- Six metrics span the analytical surface phase 04 will exercise.
SELECT
    'ugds (enrollment)'                                AS "Metric",
    COUNT(*)                                           AS "Total Rows",
    COUNT(ugds)                                        AS "Non-Null",
    ROUND(100.0 * COUNT(ugds) / COUNT(*), 1)           AS "% Filled"
FROM annual_metrics
UNION ALL
SELECT
    'tuitionfee_in (in-state tuition)',
    COUNT(*),
    COUNT(tuitionfee_in),
    ROUND(100.0 * COUNT(tuitionfee_in) / COUNT(*), 1)
FROM annual_metrics
UNION ALL
SELECT
    'c150_4 (completion rate)',
    COUNT(*),
    COUNT(c150_4),
    ROUND(100.0 * COUNT(c150_4) / COUNT(*), 1)
FROM annual_metrics
UNION ALL
SELECT
    'md_earn_wne_p10 (10-year earnings)',
    COUNT(*),
    COUNT(md_earn_wne_p10),
    ROUND(100.0 * COUNT(md_earn_wne_p10) / COUNT(*), 1)
FROM annual_metrics
UNION ALL
SELECT
    'grad_debt_mdn (median completer debt)',
    COUNT(*),
    COUNT(grad_debt_mdn),
    ROUND(100.0 * COUNT(grad_debt_mdn) / COUNT(*), 1)
FROM annual_metrics
UNION ALL
SELECT
    'cdr3 (3-year default rate)',
    COUNT(*),
    COUNT(cdr3),
    ROUND(100.0 * COUNT(cdr3) / COUNT(*), 1)
FROM annual_metrics
ORDER BY "% Filled" DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT+%27ugds%27+AS+metric%2C+COUNT%28*%29+AS+total_rows%2C+COUNT%28ugds%29+AS+non_null%2C+ROUND%28100.0+*+COUNT%28ugds%29+%2F+COUNT%28*%29%2C+1%29+AS+pct_filled+FROM+annual_metrics+UNION+ALL+SELECT+%27tuitionfee_in%27%2C+COUNT%28*%29%2C+COUNT%28tuitionfee_in%29%2C+ROUND%28100.0+*+COUNT%28tuitionfee_in%29+%2F+COUNT%28*%29%2C+1%29+FROM+annual_metrics+UNION+ALL+SELECT+%27c150_4%27%2C+COUNT%28*%29%2C+COUNT%28c150_4%29%2C+ROUND%28100.0+*+COUNT%28c150_4%29+%2F+COUNT%28*%29%2C+1%29+FROM+annual_metrics+UNION+ALL+SELECT+%27md_earn_wne_p10%27%2C+COUNT%28*%29%2C+COUNT%28md_earn_wne_p10%29%2C+ROUND%28100.0+*+COUNT%28md_earn_wne_p10%29+%2F+COUNT%28*%29%2C+1%29+FROM+annual_metrics+UNION+ALL+SELECT+%27grad_debt_mdn%27%2C+COUNT%28*%29%2C+COUNT%28grad_debt_mdn%29%2C+ROUND%28100.0+*+COUNT%28grad_debt_mdn%29+%2F+COUNT%28*%29%2C+1%29+FROM+annual_metrics+UNION+ALL+SELECT+%27cdr3%27%2C+COUNT%28*%29%2C+COUNT%28cdr3%29%2C+ROUND%28100.0+*+COUNT%28cdr3%29+%2F+COUNT%28*%29%2C+1%29+FROM+annual_metrics+ORDER+BY+pct_filled+DESC%3B)

Result:

| Metric | Total Rows | Non-Null | % Filled |
|---|---:|---:|---:|
| cdr3 (default rate) | 920 | 858 | 93.3 |
| ugds (enrollment) | 920 | 846 | 92.0 |
| tuitionfee_in | 920 | 798 | 86.7 |
| c150_4 (completion) | 920 | 730 | 79.3 |
| grad_debt_mdn | 920 | 523 | 56.8 |
| md_earn_wne_p10 | 920 | 147 | 16.0 |

Enrollment and default-rate data are nearly always present. Completion rates are present for most institutions most years. Median completer debt is missing for nearly half the rows, mostly small institutions whose cohorts fall below privacy thresholds. Ten-year-out median earnings (`md_earn_wne_p10`) is filled for only 147 of 920 rows, sixteen percent.

The earnings number is unexpectedly low. A first reading might attribute it to widespread privacy suppression. The actual cause is structural and worth documenting before phase 04 builds analyses that depend on this column.

## The Earnings Reporting Cadence

The fifth decision: name the structural quirk in earnings reporting before phase 04 stumbles into it.

Looking at where the 147 filled `md_earn_wne_p10` rows actually live in the data:

```sql
-- Drill into the md_earn_wne_p10 fill pattern by year and sector.
-- The hypothesis when the headline 16% number surfaced was that
-- privacy suppression was hitting small-institution rows hard.
-- This query tests it: if suppression is the cause, the fill rate
-- should be roughly even across years and concentrate in larger
-- institutions. If reporting cadence is the cause, the fill rate
-- should cluster in specific years and be sector-uniform within
-- those years.
SELECT
    am.cohort_year                                              AS "Cohort Year",
    i.sector                                                    AS "Sector",
    COUNT(*)                                                    AS "Rows",
    COUNT(am.md_earn_wne_p10)                                   AS "Earnings Filled",
    ROUND(100.0 * COUNT(am.md_earn_wne_p10) / COUNT(*), 1)      AS "% Filled"
FROM annual_metrics am
JOIN institutions   i USING (unitid)
GROUP BY am.cohort_year, i.sector
ORDER BY am.cohort_year, i.sector;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT+am.cohort_year%2C+i.sector%2C+COUNT%28*%29+AS+rows%2C+COUNT%28am.md_earn_wne_p10%29+AS+earn_p10_filled%2C+ROUND%28100.0+*+COUNT%28am.md_earn_wne_p10%29+%2F+COUNT%28*%29%2C+1%29+AS+pct_filled+FROM+annual_metrics+am+JOIN+institutions+i+USING+%28unitid%29+GROUP+BY+am.cohort_year%2C+i.sector+ORDER+BY+am.cohort_year%2C+i.sector%3B)

Two cohort years account for all the filled values: 2014 and 2020. Every other year reports zero filled rows for ten-year earnings, regardless of sector.

This is not random privacy suppression. It is the College Scorecard's reporting cadence. Ten-year-out earnings require federal tax data linked to the cohort five years after the cohort completed, which is itself five years after the cohort entered: a fifteen-year reporting lag from cohort entry to data availability. The Department of Education does not update this column annually. They release ten-year earnings as periodic look-back snapshots, currently spaced about five to six years apart.

The cohort year 2014 column reports earnings for students who entered in 2003-04 (eleven years before the file year). The cohort year 2020 column reports earnings for students who entered around 2009-10. Neither column reports earnings for students who entered in the year named on the file.

This matters for analysis. Any phase 04 query that joins `md_earn_wne_p10` to `cohort_year` should treat the cohort year as a reporting year, not an entry year, and should expect to find this column filled only for 2014 and 2020 rows. Six-year earnings (`md_earn_wne_p6`) and eight-year earnings (`md_earn_wne_p8`) follow the same pattern; only the lag horizons differ.

A phase 04 finding that says "earnings rose from 2014 to 2020" is therefore comparing two cohorts that entered six years apart, not two cohorts measured at the same horizon. The case study will frame these comparisons explicitly.

## Cross-Year Schema Stability

The sixth decision: trust that the schema is stable across the decade.

A common build-script complication for longitudinal analysis is that source files change schema across years. Columns get renamed, added, retired. Build scripts have to either backfill, accept missing data, or maintain a year-by-year column-mapping table.

College Scorecard avoided this entirely. Comparing the 2014-15 MERGED file's column set to the 2023-24 MERGED file's column set: zero columns differ. All 3,308 columns are present in both. The build script does not need defensive handling for missing columns. The column-name choices made in 2014 are still valid in 2023.

```bash
# Verification (run from the College Scorecard download directory)
diff <(head -1 MERGED2014_15_PP.csv | tr ',' '\n' | sort -u) \
     <(head -1 MERGED2023_24_PP.csv | tr ',' '\n' | sort -u)
# Output: empty (no differences)
```

This stability is unusual for federal datasets and worth flagging. NIH RePORTER's export format has changed multiple times in the same window (the kentucky-nih case study documents a column reorganization between 2018 and 2020). College Scorecard has not.

## The Five Verification Invariants

The seventh decision: prove the schema works before claiming it does.

Following the kentucky-nih precedent, the build script verifies five invariants before declaring success. If any invariant fails, the build raises an error and the database is not committed. The five invariants:

1. **All institutions have a CONTROL value of 1, 2, or 3.** Equivalent to "every institution has a recognized sector." A fail would mean an institution slipped past the four-year filter without a valid sector designation.
2. **All institutions have STABBR = 'FL'.** Equivalent to "the geographic filter held." A fail would mean a non-Florida institution made it into the database.
3. **All annual_metrics rows reference a UNITID in institutions.** A fail would mean an orphaned annual_metrics row exists without a parent institution. The foreign key declaration prevents inserts that would violate this, but the verification re-checks it after the build is complete.
4. **All field_of_study rows reference a UNITID in institutions.** Same pattern as the above, applied to the field_of_study table.
5. **All cohort_year values are in the range 2014 through 2023.** A fail would mean a row was loaded from a CSV outside the intended decade window.

All five invariants passed on the build that produced the database this case study queries. The build script's verification output is reproducible: anyone running `python tools/build_florida_scorecard.py` against a fresh download of the College Scorecard data should see the same five passing checks and the same row counts (112 institutions, 920 annual_metrics, 36,610 field_of_study).

## Coverage Gaps Worth Naming

The eighth decision: name the coverage gaps the build produces, rather than hide them.

108 of the 112 institutions have field_of_study data. The four that do not:

```sql
-- Identify institutions with NO field_of_study rows at all.
-- A LEFT JOIN with a NULL filter on the right side is the
-- canonical "anti-join" pattern: rows in institutions that have
-- no matching row in field_of_study come through with NULL on
-- every fos.* column. Sorted by last_year_in_data so closures
-- group together at the top.
SELECT
    i.instnm                AS "Institution",
    i.sector                AS "Sector",
    i.first_year_in_data    AS "First Year",
    i.last_year_in_data     AS "Last Year"
FROM institutions       i
LEFT JOIN field_of_study fos
    ON i.unitid = fos.unitid
WHERE fos.unitid IS NULL
ORDER BY i.last_year_in_data, i.instnm;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT+i.instnm%2C+i.sector%2C+i.first_year_in_data%2C+i.last_year_in_data+FROM+institutions+i+LEFT+JOIN+field_of_study+fos+ON+i.unitid+%3D+fos.unitid+WHERE+fos.unitid+IS+NULL+ORDER+BY+i.last_year_in_data%2C+i.instnm%3B)

Result:

| Institution | Sector | First Year | Last Year |
|---|---|---:|---:|
| American InterContinental University-South Florida | for_profit | 2014 | 2014 |
| Northwood University-Florida | private_nonprofit | 2014 | 2014 |
| Knox Theological Seminary | private_nonprofit | 2014 | 2015 |
| URBE University | for_profit | 2023 | 2023 |

Three of the four closed before field-of-study reporting was required for their cohort year. The fourth is too new to have field-of-study data yet. None of the four affect institution-level analyses, which can be run against `institutions` and `annual_metrics` directly. They become a documented limitation only for program-level questions in phase 04.

The annual_metrics table also has a population that varies year to year. Not every institution reports every year:

| Cohort Year | Institutions Reporting |
|---|---:|
| 2014 | 98 |
| 2015 | 98 |
| 2016 | 97 |
| 2017 | 96 |
| 2018 | 90 |
| 2019 | 89 |
| 2020 | 88 |
| 2021 | 87 |
| 2022 | 89 |
| 2023 | 88 |

The institution count drops from 98 in 2014 to 87 in 2021, then stabilizes around 88-89 through 2023. The drop is partially the for-profit closure wave (phase 04 develops this thread) and partially small institutions that report intermittently. The 112 distinct UNITIDs across the full decade is larger than any single year's count because some institutions appear only in some years (closures, openings, accreditation gaps).

## What This Phase Doesn't Solve

A schema that survived five verification invariants is not a schema that has solved every analytical problem. The earnings reporting cadence (filled only in 2014 and 2020) is a structural feature of the source data; the schema cannot fix it. The 16 percent fill rate on `md_earn_wne_p10` is honest data, not a build-script bug. Phase 04 will frame any earnings-trajectory finding around the cohort years that actually have earnings data.

Privacy suppression is also irreducible. Small institutions with small cohorts lose their median completer debt to suppression even when the underlying data exists; no amount of schema design recovers it. Phase 03 will document the suppression pattern explicitly so phase 04 does not silently exclude small institutions from analyses that depend on suppressed columns.

The schema makes the next two phases possible: orientation queries in phase 03, window functions and CTEs in phase 04, both running against a database where the structural decisions have been documented and the invariants have been verified. The reproducibility-is-the-floor commitment from the [case study philosophy](/biblioteca/) is satisfied: anyone running the same build script against the same College Scorecard download produces the same database, the same invariants, the same coverage gaps. The case study can begin.
