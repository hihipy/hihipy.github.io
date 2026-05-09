---
title: "Exploration"
weight: 30
description: "First-pass queries against the database to see what twenty years of NIH funding in Kentucky actually looks like, including yearly trends, the institutional concentration, and the ARRA stimulus visible in the 2009 data."
summary: "Phase 3: First-pass queries"
tags: ["sql", "sqlite", "exploratory-analysis", "datasette"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
First-pass queries to see what the data says, and the questions worth following further.
{{< /lead >}}

## At a Glance

<!-- The setup: with the schema in place, the first analytical move is the
"breadth before depth" pass. Run a handful of queries that cover the obvious
dimensions (time, organization, category, funding mechanism) before reaching
for window functions or CTEs. See what the data says at a glance, then
decide which questions are worth following further in phase 04.

Each query in this phase is linked into Datasette Lite so the reader can
re-run it directly in the browser. -->

## Funding By Year

<!-- The first query, and the one that anchors most of the later analysis:

SELECT p.fiscal_year, ROUND(SUM(f.total_cost_ic) / 1e6, 1) AS millions
FROM projects p
JOIN project_funders f USING (application_id)
GROUP BY p.fiscal_year
ORDER BY fiscal_year;

Note the use of SUM(total_cost_ic) rather than SUM(total_cost), per the
co-funding invariant from phase 02. Show the 21-row result. The shape
ranges from a low around $190M (2014) to peaks above $260M (2020-2021).
2009 sticks out as expected. 2025 is partial because the year hasn't ended.

[Link into Datasette Lite with this query pre-loaded.] -->

## Top Institutions

<!-- The second obvious cut: who actually does this research?

SELECT organization_name, COUNT(*) AS projects
FROM projects
GROUP BY organization_name
ORDER BY projects DESC
LIMIT 10;

Result: University of Kentucky and University of Louisville together
account for 87 percent of all rows. The long tail includes the state
public-health cabinet, two VA medical centers, and a handful of small
biotech firms (PGXL Technologies, Naprogenix, Tru Diagnostics, Enepret).

This is a Kentucky-specific finding: a state-level NIH portrait is
substantially the portrait of two large research universities.

[Link into Datasette Lite.] -->

## NIH Spending Categories

<!-- The category breakdown across the entire 21-year window:

SELECT c.category, COUNT(*) AS projects
FROM project_categories c
WHERE c.category != 'No NIH Category available'
GROUP BY c.category
ORDER BY projects DESC
LIMIT 10;

Top categories: Clinical Research, Neurosciences, Prevention, Cancer,
Genetics, Brain Disorders, Behavioral Science, Biotechnology, Aging.
This is a recognizably general-research portrait.

What's NOT in the top ten that we'd expect to see for Kentucky: Tobacco
(despite the agricultural history), Substance Abuse, and Rural Health.
These show up further down the list. -->

## The ARRA Spike

<!-- A specific finding the year-by-year query revealed: 2009 has 911 grants
versus the typical ~640 per year. The American Recovery and Reinvestment
Act was signed in February 2009 and included $10.4 billion in NIH funding
through the Recovery Act mechanism, distributed largely as one-year and
two-year supplements to existing grants.

Query showing the spike, with NIH activity codes added to confirm the
mechanism mix:

SELECT activity_code, COUNT(*) AS grants
FROM projects
WHERE fiscal_year = 2009
GROUP BY activity_code
ORDER BY grants DESC
LIMIT 10;

The R01 base mechanism dominates as expected, but several activity codes
(R03, R21, R56, ARRA-specific supplements) are unusually frequent that
year, consistent with ARRA's pattern of supplementing rather than
displacing the regular grant cycle. -->

## What's Worth Following Further

<!-- One paragraph wrapping up: the first-pass queries give the shape of
the data, but they don't yet cross dimensions. The interesting questions
mostly live at intersections: "How has funding shifted across ICs over
time at UK?", "Which categories are growing or shrinking decade over
decade?", "What's the moving average of annual funding once the 2009
spike is smoothed?". Phase 04 reaches for window functions and CTEs
to answer those. -->
