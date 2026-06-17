---
title: "Source"
weight: 10
description: "Where the data came from, why one state across twenty-one years, and the export limit that shaped the scope before any analysis began."
summary: "Phase 1: Source data and provenance"
tags: ["csv", "data-quality", "nih-reporter", "public-data"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Where the data came from, why one state across twenty-one years, and the export limit that shaped the scope.
{{< /lead >}}

## At a Glance

[NIH RePORTER](https://reporter.nih.gov/) is the public-facing search interface that the National Institutes of Health publishes for every research grant it funds. The database goes back decades, contains the full project metadata for each grant (principal investigator, institution, fiscal year, dollar amounts, scientific abstract, research category), and is searchable by anyone with a browser. Federal research funding is a multi-billion-dollar annual public investment, and RePORTER is the closest thing to a complete public ledger of how that money gets allocated.

This case study takes one slice of RePORTER's data: every grant awarded to a Kentucky institution from fiscal year 2005 through 2025. The slice is small enough to load locally and analyze in [SQLite](https://www.sqlite.org/), large enough to support real questions about institutional trends and research priorities, and personal to me because Kentucky is where I grew up.

This phase covers how the export came out of RePORTER and what was already strange about it before any analysis began. The next phase builds a schema on top of it; the two phases after that explore and analyze. Each phase is short enough to read on its own.

## Choosing The Scope

The scope choice has both an honest reason and a defensible reason.

The honest reason: I was born and raised in Kentucky. Of all the states I could have picked for a public-data SQL exercise, this is the one I have a personal stake in. The case study is more interesting to me to write because of that connection, and I think it reads as more honest to acknowledge the motivation than to pretend the choice was purely analytical. The [case study philosophy](/biblioteca/#approach) treats a hidden motivation as a hidden decision, and hidden decisions are exactly what the source phase exists to surface.

The defensible reasons hold up too. Kentucky is large enough to have substantial NIH activity (the University of Kentucky and the University of Louisville together account for the majority of it) but small enough that twenty-one years of data fits in a 75-megabyte SQLite file. The Appalachian region has a recognizable research footprint (opioid response, occupational safety, rural health) that gives the categorical distributions a coherent shape rather than a generic one. And none of the data overlaps with my work at the Miller School of Medicine, which keeps this a clean public-data exercise rather than a thinly disguised work project.

The twenty-one-year window from FY 2005 through FY 2025 captures three things worth seeing in the same dataset: a pre-recession baseline, the 2009 [American Recovery and Reinvestment Act](https://en.wikipedia.org/wiki/American_Recovery_and_Reinvestment_Act_of_2009) stimulus that briefly doubled NIH funding, and the post-pandemic period through the most recent complete fiscal year. Cutting the window shorter would lose one of those; extending it earlier would push past the point where RePORTER's data quality is consistent.

## The Export Limit

NIH RePORTER's CSV export caps at 15,000 records per query. The cap is not surfaced prominently in the export dialog, and the resulting CSV file gives no indication that data has been truncated. A US-wide query across twenty-one years would return well over a million records, and the export would silently deliver only the first 15,000 with no warning, no error, and no metadata distinguishing the truncated file from a complete one.

This is the kind of constraint that shapes a project before any deliberate scope decisions get made. A case study that started "let me look at NIH funding nationally" would have produced a fundamentally broken dataset that looked complete. The Kentucky-twenty-one-year scope brought the result count to 13,876, comfortably under the cap, with the bonus that any reader who wants to re-run the export can verify that 13,876 is also what they get.

Documenting the limit here is not just trivia. The [phased walkthrough](/biblioteca/#the-phased-walkthrough) section of the case study philosophy makes this point explicit: each phase exists to make visible the decisions and constraints that shaped what came next. The cap is one of those constraints; it shaped the scope as much as my personal connection to Kentucky did, and the case study is more honest for naming both.

## What's In The File

The export is one CSV file, roughly 58 megabytes at the time of export, 14,181 rows of data plus a six-line preamble plus a header row. Opening it in any text editor reveals seven structural details that the loader has to handle, none of which are documented in the export dialog. These observations were made when the file was originally exported; the file itself is not committed to this repository (the source of truth is NIH, not the portfolio site), so anyone re-exporting from the [search URL](#reproducing-the-export) below should expect the same structural quirks unless RePORTER has changed its export format since.

The seven quirks at a glance, with the impact each one has on a naive load and the resolution the build script applies:

| Quirk | Impact | Resolution |
|---|---|---|
| UTF-8 Byte-Order Mark at File Start | First Column Name Corrupted by `EF BB BF` Prefix | `encoding="utf-8-sig"` Strips the BOM During Read |
| Six-Line Preamble Before Header Row | Header Is on Line 7, Not Line 1 | `skiprows=6` |
| 54 Named Columns + Phantom 55th from Trailing Comma | Strict Parsers Refuse; Permissive Parsers Invent a Column | Drop the Phantom Column After Load |
| Quoted Fields Containing Commas, Semicolons, Quotes | Splitting Blindly on Commas Produces Wrong Field Counts | Use a real CSV parser (pandas, csv module) that respects quoting |
| Blank Strings AND Single-Space Strings Used as Null | Field Equality and `IS NULL` Checks Fail on Different Rows | Coerce Both `""` and `" "` to Proper SQL `NULL` |
| Dates in `MM/DD/YYYY` Format | Default Parsers Refuse non-ISO 8601 | Explicit `format="%m/%d/%Y"` Parsing |
| 14,181 Rows Describe 13,876 Distinct Projects | Row-Level Aggregations Double-Count Co-Funded Grants | Documented in Phase 02; Resolved by Three-Table Normalized Schema |

The detail on each quirk follows.

A UTF-8 byte-order mark at the start of the file. The BOM is three bytes (`EF BB BF`) before the first visible character. A naive CSV reader treats those bytes as part of the first column name, producing a header that does not match what subsequent reads expect.

A six-line preamble before the actual header row. The preamble contains the search criteria, the export timestamp, and a blank line. The preamble exists for human readers reviewing the file; it is invisible to RePORTER's own re-import path but breaks every CSV library that assumes line one is the header.

Fifty-four named columns plus a phantom fifty-fifth from a trailing comma on every data row. The trailing comma was almost certainly an unintended consequence of however RePORTER's CSV writer terminates each row, but the result is that every row has one more field than the header declares. A strict parser will refuse the file; a forgiving one will silently invent a column.

Quoted fields containing arbitrary text, including commas and other punctuation. Project titles and abstracts both routinely contain commas, semicolons, and quotation marks. The quoting is correct, but the parser has to be one that actually handles quoted-field semantics rather than splitting blindly on commas.

Blank or single-space strings instead of true SQL null values. Where data is absent, the field is either empty (`""`) or contains exactly one space (`" "`). Both forms appear in the same export. The schema phase has to translate both into proper nulls or any analytical query against the field will return the wrong answer.

Dates in `MM/DD/YYYY` format. Not [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), not Unix timestamps, not anything that [pandas](https://pandas.pydata.org/) or SQLite parses by default. The schema phase has to convert these explicitly, and the conversion has to be robust to the occasional malformed date that the export produces.

A row count that does not match the project count. The file has 14,181 rows but represents 13,876 distinct projects. The 305-row gap is co-funding splits, where a single project that received money from multiple NIH institutes appears as one row per (Application ID, Funding IC) combination. This is the single most important structural detail for anyone planning to query the data, because every aggregation has to decide whether to count rows or count projects, and the answer is usually different.

Each of these details gets resolved in the schema phase. The point of the source phase is to surface them so the next phase has somewhere to start.

## A First Look At The Database

The schema phase produces a SQLite database from the CSV. Before reading the schema phase in detail, it helps to see what the loaded data actually looks like: what tables exist, what columns are in each, and what a real record looks like when queried. The next four queries are the SQL equivalent of running [`dplyr::glimpse()`](https://dplyr.tidyverse.org/reference/glimpse.html) on a fresh dataset: orientation, not analysis.

```sql
-- List the tables in the database. Three tables means three grain
-- levels: one row per project, one row per (project, funder) pair,
-- one row per (project, category) pair. The schema phase explains
-- why those three grains are the right ones.
SELECT
    name AS "Table"
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+name+AS+%22Table%22+FROM+sqlite_master+WHERE+type+%3D+%27table%27+ORDER+BY+name%3B)

Result:

```text
Table
project_categories
project_funders
projects
```

The three-table structure is the answer to the row-vs-project gap surfaced above. The schema phase explains the reasoning. For now, the second query shows what columns are in each table:

```sql
-- Column types in the project_funders table. This is the smallest of
-- the three tables and the easiest to read in full. The first column
-- is the foreign key to projects; the next four are the per-funder
-- cost split that makes co-funded projects analytically tractable.
SELECT
    name  AS "Column",
    type  AS "Type"
FROM pragma_table_info('project_funders');
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+name+AS+%22Column%22%2C+type+AS+%22Type%22+FROM+pragma_table_info%28%27project_funders%27%29%3B)

Result:

```text
Column              Type
application_id      INTEGER
funding_ic          TEXT
direct_cost_ic      FLOAT
indirect_cost_ic    FLOAT
total_cost_ic       FLOAT
```

The `projects` table has 49 columns, too many to list inline. The schema phase shows the ER diagram. The third table, `project_categories`, has only two columns (`application_id` and `category`) since it just unfolds the multi-valued category string into one row per tag.

The third query shows what a single project actually looks like by pulling the most-cited record in this case study, the institutional training grant from fiscal year 2005:

```sql
-- A single project record, picking the application that gets cited
-- most in the schema phase: a 19-funder institutional training grant
-- from fiscal year 2005. Showing only the most-relevant six columns;
-- the projects table has 49 in total. CAST(...) on fiscal_year drops
-- the trailing .0 from the float storage; CAST on total_cost converts
-- the dollar amount to an integer for clean display.
SELECT
    application_id                              AS "Application",
    CAST(fiscal_year AS INTEGER)                AS "Fiscal Year",
    organization_name                           AS "Institution",
    administering_ic                            AS "Administering IC",
    activity_code                               AS "Activity Code",
    printf('%,d', CAST(total_cost AS INTEGER))  AS "Total Cost ($)"
FROM projects
WHERE application_id = '6874256';
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+application_id+AS+%22Application%22%2C+CAST%28fiscal_year+AS+INTEGER%29+AS+%22Fiscal+Year%22%2C+organization_name+AS+%22Institution%22%2C+administering_ic+AS+%22Administering+IC%22%2C+activity_code+AS+%22Activity+Code%22%2C+CAST%28total_cost+AS+INTEGER%29+AS+%22Total+Cost+%28%24%29%22+FROM+projects+WHERE+application_id+%3D+%276874256%27%3B)

Result:

```text
Application   Fiscal Year   Institution                Administering IC   Activity Code   Total Cost ($)
6874256              2005   UNIVERSITY OF LOUISVILLE   NHLBI              T15                    413,364
```

A T15 activity code is an [NIH institutional training grant](https://grants.nih.gov/grants/funding/t-kiosk/index.htm) for continuing education programs. The record is administered by the National Heart, Lung, and Blood Institute (NHLBI) but is co-funded by 18 other Institutes (which is why this particular grant has 19 funder rows in `project_funders`, the schema-phase example). Total cost is $413,364, the same number that the schema phase verifies as the sum of the 19 per-funder splits.

The fourth query previews the analytical shape ahead by showing the top 10 administering Institutes for the full window:

```sql
-- Top ten administering Institutes by project count across the full
-- window. The administering IC is which NIH division "owns" the grant
-- for administrative purposes; co-funded projects appear once here
-- regardless of how many funders are on the project_funders table.
-- This previews the analytical shape phases 03 and 04 work with.
SELECT
    administering_ic         AS "Administering IC",
    printf('%,d', COUNT(*))  AS "Projects"
FROM projects
GROUP BY administering_ic
ORDER BY COUNT(*) DESC
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+administering_ic+AS+%22Administering+IC%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+projects+GROUP+BY+administering_ic+ORDER+BY+COUNT%28*%29+DESC+LIMIT+10%3B)

Result:

```text
Administering IC   Projects
NCI                   1,581
NHLBI                 1,220
NIGMS                 1,184
NINDS                   973
NIA                     963
NIEHS                   920
NCRR                    878
NIDA                    771
NIAID                   752
NIDDK                   607
```

The Cancer Institute (NCI), the Heart, Lung, and Blood Institute (NHLBI), and the General Medical Sciences Institute (NIGMS) lead the count. NCRR (the National Center for Research Resources) shows up in seventh place with 878 projects, almost all of which are from the first decade of the window, since [NCRR was dissolved in December 2011](https://www.nih.gov/news-events/news-releases/nih-establishes-national-center-advancing-translational-sciences) and its functions absorbed into other ICs. Phase 04's cross-IC findings examine that rename in detail.

Each of those query result sets is also the seed of a finding. NIGMS being on this list is the entrance to the IDeA-program story phase 04 develops. NCRR being on this list is the entrance to the rename story phase 04 documents. The source phase is the right place to surface the structural shape; the exploration and findings phases are where the shape becomes claims.

## Reproducing The Export

The search criteria that produced this dataset are encoded in a permanent RePORTER URL that any reader can open to re-run the same search:

`https://reporter.nih.gov/search/EeUf1tz3Akuz5bpcPbIzpg/projects`

The filters that hash represents are: Fiscal Year 2005 through 2025, State Kentucky, Country United States. Clicking the URL takes you to the same search results I exported, with the option to download the same CSV.

The CSV itself is not committed to this repository. The source of truth is NIH, not the portfolio site, and committing a 58-megabyte CSV that anyone can regenerate from the search URL would be a maintenance burden without a benefit. What is committed is the build script that turns the CSV into the SQLite database (covered in [the schema phase](/archivo/kentucky-nih/02-schema/)), the database itself (also covered there, served at `https://pgbd.casa/data/kentucky-nih.sqlite` for direct download), and the case study prose you are reading now.

If RePORTER changes its export format in the future, the seven structural quirks documented above may no longer match. The build script's resolutions assume a specific shape (BOM, six-line preamble, 54-column header with a phantom 55th, dates in `MM/DD/YYYY`, blank/single-space nulls). Anyone re-running the export should re-verify each quirk against the fresh file before trusting the build script's output; a silent format change could load successfully and produce wrong data without obvious error. Treating this case study as living documentation rather than a one-time deliverable is what keeps it reproducible across years rather than just at the moment of publication.

## Looking Ahead

What looked like one row per project turned out not to be. The 305-row gap between the file's 14,181 rows and its 13,876 projects is the doorway into [the schema phase](/archivo/kentucky-nih/02-schema/), where the data model has to decide what a project actually is, where the funding-institute splits live, and how to keep the two perspectives queryable from the same database without one corrupting the other. That is what comes next.
