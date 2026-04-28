---
title: "excel-vba-toolkit"
weight: 10
description: "A collection of ten Excel VBA macros covering data cleaning, structured exports, and analyst utilities. Plain .bas modules that import into any workbook in under a minute, with engineering patterns that hold up against modern expectations."
summary: "Reusable Excel VBA macros."
tags: ["vba", "excel", "data-cleaning", "documentation", "macros"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A library of ten ready-to-use Excel macros for the cleaning, exporting, and documentation tasks analysts do every week.
{{< /lead >}}

## At a Glance

VBA is unfashionable. It also runs in nearly every office in the world, because Excel runs in nearly every office in the world, and VBA is the language that lets analysts automate Excel without leaving Excel. Anyone who works with spreadsheets at scale eventually hits the same wall: a task that takes one minute by hand takes thirty seconds in VBA, and you do it five hundred times a year.

This toolkit is ten of those tasks, written carefully, organized by category, distributed as plain `.bas` text files that import into any workbook through the VBA editor's Import dialog. Each macro is documented with a header block describing what it does, what it expects, and what it returns. The collective focus is on the unglamorous middle layer of analyst work: cleaning, documenting, and extracting from spreadsheets that other people built.

## Why a Toolkit Rather Than One Big Macro

Most Excel automation guidance pushes toward monolithic workbooks: a single `.xlsm` file that contains all the macros for a specific workflow. That works for one analyst on one project. It does not work for a team that needs the same operations across many different workbooks.

The `.bas` module approach inverts the model. Each macro lives in a plain text file. Importing one into a new workbook takes about thirty seconds through the VBA editor's `File → Import File...` dialog. The macros are designed to operate on whatever workbook they are imported into, not a specific data layout, so a macro that cleans whitespace works the same way on a finance spreadsheet, a clinical trial dataset, or an HR roster.

This also means version control works. Plain text `.bas` files diff cleanly in Git, which monolithic `.xlsm` files do not. Anyone who has tried to review a coworker's macro change in a binary Excel file knows the pain this avoids.

## The Three Categories

The toolkit is organized into three folders, each addressing a recurring class of analyst pain.

### Data Cleaning

These macros fix the kind of structural problems that make a spreadsheet impossible to analyze without preprocessing. **DeleteHiddenRows** removes rows hidden by filters or manual hiding, working bottom-up so that row indices stay stable during deletion. **FillBlanksDown** fills empty cells with the value above, which is the operation needed to repair pivot table exports where labels appear only on the first row of each group. **WhitespaceTools** detects and removes leading, trailing, and multiple-internal-space issues across an entire workbook in a single pass.

### Exports and Documentation

These macros translate Excel content into formats that other tools can consume. **ExportRangeToCSV** writes a clean CSV with intelligent type detection and configurable quoting. **ExportPivotToMarkdown** writes a GitHub-flavored Markdown table from a PivotTable, preserving structure and escaping special characters. **DocumentFormulas** scans every formula on a worksheet and emits a structured JSON file describing each one, including its category, dependencies, and any errors. **DocumentTableFormulas** does the same for Excel Tables (`ListObject` references). **GenerateTableDoc** and **GenerateAdvancedPivotReport** produce comprehensive Markdown documentation of all tables and PivotTables in a workbook, with output deliberately formatted for AI consumption.

### Utilities

A single small macro for a recurring problem: **GetHyperlinkURL** is a custom Excel function that extracts the actual URL from a hyperlinked cell, callable from any worksheet as `=GetHyperlinkURL(A1)`. Excel does not provide a built-in for this, despite its being a near-constant analyst need.

## The Macros

A complete reference, with a one-line description of each:

| Macro | Category | What it does |
|---|---|---|
| `DeleteHiddenRows` | Cleaning | Removes hidden rows using bottom-up scanning and Union batching |
| `FillBlanksDown` | Cleaning | Fills blank cells with the value above, preserving merged cells |
| `WhitespaceTools` | Cleaning | Single-pass workbook-wide whitespace detection, highlighting, and cleanup |
| `DocumentFormulas` | Export | Exports all worksheet formulas to structured JSON for AI review |
| `DocumentTableFormulas` | Export | Documents Excel Table column formulas to Markdown |
| `ExportPivotToMarkdown` | Export | Converts a PivotTable to GitHub-flavored Markdown |
| `ExportRangeToCSV` | Export | High-performance CSV export with type detection and quoting |
| `GenerateAdvancedPivotReport` | Export | Documents all PivotTables (regular and OLAP) in a workbook |
| `GenerateTableDoc` | Export | Generates AI-ready Markdown documentation of all Excel Tables |
| `GetHyperlinkURL` | Utility | Custom function that extracts URLs from hyperlinked cells |

## Why The Documentation Macros Output for AI

Three of the export macros (`DocumentFormulas`, `GenerateTableDoc`, `GenerateAdvancedPivotReport`) deliberately format their output for consumption by AI assistants rather than human reviewers. This is a design choice worth being explicit about.

Modern analytical workflows increasingly involve asking an LLM to help reason about a spreadsheet: explain a formula, suggest an optimization, find an inconsistency, check that a model handles edge cases correctly. These tasks require the LLM to understand the structure of the workbook before it can do anything useful with it. The same context that a human would build by clicking around the workbook (what tables exist, what columns each has, what formulas reference what, where the data quality issues are) is information the LLM has to be given explicitly.

The three documentation macros produce output specifically tuned for this. `GenerateTableDoc` prepends its Markdown with a "Quick Reference for AI" section listing conventions that downstream prompts should respect. `DocumentFormulas` outputs JSON with formula categorization, dependency mapping, and error analysis pre-computed, which lets a follow-up prompt focus on reasoning rather than parsing. The point is that the macros do the structural work that an LLM would otherwise spend tokens on, leaving the LLM free to do the actual analysis the user wants.

## Under The Hood

Three of the macros illustrate engineering patterns worth highlighting. Each one demonstrates a different lesson about working with Excel at scale.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Union batching for fast row deletion" >}}

A naive implementation of "delete all hidden rows" is a loop that calls `Rows(i).Delete` once per hidden row. On a worksheet with hundreds of rows this is fine. On a worksheet with tens of thousands of rows it grinds for minutes, because each individual `Delete` operation triggers Excel's recalculation, screen redraw, and event firing.

The DeleteHiddenRows macro avoids this by collecting all hidden rows into a single `Range` object using `Union`, then deleting that combined range in one call:

```vb
For iCntr = lastRow To 1 Step -1
    If iCntr Mod 500 = 0 Then
        Application.StatusBar = "Scanning row " & iCntr & " of " & lastRow & _
                                " (" & Format((lastRow - iCntr) / lastRow, "0%") & ")"
        DoEvents
    End If

    If ws.Rows(iCntr).Hidden = True Then
        ' Unhide first so Excel can delete it
        ws.Rows(iCntr).Hidden = False

        If rngToDelete Is Nothing Then
            Set rngToDelete = ws.Rows(iCntr)
        Else
            Set rngToDelete = Union(rngToDelete, ws.Rows(iCntr))
        End If
        deletedRows = deletedRows + 1
    End If
Next iCntr

' Delete all collected rows at once
If Not rngToDelete Is Nothing Then
    rngToDelete.EntireRow.Delete
End If
```

Three details are doing real work here.

The loop runs from `lastRow` to `1` in reverse. Forward iteration would break because deleting row 5 would shift rows 6, 7, 8 down to positions 5, 6, 7, and the loop counter would skip a row. Reverse iteration deletes from the bottom up so earlier indices remain stable.

The single deletion at the end batches what would otherwise be thousands of individual operations. Excel's `Delete` method is expensive because of all the bookkeeping it triggers; calling it once on a Union of all hidden rows is dramatically faster than calling it once per row.

The progress reporting (`Application.StatusBar`) updates only every 500 rows, not every row. Updating the status bar is itself an operation; doing it every iteration would add measurable overhead on its own. The 500-row interval gives the user visible progress without measurably slowing the scan.

Excel-side performance flags wrap the whole thing: `ScreenUpdating = False`, `Calculation = xlCalculationManual`, `EnableEvents = False`. These prevent Excel from redrawing, recalculating, and firing change events during the scan. The `CleanExit` block restores them whether the macro succeeds or errors, so the user is never left with a workbook in a strange state.

{{< /accordionItem >}}

{{< accordionItem title="In-memory array processing for whitespace detection across an entire workbook" >}}

A worksheet with 10,000 cells, accessed one cell at a time through `Range.Value` lookups, takes minutes. The same 10,000 cells accessed as a single 2D array (`dataArray = ws.UsedRange.Value`) takes seconds. The cost is in the number of round trips between VBA and Excel's internal model, not in the volume of data.

`WhitespaceTools` exploits this by reading each worksheet's used range into a 2D variant array, scanning the array entirely in memory, building a parallel array marking which cells need highlighting, and writing the highlights back to Excel as bulk operations. The pattern, simplified:

```vb
' Read all cell values at once into memory
dataArray = ws.UsedRange.Value

' Allocate a parallel boolean array for highlighting decisions
ReDim highlightArray(1 To UBound(dataArray, 1), 1 To UBound(dataArray, 2))

' Single pass through the in-memory array
For r = 1 To UBound(dataArray, 1)
    For c = 1 To UBound(dataArray, 2)
        originalText = CStr(dataArray(r, c))
        If Len(originalText) > 0 Then
            ' Detect leading, trailing, or multiple internal spaces
            If Left(originalText, 1) = " " Or Right(originalText, 1) = " " _
               Or InStr(originalText, "  ") > 0 Then
                highlightArray(r, c) = True
                totalIssues = totalIssues + 1
            End If
        End If
    Next c
Next r

' Apply all highlighting in bulk operations on the worksheet
```

Three things this pattern gets right.

The actual scan happens entirely in VBA memory. There is no Excel object access inside the inner loop, which is where the round-trip cost lives. A naive version that called `ws.Cells(r, c).Value` inside the loop would be measurably slower on the same dataset.

The highlight decisions are computed first, then applied. This separation lets the macro batch its formatting operations rather than highlighting cell-by-cell as it scans. Bulk formatting is dramatically faster than per-cell formatting in Excel.

The traversal handles every worksheet in the workbook automatically. The user does not need to select a range or even open a specific sheet; the macro iterates `ActiveWorkbook.Worksheets` and processes each. For a workbook with twenty sheets, this is twenty times less manual work than the equivalent per-sheet macro would require.

{{< /accordionItem >}}

{{< accordionItem title="AI-targeted documentation output" >}}

`GenerateTableDoc` produces Markdown documentation of every Excel Table (`ListObject`) in a workbook. The format is deliberately tuned for an AI assistant rather than a human reader. The opening section makes that explicit:

```vb
output = "# AI-READY EXCEL TABLE DOCUMENTATION" & vbNewLine
output = output & "Generated: " & Format(Now, "yyyy-mm-dd hh:mm:ss") & vbNewLine
output = output & "Workbook: " & wb.Name & vbNewLine
output = output & "Total Tables: " & totalTables & vbNewLine & vbNewLine

' Quick reference for AI
output = output & "## QUICK REFERENCE FOR AI" & vbNewLine
output = output & "- Use table references: TableName[ColumnName]" & vbNewLine
output = output & "- XLOOKUP is preferred over VLOOKUP" & vbNewLine
output = output & "- Check data quality flags before complex analysis" & vbNewLine
output = output & "- Consider performance notes for large datasets" & vbNewLine & vbNewLine
```

The "Quick Reference for AI" header signals to the LLM that the document was prepared with downstream AI consumption in mind. The four bullet points are conventions the user wants the LLM to follow when reasoning about the workbook. Pre-loading these conventions into the documentation means the user does not have to repeat them in every prompt; the LLM sees them once when it ingests the document and applies them throughout the conversation.

The body of the document then describes each table with a consistent structure: name, range, dimensions, column definitions with type detection, formula transparency with full syntax, data quality flags (CLEAN / WARNING / ERROR with percentages), and performance notes calibrated to the dataset size. Every section is in plain Markdown with no Excel-specific formatting.

The result is a document that an LLM can ingest and immediately use to answer questions like "which formulas in this workbook depend on the Sales table?" or "are there any columns with data quality issues that would affect a join with the Customers table?" without the user having to manually describe the workbook structure first. The macro does the structural work; the LLM does the reasoning.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Microsoft Visual Basic for Applications (VBA)
- **Format:** Plain text `.bas` modules importable through the VBA editor
- **Requirements:** Microsoft Excel (Windows or Mac), macro-enabled workbook (`.xlsm`)
- **Recommended:** Excel 2016 or later for best performance on large datasets

## Repo

[github.com/hihipy/excel-vba-toolkit](https://github.com/hihipy/excel-vba-toolkit)
