---
title: "pbi-model-export"
weight: 40
description: "A Tabular Editor 2 C# script that exports a Power BI model to AI-ready JSON: full schema, recursive DAX dependency chains, top-level KPI detection, RLS roles, and a data head sampled directly from source files on disk."
summary: "Power BI to AI-ready JSON."
tags: ["power-bi", "tabular-editor", "csharp", "dax", "bi", "ai"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< katex >}}

{{< lead >}}
Exports a Power BI dashboard's complete structure to a single file, designed so an AI assistant can answer questions about how the model works.
{{< /lead >}}

## At a Glance

Power BI models are dense. A medium-sized dashboard might contain a dozen tables, two hundred columns, fifty measures with intricate DAX expressions referencing each other, several relationships with their own filtering rules, and row-level security roles applied across the model. All of that structure is invisible from outside Power BI Desktop. You cannot grep it, you cannot diff it, and you cannot show it to anyone who does not already have the file open in Power BI.

This script extracts the entire model into a single structured JSON file. Tables with their columns and types, measures with their full DAX expressions and recursive dependency chains, relationships with cardinality and fact/dimension role hints, RLS roles, and a sample of the actual rows from each table's source file on disk. The JSON is sized and structured to be uploaded directly to an AI assistant, which can then answer questions about the model that would otherwise require manually walking the entire structure in Power BI Desktop.

The script runs inside [Tabular Editor 2](https://github.com/TabularEditor/TabularEditor) — a free third-party tool used by Power BI developers to inspect and edit tabular models. Output lands in the user's Downloads folder, named automatically after the report.

## The Problem

Power BI models are opaque in three specific ways that matter for analyst work.

**They are not text.** A `.pbix` file is a binary archive. You cannot read it without opening it in Power BI Desktop. You cannot diff two versions of a model in a Git tool. You cannot search for a measure's definition without clicking through the model UI. Every exploratory question (what fields are on this table? what's the DAX for this measure?) requires opening the file.

**The dependency graph is implicit.** A measure named `Revenue Growth` might call `[YTD Revenue]`, which calls `[Total Revenue]`, which references the `Sales` table directly. To understand what `Revenue Growth` actually computes, an analyst has to walk this chain manually, jumping between measure definitions in the Power BI UI. There is no view that shows the full transitive closure of dependencies for a given measure.

**The data is one click away from the schema.** A model can be perfectly documented at the schema level (table names, column types, measure DAX) and still be ambiguous about what the data actually looks like. Knowing that a column is named `Region` and has type `String` does not tell you whether its values are full names ("Northeast"), abbreviations ("NE"), codes ("R01"), or something else. Most BI documentation tools stop at the schema and never look at the data.

The script addresses all three. The output is plain JSON, which is greppable, diffable, and parseable. The dependency chains are pre-computed, so a measure's full upstream graph is one field lookup away. And the data head section samples actual rows from each table's source file, so the JSON conveys not just structure but content.

## The Approach

A single C# script (`PBIModelExport.csx`) that runs inside Tabular Editor 2's Advanced Scripting tab. The user opens their Power BI model in Tabular Editor, opens the script, and clicks Run. A few seconds later, a JSON file lands in their Downloads folder, named after the report.

The script does six things in sequence. It enumerates every table, column, measure, relationship, hierarchy, partition, and role in the model. It walks the DAX expressions of every measure to build a dependency graph, both direct and recursive. It computes top-level KPIs by finding measures that no other measure references. It resolves the on-disk source path for each table by parsing the table's M expression and falling through three resolution strategies if the literal path does not exist. It samples the first N rows from each resolved source file. And it writes everything as JSON to the Downloads folder.

{{< mermaid >}}
flowchart TD
    A[User opens Power BI model in Tabular Editor 2] --> B[User runs the script]
    B --> C[Enumerate model: tables, columns, measures, relationships, roles]
    C --> D[For each measure: compute direct dependencies via regex]
    D --> E[For each measure: compute full recursive chain with cycle protection]
    E --> F[Reverse-index dependencies to identify top-level KPIs]
    F --> G[For each table: parse M expression for source folder]
    G --> H[Resolve source folder path on current machine]
    H --> I[Read first N rows from source file]
    I --> J[Build summary section: KPIs, fact/dim hints, measure folders]
    J --> K[Write JSON to Downloads folder]
{{< /mermaid >}}

## The Tabular Editor Constraint

Tabular Editor 2 is a generous host for scripts but a constrained one. It exposes the Power BI tabular object model (TOM) directly, which makes enumeration trivial. But it runs scripts in a sandbox that does not permit arbitrary external DLL references. The .NET base class library is available; specific assemblies that come bundled with the Tabular Editor distribution are available; nothing else.

This rules out the obvious tools for several common operations. Reading XLSX files normally requires either OLEDB drivers (`Microsoft.ACE.OLEDB.12.0`), the Open XML SDK, or EPPlus. None of these are available in TE2's runtime. Writing JSON normally requires Newtonsoft.Json or `System.Text.Json`. These are also not available. Reading source files from non-standard locations would normally use libraries to abstract over OneDrive, SharePoint, etc. Not available.

The script works around each of these. JSON output is built by manual string concatenation with explicit escaping. XLSX files are read by treating them as ZIP archives (which they technically are) and parsing the internal XML directly using `ZipArchive` and `XmlDocument`, both available in the .NET base runtime. Source paths are resolved through environment variables and folder-name search rather than any external service.

The result is a single self-contained `.csx` file with one assembly reference (`#r "System.IO.Compression.dll"`) that runs anywhere Tabular Editor 2 runs. No installation, no configuration, no dependencies beyond what TE2 already provides.

## The AI-First Output Design

The JSON structure is built to be uploaded directly to a chat-based AI assistant rather than read by a human. Three design choices make this work.

The summary section is at the front and condensed. An AI ingesting the file does not need to walk the full schema before it can answer simple questions; the summary already names the user-facing tables, the top-level KPIs, the relationship map, and the column inventory in a few hundred lines. For broad questions, the summary is enough; for specific questions, the rest of the file provides depth.

Every measure carries its own dependency chain, both direct and recursive. An AI asked "what does the `Revenue Growth` measure actually compute?" can read the full upstream graph from a single field rather than having to chase references across the file. The chain is pre-resolved and de-duplicated, so a measure that is reached through three different paths appears once.

The data head section grounds the schema in real values. An AI told that a `Region` column has type `String` does not know whether the values are abbreviations or full names. An AI told that the column has type `String` and shown that the first ten rows contain "Northeast", "Southwest", "Midwest", and "South" can answer concrete questions about the data without guessing.

The trade-off is file size. A model with fifty tables and two hundred measures produces a JSON file of several hundred kilobytes. This is comfortably within the upload limit of any current AI assistant, but it is not a format you would want to read with your eyes.

## Top-Level KPI Detection

The detection of top-level KPIs is conceptually clean. A measure is a top-level KPI if no other measure references it. Equivalently, the set of top-level KPIs is the complement of the set of "measures that are referenced by some other measure":

$$\text{TopLevelKPIs} = \text{AllMeasures} \setminus \text{ReferencedByOthers}$$

In plain English: the top-level KPIs are exactly the measures that nothing else uses. Start with every measure in the model, remove any measure that some other measure references, and what remains is the set of top-level KPIs. The backslash (`\setminus` in math notation) is the set-difference operator, equivalent to "remove from the left side anything that appears in the right side."

The implementation builds this set by walking every measure's DAX expression and extracting the bracketed names it references. Each name found gets added to a `referencedByOthers` set. After the full pass, any measure whose name is *not* in this set is a top-level KPI.

This works because Power BI models, in practice, have a layered measure architecture. Base measures aggregate columns directly: `Total Revenue = SUM(Sales[Revenue])`. Intermediate measures combine base measures: `YTD Revenue = TOTALYTD([Total Revenue], 'Calendar'[Date])`. Top-level KPIs are the names that surface in the visual layer — the cards, the charts, the slicers — and nothing else builds on them. A clean model has a small handful of top-level KPIs and many supporting measures underneath; an unclean model has flat layers with everything at the top.

The output flags this distinction explicitly. Each measure has an `isTopLevelKPI` boolean, and the summary section lists the top-level KPIs separately. An AI asked to review a model can immediately see whether the architecture is clean or whether intermediate measures are being inappropriately surfaced as user-facing KPIs.

## Under The Hood

For the technically curious, three implementation pieces that distinguish the script.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Reading XLSX as a ZIP archive" >}}

XLSX files are ZIP archives with XML inside. The structure is part of the OOXML standard and has been documented by Microsoft since Office 2007. Reading them does not require Office, OLEDB, or any third-party library — just `System.IO.Compression.ZipArchive` and `System.Xml.XmlDocument`, both available in the .NET base runtime that ships with Tabular Editor 2.

Two internal XML files are needed:

- `xl/sharedStrings.xml` is Excel's string deduplication table. Every string value that appears in the workbook is stored once in this table; cells containing those strings reference them by integer index. This means a cell containing the word "Northeast" stores `<v>3</v>` rather than the literal string. Without resolving the shared strings table, every string cell would appear to contain a meaningless number.

- `xl/worksheets/sheet1.xml` contains the actual cell data for the first worksheet. Each cell carries an attribute `t="..."` indicating its type (`s` for shared string, `n` for number, `b` for boolean, etc.) and a `<v>` element with the value. For shared-string cells, the value is the index into the shared strings table.

The script's reader pattern:

```csharp
using (var fileStream = File.OpenRead(filePath))
using (var zip = new ZipArchive(fileStream, ZipArchiveMode.Read))
{
    // Load the shared strings table first
    var sharedStrings = new List<string>();
    var ssEntry = zip.GetEntry("xl/sharedStrings.xml");
    if (ssEntry != null)
    {
        using (var stream = ssEntry.Open())
        {
            var ssDoc = new XmlDocument();
            ssDoc.Load(stream);
            var nsMgr = new XmlNamespaceManager(ssDoc.NameTable);
            nsMgr.AddNamespace("x",
                "http://schemas.openxmlformats.org/spreadsheetml/2006/main");

            foreach (XmlNode si in ssDoc.SelectNodes("//x:si", nsMgr))
                sharedStrings.Add(si.InnerText);
        }
    }

    // Then read the worksheet, resolving shared strings as we go
    var sheetEntry = zip.GetEntry("xl/worksheets/sheet1.xml");
    using (var stream = sheetEntry.Open())
    {
        // ... parse cell values, looking up shared strings by index ...
    }
}
```

The `XmlNamespaceManager` is necessary because the OOXML schema uses an XML namespace. Without registering it, XPath queries like `//x:si` would not match anything. The namespace URI itself is fixed by the standard.

One gotcha: XLSX stores numbers at full IEEE 754 precision in the XML, which means decimal values often appear as scientific notation strings like `3.9E-1`. The script returns these as-is rather than reformatting them, on the principle that downstream consumers (Python, AI assistants) can parse and round as needed. Reformatting in C# would just add a step where precision could be lost.

{{< /accordionItem >}}

{{< accordionItem title="Three-strategy OneDrive path resolution" >}}

When a Power BI model author builds a dashboard, the M expressions for each table contain absolute file paths to the source files. These paths are baked in at authoring time. They contain the original author's username and the original author's OneDrive tenant name. On the original author's machine, they look like:

```
C:\Users\sarah.kim\OneDrive - University of Miami\Sales Data\FY2025
```

On a different user's machine, this path does not exist. Even on the same machine after an account migration, it might not exist. The script's resolver runs three strategies in order:

```csharp
// Strategy 1: try the path verbatim (same machine, same user)
if (Directory.Exists(rawPath)) return rawPath;

// Strategy 2: rebuild using the current user's OneDrive root
var oneDriveRoots = new List<string>();
foreach (var envVar in new[] { "OneDriveCommercial", "OneDrive", "OneDriveConsumer" })
{
    var val = Environment.GetEnvironmentVariable(envVar);
    if (!string.IsNullOrEmpty(val) && !oneDriveRoots.Contains(val))
        oneDriveRoots.Add(val);
}

// Find the OneDrive segment in the stored path and rebuild from there
var segments = rawPath.Split(Path.DirectorySeparatorChar);
var oneDriveSegmentIndex = -1;
for (int i = 0; i < segments.Length; i++)
{
    if (segments[i].StartsWith("OneDrive", StringComparison.OrdinalIgnoreCase))
    {
        oneDriveSegmentIndex = i;
        break;
    }
}

if (oneDriveSegmentIndex >= 0)
{
    var relativeParts = segments.Skip(oneDriveSegmentIndex + 1).ToList();
    var relativePath = string.Join(Path.DirectorySeparatorChar.ToString(), relativeParts);
    foreach (var root in oneDriveRoots)
    {
        var candidate = Path.Combine(root, relativePath);
        if (Directory.Exists(candidate)) return candidate;
    }
}

// Strategy 3: search by folder name as a last resort
// ... recursive folder search under OneDrive roots and profile paths ...
```

Each strategy addresses a different failure mode of the previous one.

Strategy 1 (literal path) works when the script runs on the original author's machine. Trivial case.

Strategy 2 (environment-based rebuild) handles the common case where the script runs on a different user's machine, but the directory structure under OneDrive is the same. The script identifies the segment of the stored path that begins with "OneDrive", takes everything after it, and prepends the current user's OneDrive root from `OneDriveCommercial` (the standard env var on Windows machines logged into a work or school account). For the path above, this produces `C:\Users\philip.bachas\OneDrive - University of Miami\Sales Data\FY2025`.

Strategy 3 (folder name search) is the last resort. If the directory structure has changed between the author's setup and the current user's setup (a folder was renamed, the data moved into a subfolder), the rebuild fails. The script searches recursively under each OneDrive root and the user profile directory for any folder matching the target's leaf name. This is slow and imperfect (a name collision would return the wrong folder) but it covers cases where a careful resolver would otherwise fall back to "folder not found."

If all three strategies fail, the script writes the original path back into the output with an `error` field, so the JSON tells the consumer exactly what was attempted and why it could not be resolved.

{{< /accordionItem >}}

{{< accordionItem title="Recursive DAX dependency resolution with cycle protection" >}}

DAX measures reference each other through bracketed names: `[Total Revenue]`, `[YTD Revenue]`, etc. To compute a measure's full dependency chain, the script walks every reference and recurses into the referenced measure's expression, tracking visited measures to prevent infinite loops on circular references.

```csharp
// Build a name lookup once, before resolving any chains
var allMeasureNames = new HashSet<string>();
foreach (var m in Model.AllMeasures)
    allMeasureNames.Add(m.Name);

var measureExpressions = new Dictionary<string, string>();
foreach (var m in Model.AllMeasures)
    measureExpressions[m.Name] = m.Expression ?? "";

// Recursive resolver
Func<string, HashSet<string>, HashSet<string>> GetFullChain = null;
GetFullChain = (string measureName, HashSet<string> visited) =>
{
    var result = new HashSet<string>();
    if (visited.Contains(measureName)) return result; // cycle detected, bail out
    visited.Add(measureName);

    string expr;
    if (!measureExpressions.TryGetValue(measureName, out expr)) return result;

    foreach (Match match in bracketTokenRegex.Matches(expr))
    {
        var token = match.Groups[1].Value;
        if (token != measureName && allMeasureNames.Contains(token))
        {
            result.Add(token);
            foreach (var downstream in GetFullChain(token, visited))
                result.Add(downstream);
        }
    }
    return result;
};
```

A few details matter.

The `allMeasureNames` set is built once and used as a filter. DAX expressions contain bracketed references to many things that are not measures: column references (`Sales[Revenue]`), table references (`'Calendar'[Date]`), context variables, and so on. The script extracts every bracketed token but only keeps tokens that match a known measure name. This avoids polluting the dependency graph with column references.

The `visited` set is per-call. Each top-level call to `GetFullChain` starts with a fresh `HashSet<string>`. Within a single resolution, a measure that has already been visited returns immediately. This handles the case where a measure has multiple paths to the same upstream measure — it gets counted once.

The cycle protection handles a real edge case. Power BI does not technically prevent circular references at the model level (`A` calling `[B]` which calls `[A]`), and real models occasionally contain them by accident. Without the visited check, the recursion would never terminate. With it, the script bails on the second visit and the cycle is silently broken without affecting the rest of the resolution.

The dependency graph then drives the top-level KPI detection. A reverse pass through every measure's direct dependencies builds a `referencedByOthers` set; the complement of this set against `allMeasureNames` is the top-level KPI list. This is the same set difference computed earlier:

$$\text{TopLevelKPIs} = \text{AllMeasures} \setminus \text{ReferencedByOthers}$$

Both sides of this equation come from the same regex-driven walk. The cost is one full pass through every DAX expression in the model, which is fast even for large models (Tabular Editor's TOM provides the expressions in memory; no I/O is required).

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** C# 6.0 (Tabular Editor 2 scripting flavor, `.csx`)
- **Runtime:** Tabular Editor 2.x with bundled .NET Framework runtime
- **Standard library:** `System.IO.Compression` (XLSX/ZIP parsing), `System.Xml` (Open XML parsing), `System.Text.RegularExpressions` (DAX dependency extraction)
- **No external dependencies:** Single-file `.csx` script with one assembly reference; no NuGet packages, no Office installation, no OLEDB drivers

## Repo

[github.com/hihipy/pbi-model-export](https://github.com/hihipy/pbi-model-export)
