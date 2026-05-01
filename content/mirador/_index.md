---
layout: "single"
title: "~/mirador  # Dashboard Philosophy"
description: "How I think about designing dashboards: a chef's approach to plating data for the people who use it. Accessibility as the non-negotiable floor, the end user as the ultimate diner, iteration as the standard."
summary: "Dashboard design philosophy."
draft: false
showAuthor: false
showDate: false
showReadingTime: false
showWordCount: false
showBreadcrumbs: true
showTableOfContents: true
showPagination: false
---

{{< katex >}}

{{< lead >}}
{{< typeit speed=70 loop=true breakLines=false >}}
Mi Filosofía de Dashboards
My Dashboard Philosophy
La Meva Filosofia de Dashboards
Η Φιλοσοφία μου για Dashboards
{{< /typeit >}}
{{< /lead >}}

## Approach

I think about building a dashboard the way a chef thinks about opening a new restaurant.

I am the chef. I have a kitchen, a set of techniques, opinions about how a plate should look. I curate a menu. When the diner sits down, I present what I think is the right thing for them and I explain why. Then I cook what they want.

The dashboard is the meal. The end user is the diner. They are the one who will eat it every day, week after week, quarter after quarter. I built it once. They live with it. If they do not like it, the restaurant fails, and bringing my ego to the table is the fastest way to empty it.

That framing keeps me honest. There are things a chef brings that the diner cannot: which charts encode comparisons accurately, what the data can and cannot support, where the visual decisions are non-negotiable for accessibility. There are things the diner sees that the chef cannot: what they actually do with the dashboard on a Tuesday afternoon, which numbers they trust at a glance, what question they always have to look up somewhere else.

The whole job is knowing which is which, and respecting both.

## Accessibility

The kitchen has standards. These are not up for debate.

A real kitchen does not let a customer talk it out of food safety. The dashboard equivalent is **accessibility**, meaning legibility and color contrast. If the dashboard cannot be read, it cannot do its job. This is the only place where I will hold the line against a stakeholder who wants something different.

**Fonts.** Use a typeface that was actually designed for clarity. For body text, that means avoiding thin geometric sans-serifs where similar characters are easy to swap (1/l/I, 0/O, B/8). For data tables, code, and terminal-style elements, a monospaced face keeps columns aligned and characters distinct. The cost of a bad font choice is invisible: a reader misreads a 0 as an O, a 1 as an l, makes a decision on the wrong number, and you never find out.

**Color.** Use a palette designed for color-blind viewers. Pair color with shape, position, or label so the meaning never depends on color alone. About 8% of men have some form of red-green color blindness, which means the green-good/red-bad shorthand in business dashboards fails for roughly one in twelve men in the room.

**Contrast.** Color choices alone are not enough. The actual measurement is contrast ratio:

$$\text{Contrast Ratio} = \frac{L_1 + 0.05}{L_2 + 0.05}$$

where \\(L_1\\) is the relative luminance of the lighter color and \\(L_2\\) the darker. The [WCAG 2.1 AA standard](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) requires at least 4.5:1 for normal text and 3:1 for large text (18pt and up, or 14pt bold and up). Below those numbers, you have excluded somebody, usually silently, because they will not say so.

To check any specific foreground-background pair, the [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) is the standard tool: paste two hex codes, get the ratio and pass/fail at each WCAG level.

**Recommended pairings.** I use the GitHub light and dark theme accent palettes throughout this site. Every pair clears AA for normal text, the contrast ratios are public and verifiable, and using the same palette in both modes means one design decision instead of two.

**Density and spacing.** Crowding is its own legibility failure. When numbers, labels, and charts are pressed together with no breathing room, the eye cannot find anchors. Generous padding around tiles, consistent line height, and white space between sections are not decorative; they are how the reader navigates without effort.

**The export test.** Every dashboard I build will eventually be screenshotted into a slide deck or exported to PDF for a board meeting. The first time that happens, all interactivity dies. Tooltips disappear. Filters freeze. Whatever the user is looking at is what the audience gets. If a chart relies on a tooltip to make sense, it is broken on paper. Build for the static export from the start.

The principle behind all of these is the same: design for the worst pair of eyes in the room, looking at the worst version of the document. If they can read it, everyone can.

You can see this philosophy applied on this site itself: Atkinson Hyperlegible for body text, MonoLisa for code blocks and the terminal-style room paths in the header.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Specific Typefaces I Recommend" >}}

For body text:

- **[Atkinson Hyperlegible](https://www.brailleinstitute.org/freefont/)** (Free, OFL). My default. Designed by the Braille Institute for low-vision and dyslexic readers, with deliberate disambiguation between characters that get confused at low resolution.
- **[Inter](https://rsms.me/inter/)** (Free, OFL). Designed for screen UIs. Widely supported.
- **[IBM Plex Sans](https://www.ibm.com/plex/)** (Free, OFL). Broad language coverage. Technical pedigree.
- **[Lexend](https://www.lexend.com/)** (Free, OFL). Research-backed for reading proficiency, especially for readers with reading difficulties.

For data tables, code, and terminal-style elements:

- **[MonoLisa](https://www.monolisa.dev/)** (Paid). My pick. The casa uses it for code blocks and the room paths in the header.
- **[JetBrains Mono](https://www.jetbrains.com/lp/mono/)** (Free, OFL). Designed by JetBrains for IDE use.
- **[Fira Code](https://github.com/tonsky/FiraCode)** (Free, OFL). Popular for its programming ligatures.
- **[Atkinson Hyperlegible Mono](https://www.brailleinstitute.org/freefont/)** (Free, OFL). New 2025 monospaced version from the Braille Institute team.

{{< /accordionItem >}}

{{< accordionItem title="The Color Palettes I Use" >}}

**[Okabe-Ito](https://jfly.uni-koeln.de/color/).** Categorical, up to 8 categories. Default categorical in *Nature Methods*.

- {{< swatch "#E69F00" >}} [Orange Peel](https://chir.ag/projects/name-that-color/#E69F00) (#E69F00)
- {{< swatch "#56B4E9" >}} [Picton Blue](https://chir.ag/projects/name-that-color/#56B4E9) (#56B4E9)
- {{< swatch "#009E73" >}} [Green Haze](https://chir.ag/projects/name-that-color/#009E73) (#009E73)
- {{< swatch "#F0E442" >}} [Starship](https://chir.ag/projects/name-that-color/#F0E442) (#F0E442)
- {{< swatch "#0072B2" >}} [Deep Cerulean](https://chir.ag/projects/name-that-color/#0072B2) (#0072B2)
- {{< swatch "#D55E00" >}} [Tenn](https://chir.ag/projects/name-that-color/#D55E00) (#D55E00)
- {{< swatch "#CC79A7" >}} [Hopbush](https://chir.ag/projects/name-that-color/#CC79A7) (#CC79A7)
- {{< swatch "#000000" >}} [Black](https://chir.ag/projects/name-that-color/#000000) (#000000)

**[Paul Tol Bright](https://sronpersonalpages.nl/~pault/).** Categorical alternative, less saturated. Vibrant and Muted variants on the source page.

- {{< swatch "#4477AA" >}} [San Marino](https://chir.ag/projects/name-that-color/#4477AA) (#4477AA)
- {{< swatch "#EE6677" >}} [Froly](https://chir.ag/projects/name-that-color/#EE6677) (#EE6677)
- {{< swatch "#228833" >}} [Forest Green](https://chir.ag/projects/name-that-color/#228833) (#228833)
- {{< swatch "#CCBB44" >}} [Turmeric](https://chir.ag/projects/name-that-color/#CCBB44) (#CCBB44)
- {{< swatch "#66CCEE" >}} [Sky Blue](https://chir.ag/projects/name-that-color/#66CCEE) (#66CCEE)
- {{< swatch "#AA3377" >}} [Royal Heath](https://chir.ag/projects/name-that-color/#AA3377) (#AA3377)
- {{< swatch "#BBBBBB" >}} [Silver](https://chir.ag/projects/name-that-color/#BBBBBB) (#BBBBBB)

**[ColorBrewer Sequential (Blues 5)](https://colorbrewer2.org/#type=sequential&scheme=Blues&n=5).** Heatmaps, gradients, choropleth maps.

- {{< swatch "#EFF3FF" >}} [Zircon](https://chir.ag/projects/name-that-color/#EFF3FF) (#EFF3FF)
- {{< swatch "#BDD7E7" >}} [Periwinkle Gray](https://chir.ag/projects/name-that-color/#BDD7E7) (#BDD7E7)
- {{< swatch "#6BAED6" >}} [Danube](https://chir.ag/projects/name-that-color/#6BAED6) (#6BAED6)
- {{< swatch "#3182BD" >}} [Boston Blue](https://chir.ag/projects/name-that-color/#3182BD) (#3182BD)
- {{< swatch "#08519C" >}} [Venice Blue](https://chir.ag/projects/name-that-color/#08519C) (#08519C)

**[ColorBrewer Diverging (RdBu 5)](https://colorbrewer2.org/#type=diverging&scheme=RdBu&n=5).** Variance and deviation from a baseline.

- {{< swatch "#CA0020" >}} [Monza](https://chir.ag/projects/name-that-color/#CA0020) (#CA0020)
- {{< swatch "#F4A582" >}} [Tacao](https://chir.ag/projects/name-that-color/#F4A582) (#F4A582)
- {{< swatch "#F7F7F7" >}} [Alabaster](https://chir.ag/projects/name-that-color/#F7F7F7) (#F7F7F7)
- {{< swatch "#92C5DE" >}} [Morning Glory](https://chir.ag/projects/name-that-color/#92C5DE) (#92C5DE)
- {{< swatch "#0571B0" >}} [Deep Cerulean](https://chir.ag/projects/name-that-color/#0571B0) (#0571B0)

{{< /accordionItem >}}

{{< accordionItem title="Recommended UI Pairings For Light And Dark Modes" >}}

A starting point that clears WCAG AA in both modes. The casa uses these throughout, and the light and dark sets map to each other so the same design works in both.

For a white or near-white background:

- {{< swatch "#1F2328" >}} [Shark](https://chir.ag/projects/name-that-color/#1F2328) (#1F2328). 15.80:1 against white. Body text, primary headings.
- {{< swatch "#0969DA" >}} [Science Blue](https://chir.ag/projects/name-that-color/#0969DA) (#0969DA). 5.19:1 against white. Links, primary accents.
- {{< swatch "#CF222E" >}} [Cardinal](https://chir.ag/projects/name-that-color/#CF222E) (#CF222E). 5.36:1 against white. Warnings, negative deltas.
- {{< swatch "#1A7F37" >}} [Jewel](https://chir.ag/projects/name-that-color/#1A7F37) (#1A7F37). 5.08:1 against white. Success, positive deltas.
- {{< swatch "#9A6700" >}} [Chelsea Gem](https://chir.ag/projects/name-that-color/#9A6700) (#9A6700). 4.87:1 against white. Caution, in-progress states.
- {{< swatch "#8250DF" >}} [Medium Purple](https://chir.ag/projects/name-that-color/#8250DF) (#8250DF). 5.05:1 against white. Secondary categories, tags.

For a dark background (the canvas color is #0D1117):

- {{< swatch "#F0F6FC" >}} [Polar](https://chir.ag/projects/name-that-color/#F0F6FC) (#F0F6FC). 17.39:1 against #0D1117. Body text, primary headings.
- {{< swatch "#79C0FF" >}} [Malibu](https://chir.ag/projects/name-that-color/#79C0FF) (#79C0FF). 9.73:1 against #0D1117. Links, primary accents.
- {{< swatch "#FF7B72" >}} [Salmon](https://chir.ag/projects/name-that-color/#FF7B72) (#FF7B72). 7.51:1 against #0D1117. Warnings, negative deltas.
- {{< swatch "#7EE787" >}} [Pastel Green](https://chir.ag/projects/name-that-color/#7EE787) (#7EE787). 12.32:1 against #0D1117. Success, positive deltas.
- {{< swatch "#FFA657" >}} [Texas Rose](https://chir.ag/projects/name-that-color/#FFA657) (#FFA657). 9.77:1 against #0D1117. Caution, in-progress states.
- {{< swatch "#D2A8FF" >}} [Mauve](https://chir.ag/projects/name-that-color/#D2A8FF) (#D2A8FF). 9.72:1 against #0D1117. Secondary categories, tags.

These are the GitHub light and dark theme accent palettes. They are not the only valid choices. They are a reliable starting point: every pair clears AA for normal text, the contrast ratios are public and verifiable, and using the same palette in both modes means one design decision instead of two.

{{< /accordionItem >}}

{{< /accordion >}}

## Clarity

A good dashboard reads like a children's storybook. The plot is obvious. You know what is happening without having to think about it.

That sounds like a low bar. It is not. Most dashboards fail it.

**The five-second test.** Show someone the dashboard for five seconds, then ask what they remember. If they can say "revenue is down this quarter" or "the West region is flagged red", you have a dashboard. If they say "I saw a lot of charts", you have a wall of charts.

**Headlines, not topics.** Captions describe what the chart is *about*, not what it is. "Revenue Down 12% in Q3" beats "Quarterly Revenue Bar Chart". The first does the interpretive work for the reader; the second leaves them to figure it out. A good headline reduces the cognitive cost of using the dashboard, which means the reader actually uses it.

**Annotation on the chart, not in a legend.** Legends ask the reader to look somewhere else, hold the mapping in their head, and look back. Direct labels on the data put the meaning where the eye already is. If a chart genuinely needs a legend, fine; treat the legend as a confession that something else could be clearer.

**One question per chart.** A chart trying to answer three questions answers none. If a stakeholder asks for "revenue, profit, and margin all on one view", that is three charts, not one chart with three lines.

**Reading order matters.** Dashboards are read like newspapers: top-left to bottom-right, biggest first. Put the most important number where the eye lands first. Layer secondary information below or beside it. Do not bury the lede.

The reader should arrive at the punchline in a glance, not after squinting.

## Curation

A tasting menu is not a buffet.

The most common dashboard failure mode is including everything anyone has ever asked about, somewhere, on the same page. The result looks comprehensive. It is not. It is a haystack with the needle sometimes in it.

Curation is the harder version of the chef's job. Every metric on a dashboard has to earn its place by answering: would the reader's decisions change if this were not here? If the answer is no, cut it. The metric is not wrong; it is just somewhere else's job. Detail belongs in a drill-through, an appendix, an ad-hoc query, a separate report. The dashboard itself stays focused on what the reader actually decides on.

The hardest cuts are political. Someone fought to get their metric on the dashboard. Removing it feels like a slight. Address that directly: their metric still matters, it still gets reported, it just does not earn the prime real estate of the executive view. Move it into a "details" page that is one click away. The dashboard is for the headlines.

Curation is not minimalism for its own sake. It is the consequence of taking the reader's attention seriously.

## Chart Selection

Bar, line, and pie are the spaghetti, burger, and salad of dashboards. Familiar, well understood, often the right call. But not always.

When a familiar chart does not fit the data, look for one that does. [Data to Viz](https://www.data-to-viz.com/) is a strong starting catalog: it organizes chart types by what your data actually looks like, not by what you have already seen a hundred times. AI assistants are also useful for "what kind of chart would best show this", because they will surface options outside your default vocabulary.

A few cases where stepping off the bar/line/pie path consistently wins:

A two-point comparison (this year vs last year, before vs after). A slope chart connects the two with a line and labels both ends, making the per-item change visible at a glance. A grouped bar chart hides the per-item change inside two side-by-side groups.

Many small charts, same shape. Small multiples (a grid of identical mini-charts, one per category) outperform a single overcrowded chart with twenty colored lines on it.

A flow or movement (revenue from source to channel, customers from acquisition to churn). A Sankey diagram shows the proportions of the flow itself; a stacked bar chart only shows the totals at each end.

A single answer. Sometimes the most honest visualization is one number, big, with a target underneath. No chart at all. The "is it good or bad" question gets answered without decoration.

The caveat: a non-standard chart that the audience cannot read is worse than a standard chart that is slightly suboptimal. Familiarity has real value. The point is not to be exotic. The point is to keep the option open instead of reflexively reaching for a bar.

Common traps to avoid: 3D charts of any kind (the third dimension distorts the data without adding information), pie charts with more than three or four slices (the eye cannot compare angles past that), dual-axis charts where the two axes invite the reader to read a relationship that may not be real, and stacked area charts where every series except the bottom one is unreadable.

## Disagreement

This is where ego shows up and where it does not belong.

You presented the menu. You explained the trade-offs. They picked something else. Maybe they want a pie chart where you wanted a slope graph. Maybe they want everything on one screen where you wanted to layer it. Maybe they want a color you think clashes.

Cook what they ordered.

You can, and should, make the case before plating. The most effective form is side-by-side: build a quick mock of both options, your recommendation and the request, and let the comparison speak. Words alone rarely convince. Seeing both versions does.

Calibrate how hard to push by the cost of being wrong. A request for a different shade of blue is not a hill to die on. A request that distorts the underlying data, a truncated y-axis exaggerating a small change, a pie chart implying parts of a non-whole, a misuse of percent that makes things look bigger or smaller than they are, is. The kitchen's standards include serving food that is what it claims to be. Defer on style; push hard on substance.

When you accept a choice against your recommendation, document it briefly. Not for "I told you so" reasons. For practical ones: when the user comes back in six months saying "this dashboard is not working for me anymore", you can revisit the choice without having to rediscover what was decided and why. The note is for the future you, not the present them.

The end user lives with this dashboard. You used it to build it. Their preference outranks yours by orders of magnitude. The restaurant survives by feeding them, not by impressing the chef next door.

The exception, again, is the floor. If the request would make the dashboard inaccessible (illegible, color-fail, contrast-fail), that is where you push hard, because that is the food-safety line. Everywhere else, you defer.

## Iteration

A real chef does not plate once and walk away. They taste, adjust, and plate again.

Same with dashboards. The first version is a draft.

{{< mermaid >}}
flowchart LR
    A[Plate the draft] --> B[Watch the diner]
    B --> C[Note actual usage]
    C --> D[Adjust and re-plate]
    D --> A
{{< /mermaid >}}

What you watch for: questions the dashboard should answer but does not, sections people scroll past, filters nobody touches, numbers people copy into Excel because the format on the dashboard is not quite right. That last one is particularly telling. If a number is being lifted somewhere else, the dashboard has the right value but the wrong frame.

What people *say* about a dashboard and what they *do* with it are often different stories. A diner saying the meal is fine while pushing it around the plate is still feedback. Watch the plate.

The questions that get the best answers are the concrete ones. Not "do you like this dashboard?" but "what is the first thing you check when you open this page?" Not "is anything missing?" but "what number did you have to look up somewhere else this week?" Not "is this clear?" but "tell me what you think the orange line is showing." Specific questions surface specific problems.

The deletion experiment is sometimes the strongest signal. Remove a chart for a sprint and see if anyone notices. If nobody mentions it, it was not earning its space. The fear of cutting metrics is usually larger than the cost of cutting them; the fear is what keeps dashboards bloated.

A dashboard is a living document, not a project deliverable. The first version is the starting point. The version six months in, after twenty rounds of "I noticed users always click here first" and "we removed that chart and nobody asked about it", is the actual product.

Iterate on what you see, not on what you imagined.

## Model Organization

Mise en place is the chef's term for everything in its place: knives sharpened, sauces ladled, herbs chopped, every ingredient at hand and known before service starts. The chef who skips it spends the dinner shift hunting for the salt instead of cooking.

The dashboard equivalent is the data model underneath. Every dashboard sits on top of tables, columns, measures, and relationships. As the dashboard ages, the model grows. Measures get added. Calculations get duplicated under different names. Relationships get tangled. Without discipline, the model becomes a junk drawer where finding "the right Total Revenue calculation" is its own treasure hunt.

The cost is operational, not aesthetic. Three different "Total Revenue" measures, and the executive sees one of them, the operations team sees another, and they don't reconcile. A measure no one can safely delete because no one knows what depends on it. A new analyst onboarding who needs three weeks of archaeology before they can ship anything.

The principles for keeping the pantry in order:

**Group related things.** Most BI tools support display folders or some equivalent. Group measures within each table by domain (Revenue, Cost, Pipeline, KPI). A flat list of two hundred measures is unnavigable.

**Name things consistently.** A naming convention matters more than the specific convention. "Revenue [YTD]", "Revenue [QTD]", "Revenue [MTD]" beats those three measures named in three different formats. Pattern-matching is how the eye scans a measure list; consistency is what makes the pattern visible.

**Document in the description field.** Every measure should answer two questions in its description: what it calculates, and where it should be used. Most BI tools provide this field. Almost no one fills it in. Fill it in.

**Track dependencies.** When you change a measure, you need to know what breaks. The dependency graph (this measure references that measure references this column) exists in the model already; making it visible is the work.

**Source-control what you can.** Modern formats let the model itself live in git: Power BI Project (PBIP), LookML, dbt models, Tabular Editor save files. The visualization layer may not be source-controllable, but the model behind it usually is.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Power BI Implementation: Tabular Editor 2 + pbi-model-export" >}}

[Tabular Editor 2](https://github.com/TabularEditor/TabularEditor) is the actual development tool: a real measure editor with display folders, bulk operations, and dependency views the built-in interface never surfaces. Free, open-source, MIT-licensed, indispensable. Alongside it, [pbi-model-export](/garaje/pbi-model-export/), my own tool, extracts the entire model as JSON: every table, column, measure, relationship, hierarchy, role, plus the DAX dependency graph and the resolved source paths for each table. Tabular Editor 2 is for active development; pbi-model-export is for periodic full inventory and review. Together they finally let me work on a dashboard's model the way I work on code.

{{< /accordionItem >}}

{{< accordionItem title="Equivalent Approaches In Tableau, Looker, And dbt" >}}

Tableau organizes calculated fields into folders in the Data pane (right-click → Folders); Tableau Catalog, a Server/Cloud feature, provides lineage tracking for the model layer. Looker is code-first by design: LookML is a text modeling language, every measure and dimension lives in a `.lkml` file, and version control is the default workflow rather than an add-on. dbt sits one layer earlier in the pipeline: it models the data warehouse itself with auto-generated documentation and lineage, then any dashboard tool consumes the cleaned model. Each path arrives at the same destination by different routes.

{{< /accordionItem >}}

{{< /accordion >}}

The principle is consistent regardless of tool: treat the model with the same discipline as code. Name things consistently. Group related things. Track dependencies. Make it possible to delete with confidence.

Without mise en place, every dashboard project starts with archaeology.

## Tools

A note on tools.

I work primarily in Power BI. It is my kitchen. The principles above do not depend on it. They would apply equally in Tableau, Looker, plain HTML and CSS, or a Jupyter notebook. The constraints differ. Power BI's font selection is tighter than the open web. Tableau's color customization is more flexible. Looker's modeling layer pulls some decisions earlier in the pipeline. Each kitchen has its own quirks; the cooking is the same.

What I do not do is justify a design choice with "because the tool defaults to it". Defaults are starting points, not endpoints. A dashboard that is good *because* it follows the defaults is suspect. A dashboard that is good *despite* the defaults, where I had to wrestle the tool to get the right outcome, is usually the better one.

The kitchen is just the kitchen. The cooking is the cooking.
