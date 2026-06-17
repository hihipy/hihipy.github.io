---
title: "Two Years of NCLEX-RN Outcomes at Penobscot College of Nursing"
weight: 30
description: "A SQL case study on two years of NCLEX-RN performance at a multi-campus nursing college, built on the real structure of the institution's data with synthetic outcomes. Three findings emerge: a 26-point campus spread, a cohort decline tracking the national post-NGN trend, and retake conversion reframed as engagement. Walked through phase by phase so every analytical decision is auditable."
summary: "NCLEX-RN, 19 campuses, two years"
tags: ["datasette", "nclex", "nursing-education", "r", "sql", "sqlite"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A SQL case study on two years of NCLEX-RN outcomes across nineteen campuses, walked through phase by phase.
{{< /lead >}}

## At a Glance

This case study takes a 7,635-attempt slice of NCLEX-RN data, every test attempt by every student across 19 campuses of a multi-campus nursing college over eight quarters from 2024SPQ through 2025WIQ, and walks through how to reason about it. Source, schema, exploration, findings: four phases, each short enough to read on its own, together documenting the full process from a flat CSV through to the SQL patterns that surface the interesting answers. The SQLite database produced at the end of phase 02 is queryable directly in the browser via Datasette Lite, so any reader can re-run every query in the case study.

The institution is anonymized and the outcome values are synthetic. The institution name, region names, and one program-code suffix are replaced for privacy, and the pass and fail outcomes are perturbed so that no published rate matches a real reported figure. Every campus, cohort, program, attempt count, and the full retake structure are real, the analytical patterns are preserved, and every number traces to the published database. The methodology is the case study's contribution. The point of the SQL-primary approach is to rebut the assumption that statistical work needs a procedural language: confidence intervals, group comparisons, and counterfactual aggregations are all expressible directly in SQL. R appears only in phase 04, where logistic regression hits the SQL ceiling. The full reasoning, including what the anonymization and perturbation do and do not change, lives in phase 01.

## The Phases
