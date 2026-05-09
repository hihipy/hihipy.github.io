---
title: "Schema"
weight: 20
description: "Exploratory analysis of a 14,181-row CSV that turned out to describe 13,876 projects, the co-funding split that explained the gap, and the three-table normalized SQLite schema that resulted."
summary: "Phase 2: Schema design from EDA"
tags: ["sql", "sqlite", "schema-design", "python", "sqlite-utils"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
What the data actually looks like once you query it, and the three-table schema that the structure required.
{{< /lead >}}

## At a Glance

<!-- The setup: a 14,181-row CSV, but the search said 13,876 projects. A 305-row
gap that needs explaining before any schema decisions can be made. The phase
walks through the EDA that surfaced the explanation, the verification that
nailed it down, and the three-table normalized schema that came out of it. -->

## The Row vs Project Gap

<!-- Document the discovery:
- pandas.read_csv after skipping the 6-line preamble: 14,181 rows
- df["Application ID"].nunique(): 13,876
- The gap (305 rows) is real and structural, not a duplicate-record bug

What's going on: when an NIH project is co-funded by multiple Institutes and
Centers (ICs), the export gives one row per (Application ID, Funding IC) pair.
Most projects have one funder; some have two or three; one training grant
in 2005 has 19 rows for 19 different ICs. -->

## Verifying The Co-Funding Invariant

<!-- The hypothesis: Total Cost is the same on every funder row of a co-funded
project, and Total Cost IC is the per-funder split. Show the verification
on Application ID 6874256 (the 19-row T15 training grant): SUM(Total Cost IC)
across its 19 rows = $413,364, which equals the Total Cost field on every row.

Generalize: across all 13,876 applications, the number of cases where Total
Cost varied across funder rows = 0. The invariant holds.

This single fact determines the rest of the schema. -->

## The 25 Percent Missing-Cost Pattern

<!-- 3,580 of the 14,181 rows (25.2 percent) have no Funding IC at all. These
also have no Total Cost, no Direct Cost IC, no Indirect Cost IC. Initially
this looks like a data-quality issue; per the NIH ExPORTER FAQ it's actually
by design: cost data is only published for projects funded by NIH, CDC, FDA,
and ACF. Other partners (NASA, USDA, VA cooperative) report grants without
dollar amounts.

So these rows go into the projects table (the project exists) but not the
funders table (no funding IC to record). -->

## The Multi-Valued Category Field

<!-- NIH Spending Categorization is a semicolon-delimited string. Some projects
have one category, some have ten. "No NIH Category available" appears as
a literal value 4,871 times and is meaningful (the project predates RCDC
categorization, or hasn't been categorized yet), so it's kept rather than
filtered.

This wants to be its own table with an Application ID foreign key and one
row per category-tag pair, so SQL queries can JOIN on it cleanly. -->

## The Three-Table Schema

<!-- Document the design decision:

projects (1 row per Application ID): all the project-level fields, including
Total Cost rolled up via DISTINCT (since it's identical across funder rows).
13,876 rows.

project_funders (1 row per (Application ID, Funding IC)): the funding split.
10,601 rows, after dropping the 3,580 rows with no Funding IC.

project_categories (1 row per (Application ID, Category)): exploded from the
semicolon-delimited string. 56,845 rows, averaging about four categories
per project.

Indexes on the heavy filter columns: fiscal year, organization name,
administering IC, activity code, contact PI person ID, and the multi-valued
category column. -->

## The Build Script

<!-- Brief description of build_kentucky_nih.py: pandas to load, sqlite-utils
to write, with explicit cleaning for blank-vs-null and date parsing.
Documented decisions (the eight numbered ones at the top of the script)
make every choice traceable.

Output: kentucky_nih.sqlite, 71 MB. Verified against the source CSV with
foreign-key checks and a sum-equals-total spot-check on the 19-row example.

Link to the script in the GitHub repo:
https://github.com/hihipy/hihipy.github.io/blob/main/tools/build_kentucky_nih.py -->

## Looking Ahead

<!-- Bridge to phase 03: the database is queryable now, in the browser, via
Datasette Lite. The next phase is the first-pass exploration. -->
