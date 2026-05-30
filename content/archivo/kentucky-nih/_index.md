---
title: "Two Decades of NIH Funding in Kentucky"
weight: 20
description: "A SQL case study on twenty-one years of NIH grants in Kentucky: the 2009 ARRA stimulus that briefly doubled federal funding, the two universities that absorbed 87 percent of it, and the IDeA-program shift that drove the second decade's growth. Walked through phase by phase so every decision is auditable."
summary: "Twenty-one years, two universities, one stimulus"
tags: ["datasette", "kentucky", "nih-reporter", "sql", "sqlite"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A SQL case study on twenty years of NIH grant funding in Kentucky, walked through phase by phase.
{{< /lead >}}

## At a Glance

This case study takes a 13,876-project slice of [NIH RePORTER](https://reporter.nih.gov/), every research grant awarded to a Kentucky institution from fiscal year 2005 through 2025, and walks through how to reason about it. Source, schema, exploration, findings: four phases, each short enough to read on its own, together documenting the full process from a blank query on a federal data portal through to the SQL patterns that surface the interesting answers. The SQLite database produced at the end of phase 02 is queryable directly in the browser via Datasette Lite, so any reader can re-run every query in the case study.

I picked Kentucky because I was born and raised there. The full reasoning, including why this state is well-suited to a single-file SQLite exercise and the export limit that shaped the scope, lives in phase 01.

## The Phases
