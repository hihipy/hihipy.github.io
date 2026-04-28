---
title: "expense-report-review-calculator"
weight: 20
description: "A single-sheet Excel calculator that helps financial reviewers spot late-submitted expenses against an institution's reimbursement window. Small in scope, careful in design."
summary: "Flags late expense submissions."
tags: ["excel", "finance", "calculator", "higher-ed"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A small Excel calculator that flags expenses submitted past your institution's reimbursement window, so financial reviewers don't miss them.
{{< /lead >}}

## At a Glance

Most institutions have a written policy about how soon after an expense is incurred it must be submitted for reimbursement. The window is usually somewhere between thirty and ninety days. When an analyst reviewing an expense report has to check forty line items against that policy, they end up doing the same calculation forty times: subtract the policy window from the submission date, compare each expense date against the result, flag anything that falls outside the window.

This calculator is one Excel sheet that does that calculation. Two inputs (the submission date and the institution's window in days), a structured table for line items, and an automatic per-row flag that tells the reviewer whether each expense is within policy and by how many days it misses if it isn't.

## The Problem

The work itself is simple arithmetic. The friction is volume and consistency.

A single expense report can run forty line items. A reviewer handles dozens of reports per cycle. Doing the date math by hand for every line is tedious; doing it in the head is unreliable; doing it in a sticky note next to the screen is ad-hoc. Either the work takes longer than it should, or it takes the right amount of time but the reviewer is not actually checking every line.

The calculator solves this by making the policy check a property of the row itself rather than a separate task. The reviewer enters the submission date once, the policy window once, and then each line they paste into the table either silently passes or surfaces the exact number of days it fails by. There is no "I'll check the dates after I'm done with the totals" mode, because the dates are already checked.

## The Approach

A single Excel worksheet with two inputs at the top, three auto-calculated summary cells below, and a structured table for line items underneath.

The two inputs are the submission date (B1) and the institution's window in days (B2). Both cells are conditionally formatted to show red when empty, which serves as a built-in "fill these first" prompt without needing separate instructions. The three summary cells immediately below those inputs compute the threshold date, the total of all currency amounts, and the count of expenses entered.

The line item table is an Excel Table (`ListObject`) named `Table1`, which means the formulas reference its columns by name (`Table1[Currency Amount]`) rather than by hardcoded range. The table can grow as the user pastes more rows without anything breaking, and the column-name references make the formulas legible: `=SUM(Table1[Currency Amount])` reads exactly the way it sounds.

Each row in the table has a per-row check formula in the last column (E) that returns one of three things depending on the row's state. If required data is missing, it returns instructive text telling the user what to fill in. If the expense is past the policy threshold, it returns the number of days the expense exceeds the window. If the expense is within policy, it returns "N/A". All three states come from a single `IFS` formula per row.

## The Math

The threshold calculation is straightforward subtraction:

`Threshold Date = Submission Date − Institution's Window in Days`

If the submission date is October 15, 2024 and the window is 60 days, the threshold is August 16, 2024. Any expense dated before August 16 is past the window. Any expense dated on or after August 16 is within policy.

The per-row count of days overdue is then:

`Days Overdue = Threshold Date − Expense Date`

Only computed when the expense is past the threshold. For expenses still within policy, the formula returns "N/A" rather than a negative number, because a compliant expense being shown as `-23 days overdue` is more confusing than helpful.

## Why The Defensive Display Matters

A spreadsheet calculator can be technically correct and still useless if its outputs are cryptic when the inputs are incomplete. A blank cell, a `#VALUE!` error, or a nonsense calculation are all worse than the cell saying what to do.

Every output cell in this calculator handles the missing-input case explicitly. The total currency cell shows "Enter Data Starting in Rows 1 & 8" when the table is empty. The expense count cell shows the same. The threshold date cell shows "Enter EXP Submission Date at Row 1 & Institution's Upper Limit of Days After Expense was Paid or Incurred at Row 2" when either input is missing. The per-row flag shows similar guidance.

The instructional text is the same length and style as a real result, so the reviewer's eye lands on the cell, reads the instruction, and moves to the indicated input. No error message, no broken-looking spreadsheet, no separate documentation. The cells themselves are the documentation.

## Under The Hood

For the technically curious, three of the implementation choices that make the calculator work the way it does.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The IFS state machine for per-row status" >}}

The per-row check in column E is a single `IFS` call that handles three distinct states cleanly:

```
=IFS(
    OR(ISBLANK(B10), ISBLANK(C10)),
        "Enter Data in 'Date of Expense' & 'Currency Amount' as Needed",
    B$3 > B10,
        B$3 - B10,
    TRUE,
        "N/A"
)
```

The conditions are evaluated in order, which makes the logic readable as a state machine:

1. **Missing inputs.** If either the date or the amount is blank, the row is incomplete. Return instructional text.
2. **Past threshold.** If the threshold date (`B$3`) is later than the expense date, the expense is overdue. Return the difference in days.
3. **Compliant.** Otherwise (the catch-all `TRUE` branch), return "N/A".

The `B$3` reference uses a row-locked absolute reference (`$3`) but a relative column. This means dragging the formula down the column keeps it pointing to row 3 (where the threshold lives) while letting the row-level inputs (`B10`, `C10`) move with the row.

The first row of the table uses a slightly different version of the formula because the threshold cell itself can be in an error state when the inputs above are missing. The first-row formula adds an `ISERROR(B$3-B9)` check at the front so it returns the right instructional text in that case rather than a confusing intermediate result.

{{< /accordionItem >}}

{{< accordionItem title="The dynamic column header" >}}

The threshold-date row has a label that updates with the user's input. Cell A3 contains:

```
=B2 & " Days Ago Date"
```

When the user enters `60` in B2, the row label reads `60 Days Ago Date`. When they enter `90`, it reads `90 Days Ago Date`. The label always tells the truth about what the cell beside it represents.

This is a small thing that makes a meaningful difference. A static label like "Threshold Date" is correct but generic; a dynamic label that reads "60 Days Ago Date" is correct and *specific to this calculation*. The reviewer reading the sheet can see at a glance what window is in effect without having to look up at B2 to check.

The same pattern applies to the column E header, which references the policy text in its name. As the policy window changes, the column header changes with it, so the per-row flag column always describes itself accurately.

{{< /accordionItem >}}

{{< accordionItem title="Structured table references for resilience" >}}

The summary formulas at the top of the sheet reference the line-item table by column name rather than by hardcoded range:

```
=SUM(Table1[Currency Amount])
=COUNTA(Table1[Date of Expense])
```

`Table1` is an Excel Table (technically a `ListObject`), and `Table1[Currency Amount]` resolves to whatever range that column currently occupies. If the user adds a row to the table, the range automatically expands. If they delete a row, it contracts. The summary formulas never need updating.

This is the modern Excel idiom but it is still surprisingly rare in calculators built for non-developer audiences. The alternative (`=SUM(C9:C55)`) works for exactly the size the spreadsheet was built at, then silently breaks the moment the table grows beyond row 55 because the new rows are not included in the sum. The structured reference avoids that failure mode entirely.

The named-column approach also makes the formulas self-documenting. A reviewer reading `=SUM(Table1[Currency Amount])` understands what is being summed without having to look up what column C contains. A reviewer reading `=SUM(C9:C55)` has to cross-reference.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Format:** Microsoft Excel `.xlsx`
- **Features used:** Excel Tables (`ListObject`), structured references, `IFS` formula, conditional formatting, dynamic text concatenation
- **Compatibility:** Excel 2019 or later (the `IFS` function), or Excel 365

## Repo

[github.com/hihipy/expense-report-review-calculator](https://github.com/hihipy/expense-report-review-calculator)
