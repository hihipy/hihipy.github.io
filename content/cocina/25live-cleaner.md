---
title: "25live-cleaner"
weight: 10
description: "A Python tool that turns messy 25Live scheduling exports into clean data ready for analysis, with a full record of every change made."
summary: "Cleans 25Live calendar exports."
tags: ["python", "pandas", "etl", "data-cleaning", "audit"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< katex >}}

{{< lead >}}
A Python tool that takes messy university scheduling exports and turns them into clean spreadsheet rows ready for analysis.
{{< /lead >}}

## At a Glance

[25Live](https://collegenet.com/scheduling/25live) is the room and event scheduling system used by most universities. When you export a schedule report, the resulting Excel file looks usable but contains structural problems that quietly break any analysis you try to do with it. This tool fixes those problems automatically and produces both a clean dataset and a written record of every fix that was made.

## The Problem

Imagine you ask 25Live for a report of every event held on campus last semester so you can answer a simple question: how many hours per week is each lecture hall actually in use? You open the export and immediately hit four issues.

### Issue 1: Events Split Across Midnight

A late-running event like a film screening or a hackathon does not appear as a single row. The system splits it at midnight and uses the placeholder word `cont` (short for *continued*) where a real timestamp should be:

| Date       | Start    | End      | Location          |
|------------|----------|----------|-------------------|
| 2024-09-15 | 9:00 PM  | `cont`   | Lecture Hall 101  |
| 2024-09-16 | `cont`   | 2:00 AM  | Lecture Hall 101  |

A human reading this can tell that a single event ran from 9 PM Sunday to 2 AM Monday. To a computer doing arithmetic on it, those `cont` cells are nonsense and the event looks like two unrelated rows.

### Issue 2: Multi-Day Events Fragmented Into Pieces

Even when timestamps are present, an event spanning multiple days gets split into one row per calendar day. A weekend conference becomes three rows that need to be recognized as one continuous event for utilization math to work.

### Issue 3: Silent Duplicates

If you export "September" and then later export "September through October," every September row exists twice. The duplicates are not flagged, and they inflate every count and total.

### Issue 4: Inconsistent Text

`"Lecture Hall 101"`, `"Lecture Hall  101"` (two spaces), and `"lecture hall 101"` are three different strings to a computer. Any grouping by location double-counts.

Each issue is fixable manually, but doing it by hand for a semester's worth of data takes hours and is error-prone. Doing it the same way every time is nearly impossible.

## The Approach

The tool runs the data through a fixed sequence of cleaning steps and writes two files: a clean CSV ready for analysis, and a JSON file documenting exactly what happened.

{{< mermaid >}}
flowchart TD
    A[Raw Excel Export] --> B[Parse and Standardize]
    B --> C[Reconstruct cont Timestamps]
    C --> D[Stitch Multi-Day Fragments]
    D --> E[Deduplicate]
    E --> F[Clean CSV]
    E --> G[Audit Log JSON]
{{< /mermaid >}}

A single Python script handles all of it. A non-technical user double-clicks, picks an Excel file in a pop-up window, and gets the cleaned files in their Downloads folder. No notebooks, no environment setup, no command-line knowledge required.

## Walking Through the Cleanup

### Reconstructing `cont` Timestamps

The handler scans each event group and replaces `cont` placeholders with real timestamps inferred from neighboring rows. Following the earlier example:

**Before:**

| Date       | Start    | End      |
|------------|----------|----------|
| 2024-09-15 | 21:00:00 | `cont`   |
| 2024-09-16 | `cont`   | 02:00:00 |

**After:**

| Date       | Start    | End      |
|------------|----------|----------|
| 2024-09-15 | 21:00:00 | 23:59:59 |
| 2024-09-16 | 00:00:00 | 02:00:00 |

The two rows now have valid timestamps and can be joined cleanly in the next step.

### Stitching Multi-Day Fragments

Two consecutive rows for the same event are merged into one if the gap between them is small enough to count as continuous. Formally, rows \\(A\\) and \\(B\\) are merged when:

$$\text{start}(B) - \text{end}(A) \leq \delta$$

where \\(\delta\\) is a configurable maximum gap (default: 1 minute). The two rows above become a single event:

| Event             | Start                | End                  |
|-------------------|----------------------|----------------------|
| Hackathon Kickoff | 2024-09-15 21:00:00  | 2024-09-16 02:00:00  |

Now duration math works: 5 hours, and not "two events of unclear length."

### Removing Duplicates

Each row is treated as a tuple of its identifying fields: \\((\text{date}, \text{start}, \text{end}, \text{location}, \text{organization}, \text{event})\\). A row is kept only if that tuple has not already been seen. A configuration flag controls whether the head-count column participates in this comparison; by default it does not, because the same event re-exported on different days sometimes carries a slightly different head-count value, and treating those as different rows would defeat the purpose.

### Standardizing Text

Location and organization fields are stripped of stray whitespace and normalized for capitalization, so `"Lecture Hall 101"`, `"lecture hall 101"`, and `"Lecture Hall  101"` all collapse to a single canonical spelling.

## Why the Audit Log Matters

When data has been transformed before analysis, three questions need defensible answers:

1. **What changed.** How many rows were dropped as duplicates? How many `cont` cells were resolved? How many fragments were stitched?
2. **What software did the changing.** Which version of the script, which version of pandas, on which operating system?
3. **Can we reproduce this.** Given the same input file, does running the script again produce the same output?

The audit log answers all three. Each run writes a JSON file containing a SHA-256 cryptographic fingerprint of the script itself, the pandas and Python versions, the operating system, every configuration flag in effect, and counts for every transformation. If a number in a downstream report ever needs to be defended, the audit log makes that defense possible.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Detecting and reconstructing cont continuations" >}}

The `cont` token shows up in two flavors: a bare `cont` cell, or a prefixed form like `cont 2:00 AM` where the system left a continuation marker followed by an actual time. A naive equality check misses the prefixed case. The detector handles both:

```python
def _is_cont(v) -> bool:
    if pd.isna(v):
        return False
    s = str(v).strip().lower()
    return s == "cont" or s.startswith("cont ")
```

Once a row is identified as having a `cont` start, end, or both, the reconstruction substitutes the conventional sentinel times. A `cont` start becomes `00:00:00` (the row inherits midnight as its starting boundary). A `cont` end becomes `23:59:59` (the row runs to the end of its calendar day):

```python
def _fill_cont_times(row, start_col_raw, end_col_raw, start_col_parsed, end_col_parsed):
    start_is_cont = _is_cont(row[start_col_raw])
    end_is_cont   = _is_cont(row[end_col_raw])
    start_s = "00:00:00" if start_is_cont else _time_to_str_hms(row[start_col_parsed])
    end_s   = "23:59:59" if end_is_cont   else _time_to_str_hms(row[end_col_parsed])
    return start_is_cont, end_is_cont, start_s, end_s
```

The function returns flags alongside the values so the audit log can later count exactly how many `cont` cells were resolved on each side. Without those flags, downstream code would have no way to distinguish a row that was reconstructed from one whose timestamps were already clean.

{{< /accordionItem >}}

{{< accordionItem title="Identity-aware stitching with a configurable gap threshold" >}}

The stitching pass treats each event group as an interval-merging problem. Rows are sorted by event identity, then by start time, then iterated once through a single pass that maintains an open interval `[open_start, open_end]` and absorbs any subsequent row whose start falls within `max_gap` of the current end:

```python
for _, grp in df_sorted.groupby(key_cols, dropna=False, sort=False):
    valid = grp[grp[start_col].notna() & grp[end_col].notna()].copy()

    open_start = None
    open_end = None
    open_row = None
    stitched_rows = []

    for _, r in valid.iterrows():
        if open_start is None:
            open_start = r[start_col]
            open_end = r[end_col]
            open_row = r.copy()
        else:
            if (r[start_col] - open_end) <= pd.Timedelta(max_gap):
                if r[end_col] > open_end:
                    open_end = r[end_col]
            else:
                # gap too large, close the current interval and start a new one
                base = open_row.copy()
                base[start_col] = open_start
                base[end_col]   = open_end
                stitched_rows.append(base)
                open_start = r[start_col]
                open_end = r[end_col]
                open_row = r.copy()
```

`max_gap` is configurable (default `1min`) and parsed by `pd.Timedelta`, so callers can tighten or loosen the contiguity definition without touching the code. The `kind="mergesort"` flag on the upstream sort guarantees stability: when two rows share identical key fields and start times, their original order is preserved, which matters because one of those rows gets chosen as the template for the merged record's non-time metadata.

Identity awareness comes from the `groupby(key_cols)` wrapper. Stitching only happens within rows that share event, location, and organization, so two unrelated events that happen to abut in time never merge.

{{< /accordionItem >}}

{{< accordionItem title="Reproducibility through script self-hashing" >}}

Every audit log captures a fingerprint of the exact code that produced it. The script reads its own bytes, hashes them with SHA-256, and writes that hash into the JSON output alongside Python and pandas versions and the host platform:

```python
def _script_identity():
    here = os.path.abspath(__file__)
    with open(here, "rb") as fh:
        sha256 = hashlib.sha256(fh.read()).hexdigest()
    return {
        "script_version": SCRIPT_VERSION,
        "script_path": here,
        "script_mtime": mtime,
        "script_sha256": sha256,
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "pandas_version": pd.__version__,
        "cwd": os.getcwd(),
    }
```

Two practical consequences. First, comparing the SHA-256 across two audit logs answers a question that file modification timestamps cannot: did the code actually change between these two runs, or just the file's metadata? Second, embedding the pandas version closes a subtle reproducibility gap. Pandas' datetime parsing has shifted behavior across major versions, and the same input can produce different outputs on pandas 1.5 versus 2.x. Recording the version means a future investigation can identify whether a discrepancy is real or a library upgrade artifact.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.10+
- **Data handling:** pandas, numpy
- **Excel reading:** openpyxl
- **User interface:** tkinter (built into Python, used for the file-picker pop-up)

## Repo

[github.com/hihipy/25live-cleaner](https://github.com/hihipy/25live-cleaner)
