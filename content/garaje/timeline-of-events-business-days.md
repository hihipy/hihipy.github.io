---
title: "timeline-of-events-business-days"
weight: 50
description: "A small Excel timeline tool that measures every phase of a process in business days, including the gaps between phases. Built for spotting where time actually goes in a multi-step workflow."
summary: "Process timeline with gap detection."
tags: ["excel", "process-improvement", "calculator", "higher-ed"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
An Excel timeline that measures every step of a multi-stage process, including the time spent waiting between steps.
{{< /lead >}}

## At a Glance

When a multi-step process takes too long, the question is rarely "did each step take too long?" It is usually "where did the time go between steps?" A grant submission that took eight weeks is sometimes eight weeks of work, but more often four weeks of work and four weeks of waiting between phases for sign-offs, document handoffs, or a person to come back from leave.

This is a single-sheet Excel tool that surfaces both numbers separately. The user enters the phases of a process with their start and end dates, and the sheet computes three things per phase: the business days the phase itself took, the business days that elapsed between the previous phase ending and this phase starting, and the cumulative business days since the process began. The gap column is the point of the tool.

## The Problem

Calendar days lie about how processes actually work. A phase that takes "five days" but spans a weekend really took three working days. A phase that takes "ten days" but includes a federal holiday and the day before Thanksgiving took maybe six working days. Counting in calendar days makes every measurement systematically too long, in ways that vary unpredictably with which week the work happened to land in.

Business days fix this. Excel's `NETWORKDAYS` function counts the weekdays between two dates, automatically excluding Saturdays and Sundays. The result is a measurement of the actual working time available rather than the elapsed wall-clock time.

But just measuring each phase's duration in business days is only half the answer. The other half is the time *between* phases. A process with five phases each taking three business days could finish in fifteen business days, or in thirty, depending on whether each phase starts the next business day after the previous phase ended or whether each handoff sits for a few days before the next person picks it up. The total wall-clock time depends on both numbers, but the optimization opportunities are usually in the gaps, not the phases themselves.

The tool computes both: phase duration and inter-phase gap, side by side, on every row.

## What's In The Sheet

A single Excel Table (`Table1`) with eight columns:

| Column | Contents | Source |
|---|---|---|
| A | Action Item Phase | User enters |
| B | Start Date | User enters |
| C | End Date | User enters |
| D | Period | Auto: pretty-printed date range |
| E | Business Days Needed to Complete Action Item | Auto: `NETWORKDAYS(B, C)` |
| F | Business Days Between Previous Phase End and This Phase Start | Auto: `NETWORKDAYS(C of previous row, B)` |
| G | Business Days Since Initiation | Auto: `NETWORKDAYS(C$2, C)` |
| H | Further Details | User enters (optional) |

The user fills in three columns (A, B, C) and gets four computed columns (D, E, F, G). H is a free-form notes field.

The three computed metrics tell different stories. Column E shows how long each phase took in pure business days. Column F shows how long the handoff between each pair of adjacent phases took. Column G is the running total of business days since the process began, useful for benchmarking against an SLA or a target completion window.

## The Three Formulas That Matter

The whole tool is three formulas applied across the table.

**Phase duration** — business days within a single phase, inclusive of both start and end dates:

```excel
=NETWORKDAYS(B2, C2,)
```

The trailing comma is a placeholder for the optional `holidays` argument, which is left empty by default. Users who want to exclude specific holidays from the count can supply a range of holiday dates as the third argument; without it, the function only excludes weekends.

**Inter-phase gap** — business days between the previous phase ending and the current phase starting:

```excel
=IFERROR(NETWORKDAYS(C1, B2,), "Please fill in Start Date and End Date Rows")
```

The `C1` reference is the relative reference to the previous row's End Date. As the formula is dragged down the column, it always points one row up. Row 2's gap formula uses `C1` (which is the header row, producing zero); row 3 uses `C2`; row 4 uses `C3`; and so on. The first phase's gap is therefore meaningless, and the user is expected to ignore it. The `IFERROR` wrapper catches the case where the previous phase has no end date yet, returning a friendly instruction instead of a `#VALUE!` error.

**Cumulative time** — business days from the very first phase's end date to the current phase's end date:

```excel
=NETWORKDAYS(C$2, C2,)
```

The `C$2` reference is locked to row 2 (the first phase's end date) using the `$` prefix on the row number. As the formula is dragged down the column, the second argument increments through `C3`, `C4`, etc., but the first argument stays fixed at `C$2`. The result is a running count of business days since the process began, computed on every row. The locked reference is what makes this work: without it, the formula would give the wrong answer in every row except the first.

## Why The Gap Column Is The Point

The phase-duration column (E) is what most people would build if asked to make a process timeline tracker. It tells you how long each phase took. It is necessary but not sufficient.

The gap column (F) is what makes the tool useful for actually finding bottlenecks. A timeline where every phase took its expected duration but the overall process still ran long is a timeline where the gap column has the answer. Maybe Phase 2 ended on a Friday and Phase 3 didn't start until the following Wednesday — three business days lost waiting for someone to pick up the work. Maybe Phase 5 finished a week before Phase 6 began because Phase 6's owner was on PTO. Without the gap column, those delays are invisible. The user sees an eight-week process and a sequence of two-week phases and concludes nothing is wrong.

The cumulative column (G) ties the analysis to a wall-clock perspective. If the process has a target completion date, comparing G against the target tells the user whether the process is currently on track. If the process has historical baselines, G makes period-over-period comparison straightforward.

## Stack

- **Format:** Microsoft Excel `.xlsx`
- **Features used:** Excel Table (`ListObject`), `NETWORKDAYS` for business-day arithmetic, `IFERROR` for graceful empty-cell handling, `TEXT` for formatted date display
- **Compatibility:** Excel 2016 or later (or Excel 365)

## Repo

[github.com/hihipy/timeline-of-events-business-days](https://github.com/hihipy/timeline-of-events-business-days)
