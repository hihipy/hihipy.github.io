---
title: "Findings"
weight: 40
description: "Deeper analytical queries using window functions and common table expressions to surface multi-year patterns, institutional rankings, and the funding shifts visible across two decades of NIH research grants awarded in Kentucky."
summary: "Phase 4: Window functions and CTEs"
tags: ["sql", "sqlite", "window-functions", "ctes", "datasette"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Window functions, CTEs, and the patterns that emerge when twenty years of grants get cross-joined by institute.
{{< /lead >}}

## At a Glance

<!-- The setup: the first-pass exploration in phase 03 gave the shape of
the data but stopped at single-dimension cuts. Phase 04 reaches for the
SQL constructs that show how things change across dimensions: window
functions for moving averages and rankings, common table expressions for
multi-step aggregations, and self-joins or anti-joins for "what's
different about this group" questions.

Each finding here is reproducible via the linked Datasette Lite queries. -->

## Smoothing The Annual Series

<!-- The 2009 ARRA spike visually dominates any chart of annual funding
unless it's smoothed. A 5-year centered moving average tells the
underlying trajectory more clearly:

WITH annual AS (
  SELECT p.fiscal_year, SUM(f.total_cost_ic) AS total
  FROM projects p
  JOIN project_funders f USING (application_id)
  GROUP BY p.fiscal_year
)
SELECT
  fiscal_year,
  total,
  ROUND(AVG(total) OVER (
    ORDER BY fiscal_year
    ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
  ), 0) AS moving_avg_5yr
FROM annual
ORDER BY fiscal_year;

The moving average reveals: a slow climb from 2005 to 2010, a plateau
through the 2010s, and a steeper rise from 2018 onward. The 2009 spike
was real but isolated; the longer-term shape is a step up, not a peak. -->

## Institutional Ranking Over Time

<!-- Which UK departments and U of L schools dominate funding, and how that
has changed:

WITH dept_year AS (
  SELECT
    p.organization_name,
    p.department,
    p.fiscal_year,
    SUM(f.total_cost_ic) AS funding
  FROM projects p
  JOIN project_funders f USING (application_id)
  WHERE p.organization_name IN (
    'UNIVERSITY OF KENTUCKY', 'UNIVERSITY OF LOUISVILLE'
  )
  GROUP BY 1, 2, 3
)
SELECT
  department,
  organization_name,
  fiscal_year,
  funding,
  RANK() OVER (
    PARTITION BY fiscal_year
    ORDER BY funding DESC
  ) AS rank_in_year
FROM dept_year
WHERE fiscal_year IN (2005, 2015, 2025)
  AND rank_in_year <= 5
ORDER BY fiscal_year, rank_in_year;

This produces a comparison table showing the top 5 departments at each
school in three benchmark years (early window, mid window, latest
complete year). The shifts are visible: which departments climbed, which
fell, which appeared or disappeared. -->

## Cross-IC Funding Patterns

<!-- Which Institutes and Centers fund the most Kentucky research, and how
that distribution has shifted:

WITH ic_decade AS (
  SELECT
    f.funding_ic,
    CASE
      WHEN p.fiscal_year BETWEEN 2005 AND 2014 THEN '2005-2014'
      WHEN p.fiscal_year BETWEEN 2015 AND 2024 THEN '2015-2024'
    END AS decade,
    SUM(f.total_cost_ic) AS funding
  FROM projects p
  JOIN project_funders f USING (application_id)
  WHERE p.fiscal_year BETWEEN 2005 AND 2024
  GROUP BY 1, 2
)
SELECT
  funding_ic,
  SUM(CASE WHEN decade = '2005-2014' THEN funding END) AS first_decade,
  SUM(CASE WHEN decade = '2015-2024' THEN funding END) AS second_decade,
  ROUND(
    100.0 *
    (SUM(CASE WHEN decade = '2015-2024' THEN funding END) -
     SUM(CASE WHEN decade = '2005-2014' THEN funding END)) /
    SUM(CASE WHEN decade = '2005-2014' THEN funding END),
    0
  ) AS pct_change
FROM ic_decade
GROUP BY funding_ic
ORDER BY second_decade DESC NULLS LAST
LIMIT 15;

This shows the IC mix shift decade-over-decade. The story will likely
involve NIDA and NIA growing (drug abuse research and aging research,
both of which fit Kentucky's demographic profile) and possibly NCRR
appearing in the first decade and disappearing in the second (NCRR was
dissolved in 2011 and folded into NCATS). -->

## What This Doesn't Tell You

<!-- A short, honest section: SQL on grant data tells you about awarded
research dollars and the institutional structure of who receives them.
It doesn't tell you about research outcomes, publication impact,
patient outcomes, or the lived experience of the communities the
research is supposedly serving. The data is administrative, not clinical.

This is the analytical equivalent of the "I'm not a lawyer" disclaimer:
useful framing for a portfolio reader who might otherwise infer more
than the data supports. -->

## Closing

<!-- One paragraph closing the case study: what the four phases together
demonstrate (the full process of an analytical project, from federal
data portal to deeper SQL findings, with each step verifiable). The
schema design from phase 02 turned out to be the load-bearing piece;
without the co-funding invariant verified, every aggregate query in
phases 03 and 04 would have silently double-counted.

Optional final line: invite readers to clone the SQLite, modify the
queries, and follow their own questions. -->
