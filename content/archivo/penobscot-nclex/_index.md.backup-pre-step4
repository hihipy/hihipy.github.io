---
title: "Two Years of NCLEX-RN Outcomes at Penobscot College of Nursing"
weight: 30
description: "A SQL case study on two years of NCLEX-RN performance at a multi-campus nursing college, built on a synthetic dataset derived from a real institution. Three findings emerge: a 21-point campus spread, a cohort decline against the national trend, and retake conversion reframed as engagement. Walked through phase by phase so every analytical decision is auditable."
summary: "NCLEX-RN, 19 campuses, two years"
tags: ["sql", "r", "sqlite", "datasette", "nclex", "nursing-education"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A SQL case study on two years of NCLEX-RN outcomes across nineteen campuses, walked through phase by phase.
{{< /lead >}}

## At a Glance

This case study takes a 7,635-attempt slice of synthetic NCLEX-RN data, every test attempt by every student across 19 campuses of a multi-campus nursing college from winter 2024 through fall 2025, and walks through how to reason about it. Source, schema, exploration, findings: four phases, each short enough to read on its own, together documenting the full process from a flat CSV through to the SQL patterns that surface the interesting answers. The SQLite database produced at the end of phase 02 is queryable directly in the browser via Datasette Lite, so any reader can re-run every query in the case study.

The data is synthetic, derived from a real institutional engagement with every identifier randomized and every outcome value perturbed. The methodology is not. The point of the SQL-primary approach is to rebut the assumption that statistical work needs a procedural language: confidence intervals, group comparisons, and counterfactual aggregations are all expressible directly in SQL. R appears only in phase 04, where logistic regression hits the SQL ceiling. The full reasoning, including why the dataset is synthetic and what that does and does not change, lives in phase 01.

## The Phases
