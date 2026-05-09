---
title: "Source"
weight: 10
description: "How the export came to be, why the search criteria settled on Kentucky from 2005 through 2025, the 15,000-record cap that almost truncated the data silently, and how the file structure had to be parsed before anything could be loaded."
summary: "Phase 1: Where the data came from"
tags: ["sql", "data-sourcing", "nih-reporter"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Where the data came from, why one state across twenty years, and the export limit that shaped the scope.
{{< /lead >}}

## At a Glance

[NIH RePORTER](https://reporter.nih.gov/) is the public-facing search interface that the National Institutes of Health publishes for every research grant it funds. The database goes back decades, contains the full project metadata for each grant (principal investigator, institution, fiscal year, dollar amounts, scientific abstract, research category), and is searchable by anyone with a browser. Federal research funding is a multi-billion-dollar annual public investment, and RePORTER is the closest thing to a complete public ledger of how that money gets allocated.

This case study takes one slice of RePORTER's data: every grant awarded to a Kentucky institution from fiscal year 2005 through 2025. The slice is small enough to load locally and analyze in [SQLite](https://www.sqlite.org/), large enough to support real questions about institutional trends and research priorities, and personal to me because Kentucky is where I grew up.

This phase covers how the export came out of RePORTER and what was already strange about it before any analysis began. The next phase builds a schema on top of it; the two phases after that explore and analyze. Each phase is short enough to read on its own.

## Choosing the Scope

The scope choice has both an honest reason and a defensible reason.

The honest reason: I was born and raised in Kentucky. Of all the states I could have picked for a public-data SQL exercise, this is the one I have a personal stake in. The case study is more interesting to me to write because of that connection, and I think it reads as more honest to acknowledge the motivation than to pretend the choice was purely analytical.

The defensible reasons hold up too. Kentucky is large enough to have substantial NIH activity (the University of Kentucky and the University of Louisville together account for the majority of it) but small enough that twenty years of data fits in a 71-megabyte SQLite file. The Appalachian region has a recognizable research footprint (opioid response, occupational safety, rural health) that gives the categorical distributions a coherent shape rather than a generic one. And none of the data overlaps with my work at the Miller School of Medicine, which keeps this a clean public-data exercise rather than a thinly disguised work project.

The twenty-year window from FY 2005 through FY 2025 captures three things worth seeing in the same dataset: a pre-recession baseline, the 2009 [American Recovery and Reinvestment Act](https://en.wikipedia.org/wiki/American_Recovery_and_Reinvestment_Act_of_2009) stimulus that briefly doubled NIH funding, and the post-pandemic period through the most recent complete fiscal year. Cutting the window shorter would lose one of those; extending it earlier would push past the point where RePORTER's data quality is consistent.

## The Export Limit

NIH RePORTER's CSV export caps at 15,000 records per query. The cap is not surfaced prominently in the export dialog, and the resulting CSV file gives no indication that data has been truncated. A US-wide query across twenty-six years would return well over a million records, and the export would silently deliver only the first 15,000 with no warning, no error, and no metadata distinguishing the truncated file from a complete one.

This is the kind of constraint that shapes a project before any deliberate scope decisions get made. A case study that started "let me look at NIH funding nationally" would have produced a fundamentally broken dataset that looked complete. The Kentucky-twenty-year scope brought the result count to 13,876, comfortably under the cap, with the bonus that any reader who wants to re-run the export can verify that 13,876 is also what they get.

Documenting the limit here is not just trivia. The principle from the case study philosophy applies: the source phase has to make visible the decisions and constraints that shaped what came next. The cap is one of those constraints; it shaped the scope as much as my personal connection to Kentucky did, and the case study is more honest for naming both.

## What's in the File

The export is one CSV file, 58 megabytes, 14,181 rows of data plus a header. Opening it in any text editor reveals seven structural details that the loader has to handle, none of which are documented in the export dialog.

A UTF-8 byte-order mark at the start of the file. The BOM is three bytes (`EF BB BF`) before the first visible character. A naive CSV reader treats those bytes as part of the first column name, producing a header that does not match what subsequent reads expect.

A six-line preamble before the actual header row. The preamble contains the search criteria, the export timestamp, and a blank line. The preamble exists for human readers reviewing the file; it is invisible to RePORTER's own re-import path but breaks every CSV library that assumes line one is the header.

Fifty-four named columns plus a phantom fifty-fifth from a trailing comma on every data row. The trailing comma was almost certainly an unintended consequence of however RePORTER's CSV writer terminates each row, but the result is that every row has one more field than the header declares. A strict parser will refuse the file; a forgiving one will silently invent a column.

Quoted fields containing arbitrary text, including commas and other punctuation. Project titles and abstracts both routinely contain commas, semicolons, and quotation marks. The quoting is correct, but the parser has to be one that actually handles quoted-field semantics rather than splitting blindly on commas.

Blank or single-space strings instead of true SQL null values. Where data is absent, the field is either empty (`""`) or contains exactly one space (`" "`). Both forms appear in the same export. The schema phase has to translate both into proper nulls or any analytical query against the field will return the wrong answer.

Dates in `MM/DD/YYYY` format. Not [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601), not Unix timestamps, not anything that [pandas](https://pandas.pydata.org/) or SQLite parses by default. The schema phase has to convert these explicitly, and the conversion has to be robust to the occasional malformed date that the export produces.

A row count that does not match the project count. The file has 14,181 rows but represents 13,876 distinct projects. The 305-row gap is co-funding splits, where a single project that received money from multiple NIH institutes appears as one row per (Application ID, Funding IC) combination. This is the single most important structural detail for anyone planning to query the data, because every aggregation has to decide whether to count rows or count projects, and the answer is usually different.

Each of these details gets resolved in the schema phase. The point of the source phase is to surface them so the next phase has somewhere to start.

## Reproducing The Export

The search criteria that produced this dataset are encoded in a permanent RePORTER URL that any reader can open to re-run the same search:

[`https://reporter.nih.gov/search/EeUf1tz3Akuz5bpcPbIzpg/projects`](https://reporter.nih.gov/search/EeUf1tz3Akuz5bpcPbIzpg/projects)

The filters that hash represents are: Fiscal Year 2005 through 2025, State Kentucky, Country United States. Clicking the URL takes you to the same search results I exported, with the option to download the same CSV.

The CSV itself is not committed to this repository. The source of truth is NIH, not the portfolio site, and committing a 58-megabyte CSV that anyone can regenerate from the search URL would be a maintenance burden without a benefit. What is committed is the build script that turns the CSV into the SQLite database (covered in the next phase), the database itself (also covered in the next phase, served at [`https://pgbd.casa/data/kentucky-nih.sqlite`](https://pgbd.casa/data/kentucky-nih.sqlite) for direct download), and the case study prose you are reading now.

## Looking Ahead

What looked like one row per project turned out not to be. The 305-row gap between the file's 14,181 rows and its 13,876 projects is the doorway into [the schema phase](/archivo/kentucky-nih/02-schema/), where the data model has to decide what a project actually is, where the funding-institute splits live, and how to keep the two perspectives queryable from the same database without one corrupting the other. That is what comes next.
