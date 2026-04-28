---
title: "ai-csv-profiler"
weight: 10
description: "A Python utility that produces concise, AI-readable JSON profiles of CSV files. Built so that LLMs can reason about a dataset without ever seeing the raw rows."
summary: "CSV profiler for LLMs."
tags: ["python", "pandas", "data-profiling", "ai", "csv"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< katex >}}

{{< lead >}}
Reads any CSV file and writes a short summary an AI assistant can read, so you can ask it questions about the data.
{{< /lead >}}

## At a Glance

When you want an AI assistant to help you with a CSV file, the obvious move is to paste the file into the chat. That works for ten rows, breaks down at a hundred, and is impossible at a million. This tool produces a small, structured JSON document that captures the important things about a CSV (column types, ranges, distributions, quality issues) so an assistant can reason about the data without ever seeing the raw rows.

The same tool is also useful for human analysts: it gives a fast snapshot of an unfamiliar file before you commit to working with it.

## The Problem

A useful CSV profile is harder to produce than it sounds. Three things have to be true at the same time.

### It Has To Be Compact

The whole point of a profile is to fit in a context window. A profile of a 200-column file that runs to 50,000 tokens defeats its own purpose. Pandas built-in `df.describe()` returns a useful but human-oriented summary that doubles or triples in size once serialized to JSON. Existing libraries like `ydata-profiling` produce excellent HTML reports for human review but are far too verbose for an LLM context.

### It Has To Be Accurate Without Manual Hints

The profiler does not get to ask the user *"is this column a date?"*. It has to figure that out from the data. Every column gets classified into one of six types: numeric, currency, datetime, categorical, boolean, or text. A wrong classification is worse than no classification, because it sends the assistant down a path that does not match the data.

### It Has To Survive The Actual State Of CSV Files In The Wild

Real CSV files arrive with a Byte Order Mark, with semicolons instead of commas, with `cp1252` encoding from a Windows export, with accounting-style negatives like `$(1,234.56)`, with mixed types in a single column, and occasionally with structural corruption. A profiler that crashes on any of these is not useful, because the files that most need profiling are exactly the messy ones.

## The Approach

A single Python script with two interfaces (a Tkinter GUI for interactive use, a CLI for scripting) that reads any reasonably-shaped CSV, classifies each column, computes type-appropriate statistics, and emits a single JSON document.

The reading stage uses a cascading fallback strategy designed around the failure modes above:

{{< mermaid >}}
flowchart TD
    Start[CSV File] --> S1{Strategy 1: encoding x separator matrix}
    S1 -- success --> Done[JSON profile]
    S1 -- all combos failed --> S15{Strategy 1.5: common encodings + auto separator}
    S15 -- success --> Done
    S15 -- failed --> S2{Strategy 2: UTF-8 + auto separator}
    S2 -- success --> Done
    S2 -- failed --> S3{Strategy 3: manual line-by-line parse}
    S3 -- success --> Done
    S3 -- failed --> Err[Return error report]
{{< /mermaid >}}

Whichever strategy succeeds is recorded in the output, so a downstream consumer can see how the file was read. A clean read is recorded in `info`. Strategy 2 or 3 succeeding adds an entry to `warnings`, signalling that the file needed special handling.

## Walking Through the Profile

### Detecting Column Types

Every column goes through a short cascade of heuristic checks. The first one that matches wins, and the order matters: more specific types are checked first, so a numeric-looking column that is actually a currency column gets classified as currency, not as numeric.

| Order | Type | Detection |
|-------|------|-----------|
| 1 | currency | At least 80% of sampled values match a currency regex AND at least one currency symbol is present in the sample |
| 2 | datetime | At least 70% of sampled values parse via `pd.to_datetime` |
| 3 | boolean | All non-null values fall into a small set of known true/false tokens |
| 4 | numeric | Values cleanly cast to float |
| 5 | categorical | Distinct value count is small relative to total values |
| 6 | text | Default fallback |

The cascade is deliberately strict at each step. A column with three non-currency-looking values out of ten will not be classified as currency, because the 80% threshold fails. A column with two distinct text values across 10,000 rows ends up as categorical, not text. The intent is that a wrong classification should be rare even at the cost of occasionally falling back to a more general type.

### Computing Statistics

Numeric and currency columns get a paired statistic block: a *clipped* set computed after dropping the bottom 1% and top 1% of values, and a *raw* set capturing the true minimum and maximum. The clipped block is what ends up in summary fields; the raw block is preserved separately when it differs.

The reason for this split: a single bad row can wreck a column's mean and standard deviation. A salary column with one entry mistakenly recorded as `93508247281341072` will produce statistics that are useless for any human or AI reasoning about the column. Clipping to the 1-99% range gives a representative summary; preserving the raw extremes alongside means the bad row is still visible in the output, just no longer dominating the math.

A separate check then asks whether those raw extremes are far enough from the clipped mean to warrant a warning. The check is a standard z-score test:

$$\frac{|x - \mu|}{\sigma} > k$$

where the threshold \\(k\\) depends on the column type:

- \\(k = 5\\) for plain numeric columns (FTE, counts, IDs)
- \\(k = 30\\) for currency columns (salary, revenue, grant amounts)

The two thresholds exist because the underlying distributions are genuinely different. An FTE column should sit between 0 and 1, so a value 5 standard deviations from the mean is almost certainly corrupt. A salary column at a research institution might legitimately contain both a $225 part-time stipend and a $467K endowed-chair salary, and flagging that as suspicious produces a warning every time. The 30-SD threshold for currency is calibrated to that reality.

### Producing the JSON

The output is a single JSON document with five top-level keys: `file`, `shape`, `columns`, `warnings`, `info`, and `metadata`. Each column entry includes its detected type, missing-value count, three sample values, and a type-appropriate analysis block. A trimmed example for a currency column:

```json
{
  "name": "revenue",
  "type": "currency",
  "total_values": 995,
  "missing": 5,
  "samples": [" $1,250.50 ", " $(890.25)", " $2,100.00 "],
  "analysis": "currency",
  "currency_symbol": "$",
  "valid_numbers": 990,
  "invalid_numbers": 5,
  "statistics": { "min": 45.0, "max": 9876.0, "mean": 1425.75, "median": 1200.0, "std": 850.3 },
  "raw_statistics": { "min": 0.01, "max": 98760.0, "note": "Raw min/max before 1%-99% outlier clipping" },
  "quartiles": { "q25": 750.0, "q75": 2100.0 },
  "zero_count": 0,
  "negative_count": 12
}
```

Note that the sample values preserve original formatting (whitespace, parentheses for negatives), because that information is itself useful: it tells the consumer how the data is actually stored, not just what it logically represents.

## Why The Schema Matters

The output schema is deliberately tuned for LLM consumption. Three design choices worth calling out.

**Warnings are separated from info.** A clean run has an empty `warnings` array and one entry in `info` describing how the file was read. This means a downstream prompt can include something like *"if warnings is non-empty, surface them to the user before answering"* and reliably get the right behavior. Mixing genuine quality issues into the same field as informational messages would break that pattern.

**Statistics come in pairs when outliers exist.** An LLM consuming `statistics` alone gets a clean summary it can trust. If `raw_statistics` is also present, the consumer knows there is something extreme in the data and can choose whether to mention it. This is more useful than a single statistic block where the consumer cannot tell whether the numbers are clean.

**Sample values are always exactly three, always non-null, always truncated to 100 characters.** The consistency means a prompt can rely on the structure without per-column branching. Three is enough to convey format and content; 100 characters caps token usage even on text columns containing essays.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Currency detection with global symbol coverage" >}}

A currency column has to be detected from the data alone, with no schema to lean on. The detection has two parts: a regex that captures the *shape* of a currency value, and a confirmation step that requires at least one actual currency symbol to be present in the sample.

```python
_CURRENCY_SYMBOLS = r"\$€£¥\u20a0-\u20cf"

_CURRENCY_VALUE_RE = re.compile(
    r"^\s*["
    + _CURRENCY_SYMBOLS
    + r"]?\s*"   # optional leading currency symbol
    r"[\(\-]?\s*"           # optional negative: '-' or opening '('
    r"[\d,\.\s]+"           # digits, commas, dots, spaces
    r"\s*\)?\s*$"           # optional closing ')' for accounting negatives
)
```

The symbol class covers the four Latin-alphabet currencies (`$`, `€`, `£`, `¥`) plus the entire Unicode currency symbols block `U+20A0` through `U+20CF`, which contains the rest (₹, ₽, ₩, ₪, ₫, and so on). Coverage is global without enumerating every currency by name.

```python
def _is_currency_column(self, str_values: pd.Series) -> tuple:
    sample = str_values.head(100)
    if len(sample) == 0:
        return False, None

    match_count = sum(1 for v in sample if _CURRENCY_VALUE_RE.match(str(v)))
    if match_count / len(sample) < 0.8:
        return False, None

    # Confirm at least one explicit currency symbol is present.
    joined = " ".join(sample.astype(str))
    symbol_match = re.search(r"[" + _CURRENCY_SYMBOLS + r"]", joined)
    if not symbol_match:
        return False, None

    return True, symbol_match.group(0)
```

The 80% threshold guards against a column where the first few rows are blank or malformed. The symbol confirmation is the part that prevents false positives: a column of plain comma-separated numbers like `"1,234.56"` will match the regex but contains no currency symbol, so it correctly stays classified as numeric.

{{< /accordionItem >}}

{{< accordionItem title="Dual outlier thresholds for numeric versus currency" >}}

The same outlier check would be wrong applied uniformly to all numeric data. The thresholds are deliberately split:

```python
_OUTLIER_SD_THRESHOLD_NUMERIC  = 5    # plain numeric columns (FTE, counts, etc.)
_OUTLIER_SD_THRESHOLD_CURRENCY = 30   # currency columns (salary, revenue, etc.)
```

The asymmetry traces directly to the underlying distributions. Plain numeric columns in a clean dataset are usually drawn from something close to a normal distribution. A 5-sigma deviation in a column that should sit between 0 and 1 (an FTE allocation, for example) is almost certainly corruption: a misplaced decimal point, a stuck key, a stray character that confused the type cast. Flagging it loudly is the right call.

Financial data is different. Salary distributions in a research institution are heavy-tailed by construction. A clinical fellow might earn $52K and an endowed-chair physician $1.2M; both are legitimate. A 5-sigma rule applied here would emit a warning on every salary column, training the consumer to ignore warnings, which is the worst possible outcome for a tool whose value depends on warnings being meaningful.

The 30-sigma threshold for currency is calibrated against this reality. It still catches the egregious case (a salary entered as `93508247281341072` because a database export went wrong), but lets the legitimate long tail through quietly.

{{< /accordionItem >}}

{{< accordionItem title="Cascading CSV read with progressive looseness" >}}

The reader tries strategies in increasing order of permissiveness, recording which one succeeded:

```python
self.encoding_attempts = [
    "utf-8-sig", "utf-8", "cp1252", "iso-8859-1",
    "latin1", "ascii", "utf-16", "utf-32",
]
self.separator_attempts = [",", ";", "\t", "|", ":", " "]
```

`utf-8-sig` is first because BOM-prefixed files (typical of Windows Excel exports) are extremely common and otherwise produce a junk character in the first column name that quietly breaks downstream code. Once that is handled, the rest of the encodings fan out from common to rare.

Each encoding is tried with both pandas engines: the C engine first (fast, strict) and the Python engine as a fallback (slower, more permissive about malformed rows). Only if the entire encoding-by-separator-by-engine matrix fails does the reader fall back to Strategy 1.5, then 2, then a manual line-by-line parse as a last resort.

The progressive structure means clean files take the fast path, edge-case files still get read, and the consumer can always see in the output exactly which path was taken.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.6+
- **Data engine:** pandas
- **GUI:** tkinter (built into Python)
- **Concurrency:** `threading.Thread` with `queue.Queue` for thread-safe UI updates
- **Standard library only otherwise:** `re`, `json`, `argparse`, `pathlib`

## Repo

[github.com/hihipy/ai-csv-profiler](https://github.com/hihipy/ai-csv-profiler)
