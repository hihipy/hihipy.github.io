# pgbd.casa: Repository Reference

This is the source repository for **pgbd.casa**, the personal portfolio of Philip Bachas-Daunert. It is a Hugo + Blowfish static site deployed via GitHub Pages.

This README is written for AI assistants and future contributors who need to be productive on the codebase quickly. It documents what the site is, how it is structured, every non-default decision, every quirk encountered during development, and the exact templates required to extend it. It is dense by design.

---

## 1. Site Facts

| Property | Value |
|---|---|
| Live URL (canonical) | `https://pgbd.casa` |
| Live URL (redirect alias) | `https://pgbd.us` (→ redirects to `pgbd.casa`) |
| Repository | `github.com/hihipy/hihipy.github.io` |
| Hosting | GitHub Pages (via `CNAME` in `static/`) |
| Build | Hugo, vendored via theme submodule |
| Hugo | Extended edition, recent stable release |
| Theme | Blowfish |
| Site language | `en` |
| Default appearance | `dark`, with auto-switch enabled |
| Color scheme | `github` |
| Author | Philip Bachas-Daunert (handle: `hihipy`, email contact uses `pgbd.kipol@passmail.net`) |

### Why two URLs?

The site has two domains pointing at the same content:

- **`pgbd.casa`** is the canonical (primary) URL. It carries the casa metaphor in the URL itself, matches the site's brand identity, and is what visitors see in the URL bar after any redirect.
- **`pgbd.us`** is a redirect alias registered through Cloudflare. It exists as a fallback for visitors whose networks block newer/uncommon TLDs. The `.us` ccTLD is more universally accepted by enterprise security filters than `.casa`. The Cloudflare zone for `pgbd.us` performs a 301 redirect of all traffic (path-preserving, query-string-preserving) to `https://pgbd.casa`.

**Use `pgbd.us`** in venues where universal accessibility matters more than brand:
- LinkedIn profile (Contact info → Website)
- Email signature
- Résumé
- Job application URL fields
- Cold outreach where the recipient's network is unknown

**Use `pgbd.casa`** in venues where brand identity matters more than universal access:
- The site's own self-references (anywhere it's linked from itself)
- Personal communications and GitHub repos
- Casual social media

The user experience: a recruiter clicking `pgbd.us` from LinkedIn lands at `pgbd.casa` after a brief 301 redirect. The URL bar updates to show `.casa`. Most visitors won't notice; those who do see a Spanish-named domain consistent with the casa metaphor.

### Cloudflare configuration for `pgbd.us`

The `pgbd.us` zone is configured in Cloudflare to 301-redirect all traffic to `https://pgbd.casa`. The redirect preserves both path and query string, covers both apex and `www`, and is enforced over HTTPS via Cloudflare's Universal SSL.

If the redirect needs to be modified, the rule lives in the `pgbd.us` zone under Rules → Redirect Rules. SSL/TLS settings are under SSL/TLS → Overview. Account security for the Cloudflare account itself is documented in §15.

---

## 2. The Casa Metaphor

The site is organized as a "digital casa" (Spanish for "house"). Each top-level navigation entry is a "room" with a Spanish name. This is a deliberate brand element, not decoration. Do not change it without explicit instruction.

The home page lead is a rotating typing animation (Blowfish `{{< typeit >}}` shortcode wrapped inside `{{< lead >}}`, looping with `breakLines=false`) that cycles through four languages: Spanish (`Mi Casa Digital es Su Casa Digital`, canonical and matched by the site's `description` meta tag), English (`My Digital Home is Your Digital Home`), Catalan (`La Meva Casa Digital és La Teva Casa Digital`), and Greek (`Το Ψηφιακό Σπίτι μου είναι Το Ψηφιακό Σπίτι σου`). All four use the same casing rule (see §7). Spanish and English reflect citizenship (Spain and U.S. respectively); Catalan and Greek reflect heritage. The welcome paragraph immediately below the lead names all four connections explicitly.

This pattern extends to all twelve room landing pages. Each `{{< lead >}}` contains a typing animation cycling a short page-purpose tagline through the same four languages in the same order. Each tagline describes what is actually on the page, not the room name itself, so a visitor who lands on cocina or estudio without context understands what they are looking at. The taglines are: puerta cycles `Mi Currículum / My Résumé / El Meu Currículum / Το Βιογραφικό μου`; sala cycles `Mi Trayectoria / My Background / La Meva Trajectòria / Το Υπόβαθρό μου`; mirador cycles `Mi Filosofía de Dashboards / My Dashboard Philosophy / La Meva Filosofia de Dashboards / Η Φιλοσοφία μου για Dashboards`; taller cycles `Mi Dashboard / My Dashboard / El Meu Dashboard / Το Dashboard μου`; obrador cycles `Mi Filosofía de Herramientas / My Tool-Building Philosophy / La Meva Filosofia d'Eines / Η Φιλοσοφία μου για τα Εργαλεία`; cocina cycles `Mis Pipelines de Datos / My Data Pipelines / Els Meus Pipelines de Dades / Τα Pipelines Δεδομένων μου`; estudio cycles `Mis Experimentos con IA / My AI Experiments / Els Meus Experiments amb IA / Τα Πειράματά μου με AI`; garaje cycles `Mis Utilidades de Analista / My Analyst Utilities / Les Meves Utilitats d'Analista / Τα Εργαλεία Αναλυτή μου`; jardín cycles `Mis Proyectos Personales / My Side Projects / Els Meus Projectes Personals / Τα Προσωπικά Έργα μου`; despacho cycles `Mis Ensayos de Datos / My Data Essays / Els Meus Assajos de Dades / Τα Δοκίμια Δεδομένων μου`. The biblioteca and archivo taglines follow the same four-language pattern and live in their respective `_index.md`; transcribe them here when reconciling. Greek possessive clitics (`μου`) stay lowercase per native convention; Greek proparoxytone words (`Πειράματα`, `Υπόβαθρο`) take the secondary accent when followed by the clitic (`Πειράματά μου`, `Υπόβαθρό μου`).

On puerta and sala, the previous static lead content (résumé explainer and professional summary respectively) is preserved as a regular paragraph immediately below the new animated lead. The puerta page also drops the redundant separate download button, since the inline PDF embed has its own download control in the browser-native PDF toolbar.

The metaphor is the differentiator. When in doubt, choose the option that strengthens the casa framing rather than the conventional portfolio framing.

The casa metaphor extends to the 404 page, which uses casa language ("No room here. The hallway you walked down doesn't lead anywhere"). See §9.

---

## 3. Room Inventory

Twelve rooms total, organized as four practice areas bracketed by two entry pages. Entry: puerta, sala. Dashboards: mirador (philosophy) and taller (applied). Case studies: biblioteca (philosophy) and archivo (applied). Tooling: obrador (philosophy) and four project rooms (cocina, estudio, garaje, jardín). Data essays: despacho.

| Room | Path | Title (Title Case) | Role |
|---|---|---|---|
| `puerta` | `/puerta/` | Résumé PDF | Door, entry point. Terminal page that embeds `static/resume.pdf`. |
| `sala` | `/sala/` | About Me | Living room, about page. Terminal page with long-form bio (Experience / Education / Certifications / Skills). |
| `mirador` | `/mirador/` | Dashboard Philosophy | Lookout, methodology room. Holds dashboard design philosophy and methodology essays. Not a project room. |
| `taller` | `/taller/` | Built Dashboard | Workshop, applied room. Holds a worked dashboard example built from public data. Not a project room. |
| `biblioteca` | `/biblioteca/` | Case Study Philosophy | Library, methodology room. Holds case-study philosophy: sourcing, reproducibility, peer review. Not a project room. |
| `archivo` | `/archivo/` | Case Studies | Archive, applied room. Holds phased case-study walkthroughs from source to findings. Not a project room. |
| `obrador` | `/obrador/` | Tool-Building Philosophy | Craft workshop, methodology room. Holds tool-building philosophy: when to automate, how to work with AI, identifier protection. Not a project room. |
| `cocina` | `/cocina/` | Data Prep & ETL | Kitchen, data preparation tools. |
| `estudio` | `/estudio/` | AI & Experiments | Studio, AI-augmented analytics tools. |
| `garaje` | `/garaje/` | Analyst Utilities | Garage, Excel macros, calculators, processing scripts. |
| `jardin` | `/jardín/` | Side Projects | Garden, personal projects and miscellaneous experiments. |
| `despacho` | `/despacho/` | Data Essays | Study/home-office, content room. Holds long-form, sourced data essays that reason with data. Not a project room. |

Room symbol rationale: room pages have **no** decorative symbol prefix. The terminal-prompt path (`~/sala`, `~/cocina`, etc.) is the room identity; an additional symbol prefix is redundant decoration. The site went through three iterations on this. First, mixed Unicode glyphs (`◰ § ⛁ ✦ ⛭ ❀`), visually distinct but five of six were not in MonoLisa and rendered via system font fallback (BUG-013 in its original form). Second, Greek capitals (`Π Σ Δ Ψ Ω Φ`), fully present in MonoLisa with a defensible thematic mapping (Σαλόνι, Δεδομένα, golden ratio in plant biology). Third, none: the realization that the Greek letters were redundant decoration in front of already-distinctive paths, and that the homepage `⛫` castle was doing the symbolic work for the entire site without needing per-room reinforcement. The terminal-prompt format alone is the room identity. The homepage `⛫` (castle) is the brand anchor and remains the only symbolic glyph on the site. Anyone tempted to add per-room symbols back should weigh the symbolic redundancy against the visual flourish; previous iterations are documented for reference but were removed deliberately.

**Home page order (intentional):** Five sections separated by H2 headers, ordered to build toward the strongest work for a job-portfolio reader. *Who I Am* contains `puerta`, `sala` (puerta first because the metaphor is "visitor walks through the door first"). *Tooling* contains `obrador` first (the methodology room) followed by the four project rooms alphabetically (`cocina`, `estudio`, `garaje`, `jardín`). *Dashboards* contains `mirador`, `taller`. *Case Studies* contains `biblioteca`, `archivo`. *Data Essays* contains `despacho`. Within each practice area the philosophy room precedes the applied room. This structure is non-negotiable; do not reorder without instruction.

Counts are NOT listed in this table by design. The four project rooms render their counts dynamically via the `section-count` shortcode, `archivo` via `case-study-count`, and `despacho` via `essay-count` (see §9), so manual counts here would be a maintenance burden and a source of drift. For the actual contents of each room, see §4.

---

## 4. Project Pages: Complete Inventory

Listed in alphabetical order within each room (matches Hugo render order, see §8).

### `/cocina/`

| Filename | Title | Summary (card label) |
|---|---|---|
| `25live-cleaner.md` | 25live-cleaner | Cleans 25Live calendar exports. |
| `brimr-downloader.md` | brimr-downloader | Downloads NIH funding rankings. |
| `qualtrics-processing-pipeline.md` | qualtrics-processing-pipeline | Cleans Qualtrics survey data. |
| `qualtrics-report-generator.md` | qualtrics-report-generator | Renders Qualtrics surveys as HTML. |

### `/estudio/`

| Filename | Title | Summary |
|---|---|---|
| `ai-csv-profiler.md` | ai-csv-profiler | CSV profiler for LLMs. |
| `decode-for-humans.md` | decode-for-humans | AI source-code translator. |
| `linkedin-banner-wordcloud-generator.md` | linkedin-banner-wordcloud-generator | AI résumé wordcloud generator. |
| `sql-x-ray.md` | sql-x-ray | SQL schema dump for LLMs. |

### `/garaje/`

| Filename | Title | Summary |
|---|---|---|
| `excel-vba-toolkit.md` | excel-vba-toolkit | Reusable Excel VBA macros. |
| `expense-report-review-calculator.md` | expense-report-review-calculator | Flags late expense submissions. |
| `foreign-per-diem-calculator-for-usa-based-institutions.md` | foreign-per-diem-calculator-for-usa-based-institutions | International per diem calculator. |
| `pbi-model-export.md` | pbi-model-export | Power BI to AI-ready JSON. |
| `timeline-of-events-business-days.md` | timeline-of-events-business-days | Process timeline with gap detection. |

### `/jardin/`

| Filename | Title | Summary |
|---|---|---|
| `ascii-username-generator.md` | ascii-username-generator | ASCII usernames in 19 languages. |
| `dialogorithm.md` | dialogorithm | Phone numbers as PhD math. |
| `fantasy-draft-lottery-randomizer.md` | fantasy-draft-lottery-randomizer | Auditable fantasy draft lottery. |
| `seo-analysis-tool.md` | seo-analysis-tool | SEO analyzer with teaching reports. |

---

## 5. The Three-Tier Complexity Gradient

Every project page exposes three distinct text fields, each targeting a different audience and reading depth. Understanding this gradient is essential for editing existing pages or writing new ones.

| Tier | Field | Length | Audience | Where it appears |
|---|---|---|---|---|
| 1 | `summary` (frontmatter) | 3-6 words | Recruiter scanning room | As card label on `/<room>/` listing AND in search results |
| 2 | `{{< lead >}}` block | 12-20 words | HR/recruiter on the page itself | At the very top of the project page body |
| 3 | `description` (frontmatter) | 30-50 words | Search engines, social previews | `<meta name="description">` and Open Graph tags |
| 4 | Body content | 1500-3500 words | Reader who clicked in deliberately | Below the lead block |

The three written fields are NOT redundant. Each serves a different function and CANNOT be auto-derived from the others. Tier 1 is for scanability. Tier 2 is for "should I read this page or move on." Tier 3 is for SEO and link previews. Tier 4 is for actual technical depth.

When asked to add a new project, all four tiers must be authored deliberately.

**Tag accuracy is non-negotiable.** Tags should reflect what the project's source code actually imports, uses, or implements; they should NOT reflect skills the author has elsewhere. A Python project that does not actually use NumPy should not be tagged `numpy` even if the author is fluent in NumPy. The biblioteca philosophy of reproducibility-as-the-floor applies to portfolio claims as much as to case study numbers: a recruiter who clicks the `numpy` tag and reads the project should find numpy code. Skills the author has but the portfolio does not yet demonstrate belong on `~/sala` (the bio page), not in project frontmatter. When auditing tags on an existing project, run `grep -E "^import|^from" project_file.py` against the real source code; the resulting list of actual imports is the canonical tag inventory for that project.

**Skill name consistency.** When a skill appears on `~/sala` AND as a project tag, the casing must match between the two. The project tag map in `layouts/partials/article-link/card.html` is the canonical source: if the map says `nltk` -> `NLTK`, then sala should write `NLTK` (not `nltk` or `Nltk`). Update both at once when adding new skills.

**Important: `summary` also drives search result quality.** If `summary` is missing from a page's frontmatter, Blowfish's search index falls back to Hugo's auto-generated summary (the first ~70 words of body content). This produces noisy, bloated search results. Every page that is discoverable via search SHOULD have a `summary` field, including non-project pages (home, sala, puerta). See BUG-010.

---

## 6. Project Page Template

Every project page must follow this exact structure. The order of sections matters; do not rearrange without explicit instruction.

```markdown
---
title: "<repo-name>"
weight: <N>   # see §8 for weight conventions
description: "<30-50 word SEO description>"
summary: "<3-6 word card label>"
tags: ["tag1", "tag2", "tag3"]
showDate: false
showReadingTime: true   # Hugo auto-estimate; surfaced on cards too. See §10 for exceptions.
showAuthor: false
---

{{< katex >}}   # ONLY if the page contains math expressions; OMIT if not

{{< lead >}}
<12-20 word elevator pitch, plain English, HR-friendly>
{{< /lead >}}

## At a Glance

<Conversational opener, 2-3 paragraphs, sets up the problem before describing the solution.>

## The Problem

<Concrete examples of the friction the tool addresses. Recruiter-readable.>

## The Approach

<High-level architecture description. Include a Mermaid diagram if the data flow is non-trivial.>

## Walking Through

<Section per capability with before/after examples. This is where domain readers verify competence.>

## Why <X> Matters

<Variable section name. Replace X with the design philosophy of the project. Examples: "Why The Audit Log Matters", "Why Multi-Provider Architecture Matters". This section explains the design choice that distinguishes the project from a generic implementation.>

## Under The Hood

{{< accordion mode="collapse" separated="true" >}}
{{< accordionItem title="<Technical detail 1>" >}}
<Body of accordion item 1>
{{< /accordionItem >}}
{{< accordionItem title="<Technical detail 2>" >}}
<Body of accordion item 2>
{{< /accordionItem >}}
{{< accordionItem title="<Technical detail 3>" >}}
<Body of accordion item 3>
{{< /accordionItem >}}
{{< /accordion >}}

## Stack

- **Language:** <Python | Excel/VBA | C# | etc.>
- **Libraries:** <list>
- **Output format:** <CSV, PDF, JSON, etc.>

## Repo

[github.com/hihipy/<repo-name>](https://github.com/hihipy/<repo-name>)
```

### CRITICAL ordering rule for KaTeX pages

If a page uses math (`{{< katex >}}` is present), the katex shortcode MUST come BEFORE the `{{< lead >}}` block. See BUG-003 in §10.

```markdown
{{< katex >}}        # FIRST

{{< lead >}}         # SECOND
...
{{< /lead >}}

## At a Glance       # THIRD
```

NOT this order:

```markdown
{{< lead >}}         # ❌ WRONG
...
{{< /lead >}}

{{< katex >}}        # ❌ WRONG — breaks lead rendering

## At a Glance
```

---

## 7. Tone and Style Conventions

These are established conventions across all 16 project pages. Match them when authoring new content.

| Rule | Notes |
|---|---|
| **No em dashes** | Use commas, parens, colons, semicolons, or restructure. The em dash is on the AI-tells list. |
| **No "delve," "comprehensive," "in summary," "moreover," "furthermore"** | All on the AI-tells list. |
| **Title Case for headings** | "Data Prep & ETL", "AI & Experiments", "Side Projects". |
| **Body and most headings: Atkinson Hyperlegible** | Sans-serif designed by the Braille Institute for low-vision and dyslexic readers. Loaded from `static/fonts/AtkinsonHyperlegible-{Regular,Bold,Italic,BoldItalic}.woff2`. Switched from MonoLisa Italic + SS02 cursive in BUG-016. |
| **Page titles (H1) and typing animations: MonoLisa upright** | Terminal-prompt strings like `Σ ~/sala  # About Me` and the {{< typeit >}} animations keep the monospace look. Upright (not italic) is fine for short strings; italic cursive was the dyslexia barrier. |
| **Code blocks: MonoLisa upright with ligatures** | Unchanged; code retains identity-defining typography. |
| **Sentence case for descriptions and body prose** | "Cleans messy data exports." not "Cleans Messy Data Exports." |
| **Title case for the home page typing animation** | Content words capitalized, verbs/copulas lowercase. Applies across all four languages in the rotation: `es` (Spanish), `is` (English), `és` (Catalan), `είναι` (Greek) all stay lowercase. Greek exception: possessive clitics `μου` and `σου` also stay lowercase per native convention (they follow the noun and aren't capitalized mid-sentence even in display text). See §2 for the full phrases. |
| **Audience: HR/recruiter with bachelor's degree, no coding background** | Avoid jargon in leads and summaries. Domain terms acceptable in body. |
| **Conciseness over completeness** | Tighter is better. The reader can scroll for more. |
| **Mention Miller School only when project genuinely connects** | Not as decoration. |
| **No invented content, no redundancy** | If two fields say the same thing, one of them is wrong. |
| **Backticks for inline code/paths** | `~/sala`, `Path.glob()`, `summaryLength = 70`. |

---

## 8. Frontmatter Conventions

### Required fields on every project page

```yaml
title: "<exact-repo-name>"     # matches GitHub repo name and filename stem
weight: <multiple of 10>       # see weight rules below
description: "<30-50 word SEO description>"
summary: "<3-6 word card label>"
tags: ["..."]
showDate: false
showReadingTime: true
showAuthor: false
```

### Weight conventions

Pages within a room are sorted alphabetically by enforcing weights in alphabetical order: `10, 20, 30, 40, 50, ...`. This requires `orderByWeight = true` in `params.toml` (see §11). When adding a new project to a room:

1. Sort existing files alphabetically including the new one.
2. Re-assign weights `10, 20, 30, ...` in order.

### Field role reminders

| Field | Used for |
|---|---|
| `title` | H1 of the page; also used as alphabetical sort key when no weight is set |
| `weight` | Hugo section list ordering |
| `description` | `<meta name="description">`, Open Graph, Twitter card |
| `summary` | Card label on the room landing page AND search result snippet |
| `tags` | Currently unused for navigation but indexed; reserve for future tag pages |
| `showDate`, `showAuthor` | Both `false` to keep pages stripped of clutter |
| `showReadingTime` | `true`: surfaces Hugo's auto-estimated reading time on cards ("10 mins") and on the page itself. The only `true` of the three; see BUG-030 for the §8/§6 drift that previously documented this as `false` |

### Forbidden in frontmatter

- `date`: not set anywhere; presence triggers reverse-chronological sort fallback
- `lastmod`: handled automatically by `enableGitInfo`
- `draft: true`, never used; commit only when ready

---

## 9. Custom Infrastructure

### `layouts/404.html`

Custom 404 page in casa style. Renders:

- Title in terminal format: `~/404 # Not Found`
- Casa-flavored copy: "No room here. The hallway you walked down doesn't lead anywhere..."
- Keyboard shortcut hint: press `/` to open Blowfish's built-in search modal
- Link back to the home page. The 404 no longer mirrors the room list, to eliminate maintenance drift; the home page is the single source of truth.
- Inherits Blowfish's `baseof.html` (header with search, footer, dark-mode toggle, fonts)

GitHub Pages automatically serves `/404.html` (which Hugo generates from this layout) for any unmatched URL.

### `layouts/shortcodes/section-count.html`

Auto-counts pages in a section and renders `(N Project)` or `(N Projects)` with proper pluralization. Used on the home page next to project room links.

### `layouts/shortcodes/case-study-count.html`

Same mechanism as `section-count`, pluralizing as `(N Case Study)` / `(N Case Studies)`. Used on the home page next to the `archivo` room link.

### `layouts/shortcodes/essay-count.html`

Same mechanism, pluralizing as `(N Essay)` / `(N Essays)`. Used on the home page next to the `despacho` room link. Added May 2026 with the despacho room. The three count shortcodes are near-identical and differ only in the pluralized noun; a future cleanup could consolidate them into one parameterized shortcode taking the noun as a second argument.

### `layouts/shortcodes/swatch.html`

Renders an inline color swatch (small colored square) followed by the hex code in monospace. Used in `~/mirador` to make the named palettes actually viewable as colors rather than as bare hex strings the reader has to mentally translate.

Usage: `{{< swatch "#E69F00" >}}`. Pass the hex value with leading `#` as the first positional argument. The shortcode emits a 0.85em colored square with a faint inset border (so very light colors stay visible against light backgrounds) followed by the hex code in a `<code>` tag.

**Color naming convention.** When a color in mirador needs a name (palette entries, recommended pairings), the name comes from [chir.ag's Name That Color](https://chir.ag/projects/name-that-color/) tool. The format on the page is: swatch shortcode, then linked color name, then hex in parens, e.g. `{{< swatch "#56B4E9" >}} [Picton Blue](https://chir.ag/projects/name-that-color/#56B4E9) (#56B4E9)`. The link points to chir.ag with the hex as URL fragment (uppercase, no `#` in the URL itself; the fragment marker is the literal `#` separator). The link text MUST match what chir.ag's live tool actually returns for that hex; do not transcribe a name from a search result or a port of the ntc.js algorithm, since neither reliably matches the live tool's output. Verify by clicking the chir.ag link and reading the name from the live page. This convention exists so the page's prose stays in sync with the link target; a reader who clicks "Picton Blue" should land on a page that confirms it's Picton Blue, not Sky Blue or anything else.

```go-html-template
{{- /*
  section-count: returns the number of pages in a content section.

  Pass the section name as the first argument. The output is wrapped
  in parentheses with proper pluralization: a single page returns
  "(1 Project)", any other count returns "(N Projects)".

  Counts regular pages only; section _index.md files are excluded.
*/ -}}
{{- $section := .Get 0 -}}
{{- $pages := where (where .Site.RegularPages "Section" $section) "Kind" "page" -}}
{{- $count := len $pages -}}
{{- if eq $count 1 -}}
({{ $count }} Project)
{{- else -}}
({{ $count }} Projects)
{{- end -}}
```

**Invocation:** `{{< section-count cocina >}}` takes an unquoted single-token argument. See BUG-001 for why.

### `layouts/partials/header.html` and `footer.html`

Existing Blowfish overrides. Their content is project-specific and should not be modified without inspection.

### `layouts/partials/article-link/card.html`: card layout and inline tag map

Custom Blowfish override. Renders project cards with the tags row at the bottom, applying a display-time formatting map that converts lowercase-kebab-case frontmatter tags to their proper display casing **on room landing pages**. Frontmatter tags stay lowercase (clean URLs, easy alphabetization); the map at runtime produces `JSON`, `PostgreSQL`, `Power BI`, `CustomTkinter`, and so on as the inline pills under each project card.

**Important:** this map ONLY controls tag display on room cards. The search modal, the tag taxonomy term pages (`/tags/sql/`, `/tags/mysql/`, etc.), and the breadcrumbs on those term pages use a separate display path that comes from `content/tags/<tag>/_index.md` files. See the next subsection. Both sources of truth must stay in sync. See BUG-031 for what happens when they drift.

**Tag map currently covers** (alphabetical):

`ai`, `api`, `asyncio`, `audit`, `beautifulsoup`, `bigquery`, `bi`, `browser-automation`, `calculator`, `cnn`, `college-scorecard`, `combinatorics`, `csharp`, `csv`, `ctes`, `customtkinter`, `data-analysis`, `data-cleaning`, `data-profiling`, `data-quality`, `datasette`, `dax`, `documentation`, `etl`, `excel`, `exploratory-analysis`, `finance`, `firebird`, `florida`, `higher-ed`, `html`, `json`, `jupyter`, `kentucky`, `latex`, `llm`, `logistic-regression`, `macros`, `mariadb`, `mathematics`, `matplotlib`, `ml-models`, `multi-provider`, `mysql`, `nclex`, `nih`, `nih-reporter`, `nlp`, `nltk`, `nursing-education`, `oracle`, `pandas`, `pdf`, `per-diem`, `postgresql`, `power-bi`, `predictive-modeling`, `process-improvement`, `public-data`, `python`, `qualtrics`, `r`, `reporting`, `schema-design`, `selenium`, `seo`, `side-project`, `sql`, `sql-server`, `sqlite`, `sqlite-utils`, `survey-data`, `tabular-editor`, `tkinter`, `travel`, `vba`, `window-functions`, `word-cloud`, `wordnet`

**Fallback for missing tags:** any frontmatter tag NOT in the map renders via `{{ replace $tag "-" " " | title }}`. Hyphens become spaces and the result is title-cased. A future tag like `machine-learning` renders correctly as "Machine Learning" without a map update. Single-word tags without map entries also render via `title` (e.g., a future `kotlin` renders as `Kotlin`).

**When to add a map entry:** when the fallback produces something wrong. The fallback breaks on acronyms (`json` → `Json`, should be `JSON`), proper-cased brand names (`postgresql` → `Postgresql`, should be `PostgreSQL`), and library names that style themselves in non-title-case (`pandas` stays lowercase; `BeautifulSoup` uses internal capitals). Multi-word tags that title-case correctly (`Side Project`, `Power BI`) work via the fallback but are added to the map anyway for explicitness, so the map serves as the single source of truth for tag display on cards.

**Where it lives:** the map is a `dict` literal inside the `{{ with .Params.tags }}` block of `layouts/partials/article-link/card.html`. It's the only customization in an otherwise-vanilla Blowfish card template, so future Blowfish theme updates can be applied by re-pulling card.html and re-adding the map.

### `content/tags/<tag>/_index.md`: taxonomy term pages and search-index display

Per-tag content files that set the canonical title used by the tag taxonomy term pages (`/tags/sql/`, `/tags/mysql/`, and so on), the search modal results, and the breadcrumbs on those term pages. Each file is four lines of frontmatter:

```yaml
---
title: "SQL"
---
```

**Why these files exist:** Hugo auto-generates a term page for every unique tag used in any page's `tags:` array. The page's `.Title` defaults to `humanize` of the slug, which produces "Sql", "Mysql", "Sql-Server" and so on. The search index (`/index.json`) reads `.Title` directly, so the search modal shows the auto-humanized title regardless of what `card.html` does. The fix is to set `.Title` explicitly in a content file. See BUG-031.

**One file per tag in use.** As of May 2026 there are 74 such files, one for every tag referenced by at least one frontmatter `tags:` array across all 32 pages with tags (17 project pages + 15 archivo case-study phase pages). Tags that exist only in the `card.html` map but are not yet used by any page do not need a content file, because Hugo only generates a term page when at least one content page references the tag.

**Two sources of truth, kept in sync.** The display title for a tag now lives in two places: the `card.html` map (for room-card pills) and the `content/tags/<tag>/_index.md` file (for taxonomy pages, search, breadcrumbs). They must agree. When introducing a new tag, update both at once. The long-term fix is to move both behind a single `data/tagmap.toml` file that both `card.html` and a custom term layout read from; until then, the dual-update discipline is the contract.

**Regenerating the files.** A `tools/create_tag_term_pages.py` script (root of the repo) reads a canonical list of tag-to-title mappings and creates/rewrites every `_index.md` to match. It is idempotent: re-running it only touches files whose title disagrees. Run it after adding a new tag (after also updating the canonical list inside the script).

### `assets/icons/`: 25 custom SVGs

Used primarily by `content/sala/index.md` (about page) and a few project pages. Inventory:

`book, book-open, briefcase, building-columns, bullhorn, calculator, certificate, chart-bar, chart-line, clipboard-check, coins, compass, earth-americas, file-pen, flask, house, landmark, lightbulb, magnifying-glass, microscope, network-wired, pen-nib, school, server, vial`

21 are referenced in content. 4 are unused (`building-columns`, `certificate`, `compass`, `house`) but kept available.

**Usage in markdown:** `{{< icon "calculator" >}}` (this shortcode is provided by Blowfish theme).

### `assets/css/custom.css`

Custom CSS overrides, roughly 5KB. Concerns:

1. Atkinson Hyperlegible `@font-face` declarations (Regular, Italic, Bold, BoldItalic, all woff2 self-hosted from `static/fonts/`)
2. MonoLisa `@font-face` declaration (variable, upright only; italic was retired in BUG-016)
3. Body and most headings (h2-h6) use Atkinson sans-serif for readability; H1 page titles and typeit animations use MonoLisa upright to preserve terminal-prompt aesthetic; code blocks use MonoLisa upright with ligatures
4. `white-space: nowrap !important` on Blowfish badge spans: prevents date ranges from breaking ugly across lines
5. Mermaid diagrams and figures centered with auto margins
6. Mobile timeline overflow fix at `@media (max-width: 640px)`, see BUG-012
7. Mobile typing-animation lead font shrink + min-height to prevent bounce, see typing animation work in §2
8. Markdown tables centered with `width: fit-content` + auto margins, and cells center-aligned, see BUG-038

Inspect before modifying; every rule has a reason.

### `assets/img/favicon-source.svg`

Canonical SVG source for the favicon set. Donut chart in Blowfish github palette: primary blue (`#0969da`), light blue tint (`#54aeff`), neutral gray (`#656d76`). Three segments at 50/30/20 percent with 4-degree gaps. The PNG/ICO files in `static/` are derived from this source. To regenerate the full favicon pack from this SVG, see §13.

---

## 10. Bug Catalog (BUG-NNN format)

Hugo and Blowfish quirks discovered during development. Reference these when AI-troubleshooting render issues.

### BUG-001: Smartypants converts straight quotes to curly inside markdown body

**Symptom:** Shortcode invocations like `{{< section-count "cocina" >}}` render as literal text instead of executing.

**Cause:** Hugo's smartypants module processes markdown body content and converts straight ASCII double quotes (`"` U+0022) to typographic open/close quotes (`“` U+201C, `”` U+201D). The shortcode parser only recognizes straight quotes, so the conversion makes the shortcode unparseable.

**Workaround:** Use unquoted single-token arguments where possible.

```markdown
✅ {{< section-count cocina >}}
❌ {{< section-count "cocina" >}}
```

This works for any argument that is a single word with no spaces or special characters. Section names, room names, and identifiers all qualify.

For arguments that require spaces (or quotes for any reason), the alternative is to disable smartypants in `markup.toml`, but this affects all body content, which is undesirable for a portfolio site where résumé/résumés should still get smart quotes.

### BUG-002: Hugo template comments parse `*/` as terminator inside `{{- /* */ -}}`

**Symptom:** Template parse error `comment ends before closing delimiter` even though the comment block has matching `{{- /*` and `*/ -}}`.

**Cause:** Go's text/template parser scans for the literal sequence `*/` to terminate the comment, with no escape mechanism. If the comment body contains `*/` for any reason (such as an embedded shortcode example using `{{</* ... */>}}` notation), the parser ends the comment early, then chokes on the rest.

**Workaround:** Never embed shortcode example syntax in `{{- /* */ -}}` block comments. Use plain prose for documentation. If you must show example syntax, use markdown comments or HTML comments outside the template comment.

### BUG-003: `{{< katex >}}` adjacent to `{{< lead >}}...{{< /lead >}}` breaks rendering

**Symptom:** On project pages with both shortcodes, the lead block fails to render; the closing `{{< /lead >}}` shows as literal text in the body, KaTeX expressions later on the page render as raw `\(...\)` source.

**Cause:** Specific interaction between Hugo's shortcode parser and the paired-vs-standalone shortcode arrangement. The bug is triggered when a paired block (`{{< lead >}}...{{< /lead >}}`) is immediately followed by a standalone shortcode (`{{< katex >}}`) with only blank lines between them, before any prose content.

**Workaround:** Place `{{< katex >}}` BEFORE the lead block, immediately after the frontmatter, not after.

```markdown
✅ {{< katex >}}

   {{< lead >}}
   ...
   {{< /lead >}}

   ## At a Glance

❌ {{< lead >}}
   ...
   {{< /lead >}}

   {{< katex >}}

   ## At a Glance
```

This affects 7 of the 16 project pages currently:
- `cocina/25live-cleaner.md`
- `cocina/qualtrics-processing-pipeline.md`
- `estudio/ai-csv-profiler.md`
- `garaje/foreign-per-diem-calculator-for-usa-based-institutions.md`
- `garaje/pbi-model-export.md`
- `jardin/dialogorithm.md`
- `jardin/fantasy-draft-lottery-randomizer.md`

### BUG-004: Mermaid 11.x requires double-quoted node labels

**Symptom:** Mermaid diagrams fail to render with parse error when node labels contain parentheses.

**Cause:** Mermaid 11.x is stricter about node label parsing. Bare-text labels with special characters (parens, brackets, slashes) are rejected.

**Workaround:** Wrap ALL node labels in double quotes.

```mermaid
✅ flowchart TD
   A["Read input file"] --> B["Parse rows (one per event)"]
   B --> C["Write output"]

❌ flowchart TD
   A[Read input file] --> B[Parse rows (one per event)]
   B --> C[Write output]
```

This applies to every Mermaid diagram in the codebase. New diagrams must follow this convention.

Mermaid is enabled per-page via `mermaid = true` in `params.toml` `[article]` block, and invoked via `{{< mermaid >}}...{{< /mermaid >}}` shortcode (NOT triple-backtick code blocks; that's a different render path that doesn't work with Blowfish's setup).

### BUG-005: Mobile rendering issue with U+2699 gear icon

**Symptom:** Gear icon `⚙` renders as a colored emoji on iOS Safari (and in some MonoLisa font fallbacks), breaking the typographic consistency of room symbols.

**Cause:** U+2699 (`⚙`) is in Unicode's emoji-presentation table. Mobile browsers and some fonts render it with emoji presentation by default, which displays it as a colored multi-pixel glyph rather than a monospace text character.

**Workaround:** Use U+26ED (`⛭` GEAR WITHOUT HUB) instead. This codepoint is NOT in the emoji-presentation table, so it renders as a pure typographic glyph everywhere.

The site originally tried `⚙` followed by U+FE0E (TEXT VARIATION SELECTOR) as the workaround, but this still fails when the font lacks a text-style glyph for U+2699. The U+26ED swap is the reliable fix.

### BUG-006: `enableGitInfo = true` + `orderByWeight = false` produces reverse-chronological sort

**Symptom:** Project rooms display projects in order of git commit date (newest first) instead of alphabetically.

**Cause:** With `enableGitInfo = true` in `hugo.toml`, Hugo populates each page's `.Lastmod` field from git history. Blowfish's section list templates fall back to `.Lastmod` for sorting when `orderByWeight = false` and no `date` field is set.

**Fix applied:** Set `orderByWeight = true` in `params.toml` `[list]` section, and assign `weight` values to all project pages.

### BUG-007: `summaryLength = 0` in hugo.toml disables card summary rendering

**Symptom:** Card listings on room landing pages show only the title, with no description text.

**Cause:** Hugo's auto-summary generation requires `summaryLength` to be a positive integer. With `summaryLength = 0`, Hugo generates empty auto-summaries, and Blowfish's card template falls through to using nothing.

**Fix applied:** Set `summaryLength = 70` in `hugo.toml`. This makes Hugo generate auto-summaries from the first 70 words of body content. However, frontmatter `summary` field always takes priority when present (which it is on all project pages).

### BUG-008: Hugo dev server cache occasionally serves stale output

**Symptom:** After a config change or rapid frontmatter edits across many files, the dev server continues serving old rendered output even though the source files are correct.

**Cause:** Hugo's file watcher debounce can drop file change events when many files are modified simultaneously. Config changes (especially to `hugo.toml`) sometimes do not auto-restart cleanly.

**Workaround:** Stop the dev server (Ctrl+C) and restart it manually after batch edits or config changes. The fresh start clears the cache.

### BUG-009: Bar chart favicon reads as cellular signal strength

**Symptom:** Original favicon (three vertical ascending bars) was visually ambiguous, reading as a cellular signal indicator rather than data analytics.

**Cause:** Vertical bars of uniformly increasing height are the universal symbol for cellular signal strength in mobile UIs (status bar icons). The bar chart shape, while semantically correct for "data analytics," is visually overloaded.

**Fix applied:** Replaced with a donut chart design (three segments: 50%, 30%, 20% with 4-degree gaps) using the Blowfish github color palette. The donut shape has no competing semantic interpretation and reads unambiguously as analytics. Source SVG at `assets/img/favicon-source.svg`. Generated PNG/ICO files at the standard locations in `static/`.

### BUG-010: Search index uses Hugo auto-summary when `summary` field is missing

**Symptom:** Search results for non-project pages (home, sala, puerta) showed bloated descriptions: full paragraphs of body content, embedded HTML fallback text from PDF objects, concatenated room descriptions, etc.

**Cause:** Blowfish's search index (`index.json` output) includes a description field for each result. The field is sourced from the page's `summary` frontmatter if present, otherwise falls back to Hugo's auto-generated `.Summary` (the first ~70 words of body content). Pages without an explicit `summary` produce noisy search snippets.

**Fix applied:** Added `summary` frontmatter fields to the home page, `content/sala/index.md`, and `content/puerta/_index.md`. Project pages already had summaries from earlier work.

**Convention:** Every page that should be discoverable via search MUST have a `summary` field. This is now part of the page-creation checklist (§13).

### BUG-011: Newly-registered domains blocked by aggressive enterprise security filters

**Symptom:** A newly-registered domain (typically less than 30-90 days old) cannot be accessed from certain restrictive enterprise networks even when DNS, SSL, and routing are all correctly configured. TCP connections succeed but TLS handshake is reset by an inline security appliance.

**Cause:** Enterprise security infrastructure (Cisco Umbrella, Zscaler, Palo Alto Networks, Forcepoint, etc.) frequently maintains "newly observed domain" blocklists. Domains registered in the last 30-90 days are treated as suspicious by default until they've aged. This is independent of TLD; even `.com` and `.us` domains hit this when freshly registered.

**Diagnosis:**
- TCP connection to port 443 succeeds (`Test-NetConnection <domain> -Port 443` returns `True`)
- TLS handshake is reset (Connection was reset, ALPN negotiation fails)
- DNS resolution returns the correct origin IPs
- Site loads correctly from cellular networks, home wifi, or any non-restrictive network

**Real-world impact:** During this site's development, the University of Miami's Miller School of Medicine network blocked both `pgbd.casa` and `pgbd.us` for the first ~24 hours after their respective registrations. Both domains worked fine from non-UM networks (cellular, residential, other corporate networks tested via the whatsmydns.net global check).

**Workaround:** None for the local network. The block typically expires automatically after 30-90 days as the domain ages. Workaround for the user: access via cellular or non-restrictive network. Workaround for owners maintaining the site: do not rely on viewing the live site from highly-restrictive networks.

**Why this matters for the README:** Anyone troubleshooting connectivity from a corporate network should rule out this cause before assuming the site is broken. The first diagnostic step is always: try the URL from cellular or a different network.

### BUG-012: Blowfish timeline cards overflow viewport on mobile

**Symptom:** On viewports under ~640px (phones), timeline entries in `content/sala/index.md` overflow horizontally. The header wraps word-by-word into a tall stack, the date badge gets clipped at the right edge, and body text is cut off mid-word past the viewport.

**Cause:** Blowfish's `timelineItem.html` shortcode places the entry header and date badge inside a `<div class="flex justify-between">`. On desktop this works: title left, badge right. On mobile, the badge has `white-space: nowrap !important` (set in `custom.css` to prevent date ranges like `Apr 2023 - Mar 2025` from breaking across lines), and the heading refuses to share a line with the badge. The row demands more horizontal space than a phone viewport offers. The parent card is `flex-1` with default `min-width: auto`, so it cannot shrink below its content's natural width, and the entire card overflows, dragging body text past the right edge.

**Fix applied:** Added a mobile-only media query block to `assets/css/custom.css`:

```css
@media (max-width: 640px) {
  .shadow-2xl.flex-1.ms-6 > .flex.justify-between {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .shadow-2xl.flex-1.ms-6 {
    min-width: 0;
  }
}
```

Under 640px, this stacks header above badge and lets the card shrink below its natural content width. The `nowrap` on the badge is preserved (date ranges still don't break ugly).

The selectors target Blowfish's Tailwind utility classes (`.shadow-2xl.flex-1.ms-6` matches the timelineItem's outer card div). If upstream Blowfish ever changes those class names, this rule needs re-targeting; check `themes/blowfish/layouts/shortcodes/timelineItem.html` for the current selector.

**Coverage:** Selector-based, not page-based. Applies anywhere `{{< timelineItem >}}` is used. On `sala`, that's Experience, Education, and Certifications sections, plus any future timeline entry. No per-page work when adding entries.

### BUG-013: Five of six room symbols are not in MonoLisa's character map [RESOLVED]

**Resolution (April 2026):** Room symbols removed entirely. After two iterations (original mixed Unicode glyphs `◰ § ⛁ ✦ ⛭ ❀`, then Greek capitals `Π Σ Δ Ψ Ω Φ`), the conclusion was that the per-room symbol prefix was redundant decoration in front of already-distinctive terminal-prompt paths (`~/sala`, `~/cocina`, etc.). The Greek-letter intermediate iteration *did* eliminate the font-fallback issue (Greek capitals are fully present in MonoLisa), so it would have resolved this bug if kept. Removing the symbols entirely also resolves the bug while simplifying the visual identity. The homepage `⛫` (castle) is preserved as the single brand anchor and is the only symbol on the site that renders via system font fallback; that one instance is acceptable because the castle is the brand and is contained to a single location. Bug retained in this catalog as historical context; anyone tempted to re-introduce per-room symbols should know the constraints (must render in MonoLisa to avoid fallback inconsistency) and the reasoning for removal (symbolic redundancy with the path).

**Symptom:** The room symbols `⛫` (homepage), `⛁` (cocina), `✦` (estudio), `⛭` (garaje), and `❀` (jardín) render via system font fallback rather than from MonoLisa. Visual rendering of these glyphs varies by OS and browser depending on which fallback font supplies them. Only `◰` (puerta) and `§` (sala) are confirmed present in MonoLisa.

**Detection:** Verified by inspecting the codepoint membership of MonoLisa's character map directly:

```python
from fontTools.ttLib import TTFont
font = TTFont('static/fonts/MonoLisaVariable.woff2')
cmap = font.getBestCmap()
for c in '⛫◰§⛁✦⛭❀':
    print(c, ord(c) in cmap)
```

This requires `pip install fonttools brotli` (Brotli is needed because woff2 is brotli-compressed).

**Implications:** Mobile platforms in particular may substitute emoji-presentation variants from system fallback fonts (Apple Color Emoji, Segoe UI Symbol, Noto Sans Symbols). This is the same risk class as BUG-005, where U+2699 was swapped to U+26ED to escape emoji presentation. The five fallback-rendered symbols are sitting in this risk zone today.

**Status:** Not currently fixed. The site renders acceptably across tested platforms because common fallback fonts cover these codepoints with text-presentation glyphs in most cases. A future cleanup would either:

- Replace the five codepoints with alternatives that exist in MonoLisa (requires running fontTools cmap checks against candidate replacement codepoints, then updating frontmatter on every page that uses each symbol, plus the homepage room list and README §3 symbol column).
- Augment `assets/css/custom.css` with explicit fallback declarations so the rendering is deterministic instead of system-dependent.

**Why this discovery happened:** Surfaced during work on the per-room typing animations, when verifying that all glyphs in the cycling strings (Spanish accents, Catalan accents, full Greek script) would render in MonoLisa. Spanish/Catalan/Greek all confirmed present in MonoLisa; the room symbols were the surprise miss.

### BUG-014: iOS Safari Translate prompt triggers on multilingual typing animation

**Symptom:** When viewing the site on iOS Safari (and in some cases other browsers with translation extensions), an inline translation UI overlay appears at the top of the page. The overlay shows fields like "Original text" and buttons reading "Contribute" / "Cancel". This is not part of the site's design.

**Cause:** The {{< typeit >}} animations on the homepage and all eight room landing pages cycle through Spanish, English, Catalan, and Greek strings within the same DOM element. Safari's page-language detection sees four languages on a single page and treats it as multilingual content needing translation. The Translate page feature then injects its UI to offer translation. Other browsers with translation extensions (Google Translate, DeepL) can exhibit similar behavior.

**Detection:** Inspect the rendered page on a device where the overlay appears. The injected UI does not match any selector in `assets/css/custom.css` or any Blowfish template. The strings "Original text" and "Contribute" / "Cancel" are Safari's translation interface labels.

**Status:** Not a site bug. The behavior is browser-side and cannot be suppressed from the site without removing the multilingual content that makes the typing animation interesting in the first place. The overlay is dismissable via the browser's address bar UI (Safari: tap `ᴀA` icon → cancel translation prompt) or by disabling translation in browser settings.

**Why this matters for the README:** Anyone troubleshooting an unexpected UI element on the site should first rule out browser-injected translation widgets before assuming it is a site rendering issue. This is parallel to BUG-011 (newly-registered domain blocks at the network level), where the symptom appears on the site but the cause is external infrastructure.

### BUG-015: Email address leaked in plain HTML via menu rendering

**Symptom:** The contact email `career-pgbd@pm.me` appeared as an unobfuscated `mailto:` link in the rendered HTML of every page (desktop menu and mobile menu collapse, two instances per page). Bots scraping `mailto:` links via regex harvested the address, leading to spam.

**Cause:** Blowfish has *two* paths that render the email link, and only one of them is obfuscated:

1. The `[params.author].links` block in `languages.en.toml` is rendered by `themes/blowfish/layouts/partials/author-links.html`. That partial special-cases email entries: it writes `href="#"`, encodes the real address into a `data-email="..."` base64 attribute, and adds a `class="email-link"` hook that JavaScript uses to decode and trigger `mailto:` on click. This path is properly obfuscated and safe.

2. The `[[main]]` entries in `menus.en.toml` are rendered by Blowfish's generic menu partials (`header/components/desktop-menu.html` and `header/components/mobile-menu.html`). These use a generic `<a href="{{ .URL }}">` template that does *not* special-case email URLs. Whatever URL is in the menu entry, including `mailto:`-prefixed ones, gets written literally to HTML.

The site had the email address in *both* places: as a `params.author.links` entry (safe) and as a `[[main]]` menu entry (leaking). The menu version was the actual scraping target.

**Fix applied:** Removed the email `[[main]]` entry from `menus.en.toml`. The email icon still renders in the social links area via the obfuscated `author-links.html` path. The menu layout loses one redundant icon. Re-weighted the remaining github entry from `30` to `20` to close the gap.

**Diagnostic:** To verify no email addresses leak in plain HTML, run after a build:

```bash
grep -n "career-pgbd\|mailto" public/index.html
```

Should return zero matches. The obfuscated `data-email="..."` base64-encoded value is fine and will not show up in this grep because it does not contain the literal address.

**What this fix does NOT do:** The address has already been harvested. Removing the leak protects against *future* harvesting only. To stop spam to the already-leaked address, rotate to a new contact alias (Proton's SimpleLogin integration handles this), update `params.author.links` in `languages.en.toml` to point at the new alias, and let the old address become a spam trap that can be filtered or disabled.

**Generalized lesson:** When a Hugo theme renders the same conceptual data via multiple template paths, audit *each* path independently. "The email is obfuscated" was true on the path I happened to look at; it was false on the path that mattered.

### BUG-016: MonoLisa Italic + SS02 cursive script unreadable for dyslexic readers

**Symptom:** A reader with dyslexia reported the body text was hard to read. The site shipped MonoLisa Italic with `font-feature-settings: "ss02" 1` everywhere except code blocks. SS02 is MonoLisa's stylistic alternate that turns italic into a flowing cursive script, visually striking but functionally a script font for body text and headings.

**Cause:** Italic-as-body-text is unconventional and creates real reading friction for many readers. Cursive-style italic specifically (which SS02 is) compounds the issue because the connected, sloped letterforms reduce per-character visual distinctiveness. Dyslexic readers in particular rely on per-character distinctiveness to disambiguate similar letters (b/d, p/q, m/w). The italic cursive collapses this distinctiveness across all letters, not just the typically-confused pairs.

**Fix applied:** Switched to a hybrid typography system. Body text and most headings (h2-h6) now use **Atkinson Hyperlegible**, a sans-serif designed by the Braille Institute specifically for low-vision and dyslexic readers. The font has visually distinct letterforms (no I/l/1 collisions, no b/d mirroring) which helps every reader, not just dyslexic ones. Loaded as four self-hosted woff2 files (Regular, Italic, Bold, BoldItalic) from `static/fonts/`, converted from upstream TTF via fontTools at ~24KB each.

H1 page titles (the terminal-prompt strings like `Σ ~/sala  # About Me`) and the {{< typeit >}} typing animations remain in MonoLisa upright. These are the identity-defining typography of the site, and upright MonoLisa is not the readability barrier; italic cursive was. Keeping the terminal-prompt look in H1s and animations preserves the brand without re-introducing the dyslexia issue. Code blocks remain in MonoLisa upright with ligatures, unchanged.

**Implementation in `assets/css/custom.css`:**

- Atkinson `@font-face` declarations for all four weights/styles
- MonoLisa Italic `@font-face` removed entirely (no longer used anywhere)
- `html, body` and `h2, h3, h4, h5, h6` selectors point to Atkinson with system sans-serif fallback chain
- `h1` and `[id^="typeit-"]` selectors point to MonoLisa upright with monospace fallback chain
- `em, i` defensive italic rule removed (was MonoLisa-specific; Atkinson has its own italic variant)

**Verification:** Load any page on the site. Body text and h2/h3 headings should render in Atkinson Hyperlegible (clean sans-serif). H1 page titles like `Σ ~/sala  # About Me` should render in MonoLisa upright (monospace). The cycling typing animations should also render in MonoLisa upright. Code blocks in project pages should render in MonoLisa with ligatures, unchanged from before.

**Why this matters generally:** The original cursive script was visually distinctive but it traded readability for aesthetics across every page. The fix demonstrates that "identity-defining typography" and "accessible typography" are not always in conflict; they can coexist by scoping each to where it does its best work. The terminal-prompt look defines the brand in short strings (page titles, animations); long-form prose needs to be read by humans, including those for whom italic cursive is a real barrier.

### BUG-017: Inline KaTeX requires `\\(...\\)` (double-backslash) in markdown source

**[SUPERSEDED by BUG-039, June 2026.]** The double-backslash workaround below is obsolete. Goldmark passthrough is now enabled, so inline math uses SINGLE-backslash `\(...\)`. The history below is retained to explain why the old workaround existed; do not apply it.

**Symptom:** Writing inline math as `\(M\)` in markdown source renders as the literal text `(M)` in the browser. KaTeX never processes it.

**Cause:** Hugo's Goldmark Markdown renderer interprets `\(` and `\)` as Markdown escape sequences for literal parentheses *before* the HTML reaches KaTeX. Goldmark eats the backslashes, leaving plain `(M)` in the rendered HTML. KaTeX's auto-render then has nothing to recognize.

**Fix (current, BUG-039):** Use SINGLE-backslash `\(...\)` in markdown source. With Goldmark passthrough enabled, the delimiters pass through verbatim and KaTeX's default render matches them. Before passthrough, the workaround was double-backslash; that is now obsolete and would break matching.

**Working examples on the site (verified):**

- `content/cocina/25live-cleaner.md` uses `\\(A\\)`, `\\(B\\)`, `\\(\\delta\\)`
- `content/cocina/qualtrics-processing-pipeline.md` uses `\\(P_{\\text{straight}} \\geq 0.8\\)`
- `content/garaje/foreign-per-diem-calculator-for-usa-based-institutions.md` uses `\\(N\\)`
- `content/estudio/ai-csv-profiler.md` uses `\\(k = 5\\)`, `\\(k = 30\\)`
- `content/garaje/pbi-model-export.md` uses `\\(M\\)`, `\\(K\\)`, `\\(m\\)`, `\\(n\\)` in set-builder notation

All of these render correctly. The pattern is consistent across the codebase.

**Single-dollar `$...$` does not work and cannot be enabled.** Blowfish's `katex-render.js` calls `renderMathInElement(document.body)` with no explicit delimiters array, so KaTeX uses its defaults: double-dollar block delimiters (enabled) and backslash-paren inline delimiters (enabled). Single-dollar inline is excluded by default for safety because it would conflict with currency notation, which the site uses heavily on `sala` (e.g. `$540M`, `$96.7M`) and several `garaje` pages (e.g. `$2` in `C$2` Excel formulas). Enabling single-dollar globally would mangle all of those.

**Avoid apostrophe-style primes (`m'`) in math expressions.** The apostrophe is converted to a curly typographic quote by Hugo's smartypants module before KaTeX processes the expression, breaking the parse. Use either a different variable name (e.g. `n` instead of `m'`) or LaTeX's `\\prime` superscript syntax (`m^{\\prime}`). The pbi-model-export page uses the former (`n`) for simplicity. See also BUG-001 for the broader smartypants issue with shortcodes.

**Diagnostic recipe.** If inline math is rendering as literal text on a new page, check three things in order:
1. Is the page calling `{{< katex >}}` *before* `{{< lead >}}`? See BUG-003.
2. Is the inline math written as SINGLE-backslash `\(...\)` in markdown source, and is Goldmark passthrough enabled in markup.toml (BUG-039)? Double-backslash is obsolete and now breaks matching.
3. Does the expression contain an apostrophe (`'`)? Replace it with `\\prime` or restructure to avoid.

**Why this matters.** With Goldmark passthrough enabled (BUG-039), the natural single-backslash syntax now works correctly, because passthrough stops Goldmark from touching the delimiters. This replaces the older, fragile double-backslash workaround. The lesson retained: math rendering problems on this site are almost always Goldmark processing the source before KaTeX sees it; passthrough is the structural fix, not delimiter escaping.

### BUG-018: Blowfish `{{< chart >}}` shortcode body must be the inside of an object literal, not a complete object

**Symptom:** Charts render as blank canvas. KPI tiles, prose, and other content around them work normally. Chart.js loads (the bundle is visible at `public/js/chart.bundle.[hash].js`) but no chart draws on any of the canvases.

**Cause:** The shortcode template at `themes/blowfish/layouts/shortcodes/chart.html` already emits `new Chart(ctx, { ... })` and substitutes `.Inner` between the braces. The shortcode body is supposed to be the *inside* of the config object. Wrapping the body in its own `{ ... }` produces nested braces in the rendered JS, `new Chart(ctx, { { type: 'line', ... } })`, which is a syntax error. The script silently fails to parse, the canvas stays blank, and there is no visible error if dev tools were not open during the initial parse.

**Workaround:**

```
✅ {{< chart >}}
type: 'line',
data: { labels: [...], datasets: [...] },
options: { ... }
{{< /chart >}}

❌ {{< chart >}}
{
  type: 'line',
  data: { labels: [...], datasets: [...] },
  options: { ... }
}
{{< /chart >}}
```

The Blowfish docs do show the correct unwrapped format, but the convention is non-obvious. Most Chart.js examples on the open web (Stack Overflow, Chart.js documentation, output from AI assistants) show full object literals with outer braces. Wrapping a literal directly into the shortcode is the natural reflex and produces a silent failure.

**Diagnostic recipe.** If a chart renders blank:
1. View page source. Locate the rendered `<script>` near the chart's canvas. Look for `new Chart(ctx, {`. The next non-whitespace token should be `type: ...`, not `{`.
2. If the next token is `{`, the shortcode body had outer braces. Strip them.
3. If the chart still renders blank, check dev tools Console for parse errors near `new Chart`.

Applies to every `{{< chart >}}` instance. The `/taller/` page has 11 charts; all 11 had this bug initially.

### BUG-019: Per-page interactive scripts must be inlined in markdown body, not loaded via a partial

**Symptom:** A small JavaScript adapter that listens for `<html>` class changes and updates Chart.js instance colors does not execute when delivered through any of these paths:
- External file at `assets/js/chart-theme.js` referenced from `layouts/partials/extend-footer.html` via Hugo Pipes (`resources.Get | resources.Minify | resources.Fingerprint`).
- Inline `<script>` block inside `layouts/partials/extend-footer.html` (no external file, no Pipes).

The adapter's `console.log` calls never appear. A sentinel global (`window.__chartThemeLoaded = true`) never gets set. The script is unreachable.

**Cause:** Not fully isolated. Suspected interaction between Blowfish's `partialCached "extend-footer.html" .` call in `themes/blowfish/layouts/partials/footer.html` and the per-page evaluation of `.Page.HasShortcode "chart"` inside the partial. Other content added inside the partial alongside the script also did not appear in the page output, which suggests the partial itself was not being rendered for `/taller/`. Browser cache and integrity-hash mismatch were ruled out by hard refresh and by removing the integrity attribute, with no change in behavior.

**Workaround:** Inline the `<script>` block directly in the markdown source of the page that uses it, at the bottom of the file, surrounded by an HTML comment sentinel for easy re-finding:

```html
<!-- chart-theme-adapter -->
<script>
(function () {
  // adapter body: attach MutationObserver to document.documentElement,
  // walk Chart instances via Chart.getChart(canvas) on each class change,
  // swap known palette hexes, call chart.update() (see BUG-021)
})();
</script>
```

`markup.goldmark.renderer.unsafe = true` (set in `markup.toml`) permits raw HTML in markdown body, so the `<script>` tag passes through unmodified into the rendered HTML. Confirmed working: the script registers, finds Chart instances via `Chart.getChart(canvas)`, attaches a `MutationObserver` for class changes on `<html>`, swaps known palette hexes (`#0969DA` ↔ `#79C0FF`, `#000000` ↔ `#FFFFFF`, plus the matching rgba area-fill), updates grid and tick label colors, and calls `chart.update()` on each instance.

**Verification.** Open dev tools Console on `/taller/`. Look for `[chart-theme] inline-in-markdown script registered` followed by `init: html.dark=..., charts=11`. Toggle the moon icon. Look for `switching light -> dark, charts: 11`. The chart colors should swap with a brief animated transition.

**Why this matters.** This pattern generalizes. Any per-page interactive enhancement of Blowfish content that needs JavaScript against existing globals (Chart.js, Mermaid, KaTeX) can be inlined in markdown rather than wired through theme partials. The cost is a `<script>` block in the markdown source; the benefit is reliable execution colocated with the content it enhances. Theme partials remain useful for cross-cutting concerns; per-page enhancements live with the page.

### BUG-020: Chart.js axis labels touch the canvas edge without explicit `layout.padding`

**Symptom:** On small-multiple line charts (8 mini charts at 130px height inside cards on `/taller/`), x-axis tick labels (years like `1985`, `1996`, `2007`, `2018`) visually butt up against the bottom edge of the chart canvas. With the canvas sitting inside a card with a 1px border, the labels look like they are touching the card border itself, producing a cramped, edge-pinned appearance.

**Cause:** Chart.js does not add internal layout padding by default. With `maintainAspectRatio: false` and a fixed-height parent, the chart fills the parent and tick labels are drawn at the canvas edges with no breathing room.

**Fix applied:** Add a `layout.padding` block to the `options` of each affected chart:

```js
options: {
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { top: 2, right: 6, bottom: 4, left: 2 } },
  plugins: { ... },
  scales: { ... }
}
```

Right padding (6px) prevents the rightmost x-tick label from extending past the canvas right edge when the last data point sits near the right side. Bottom padding (4px) keeps year labels off the canvas bottom edge. Top and left (2px each) provide symmetric breathing room.

Applied to all 8 small multiples on `/taller/`. The annual time series (360px tall), bar chart (540px tall), and slope chart (360px tall) have enough vertical room to not need explicit padding.

### BUG-021: Chart.js dynamic dataset color changes need explicit point colors and the default update mode

**Symptom:** A theme adapter mutates a dataset's `borderColor` and `backgroundColor` at runtime to swap palettes, then calls `chart.update('none')` to re-render without animation. The line color updates correctly. The point colors do not. Inspection shows the dataset object's color values ARE updated, but the rendered points use stale resolved options. On `/taller/`'s slope chart, this manifested as Alberta's line going black-to-white correctly on theme toggle while its data points stayed black on the now-white line.

**Cause:** Two compounding issues, either of which alone is sufficient to break runtime point-color updates:

1. Chart.js v4's default property routing makes `pointBackgroundColor` fall back to `dataset.backgroundColor` and `pointBorderColor` to `dataset.borderColor`. When a dataset config provides `borderColor` and `backgroundColor` but omits the point-specific properties, point colors are routed at construction time. Subsequent runtime mutations of `backgroundColor` do not flow back through the route; points keep drawing with the construction-time resolved value.

2. `chart.update('none')` skips the animation transition mode. As an apparent side effect, it also skips full re-resolution of element-level options. Even when the point-color properties ARE explicit on the dataset, 'none' mode update may not pick up changes to them.

**Fix (both required):**

1. Set `pointBackgroundColor` and `pointBorderColor` explicitly on every dataset whose colors will be mutated at runtime, even when they would default to the line colors via routing. This gives the adapter explicit properties to mutate.

   Slope chart dataset shape after the fix:

   ```js
   {
     label: 'University of Alberta',
     data: [...],
     borderColor: '#000000',
     backgroundColor: '#000000',
     pointBackgroundColor: '#000000',
     pointBorderColor: '#000000',
     borderWidth: 1.5,
     pointRadius: 4,
     pointHoverRadius: 6,
     tension: 0
   }
   ```

2. Use `chart.update()` (no argument, default mode) instead of `chart.update('none')` in the theme adapter. Default mode forces full element-option re-resolution. The tradeoff is a brief animated transition on theme switch, which reads as natural rather than as a visual regression.

**Diagnostic recipe.** If a runtime color change is visible on lines but not on points:

1. In dev tools console, find the chart via `Chart.getChart(canvas)`.
2. Compare the dataset value to the resolved element option:
   - Dataset value: `chart.data.datasets[i].pointBackgroundColor`
   - Resolved value Chart.js draws with: `chart.getDatasetMeta(i).data[0].options.backgroundColor`
3. If the dataset value is updated but the resolved value is stale, the update mode is the problem. Switch to `update()`.
4. If the dataset value is `undefined`, the property is being routed via Chart.js defaults. Set it explicitly on the dataset.

**Why this matters.** The bug was diagnosed only by inspecting `getDatasetMeta(i).data[0].options` and comparing to the dataset value. The dataset values themselves were lying about what was being rendered. Three rounds of "this should fix it" iterations preceded the diagnosis. Theme adapters and any code that mutates Chart.js colors dynamically must be defensive on both fronts: set every color property explicitly on the dataset, and use the default update mode. The combination of property routing plus 'none' update mode silently breaks point rendering, with no console error and no visible warning.



### BUG-022: Chart color contrast must be measured against WCAG ratios, not eyeballed

**Symptom:** A dashboard built with a "color-blind-safe palette" (Okabe-Ito) and a "documented light/dark theme" (GitHub accent palette) still shipped with two chart series at FAIL contrast in light mode (`#56B4E9` Picton Blue at 2.31:1 and `#E69F00` Orange Peel at 2.25:1, both below the 3:1 minimum) and three more at marginal AA-large/non-text in dark mode. The author had personally verified the dashboard "looked fine" in both themes; eyeballing missed it.

**Cause:** Two compounding issues, each plausible-sounding on its own:

1. **CVD-safe palette is not the same as high-contrast palette.** Okabe-Ito was designed for distinguishability across color-vision deficiencies on the gray paper backgrounds typical in scientific journals. Several of its colors (`#56B4E9`, `#E69F00`, `#F0E442`) are deliberately bright and pale: perfect for distinguishability, terrible for contrast against a pure-white web background. Adopting the palette without measuring per-color contrast against the actual canvas color produces silent failures.

2. **A theme adapter that swaps a documented light hex (e.g., `#0969DA`) to its documented dark equivalent (e.g., `#79C0FF`) only protects the swapped colors.** Any chart series color outside the swap map (every Okabe-Ito hue) renders identically in both themes. A series at AA-text in light mode may collapse to AA-large in dark mode (or vice versa) without any code change, just because the background flipped.

**Fix:** A scripted contrast audit that runs against the actual markdown source rather than against documentation. The audit script must:

1. **Parse the swap map directly out of the inline theme adapter,** not maintain a separate hardcoded list. The script and the rendered page must read from the same source of truth or they will drift.

2. **Enumerate every chart series color from every chart on the page** (not just the slope chart, not just the Okabe-Ito palette) and compute WCAG 2.1 contrast against the canvas color of each theme. Group results by ratio, tag each entry as AAA-text / AA-text / AA-large/non-text / FAIL.

3. **Report both modes side by side.** A color that's AA-text in light mode and AA-large in dark mode is a different design situation than one that's AA-text in both. The two-mode report makes the trade-off visible.

The audit script for `/taller/` lives at [`tools/audit_contrast.py`](tools/audit_contrast.py). It produces output like:

```
LIGHT MODE — chart series colors against #FFFFFF
  COLOR      RATIO      GRADE                        USAGE
  #0969DA    5.19:1     AA-text                      borderColor on Annual funding
  #56B4E9    2.31:1     FAIL                         borderColor on Centre for Addiction...
  ...
```

**Diagnostic recipe.** When building a new dashboard:

1. Run the audit before the first commit. Note any FAIL entries; those need new colors.
2. AA-large/non-text entries (3.0-4.49:1) are within mirador's documented 3:1 floor for chart elements but require a deliberate decision: accept the marginal contrast to preserve palette identity, or push the color darker/lighter at the cost of palette recognizability. Whichever you pick, **document the choice inline in the chart config** so future-you doesn't "fix" it unknowingly.
3. After every theme-adapter change, rerun the audit. The map and the audit must stay in sync.

**Why this matters.** Three rounds of "the colors look fine" preceded the FAIL discovery on `/taller/`. Visual inspection on a single monitor in a single lighting condition by a single non-CVD viewer is not an accessibility test. The math is the test. A 100-line Python script is enough to make it permanent and re-runnable; treating contrast as a one-time eyeball check is what produces silent inaccessibility in production dashboards.




### BUG-023: `{{< chart >}}` wrapped in `<div>` with blank lines stops markdown rendering

When wrapping a `{{< chart >}}` shortcode in custom HTML (for example, a `<div class="pgbd-case-chart-wrap">` for headline-above-chart styling), a blank line immediately after the opening `<div>` causes Hugo plus goldmark to stop rendering markdown after the chart's closing tag. Every H2 section below the chart silently disappears from the rendered HTML output, even though the markdown source on disk is intact.

**Symptom:** the page renders the chart correctly, but everything below it (the next H2 heading, all subsequent prose, all later shortcodes) is missing from the live page. The file on disk looks complete; only the rendered output is truncated.

**Diagnostic:** `curl -s "http://localhost:1313/<page>/" | grep "<h2"`. If only the H2 sections above the chart come back in the rendered HTML, BUG-023 is the cause.

**Pattern that fails (do not write this):**

```html
<div class="pgbd-case-chart-wrap">

<p>Headline...</p>

{{< chart >}}
...config...
{{< /chart >}}

</div>
```

**Pattern that works:**

```html
<div class="pgbd-case-chart-wrap">
<p>Headline...</p>
{{< chart >}}
...config...
{{< /chart >}}
</div>
```

**Rule:** no blank lines between the opening `<div>` and the first child element, no blank line between the closing `{{< /chart >}}` and the closing `</div>`. The blank line after the closing `</div>` is required so the markdown that follows gets parsed as markdown again.

This trap also affects `{{< mermaid >}}` blocks and any other shortcode wrapped in custom HTML. The fix is the same in every case: tight HTML wrapper with no internal blank lines, blank line after the closing tag.

First encountered: kentucky-nih case study phase 03 (exploration) when adding the headline-above-chart wrapper from the taller dashboard pattern. Four sections below the chart silently failed to render until the blank lines inside the wrapper were collapsed.

### BUG-024: Case study prose contained fabricated numbers that did not reproduce against the database

When the kentucky-nih case study was first drafted, multiple SQL queries had "expected output" tables and prose claims based on numbers that were never actually generated by running the queries. The numbers were plausible-looking but wrong: the funding-by-year table had values off by 10-30 percent across all 21 years, organization names were in the wrong case ("University Of Kentucky" vs the real "UNIVERSITY OF KENTUCKY") and included institutions ("Tru Diagnostics", "Lexington VA Medical Center") that do not appear in the actual top 10, the "RC1/RC2 as smoking gun for ARRA" finding cited activity codes that don't appear in the real top 10, and an entire "2025 Cliff" section in phase 04 was built around a fabricated $81.3M FY 2025 figure when the actual value is $235.2M. The case study made philosophical commitments to reproducibility while failing them.

**Symptom:** any reader running a query in Datasette Lite gets numbers that don't match what the case study prose claims. The reproducibility-is-the-floor commitment from the biblioteca philosophy fails immediately for anyone who actually checks.

**Detection:** running the SQL queries from the case study against the live `static/data/kentucky-nih.sqlite` database and comparing the actual output line-by-line against what's in the prose and result blocks.

**Cause:** when an AI assistant is asked to write a multi-section case study with multiple SQL queries and expected outputs, the temptation is to generate plausible-looking numbers that fit the prose narrative rather than running queries to capture real output. This works in textbook contexts (where the data is hypothetical) and fails catastrophically for case studies built on real databases. The discipline that prevents it is documented in §17.

**Fix:** a full rewrite of phases 02, 03, and 04 against verified output. Every SQL query was run against the live database, the actual output was captured with `sqlite3 -header -column`, and the prose, result blocks, and Chart.js data arrays were rebuilt from the captured output. Phase 04's "2025 Cliff" section was deleted entirely (the cliff doesn't exist in the data); phase 03's "What's Worth Following Further" section was rewritten to reflect threads the data actually supports. The corrected case study reproduces; anyone running any query gets exactly the numbers shown in the prose.

**Prevention:** see §17. Before writing prose around a SQL result, run the query and capture the real output. Build prose from captured output, not the reverse. After draft, re-run every query and confirm the result blocks match.

First encountered: kentucky-nih case study phases 03 and 04, May 2026.

### BUG-025: Bash heredoc with literal `$N,NNN` is shell-expanded before reaching Python

Bash scripts that pipe content into Python via `python3 <<DELIM` will shell-expand any unescaped `$NNN` token in the heredoc body before Python sees it. When the body contains a literal SQL fragment or anchor string with currency values like `$5,896`, the bash parser interprets `$5` as the (typically unset) fifth positional parameter and substitutes the empty string, leaving `,896` in its place. Python then receives a corrupted anchor and `text.count(anchor)` returns zero matches.

**Symptom:** a patch script's pre-flight check reports zero matches for an anchor that is unambiguously present in the target file. Diagnostic greps confirm the anchor exists in the file. The pre-flight failure is real but the cause is in the bash layer, not the Python layer.

**Diagnostic:** `cat -A` (or `grep` with `-P` and a control-character pattern) on the script source reveals the anchor as written. Compare against what the script actually passes to Python by adding a `print(repr(old))` line at the top of the heredoc body. If the printed value differs from what's in the script source, BUG-025 is the cause.

**Pattern that fails:**
```bash
python3 <<__DELIM__
old = "| 2023 | Public | $5,896 | 13 |"  # bash sees $5 and expands it
text.replace(old, new)
__DELIM__
```

**Pattern that works:**
```bash
python3 <<'__DELIM__'
old = "| 2023 | Public | $5,896 | 13 |"  # quoted heredoc disables expansion
text.replace(old, new)
__DELIM__
```

**Rule:** if a heredoc body contains literal `$` characters (currency values, SQL parameter syntax, regex backreferences, etc.), the heredoc delimiter must be single-quoted. The single quotes around the delimiter tell bash to pass the body verbatim.

This trap is invisible at script-write time: the script source looks correct and bash syntax is valid. It only manifests at runtime when the pre-flight check fails. The mitigation is to default to quoted heredocs in any patch script that handles content with potential `$` characters; the cost of the quotes is zero.

First encountered: college-scorecard-fl case study phase 03 chart-adding script, May 2026. The patch had `$5,896` in three SELECT-result anchors; the unquoted heredoc expanded `$5,896` to `,896` and the pre-flight reported zero matches for an anchor unambiguously present in the file.

### BUG-026: F-string with backslash-escaped quotes inside expression is a Python SyntaxError

Python f-strings do not allow backslash escape characters inside the expression part of the f-string. A line like `f"text: {variable.count('hello')}"` works because no escape is needed; a line that tries to escape quotes inside the brace expression is a SyntaxError, because the f-string parser cannot reason about backslash escapes at runtime. The fix is to bind the long string to a variable outside the f-string and reference the variable inside the expression.

**Symptom:** a patch script's heredoc body fails with `SyntaxError: unexpected character after line continuation character` at the line containing the f-string. The error message points to the backslash position. The script never executes any patches.

**Diagnostic:** read the failing line and look for backslash-escaped quotes inside `{...}` brackets within an f-string. If present, BUG-026 is the cause.

**Pattern that fails (do not write this):**
- An f-string where the expression inside braces contains backslash-escaped quotes around a long substring being passed to `.count()` or similar.

**Pattern that works:**
- Bind the substring to a named variable outside the f-string.
- Reference the variable inside the f-string expression.

**Rule:** never use backslash-escaped quotes inside an f-string expression. If the value to be inserted requires literal quotes, bind it to a named variable first and reference the variable in the f-string. The f-string parser handles variable lookups; it does not handle backslash escapes inside braces.

This was caught at script execution time, not at script write time, because Python f-string syntax errors fire only when the interpreter parses the function or top-level expression containing the f-string. The mitigation is to extract the Python heredoc body from the bash script and run a `compile(body, 'heredoc', 'exec')` check before presenting the script. The compile-check fires the same SyntaxError that the runtime would, but at write-time when the cost of fixing it is one iteration instead of one round-trip through the user.

First encountered: college-scorecard-fl phase 04 trim-earnings-chart-to-top10 script, May 2026. The audit section inlined a 200-character substring check inside an f-string with escaped quotes around the substring. The fix was to bind the substring to a named variable outside the f-string.

### BUG-027: SQL alias column alignment produces excessive padding when one expression is much longer than its siblings

A naive per-group SQL alias aligner that pads every line to one-space-past-the-longest-expression in a contiguous group produces clean output for typical SELECT clauses but blows up when one expression is dramatically longer than its siblings. Window functions like `RANK() OVER (PARTITION BY x ORDER BY y ASC)` or stacked aggregates like `SUM(SUM(value)) OVER (PARTITION BY year)` can be 80 to 100 characters long, and aligning all sibling expressions to that length pushes the AS aliases off the right edge of a code block on rendering.

**Symptom:** SQL code blocks in case study prose have AS aliases that are not visible in the rendered HTML because they are padded past the right edge of the code block. The block scrolls horizontally on smaller viewports.

**Diagnostic:** for each SQL block, find the maximum run of spaces immediately before `AS`. If the maximum exceeds approximately 50 characters, the block has an alignment-blow-up case.

**Cause:** typical kentucky-nih SQL alignment is per-group (each contiguous SELECT clause aligns its AS columns) with most expressions in the 5-30 character range. The aligner script computes max expression length and pads to that. When a single expression in the group is 80-100 chars (a window function, for example), every shorter expression in the same group gets padded out to that length.

**Fix:** cap alignment at a reasonable width (45 characters in the College Scorecard FL case study). When the longest expression in a group exceeds the cap, all lines in the group fall back to single-space-before-AS instead of column alignment. This produces readable output for both typical and pathological cases.

**Rule:** SQL alias alignment scripts should always include a width cap. The cap value should match the typical column width of the rendered code block (around 80 characters minus indent and AS overhead). Per-group alignment is good when the longest expression is reasonable; column-aligned for-its-own-sake alignment is not the goal.

First encountered: college-scorecard-fl case study phases 02-04 SQL alias realignment, May 2026. The first realigner script collapsed 60-space gaps to clean alignments for most queries but pushed Phase 04 Q1 (cost-per-completer) to 91 spaces because the RANK() OVER expression was 100 characters long. The cap at 45 characters fixed the regression.

### BUG-028: College Scorecard `c150_4 = 0` is often a measurement artifact, not zero completion

The College Scorecard's `c150_4` metric (completion rate within 150 percent of normal time, four-year cohort) measures specifically first-time, full-time bachelor's-seeking students who completed within six years. At institutions whose student bodies are mostly part-time, mostly transfer students, or in programs longer than four years, the metric can return zero even when the institution graduates students normally. Naive interpretation of `c150_4 = 0` as a zero-completion finding is wrong; the metric measures a specific cohort definition that does not fit every institutional profile.

**Symptom:** a SELECT or visualization that includes `c150_4` returns 0.0 for institutions like Chamberlain University-Florida (a thousand-student-cohort nursing school), Polytechnic University of Puerto Rico's Florida branches, and small religious seminaries. The rate of 0 percent looks like institutional failure on first glance.

**Diagnostic:** for any institution-year reporting `c150_4 = 0`, query `c200_4` (200 percent completion rate, eight-year window) for the same institution-year. If `c200_4` is meaningfully nonzero (10 percent or higher), the institution graduates students; the `c150_4 = 0` is a measurement artifact reflecting the cohort definition mismatch.

**Cross-check query:**
```sql
-- Confirms whether c150_4 = 0 is artifact or genuine zero completion.
-- A meaningful c200_4 value at the same institution-year proves the
-- institution graduates students, just on a longer timeline than the
-- six-year window measures.
SELECT
    i.instnm                  AS "Institution",
    am.cohort_year            AS "Year",
    ROUND(am.c150_4 * 100, 1) AS "c150_4 (6yr) %",
    ROUND(am.c200_4 * 100, 1) AS "c200_4 (8yr) %"
FROM institutions       i
JOIN annual_metrics     am USING (unitid)
WHERE am.c150_4 = 0
  AND i.sector IN ('private_nonprofit', 'for_profit')
ORDER BY i.instnm, am.cohort_year;
```

**Cause:** `c150_4` is calibrated for the canonical first-time-full-time bachelor's seeking cohort. Career-focused institutions with adult-learner populations, transfer-heavy specialty schools, religious seminaries with non-traditional programs, and branch campuses all violate the cohort assumption. The metric returns zero when the violating institution has too few first-time-full-time students to compute a meaningful rate.

**Fix in case study prose:** when reporting `c150_4` averages, document the artifact rule and present a comparison row showing `c150_4 = 0` and `c200_4 > 0` for the same institutions. Filter measurement-artifact rows out of any aggregate that would mislead (e.g., HAVING COUNT >= 5 to require five years of c150_4 data).

**Rule:** treat `c150_4` as a metric for traditional first-time-full-time cohorts only. Use `c200_4` as a sanity check for any institution-year where the value is suspiciously low. Document the artifact pattern in any case study that uses the metric.

First encountered: college-scorecard-fl case study phase 03 (exploration), May 2026. Several institutions reported 0.0 percent c150_4 in the result table; verification with c200_4 showed meaningful eight-year completion at most of them: Argosy University-Sarasota 0.0 percent over six years and 66.7 percent over eight, Polytechnic UPR-Miami 0.0 percent and 100.0 percent, Chamberlain University-Florida 0.0 percent and 50.0 percent.

### BUG-029: KaTeX display math `\\[...\\]` containing `}_{...}` is corrupted by markdown italic parser

**[SUPERSEDED by BUG-039, June 2026.]** This corruption no longer occurs: Goldmark passthrough now leaves display math untouched, so `}_{...}` and all underscores are safe. Display math uses SINGLE-backslash `\[...\]`. The analysis below correctly diagnoses the cause but its workaround is obsolete.

Hugo's goldmark markdown parser processes display math blocks (`\\[...\\]`) BEFORE KaTeX sees the source. When the LaTeX inside contains the pattern `}_{...}` (a closing brace immediately followed by underscore-brace), goldmark interprets the underscore as the start of an italic emphasis span and corrupts the source. KaTeX then receives malformed LaTeX and the formula renders as raw markdown text on the page instead of as typeset math.

**Symptom:** A display formula renders as literal text on the page, e.g., `\[\overline{f}_{t} = \dfrac{1}{5}\sum_{i=t-2}^{t+2} f_i\]` shown verbatim. Inline math `\\(...\\)` on the same page using the same expressions renders correctly.

**Diagnostic:** view the page source after Hugo renders it. If the display formula's raw HTML contains underscores converted to `<em>` tags or stripped entirely, BUG-029 is the cause. Compare against an equivalent inline formula on the same page; if the inline version is fine, the issue is the markdown parser specifically processing display math differently from inline math.

**Cause:** display math blocks in markdown are treated as block-level content and get standard markdown processing (italic, bold, code spans). Inline math is parsed within paragraph context with different rules. The pattern `}_{...}` triggers italic-emphasis parsing because the underscore appears between two non-whitespace characters.

**Pattern that fails:**
```markdown
\[\overline{f}_{t} = \dfrac{1}{5}\sum_{i=t-2}^{t+2} f_i\]
```

The `}_{t}` substring at position 12 looks like the start of an italic span to goldmark. Same thing happens at `\sum_{i=t-2}` and `f_i`.

**Patterns that work:**

Option 1: Nest subscripts inside the outer brace group so underscores are protected:
```markdown
\[\overline{f_t} = \dfrac{1}{5}\sum\_{i=t-2}^{t+2} f\_i\]
```

Option 2: Escape underscores with backslash so markdown ignores them:
```markdown
\[\overline{f}\_{t} = \dfrac{1}{5}\sum\_{i=t-2}^{t+2} f\_i\]
```

KaTeX strips backslash-escaped underscores back to plain underscores during its own parsing, so the rendered math is mathematically identical.

**Rule:** when writing display math, never use the pattern `}_{` (close brace, underscore, open brace). Either nest the subscript inside the outer brace group or escape the underscore with backslash. Inline math `\\(...\\)` does not have this problem and the same expressions work without escaping.

**Prevention discipline:** after adding any display formula to a page, view the rendered output in a browser. The visual check is the only reliable way to catch this; the markdown source looks correct.

First encountered: kentucky-nih case study phase 04 (findings), May 2026. The 5-year centered moving average formula `\[\overline{f}_{t} = \dfrac{1}{5}\sum_{i=t-2}^{t+2} f_i\]` rendered as raw text. The college-scorecard-fl Phase 04 cost-per-completer formula on a sibling page used `\overline{c_{150,4}}` (subscript inside the outer brace) and rendered correctly, confirming that the issue is specifically the bare-underscore-between-brace-groups pattern, not KaTeX or display math in general.

### BUG-030: README §8 frontmatter `showReadingTime` documented as `false` while all live pages use `true`

**Symptom:** A new project page authored strictly from the README §8 "Required fields on every project page" template lacks the "N mins" reading-time label that appears on every other card on the room landing page. The label is missing from the project page body too.

**Diagnostic:** check any existing project page's frontmatter against §8. The §6 template block shows `showReadingTime: true   # Hugo auto-estimate; surfaced on cards too`. The §8 required-fields block (until this fix) showed `showReadingTime: false`. The two disagreed.

**Cause:** the §8 block was authored before the reading-time feature was enabled on cards. When the feature was enabled, the §6 template was updated but §8 was not, and the "Field role reminders" table that follows §8 still described `showDate`, `showReadingTime`, `showAuthor` together as "All `false` to keep pages stripped of clutter." The rationale text became wrong at the same moment the field value did, but in three places at once that all had to be updated together.

**Fix applied:** §8 required-fields block updated to `showReadingTime: true`. The field-role-reminders table now lists `showReadingTime` on its own row with its own rationale (surfaces Hugo's auto-estimated reading time on cards and on the page), while `showDate` and `showAuthor` keep the original `false`-to-strip-clutter rationale on a shared row.

**Rule:** when §6 (the template) and §8 (the required-fields spec) disagree, §6 wins. §6 is what authors actually copy from, so it is the de facto live spec; §8 is a documentation summary that can drift. Any future change to the frontmatter contract has to update both at once, and the field-role-reminders rationale text has to be re-read to confirm it still describes reality.

**Prevention discipline:** when authoring a new project page, do not just follow §8. Read the frontmatter of one existing project page in the same room and confirm it matches §8 before treating §8 as authoritative. If they disagree, the live page wins and §8 needs a BUG entry.

First encountered: sql-x-ray project page authored May 2026. The first draft followed §8 (`showReadingTime: false`) and rendered without a "N mins" label, breaking visual consistency with the other three estudio cards. Discovered by spot-reading the live frontmatter of all 16 existing project pages, every one of which uses `showReadingTime: true`.

### BUG-031: Search modal renders tag taxonomy results with Hugo's auto-humanized titles, not the `card.html` tag-map values

**Symptom:** searching for `sql` in the site search modal (press `/`) returns tag results titled "Sql", "Mysql", "Postgresql", "Sql-Server", "Sqlite", "Sqlite-Utils" instead of the properly-cased "SQL", "MySQL", "PostgreSQL", "SQL Server", "SQLite", "sqlite-utils". Room cards on the same site show the same tags with correct casing, so the inconsistency is visible to anyone who searches.

**Diagnostic:** open the search modal and search for a tag whose proper casing involves an acronym or non-title-case form (`sql`, `mysql`, `ai`, `json`, `csv`, `pandas`). If the result row's title is Hugo's humanized version of the slug rather than the casing shown on room cards, BUG-031 is the cause. Confirm by visiting the corresponding term page (e.g., `/tags/sql/`) directly: the H1 there will also show the auto-humanized title.

**Cause:** the search index at `/index.json` is built by Hugo from each page's `.Title` field at build time. For tag taxonomy term pages, Hugo auto-generates `.Title` from the slug via `humanize`, which preserves hyphens and does not know about acronyms. The `card.html` tag map runs at template render time on room landing pages, but never touches the term pages' `.Title`, so the map has no effect on the search index. There are effectively two separate display paths: `card.html` for inline pills on room cards, and Hugo's auto-humanization for everything else (term pages, search results, breadcrumbs).

**Fix applied:** created `content/tags/<tag>/_index.md` for every tag in use across the site (69 files as of May 2026), each with frontmatter `title:` set to the correct display value. Hugo prefers explicit content over auto-generated humanization, so the term page `.Title` is now whatever the content file specifies. This propagates to the search index entry, the term page H1, and the breadcrumb at the top of the term page.

**Rule:** tag display has TWO sources of truth. The `card.html` tag map controls how tags render on room landing pages (the inline pills under each project card). The `content/tags/<tag>/_index.md` files control how tags render everywhere else (search results, taxonomy term pages, breadcrumbs). Both must agree. When adding a new tag that needs explicit display formatting, update both at once or the search modal will silently drift from the cards.

**Prevention discipline:** when adding a new tag to any project, two steps in addition to adding it to the project's frontmatter:

1. Add the tag to the `card.html` map in alphabetical position with the correct display label.
2. Create `content/tags/<new-tag>/_index.md` with frontmatter `title: "Display Label"` matching the card.html label exactly.

The `tools/create_tag_term_pages.py` script can be re-run after step 1 to regenerate step 2 from a canonical list, but the canonical list inside the script has to be updated by hand. There is currently no single-file source of truth that both `card.html` and the script read from. Future cleanup: move both consumers behind `data/tagmap.toml` and read from there.

**First encountered:** May 2026, after the sql-x-ray project page added eight new tags (`postgresql`, `mysql`, `mariadb`, `sql-server`, `bigquery`, `firebird`, `oracle`, `json`). The `card.html` tag map was updated and the room cards rendered correctly. The search modal continued showing the auto-humanized fallbacks ("Sql", "Mysql", "Postgresql") because no one had previously noticed that the taxonomy pages were a separate display path. Found by spot-checking search results after the sql-x-ray page deployment.

### BUG-032: Empirical permutation search validates SPQ/SUQ/FAQ/WIQ term ordering

**Symptom:** Penobscot NCLEX-RN testing-cohort terms use the codes SPQ, SUQ, FAQ, WIQ. The natural-language reading is Spring/Summer/Fall/Winter, but an academic-year reading (Fall/Winter/Spring/Summer) is also defensible because the institution operates on an August-July academic calendar. The two readings produce different chronological orderings of the 8-quarter testing window and therefore different retake funnel statistics. Without empirical validation, the case study cannot defend its choice.

**Diagnostic:** for each of the 24 permutations of (SPQ, SUQ, FAQ, WIQ) onto ordinal positions 1-4, count the number of "negative gap" students whose `terms_grad_to_first_test` value comes out negative. Negative gaps are causally impossible (a student cannot test before graduating), so the correct ordering should produce the minimum count of negative gaps. The permutation that produces fewest violations is the empirically correct one.

**Outcome:** the SPQ=1, SUQ=2, FAQ=3, WIQ=4 ordering produces 4 negative-gap violations (3 students at -3 quarters; one student at -1 due to a likely data entry error). The runner-up ordering produces 1,500+ violations. The three-orders-of-magnitude separation makes the choice unambiguous: spring/summer/fall/winter is correct, and the institution's August-July calendar is a red herring for testing-cohort ordering (the testing cohort runs on calendar-year quarters, not academic-year quarters).

**Rule:** when a categorical ordering is ambiguous from the data alone, write an empirical validation that uses an external constraint (here: causal impossibility of negative time gaps) to discriminate among orderings. The validation should compute the constraint-violation count for every permutation and report the result, not just the winner. The order-of-magnitude separation between best and worst is the evidence the choice is correct, not the absolute count of violations under the best ordering.

**Prevention discipline:** for any categorical-with-natural-ordering column in a database, do not assume the natural-language reading is correct. Compute a validation against a known causal or temporal constraint before relying on the ordering in queries or prose. The cost is a 30-line script; the benefit is defending the choice in writing without hand-waving.

First encountered: Penobscot NCLEX-RN case study, May 2026. The case study's retake-funnel analysis depends on which testing cohorts come "before" or "after" any given cohort, so an incorrect ordering propagates to every retake statistic. The 24-permutation search ran in seconds and produced unambiguous results; the same approach generalizes to any case study that depends on categorical ordering.

### BUG-033: Schema-first-values-never: do not recode existing column values mid-session

**Symptom:** Penobscot NCLEX-RN's `attempts.result` column stored values as INTEGER 0/1. Mid-session, the column was recoded to TEXT 'Pass'/'Fail' for readability. Every downstream SQL query that depended on the original 0/1 representation broke immediately: `AVG(CAST(result AS REAL))` returned errors, `100.0 * AVG(result)` returned NaN, and the Wald confidence intervals computed across phases 03 and 04 silently produced garbage values.

**Diagnostic:** when a query that previously worked starts returning errors or implausible values, check whether the column it depends on has been recoded. The fastest test is `SELECT typeof(column_name) FROM table LIMIT 1` and compare against what the query assumes.

**Cause:** SQL queries written against `result` as INTEGER 0/1 (e.g., `AVG(result)` as a pass-rate proxy, `SUM(result)` as a pass count, `CAST(result AS REAL)` for binomial proportion math) all fail or return NaN when `result` becomes TEXT 'Pass'/'Fail'. The recoding is a semantic improvement (the rows now read more naturally in a raw `SELECT *`) but it breaks every downstream consumer that assumed numeric.

**Rule:** Schema-first-values-never. Once a database column's type and value encoding are established and have downstream consumers (queries, charts, prose tables), do not change them mid-session. If a different representation is needed for readability, add a virtual column or a CASE WHEN in the SELECT clause; never mutate the underlying value encoding in place.

**Prevention discipline:** before recoding any column value in a working database, run a `grep -r` against all `.md` files in the repo for the column name. If any SQL block uses the column in an arithmetic, AVG/SUM/aggregate, or CAST context, the recoding will break those queries. The choice is then: either don't recode, or recode AND patch every downstream consumer in the same transaction.

First encountered: Penobscot NCLEX-RN case study, May 2026, between Step 1 (database rebuild) and Step 5 (prose patches). The recoding to 'Pass'/'Fail' was applied to the database but the SQL in phases 03 and 04 was not patched. The Step 3 audit dump showed pass rates as NaN, which triggered the rollback. After reverting to INTEGER 0/1, all downstream queries worked again. The lesson is to never change column representations once they have consumers; add readable views or CASE expressions instead.

### BUG-034: Chart axis text and dataset colors invisible in dark mode when hardcoded as `#000000`

**Symptom:** new chart configs added to the Penobscot case study rendered with completely invisible axis tick labels and gridlines in dark mode, plus invisible second-series bars (NCSBN comparison bars in Phase 04 Chart 3, "Did Not Retake" bar in Phase 04 Chart 4). In light mode the charts looked fine. Side-by-side comparison with Kentucky and Florida case studies showed Kentucky/Florida charts rendered correctly in both modes despite using similar Chart.js configs.

**Diagnostic:** open the Penobscot case study phase pages in dark mode (toggle via the site's theme switcher). Tick labels on the chart axes should be visible against the dark background. If they are not, search the chart shortcode body for hardcoded `ticks: { color: '#000000' }` or `grid: { color: 'rgba(0,0,0,...)' }`. Both render as black-on-dark, invisible. For the bar visibility issue, search for hardcoded `backgroundColor: '#000000'` or `borderColor: '#000000'` in the dataset arrays.

**Cause:** Chart.js does not auto-theme dataset colors or hardcoded axis colors based on the page's light/dark mode. Blowfish's `themes/blowfish/assets/js/chart.js` sets `Chart.defaults.backgroundColor`, `borderColor`, `elements.point.borderColor`, etc., to theme-aware CSS variables (e.g., `--color-primary-300`) that swap when the user toggles theme. But Blowfish does NOT set `Chart.defaults.color` (the default text color for ticks, legend, title), and it does NOT set `Chart.defaults.scale.grid.color` (the default gridline color). When chart configs override these with hardcoded hex values, the override wins and the colors do not respond to theme changes.

**Comparison:** Kentucky's chart configs (4 charts across phases 03 and 04) hardcode no tick/grid/legend colors and use only documented GitHub-palette dataset colors (`#0969DA`, `#BF8700`, `#BF3989`). Florida's chart configs (8 charts across phases 01, 03, 04) follow the same pattern with `#0969DA`, `#BF8700`, `#CF222E`, `#1A7F37`, `#8250DF`. Penobscot's initial configs hardcoded `ticks: { color: '#000000' }`, `grid: { color: 'rgba(0,0,0,0.12)' }`, and `legend.labels: { color: '#000000' }`. Penobscot also used `#000000` as a second-series dataset color for the NCSBN comparison and "Did Not Retake" series, neither of which is in the documented GitHub palette.

**Fix:** strip every hardcoded `ticks.color`, `grid.color`, and `legend.labels.color` from chart configs. Let Chart.defaults (set globally by the site-level `chart.js` override; see BUG-035) drive these. Replace `#000000` second-series with `#BF8700` (GitHub gold), which is production-validated in Kentucky 04's 5-year moving-average line. Final Penobscot palette: `#0969DA` blue and `#BF8700` gold across all four charts.

**Rule:** chart configs should hardcode only documented dataset colors from the GitHub palette (`#0969DA`, `#BF8700`, `#CF222E`, `#BF3989`, `#1A7F37`, `#8250DF`). Never hardcode tick colors, grid colors, or legend label colors; let `Chart.defaults` (theme-aware via Blowfish) handle them. Never use `#000000` or `#FFFFFF` as dataset colors; both are invisible in one of the two themes.

**Prevention discipline:** before declaring a chart finished, view the page in both light and dark mode. The bug is invisible in light mode and silent in build output; only visual inspection catches it. Hard-refresh the page after toggling theme (Cmd-Shift-R) because Chart.defaults are evaluated once at script-load and don't live-update on theme toggle without a page reload.

First encountered: Penobscot case study Phase 01/03/04, May 2026. Four charts deployed with hardcoded black tick/grid colors and one black dataset hue. Discovered by viewing each phase page in dark mode after the initial chart deployment. Patched by replacing the four chart configs in a single sweep; final hex audit confirmed only `#0969DA` and `#BF8700` remained.

### BUG-035: Site-level asset override of `assets/js/chart.js` is not picked up by Hugo Pipes; use `extend-footer.html` partial instead

**Symptom:** the site needed Chart.js's default text color (`Chart.defaults.color`) and grid line color (`Chart.defaults.scale.grid.color`) to be theme-aware so axis labels would automatically render in the correct contrast color in both light and dark mode. The Hugo-canonical approach is to override `themes/blowfish/assets/js/chart.js` by creating `assets/js/chart.js` at the project root, which Hugo Pipes is supposed to prefer over the theme version. Created the override file with three additional lines: `Chart.defaults.color = css("--color-neutral-700")`, `Chart.defaults.borderColor = css("--color-neutral-300")`, and `Chart.defaults.scale.grid.color = css("--color-neutral-200")`. Forced a full rebuild with `rm -rf resources/_gen/assets public/js/chart.bundle.*.js && hugo --cleanDestinationDir`. The resulting bundle did NOT contain the override; bundled output was the theme version verbatim.

**Diagnostic:** after creating `assets/js/chart.js` and forcing a rebuild, run `grep -c "neutral-700" public/js/chart.bundle.*.js`. If the count is 0, the override is not in the bundle. Confirm by `tail -c 800 public/js/chart.bundle.*.js` and visually checking the end of the minified bundle for the expected `Chart.defaults.color=css("--color-neutral-700")` call.

**Cause:** Blowfish's `vendor.html` partial uses `resources.Get "js/chart.js"` which in standard Hugo SHOULD resolve `assets/` at the project root first and fall back to `themes/blowfish/assets/` only if missing. In this codebase the override resolution does not work; the bundle continues to pick up the theme version. Why is unclear (possibly a Hugo version-specific behavior, possibly an unstated asset mount config). Investigation budget was not justified when a different mechanism works cleanly.

**Solution (the correct one):** use the `extend-footer.html` partial pattern. Blowfish's `footer.html` (and the site-level override of footer.html in this codebase) contains a hook block:

```hugo
{{ if templates.Exists "partials/extend-footer.html" }}
  {{ partialCached "extend-footer.html" . }}
{{ end }}
```

Create `layouts/partials/extend-footer.html` with an inline script that runs after Chart.js loads. The script lives entirely in YOUR repo (not in the Blowfish submodule), so it survives Blowfish updates and never triggers a fork suggestion in GitHub Desktop.

```html
<script>
  (function() {
    if (typeof Chart === 'undefined') return;
    function css(name) {
      return "rgb(" + getComputedStyle(document.documentElement).getPropertyValue(name) + ")";
    }
    Chart.defaults.color = css("--color-neutral-700");
    Chart.defaults.borderColor = css("--color-neutral-300");
    if (Chart.defaults.scale && Chart.defaults.scale.grid) {
      Chart.defaults.scale.grid.color = css("--color-neutral-200");
    }
  })();
</script>
```

The `typeof Chart === 'undefined'` guard means the script is a no-op on pages without charts. It is safe to inject on every page; the cost is roughly 800 bytes of inline HTML and a single guard check.

**Rule:** when customizing Chart.js (or any other vendored JS in Blowfish), do NOT edit the theme file directly even though it would work. Use the `extend-head.html` (loaded in `<head>`) or `extend-footer.html` (loaded near `</body>`) partial pattern. The partials hook is defined in the site-level `layouts/partials/footer.html` override and survives Blowfish updates without modification.

**Anti-pattern that surfaced first:** the initial fix was to append the override lines directly to `themes/blowfish/assets/js/chart.js`. This works locally (the bundle picks up the modified theme file) but GitHub Desktop sees the modification as a pending commit on the Blowfish submodule, prompts the user to fork the Blowfish repo, and creates pressure to either fork (which is wrong; Blowfish is a third-party theme) or discard the work. The `extend-footer.html` mechanism produces the same runtime behavior without any of those problems.

**Prevention discipline:** for any Chart.js customization, KaTeX setting, Mermaid config, or other vendored-JS-default the site needs to adjust, write the customization as an inline script in `layouts/partials/extend-footer.html`. Never edit files inside `themes/blowfish/`. If a theme file MUST be modified (rare), document why in this README and explain how to track upstream changes.

First encountered: May 2026, during the Penobscot chart contrast fix (BUG-034). The initial workaround was a direct edit of the theme; the proper solution via `extend-footer.html` was identified after GitHub Desktop surfaced the submodule modification and offered to fork Blowfish. After switching to the `extend-footer.html` mechanism, the Blowfish submodule has zero modified files (the only untracked file is the harmless backup left from the initial workaround, removable via `rm`).

### BUG-036: SQL number formatting via `printf('%,d', expr)` portfolio convention

**Symptom:** Case study prose tables formatted large integers with thousand separators (e.g., `1,514` first-attempts, `36,610` field_of_study rows, `102,672` median earnings). The same queries' SQL blocks displayed identical integers without separators (`1514`, `36610`, `102672`). Datasette Lite users clicking the "Run this query" link saw the un-formatted version. Two parallel displays of the same data created visual dissonance.

**Diagnostic:** in any prose result table, check whether values >= 1,000 use comma separators. If yes, check whether the corresponding SQL block produces values with the same formatting. If the SQL produces raw integers, the formatting is inconsistent.

**Solution:** wrap all large-integer-returning columns in `printf('%,d', expr)` inside the SELECT clause. SQLite's `printf` function with the `%,d` format specifier inserts thousand separators into integer output. The function is available in SQLite 3.38+ (the local environment runs 3.51, and Datasette Lite uses sql.js >= 3.45). Verified on the live databases: `SELECT printf('%,d', 1514)` returns the string `'1,514'`.

**Rule:** integer columns that can grow beyond 1,000 should be wrapped in `printf('%,d', expr)` in their SELECT clause. Percentage columns already ROUND'd to 1-2 decimals are left unwrapped (they display correctly without separators). Dollar columns formatted as millions (`ROUND(x/1e6, 1)`) are left unwrapped (values like `198.5` would be corrupted by comma insertion).

**Pattern that works:**
```sql
SELECT
    campus                          AS "Campus",
    printf('%,d', COUNT(*))         AS "First Attempts",
    ROUND(100.0 * AVG(result), 2)   AS "Pass Rate %"
FROM attempts
WHERE attempt_number = 1
GROUP BY campus;
```

The first column is a label, the second is wrapped (4-digit integers expected), the third is a percentage (already decimal-formatted, do not wrap).

**Categories of columns:**
- WRAP: `COUNT(*)`, `SUM()`, `CAST(... AS INTEGER)` returning values >= 1,000 (e.g., row counts, enrollment totals, dollar amounts in raw form)
- DO NOT WRAP: percentages (`ROUND(100.0 * AVG(...), 2)`), CI bounds, ratios, small integers (term ordinals, single-digit attempt numbers), dollar amounts already in millions form (`/1e6`)

**Prevention discipline:** when adding any SQL block to a case study, identify which columns return integer values >= 1,000 and wrap them in printf. Verify against the live database that the SQL executes and returns formatted output before declaring the block correct. Both local SQLite (3.51 on the build machine) and Datasette Lite (sql.js >= 3.45) support `%,d`.

**Portfolio totals as of May 2026:**

| Case Study | Phase 01 | Phase 02 | Phase 03 | Phase 04 | Total |
|---|---|---|---|---|---|
| Penobscot | 4 | 0 | 9 | 8 | 21 |
| Kentucky | 2 | 5 | 5 | 0 | 12 |
| Florida | 3 | 24 | 4 | 10 | 41 |
| **Portfolio** | **9** | **29** | **18** | **18** | **74** |

Kentucky Phase 04 is 0 printfs because every result column is millions-formatted (`ROUND(x/1e6, 1)`). Florida Phase 02 is high (24 printfs) because the fill-rate audit and MSI flag audit queries have many UNION ALL legs, each with two integer columns.

**Known limitation:** the Datasette Lite URLs embedded in case study markdown still encode the OLD pre-printf SQL queries. Clicking the link runs the un-formatted version; the SQL block on the page shows the printf-wrapped form. Re-encoding every URL is a follow-up pass: the prose result tables already show formatted numbers, and the SQL block reads correctly, so the inconsistency is at the level of "what runs when you click" not "what the page shows." Future cleanup: programmatically re-encode every Datasette Lite URL to match its current SQL block.

First encountered: portfolio-wide sweep, May 2026. The Penobscot case study's prose tables used `1,514` formatting from the start, but the SQL blocks used raw `1514`. Extending to Kentucky and Florida revealed identical inconsistency. Applied as 74 patches across the three case studies in one session.

### BUG-037: Patch script regression caused by lost-then-reapplied state

**Symptom:** the Penobscot Phase 01 SQL printf patches were applied and verified end-to-end (local DB sanity-check returned `7,635 / 6,819` and `1,514` matching prose). Three patch cycles later (during the Phase 04 patch attempt), a portfolio-wide audit showed Phase 01 had 0 printfs while Phase 03 retained its 9. Phase 01 had regressed silently.

**Diagnostic:** any time a multi-phase patching session involves shared shell state (cache clears, builds, file operations across multiple directories), do a post-session audit of each phase's expected patches. The audit is `grep -c "expected_string" <file>` for each phase. A zero where there should be N patches indicates regression.

**Likely cause:** during the asset-override debugging for BUG-035, the command `rm -rf resources/` was run to force Hugo to invalidate its cache. The directory deletion did not touch content/ files, but Hugo's hot-reload mechanism may have re-emitted a cached older version of the file when the dev server detected the missing resources directory. Alternative hypothesis: an editor's auto-save replayed an older buffer onto disk. The exact mechanism was not identified; the regression was recovered by re-applying the Phase 01 patch from a fresh backup.

**Rule:** for multi-phase patching sessions, retain `.backup-pre-<stepname>` files for every phase across every step. The full backup chain provides a complete recovery path. When regression is detected, identify which step's backup is the rollback target and re-apply later steps from there.

**Prevention discipline:** when running cache-clearing commands (`rm -rf resources/`, `rm -rf public/`, `hugo --cleanDestinationDir`), verify content/ files immediately after with `grep -c <pattern> content/<path>` to confirm nothing in content/ regressed. The check costs 1 second and prevents silent rollback. If a dev server is running, restart it after any `rm -rf` to avoid stale-cache re-emission.

First encountered: Penobscot SQL-formatting sweep, May 2026. Phase 01 lost its 4 printfs between Step 7 verification and Step 7 Phase 04 attempt. Detected by post-Phase-04 portfolio audit. Recovered by re-applying the Phase 01 patch as part of the Phase 04 script (`step7_p01_p04_redo.py`). After the redo, Phase 01 had 4 printfs and Phase 04 had 8 printfs, matching plan.

### BUG-038: Markdown tables render left-pinned; centering the block needs `width: fit-content`, not just `margin: auto`

**Symptom:** Markdown tables sit against the left edge of the content column with dead space to their right. Cell *text* can be centered with the `:---:` column-alignment syntax, but the table *block* stays left, and `margin-left/right: auto` on the table has no visible effect.

**Cause:** Blowfish styles article content with the Tailwind Typography (`prose`) plugin, which renders the table to fill the full content width as a block. A box already at full width has no horizontal slack, so `margin: auto` has nothing to distribute and cannot center it; the cell grid simply shrink-wraps to the left inside the full-width box. Separately, Typography sets `'th, td': { text-align: start }` with no `!important` and a `:where()` (single-class) specificity, which is why an inline `style="text-align: center"` emitted by Hugo from `:---:` overrides it and the cell text *does* center while the block does not.

**Fix:** Give the table `width: fit-content` first (shrinks the box to its content width), then `margin-left: auto; margin-right: auto` to center the now-narrower box; `max-width: 100%` keeps it inside a narrow viewport. A backstop `th, td { text-align: center }` guarantees cell centering independent of the inline style. Canonical home is `assets/css/custom.css` (loaded after theme styles, so no `!important` is needed there), alongside the existing figure-centering rule:

```css
.prose table, article table {
  width: fit-content;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
}
.prose th, .prose td { text-align: center; }
```

The despacho "2026 Job Application Paradox" essay carries the same rule in its page-scoped `<style>` block (with `!important`, since an inline block's order relative to theme CSS is less predictable) as an interim measure. Once the `custom.css` rule is in place, the inline duplicate can be removed.

**Detection:** in devtools, a header cell computes `text-align: center` (cell text is fine) but the `<table>` computed width equals the container width while its visible content is narrower, the tell that the block is full-width and needs `fit-content`. Confirmed via console: `getComputedStyle(table).width` vs `table.parentElement.clientWidth`.

First encountered: despacho "2026 Job Application Paradox" essay, May 2026.

### BUG-039: KaTeX math fixed permanently by Goldmark passthrough; single-backslash delimiters are now correct (supersedes the double-backslash workaround in BUG-017 and BUG-029)

**This is the root-cause resolution of BUG-017 and BUG-029. Read this before applying either of those older entries; their double-backslash workaround is now obsolete and will PREVENT rendering.**

**Root cause (the thing both older bugs were symptoms of):** Hugo's Goldmark renderer applies normal Markdown processing (emphasis, escape sequences, smartypants) to math source BEFORE KaTeX's client-side auto-render runs. Two distinct corruptions result. Inline `\(...\)` has its backslashes eaten as Markdown escapes, leaving bare `(...)` that KaTeX ignores (this was BUG-017). Display `\[...\]` containing `}_{...}` or any `_x ... _y` pattern has the underscores parsed as emphasis and rewritten to `<em>` tags inside the formula, so KaTeX receives malformed LaTeX and renders raw source (this was BUG-029). The double-backslash workaround papered over the symptom by surviving Goldmark in SOME contexts, but it was fragile: whether the delimiter collapsed or stayed literal depended on the surrounding Markdown context, which is why some formulas rendered and visually identical ones did not.

**Permanent fix:** enable the Goldmark passthrough extension in `config/_default/markup.toml`. Passthrough tells Goldmark to leave the delimited regions completely untouched (no emphasis, no escape handling, no smartypants), so math reaches the HTML verbatim and KaTeX renders it. The exact block:

```toml
[goldmark.extensions.passthrough]
  enable = true
  [goldmark.extensions.passthrough.delimiters]
    block = [['\[', '\]'], ['$$', '$$']]
    inline = [['\(', '\)']]
```

**Current correct convention (use this from now on):** write math with SINGLE-backslash delimiters. Display: `\[ ... \]`. Inline: `\( ... \)`. This is internally consistent across the whole pipeline: the passthrough config matches single-backslash, KaTeX's default `renderMathInElement` matches single-backslash, and the source files are single-backslash. Underscores, `}_{` patterns, and primes inside math are all safe because passthrough stops Goldmark from touching them. The `{{< katex >}}`-before-`{{< lead >}}` ordering rule (BUG-003) still applies and is unaffected.

**Do NOT use double-backslash anymore.** With passthrough configured for single-backslash, a double-backslash delimiter no longer matches the passthrough pair, so Goldmark would process it normally again and the underscore/escape corruption returns. The double-backslash workaround and passthrough are mutually exclusive; the project is now standardized on passthrough plus single-backslash.

**Requires:** Hugo 0.122.0 or newer (passthrough landed Feb 2024). Verified on Hugo 0.163.2 extended.

**Detection that passthrough is working:** after a clean rebuild, view the built HTML for a math-heavy page. A correctly-passed formula appears with its underscores intact (`\hat{Y}_{\text{TX},t}`), no `<em>` tags inside the delimiters. If you see `<em>` inside a formula, passthrough is not matching that delimiter; check that the delimiter in the source matches the configured pair exactly.

First resolved: texas-synthetic-control case study, June 2026, after the case study's heavily-subscripted display formulas exposed the fragility of the double-backslash workaround across all four phase files.

### Eon Color Palette: Colorblind-Safe and Theme-Aware (despacho deep-time essay)

The deep-time essay tags each geologic eon with one fixed color that repeats across the scale bar, the at-a-glance timeline rows, and the eon section headings, so a reader learns one color per eon. The palette is the Okabe-Ito colorblind-safe set (yellow and black dropped, leaving six), reordered warm/cool so neighboring eons never share a hue family:

| Eon | Light | Okabe-Ito name |
| --- | --- | --- |
| Hadean | `#D55E00` | vermillion |
| Archean | `#56B4E9` | sky blue |
| Proterozoic | `#E69F00` | orange |
| Paleozoic | `#009E73` | bluish green |
| Mesozoic | `#CC79A7` | reddish purple |
| Cenozoic | `#0072B2` | blue |

Two of the six are blues (sky blue and blue): they sit at positions 2 and 6, so they are never adjacent in the bar or in consecutive timeline rows.

Theme adaptation. The colors are CSS custom properties (`--eon-hadean` through `--eon-cenozoic`) declared in the page's inlined `<style>`. The `.dark` rule overrides only the colors too dim on the dark background, currently just Cenozoic, lifted from `#0072B2` to `#007FC6`. Every colored mark is a fill, border, or underline placed beside the eon's name, so color is always redundant with text and never the sole signal.

Bar labels. Only the three widest bands (Hadean, Archean, Proterozoic) carry a text label; the narrow three are label-free but stay hoverable and keyboard-focusable, with the detail surfaced in the info line below the bar. Label text is black on all three, chosen by WCAG contrast against the fill.

Verification. `tools/eon_palette_audit.py` prints, for both themes, the WCAG non-text contrast of each color against white and dark backgrounds, plus the adjacent-eon separation (CIE dE76) under deuteranopia, protanopia, and tritanopia via the Machado 2009 simulation. Reproduce with:

```bash
python3 tools/eon_palette_audit.py
```

Current result: every adjacent pair stays above dE76 18 under all three colorblindness types (worst case deuteranopia at 18.1), versus the earlier Tailwind-700 palette whose closest adjacent pair was an order of magnitude smaller.

---

## 11. Configuration Files

### `config/_default/hugo.toml`

```toml
theme = "blowfish"
baseURL = "https://pgbd.casa/"
defaultContentLanguage = "en"
languageCode = "en"

enableRobotsTXT = true
paginate = 10
summaryLength = 70           # see BUG-007

buildDrafts = false
buildFuture = false

enableEmoji = true
enableGitInfo = true         # see BUG-006

[outputs]
  home = ["HTML", "RSS", "JSON"]

[imaging]
  anchor = "Center"

[caches]
  [caches.images]
    dir = ":resourceDir/_gen"
    maxAge = "720h"
  [caches.assets]
    dir = ":resourceDir/_gen"
    maxAge = "720h"
```

### `config/_default/params.toml`: non-default values only

```toml
colorScheme = "github"
defaultAppearance = "dark"
autoSwitchAppearance = true

enableSearch = true
enableCodeCopy = true

[homepage]
  layout = "page"
  showRecent = false
  cardView = false

[article]
  mermaid = true             # required for Mermaid diagrams
  showLastUpdated = true
  showDate = false
  showAuthor = false
  showReadingTime = false
  showTableOfContents = true
  showWordCount = false
  showRelatedContent = false
  showComments = false

[list]
  showSummary = true
  showCards = true
  cardView = true
  orderByWeight = true       # see BUG-006
  groupByYear = false
```

### `config/_default/languages.en.toml`

```toml
title = "⛫ pgbd's digital casa"

[params]
  description = "Mi casa digital es su casa digital. Personal portfolio and analytical work."

[params.author]
  name = "Philip Gregory Bachas-Daunert"
  headline = "Data analyst at the University of Miami Miller School of Medicine"
  bio = "Humanities to analytics, the long way."
  links = [
    { github = "https://github.com/hihipy" },
    { linkedin = "https://linkedin.com/in/pbachas/" },
    { email = "mailto:pgbd.kipol@passmail.net" }
  ]
```

### `config/_default/menus.en.toml`

Three social links: linkedin, email, github. Order via `weight` field (10, 20, 30).

### `config/_default/markup.toml`

Existing markup configuration. Inspect before modifying.

---

## 12. Directory Layout

```
hihipy.github.io/
├── README.md                           # this file
├── assets/
│   ├── css/
│   │   └── custom.css                  # custom Blowfish CSS overrides
│   ├── icons/                          # 25 SVG icons (see §9)
│   └── img/
│       ├── favicon-source.svg          # donut chart favicon source (see §9)
│       └── logo.svg                    # site logo
├── config/_default/
│   ├── hugo.toml                       # Hugo core config
│   ├── languages.en.toml               # English language pack
│   ├── markup.toml                     # markup options
│   ├── menus.en.toml                   # social link menu
│   └── params.toml                     # Blowfish theme params
├── content/
│   ├── _index.md                       # home page (has summary field)
│   ├── puerta/_index.md                # door / résumé room (has summary field)
│   ├── sala/index.md                   # about page, regular page (has summary field)
│   ├── mirador/_index.md               # dashboard philosophy methodology room
│   ├── taller/_index.md                # built dashboard applied room (placeholder)
│   ├── obrador/_index.md               # tool-building philosophy methodology room
│   ├── cocina/
│   │   ├── _index.md                   # room landing
│   │   └── <project>.md × 4
│   ├── estudio/
│   │   ├── _index.md
│   │   └── <project>.md × 3
│   ├── garaje/
│   │   ├── _index.md
│   │   └── <project>.md × 5
│   └── jardin/
│       ├── _index.md
│       └── <project>.md × 4
├── layouts/
│   ├── 404.html                        # custom casa-style 404 (see §9)
│   ├── partials/
│   │   ├── footer.html                 # custom footer override
│   │   └── header.html                 # custom header override
│   └── shortcodes/
│       ├── section-count.html          # custom shortcode (see §9)
│       └── swatch.html                 # inline color swatch (see §9), used in mirador
├── static/
│   ├── CNAME                           # GitHub Pages custom domain (pgbd.casa)
│   ├── android-chrome-192x192.png      # PWA icons (donut chart)
│   ├── android-chrome-512x512.png
│   ├── apple-touch-icon.png            # 180×180
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   ├── favicon.ico                     # multi-resolution: 16, 32, 48
│   ├── fonts/
│   │   ├── AtkinsonHyperlegible-Regular.woff2     # body and h2-h6 (BUG-016)
│   │   ├── AtkinsonHyperlegible-Italic.woff2
│   │   ├── AtkinsonHyperlegible-Bold.woff2
│   │   ├── AtkinsonHyperlegible-BoldItalic.woff2
│   │   └── MonoLisaVariable.woff2                 # H1 titles, typeit, code
│   ├── resume.pdf                      # served at /resume.pdf
│   └── site.webmanifest
└── themes/blowfish/                    # theme submodule (NOT in this README)
```

**Important:**
- `content/sala/index.md` is a single-file page, NOT `_index.md` (no underscore). This makes `/sala/` a regular page with body content rather than a section listing.
- `content/puerta/_index.md` is a section index because puerta is technically a section (with no children currently).
- `static/resume.pdf` is served verbatim at `/resume.pdf` regardless of which content page links to it.
- Favicon files are donut chart in github palette, see BUG-009. Source SVG at `assets/img/favicon-source.svg`.
- The `pgbd.us` redirect alias is configured in Cloudflare DNS + Rules, see §1. Not a file in this repo.

---

## 13. Adding a New Project Page: Procedure

When adding a new project to the portfolio, follow this exact procedure.

### Step 1: Decide the room

Match the project to a room based on its primary purpose:

| If the project... | Goes in |
|---|---|
| ...prepares, cleans, or transforms data | `cocina` |
| ...uses AI/LLMs as a primary feature | `estudio` |
| ...is a utility tool for analysts (Excel, calculators, processing) | `garaje` |
| ...is a personal/creative side project unrelated to professional work | `jardin` |

If the project is genuinely cross-cutting, prefer the room where the project's *primary distinguishing feature* lives (its differentiator, not its substrate).

### Step 2: Author the page

Create `content/<room>/<repo-name>.md` using the template in §6. Author all four text tiers (summary, lead, description, body) deliberately per §5. Match the tone conventions in §7.

**Checklist before saving:**

- [ ] `title` matches the GitHub repo name exactly
- [ ] `description` is 30-50 words, recruiter-readable
- [ ] `summary` is 3-6 words (CRITICAL for clean search results, see BUG-010)
- [ ] `tags` includes language, libraries, and domain
- [ ] Any new tag introduced by this project is also added to the `card.html` map in alphabetical position (see §9)
- [ ] Any new tag also has a matching `content/tags/<new-tag>/_index.md` file with title matching the `card.html` map value (see §9, BUG-031). Re-run `tools/create_tag_term_pages.py` after updating the script's canonical list
- [ ] `weight` is set; will be re-assigned in Step 3
- [ ] `{{< lead >}}` block is 12-20 words
- [ ] `{{< katex >}}` is BEFORE the lead block if math is used (BUG-003)
- [ ] All Mermaid node labels are double-quoted (BUG-004)

### Step 3: Re-assign weights

After adding the new file, ALL files in that room must have their weights re-assigned to maintain alphabetical order.

```python
# Pseudocode for the resort
files = sorted(<room>/*.md)
for i, file in enumerate(files):
    file.weight = (i + 1) * 10
```

The room's project list in §4 of this README must also be updated.

### Step 4: Verify locally

```bash
hugo server -D
```

Visit `http://localhost:1313/<room>/` and confirm:

- The new project appears in alphabetical order
- The card shows the summary text (3-6 word label)
- Clicking through opens the project page
- The lead block renders styled at the top
- Math expressions (if any) render correctly
- Mermaid diagrams (if any) render correctly
- Press `/` and search for the new project; it should appear with a clean compact summary (BUG-010)

### Step 5: Update the home page count automatically

The `section-count` shortcode auto-updates. No manual intervention needed.

### Step 6: Commit and deploy

Commit and push to `main`. Deployment is automatic via GitHub Pages.

### Regenerating the favicon

If the favicon design needs to change, regenerate from `assets/img/favicon-source.svg`:

1. Edit the SVG (segments, colors, geometry as needed)
2. Run a Python script using PIL to render PNG variants at sizes 16, 32, 180, 192, 512
3. Build favicon.ico as a multi-resolution ICO containing 16, 32, 48
4. Place all output files in `static/` replacing the existing icons
5. Hard-refresh the browser (Cmd+Shift+R) to bust the favicon cache

The full generation script used to produce the current favicon set is preserved in this session's history.

---

## 14. Build and Deploy

### Local development

```bash
cd hihipy.github.io
hugo server -D
# visit http://localhost:1313/
```

### Production build

GitHub Pages handles this automatically on push to `main`. No manual build step.

### Deployment URL chain

`main` branch push → GitHub Pages builds → serves at `https://hihipy.github.io` → CNAME redirects to `https://pgbd.casa`. Separately, `https://pgbd.us` 301-redirects to `https://pgbd.casa` via Cloudflare, see §1.

---

## 15. Account & Access Security

This section documents the security posture the site is built around. It is operational reference, not configuration. None of these items live in the repo.

### Critical accounts

The site's integrity depends on three distinct accounts being independently secured:

1. **GitHub** (`hihipy`). Holds the repo and serves the Pages site. A compromise here lets an attacker push arbitrary content to `pgbd.casa`.
2. **Cloudflare**. Holds DNS for `pgbd.us` and the redirect rule. A compromise here lets an attacker redirect `pgbd.us` traffic anywhere.
3. **Domain registrar(s)**. Hold the registrations for `pgbd.casa` and `pgbd.us`. A compromise here lets an attacker move the domains entirely.

Each account has its own credentials and its own 2FA. They are not linked via OAuth or shared sign-in.

### Posture requirements

- All three accounts use 2FA. Hardware security keys preferred where supported; TOTP via authenticator app otherwise. SMS 2FA is not sufficient.
- Recovery codes for each account are stored offline.
- The recovery email address has its own strong 2FA, since email is the universal account-reset channel.
- Registrar locks (transfer lock and update lock) enabled on both domain registrations.

### Avoided by design

Cloudflare is not authenticated via "Sign in with GitHub" or any other OAuth provider. Cloudflare uses an independent password and independent 2FA. This is intentional: it prevents a GitHub account compromise from automatically becoming a DNS takeover. Do not re-link the two without re-evaluating this tradeoff.

### Maintenance triggers

Re-verify the posture above whenever:

- A 2FA device is added, replaced, or lost
- The recovery email address changes
- A new admin or member account is created on any of the critical services
- An OAuth integration is added or removed between any of the three account systems

---

## 16. Outstanding Items / Known Issues

| Item | Notes |
|---|---|
| Sala description discrepancy | The `description` field in `content/sala/index.md` says "Institutional research analyst" but other contexts (the Blowfish `[params.author]` headline) say "Data analyst." If they refer to the same role under different terminology, fine. If alignment is desired, update the sala frontmatter. |
| Four unused icons | `building-columns`, `certificate`, `compass`, `house` in `assets/icons/` are not referenced anywhere. Kept available for future use. The `certificate` icon is the most likely candidate for sala's Certifications section if one is added. |
| Newly-registered domain blocking | The University of Miami network has been observed blocking both `pgbd.casa` and `pgbd.us` for some time after each domain's registration. This is BUG-011, a generic enterprise filter for newly-observed domains, not site-specific. Expected to resolve on its own after 30-90 days as the domains age. Affects only highly-restrictive corporate networks; the site is accessible from cellular, residential, and most non-restrictive networks. |

---

## 17. Working with AI on Analytical Content

When using AI assistants to help write case studies, dashboards, or any content where claims are backed by data, the failure mode documented in BUG-024 is real and recurring. AI assistants will generate plausible-looking numbers, organization names, dates, and percentages that match the surrounding prose narrative. These look correct, read correctly, and may even be internally consistent across a multi-page document. They are still wrong if they were not generated by running an actual query.

This section documents the discipline that prevents fabrication. The principles apply to any AI-assisted analytical work, not just SQL on the kentucky-nih dataset.

### Verify before writing prose around a result

The order of operations matters. The wrong order is: write the SQL, write prose around plausible-looking output, hope the SQL produces something close. The right order is: write the SQL, run it, capture the real output, then write prose around the captured output.

For a SQL case study, the workflow is:

1. Draft each SQL query in isolation.
2. Run each query against the actual database. Capture the output with `sqlite3 -header -column path/to/database.sqlite "SELECT ..."`.
3. Paste the captured output into a verification document or send it to the AI assistant alongside the request to draft prose.
4. The AI drafts prose, result blocks, and any chart data arrays from the captured output.
5. After draft, re-run every query and confirm the result blocks in the prose match the live output exactly.

Step 3 is the load-bearing step. An AI assistant given verified query output will work from it. An AI assistant not given verified output will generate plausible numbers and present them confidently. The difference between fabrication and reproducibility is whether the captured output entered the assistant's context window before prose was written.

### Send the AI assistant real data, not the schema alone

A common failure pattern: the assistant is told "the schema has columns X, Y, Z" and asked to draft a case study. The assistant correctly writes queries against the schema, then generates plausible-looking output that matches the prose narrative. The schema description is not enough; the actual query output is.

For analytical case studies on real data, the human should run the queries first and send the captured output. For dashboards or visualizations, the human should provide the actual data points (or a representative sample), not just the data shape.

### After-draft verification is the floor

Even when the workflow above is followed, verify the final document by running every query and confirming the result blocks match. This catches:

- Queries the assistant modified during drafting (added a `LIMIT`, changed a sort, dropped a column) that no longer produce the captured output
- Numbers that drifted during prose revision (the captured output said 7,835 projects, the prose says 7,541 because someone "rounded" or "cleaned" the number during editing)
- Charts whose data arrays don't match the underlying query output
- Result blocks that have correct numbers but wrong column headers or wrong row order

The verification pass is short relative to the drafting work. It is the difference between a case study that reproduces and one that fails its own commitments.

### Treat AI output like an over-eager intern

The framing from the obrador philosophy applies directly: an AI assistant producing analytical content should be treated like work from an over-eager intern who is fast, capable, and confident, but who has not actually run the query and is filling in plausible numbers from context. Every number, organization name, date, and percentage requires verification before it ships. The intern doesn't know they're confabulating; they're trying to be helpful. The verification step is what turns helpful-looking work into trustworthy work.

### When the AI says it ran the query, ask to see the output

If an AI assistant claims to have run a query and gives you a result, ask to see the captured output (or the tool call that produced it). The assistant may have actually run the query, or it may have generated plausible output and labeled it as run. Without seeing the captured output, both look identical in chat.

In practice, only the human running the actual database environment can produce verified output. Treat any "result" the AI presents without explicit tool-call evidence as a draft to be verified against a real run.

### The reproducibility commitment is not aspirational

For case studies and analytical work that links to live databases or invites readers to re-run queries, every published number must reproduce. This is non-negotiable. A case study with prose that says "Kentucky NIH funding peaked at $260.9M in FY 2021" must produce $260.9M when a reader runs the query in Datasette Lite. The biblioteca page calls this reproducibility-is-the-floor: if the floor isn't there, nothing else holds.

For non-published work (drafts, internal exploration, scratch analysis), looser standards are acceptable. For anything that ships under your name and links to a live database, verification is the floor.

### Discipline for AI-assisted patch scripts

When working with an AI assistant to maintain analytical content (case studies, SQL queries, chart configurations), the assistant's output is typically a bash script that pipes content to Python via heredoc. This pattern is powerful but has failure modes that are invisible at write-time and only manifest at runtime. The following discipline catches them at write-time.

#### Pre-write Python compile check

Every patch script the assistant generates should be compile-checked before presentation. The check extracts the Python heredoc body from the bash script and runs `compile()` on it. If the compile succeeds, the script's Python is syntactically valid. If it fails, the script has a write-time error that would otherwise become a runtime error after the user runs it.

The compile check fires the same SyntaxError that the runtime would, but at write-time when the cost of fixing it is one iteration instead of one round-trip through the user.

Run this check before sharing any patch script. It catches BUG-026-class issues (f-string escape errors, malformed string literals, mismatched brackets, and any other Python syntax error) before they become a failed run-and-iterate cycle. The cost is one extra command per script; the benefit is one fewer round-trip when the script has a syntax error.

#### Bundle patch scripts inline; never rely on /tmp persistence

macOS aggressively cleans `/tmp`. A patch script created with `cat > /tmp/script.py <<'EOF' ... EOF` and then executed separately with `python3 /tmp/script.py` may fail silently with `Errno 2: No such file or directory` if the cleanup ran between the two commands. The user sees the script fail with no output and no backup files created; the patch never landed but no error surfaced clearly.

The fix is to chain creation and execution in a single shell command using `&&`:

```bash
cat > /tmp/script.py <<'EOF' && python3 /tmp/script.py
... script body ...
EOF
```

The `&&` ensures Python runs immediately after the heredoc closes, before macOS gets a chance to clean `/tmp`. The cost is one extra ampersand; the benefit is eliminating an entire class of silent failure.

**Rule:** for any multi-line patch script that needs to run once, use the inline pattern `cat > /tmp/<name>.py <<'DELIM' && python3 /tmp/<name>.py`. For scripts that need to be re-run later (e.g., during debugging), write them to a non-temporary location (the project's `tools/` directory or a `~/scripts/` directory).

#### Always quote heredoc delimiters

Default to a single-quoted heredoc delimiter (`<<'__DELIM__'` rather than `<<__DELIM__`) for any patch script. The single quotes around the delimiter tell bash to pass the heredoc body verbatim, disabling shell expansion. This prevents BUG-025 (literal `$NNN` getting shell-expanded into emptiness) and other expansion-related corruption.

The cost of quoted heredocs is zero. The cost of unquoted heredocs is one debugging cycle per `$` character in the body that the writer forgets about.

#### Atomic rewrites beat multi-patch sequences for complex content

When a target file contains many shortcodes, custom HTML wrappers, or other parser-sensitive constructs (Hugo chart shortcodes wrapped in styled divs, for example), accumulating fixes via multiple patches can introduce hard-to-diagnose issues that compound across patches. The Phase 04 chart-rendering bug in college-scorecard-fl is the canonical example: four patches added charts incrementally, charts failed to render despite the BUG-023 rule being apparently followed, four more patches tried to fix the rendering, and the issue was finally resolved by an atomic rewrite of the entire phase using a verified-working pattern from a sibling phase.

The rule: if a multi-patch sequence is already 3+ patches deep and the target output still has structural issues that don't reproduce in a sibling that was written cleanly, switch to atomic rewrite. Copy the verified-working pattern from the sibling and rewrite the target as a single replace operation. The cost is one larger patch; the benefit is the elimination of cumulative-bug hypothesis space.

#### Provide reproducer commands for every claim

When the assistant claims a bug is fixed (or a constraint is satisfied), the response should include the diagnostic command the user can run to verify. Phrases like "this should now work" without a verification command are weak; phrases like "run `bash script.sh`, then `grep -c 'pattern' file.md` should report N" are strong. The user is the verification step, and asking the user to verify with a specific command is a contract.

This applies to both audit-after-write and audit-before-write. Pre-write audits prevent the assistant from generating prose around projected output; post-write audits prevent the user from accepting changes that don't match the claim.

### Choosing the delivery mode: console fix vs download-to-repo

Two delivery modes cover almost every change to this repo. Picking the right one up front saves a round-trip.

**Run Python in the console; never paste it interactively.** When a change needs Python (an audit, a bulk find-and-replace, a generated file), the assistant should hand over a script delivered with a quoted heredoc and run in one chained command, not a block of Python to paste at an interactive prompt. Pasting multi-line Python into an interactive shell triggers `zsh: parse error` on the first blank line or dedent. The canonical pattern is the same inline, single-quoted-delimiter discipline documented above for patch scripts:

```bash
cat > /tmp/task.py <<'PYEOF' && python3 /tmp/task.py
# ... script body ...
PYEOF
```

It applies to any console Python, not only patch scripts. See "Bundle patch scripts inline" and "Always quote heredoc delimiters" for the why.

**Small things: fix in the console.** For an edit that is small and well-scoped (a typo, a frontmatter field, a weight renumber, a one-line CSS rule, a find-and-replace across a few files), do it directly in the console with a short script or a targeted replace. The change is faster to apply than to download, and the diff shows up in `git diff` immediately. Back up before in-place surgery on a tracked file: `cp file "file.backup-$(date +%Y%m%d-%H%M%S)"`.

**Big things: download to repo.** For a new page, a full rewrite, or any deliverable large enough that pasting or scripting it inline is error-prone (a new despacho essay, a regenerated case-study phase, a new tool), the assistant produces the complete file as a download. It lands in `~/Downloads`, and a single console command moves it into the repo at its final path. This keeps large content out of the chat-to-console copy path, where whitespace, smart quotes, and long heredocs are fragile, and it makes the repo the source of truth. The canonical move, reusable for any single-file handoff:

```bash
REPO="$HOME/Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
SRC="$HOME/Downloads/<filename>.md"
DST="$REPO/content/<room>/<filename>.md"

[ -f "$DST" ] && cp "$DST" "$DST.backup-$(date +%Y%m%d-%H%M%S)"   # backup only if overwriting
mv "$SRC" "$DST" && echo "Landed: $DST" && wc -l "$DST"
```

**The line between the two:** if the change fits comfortably in a heredoc body and reads clearly in `git diff`, it is a console fix. If it is a whole file authored from scratch or rewritten end to end, it is a download-to-repo handoff. When in doubt, download: a file move is cheaper than reconstructing content mangled in transit.

---

## 18. Glossary

| Term | Meaning |
|---|---|
| Casa | Spanish for house. Brand metaphor for the site. |
| Room | A top-level navigation section. Nine total. |
| Project page | A markdown file inside a project room (cocina/estudio/garaje/jardin). |
| Lead block | The `{{< lead >}}...{{< /lead >}}` shortcode, used for tier-2 elevator pitches. |
| Summary | The frontmatter `summary` field, used as tier-1 card label AND search result snippet. |
| Section count | The `{{< section-count <room> >}}` custom shortcode. |
| Blowfish | The Hugo theme (`themes/blowfish/`). Reference: https://blowfish.page/docs/ |
| Tier 1-4 | The complexity gradient. See §5. |
| Puerta-first | The convention that `puerta` (door) comes first on the home page. |
| Redirect alias | A second domain (`pgbd.us`) that 301-redirects to the canonical `pgbd.casa`. See §1. |

---

## 19. Reference Links

- Hugo docs: https://gohugo.io/documentation/
- Blowfish theme docs: https://blowfish.page/docs/
- KaTeX docs (used by `{{< katex >}}` shortcode): https://katex.org/docs/supported.html
- Mermaid docs (used by `{{< mermaid >}}` shortcode): https://mermaid.js.org/intro/
- Hugo shortcode reference: https://gohugo.io/templates/shortcode-templates/
- GitHub Pages custom domain setup: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site
- Cloudflare Redirect Rules: https://developers.cloudflare.com/rules/url-forwarding/single-redirects/

---

## 20. Document Maintenance

This README is the canonical reference for the codebase. When making non-trivial changes to the site, update the relevant section here. Specifically:

- §1 if domain configuration changes (new domains, expired registrations, etc.)
- §3 if room structure changes
- §4 if a project is added, removed, or renamed
- §6 if the project page template changes
- §10 when new bugs are discovered
- §11 when configuration is changed
- §15 when account security posture changes (new accounts, new 2FA devices, OAuth re-coupling, recovery email change)
- §16 when known issues are resolved or new ones found
- §17 when AI-assisted analytical work surfaces a new failure mode worth documenting, or when the verify-before-prose workflow gains new techniques

The README is intentionally dense. It is not meant to be read sequentially; it is meant to be searched and referenced by section.

### BUG-040: Site-wide dark-mode chart theming via one global adapter; per-theme series swap, computed-color theme detection, and the real dark canvas (supersedes the defaults-only script in BUG-035 and retires the per-page adapters of BUG-019)

**This is the consolidation of all per-page chart theming into a single mechanism. Read this before applying BUG-019 (per-page adapter) or BUG-035 (defaults-only override); both are now superseded by the global adapter in `layouts/partials/extend-footer.html`.**

**What changed and why.** Charts had three different theming mechanisms across the site: BUG-035's defaults-only script (set `Chart.defaults` once at load, no live toggle, did not repaint already-constructed charts), the per-page `Chart.getChart` adapters on taller and the paradox essay (BUG-019), and first-trillion's `window.__tc()`/`__gc()`/`__retheme` helpers. Three mechanisms meant three places to fix and inconsistent behavior: some charts themed text but not series colors, none swapped series colors for maximum per-theme contrast, and the live toggle worked on some pages and not others. The global adapter replaces all of this with one script that themes every chart on every page, in both modes, live on toggle.

**The mechanism.** `extend-footer.html` is injected as the last item in the footer on every page (Blowfish includes `layouts/partials/extend-footer.html` automatically via `partialCached` in the theme footer). After Chart.js loads, the adapter:

1. Reads the live theme from the computed text color's luminance, not the `html.dark` class. The class is reliable here, but the computed color cannot lie and survives any class/appearance desync. Luminance above 140 means light text, which means dark mode.
2. Swaps every series color via a canonical light-to-dark map (below), idempotent and directional: light-to-dark only when dark, dark-to-light only when light, so a value that is already a dark partner is never re-mapped as if it were a light key.
3. Repaints tick, axis-title, legend, and chart-title colors from the computed text color, and gridlines from a fixed low-alpha gray (`rgba(128,128,128,0.22)`) that reads on either background.
4. Themes the tooltip box to match the page rather than leaving the Chart.js default dark box.
5. Re-runs all of this on a `MutationObserver` watching `<html>` class changes, so the toggle is live without a reload.

**Two failures cost most of the debugging time; both are documented here so they are not repeated.**

First, an inherited top-level guard. The script began with `if (typeof Chart === 'undefined') return;`, carried over from BUG-035's defaults-only script, which only needed Chart at the instant it ran. The global adapter must instead WAIT for Chart, because on some pages the adapter executes before the Chart.js bundle finishes loading. The early return killed the entire adapter before its retry loop could run, so the script was present in the page but did nothing. The fix is to remove the top-level guard and let `init` retry (`setTimeout(init, 300)`) until both `Chart` and the constructed charts exist.

Second, fabricating partial option objects crashes Chart.js. An earlier version set `s.grid = s.grid || {}` then assigned a color, creating a bare grid object with only a color field. Chart.js then resolved the object's other scriptable properties and called `.startsWith` on a non-string, throwing inside `chart.update()` and aborting the repaint partway. The rule: only write color onto `ticks`, `title`, and `grid` objects that the chart config already defined; never fabricate them. For axes that define no such object, the color comes from `Chart.defaults`, which the adapter sets.

**The real dark canvas is `#14191F`, not `#0F172A`.** The `github` scheme reverses its neutral scale under `.dark`, and the rendered body background in dark mode is neutral-800 (`#14191F`, confirmed by reading `getComputedStyle(document.body).backgroundColor` in the browser, which returns `rgb(20,25,31)`), not neutral-900 (`#0F172A`) as the audit tool previously assumed. The contrast difference between the two is below any grade boundary, so it changed zero verdicts, but the tool now grades against the measured value. The fix in `audit_figures.py` was to repoint the DEFAULT entry of the neutral reversal table to step 800.

**Theme detection: computed color, not the class.** Copied from first-trillion's working `__tc` helper. The adapter reads `getComputedStyle(.prose || article || main || body).color` and decides dark from its luminance. This is the single most important correctness choice in the adapter; every earlier version that read `html.dark` directly hit edge cases where the class and the rendered appearance disagreed.

**first-trillion keeps its own helpers, by design.** Unlike taller and the paradox essay, whose inline adapters were self-contained and were removed, first-trillion's chart configs call `window.__tc()` and `window.__gc()` inline at construction time in dozens of places (`borderColor: window.__tc()`, `grid: { color: window.__gc() }`, and so on). Those helpers are load-bearing dependencies of the configs, not just a duplicate adapter. Deleting the helper block would throw `window.__tc is not a function` at construction and the charts would not render at all. The helpers and the global adapter do not conflict (both read the computed color and set the same fixed grid), and the global adapter still handles first-trillion's series swaps on top. So first-trillion is the one page that keeps inline theming code, and that is correct.

**Canonical light-to-dark series map (20 pairs).** Light values are the existing saturated series colors, all of which already clear the 3:1 chart-mark floor on white. Each dark partner is the brightest tint that still reads as the hue and stays CVD-distinct, sourced from GitHub's own dark accent palette for the github-scheme colors and from the existing taller pairs for the Okabe-Ito and Tol colors. The light side was not changed; only dark partners were added.

| Light | Dark | Notes |
| --- | --- | --- |
| `#0969DA` | `#79C0FF` | blue (GitHub) |
| `#0072B2` | `#79C0FF` | Okabe-Ito blue, shares dark partner |
| `#1F6FEB` | `#56B4E9` | |
| `#D55E00` | `#FFA657` | vermillion |
| `#9A6700` | `#E69F00` | taller slope gold |
| `#E69F00` | `#F2CC60` | orange (dual role, see below) |
| `#009E73` | `#7EE787` | bluish green |
| `#1A7F37` | `#3FB950` | green (GitHub) |
| `#CC79A7` | `#FFADCC` | reddish purple |
| `#AE377B` | `#D2A8FF` | |
| `#BF3989` | `#F778BA` | pink (GitHub) |
| `#4477AA` | `#A5D6FF` | Tol blue |
| `#369CCF` | `#56D4FF` | lifted skyblue |
| `#BF8700` | `#E3B341` | gold (GitHub) |
| `#CF222E` | `#FF7B72` | red (GitHub) |
| `#8250DF` | `#D2A8FF` | purple (GitHub) |
| `#F0E442` | `#EAE234` | yellow |
| `#000000` | `#FFFFFF` | Alberta slope series |
| `#8B949E` | `#C9D1D9` | neutral (moving-average line) |
| `#838B94` | `#768089` | muted gray (recessive bars, distinct from Alberta white) |

**The `#E69F00` dual role is why the map is per-value-directional, not a naive two-way swap.** `#E69F00` is a light-mode SERIES in first-trillion but the dark-mode TARGET of `#9A6700` in taller. A single naive bidirectional map cannot represent the same hex meaning two different things. The adapter resolves this by only ever applying the light-to-dark direction when dark and the dark-to-light direction when light, keyed on the dataset's current value, so in taller dark mode `#9A6700` becomes `#E69F00` and in first-trillion dark mode `#E69F00` becomes `#F2CC60`, both correct.

**Warm Okabe-Ito bars keep their fills and get theme-aware borders, not contrast-driven recoloring.** `#E69F00` and `#F0E442` cannot be darkened to clear 3:1 on white without collapsing their CVD separation from the other warm colors (they are separated by lightness; darkening merges them). The accepted resolution is to keep the audited Okabe-Ito fills and add a `borderColor: window.__tc()` hairline so they stay legible on both backgrounds. These datasets carry an inline `// audit-ok` marker and appear in the audit's ACCEPTED section rather than as failures. This extends the BUG-022 principle: when a color cannot clear the floor without breaking a more important property, document the choice inline and border for legibility.

**Verified.** `python3 tools/audit_figures.py` reports 233 color slots across 11 files, 0 issues flagged, 13 accepted (the warm bars), 0 uncovered hexes, exit 0. Every series color clears the 3:1 mark floor in both themes graded against `#14191F`, with the global swap applied. Tightest dark ratios are the GitHub reds and pinks at about 7:1; most land between 9:1 and 17:1. The full rollout (taller and paradox inline adapters removed, first-trillion helpers retained, college-scorecard reverted to no per-page code) was confirmed by rendering every chart on taller, the paradox essay, first-trillion, and the college-scorecard case study in both modes.

First resolved: June 2026, during the site-wide figure contrast pass.

### Changelog: Figure Contrast and Dark-Mode Theming Pass (June 2026)

A single pass brought every chart on the site to WCAG-compliant contrast in both themes and consolidated all chart theming into one mechanism. In order:

The first contrast audit (the new `tools/audit_figures.py`) found the dark-mode failures the eye had been missing: series colors graded against the wrong canvas, hardcoded text colors invisible in one theme, and no per-theme series swap at all. The skyblue lift (`#56B4E9` to `#369CCF`) and the Queen's-line nudge (`#AA3377` to `#AE377B`) were applied to clear 3:1 on the dark canvas while staying CVD-distinct. The warm Okabe-Ito bars in first-trillion were given theme-aware borders rather than recoloring, because darkening them would have collapsed their colorblind separation.

The work then expanded from one-off fixes to a universal per-theme model: every series color gets a light value and a dark partner, maximum contrast in each theme, CVD-safe, the brightest tint that still reads as the hue. The 20-pair canonical map (documented in BUG-040) was computed and verified per chart for colorblind separation under deuteranopia, protanopia, and tritanopia.

The delivery mechanism went through several wrong turns (a taller-derived per-page adapter that fought Chart.js internals and the Blowfish theme-state desync) before settling on one global adapter in `extend-footer.html`, superseding the BUG-035 defaults-only script. The per-page adapters on taller and the paradox essay were then removed so the global adapter is the single mechanism; first-trillion keeps its `__tc`/`__gc` helpers because its chart configs depend on them inline.

The audit tool was rewritten to match the shipped model: it reads the canonical map from `extend-footer.html` at runtime (single source of truth), grades the dark side against the real `#14191F` canvas, and adds a coverage pass that flags any series hex not covered by the global map. Final state: 233 slots, 0 issues, 0 uncovered, exit 0.

### Tool: tools/audit_figures.py (figure contrast auditor)

`audit_figures.py` walks every Chart.js figure in `content/**/*.md`, measures WCAG contrast for each series color and each text element against the actual canvas in both light and dark themes, and reports per chart. It is pure standard library, Python 3.8 or newer.

**Model (current, BUG-040).** The tool reads the canonical light-to-dark swap map from `layouts/partials/extend-footer.html` at runtime, so there is exactly one source of truth and no second copy to drift. Every series hex is graded in dark mode at its mapped partner's value (or unchanged if not in the map, which the coverage pass then flags). The dark canvas is `#14191F` (neutral-800 reversed), the measured rendered background. The light canvas is `#FFFFFF` (the card surface). Series colors must clear 3:1 in both themes.

**Coverage pass.** Every distinct series hex used anywhere in content must be a key in the global map (or itself be a dark-target value). A hex that is neither will not swap in dark mode and would render its light value on the dark canvas; the tool lists any such hex with its locations and exits nonzero. This automates the by-hand coverage check used during the rollout.

**Text and grid.** A text or grid color set to `window.__tc()`/`window.__gc()` or driven by theme-aware `Chart.defaults` is recognized as theme-aware and passes. Only a hardcoded hex in a title, tick, legend, or grid slot is a BUG-034 violation, reported with its real two-mode contrast.

**Accept markers.** A dataset carrying an inline `// audit-ok` or `// audit-accept` comment is moved to a separate ACCEPTED section rather than counted as a failure (the BUG-022 "document the choice inline" rule, made machine-checkable). The first-trillion warm bars use this.

Usage:

```bash
python3 tools/audit_figures.py                 # audit content/, report only
python3 tools/audit_figures.py --self-test     # theme and palette tables
python3 tools/audit_figures.py --fix           # strip hardcoded text colors; remap invisible series
python3 tools/audit_figures.py --fix-all       # also remap FAIL series to nearest approved
python3 tools/audit_figures.py --json          # machine-readable findings
```

Exit code is nonzero while any unresolved failure, hardcoded text color, or uncovered series hex remains.

### BUG-041: `tools/gen.py` silently crashes without `us-states.json` and `canada.json`, leaving stale maps deployed

**Symptom.** The realignment maps in the despacho "Conference Premium" essay kept showing an old render no matter how many times the fix was applied. Every regeneration looked successful from the chat side, but the live maps never changed. The real cause was that `python3 gen.py` was aborting on its second line before producing a single figure.

**Root cause.** `gen.py` opens four files by bare relative name at import time: `teams.json`, `all_alignments.json`, `us-states.json`, and `canada.json`. The first two live in `tools/`, but the two boundary GeoJSON files were never on the drive at all (a `find` across the whole ProtonDrive folder returned nothing). With them missing, `gen.py` raised `FileNotFoundError` immediately, wrote zero `fig_*.html` files, and the follow-up `mv fig_*_*.html` matched nothing, so `static/figs/` kept serving the previous maps. The crash was easy to miss because the next commands in the deploy block produced their own "no such file" noise and Hugo still rebuilt fine.

**The fix.** The two boundary files are standard GeoJSON and were sourced from GitHub, then confirmed to match exactly what `gen.py` consumes:

- `us-states.json`: the classic Leaflet file from `raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json`. A FeatureCollection where each feature has `properties.name` set to the full state name and a `Polygon` or `MultiPolygon` geometry in `[lon, lat]` order. `gen.py` keeps every state except Alaska, Hawaii, and Puerto Rico, which it drops by name.
- `canada.json`: `raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/canada.geojson`. Same shape, with `properties.name` carrying province names. `gen.py` keeps only British Columbia, Alberta, Manitoba, Ontario, Quebec, and Saskatchewan by exact name and clips each ring to latitude 58 and below.

Both files go in `tools/` alongside `teams.json` and `all_alignments.json`. `gen.py` must run from that directory because it reads by relative name, and it writes `fig_<league>_<panel>.html` to the current directory.

**Lesson for the next instance.** When a regenerated artifact "will not update," confirm the generator actually ran to completion before assuming a logic bug. A generator that reads inputs by bare relative name fails loudly only if you are watching its first lines; downstream `mv` and build steps will happily mask the crash.

First resolved: June 2026, Conference Premium map pipeline.

### BUG-042: `gen.py` fanned close teams in alphabetical order, inverting their geography

**Symptom.** On the NFL maps, Washington rendered north of Baltimore, which is backwards (Baltimore is about 40 miles north of DC). The team coordinates in `teams.json` were correct (Ravens latitude 39.278 is north of Commanders 38.908); the inversion was purely in rendering.

**Root cause.** `content()` clustered any teams whose projected positions fell within a pixel threshold (originally 9px, about 28 miles at the continental scale) and fanned the cluster members around a circle in `sorted()`, alphabetical, order starting from the top. For Washington and Baltimore, "Commanders" sorts before "Ravens," so Washington landed at the top of the fan regardless of actual latitude. The threshold also swept up genuinely distinct teams 28 miles apart and mislabeled them "Shared venue."

**The fix, final form.** Only teams that genuinely share a venue (near-identical coordinates, `THRESH=1.0`px) are clustered and split; every other team renders at its true projected coordinate. Same-city distinct teams (Yankees/Mets, Nets/Knicks, the two Los Angeles pairs) therefore sit close enough to overlap slightly at their real spots, which is geographically faithful and was the explicit design choice. Only the two true shared-stadium pairs stay split: Giants/Jets at MetLife and Rams/Chargers at SoFi, which must be separated or one hides the other. An intermediate version (fan by true compass bearing instead of alphabetically) was geometrically correct but still displaced teams more than wanted; true coordinates won.

**Verification mechanism.** Because the rendered SVG places each marker at a known `cx`/`cy`, correctness is checkable without a browser: read the marker `cy` for two teams and confirm the northern one has the smaller value. Ravens `cy` 237.2 sits above Commanders `cy` 245.0 in every regenerated NFL panel.

First resolved: June 2026, Conference Premium maps.

### BUG-043: map labels stacked on nearby teams; fixed with directional placement, a collision pass, and a halo

**Symptom.** With teams at true coordinates (BUG-042), the abbreviation labels collided. "BAL" and "WAS" printed on the same spot, and even isolated labels sat partly behind their own markers, because every label was hard-coded 9px directly above its marker.

**The fix, three parts.**

1. Directional placement. Each label is placed in the open direction, away from the average position of teams within 36px. Two close neighbors throw their labels opposite ways (Baltimore's up and left, Washington's down).
2. Collision pass. After placement, a short iterative loop nudges any still-overlapping label boxes apart vertically until none collide. This is what separates same-point pairs (Yankees/Mets, Nets/Knicks) that directional placement alone cannot, because both members of a co-located pair inside a larger cluster get pushed the same way.
3. Halo. Each label is drawn with `stroke="var(--map-bg)" stroke-width="2.5" paint-order="stroke" stroke-linejoin="round"`, a background-colored outline behind the fill, so it stays legible where it crosses a marker or a division line.

Labels stay inside their team `<g>` so the click-to-focus dimming still applies to them.

**Verified.** A bounding-box overlap scan across all 14 generated maps reports zero overlapping label pairs, with the markers still at true coordinates.

First resolved: June 2026, Conference Premium maps.

### BUG-044: embedded iframe maps are cached independently of the parent page; hard-refresh does not evict them

**Symptom.** After deploying corrected maps, the essay page still showed the old map through several hard-refreshes, producing repeated "it is still broken" reports when the file on disk was already correct.

**Root cause.** The maps are embedded with `<iframe src="/figs/fig_<league>_<panel>.html">` via the `realign` shortcode. A browser caches an iframe's source document as its own resource, so a hard-refresh (Cmd+Shift+R) of the parent page reloads the page but often serves the iframe body from cache.

**Diagnosis and fix.**

- Verify the deploy off disk, not through the browser. Each `gen.py` version carries a unique magic string in its help text (currently "Every other team sits at its true location"). `grep -c "<magic string>" static/figs/fig_nfl_B.html` returning 1 proves the new file is in place; reading the marker `cy` values off the file (BUG-042) proves the geometry.
- To view the new map, load it directly at `http://localhost:1313/figs/fig_<league>_<panel>.html` and hard-refresh that tab, or open the essay in a private window, or use "Empty Cache and Hard Reload" from DevTools. A plain parent-page refresh is not enough.
- Permanent option, not yet applied: add a version query to the iframe `src` in `realign.html` (for example `/figs/fig_nfl_B.html?v=2`) so each regenerate is a new URL the browser cannot serve from cache.

**Lesson.** When a deployed file "will not show," distinguish three layers before re-editing code: the file on disk, the server output, and the browser cache. Confirm the first two by reading bytes; only then chase the third.

First resolved: June 2026, Conference Premium maps.

### Tool: tools/gen.py (realignment map generator) and the `realign` shortcode

`gen.py` builds the interactive league-realignment maps for the despacho "Conference Premium" essay. It reads four files from its working directory, `teams.json` (per-league team coordinates, colors, and abbreviations), `all_alignments.json` (the A/B/C division partitions from the optimizer), and the two boundary files `us-states.json` and `canada.json` (BUG-041), and writes one theme-aware HTML file per panel, `fig_<league>_<panel>.html`, to the current directory. Panels are A (actual divisions), B (conferences kept, divisions redrawn), and C (free optimum); MLS has only A and C. Each output is self-contained SVG plus a small zoom, pan, and focus script, themed through CSS variables so one file renders in both light and dark mode.

Internals a future instance will need: markers sit at true projected coordinates except genuine shared-venue pairs, which are split (BUG-042); labels are placed directionally with a collision pass and a halo (BUG-043); Canada rings are drawn only for the NHL and MLS maps, the leagues with Canadian teams, and clipped at latitude 58. The premium values shown in the essay come from the separate optimizer that produced `all_alignments.json`, not from `gen.py`; `gen.py` only draws.

The maps are embedded in markdown through the `realign` shortcode (`layouts/shortcodes/realign.html`). It supports a single-panel mode, `{{< realign league="nfl" panel="B" >}}`, which renders one iframe so prose and tables can sit between maps; with no `panel` argument it stacks all of a league's panels. After regenerating, move the figures into `static/figs/`, and remember the iframe cache (BUG-044).

### Changelog: The Conference Premium essay (despacho, June 2026)

A long build of `content/despacho/the-conference-premium.md`, a data essay measuring how much travel each of five leagues spends honoring conference boundaries that geography alone would not draw. Conventions established here that a future instance editing this essay should preserve:

- The metric is the conference premium, defined in plain words in the lead, the first line of the TL;DR, and the intro before any math: the share of in-division travel that exists only because of where a league drew its conference line. Formally `premium = (B - C) / A`, where A is the actual divisions' total within-division great-circle miles, B keeps the conferences and redraws divisions, and C is the free geographic redraw. Partitions are solved as an exact set-partition integer program (CBC via PuLP or OR-Tools).
- The NBA is modeled at its real thirty teams, where the premium is 0.00 percent, since its East and West already are the optimal split. The two presumptive expansion clubs (a returning Seattle and a Las Vegas team, both Western) appear as a projected thirty-two-team scenario, squared up to four divisions of four at sixteen per conference, which also pays 0.00 percent because the optimal even split is already a clean East and West (B equals C at 16,625.25 miles). That expansion is one the league voted in March 2026 to explore but has not yet approved, so the projected panel is framed as a what-if shown at the optimum, not a forecast of the exact divisions. The NBA section's maps therefore depict both the real thirty-team league and the projected thirty-two-team one, and the optimizer independently lands the Timberwolves in an eastern division, matching the league's own reported instinct to shift a central team east and balance the conferences at sixteen apiece. The thesis is merger-and-resort: of the four leagues that absorbed a rival, two kept the old line as a brand and still pay (MLB, NFL) and two re-sorted by geography and pay nothing (NBA, NHL); MLS never merged and has no division layer, so its zero is structural.
- Every KaTeX display formula is followed by a bulleted key defining its variables (single-backslash delimiters per BUG-039). League history paragraphs carry real cited footnotes (Wikipedia merger articles, SABR). The town-centroid "division hearts" are markdown tables placed directly under the map they describe (actual under A, conferences-kept under B, free-optimum under C), not stacked at the section end. Table header rows and category cells are Title Case; only the fun-fact note column is sentence case. Percentages are written `28.87%`, not "28.87 percent."
- The 2020 Census populations for the centroid towns are owner-supplied and verified by hand; do not substitute GeoNames figures or estimates.
