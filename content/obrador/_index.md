---
title: "~/obrador  # Tool-Building Philosophy"
description: "How and why I build the tools that live in cocina, estudio, garaje, and jardín, and the giants whose work makes mine possible."
date: 2026-05-01
draft: false
showAuthor: false
showBreadcrumbs: true
showDate: false
showDateUpdated: false
showHeadingAnchors: true
showPagination: false
showReadingTime: false
showTableOfContents: true
showTaxonomies: false
showWordCount: false
showSummary: false
sharingLinks: false
showEdit: false
showHero: false
heroStyle: "background"
showZenMode: false
layout: "single"
---

{{< lead >}}
{{< typeit
    tag="h3"
    speed=70
    breakLines=false
    loop=true
>}}
Mi Filosofía de Herramientas
My Tool-Building Philosophy
La Meva Filosofia d'Eines
Η Φιλοσοφία μου για τα Εργαλεία
{{< /typeit >}}
{{< /lead >}}

## Approach

Two things sit underneath every tool I build.

The first is a train of thought. This field rarely hands you a turnkey solution. The data arrives misformatted, the export is structurally broken, the workflow has a step that takes ten minutes and happens forty times a year. The work is in choosing which way of addressing it is worth the effort.

The second is gratitude. Almost nothing I build is original. Every tool sits on top of decades of open-source work, on documentation written by maintainers who answer GitHub issues in their free time, and on accumulated answers to questions that earlier versions of me would have asked. The right framing is not "I built this." It is "I assembled this on top of what was already there."

## When Friction Becomes A Tool

{{< mermaid >}}
flowchart TD
    A[I have a friction point] --> B{Does it recur?}
    B -->|No| C[Live with it<br/>One-off pain isn't worth automating]
    B -->|Yes| D{Does the manual version drift<br/>or produce inconsistent output?}
    D -->|No| E[Manual is fine<br/>Trustworthy by hand means no tool needed]
    D -->|Yes| F[Build the tool<br/>Output has stopped being trustworthy]
{{< /mermaid >}}

Not every annoyance becomes a tool. The threshold is two conditions met at once: the task recurs, and the manual version produces inconsistent results.

A one-off pain is just a one-off pain. A recurring task done consistently by hand is fine. But a recurring task done by hand that drifts a little every time, formatted differently or missing a step occasionally, is where automation pays. Not because the time saved is huge, but because the output stops being trustworthy.

A few concrete examples from the rooms next door.

**A 25Live export that looks usable but isn't.** [25Live](https://collegenet.com/scheduling/25live) is the room and event scheduling system used by most universities. The Excel export from any campus 25Live opens fine. It also has structural problems that quietly break analysis: events split across rows because of recurrence rules, room codes that do not match the master room list, dates parsed as strings. Every analyst who tries to use a 25Live export does the same hour of cleanup before they can ask the actual analytical question. [25live-cleaner](/cocina/25live-cleaner/) does the cleanup once, in code, and produces a written record of every fix applied. Recurring + manual-and-inconsistent.

**Power BI models that no one can see into.** A medium-sized Power BI model has dozens of tables, hundreds of columns, fifty measures with intricate DAX referencing each other, and relationships with their own filtering rules. All of it is invisible from outside Power BI Desktop. You cannot grep it, you cannot diff it, you cannot review it. [pbi-model-export](/garaje/pbi-model-export/) walks the model and emits the whole structure as JSON, with the DAX dependency graph included. The model becomes inspectable. Recurring + opaque.

**Per diem math nobody gets right by hand.** Foreign per diem at a U.S. institution is not a single rate. It is the M&IE rate minus 25% for travel days, minus specific dollar deductions for any provided meal, with the meal deductions varying by city. Doing this calculation by hand for a multi-city trip takes twenty minutes and produces a different answer every time. [foreign-per-diem-calculator](/garaje/foreign-per-diem-calculator-for-usa-based-institutions/) does the math correctly and consistently.

**Qualtrics exports that need an hour of cleaning before any actual work.** A raw Qualtrics export mixes preview and test responses with real ones, has cryptic column names like `Q5_3_TEXT`, stores numbers and dates as strings, and arrives without a codebook. Every fresh export gets the same hour of manual prep. [qualtrics-processing-pipeline](/cocina/qualtrics-processing-pipeline/) eats that hour.

The threshold is the same in every case. If the friction is one-time, live with it. If it recurs and the manual version drifts, build the tool.

## What Not To Share

There is a category of data I will not put into an AI conversation regardless of how convenient it would be: anything subject to a confidentiality obligation that the AI vendor has not signed onto. In my work, that covers most of what crosses my desk: medical data under HIPAA, student records under FERPA, research data under a data use agreement, anything labeled CUI, anything a colleague asked me to keep confidential.

The default assumption has to be that the AI is a third-party data processor without the contractual agreements in place to receive that data. Most consumer AI products operate without a Business Associate Agreement, Data Processing Addendum, or institutional vendor agreement by default. Pasting protected data in is not "borderline"; it is a disclosure to a third party.

The good news is that you almost never need the actual data to get useful help. You need the data's shape: column names, data types, rough cardinality, presence of nulls, distribution shape. That is enough for the AI to suggest code, identify likely problems, and walk through approaches. The shape is not protected; the values are.

A practical workflow that has served me:

**Schema first, values never.** When I want help working with a dataset that contains protected fields, I share the schema (column names, types, row counts, nulls per column) and not a single row. Most analytical questions can be answered from schema alone.

**Synthetic test data.** When I need example data to verify a transformation, I generate synthetic data myself locally and share that with the AI. Same shape as the real data; no real values.

**Aggregate-only diagnostics.** When I am debugging a pipeline and need to see what is happening at a stage, I share aggregate statistics (row counts, value distributions, null rates) rather than rows.

**Identifiers are broader than they look.** It is easy to think identifier-protection is about names and Social Security numbers. The harder cases are the quasi-identifiers: date of birth plus ZIP plus sex re-identifies most U.S. adults. "The only patient at Site 12 with this rare condition" is identifying without naming anyone. Free text in clinical notes, support tickets, and email bodies is the highest-leak surface in most organizations. The test is not "does this string contain an SSN?"; it is "could a moderately resourced adversary, given this content plus public information, identify a specific individual?"

The cost of this discipline is small. The cost of getting it wrong is enormous, and almost always invisible until it is not.

## On Working With AI Assistants

What follows is practical detail on AI assistants: why they belong in the workflow at all, why format conversion matters more than prompt engineering, and how to pre-load context so a session starts smarter than it would on its own.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Why AI Assistants Are The Latest Version Of An Old Argument" >}}

People in this field have been panicking about productivity tools for as long as the field has existed.

When the internet became searchable, there was a real argument that programmers would lose the ability to write code from scratch because every solution was now a Google query away. When Stack Overflow gained traction, there was a follow-up argument that copying and adapting answers was somehow not real engineering. Now AI assistants are the panic of the moment, with the same shape: that using them is cheating, that they will erode the underlying skill, that real practitioners write everything from first principles.

It was wrong each previous time and it is wrong now.

This is a field built on iteration through time. Each generation of practitioners builds on the work of the last, and the tools that compress that loop (search, Stack Overflow, AI assistants) are how the field actually moves forward. The objection assumes there is some pure version of programming that does not involve consulting prior work. That version has never existed.

I use AI assistants heavily. I encounter a problem, I do my own research, and I talk to an LLM. The LLM has read more pages on the problem than I will in my lifetime, and there is a good chance someone with my exact issue has already worked through it. Copying their thinking is not cheating, any more than reading a textbook is cheating. The textbook was someone else's thinking, too.

The field-specific point: most of the code I write is not novel. It is gluing together known operations on known data formats with known libraries. AI assistants are excellent at that kind of work because that kind of work is what they have seen the most of. They struggle on genuinely novel research code, but I am not writing genuinely novel research code. I am cleaning Qualtrics exports.

The right mental model for an AI assistant is an over-eager intern. Bright, fast, willing to take a swing at any problem you hand them, genuinely useful for a wide range of tasks, and still learning. That last part matters. An over-eager intern will sometimes hand you a confident-sounding answer that is partly or entirely wrong: a function that does not exist, a citation that was never published, an API call with a hallucinated parameter. The output looks finished, the tone is assured, and the mistake is invisible until you check. So check. Read every line of code before you commit it. Verify every fact before you cite it. Run every snippet before you ship it. The intern is helpful, but the work is still yours.

LLMs are here to stay, the way the internet is. Getting good at working with them is part of the craft now.

{{< /accordionItem >}}

{{< accordionItem title="Format Conversion Is Higher Leverage Than Prompting" >}}

Once you accept that AI assistants are part of the workflow, the next question is how to make them effective. The biggest leverage is in the format you give them.

LLMs are language models trained largely on the web. The web is built on HTML, which means the document formats LLMs understand best are the ones with HTML lineage: Markdown (which compiles to HTML) and JSON (which the web runs on). Hand an LLM raw Excel and it does its best. Hand it Markdown and it can actually reason. The format change does more for output quality than the prompt does.

This shapes how I build tools.

[**pbi-model-export**](/garaje/pbi-model-export/) is the clearest example. A `.pbix` file is a binary blob. The model inside is structured data, but you cannot show it to anything that does not already speak Power BI. By extracting the model to JSON (every table, column, measure, relationship, the DAX expressions, the dependency graph), the model becomes something an AI can actually read and help me work on. The JSON is for me when I am reviewing the model offline. The JSON is also for Claude when I am asking "what depends on this measure if I rename it." Both audiences benefit from the same artifact.

[**ai-csv-profiler**](/estudio/ai-csv-profiler/) is the same pattern at smaller scale. Pasting a CSV into an AI chat works for ten rows, breaks at a hundred, and is impossible at a million. So the tool produces a small structured JSON document that captures column types, ranges, distributions, and quality issues. Everything an AI needs to reason about the data without seeing the rows. The conversation about the data becomes possible because the data was first translated into a format the AI can hold in its head.

The same logic applies to documentation. Every tool I build has a README written for two audiences at once: a human colleague who needs to know what the tool does and how to run it, and an LLM that I will later ask to extend the tool or fix a bug in it. Good documentation for one is good documentation for the other. They both want clear structure, examples that actually run, and explicit assumptions stated up front.

The pattern is general: anywhere I can convert messy, tool-specific output into Markdown or JSON, I do. Not because it is elegant, though it usually is, but because the conversion expands what the AI can help with from a few lines to the whole problem.

{{< /accordionItem >}}

{{< accordionItem title="Pre-Loading Context So The AI Starts Smarter" >}}

Once the data is in a format the AI can handle, the next leverage point is the context I bring to the session before the conversation even starts.

The pattern: pick a tool, format, or workflow I use repeatedly. Write a guide whose audience is the AI itself. Paste the guide into the start of a session. The AI now begins the conversation already knowing the rules, the gotchas, the output format I expect, and the things it would otherwise get wrong.

I have three of these in heavy rotation:

- A guide that teaches the AI how to generate Standard Notes Super JSON imports correctly, bypassing every markdown-to-Super conversion issue I used to hit, because the AI no longer has to guess at the format.
- A guide that teaches the AI how to generate marimo notebooks that follow the cell-architecture rules and the actual API conventions, not the hallucinated-API ones.
- The identifier-protection reference from the previous section, which sets ground rules for how the AI should handle data I share.

The first two are several hundred lines each. The investment to write them is real, maybe an hour each. But they pay off across every subsequent session, and the alternative is re-explaining the same constraints every time.

Three structural choices that make these guides actually work:

**The audience is named explicitly.** Every guide opens with "Purpose: teaches an AI how to..." and "How to use: feed this entire document to an AI as context." The AI knows it is the audience. This is not a manual for a human reader; it is a manual for the model.

**Hard rules go in NEVER/ALWAYS lists.** These are short, declarative, and grouped. "NEVER use 'python' for Python code blocks; the correct identifier is 'py'." "ALWAYS include all four table cell fields." The list format makes the rules scannable for the AI and reduces the chance it skims past one.

**Verification notes anchor the doc to reality.** Each guide includes a "Verified against: [version], [date]" line. Partly for me, so I know when to update. Partly for the AI, so it weighs the spec higher than its own training data, which is older.

The recursive trick that makes building these tractable: I ask the AI to help me write the guide. I describe the tool or workflow, ask the AI what it would need to know to produce the output reliably, then iterate on what it tells me. The AI is its own audience and its own first reviewer. By the time I ship the guide, it has been tested against the model that will use it.

This approach has a specific limit. Guides work for tools and formats with fixed rules. They do not work for tasks that depend on judgment, context, or my actual data. For those, regular prompting still applies. But for any tool I use repeatedly with a stable spec, building a guide once is a permanent multiplier.

{{< /accordionItem >}}

{{< /accordion >}}

## The Giants

A short, incomplete list of the giants I am standing on.

The Python data ecosystem holds up almost everything in [cocina](/cocina/) and [estudio](/estudio/): [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [openpyxl](https://openpyxl.readthedocs.io/), [requests](https://requests.readthedocs.io/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [Selenium](https://www.selenium.dev/). The GUI work in [estudio](/estudio/) and [jardín](/jardín/) leans on [tkinter](https://docs.python.org/3/library/tkinter.html) and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky, plus [Pillow](https://pillow.readthedocs.io/) and the [wordcloud](https://github.com/amueller/word_cloud) library by Andreas Mueller. In Power BI land, [Tabular Editor 2](https://github.com/TabularEditor/TabularEditor) by Daniel Otykier is the only reason `pbi-model-export` was buildable in the first place. The casa itself runs on [Hugo](https://gohugo.io/) by Bjørn Erik Pedersen and the [Blowfish](https://blowfish.page/) theme by Nuno Coração.

Beyond software, [Stack Overflow](https://stackoverflow.com/) is the reason most analysts can solve most problems most days, and whoever maintains the [pandas docs](https://pandas.pydata.org/docs/) deserves a salary they probably do not get. Lately, [Claude](https://claude.ai/), [ChatGPT](https://chatgpt.com/), [Gemini](https://gemini.google.com/), [Copilot](https://copilot.microsoft.com/), and [Perplexity](https://www.perplexity.ai/) are the newest layer of this stack: not on the same shelf as pandas, but part of the substrate.

Very little of what runs on this site is original code. The composition is mine. The pieces are not.

That is the deal. You build on what is there, and you say so.
