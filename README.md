# pgbd.casa — Repository Reference

This is the source repository for **pgbd.casa**, the personal portfolio of Philip Bachas-Daunert. It is a Hugo + Blowfish static site deployed via GitHub Pages.

This README is written for AI assistants and future contributors who need to be productive on the codebase quickly. It documents what the site is, how it is structured, every non-default decision, every quirk encountered during development, and the exact templates required to extend it. It is dense by design.

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
| Author | Philip Bachas-Daunert (handle: `hihipy`, email contact uses `career-pgbd@pm.me`) |

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

## 2. The Casa Metaphor

The site is organized as a "digital casa" (Spanish for "house"). Each top-level navigation entry is a "room" with a Spanish name. This is a deliberate brand element, not decoration. Do not change it without explicit instruction.

The home page lead is a rotating typing animation (Blowfish `{{< typeit >}}` shortcode wrapped inside `{{< lead >}}`, looping with `breakLines=false`) that cycles through four languages: Spanish (`Mi Casa Digital es Su Casa Digital`, canonical and matched by the site's `description` meta tag), English (`My Digital Home is Your Digital Home`), Catalan (`La Meva Casa Digital és La Teva Casa Digital`), and Greek (`Το Ψηφιακό Σπίτι μου είναι Το Ψηφιακό Σπίτι σου`). All four use the same casing rule (see §7). Spanish and English reflect citizenship (Spain and U.S. respectively); Catalan and Greek reflect heritage. The welcome paragraph immediately below the lead names all four connections explicitly.

This pattern extends to all nine room landing pages. Each `{{< lead >}}` contains a typing animation cycling a short page-purpose tagline through the same four languages in the same order. Each tagline describes what is actually on the page, not the room name itself, so a visitor who lands on cocina or estudio without context understands what they are looking at. The taglines are: puerta cycles `Mi Currículum / My Résumé / El Meu Currículum / Το Βιογραφικό μου`; sala cycles `Mi Trayectoria / My Background / La Meva Trajectòria / Το Υπόβαθρό μου`; mirador cycles `Mi Filosofía de Dashboards / My Dashboard Philosophy / La Meva Filosofia de Dashboards / Η Φιλοσοφία μου για Dashboards`; taller cycles `Mi Dashboard / My Dashboard / El Meu Dashboard / Το Dashboard μου`; obrador cycles `Mi Filosofía de Herramientas / My Tool-Building Philosophy / La Meva Filosofia d'Eines / Η Φιλοσοφία μου για τα Εργαλεία`; cocina cycles `Mis Pipelines de Datos / My Data Pipelines / Els Meus Pipelines de Dades / Τα Pipelines Δεδομένων μου`; estudio cycles `Mis Experimentos con IA / My AI Experiments / Els Meus Experiments amb IA / Τα Πειράματά μου με AI`; garaje cycles `Mis Utilidades de Analista / My Analyst Utilities / Les Meves Utilitats d'Analista / Τα Εργαλεία Αναλυτή μου`; jardín cycles `Mis Proyectos Personales / My Side Projects / Els Meus Projectes Personals / Τα Προσωπικά Έργα μου`. Greek possessive clitics (`μου`) stay lowercase per native convention; Greek proparoxytone words (`Πειράματα`, `Υπόβαθρο`) take the secondary accent when followed by the clitic (`Πειράματά μου`, `Υπόβαθρό μου`).

On puerta and sala, the previous static lead content (résumé explainer and professional summary respectively) is preserved as a regular paragraph immediately below the new animated lead. The puerta page also drops the redundant separate download button — the inline PDF embed has its own download control in the browser-native PDF toolbar.

The metaphor is the differentiator. When in doubt, choose the option that strengthens the casa framing rather than the conventional portfolio framing.

The casa metaphor extends to the 404 page, which uses casa language ("No room here. The hallway you walked down doesn't lead anywhere"). See §9.

## 3. Room Inventory

Nine rooms total. Two non-project rooms (puerta, sala), two dashboard rooms (mirador, taller), one tool-building methodology room (obrador), and four project rooms (cocina, estudio, garaje, jardín).

| Room | Path | Title (Title Case) | Role |
|---|---|---|---|
| `puerta` | `/puerta/` | Résumé PDF | Door, entry point. Terminal page that embeds `static/resume.pdf`. |
| `sala` | `/sala/` | About Me | Living room, about page. Terminal page with long-form bio (Experience / Education / Certifications / Skills). |
| `mirador` | `/mirador/` | Dashboard Philosophy | Lookout, methodology room. Holds dashboard design philosophy and methodology essays. Not a project room. |
| `taller` | `/taller/` | Built Dashboard | Workshop, applied room. Holds a worked dashboard example built from public data. Not a project room. |
| `obrador` | `/obrador/` | Tool-Building Philosophy | Craft workshop, methodology room. Holds tool-building philosophy: when to automate, how to work with AI, identifier protection. Not a project room. |
| `cocina` | `/cocina/` | Data Prep & ETL | Kitchen, data preparation tools. |
| `estudio` | `/estudio/` | AI & Experiments | Studio, AI-augmented analytics tools. |
| `garaje` | `/garaje/` | Analyst Utilities | Garage, Excel macros, calculators, processing scripts. |
| `jardin` | `/jardín/` | Side Projects | Garden, personal projects and miscellaneous experiments. |

Room symbol rationale: room pages have **no** decorative symbol prefix. The terminal-prompt path (`~/sala`, `~/cocina`, etc.) is the room identity; an additional symbol prefix is redundant decoration. The site went through three iterations on this. First, mixed Unicode glyphs (`◰ § ⛁ ✦ ⛭ ❀`) — visually distinct but five of six were not in MonoLisa and rendered via system font fallback (BUG-013 in its original form). Second, Greek capitals (`Π Σ Δ Ψ Ω Φ`) — fully present in MonoLisa with a defensible thematic mapping (Σαλόνι, Δεδομένα, golden ratio in plant biology). Third, none — the realization that the Greek letters were redundant decoration in front of already-distinctive paths, and that the homepage `⛫` castle was doing the symbolic work for the entire site without needing per-room reinforcement. The terminal-prompt format alone is the room identity. The homepage `⛫` (castle) is the brand anchor and remains the only symbolic glyph on the site. Anyone tempted to add per-room symbols back should weigh the symbolic redundancy against the visual flourish; previous iterations are documented for reference but were removed deliberately.

**Home page order (intentional):** Three sections separated by H2 headers. *Who I Am* contains `puerta`, `sala` (puerta first because the metaphor is "visitor walks through the door first"). *Dashboards* contains `mirador`, `taller` (alphabetical, which also reads philosophy-first). *Tooling* contains `obrador` first (the methodology room) followed by the four project rooms alphabetically (`cocina`, `estudio`, `garaje`, `jardín`). This structure is non-negotiable; do not reorder without instruction.

Project counts are NOT listed in this table by design. The four project rooms render their counts dynamically on the live site via the `section-count` shortcode (see §9), so manual counts here would be a maintenance burden and a source of drift. For the actual contents of each room, see §4.

## 4. Project Pages — Complete Inventory

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

**Important: `summary` also drives search result quality.** If `summary` is missing from a page's frontmatter, Blowfish's search index falls back to Hugo's auto-generated summary (the first ~70 words of body content). This produces noisy, bloated search results. Every page that is discoverable via search SHOULD have a `summary` field, including non-project pages (home, sala, puerta). See BUG-010.

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
showReadingTime: false
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

## 7. Tone and Style Conventions

These are established conventions across all 16 project pages. Match them when authoring new content.

| Rule | Notes |
|---|---|
| **No em dashes** | Use commas, parens, colons, semicolons, or restructure. The em dash is on the AI-tells list. |
| **No "delve," "comprehensive," "in summary," "moreover," "furthermore"** | All on the AI-tells list. |
| **Title Case for headings** | "Data Prep & ETL", "AI & Experiments", "Side Projects". |
| **Body and most headings: Atkinson Hyperlegible** | Sans-serif designed by the Braille Institute for low-vision and dyslexic readers. Loaded from `static/fonts/AtkinsonHyperlegible-{Regular,Bold,Italic,BoldItalic}.woff2`. Switched from MonoLisa Italic + SS02 cursive in BUG-016. |
| **Page titles (H1) and typing animations: MonoLisa upright** | Terminal-prompt strings like `Σ ~/sala  # About Me` and the {{< typeit >}} animations keep the monospace look. Upright (not italic) is fine for short strings; italic cursive was the dyslexia barrier. |
| **Code blocks: MonoLisa upright with ligatures** | Unchanged — code retains identity-defining typography. |
| **Sentence case for descriptions and body prose** | "Cleans messy data exports." not "Cleans Messy Data Exports." |
| **Title case for the home page typing animation** | Content words capitalized, verbs/copulas lowercase. Applies across all four languages in the rotation: `es` (Spanish), `is` (English), `és` (Catalan), `είναι` (Greek) all stay lowercase. Greek exception: possessive clitics `μου` and `σου` also stay lowercase per native convention (they follow the noun and aren't capitalized mid-sentence even in display text). See §2 for the full phrases. |
| **Audience: HR/recruiter with bachelor's degree, no coding background** | Avoid jargon in leads and summaries. Domain terms acceptable in body. |
| **Conciseness over completeness** | Tighter is better. The reader can scroll for more. |
| **Mention Miller School only when project genuinely connects** | Not as decoration. |
| **No invented content, no redundancy** | If two fields say the same thing, one of them is wrong. |
| **Backticks for inline code/paths** | `~/sala`, `Path.glob()`, `summaryLength = 70`. |

## 8. Frontmatter Conventions

### Required fields on every project page

```yaml
title: "<exact-repo-name>"     # matches GitHub repo name and filename stem
weight: <multiple of 10>       # see weight rules below
description: "<30-50 word SEO description>"
summary: "<3-6 word card label>"
tags: ["..."]
showDate: false
showReadingTime: false
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
| `showDate`, `showReadingTime`, `showAuthor` | All `false` to keep pages stripped of clutter |

### Forbidden in frontmatter

- `date` — not set anywhere; presence triggers reverse-chronological sort fallback
- `lastmod` — handled automatically by `enableGitInfo`
- `draft: true` — never used; commit only when ready

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

### `layouts/shortcodes/swatch.html`

Renders an inline color swatch (small colored square) followed by the hex code in monospace. Used in `~/mirador` to make the named palettes actually viewable as colors rather than as bare hex strings the reader has to mentally translate.

Usage: `{{< swatch "#E69F00" >}}`. Pass the hex value with leading `#` as the first positional argument. The shortcode emits a 0.85em colored square with a faint inset border (so very light colors stay visible against light backgrounds) followed by the hex code in a `<code>` tag.

**Color naming convention.** When a color in mirador needs a name (palette entries, recommended pairings), the name comes from [chir.ag's Name That Color](https://chir.ag/projects/name-that-color/) tool. The format on the page is: swatch shortcode, then linked color name, then hex in parens, e.g. `{{< swatch "#56B4E9" >}} [Picton Blue](https://chir.ag/projects/name-that-color/#56B4E9) (#56B4E9)`. The link points to chir.ag with the hex as URL fragment (uppercase, no `#` in the URL itself — the fragment marker is the literal `#` separator). The link text MUST match what chir.ag's live tool actually returns for that hex; do not transcribe a name from a search result or a port of the ntc.js algorithm, since neither reliably matches the live tool's output. Verify by clicking the chir.ag link and reading the name from the live page. This convention exists so the page's prose stays in sync with the link target — a reader who clicks "Picton Blue" should land on a page that confirms it's Picton Blue, not Sky Blue or anything else.

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

**Invocation:** `{{< section-count cocina >}}` — UNQUOTED single token argument. See BUG-001 for why.

### `layouts/partials/header.html` and `footer.html`

Existing Blowfish overrides. Their content is project-specific and should not be modified without inspection.

### `assets/icons/` — 25 custom SVGs

Used primarily by `content/sala/index.md` (about page) and a few project pages. Inventory:

`book, book-open, briefcase, building-columns, bullhorn, calculator, certificate, chart-bar, chart-line, clipboard-check, coins, compass, earth-americas, file-pen, flask, house, landmark, lightbulb, magnifying-glass, microscope, network-wired, pen-nib, school, server, vial`

21 are referenced in content. 4 are unused (`building-columns`, `certificate`, `compass`, `house`) but kept available.

**Usage in markdown:** `{{< icon "calculator" >}}` (this shortcode is provided by Blowfish theme).

### `assets/css/custom.css`

Custom CSS overrides, roughly 5KB. Concerns:

1. Atkinson Hyperlegible `@font-face` declarations (Regular, Italic, Bold, BoldItalic, all woff2 self-hosted from `static/fonts/`)
2. MonoLisa `@font-face` declaration (variable, upright only — italic was retired in BUG-016)
3. Body and most headings (h2-h6) use Atkinson sans-serif for readability; H1 page titles and typeit animations use MonoLisa upright to preserve terminal-prompt aesthetic; code blocks use MonoLisa upright with ligatures
4. `white-space: nowrap !important` on Blowfish badge spans — prevents date ranges from breaking ugly across lines
5. Mermaid diagrams and figures centered with auto margins
6. Mobile timeline overflow fix at `@media (max-width: 640px)` — see BUG-012
7. Mobile typing-animation lead font shrink + min-height to prevent bounce — see typing animation work in §2

Inspect before modifying — every rule has a reason.

### `assets/img/favicon-source.svg`

Canonical SVG source for the favicon set. Donut chart in Blowfish github palette: primary blue (`#0969da`), light blue tint (`#54aeff`), neutral gray (`#656d76`). Three segments at 50/30/20 percent with 4-degree gaps. The PNG/ICO files in `static/` are derived from this source. To regenerate the full favicon pack from this SVG, see §13.

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

For arguments that require spaces (or quotes for any reason), the alternative is to disable smartypants in `markup.toml`, but this affects all body content — undesirable for a portfolio site where résumé/résumés should still get smart quotes.

### BUG-002: Hugo template comments parse `*/` as terminator inside `{{- /* */ -}}`

**Symptom:** Template parse error `comment ends before closing delimiter` even though the comment block has matching `{{- /*` and `*/ -}}`.

**Cause:** Go's text/template parser scans for the literal sequence `*/` to terminate the comment, with no escape mechanism. If the comment body contains `*/` for any reason (such as an embedded shortcode example using `{{</* ... */>}}` notation), the parser ends the comment early, then chokes on the rest.

**Workaround:** Never embed shortcode example syntax in `{{- /* */ -}}` block comments. Use plain prose for documentation. If you must show example syntax, use markdown comments or HTML comments outside the template comment.

### BUG-003: `{{< katex >}}` adjacent to `{{< lead >}}...{{< /lead >}}` breaks rendering

**Symptom:** On project pages with both shortcodes, the lead block fails to render — the closing `{{< /lead >}}` shows as literal text in the body, KaTeX expressions later on the page render as raw `\(...\)` source.

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

Mermaid is enabled per-page via `mermaid = true` in `params.toml` `[article]` block, and invoked via `{{< mermaid >}}...{{< /mermaid >}}` shortcode (NOT triple-backtick code blocks — that's a different render path that doesn't work with Blowfish's setup).

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

**Symptom:** Original favicon (three vertical ascending bars) was visually ambiguous — read as cellular signal indicator rather than data analytics.

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

**Cause:** Blowfish's `timelineItem.html` shortcode places the entry header and date badge inside a `<div class="flex justify-between">`. On desktop this works — title left, badge right. On mobile, the badge has `white-space: nowrap !important` (set in `custom.css` to prevent date ranges like `Apr 2023 - Mar 2025` from breaking across lines), and the heading refuses to share a line with the badge. The row demands more horizontal space than a phone viewport offers. The parent card is `flex-1` with default `min-width: auto`, so it cannot shrink below its content's natural width — the entire card overflows, dragging body text past the right edge.

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

The selectors target Blowfish's Tailwind utility classes (`.shadow-2xl.flex-1.ms-6` matches the timelineItem's outer card div). If upstream Blowfish ever changes those class names, this rule needs re-targeting — check `themes/blowfish/layouts/shortcodes/timelineItem.html` for the current selector.

**Coverage:** Selector-based, not page-based. Applies anywhere `{{< timelineItem >}}` is used. On `sala`, that's Experience, Education, and Certifications sections, plus any future timeline entry. No per-page work when adding entries.

### BUG-013: Five of six room symbols are not in MonoLisa's character map [RESOLVED]

**Resolution (April 2026):** Room symbols removed entirely. After two iterations (original mixed Unicode glyphs `◰ § ⛁ ✦ ⛭ ❀`, then Greek capitals `Π Σ Δ Ψ Ω Φ`), the conclusion was that the per-room symbol prefix was redundant decoration in front of already-distinctive terminal-prompt paths (`~/sala`, `~/cocina`, etc.). The Greek-letter intermediate iteration *did* eliminate the font-fallback issue (Greek capitals are fully present in MonoLisa), so it would have resolved this bug if kept. Removing the symbols entirely also resolves the bug while simplifying the visual identity. The homepage `⛫` (castle) is preserved as the single brand anchor and is the only symbol on the site that renders via system font fallback; that one instance is acceptable because the castle is the brand and is contained to a single location. Bug retained in this catalog as historical context — anyone tempted to re-introduce per-room symbols should know the constraints (must render in MonoLisa to avoid fallback inconsistency) and the reasoning for removal (symbolic redundancy with the path).

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

**Why this matters for the README:** Anyone troubleshooting an unexpected UI element on the site should first rule out browser-injected translation widgets before assuming it is a site rendering issue. This is parallel to BUG-011 (newly-registered domain blocks at the network level) — the symptom appears on the site but the cause is external infrastructure.

### BUG-015: Email address leaked in plain HTML via menu rendering

**Symptom:** The contact email `career-pgbd@pm.me` appeared as an unobfuscated `mailto:` link in the rendered HTML of every page (desktop menu and mobile menu collapse, two instances per page). Bots scraping `mailto:` links via regex harvested the address, leading to spam.

**Cause:** Blowfish has *two* paths that render the email link, and only one of them is obfuscated:

1. The `[params.author].links` block in `languages.en.toml` is rendered by `themes/blowfish/layouts/partials/author-links.html`. That partial special-cases email entries: it writes `href="#"`, encodes the real address into a `data-email="..."` base64 attribute, and adds a `class="email-link"` hook that JavaScript uses to decode and trigger `mailto:` on click. This path is properly obfuscated and safe.

2. The `[[main]]` entries in `menus.en.toml` are rendered by Blowfish's generic menu partials (`header/components/desktop-menu.html` and `header/components/mobile-menu.html`). These use a generic `<a href="{{ .URL }}">` template that does *not* special-case email URLs. Whatever URL is in the menu entry — including `mailto:`-prefixed ones — gets written literally to HTML.

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

**Symptom:** A reader with dyslexia reported the body text was hard to read. The site shipped MonoLisa Italic with `font-feature-settings: "ss02" 1` everywhere except code blocks. SS02 is MonoLisa's stylistic alternate that turns italic into a flowing cursive script — visually striking but functionally a script font for body text and headings.

**Cause:** Italic-as-body-text is unconventional and creates real reading friction for many readers. Cursive-style italic specifically (which SS02 is) compounds the issue because the connected, sloped letterforms reduce per-character visual distinctiveness. Dyslexic readers in particular rely on per-character distinctiveness to disambiguate similar letters (b/d, p/q, m/w). The italic cursive collapses this distinctiveness across all letters, not just the typically-confused pairs.

**Fix applied:** Switched to a hybrid typography system. Body text and most headings (h2-h6) now use **Atkinson Hyperlegible**, a sans-serif designed by the Braille Institute specifically for low-vision and dyslexic readers. The font has visually distinct letterforms (no I/l/1 collisions, no b/d mirroring) which helps every reader, not just dyslexic ones. Loaded as four self-hosted woff2 files (Regular, Italic, Bold, BoldItalic) from `static/fonts/`, converted from upstream TTF via fontTools at ~24KB each.

H1 page titles (the terminal-prompt strings like `Σ ~/sala  # About Me`) and the {{< typeit >}} typing animations remain in MonoLisa upright. These are the identity-defining typography of the site, and upright MonoLisa is not the readability barrier — italic cursive was. Keeping the terminal-prompt look in H1s and animations preserves the brand without re-introducing the dyslexia issue. Code blocks remain in MonoLisa upright with ligatures, unchanged.

**Implementation in `assets/css/custom.css`:**

- Atkinson `@font-face` declarations for all four weights/styles
- MonoLisa Italic `@font-face` removed entirely (no longer used anywhere)
- `html, body` and `h2, h3, h4, h5, h6` selectors point to Atkinson with system sans-serif fallback chain
- `h1` and `[id^="typeit-"]` selectors point to MonoLisa upright with monospace fallback chain
- `em, i` defensive italic rule removed (was MonoLisa-specific; Atkinson has its own italic variant)

**Verification:** Load any page on the site. Body text and h2/h3 headings should render in Atkinson Hyperlegible (clean sans-serif). H1 page titles like `Σ ~/sala  # About Me` should render in MonoLisa upright (monospace). The cycling typing animations should also render in MonoLisa upright. Code blocks in project pages should render in MonoLisa with ligatures, unchanged from before.

**Why this matters generally:** The original cursive script was visually distinctive but it traded readability for aesthetics across every page. The fix demonstrates that "identity-defining typography" and "accessible typography" are not always in conflict — they can coexist by scoping each to where it does its best work. The terminal-prompt look defines the brand in short strings (page titles, animations); long-form prose needs to be read by humans, including those for whom italic cursive is a real barrier.

### BUG-017: Inline KaTeX requires `\\(...\\)` (double-backslash) in markdown source

**Symptom:** Writing inline math as `\(M\)` in markdown source renders as the literal text `(M)` in the browser. KaTeX never processes it.

**Cause:** Hugo's Goldmark Markdown renderer interprets `\(` and `\)` as Markdown escape sequences for literal parentheses *before* the HTML reaches KaTeX. Goldmark eats the backslashes, leaving plain `(M)` in the rendered HTML. KaTeX's auto-render then has nothing to recognize.

**Fix:** Use `\\(...\\)` (double-backslash) in markdown source. Goldmark interprets `\\` as an escape for a literal backslash, leaving `\(` in the rendered HTML, which is the inline-math delimiter KaTeX recognizes.

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
2. Is the inline math written as `\\(...\\)` (double-backslash) in markdown source? Single-backslash will not work.
3. Does the expression contain an apostrophe (`'`)? Replace it with `\\prime` or restructure to avoid.

**Why this matters.** Inline KaTeX works fine on this site with the right syntax. The pitfall is that the natural syntax (`\(M\)` borrowed from LaTeX, Pandoc, and most static site generators) does not work here because of Goldmark's escape handling. The double-backslash workaround is non-obvious and easy to lose during refactors. Documenting the working syntax with verified examples saves future debugging cycles.

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

1. **CVD-safe palette is not the same as high-contrast palette.** Okabe-Ito was designed for distinguishability across color-vision deficiencies on the gray paper backgrounds typical in scientific journals. Several of its colors (`#56B4E9`, `#E69F00`, `#F0E442`) are deliberately bright and pale — perfect for distinguishability, terrible for contrast against a pure-white web background. Adopting the palette without measuring per-color contrast against the actual canvas color produces silent failures.

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
2. AA-large/non-text entries (3.0–4.49:1) are within mirador's documented 3:1 floor for chart elements but require a deliberate decision: accept the marginal contrast to preserve palette identity, or push the color darker/lighter at the cost of palette recognizability. Whichever you pick, **document the choice inline in the chart config** so future-you doesn't "fix" it unknowingly.
3. After every theme-adapter change, rerun the audit. The map and the audit must stay in sync.

**Why this matters.** Three rounds of "the colors look fine" preceded the FAIL discovery on `/taller/`. Visual inspection on a single monitor in a single lighting condition by a single non-CVD viewer is not an accessibility test. The math is the test. A 100-line Python script is enough to make it permanent and re-runnable; treating contrast as a one-time eyeball check is what produces silent inaccessibility in production dashboards.


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

### `config/_default/params.toml` — non-default values only

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
    { email = "mailto:career-pgbd@pm.me" }
  ]
```

### `config/_default/menus.en.toml`

Three social links: linkedin, email, github. Order via `weight` field (10, 20, 30).

### `config/_default/markup.toml`

Existing markup configuration. Inspect before modifying.

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
- Favicon files are donut chart in github palette — see BUG-009. Source SVG at `assets/img/favicon-source.svg`.
- The `pgbd.us` redirect alias is configured in Cloudflare DNS + Rules — see §1. Not a file in this repo.

## 13. Adding a New Project Page — Procedure

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

`main` branch push → GitHub Pages builds → serves at `https://hihipy.github.io` → CNAME redirects to `https://pgbd.casa`. Separately, `https://pgbd.us` 301-redirects to `https://pgbd.casa` via Cloudflare — see §1.

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

## 16. Outstanding Items / Known Issues

| Item | Notes |
|---|---|
| Sala description discrepancy | The `description` field in `content/sala/index.md` says "Institutional research analyst" but other contexts (the Blowfish `[params.author]` headline) say "Data analyst." If they refer to the same role under different terminology, fine. If alignment is desired, update the sala frontmatter. |
| Four unused icons | `building-columns`, `certificate`, `compass`, `house` in `assets/icons/` are not referenced anywhere. Kept available for future use. The `certificate` icon is the most likely candidate for sala's Certifications section if one is added. |
| Newly-registered domain blocking | The University of Miami network has been observed blocking both `pgbd.casa` and `pgbd.us` for some time after each domain's registration. This is BUG-011 — a generic enterprise filter for newly-observed domains, not site-specific. Expected to resolve on its own after 30-90 days as the domains age. Affects only highly-restrictive corporate networks; the site is accessible from cellular, residential, and most non-restrictive networks. |

## 17. Glossary

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

## 18. Reference Links

- Hugo docs: https://gohugo.io/documentation/
- Blowfish theme docs: https://blowfish.page/docs/
- KaTeX docs (used by `{{< katex >}}` shortcode): https://katex.org/docs/supported.html
- Mermaid docs (used by `{{< mermaid >}}` shortcode): https://mermaid.js.org/intro/
- Hugo shortcode reference: https://gohugo.io/templates/shortcode-templates/
- GitHub Pages custom domain setup: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site
- Cloudflare Redirect Rules: https://developers.cloudflare.com/rules/url-forwarding/single-redirects/

## 19. Document Maintenance

This README is the canonical reference for the codebase. When making non-trivial changes to the site, update the relevant section here. Specifically:

- §1 if domain configuration changes (new domains, expired registrations, etc.)
- §3 if room structure changes
- §4 if a project is added, removed, or renamed
- §6 if the project page template changes
- §10 when new bugs are discovered
- §11 when configuration is changed
- §15 when account security posture changes (new accounts, new 2FA devices, OAuth re-coupling, recovery email change)
- §16 when known issues are resolved or new ones found

The README is intentionally dense. It is not meant to be read sequentially; it is meant to be searched and referenced by section.
