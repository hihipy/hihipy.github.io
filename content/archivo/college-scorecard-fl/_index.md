---
title: "Florida Four-Year Institutions"
weight: 10
description: "A SQL case study on outcomes, costs, and the for-profit closure wave at Florida four-year institutions, 2014-2023. College Scorecard data normalized into a queryable database, walked through phase by phase so every analytical decision is auditable."
summary: "Outcomes, costs, and a closure wave"
tags: ["sql", "datasette", "sqlite", "higher-education", "case-study"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A SQL case study on a decade of outcomes data for Florida four-year institutions, walked through phase by phase.
{{< /lead >}}

## At a Glance

This case study takes a 112-institution slice of College Scorecard, every four-year institution awarding predominantly bachelor's or graduate degrees in Florida from cohort year 2014-15 through 2023-24, and walks through how to reason about it. Source, schema, exploration, findings: four phases, each short enough to read on its own, together documenting the full process from a federal data download through to the SQL patterns that surface the interesting answers. The SQLite database produced at the end of phase 02 is queryable directly in the browser via Datasette Lite, so any reader can re-run every query in the case study.

The case study covers public institutions (the State University System), private nonprofit institutions, and for-profit institutions across the same decade. The for-profit closure wave (more than half the for-profit four-year institutions present in 2014 had vanished by 2020) is one of the central analytical threads. The full reasoning, including why this scope, lives in phase 01.

## The Phases
