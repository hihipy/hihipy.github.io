---
title: "Source"
weight: 10
description: "The source-of-truth phase. Where College Scorecard's data comes from, the 39-CSV file structure, the 3,308-column reality of each MERGED file, the structural quirks of the export, and the scope decision: Florida four-year institutions, 2014-2023."
summary: "Where the data comes from and what's actually in it"
tags: ["college-scorecard", "csv", "data-quality", "public-data", "sql"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
The case study starts with the source data. College Scorecard publishes 39 CSVs per release; this database keeps a verified slice of three.
{{< /lead >}}

## At a Glance

The U.S. Department of Education's [College Scorecard](https://collegescorecard.ed.gov/data/) is the canonical federal dataset on American higher education. It contains institution-level financial, enrollment, and outcome metrics for every Title IV-eligible institution in the country, updated annually since 2009. The current release contains 39 CSVs per year. This case study reduces a single-state slice of that data to a three-table SQLite database covering 112 Florida four-year institutions across cohort years 2014 to 2023.

```sql
-- Three-table row count summary used in the At a Glance section.
-- UNION ALL stacks the count of each table into a single result set.
-- The 112-institution count, 920 annual_metrics rows, and 36,610
-- field_of_study rows together describe the database shape: a small
-- number of institutions, ten years of annual reports, and dozens to
-- hundreds of program-level rows per institution.
SELECT
    'institutions'           AS "Table",
    printf('%,d', COUNT(*))  AS "Rows"
FROM institutions
UNION ALL
SELECT
    'annual_metrics',
    printf('%,d', COUNT(*))
FROM annual_metrics
UNION ALL
SELECT
    'field_of_study',
    printf('%,d', COUNT(*))
FROM field_of_study;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++%27institutions%27+AS+%22Table%22%2C%0A++++COUNT%28%2A%29+++++++AS+%22Rows%22%0AFROM+institutions%0AUNION+ALL%0ASELECT%0A++++%27annual_metrics%27%2C%0A++++COUNT%28%2A%29%0AFROM+annual_metrics%0AUNION+ALL%0ASELECT%0A++++%27field_of_study%27%2C%0A++++COUNT%28%2A%29%0AFROM+field_of_study%3B)

Result:

| Table | Rows |
|---|---:|
| institutions | 112 |
| annual_metrics | 920 |
| field_of_study | 36,610 |

The deliverable is a 4 MB SQLite file at [pgbd.casa/data/college-scorecard-fl.sqlite](https://pgbd.casa/data/college-scorecard-fl.sqlite), queryable directly in the browser via [Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite). Every query in this case study runs against that file. Every claim in the prose is verifiable by re-running the query the prose cites.

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

## The Source

College Scorecard is published by the Office of Federal Student Aid within the U.S. Department of Education. The data is collected from federal financial aid reporting (IPEDS, the Federal Student Aid program data, the Treasury Department's earnings records via tax data), aggregated to the institution level, and released as a unified annual snapshot. The first public release was 2009; the data goes back further for some metrics.

What the Scorecard measures is broad: enrollment counts, demographic breakdowns, average net price by income band, federal student loan default rates, completion rates at multiple time horizons, post-graduation earnings, repayment rates, parental income distributions, debt at graduation by program, and dozens of other metrics. What it does not measure is also worth naming: state-level financial aid, institutional reputation, faculty composition, classroom experience, employer perceptions, and many qualitative dimensions of educational value. The Scorecard is a structured, federally-collected, comparable dataset across institutions; it is not a complete picture of any institution.

The release cadence is annual. Each year's release covers a "cohort year" referring to the academic year in which students entered. Cohort year 2023 in the data refers to students who entered in academic year 2023-24. Most metrics are reported within two years of the cohort year (so the 2023 cohort year report appears in the 2024 release). A handful of long-horizon metrics like 10-year-out earnings are reported less frequently.

## The 39-CSV Reality

Every College Scorecard release ships as a directory of 39 CSV files plus a Crosswalks subdirectory plus a FieldOfStudy subdirectory. The naming convention is structured: `MERGED2023_24_PP.csv` is the institution-level data for cohort year 2023; `FieldOfStudyData2122_2223_PP.csv` is the field-of-study data covering cohort years 2021-22 and 2022-23 jointly.

The `MERGED` files contain one row per institution, with columns for every metric the Scorecard reports for that year. The `FieldOfStudy` files contain one row per (institution × CIPCODE × credential level) combination, where CIPCODE is the federal Classification of Instructional Programs code (a six-digit hierarchical code identifying every academic field). The Crosswalks directory contains lookup tables for IPEDS-to-OPEID identifier matching and for CIPCODE descriptions.

The build script for this case study processes 10 of the 39 CSVs (the cohort-year files for 2014 through 2023) plus the corresponding FieldOfStudy files. The other 29 CSVs in each release contain metadata, technical reference data, and earlier-cohort historical data that this case study does not use. The full 39-CSV release is roughly 3.6 GB uncompressed; the Florida four-year slice we keep is 4 MB.

The two-cohort encoding in FieldOfStudy filenames warrants a closer look. A file named `FieldOfStudyData1415_1516_PP.csv` covers students who entered in 2014-15 AND 2015-16. The reason: field-of-study completion data needs at least two cohort years of post-entry observation to be meaningful, so the Scorecard reports them in two-year windows. The build script keeps the file whose first cohort year matches each window we want.

## The 3,308-Column Reality

A single MERGED CSV has 3,308 columns. This is not a typo. The Scorecard's columnar structure represents every metric multiplied across multiple demographic breakdowns: each completion rate, for instance, is reported as an overall figure and then again for white, Black, Hispanic, Asian, American Indian, Native Hawaiian, two-or-more-races, unknown, nonresident-alien, and other categories; each demographic figure is then reported again for Pell-eligible vs not, for first-generation vs not, for full-time vs part-time, and for several other dimensions. The result is dozens of columns per "metric" depending on how you count.

The 3,308-column reality means a naive CSV import is not viable. The build script picks 14 columns from the 3,308 (the ones this case study actually queries) and discards the other 3,294. Phase 02 documents [the column pruning](/archivo/college-scorecard-fl/02-schema/#the-column-pruning) decision in detail. The 14 columns chosen include the institution name, sector code (public/private nonprofit/for-profit), enrollment counts, in-state tuition, average net price by sector, completion rates at 150% and 200% of normal time, Pell percentage, default rate, and 10-year-out median earnings.

The trade-off is honesty. By dropping 3,294 columns, this case study cannot answer questions like "what is the completion rate gap between Pell-eligible and non-Pell-eligible students at Florida public universities" or "how does first-generation enrollment compare across sectors." Those questions require a richer extract than this one. The 14 columns we keep are sufficient for the scope of analysis we describe; for a different scope, the build script would extract different columns.

## Structural Quirks Worth Documenting

College Scorecard has eight structural patterns that surprise on first contact and require deliberate handling in the build:

1. **`PrivacySuppressed` is a literal string, not a NULL.** When a metric is suppressed for FERPA compliance (typically because the underlying cohort is small enough that the individual student could be identified), the cell value is the literal string `PrivacySuppressed`. The build script converts this to SQL NULL.

2. **`NULL` is also a literal string.** Some columns use the literal text `NULL` to indicate missing data instead of an empty cell. The build script handles both empty cells and the literal `NULL` string the same way.

3. **Sector codes are integers, not strings.** The CONTROL column uses 1 for public, 2 for private nonprofit, 3 for for-profit. The build script translates these to readable strings during the load.

4. **Institution numbers (UNITID) are stable across years; institution names are not.** Florida State College at Jacksonville was reported as "Florida Community College at Jacksonville" in earlier years. The build script joins by UNITID (the federal Unit IDentifier), not by name.

5. **The cohort year naming convention buries the year in the filename.** `MERGED2014_15_PP.csv` does not contain a "cohort_year" column; the year is parsed from the filename. The build script extracts cohort_year as 2014 from this filename.

6. **The 10-year-out earnings metric is reported only every six years.** `md_earn_wne_p10` is in the 2014 cohort report and the 2020 cohort report; intermediate cohort years have NULL for this column. Phase 02 documents [the earnings reporting cadence](/archivo/college-scorecard-fl/02-schema/#the-earnings-reporting-cadence).

7. **Field-of-study data joins by UNITID and CIPCODE.** A single institution has dozens to hundreds of program rows, each one (CIPCODE × CREDLEV) combination. The build script keeps the FieldOfStudy table separate from the institution-and-year-level data.

8. **Completion rates use first-time-full-time cohort definitions.** The `c150_4` metric (completion within 150% of normal time, four-year cohort) measures specifically first-time, full-time bachelor's-seeking students. At institutions whose student bodies are mostly part-time or transfer students, the metric can return zero even when the institution graduates students normally. Phase 03 documents [the c150_4 measurement-artifact pattern](/archivo/college-scorecard-fl/03-exploration/#completion-rates) with verified evidence.

Each of these is documented in the build script's docstring header. None of them is a defect; they are simply the conventions of how the Scorecard reports.

## The Scope Decision

The case study scope is **Florida four-year institutions, 2014 to 2023, all sectors**. Three filter decisions:

**State filter: Florida only.** I live in Florida and work at a Florida public university (the University of Miami's Miller School of Medicine), so Florida is the state I have the most context for. The Scorecard data is comparable across states, but the analytical interpretation is sharper when I can ground it in local knowledge of which institutions exist and what they do.

**Institution-type filter: four-year only.** PREDDEG is the College Scorecard's predominant degree level: 1 (less than 2-year), 2 (2-year), 3 (4-year), 4 (graduate). The build script filters to PREDDEG IN (3, 4), keeping institutions whose dominant credential is at least a bachelor's degree. This excludes Florida's substantial community college and trade-school sectors. A different scope would include them.

**Cohort year filter: 2014 through 2023.** The 2014 lower bound is the first year that has reasonably stable column definitions across the demographic breakdowns. Earlier years have substantial schema drift that would complicate cross-year comparison. The 2023 upper bound is simply the most recent year with reported data at the time the build script was written.

**Sector inclusion: all three sectors.** Public, private nonprofit, and for-profit all stay in the database. The for-profit sector is the noisiest analytically (the closure wave during this window means many for-profits report partial data) but excluding them would erase the most interesting analytical thread the data offers.

The result is 112 institutions: 15 public, 61 private nonprofit, 36 for-profit. The build script does not deduplicate or merge institutions; if a single brand has multiple campuses (Polytechnic University of Puerto Rico-Miami and Polytechnic University of Puerto Rico-Orlando, for instance), each campus is a separate row in the institutions table.

## The Closure-Wave Discovery

The first observation that pointed toward an analytical thread came from a single query: how many institutions report data each year? The answer is not constant, and the shape of the not-constant tells a story.

```sql
-- Institutions reporting per cohort year, the orientation query that
-- surfaces the closure-wave thread. The drop from 98 institutions in
-- 2014 to 88 by 2020 is the row-level signal that something structural
-- changed in the for-profit sector during the 2017-2020 window.
-- Phase 03 documents the per-sector counts; phase 04 develops the
-- enrollment displacement and survivor trajectory threads further.
SELECT
    cohort_year AS "Cohort Year",
    COUNT(*)    AS "Institutions Reporting"
FROM annual_metrics
GROUP BY cohort_year
ORDER BY cohort_year;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++cohort_year+AS+%22Cohort+Year%22%2C%0A++++COUNT%28%2A%29++++AS+%22Institutions+Reporting%22%0AFROM+annual_metrics%0AGROUP+BY+cohort_year%0AORDER+BY+cohort_year%3B)

Result:

| Cohort Year | Institutions Reporting |
|---:|---:|
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

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Florida four-year institution count drops from 98 in 2014 to 88 in 2020 and stays there through 2023.</p>
<p class="pgbd-case-chart-sub">Number of Florida four-year institutions reporting in each cohort year. Most of the drop is concentrated between 2017 and 2020, the for-profit closure-wave window. The flat 88-institution baseline since 2020 is the post-closure equilibrium.</p>
{{< chart >}}
type: 'line',
data: {
  labels: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
  datasets: [
    {
      label: 'Institutions Reporting',
      data: [98, 98, 97, 96, 90, 89, 88, 87, 89, 88],
      borderColor: '#0969DA',
      backgroundColor: 'rgba(9, 105, 218, 0.10)',
      borderWidth: 2.5,
      fill: true,
      tension: 0.2,
      pointRadius: 3.5,
      pointHoverRadius: 6,
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
          return context.parsed.y + ' institutions';
        }
      }
    }
  },
  scales: {
    x: { title: { display: true, text: 'Cohort Year' } },
    y: { title: { display: true, text: 'Institutions Reporting' }, beginAtZero: false, suggestedMin: 80, suggestedMax: 100 }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

A net loss of ten institutions across nine years is not a dramatic absolute number, but the shape matters. The drop is not gradual. It is concentrated between 2017 and 2020, with most of the contraction (98 to 88) happening in three years. The post-2020 baseline is essentially flat. Whatever caused the 2017-2020 drop was a discrete event, not a long-term trend.

The discrete event was the for-profit closure wave. Argosy University (parent of Argosy Sarasota and Argosy Tampa), Sanford-Brown, Education Management Corporation's broader collapse, and the Federal Student Aid program's tightening of regulations all happened in this window. Phases 03 and 04 develop the closure-wave thread further: Phase 03 documents [the for-profit shrinkage by sector](/archivo/college-scorecard-fl/03-exploration/#counts-by-sector-and-year), and Phase 04 documents [the enrollment displacement](/archivo/college-scorecard-fl/04-findings/#the-closure-wave-concentration) and [where the displaced students went](/archivo/college-scorecard-fl/04-findings/#where-did-the-students-go).

This is how an analytical thread emerges from data. Not from a research question imposed on the data, but from a row count that does not look like the row count you would expect.

## What Comes Next

[Phase 02 (Schema)](/archivo/college-scorecard-fl/02-schema/) documents the build script's eight major decisions: the three-table structure, the scope filter, the column pruning, the privacy-suppression handling, the earnings reporting cadence, the cross-year schema stability, the five verification invariants, and the build gap on the HBCU flag column. It is the technical reference for the database.

[Phase 03 (Exploration)](/archivo/college-scorecard-fl/03-exploration/) covers the orientation queries: how many institutions per sector, what they cost, who completes, what programs they offer. It is the single-dimension shape of the data.

[Phase 04 (Findings)](/archivo/college-scorecard-fl/04-findings/) covers the intersection analyses: cost-per-completer ranking within sectors, the closure-wave concentration, where the displaced students went, the HBCU comparison, and the 10-year-earnings ranking. It is what the data shows when the questions are sharper.

The case study philosophy lives at the [biblioteca](/biblioteca/). Every query is reproducible. Every claim is from a captured query. The reproducibility-is-the-floor commitment is satisfied: anyone can re-run any query in this case study, change the parameters, and ask their own questions.
