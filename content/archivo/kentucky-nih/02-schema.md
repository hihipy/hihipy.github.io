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

The previous phase ended on an open question: the CSV has 14,181 rows but the search results page said 13,876 projects. The 305-row gap is real and structural, not a duplicate-record bug, and the schema can not be designed until the gap is explained.

This phase walks through the [exploratory data analysis](https://en.wikipedia.org/wiki/Exploratory_data_analysis) that surfaced the explanation (NIH co-funding splits, where one project funded by multiple Institutes appears as one row per Institute), the verification query that proved the explanation held across all 13,876 projects without a single counterexample, and the three-table normalized schema the explanation forced. The result is a 75-megabyte SQLite database with the entire structure of NIH funding to Kentucky encoded in three tables connected by foreign keys, ready to query.

The schema phase is exactly the kind of work the [case study philosophy](/biblioteca/) says should be visible rather than hidden. Most published analytical writing presents a normalized dataset as if the structure were obvious or inevitable. It almost never is. The decisions in this phase (one project per row, drop the no-funder rows from the funders table, explode the multi-valued category column into its own table) are choices, and a reviewer can only audit the work if the choices are documented alongside their rationale.

## The Row vs Project Gap

The first thing any schema decision needs is an honest count of what is in the file. After skipping the six-line preamble identified in [the source phase](/archivo/kentucky-nih/01-source/), the file loads cleanly:

```python
# Load the RePORTER export and count what is actually in the file.
# skiprows=6 handles the six-line preamble identified in phase 01;
# encoding="utf-8-sig" strips the BOM so the leading column name is clean.
import pandas as pd

df = pd.read_csv(
    "kentucky-nih-2005-2025.csv",
    skiprows=6,
    encoding="utf-8-sig",
)

# Two ways to count what is in the file. The two should match for a
# well-shaped export. They do not match here, which is the structural
# surprise this phase exists to explain.
len(df)                              # 14,181
df["Application ID"].nunique()       # 13,876
```

Two different numbers for what should be the same thing. The 305-row gap is exactly the kind of structural surprise that the source phase exists to surface, and it has to be explained before any schema work begins. A duplicate-record bug would warrant cleaning. A real structural pattern warrants modeling.

NIH grants are sometimes co-funded by multiple [Institutes and Centers](https://www.nih.gov/institutes-nih/list-nih-institutes-centers-offices), the operating divisions that make up NIH (the National Cancer Institute, the National Institute on Aging, and so on, twenty-seven in total). When a project is co-funded, the RePORTER export gives one row per (Application ID, Funding IC) pair. Of the 13,876 distinct projects in the dataset, 3,580 have no funder rows at all (the missing-cost pattern documented later in this phase). The remaining 10,296 projects have at least one funder row. Most of those have exactly one funder, but a small minority are co-funded by two or more.

One project, [Application ID 6874256](https://reporter.nih.gov/search/EeUf1tz3Akuz5bpcPbIzpg/projects), an institutional training grant from fiscal year 2005, has nineteen rows for nineteen different ICs. It is the most extreme co-funding case in the dataset.

The funder-count distribution after the database is built confirms the pattern:

```sql
-- How many funders does each project have? The CTE counts rows per
-- application_id in project_funders; the outer query counts how often
-- each row-count appears across the 10,296 projects with at least
-- one funder row. The result is a histogram of co-funder counts.
WITH funder_counts AS (
    SELECT
        application_id,
        COUNT(*) AS n_funders
    FROM project_funders
    GROUP BY application_id
)
SELECT
    n_funders   AS "Funders",
    COUNT(*)    AS "Projects"
FROM funder_counts
GROUP BY n_funders
ORDER BY n_funders;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=WITH+funder_counts+AS+%28SELECT+application_id%2C+COUNT%28*%29+AS+n_funders+FROM+project_funders+GROUP+BY+application_id%29+SELECT+n_funders+AS+%22Funders%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+funder_counts+GROUP+BY+n_funders+ORDER+BY+n_funders%3B)

Result:

```text
Funders   Projects
1           10,065
2              209
3               11
4                4
5                1
6                2
11               3
19               1
```

The distribution reconciles cleanly. 10,065 single-funder projects + 209 + 11 + 4 + 1 + 2 + 3 + 1 = 10,296 distinct projects with at least one funder. Those 10,296 projects produce 10,601 total funder rows in the table (the math: 10,065 × 1 + 209 × 2 + 11 × 3 + 4 × 4 + 1 × 5 + 2 × 6 + 3 × 11 + 1 × 19 = 10,601). The 305-row excess of funder-rows over funder-applications is the gap explained: it is the sum of co-funding splits across the 231 multi-funder projects.

The 305 number from the source phase shows up here twice: once as the row gap in the original CSV (14,181 rows minus 13,876 projects), and again as the gap between funder rows and funder applications in the database (10,601 minus 10,296). They are the same gap measured at two different levels of the data. The 3,580 projects with no funder rows are a separate phenomenon, examined below.

## Verifying The Co-Funding Invariant

If the multi-funder rows are co-funding splits rather than independent records, then a specific invariant has to hold: the project-level `Total Cost` field has to be identical across every funder row of the same project, and the per-funder `Total Cost IC` field should sum to that same total. The schema can not be normalized along these lines unless the invariant is verified empirically, not just assumed.

The nineteen-row training grant is the natural test case because it has the most opportunities to fail. The check across its rows:

```python
# Verify the co-funding invariant on the 19-row training grant. Three
# checks: (1) the project-level total is identical across all 19 rows,
# (2) read that total once, (3) the per-funder slices sum back to it.
# If any check fails, the splits are not splits and the schema cannot
# be normalized along these lines.
grant = df[df["Application ID"] == 6874256]

grant["Total Cost"].nunique()                # 1 (every row reports the same total)
grant["Total Cost"].iloc[0]                  # 413364.0
grant["Total Cost IC"].sum()                 # 413364.0
```

Same value across all nineteen rows, and the per-IC slices sum back to that value. The invariant holds for this case.

The same verification can be run against the database after it is built, which confirms the invariant survives the load:

```sql
-- Verify the invariant in the database. The total_cost field on the
-- projects table for application 6874256 must equal the sum of
-- total_cost_ic across its rows in project_funders. CAST converts
-- the float-stored dollar amounts to integers for clean display.
SELECT
    p.application_id                       AS "Application",
    CAST(p.total_cost AS INTEGER)          AS "Project Total Cost ($)",
    (SELECT CAST(SUM(total_cost_ic) AS INTEGER)
     FROM project_funders
     WHERE application_id = p.application_id) AS "Sum of IC Splits ($)"
FROM projects p
WHERE p.application_id = '6874256';
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+p.application_id+AS+%22Application%22%2C+CAST%28p.total_cost+AS+INTEGER%29+AS+%22Project+Total+Cost+%28%24%29%22%2C+%28SELECT+CAST%28SUM%28total_cost_ic%29+AS+INTEGER%29+FROM+project_funders+WHERE+application_id+%3D+p.application_id%29+AS+%22Sum+of+IC+Splits+%28%24%29%22+FROM+projects+p+WHERE+p.application_id+%3D+%276874256%27%3B)

Result:

```text
Application   Project Total Cost ($)   Sum of IC Splits ($)
6874256                      413,364                413,364
```

Both values match. The co-funding invariant survived the CSV load and the schema normalization, and the database is internally consistent on this point.

Generalizing to the full dataset, the original verification was a pandas query against the source CSV:

```python
# Generalize the invariant check to all 13,876 applications. For each
# Application ID, count the number of distinct Total Cost values; the
# invariant says that count is exactly 1 for every application. Any
# application with more than one distinct total is a violation.
violations = (
    df.groupby("Application ID")["Total Cost"]
      .nunique()
      .reset_index(name="distinct_totals")
      .query("distinct_totals > 1")
)

# Zero violations means the invariant holds without exception, and the
# schema can deduplicate project-level fields without information loss.
len(violations)                              # 0
```

Across all 13,876 applications, the number of cases where `Total Cost` varies across funder rows is exactly zero. The invariant holds without exception. This single fact determines the rest of the schema: project-level fields can be deduplicated to one row per Application ID without any information loss, and the per-funder split can be promoted into its own table linked by foreign key. The schema is now writeable.

This is the [reproducibility-is-the-floor, review-is-the-ceiling](/biblioteca/#reproducibility-is-the-floor-review-is-the-ceiling) principle in concrete form. The query above is reproducibility: anyone can re-run it against the same data and get the same answer. But the question of whether to *run* the query in the first place, rather than just assuming the invariant on the basis of a plausible explanation, is what review catches. A reviewer would ask "did you actually check that the invariant holds, or did you assume it from the explanation?" and the only good answer is to run the check before they ask.

## The 25 Percent Missing-Cost Pattern

A second structural surprise emerges immediately after the first: 3,580 of the 13,876 projects (25.8 percent) have no Funding IC data at all, which means no Total Cost, no Direct Cost IC, and no Indirect Cost IC. Every cost-related field is null on roughly a quarter of projects.

The check at the project level, against the database:

```sql
-- Count projects with no funder rows. A project with no entry in
-- project_funders is a project NIH RePORTER lists but does not
-- disclose cost data for. The expected count from the source CSV
-- analysis is 3,580.
SELECT
    COUNT(*)  AS "Projects Without Funder Data"
FROM projects p
WHERE NOT EXISTS (
    SELECT 1
    FROM project_funders f
    WHERE f.application_id = p.application_id
);
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=SELECT+COUNT%28*%29+AS+%22Projects+Without+Funder+Data%22+FROM+projects+p+WHERE+NOT+EXISTS+%28SELECT+1+FROM+project_funders+f+WHERE+f.application_id+%3D+p.application_id%29%3B)

Result:

```text
Projects Without Funder Data
3,580
```

Initially this looks like a data-quality issue. It is not. The [NIH ExPORTER FAQ](https://reporter.nih.gov/exporter/faq) documents the pattern as policy: cost data is published only for projects funded by NIH, CDC, FDA, and ACF. Projects funded by other federal partners (NASA, USDA, the VA cooperative program, and others) appear in RePORTER's project listings with full metadata but no dollar amounts, because those partners do not authorize NIH to disclose their funding figures.

Without knowing this, an analyst querying for "average funding per project in Kentucky" gets a wildly wrong answer. Either they include the 3,580 rows with null costs and the average is artificially deflated, or they exclude those rows and accidentally exclude a quarter of the actual project portfolio. Both options corrupt the analysis.

The schema implication is clean: these rows go into the `projects` table (the project exists, the metadata is real) but not into the `project_funders` table (there is no Funding IC to record). Any query that asks about funding totals naturally joins through `project_funders`, which automatically excludes the 3,580 zero-disclosure projects. Any query that asks about project counts or research patterns goes against `projects` directly and gets the full picture.

## The Multi-Valued Category Field

The third structural surprise is in the `NIH Spending Categorization` column. It looks like a single text field at first glance, but inspecting actual values reveals semicolon-delimited multi-valued content. Some projects have a single category. Some have many. The exploded `project_categories` table makes the distribution easy to inspect:

```sql
-- Categories per project: how many distinct category tags does each
-- project carry, and what is the spread of category counts across the
-- 13,876 projects in the dataset? The CTE counts rows per project in
-- project_categories; the outer query summarizes the spread.
WITH cat_counts AS (
    SELECT
        application_id,
        COUNT(*) AS n_cats
    FROM project_categories
    GROUP BY application_id
)
SELECT
    ROUND(AVG(n_cats), 1)  AS "Avg Categories",
    MIN(n_cats)            AS "Min",
    MAX(n_cats)            AS "Max",
    COUNT(*)               AS "Projects"
FROM cat_counts;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite#/kentucky-nih?sql=WITH+cat_counts+AS+%28SELECT+application_id%2C+COUNT%28*%29+AS+n_cats+FROM+project_categories+GROUP+BY+application_id%29+SELECT+ROUND%28AVG%28n_cats%29%2C+1%29+AS+%22Avg+Categories%22%2C+MIN%28n_cats%29+AS+%22Min%22%2C+MAX%28n_cats%29+AS+%22Max%22%2C+COUNT%28*%29+AS+%22Projects%22+FROM+cat_counts%3B)

Result:

```text
Avg Categories   Min   Max   Projects
4.1                1    28     13,876
```

Average four categories per project, ranging from one (the minimum: every project has at least one category, even if that category is the literal string "No NIH Category available") to twenty-eight (the maximum: a single project carries 28 distinct category tags). The exploded table has 56,845 rows total across all 13,876 projects, which checks out: 13,876 × 4.1 = 56,892, close to the 56,845 actual count given the rounding in the average.

The literal string `"No NIH Category available"` appears as a category value 4,764 times. It is itself meaningful (the project predates [Research, Condition, and Disease Categorization](https://report.nih.gov/funding/categorical-spending) or has not yet been categorized), so it is kept as a real category rather than filtered out. Phase 03's exploration query filters it out only when ranking the most frequent categories, since the placeholder otherwise crowds the top of the list.

A multi-valued column in a relational database is a denormalization waiting to be undone. Querying "all projects in the Cancer category" against the raw column would require a substring match (`LIKE '%Cancer%'`) that is slow, fragile (the substring "Cancer" matches "Cancer" but also any other category that happens to contain those letters), and prevents the database from using an index on the category. The standard fix is to explode the multi-valued field into its own table with one row per (project, category) pair.

The exploded `project_categories` table supports clean indexed joins. Asking "all Cancer projects" becomes a one-line `WHERE category = 'Cancer'` against an indexed column.

## The Three-Table Schema

The three structural facts above (the row-vs-project gap, the missing-cost pattern, and the multi-valued category field) point directly to a three-table schema. Each table has one job and one grain.

{{< mermaid >}}
erDiagram
    projects ||--o{ project_funders : "co-funded by"
    projects ||--o{ project_categories : "tagged with"
    projects {
        text application_id PK
        text project_number
        text project_title
        real fiscal_year
        text organization_name
        text administering_ic
        text activity_code
        text contact_pi_person_id
        text contact_pi
        real total_cost
        text project_start_date
        text project_end_date
    }
    project_funders {
        integer application_id FK
        text funding_ic
        real total_cost_ic
        real direct_cost_ic
        real indirect_cost_ic
    }
    project_categories {
        integer application_id FK
        text category
    }
{{< /mermaid >}}

`projects` holds one row per Application ID, 13,876 rows total. All the project-level fields live here: title, fiscal year, organization, administering Institute, activity code, principal investigator, total cost, dates. The `total_cost` value is taken from the deduplicated funder rows since the verification query established it is identical across all of them.

`project_funders` holds one row per (Application ID, Funding IC) pair, 10,601 rows total. The 3,580 projects with no Funding IC are absent from this table because there is no funder to record. Each row carries the per-funder split (`total_cost_ic`, `direct_cost_ic`, `indirect_cost_ic`). Joining `projects` to `project_funders` on `application_id` produces every funder of every project; the absence of a row means the project's funding source is not in the NIH-disclosure family.

`project_categories` holds one row per (Application ID, Category) pair, 56,845 rows total. The exploded form of the semicolon-delimited categorization string. Indexed on `category` so any "show me everything in category X" query is fast.

A note worth being explicit about: the schema diagram shows a foreign-key type mismatch. `application_id` is `TEXT` in the `projects` table (because RePORTER's Application IDs are sometimes alphanumeric), but the foreign-key columns in `project_funders` and `project_categories` were declared as `INTEGER` by sqlite-utils when the build script wrote those tables. SQLite itself does not enforce strict type matching on foreign-key constraints (it is a [dynamic-typed engine](https://www.sqlite.org/datatype3.html)), so joins still work and the data is consistent in practice. But a strictly-typed database engine would reject this schema, and any future migration to PostgreSQL or similar would need to align the types. The build script at `tools/build_kentucky_nih.py` is the place to fix this; left as-is for now because every join in the case study works correctly.

Indexes on the columns that show up in WHERE clauses across the exploration phase: `fiscal_year`, `organization_name`, `administering_ic`, `activity_code`, `contact_pi_person_id` on `projects` (plus a compound index on `fiscal_year, organization_name` for the year-by-institution queries in phase 04); `funding_ic` on `project_funders`; `category` on `project_categories`. Without these, the exploration queries in the next phase would table-scan 56,845 rows on every category lookup.

## The Build Script

The schema is encoded as a Python script that turns the source CSV into the SQLite database. [pandas](https://pandas.pydata.org/) handles the load and the cleaning; [sqlite-utils](https://sqlite-utils.datasette.io/) handles the write, schema creation, and indexing. The script lives at [`tools/build_kentucky_nih.py`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/build_kentucky_nih.py) in the portfolio repository, runnable by anyone who downloads the source CSV from RePORTER and points the script at it.

The script's docstring documents eight decisions that determined the implementation, each one tied to a fact established earlier in this phase:

1. Skip the six-line preamble before reading the CSV (source-phase finding)
2. Decode as UTF-8 with BOM handling so the byte-order mark does not contaminate the first column name (source-phase finding)
3. Drop the phantom fifty-fifth column from the trailing-comma artifact (source-phase finding)
4. Coerce blank strings and single-space strings to proper SQL nulls (source-phase finding)
5. Parse `MM/DD/YYYY` dates explicitly into ISO 8601 (source-phase finding)
6. Deduplicate project-level fields on Application ID, since the co-funding invariant guarantees no information loss (this phase)
7. Drop the 3,580 zero-disclosure rows from `project_funders` only, keeping them in `projects` (this phase)
8. Explode the semicolon-delimited categorization string into one row per category (this phase)

Each decision is a comment in the source. The point is not that the decisions are clever; it is that they are recorded in the place a future reviewer (or future me) will look first, with enough context to evaluate whether the choice still makes sense. This is the [verbose-comments-for-audit](/biblioteca/#documentation-as-part-of-the-work) principle from the case study philosophy applied to a build artifact rather than to inline analytical code: the same density of "why this, why not the alternative" that a one-off script benefits from, but at the level of the structural decisions that produced the data the rest of the case study queries against.

The output is a 75-megabyte SQLite database with three tables, six indexes, and verifiable counts: 13,876 rows in `projects`, 10,601 rows in `project_funders`, 56,845 rows in `project_categories`. The sum-equals-total spot check on the nineteen-row training grant continues to hold post-build. The database is committed at `static/data/kentucky-nih.sqlite` and served at [`https://pgbd.casa/data/kentucky-nih.sqlite`](https://pgbd.casa/data/kentucky-nih.sqlite) for direct download.

## Looking Ahead

The database exists, the schema is documented, and the data invariants are verified. Anyone reading this page can open the database in [Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/kentucky-nih.sqlite) directly in the browser and run SQL against it without installing anything. The next phase, [exploration](/archivo/kentucky-nih/03-exploration/), is the first-pass orientation: how much funding flowed in each year, which institutions dominated, which categories show up most, where the surprises live.
