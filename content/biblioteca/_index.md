---
layout: "single"
title: "~/biblioteca  # Case Study Philosophy"
description: "How I think about case studies: peer review as the publish gate, phased walkthroughs over polished one-shots, and the language-tool combinations that fit each stage of the pipeline."
summary: "Case study philosophy."
draft: false
showAuthor: false
showDate: false
showReadingTime: true
showWordCount: false
showBreadcrumbs: true
showTableOfContents: true
showPagination: false
---

{{< katex >}}

{{< lead >}}
{{< typeit speed=70 loop=true breakLines=false >}}
Mi Filosofía de Estudios de Caso
My Case Study Philosophy
La Meva Filosofia d'Estudis de Cas
Η Φιλοσοφία μου για Μελέτες Περιπτώσεων
{{< /typeit >}}
{{< /lead >}}

## Approach

A case study is a piece of analytical work where the *reasoning* is the deliverable, not just the answer.

A dashboard shows a number. A project page shows a tool. A case study shows the path: where the data came from, what was wrong with it, which schema decisions were made and why, what the first-pass queries returned, what surprised me, what the final findings actually support and what they do not. The reader leaves knowing not just what I concluded but how I got there, and they leave with enough information to disagree with me if they want.

Most published analytical work hides where the decisions were made. The dataset arrives pre-cleaned. The schema is presented as if it were inevitable. The exploratory queries that did not pan out are deleted. The reader sees a clean narrative arc that the work itself never had. The case study format pushes back against that. It treats the messiness of real analytical work as content, not embarrassment.

The gating question for whether something earns the case study format: would a careful reader learn how to do this kind of work themselves by reading it? If yes, write it up. If no (the work is routine, the data is uninteresting, the reasoning is not portable), it stays a project page or an internal report.

## Peer Review As The Publish Gate

I do not publish a case study until someone else has reviewed it.

This is the central commitment of the room. Code can be reproducible and still be wrong. A pipeline can run end-to-end and still answer the wrong question. A SQL query can return a number that looks plausible and is off by a factor of two because of a join condition I did not think hard enough about. Reproducibility catches the kind of mistakes that show up when somebody else tries to run your code. It does not catch the kind of mistakes that show up when somebody else reads your *reasoning*.

What is science without the ability to be reproduced *and* reviewed? Reproducibility is the floor. Review is the ceiling. The two are different jobs.

The reviewer does not need to be a domain expert. They need to be careful. The questions a good reviewer asks are not "is this right" but "why did you do it this way" and "what would happen if". A reviewer who asks "why are you joining on Application ID instead of Project Number?" has done more for the case study than any test suite. The right number arrives the same way it arrives in scientific publication: someone who is not the author looks at the work and pushes back.

What this means in practice. Every case study in this room has been read by at least one other person before it went public. The reviewer's questions go into a follow-up pass before publishing, not after. If a reviewer surfaces a substantive issue (the methodology is wrong, the numbers are off, a key assumption is unstated), the case study does not ship until the issue is resolved. This sometimes delays things; that is fine. The cost of publishing a wrong case study is much higher than the cost of holding one for another week.

## The Phased Walkthrough

The shape I use for SQL-on-public-data case studies is four phases, in order: **source**, **schema**, **exploration**, **findings**.

Each phase has to earn its place. The principle: every phase exists to make a class of decision visible that the next phase depends on but most published work hides.

{{< mermaid >}}
flowchart TD
    A["Source: where the data came from, what the export contains, what the exporter did not tell me"] --> B["Schema: the model built on the source, normalization decisions, keys and indexes"]
    B --> C["Exploration: first-pass queries, what the dataset actually contains, where the surprises live"]
    C --> D["Findings: what the data says, what it does not say, caveats per claim"]
    D --> E["Peer Review: independent reader checks methodology and numbers before publication"]
    E --> F["Published Case Study"]
{{< /mermaid >}}

**Source** documents where the data came from. Not just "I downloaded this from NIH" but: which search criteria, which export options, what the file actually contains, what the ambiguities are. This phase is the one most often skipped, and it is the one that determines whether the case study can be reproduced at all. If a reader cannot recreate the source dataset, every downstream finding becomes unauditable. The source phase is also where I document the things the exporter did not tell me: byte-order marks, preamble lines, columns that are blank-space rather than null, a phantom column produced by a trailing comma. These are the things that bite.

**Schema** documents the model I built on top of the source. A normalized SQLite database with three tables and explicit indexes is a different deliverable than a pile of CSV files; the differences matter. This phase covers the data-modeling decisions: why this normalization rather than that one, where the keys come from, what gets indexed, what assumption each table encodes about the data. This is where the case study earns its right to be a case study rather than a CSV-in-a-zip-file. Anyone can publish a dataset; few people document the schema decisions that make the dataset useful.

**Exploration** documents the first-pass queries that establish what the dataset actually contains. Yearly counts, top institutions, category distributions. These queries are not the findings; they are the orientation. They are also the place where I notice things I did not expect (a spike in 2009 that turns out to be ARRA, a 25% rate of missing cost data that turns out to be NIH's funder-specific cost reporting policy). The case study should show these moments of orientation because they are where the analytical instinct gets exercised.

**Findings** documents what the data actually says, and equally important, what it does not say. Every finding gets its own caveat. A claim about institutional rankings has to be honest about the funder split. A claim about year-over-year growth has to mention the ARRA period and what gets included or excluded. The findings phase is where I am most disciplined about not over-claiming, because this is the phase the reader will quote.

The four phases are not the only valid structure. A case study built on streaming data, an A/B test, or a machine learning model would have different phases. The principle generalizes: each phase exists to make a category of decision visible. Pick the categories that fit your problem.

## The Stack

A case study runs the whole data science pipeline end to end. Most published analytical work shows only the last stage, the polished finding. The case study format insists on showing more, because the reasoning is the deliverable.

{{< mermaid >}}
flowchart TD
    A["Raw Source: databases, APIs, CSVs, web scrapes, public datasets"] --> B["Ingest: read into a tool that can actually work with it"]
    B --> C["Clean: fix encoding, dates, nulls, structural quirks"]
    C --> D["Transform: normalize, join, derive, build the working model"]
    D --> E["Explore: first-pass queries, distributions, surprises"]
    E --> F["Model and Analyze: statistical tests, regressions, aggregations"]
    F --> G["Validate: sanity checks, peer review, does the answer hold up"]
    G --> H["Communicate: the polished case study, readable by humans and LLMs"]
{{< /mermaid >}}

Each stage in this pipeline has its own right tool, and the pipeline as a whole has cross-cutting concerns that do not belong to any single stage. Version control wraps everything, because every stage produces artifacts worth tracking and reverting. Containerization (typically [Docker](https://www.docker.com/)) wraps the language and library versions so the pipeline runs the same on my laptop today as on someone else's laptop a year from now. Peer review sits between Validate and Communicate as the publish gate covered in section two; the pipeline is not done until somebody else has read it. [GitHub](https://github.com/) handles the version control and the collaboration around it, with pull requests as the natural unit of review.

The rest of this section walks through what happens at each stage and which tool I reach for. Different stages of the pipeline have different needs, and the right tool depends on which stage you are in. Different stages of that pipeline have different needs, and the right tool depends on which stage you are in.

The notebook stage and the polished-output stage are different jobs. Notebooks are for the iterative work where you run cells out of order, change your mind, and rebuild the dataframe three times before you trust it. The polished output is for the deliverable where the document itself is the artifact. Mixing the two produces notebooks that pretend to be reports and reports that pretend to be notebooks. Both are worse than the unmixed versions.

| Language | Strengths | Notebook | When to Reach for It |
|---|---|---|---|
| **Python** | Pipelines, ETL, Glue Code, ML, Web Work | [marimo](https://marimo.io/) (or [Jupyter](https://jupyter.org/)) | Default for Most Analytical Work |
| **R** | Statistics, Static Figures, Regression-Heavy Analysis | Jupyter with R Kernel, or [RStudio](https://posit.co/products/open-source/rstudio/) | When the output is a statistical claim or a publication-quality static figure |
| **Julia** | Numerical Computing, Simulations, Performance-Bound Work | [Pluto](https://plutojl.org/) | When Python runs out of steam. Not yet part of my stack; watching it. |
| **SQL** | Data Extraction, Joins, Aggregations | (Queries Inside Any of the Above) | When the data lives in a relational store and the work is shape, not statistics |

[Quarto](https://quarto.org/) is the unifier across all four. It executes Python, R, Julia, and SQL chunks in the same document, and it renders to HTML, PDF, Word, Typst, or several presentation formats from a single source. The polished-output decision is not language-by-language; it is Quarto, with whatever language each chunk needs.

The decision of which language and which notebook to reach for, as a tree:

{{< mermaid >}}
flowchart TD
    A["What is the deliverable?"] --> B{"Is it a statistical claim or a static figure?"}
    B -->|Yes| C["R + ggplot, Notebook: Jupyter R kernel or RStudio"]
    B -->|No| D{"Is it a pipeline, tool, or web-facing system?"}
    D -->|Yes| E["Python, Notebook: marimo or Jupyter"]
    D -->|No| F{"Is performance the binding constraint?"}
    F -->|Yes| G["Julia, Notebook: Pluto"]
    F -->|No| E
    C --> H["Polished output: Quarto"]
    E --> H
    G --> H
{{< /mermaid >}}

The tree's job is to surface the choice rather than make it. Most analytical work lands at the Python branch because most analytical work is pipelines and ETL. The R branch matters when the deliverable is the chart itself, where ggplot's defaults and the tidyverse's grammar pay off. The Julia branch is the watchlist branch, the one I would reach for if a Python loop became the bottleneck on a future case study.

A small example of what Quarto's polyglot capability actually looks like in practice. The same source file pulls data with SQL, transforms it in Python, and renders the final chart in R. The example below shows a generic daily-weather analysis (any case study could be substituted; this one was picked because the data is universally familiar):

````markdown
---
title: "Daily High Temperatures, Last Five Years"
format: html
---

```{sql connection=con}
-- Daily high temperature readings from the weather station
SELECT observation_date, high_temp_f
FROM daily_observations
WHERE observation_date >= DATE('now', '-5 years')
ORDER BY observation_date;
```

```{python}
# Convert to a pandas DataFrame and compute a 30-day rolling average
import pandas as pd
df = pd.DataFrame(_, columns=["observation_date", "high_temp_f"])
df["observation_date"] = pd.to_datetime(df["observation_date"])
df["rolling_avg"] = df["high_temp_f"].rolling(window=30, center=True).mean()
```

```{r}
# Render the publication-quality figure with ggplot
library(ggplot2)
ggplot(py$df, aes(x = observation_date, y = high_temp_f)) +
  geom_point(alpha = 0.3, color = "#0969DA") +
  geom_line(aes(y = rolling_avg), color = "#CF222E", linewidth = 1) +
  labs(x = "Date", y = "Daily High (°F)") +
  theme_minimal()
```
````

Three languages, one document, one render. The reader sees a continuous narrative; the author writes whatever fits each step. This is the pitch.

R for stats and static figures specifically because of the [tidyverse](https://www.tidyverse.org/) and [ggplot2](https://ggplot2.tidyverse.org/). `glimpse()` and `summary()` and `dplyr` and the way ggplot composes graphics layer by layer make R the language where exploratory data analysis feels right. Static figures from ggplot are publication-quality by default; getting matplotlib to the same place takes effort that most analysts do not put in.

Python for everything else, because Python is where the pipeline ecosystem lives. pandas for the dataframes, the entire `scikit-` family for ML, requests and BeautifulSoup for the web layer, sqlite3 and SQLAlchemy for the database layer. When the deliverable is a pipeline that runs on a schedule or a tool that another system consumes, Python is where the libraries you need actually exist.

Julia is the language I am watching but have not yet needed. The pitch is that it gives you Python's readability with the speed of compiled native code, plus a numerical computing ecosystem that handles things Python and R both struggle with. If a future case study runs into a database large enough that Python's performance becomes the bottleneck, or a simulation where the inner loop matters, or a machine learning experiment where the training time is the constraint, Julia is the language I would reach for. I am noting it here so I am thinking about it, not because I have used it in anger yet.

SQL is the language where most of the data lives, and a case study that does not include SQL is usually a case study that has copied data into a tool other than the one it should be in.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Why Quarto, Specifically" >}}

Three properties of Quarto matter for case studies.

**Polyglot in the same document.** A case study sometimes needs SQL for extraction, Python for transformation, and R for the regression at the end. Quarto runs all three in the same source file, with each chunk getting the right kernel. The reader sees one continuous narrative; the author writes whatever fits each step.

**One source, many outputs.** The same `.qmd` file renders to HTML for the web, PDF for distribution, Word for collaborative editing, and Typst for typeset output. Presentations come out as [reveal.js](https://revealjs.com/), Beamer, or PowerPoint without rewriting the source. This matters because case studies usually live in more than one place: the public web version, the version a colleague edits in Word, the version a stakeholder gets as PDF. One file produces all of them.

**The output stays runnable.** A Quarto document carries its computational state. Re-rendering it re-runs the chunks. If a number changes upstream, every figure that depends on it updates. The published artifact is reproducible by construction, not by hope.

The downside: Quarto is a fairly large investment to learn. The `_quarto.yml` configuration, the chunk options, the cross-reference syntax, the format-specific options, and the relationship between Quarto and pandoc all take time to internalize. For a one-off analysis, the overhead is not worth it. For case studies, where the document *is* the deliverable and where the same document needs to render to multiple formats, the investment pays.

{{< /accordionItem >}}

{{< accordionItem title="Marimo Over Jupyter For Iterative Work" >}}

[Marimo](https://marimo.io/) is a Python notebook environment with two structural advantages over Jupyter that matter for case studies.

**Files are `.py`, not `.ipynb`.** Jupyter notebooks are JSON documents that mix source, output, metadata, and execution counts in a format that is git-hostile. Two analysts editing the same notebook produce merge conflicts that include base64-encoded image data. Marimo's notebooks are Python files. The same git workflow that works for any other Python file works for marimo notebooks. A pull request shows a real diff. A code review on a marimo notebook is the same as a code review on any other Python module.

**Reactive execution kills the stale-state bug class.** In Jupyter, cells can be run out of order. A variable defined in cell 12 can be used in cell 4, then cell 12 can be deleted, then cell 4 still works because the variable is alive in the kernel. The notebook looks fine. It is not. When somebody else opens the notebook and runs it top to bottom, it crashes. Marimo solves this structurally. A cell that depends on another cell re-runs automatically when the dependency changes. Cells run in topological order. There is no hidden state because the dependency graph is the execution model. The notebook that runs in your environment is the notebook that will run in mine.

The cost of marimo is that some Jupyter conventions do not translate. IPython's `%%` magics, certain widget libraries, and a handful of niche extensions either do not work or work differently. For most analytical work, the trade is worth it. For work that depends on the specific Jupyter ecosystem, Jupyter remains the default.

[Pluto](https://plutojl.org/) is the Julia equivalent: same reactive principle, same plain-text file format, designed for the Julia ecosystem the same way marimo is designed for Python.

{{< /accordionItem >}}

{{< accordionItem title="The Step-Ladder README, With A Worked Example" >}}

The step-ladder README is a structural choice with a specific shape: plain English at the top, increasing technical depth as you scroll. Each layer answers a different question for a different reader. To make the structure concrete, here is what the three layers might look like for a hypothetical tool that cleans Qualtrics CSV exports.

**The top layer.** Plain English. Audience: anyone, including a non-technical colleague who is trying to figure out whether this tool is for them.

```markdown
# qualtrics-cleaner

Cleans up the messy CSV files that Qualtrics produces when you export
survey responses. Drops preview and test responses, fixes the column
names, and saves a tidy version that opens cleanly in Excel or any
analysis tool. If you have ever opened a Qualtrics export and seen
three header rows and cryptic column codes, this tool is for you.
```

No commands, no library names, no version numbers. A reader who only needs to know what the tool is for stops here.

**The middle layer.** Operational. Audience: an engineer or analyst who has decided to use the tool and needs to know how to run it.

```markdown
## Usage

Install requirements:

    pip install -r requirements.txt

Run the cleaner against a Qualtrics CSV export:

    python clean.py path/to/export.csv

The output is written to `path/to/export-clean.csv` in the same directory
as the input. The original file is not modified. If you want to change
the output location, pass `--output path/to/output.csv`.

Optional flags:

- `--keep-preview` retains preview responses (default: drops them)
- `--keep-test`    retains test responses (default: drops them)
- `--qsf path`     supplies a Qualtrics Survey Format file for richer
                   column labeling (default: infers labels from the CSV)
```

This is the layer most users read. It is also the layer that gets the most maintenance: as flags are added, defaults change, or new input formats are supported, the operational layer is what needs to stay current.

**The bottom layer.** Internal. Audience: a contributor or reviewer who is going to extend the tool or audit how it works.

```markdown
## How It Works

The cleaning pipeline runs in five stages. Each stage is implemented as
a separate function in `clean.py` and can be tested independently.

1. **Header parsing.** Qualtrics CSVs have three header rows: column ID
   (`Q5_3_TEXT`), question text, and a JSON metadata blob. The parser
   reads all three and reconciles them into a single canonical column
   name per column. The reconciliation logic prefers the question text
   when it is non-empty and unambiguous; falls back to column ID when
   the question text is duplicated across columns.

2. **Response filtering.** Preview responses are identified by the
   `Status` column being `Survey Preview`. Test responses are identified
   by `DistributionChannel == 'preview'`. Both are dropped by default
   because they pollute aggregate statistics, but can be retained via
   the corresponding flags.

[... continues for the remaining stages ...]

## Assumptions

The tool assumes UTF-8 encoding (Qualtrics has been BOM-less since 2023
in our experience; if your export is older, decode it first).

The tool assumes the Qualtrics export uses the "Use choice text" option.
If the export uses numeric codes instead, the cleaned file will preserve
the codes; supply a QSF file to translate them back into labels.

## Extending

The five stages are loosely coupled. To add a new cleaning step, add a
function to `clean.py` following the existing pattern (input: pandas
DataFrame, output: pandas DataFrame, with a docstring explaining the
transformation), then add it to the `pipeline` list in the `main`
function in the order it should run.
```

This layer almost never gets read by end users. It gets read intensely by anyone modifying the tool, anyone reviewing a pull request, and anyone trying to figure out whether the tool's behavior on a corner case is intentional. The "Assumptions" subsection is particularly important: it documents the things the code does not say out loud, which is exactly what a reviewer needs.

The three layers respect three different reader budgets. The top layer is for the reader who has thirty seconds. The middle layer is for the reader who has five minutes and a problem to solve. The bottom layer is for the reader who has half an hour and a fork of the repository open. A README that mixes the three (an "Installation" header above an "Architectural Decision Records" subsection above a "What is this tool" tagline) makes none of those readers happy.

The same step-ladder logic applies to case studies themselves. The case study landing page should answer "what is this and what did I find" in plain English. The phase pages should answer "how did I get there" in operational detail. The accordion-deep technical material should answer "what assumptions are baked in and how would I extend the analysis" for the reviewer or contributor. Three layers, three audiences, one document.

{{< /accordionItem >}}

{{< accordionItem title="Editors That Earn Their Place" >}}

The editor is part of the workflow, and the right editor depends on the work. A case study that touches Python for ETL, SQL for queries, R for a regression chart, Quarto for the polished output, and shell for the build commands does not have one editor that handles all of that equally well. It has a few editors that each handle their own piece, and the analyst's job is to know which is which.

**JetBrains** is the family I reach for when the work is deep in one language. [PyCharm Professional](https://www.jetbrains.com/pycharm/) is the strongest Python IDE in the field: real refactoring (rename a function and every call site updates, move a method between classes and the imports follow), an inline debugger that handles pandas and NumPy gracefully, type checking that catches things mypy misses, and a test runner that integrates with pytest without ceremony. [DataGrip](https://www.jetbrains.com/datagrip/) is the equivalent for SQL: connects to almost any database, autocompletes against the actual schema, runs queries against multiple databases at once, and surfaces query plans in a way no other tool I have used does. [IntelliJ IDEA](https://www.jetbrains.com/idea/) is the parent of all of them and the answer when the work is in Java or Kotlin. The cost is that JetBrains tools are heavy: they take a moment to launch, they consume memory, and the per-tool licensing adds up. The benefit is that for sustained work in a single language, nothing else matches the depth of what they understand about your code.

**[VS Code](https://code.visualstudio.com/)** is the omnivore. Free, fast to launch, and the extension ecosystem covers every language a case study touches and many it never will. The extensions I actually use: [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) for Python type checking and intelligent autocomplete, the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) for working with notebooks inline, the [Quarto extension](https://marketplace.visualstudio.com/items?itemName=quarto.quarto) for case study authoring, [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) for understanding why a line of code looks the way it does and who last touched it, and [Remote-SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) for editing files on a remote server as if they were local. The case for VS Code as the default editor is that the work moves between languages constantly, and an editor that handles all of them adequately beats five specialized editors that each handle one of them perfectly. JetBrains wins on depth in a single language; VS Code wins on coverage across all of them.

**[Positron](https://positron.posit.co/)** is the editor I am watching. Built by [Posit](https://posit.co/) (the company behind RStudio and Quarto) on VS Code's foundation, designed specifically for data science: R, Python, and SQL as first-class citizens, a data viewer panel showing dataframes as actual tables, a plot pane, an environment pane showing the variables currently in scope. The pitch is "RStudio for the polyglot era": the workflow that R analysts have had for fifteen years, available for Python work too, with the option to mix the two in the same session. Positron is younger than the alternatives and the extension ecosystem is still catching up, so it is not yet my daily editor. But for case study work specifically (where the data is small enough to inspect, where the workflow alternates between code and visualization, and where R and Python both show up in the same project), Positron is the editor most likely to displace VS Code in the next few years. I am noting it here because case study workflows are exactly what Positron is optimized for.

**Lightweight editors** matter for a different category of task: opening a single file, making one edit, saving, closing. Setting up a project in PyCharm or VS Code for a five-minute change is overkill. On macOS, [Sublime Text](https://www.sublimetext.com/) and [BBEdit](https://www.barebones.com/products/bbedit/) are the long-running classics; [Nova](https://nova.app/) is the polished native option for editors who want to feel at home in macOS. On Windows, [Notepad++](https://notepad-plus-plus.org/) is the workhorse: free, fast, has been "good enough" for two decades. Cross-platform, Sublime Text and VS Code in its lightweight mode (no extensions, no project loaded) both handle this category well. Pick one and learn its keyboard shortcuts; the speed of "open file, edit, save, quit" matters more than which specific editor you pick.

**[Vim](https://www.vim.org/) and [Neovim](https://neovim.io/)** are their own category. Terminal-based, modal, with a steep initial learning curve and a payoff that takes years to fully realize. The argument for them is that text editing is faster when your hands never leave the keyboard, that working over SSH on a remote server makes a terminal editor a necessity, and that the underlying skill (knowing the modal-editing vocabulary) is portable across decades because vim is part of the cultural literacy of the field. The argument against is that the learning curve is real and the payoff is back-loaded. Most analysts can be productive without ever learning vim. Most analysts who do learn it eventually use it for the small subset of tasks (quick edits over SSH, manipulating a config file on a server, working in a constrained environment) where the alternatives are worse. Worth knowing the basics (`i` to insert, `Esc` to leave insert mode, `:wq` to save and quit, `dd` to delete a line) even if you never use it as your daily driver. The basics are enough to survive when nothing else is available.

The unifying principle: editors are tools, and good tools fit the work. JetBrains for sustained work in one language. VS Code for moving between languages. Positron for the data-centric workflow. Something lightweight for the five-minute edits. Vim for the moments when no other option exists. The question is never "which editor is best" but "which editor fits the task in front of me right now."

{{< /accordionItem >}}

{{< /accordion >}}

## Documentation As Part Of The Work

The code and the document are the same artifact, written for two audiences.

**Verbose comments for audit.** I comment more than most engineers, on purpose. Every non-trivial transformation gets a comment that explains *why*, not just *what*. The audience for these comments is a future reviewer, including future me. When a colleague is auditing my work, the comments are the breadcrumbs that let them follow the reasoning without having to reconstruct it. When an LLM is helping me extend or fix a piece of code months later, the comments are what let the LLM understand the decisions that the code itself does not show. Both audiences benefit from the same density. The threshold I aim for: any decision that I had to think about gets a comment; any line where the choice was not obvious to me gets a comment; any block that does something non-default gets a comment. Code without comments is code that has been written but not explained.

A short before-and-after to make the standard concrete. The same five lines of pandas, written for shipping versus written for audit.

Before:

```python
df = pd.read_csv(path)
df = df[df["status"] == "active"]
df["amount"] = df["amount"].fillna(0)
df["amount"] = df["amount"].astype(float)
totals = df.groupby("region")["amount"].sum()
```

After:

```python
# Source CSV is the raw daily export from the source system. Header row is
# on line 1 with no preamble. Encoding is UTF-8 with no BOM, confirmed by
# inspecting the first few bytes of a sample export.
df = pd.read_csv(path)

# Keep only active records. Closed and pending entries are intentionally
# excluded per the methodology approved at the project kickoff: closed
# records are out of scope, pending records have unstable amounts that
# would distort the aggregate. See the methodology document for the
# rationale behind each exclusion.
df = df[df["status"] == "active"]

# Missing amounts get filled with zero rather than dropped. Decision: an
# active record with no amount is a real record with a zero amount (the
# value has not been entered yet), not a data-quality issue. Confirmed with
# the data owner that this matches their reporting convention.
df["amount"] = df["amount"].fillna(0)

# Cast to float because the source CSV stores amounts as strings (the
# upstream system exports numeric values with thousand-separators that
# pandas does not auto-parse on read_csv). Cast happens after fillna so
# the zero-fill values stay numeric.
df["amount"] = df["amount"].astype(float)

# Group by region and sum. This is the headline number; a reviewer should
# be able to read up to here and understand exactly what is being summed
# and why.
totals = df.groupby("region")["amount"].sum()
```

The two versions produce the same answer. The second one survives the question "why did you exclude pending records and what did you do with the nulls" without the author being in the room. That is what audit-readability buys.

Comment density is one half of audit-readability. Layout consistency is the other. The two halves work together: a reviewer auditing a pipeline does not want to spend cognitive effort decoding indentation conventions, naming rules, or where the imports go; they want to spend effort on the work. The same applies in reverse to a contributor extending the code, and to a future-self returning months later. Each language has a canonical style guide that the field has converged on. Knowing them and applying them is the cheapest available form of audit-readability:

| Language | Style Guide | Covers |
|---|---|---|
| Python (Code) | [PEP 8](https://peps.python.org/pep-0008/) | Indentation, Naming, Line Length, Imports, the Official Python Style |
| Python (Docstrings) | [PEP 257](https://peps.python.org/pep-0257/) | Docstring Conventions, Pairs with PEP 8 |
| R | [Tidyverse Style Guide](https://style.tidyverse.org/) | Naming, Syntax, Pipes, Packages, the `<-` vs `=` Rule |
| Julia | [Julia Style Guide](https://docs.julialang.org/en/v1/manual/style-guide/) | Naming, Performance Idioms, Design Patterns |
| SQL | [SQL Style Guide (Holywell)](https://www.sqlstyle.guide/) | Capitalization, Indentation, Aliasing, the Widely-Cited Unofficial Reference |
| JavaScript | [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) | ES6+, Naming, Modules, the Most-Adopted JS Style |
| Bash | [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) | Indentation, Naming, Quoting, Error Handling |

What these guides share is more important than what differentiates them. Each one names the choices that consistent style takes off the table: where to put a brace, how to break a long line, when to capitalize a keyword, whether the function name uses snake_case or camelCase. The choices themselves are mostly arbitrary. The consistency is the point. A code review on a pull request that violates twelve PEP 8 rules is a code review where eleven of the twelve comments are about style instead of about the work; that is a worse review than one where the style is uniform and the comments are about the substance. The style guide is the contract that makes the review possible at the right level.

**The step-ladder README.** Every case study and every supporting tool gets a README structured as a step ladder, plain English at the top and increasing technical depth as you scroll down.

The top of the README answers: what is this and who is it for, in language that a non-technical reader can follow. No jargon, no library names, no version numbers.

The middle answers: how do you run it. Concrete commands, expected inputs, expected outputs, environment requirements. This is the layer that an engineer who needs to use the tool reads.

The bottom answers: how does it work, what assumptions are baked in, what would I need to verify if I wanted to extend it. This is the layer for a reviewer or a contributor.

Each layer has a different audience. A reader who only needs the top gets the top. A reader who needs the middle keeps scrolling. A reader who is going to modify the code reads everything. The structure respects each audience's time.

**Code blocks, mermaid diagrams, and LaTeX where they earn their place.** The case study format has to work for two audiences at once: the technical reader who can read pandas code, and the non-technical reader (an HR partner, a director without a coding background, a recruiter who happens to be curious) who needs to follow the reasoning without parsing syntax. Visual elements are the bridge between the two.

A [mermaid](https://mermaid.js.org/) diagram does for structure what a paragraph cannot. Prose is sequential; a diagram is spatial. When the work has flow (data sources feeding a pipeline, decisions branching off a question, phases depending on each other), prose forces the reader to hold the structure in working memory while reading the next sentence. A diagram puts the structure on the page so the reader can see it at a glance. The first phased-walkthrough diagram in section two is a working example: a non-technical reader who would skim past the four paragraphs explaining source, schema, exploration, and findings can look at the diagram and immediately understand that these are sequential steps with peer review as the gate. The diagram does not replace the prose; it makes the prose easier to enter.

Mermaid earns its place beyond flowcharts as well. Database schema is the second category where a diagram outperforms prose: prose forces the reader to track which columns belong to which table, which keys are primary and which are foreign, and which tables relate to which others by which cardinality, all while reading. An [erDiagram](https://mermaid.js.org/syntax/entityRelationshipDiagram.html) puts the structure on the page so the reader can see it at a glance. A small worked example, an e-commerce schema with four normalized tables, illustrates the form:

{{< mermaid >}}
erDiagram
    CUSTOMERS ||--o{ ORDERS : "places"
    ORDERS ||--|{ LINE_ITEMS : "contains"
    PRODUCTS ||--o{ LINE_ITEMS : "appears in"

    CUSTOMERS {
        int    customer_id PK
        string email
        string first_name
        string last_name
        date   created_at
    }

    ORDERS {
        int    order_id PK
        int    customer_id FK
        date   order_date
        string status "pending / shipped / delivered"
    }

    LINE_ITEMS {
        int    line_item_id PK
        int    order_id FK
        int    product_id FK
        int    quantity
        float  unit_price "price at time of order"
    }

    PRODUCTS {
        int    product_id PK
        string sku
        string name
        float  current_price
    }
{{< /mermaid >}}

The same information rendered as prose ("the customers table has a one-to-many relationship with orders, which has a one-to-many relationship with line items, which has a many-to-one relationship with products") is technically correct but visually flat. The reader has to construct the diagram in their head. The rendered version is read at a glance. For a case study where the schema phase is one of four, the ER diagram is the natural form for the deliverable; a phase 02 that documents schema decisions without rendering the schema is doing the harder version of the same job.

[LaTeX](https://www.latex-project.org/) rendering does the same thing for mathematics. Every reader who has been through any formal education has seen formulas typeset this way: in math textbooks, in chemistry classes, in physics labs, in statistics courses, in economics readings. By the time anyone reaches adulthood, decades of pattern matching are already baked in. A rendered formula is read fluently the way a printed paragraph is read fluently, because the visual conventions are the ones the reader has been seeing since their first arithmetic worksheet. The standard notation is a universal alphabet for quantitative work, and LaTeX is the typesetter that produces it.

The same statistical claims, written two ways:

```
chi-squared(2) = 14.3, p = 0.0008
```

\\[\chi^2(2) = 14.3,\ p = 0.0008\\]

```
Cohen's d = (M1 - M2) / sqrt((s1^2 + s2^2) / 2)
```

\\[d = \dfrac{M_1 - M_2}{\sqrt{(s_1^2 + s_2^2) / 2}}\\]

```
Pearson r = sum((xi - x_mean)(yi - y_mean)) / sqrt(sum((xi - x_mean)^2) * sum((yi - y_mean)^2))
```

\\[r = \dfrac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i - \bar{x})^2 \sum_{i=1}^{n}(y_i - \bar{y})^2}}\\]

```
linear regression: y_hat = beta_0 + beta_1*x_1 + beta_2*x_2 + ... + beta_k*x_k
```

\\[\hat{y} = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \cdots + \beta_k x_k\\]

```
Bayes: P(A given B) = P(B given A) * P(A) / P(B)
```

\\[P(A \mid B) = \dfrac{P(B \mid A)\, P(A)}{P(B)}\\]

The ASCII version of each is technically faithful, but it is visually flat. The reader has to parse the symbols character by character, holding the meaning in working memory. The rendered version is read at a glance because the reader has been seeing formulas in this exact format since elementary school. Rendered math also signals formality. It says "this number was produced by a method with a name." ASCII math says "the author typed some letters and numbers in a sentence." For a non-technical reader trying to gauge how rigorous a claim is, that distinction matters.

Code blocks do a third job. The obvious one is that they let the reader copy and run the example. The less obvious one is that they let the reader skim past the example with confidence. A reader who is not interested in the SQL details for a particular query can see the code-block visual signal, recognize "this is a chunk of technical content I can skip," and move on without feeling like they have missed something. The visual chrome of a code block is itself part of the document's navigation: it gives the prose reader a clear stopping rule and lets them move at their own depth. This is the step-ladder principle applied to a single page rather than to the README as a whole. The technical material is on the page; the reader chooses how deep to go.

The unifying principle: these visual elements are not decoration. Each one earns its place by communicating something prose alone would not, and by making the document readable at multiple levels of technical depth at the same time.

**LLMs as a second audience.** The same case study should be readable by a human and by an LLM. Obrador covers the format-conversion case for AI-readability in detail; the case-study-specific angle is that a well-written case study is something you can hand to an LLM years later and ask "what did I conclude here, and why?" and get a useful answer. The LLM becomes an interface to your own past reasoning. This works better when the case study is structured: clear headings, explicit assumptions, equations rendered as math rather than ASCII, code blocks tagged with their language. None of this requires extra effort. It is the same hygiene that makes a case study readable by a human.

## The Giants

A short, incomplete list of the people whose work made this room possible.

The R and tidyverse ecosystem rests on [Hadley Wickham](http://hadley.nz/), whose [tidyverse](https://www.tidyverse.org/) and [ggplot2](https://ggplot2.tidyverse.org/) defined what modern data analysis in R looks like, and whose ["Tidy Data"](https://vita.had.co.nz/papers/tidy-data.pdf) paper is the most influential single piece of writing on data structure of the last twenty years.

[JJ Allaire](https://github.com/jjallaire) and the [Posit](https://posit.co/) team built [Quarto](https://quarto.org/), the polyglot publishing system that this whole room's output strategy depends on. They also built [RStudio](https://posit.co/products/open-source/rstudio/) before that, which made R approachable for a generation of analysts.

[Yihui Xie](https://yihui.org/) wrote [knitr](https://yihui.org/knitr/) and the dynamic-document infrastructure that Quarto extends. The model of executable documents that produce reproducible artifacts comes through his work.

[Fernando Pérez](https://bids.berkeley.edu/people/fernando-perez) and the IPython team gave the world [Jupyter](https://jupyter.org/), which is the substrate that almost every Python notebook environment, including marimo, defines itself against. Even when I prefer marimo for new work, the standard that marimo improves on is Jupyter, and that standard is enormous.

[Akshay Agrawal](https://akshayagrawal.com/) and the [Marimo Labs](https://marimo.io/) team built [marimo](https://marimo.io/) on the principle that notebook reproducibility is a structural problem with a structural solution. The reactive-execution model that makes marimo work is their contribution to the field.

[Fons van der Plas](https://fonsp.com/) and the Pluto team did the same job for Julia. [Pluto](https://plutojl.org/) is what reactive notebooks look like when they are designed from the start for a language with strong type inference and native plotting.

[Jeff Bezanson, Stefan Karpinski, Viral B. Shah, and Alan Edelman](https://julialang.org/blog/2012/02/why-we-created-julia/) created [Julia](https://julialang.org/) on the bet that scientific computing should not require choosing between speed and expressiveness. The bet has paid off enough that Julia is now on the watchlist of every analyst who has ever waited for a Python loop to finish.

The data storytelling tradition rests on [John Tukey](https://en.wikipedia.org/wiki/John_Tukey), whose [*Exploratory Data Analysis*](https://archive.org/details/exploratorydataa00tuke_0) gave the field both the name and the practice; on [Edward Tufte](https://www.edwardtufte.com/tufte/), whose [*The Visual Display of Quantitative Information*](https://www.edwardtufte.com/tufte/books_vdqi) is the standard against which every chart is implicitly judged; and on [Cole Nussbaumer Knaflic](http://www.storytellingwithdata.com/), whose [*Storytelling with Data*](http://www.storytellingwithdata.com/book) is the pragmatic translation of the older tradition for working analysts.

Beyond software and books, the [Jupyter community](https://jupyter.org/community), the [Posit community](https://forum.posit.co/), the [Julia Discourse](https://discourse.julialang.org/), and [Stack Overflow](https://stackoverflow.com/) are the ambient infrastructure that makes case study work tractable. Most of the time, the question I am about to ask has been asked and answered already. The asking and the answering are themselves contributions.

The composition of any case study is mine. The methods, the tools, and the field's accumulated knowledge that the case study draws on are not.

