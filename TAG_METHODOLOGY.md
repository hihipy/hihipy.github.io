# Tag Methodology and Controlled Vocabulary

A faceted tagging scheme for the portfolio. Every tag belongs to exactly one of five facets, drawn from a fixed controlled vocabulary. A page declares a small, bounded set across facets rather than a flat pile of keywords.

## The Five Facets

| Facet | Answers | Rule |
|---|---|---|
| **language** | what it is written in | programming, query, markup, typesetting languages actually used |
| **tool** | what it is built with | libraries, frameworks, databases, apps, formats; the primary ones, not every dependency |
| **concept** | what method or idea it shows | techniques and practices: etl, causal-inference, data-visualization |
| **domain** | what it is about | subject matter from a short controlled list of broad domains |
| **type** | what the artifact is | exactly one: case-study, data-essay, tool, calculator, side-project |

## Rules

- Canonical form is kebab-case, no spaces. `data essay` becomes `data-essay`.
- Aim for 4 to 7 tags per page, at most 2 to 3 from any one facet.
- Every page carries exactly one `type` (defaulted from its room when missing).
- A tool that supports many engines gets one representative tool plus a concept, not one tag per engine. SQL X-Ray drops from 11 tags to its real shape.
- Prefer a broader facet term over a single-use hyper-specific tag. Dataset names and state names are dropped; `public-data` plus the page title carry that weight.
- Two sources of truth stay in sync with this vocabulary: `content/tags/<tag>/_index.md` term pages and the `$tagMap` in `card.html`.

## Controlled Vocabulary: every existing tag, classified

| Old tag | Facet | Canonical | Action |
|---|---|---|---|
| `ai` | concept | `ai` | keep |
| `asyncio` | tool | `asyncio` | keep |
| `audit` | concept | `audit` | keep |
| `beautifulsoup` | tool | `beautifulsoup` | keep |
| `bi` | concept | DROP | drop |
| `bigquery` | tool | DROP | drop |
| `browser-automation` | concept | `web-scraping` | merge |
| `calculator` | type | `calculator` | keep |
| `causal-inference` | concept | `causal-inference` | keep |
| `college-scorecard` | domain | DROP | drop |
| `combinatorics` | concept | `combinatorics` | keep |
| `csharp` | language | `csharp` | keep |
| `csv` | tool | `csv` | keep |
| `ctes` | concept | `ctes` | keep |
| `customtkinter` | tool | `tkinter` | merge |
| `data essay` | type | `data-essay` | merge |
| `data-cleaning` | concept | `data-cleaning` | keep |
| `data-essay` | type | `data-essay` | keep |
| `data-profiling` | concept | `data-profiling` | keep |
| `data-quality` | concept | `data-quality` | keep |
| `data-visualization` | concept | `data-visualization` | keep |
| `datasette` | tool | `datasette` | keep |
| `dax` | language | `dax` | keep |
| `deep-time` | domain | `earth-science` | rename |
| `documentation` | concept | `documentation` | keep |
| `econometrics` | concept | `econometrics` | keep |
| `etl` | concept | `etl` | keep |
| `excel` | tool | `excel` | keep |
| `exploratory-analysis` | concept | `exploratory-analysis` | keep |
| `finance` | domain | `finance` | keep |
| `firebird` | tool | DROP | drop |
| `florida` | domain | DROP | drop |
| `higher-ed` | domain | `higher-education` | rename |
| `html` | language | `html` | keep |
| `inequality` | domain | `economics` | rename |
| `json` | tool | `json` | keep |
| `jupyter` | tool | `jupyter` | keep |
| `kentucky` | domain | DROP | drop |
| `latex` | language | `latex` | keep |
| `llm` | concept | `llm` | keep |
| `logistic-regression` | concept | `logistic-regression` | keep |
| `macros` | concept | `macros` | keep |
| `mariadb` | tool | DROP | drop |
| `mathematics` | concept | `mathematics` | keep |
| `matplotlib` | tool | `matplotlib` | keep |
| `multi-provider` | concept | `llm` | merge |
| `mysql` | tool | DROP | drop |
| `nclex` | domain | `nursing-education` | merge |
| `nih` | domain | DROP | drop |
| `nih-reporter` | domain | DROP | drop |
| `nltk` | tool | `nltk` | keep |
| `nursing-education` | domain | `nursing-education` | keep |
| `operations-research` | concept | `operations-research` | keep |
| `optimization` | concept | `optimization` | keep |
| `oracle` | tool | DROP | drop |
| `pandas` | tool | `pandas` | keep |
| `pdf` | tool | `pdf` | keep |
| `per-diem` | domain | `finance` | merge |
| `postgresql` | tool | `postgresql` | keep |
| `power-bi` | tool | `power-bi` | keep |
| `predictive-modeling` | concept | `predictive-modeling` | keep |
| `process-improvement` | concept | `process-improvement` | keep |
| `public-data` | concept | `public-data` | keep |
| `python` | language | `python` | keep |
| `qualtrics` | tool | `qualtrics` | keep |
| `r` | language | `r` | keep |
| `reporting` | concept | `reporting` | keep |
| `scale` | concept | DROP | drop |
| `schema-design` | concept | `schema-design` | keep |
| `selenium` | tool | `selenium` | keep |
| `seo` | concept | `seo` | keep |
| `side-project` | type | `side-project` | keep |
| `sports` | domain | `sports` | keep |
| `sql` | language | `sql` | keep |
| `sql-server` | tool | DROP | drop |
| `sqlite` | tool | `sqlite` | keep |
| `sqlite-utils` | tool | `sqlite-utils` | keep |
| `survey-data` | concept | `survey-data` | keep |
| `synthetic-control` | concept | `synthetic-control` | keep |
| `tabular-editor` | tool | `power-bi` | merge |
| `tkinter` | tool | `tkinter` | keep |
| `travel` | domain | `travel` | keep |
| `vba` | language | `vba` | keep |
| `web-scraping` | concept | `web-scraping` | keep |
| `window-functions` | concept | `window-functions` | keep |
| `word-cloud` | concept | DROP | drop |
| `wordnet` | tool | `nltk` | merge |

## Resulting Vocabulary by Facet

- **language** (8): `csharp`, `dax`, `html`, `latex`, `python`, `r`, `sql`, `vba`
- **tool** (18): `asyncio`, `beautifulsoup`, `csv`, `datasette`, `excel`, `json`, `jupyter`, `matplotlib`, `nltk`, `pandas`, `pdf`, `postgresql`, `power-bi`, `qualtrics`, `selenium`, `sqlite`, `sqlite-utils`, `tkinter`
- **concept** (29): `ai`, `audit`, `causal-inference`, `combinatorics`, `ctes`, `data-cleaning`, `data-profiling`, `data-quality`, `data-visualization`, `documentation`, `econometrics`, `etl`, `exploratory-analysis`, `llm`, `logistic-regression`, `macros`, `mathematics`, `operations-research`, `optimization`, `predictive-modeling`, `process-improvement`, `public-data`, `reporting`, `schema-design`, `seo`, `survey-data`, `synthetic-control`, `web-scraping`, `window-functions`
- **domain** (7): `earth-science`, `economics`, `finance`, `higher-education`, `nursing-education`, `sports`, `travel`
- **type** (3): `calculator`, `data-essay`, `side-project`

## Per-File Effect (before -> after)

**archivo/college-scorecard-fl/01-source.md**  (5 -> 5)
  - was: college-scorecard, csv, data-quality, public-data, sql
  - now: language:[sql]  tool:[csv]  concept:[data-quality, public-data]  type:[case-study]

**archivo/college-scorecard-fl/02-schema.md**  (5 -> 6)
  - was: etl, python, schema-design, sql, sqlite
  - now: language:[python, sql]  tool:[sqlite]  concept:[etl, schema-design]  type:[case-study]

**archivo/college-scorecard-fl/03-exploration.md**  (4 -> 5)
  - was: datasette, exploratory-analysis, sql, sqlite
  - now: language:[sql]  tool:[datasette, sqlite]  concept:[exploratory-analysis]  type:[case-study]

**archivo/college-scorecard-fl/04-findings.md**  (5 -> 6)
  - was: ctes, datasette, sql, sqlite, window-functions
  - now: language:[sql]  tool:[datasette, sqlite]  concept:[ctes, window-functions]  type:[case-study]

**archivo/college-scorecard-fl/_index.md**  (6 -> 5)
  - was: college-scorecard, datasette, florida, higher-ed, sql, sqlite
  - now: language:[sql]  tool:[datasette, sqlite]  domain:[higher-education]  type:[case-study]

**archivo/kentucky-nih/01-source.md**  (4 -> 4)
  - was: csv, data-quality, nih-reporter, public-data
  - now: tool:[csv]  concept:[data-quality, public-data]  type:[case-study]

**archivo/kentucky-nih/02-schema.md**  (5 -> 6)
  - was: python, schema-design, sql, sqlite, sqlite-utils
  - now: language:[python, sql]  tool:[sqlite, sqlite-utils]  concept:[schema-design]  type:[case-study]

**archivo/kentucky-nih/03-exploration.md**  (4 -> 5)
  - was: datasette, exploratory-analysis, sql, sqlite
  - now: language:[sql]  tool:[datasette, sqlite]  concept:[exploratory-analysis]  type:[case-study]

**archivo/kentucky-nih/04-findings.md**  (5 -> 6)
  - was: ctes, datasette, sql, sqlite, window-functions
  - now: language:[sql]  tool:[datasette, sqlite]  concept:[ctes, window-functions]  type:[case-study]

**archivo/kentucky-nih/_index.md**  (5 -> 4)
  - was: datasette, kentucky, nih-reporter, sql, sqlite
  - now: language:[sql]  tool:[datasette, sqlite]  type:[case-study]

**archivo/penobscot-nclex/01-source.md**  (5 -> 5)
  - was: csv, data-quality, nclex, nursing-education, public-data
  - now: tool:[csv]  concept:[data-quality, public-data]  domain:[nursing-education]  type:[case-study]

**archivo/penobscot-nclex/02-schema.md**  (5 -> 6)
  - was: etl, python, schema-design, sql, sqlite
  - now: language:[python, sql]  tool:[sqlite]  concept:[etl, schema-design]  type:[case-study]

**archivo/penobscot-nclex/03-exploration.md**  (4 -> 5)
  - was: datasette, exploratory-analysis, sql, sqlite
  - now: language:[sql]  tool:[datasette, sqlite]  concept:[exploratory-analysis]  type:[case-study]

**archivo/penobscot-nclex/04-findings.md**  (6 -> 6)
  - was: logistic-regression, nclex, nursing-education, predictive-modeling, r, sql
  - now: language:[r, sql]  concept:[logistic-regression, predictive-modeling]  domain:[nursing-education]  type:[case-study]

**archivo/penobscot-nclex/_index.md**  (6 -> 6)
  - was: datasette, nclex, nursing-education, r, sql, sqlite
  - now: language:[r, sql]  tool:[datasette, sqlite]  domain:[nursing-education]  type:[case-study]

**archivo/texas-synthetic-control/01-question.md**  (4 -> 5)
  - was: causal-inference, econometrics, public-data, synthetic-control
  - now: concept:[causal-inference, econometrics, public-data, synthetic-control]  type:[case-study]

**archivo/texas-synthetic-control/02-method.md**  (5 -> 6)
  - was: causal-inference, econometrics, predictive-modeling, r, synthetic-control
  - now: language:[r]  concept:[causal-inference, econometrics, predictive-modeling, synthetic-control]  type:[case-study]

**archivo/texas-synthetic-control/03-results.md**  (5 -> 6)
  - was: causal-inference, data-visualization, econometrics, r, synthetic-control
  - now: language:[r]  concept:[causal-inference, data-visualization, econometrics, synthetic-control]  type:[case-study]

**archivo/texas-synthetic-control/04-inference.md**  (5 -> 6)
  - was: causal-inference, data-visualization, econometrics, r, synthetic-control
  - now: language:[r]  concept:[causal-inference, data-visualization, econometrics, synthetic-control]  type:[case-study]

**archivo/texas-synthetic-control/_index.md**  (5 -> 6)
  - was: causal-inference, econometrics, predictive-modeling, r, synthetic-control
  - now: language:[r]  concept:[causal-inference, econometrics, predictive-modeling, synthetic-control]  type:[case-study]

**cocina/25live-cleaner.md**  (5 -> 6)
  - was: audit, data-cleaning, etl, pandas, python
  - now: language:[python]  tool:[pandas]  concept:[audit, data-cleaning, etl]  type:[tool]

**cocina/brimr-downloader.md**  (6 -> 6)
  - was: browser-automation, etl, higher-ed, nih, python, selenium
  - now: language:[python]  tool:[selenium]  concept:[etl, web-scraping]  domain:[higher-education]  type:[tool]

**cocina/qualtrics-processing-pipeline.md**  (6 -> 7)
  - was: etl, jupyter, pandas, python, qualtrics, survey-data
  - now: language:[python]  tool:[jupyter, pandas, qualtrics]  concept:[etl, survey-data]  type:[tool]

**cocina/qualtrics-report-generator.md**  (6 -> 7)
  - was: etl, higher-ed, html, python, qualtrics, reporting
  - now: language:[html, python]  tool:[qualtrics]  concept:[etl, reporting]  domain:[higher-education]  type:[tool]

**despacho/earths-history-lived-in-78-years.md**  (3 -> 4)
  - was: data-visualization, deep-time, public-data
  - now: concept:[data-visualization, public-data]  domain:[earth-science]  type:[data-essay]

**despacho/the-2026-job-application-paradox.md**  (2 -> 3)
  - was: mathematics, public-data
  - now: concept:[mathematics, public-data]  type:[data-essay]

**despacho/the-first-trillion-to-scale.md**  (3 -> 2)
  - was: data essay, inequality, scale
  - now: domain:[economics]  type:[data-essay]

**despacho/the-pro-conference-premium.md**  (7 -> 7)
  - was: data-essay, sports, optimization, operations-research, combinatorics, python, data-visualization
  - now: language:[python]  concept:[combinatorics, data-visualization, operations-research, optimization]  domain:[sports]  type:[data-essay]

**estudio/ai-csv-profiler.md**  (5 -> 6)
  - was: ai, csv, data-profiling, pandas, python
  - now: language:[python]  tool:[csv, pandas]  concept:[ai, data-profiling]  type:[tool]

**estudio/decode-for-humans.md**  (6 -> 6)
  - was: ai, customtkinter, documentation, llm, multi-provider, python
  - now: language:[python]  tool:[tkinter]  concept:[ai, documentation, llm]  type:[tool]

**estudio/linkedin-banner-wordcloud-generator.md**  (7 -> 6)
  - was: ai, llm, matplotlib, python, side-project, tkinter, word-cloud
  - now: language:[python]  tool:[matplotlib, tkinter]  concept:[ai, llm]  type:[side-project]

**estudio/sql-x-ray.md**  (11 -> 6)
  - was: bigquery, firebird, json, llm, mariadb, mysql, oracle, postgresql, sql, sql-server, sqlite
  - now: language:[sql]  tool:[json, postgresql, sqlite]  concept:[llm]  type:[tool]

**garaje/excel-vba-toolkit.md**  (5 -> 6)
  - was: data-cleaning, documentation, excel, macros, vba
  - now: language:[vba]  tool:[excel]  concept:[data-cleaning, documentation, macros]  type:[tool]

**garaje/expense-report-review-calculator.md**  (4 -> 4)
  - was: calculator, excel, finance, higher-ed
  - now: tool:[excel]  domain:[finance, higher-education]  type:[calculator]

**garaje/foreign-per-diem-calculator-for-usa-based-institutions.md**  (6 -> 5)
  - was: calculator, excel, finance, higher-ed, per-diem, travel
  - now: tool:[excel]  domain:[finance, higher-education, travel]  type:[calculator]

**garaje/pbi-model-export.md**  (6 -> 5)
  - was: ai, bi, csharp, dax, power-bi, tabular-editor
  - now: language:[csharp, dax]  tool:[power-bi]  concept:[ai]  type:[tool]

**garaje/timeline-of-events-business-days.md**  (4 -> 4)
  - was: calculator, excel, higher-ed, process-improvement
  - now: tool:[excel]  concept:[process-improvement]  domain:[higher-education]  type:[calculator]

**jardin/ascii-username-generator.md**  (5 -> 4)
  - was: nltk, python, side-project, tkinter, wordnet
  - now: language:[python]  tool:[nltk, tkinter]  type:[side-project]

**jardin/dialogorithm.md**  (5 -> 5)
  - was: latex, mathematics, python, side-project, tkinter
  - now: language:[latex, python]  tool:[tkinter]  concept:[mathematics]  type:[side-project]

**jardin/fantasy-draft-lottery-randomizer.md**  (5 -> 5)
  - was: asyncio, combinatorics, python, side-project, tkinter
  - now: language:[python]  tool:[asyncio, tkinter]  concept:[combinatorics]  type:[side-project]

**jardin/seo-analysis-tool.md**  (5 -> 5)
  - was: beautifulsoup, pdf, python, seo, side-project
  - now: language:[python]  tool:[beautifulsoup, pdf]  concept:[seo]  type:[side-project]

## Vocabulary Size

- Before: 86 distinct tags, 76 term pages
- After: 67 distinct tags
- Term pages to create: ['case-study', 'causal-inference', 'data-essay', 'earth-science', 'econometrics', 'economics', 'higher-education', 'operations-research', 'optimization', 'sports', 'synthetic-control', 'tool', 'web-scraping']
- Term pages now unused (candidates to delete): ['bi', 'bigquery', 'browser-automation', 'college-scorecard', 'customtkinter', 'deep-time', 'firebird', 'florida', 'higher-ed', 'kentucky', 'mariadb', 'multi-provider', 'mysql', 'nclex', 'nih', 'nih-reporter', 'oracle', 'per-diem', 'sql-server', 'tabular-editor', 'word-cloud', 'wordnet']