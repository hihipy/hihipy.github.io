---
title: "tabs-2-json"
weight: 50
description: "A Chromium browser extension that exports the text and metadata of the tabs you select as one structured JSON document, built for feeding page content to an LLM. It reads each page by how HTML organizes content rather than by any site-specific structure, peels navigation chrome, preserves Schema.org JSON-LD, and runs entirely in the browser with no network requests."
summary: "Open tabs to LLM-ready JSON."
tags: ["javascript", "json", "json-ld", "chrome-extension", "llm", "tool"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Turns the tabs you pick into one clean JSON document, so an LLM can read every page at once.
{{< /lead >}}

## At a Glance

Copying a page into an LLM sounds trivial: select all, copy, paste. Then you do it across a dozen open tabs and the friction shows up at once. Each tab is a manual round trip, the pasted text arrives wrapped in navigation and footer boilerplate, and the structured data the page already ships gets dropped on the floor.

`tabs-2-json` is a Chromium browser extension that reads the tabs you select and hands back a single JSON document. Open the popup, tick the tabs you want, and choose Download JSON or Copy to Clipboard. Readable tabs are selected by default; browser internal pages and any domains you block are shown disabled and never read. One file comes back, and an LLM can consume it end to end.

It works across page types by relying on how HTML organizes content rather than assuming any particular site structure. The read runs through the [`chrome.scripting`](https://developer.chrome.com/docs/extensions/reference/api/scripting) API, only on the tabs you pick, and only when you trigger an export. It runs in any Chromium browser on [Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3): Chrome, Brave, Edge, Opera, and others, and installs in one click from the [Chrome Web Store](https://chromewebstore.google.com/detail/tabs2json/bljpjkglinfdphfopjdfoookglelobhj).

## The Problem

Three frictions show up in real LLM-assisted work spread across many tabs.

**Copying tabs one at a time is slow.** A job search, a literature scan, or a competitive review means ten to thirty open tabs. Feeding them to a model one copy-paste at a time is a round trip per tab, and the model only ever holds one page at a time, so it cannot reason across the whole set.

**Pasted browser text is mostly chrome.** Select-all on a modern page pulls the nav bar, the cookie banner, the sidebar, the footer, and the newsletter prompt along with the article. The model spends context budget on boilerplate, and the signal it needs sits buried in the noise every page repeats.

**Structured data gets thrown away.** Many pages already ship [Schema.org](https://schema.org/) [JSON-LD](https://json-ld.org/): a `JobPosting` with structured title, organization, and location, or an `Article` with author and publish date. Copy the visible text and all of that is lost, even though it is the cleanest, most machine-readable description the page has.

`tabs-2-json` answers all three: the readable content from every tab you pick, the chrome stripped, the structured data preserved, assembled into one JSON document in a single click.

## The Approach

One popup lists the open tabs. You pick the ones you want and trigger an export; nothing is read until then. For each selected tab the extension injects a single extractor function through [`chrome.scripting`](https://developer.chrome.com/docs/extensions/reference/api/scripting), reads the page in the tab's own context, and returns a plain data object. All work happens in the browser: the extension makes no network requests and includes no analytics or tracking.

The extractor reads each page the same way regardless of how the page is built. It finds a content root, reads the visible text, peels leading navigation, collects any structured data, and reads standard metadata. The popup then shapes each result according to your settings and assembles one JSON payload.

{{< mermaid >}}
flowchart TD
    A["Popup: pick tabs, trigger export"] --> B["chrome.scripting injects pageExtractor into each selected tab"]
    B --> C1["Find content root: main, article, role=main, else density heuristic, else body"]
    B --> C2["Read innerText, peel leading nav or aside chrome"]
    B --> C3["Parse JSON-LD, reduce embedded HTML to text"]
    B --> C4["Read meta, Open Graph, canonical, lang"]
    C1 --> D["Per-tab record"]
    C2 --> D
    C3 --> D
    C4 --> D
    D --> E["Apply settings, prune empty fields"]
    E --> F["Assemble payload: exported_at, tab_count, tabs[]"]
    F --> G["Download JSON or Copy to Clipboard"]
{{< /mermaid >}}

The read is page-type-agnostic by design. A semantic modern page and an older table-layout page go through the same steps and come out in the same shape.

## Walking Through the Export

### Choosing the Content Root

The first job is deciding which part of the page is the content. Semantic markup answers this directly when it exists, so the extractor looks for a `<main>`, then an `<article>`, then an element with `role="main"`. When none exist, it scores candidate blocks by how much text they hold against how much of that text is links, so a navigation menu loses to real prose. The body is the last resort.

```javascript
let root =
    document.querySelector("main") ||
    document.querySelector("article") ||
    document.querySelector('[role="main"]');
let source = root ? root.tagName.toLowerCase() : null;

if (!root) {
    const bodyLength = document.body
        ? (document.body.innerText || "").length
        : 0;
    let best = null;
    let bestScore = 0;

    document
        .querySelectorAll("body div, body section, body td, body table")
        .forEach((el) => {
            const text = el.innerText || "";
            if (text.length < 200) {
                return;
            }
            // Penalise link-heavy blocks so navigation menus lose to real content.
            let linkLength = 0;
            el.querySelectorAll("a").forEach((a) => {
                linkLength += (a.innerText || "").length;
            });
            const score = text.length - linkLength * 2;
            if (score > bestScore) {
                bestScore = score;
                best = el;
            }
        });

    if (best && bestScore > bodyLength * 0.4) {
        root = best;
        source = "heuristic";
    } else {
        root = document.body;
        source = "body";
    }
}
```

The score is the block's text length minus twice its link length, so a link-heavy block is penalized hard and a prose-heavy block wins. The heuristic result is only trusted when it accounts for more than 40% of the body's text; below that, the extractor falls back to the body rather than risk picking a fragment. Every record carries a `content_source` field recording which path won: `main`, `article`, an element tag, `heuristic`, or `body`. That tells the consumer how confident to be in the extraction.

### Peeling Leading Chrome

Reading `innerText` from the chosen root preserves visible block structure, but the root can still begin with an in-page menu bar that lives inside it: namespace tabs, section navigation, a wiki's Read/Edit strip. The extractor removes a leading `nav` or `aside` block only when that block's normalized text is an exact prefix of the body text. That condition is what keeps it safe: a menu that appears mid-page is never touched, and an article's own heading is never mistaken for chrome.

```javascript
const chromeTexts = Array.from((root || document).querySelectorAll(CHROME_SELECTOR))
    .map((el) => normalize(el.innerText))
    .filter((t) => t.length >= 8)
    .sort((a, b) => b.length - a.length);

let peeled = true;
while (peeled) {
    peeled = false;
    const normBody = normalize(rootText);
    for (const chromeText of chromeTexts) {
        if (chromeText && normBody.startsWith(chromeText)) {
            rootText = sliceAfterNormalized(rootText, chromeText.length).replace(/^\s+/, "");
            peeled = true;
            break;
        }
    }
}
```

The selector is `nav, aside, [role="navigation"], [role="complementary"]`, so only real landmark elements qualify; a header widget built from plain divs is not a landmark and stays. Blocks under 8 normalized characters are ignored, and the loop peels stacked blocks one at a time until nothing more matches. The one subtlety is that matching happens on normalized text but the cut is applied to the original, so the surviving body keeps its own spacing. That mapping is in the accordion below.

### Keeping Structured Data Clean

Every JSON-LD block on the page is parsed verbatim and deduplicated, whatever its Schema.org type. The catch is that some sites embed large HTML fragments inside JSON-LD string values, most commonly a job posting whose `description` is a full block of markup. Left alone, that markup and its inline CSS leak into the output as noise. The extractor reduces any string value carrying markup to its text, and leaves every other value untouched.

```javascript
const HTML_TAG = /<[a-z!/][^>]*>/i;

function stripHtml(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    doc.querySelectorAll("script, style, noscript, template").forEach((el) => {
        el.remove();
    });
    return (doc.body.textContent || "").replace(/\s+/g, " ").trim();
}

function sanitizeStructured(node) {
    if (typeof node === "string") {
        return HTML_TAG.test(node) ? stripHtml(node) : node;
    }
    if (Array.isArray(node)) {
        return node.map(sanitizeStructured);
    }
    if (node && typeof node === "object") {
        const out = {};
        Object.keys(node).forEach((key) => {
            out[key] = sanitizeStructured(node[key]);
        });
        return out;
    }
    return node;
}
```

Parsing through `DOMParser` as `text/html` does not execute scripts and does not touch the live page. The `script`, `style`, `noscript`, and `template` elements are dropped first, because their text is CSS and JS that would otherwise survive a plain `textContent` read and replace the markup as a different kind of noise. A string without markup is returned as is, so ordinary values, URLs, and text that merely contains a bare `<` are left alone.

### The Output Record

Every tab record always carries `id`, `title`, `url`, `content_source`, `captured_at`, and `ok`. On success, the optional fields appear only when the page provides them and the matching setting is on, so an absent key means "not provided" rather than "empty". A single record for a job-posting tab looks like this:

```json
{
  "id": 128,
  "title": "Data Analyst III, Herbert Business School",
  "url": "https://careers.example.edu/jobs/data-analyst-iii",
  "canonical_url": "https://careers.example.edu/jobs/data-analyst-iii",
  "site_name": "Example University Careers",
  "description": "Analyze operational and financial data for the Dean's Office.",
  "language": "en",
  "content_source": "main",
  "captured_at": "2026-07-16T14:32:07.918Z",
  "ok": true,
  "headings": [
    { "level": 1, "text": "Data Analyst III" },
    { "level": 2, "text": "Minimum Qualifications" }
  ],
  "structured_data": [
    {
      "@type": "JobPosting",
      "title": "Data Analyst III",
      "hiringOrganization": { "@type": "Organization", "name": "Example University" },
      "jobLocation": { "@type": "Place", "address": "Coral Gables, FL" }
    }
  ],
  "text": "Data Analyst III\nMinimum Qualifications\nBachelor's degree and three years of relevant experience...",
  "word_count": 418
}
```

Boolean flags are present only when true, so their absence means false. `text_truncated` marks text shortened by the video trim or the character cap. `low_signal` marks an extraction to distrust, set when the text came back nearly empty (under 200 characters, the usual sign of a client-rendered page that never populated) or when the page is video-only. A `content_type` of `video` appears on video-only pages, whose real content sits in `structured_data` rather than the body.

A few consumer rules follow from the shape. Gate on `ok` before reading anything else; a failed capture carries only `id`, `title`, `url`, `captured_at`, `ok` set to `false`, and a short `error`. Treat `low_signal` or a `video` content type as a signal to lean on `structured_data` over `text`. And use `id` as the join key, because `url` is not unique once Strip Query Parameters removes the query string.

## Why Local-Only Matters

The privacy stance is not a setting; it is the architecture. The extension makes no network requests at all. There is no server, no analytics, and no telemetry, so there is nothing to opt out of. Everything the extension reads stays in the browser until you download it or copy it yourself.

The read is also scoped tightly. `chrome.scripting` runs the extractor only on the tabs you select, and only when you click Download or Copy. Browser internal pages are not scriptable and are shown disabled. Any domain you add to the block list is refused before a read is attempted, matched on the host and its subdomains. Strip Query Parameters drops the query string and fragment from every output URL, while the per-tab `id` preserves a stable join key even after the parameters are gone.

## Under The Hood

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The full page extractor" >}}

The whole read is one self-contained function injected into the target page. It cannot reference anything from the popup scope, so every helper it needs is defined inside it. It returns a plain data object; the popup does the settings-dependent shaping afterward.

```javascript
function pageExtractor(lowSignalMinChars) {
    const attr = (selector, name) => {
        const el = document.querySelector(selector);
        return el ? el.getAttribute(name) : null;
    };

    const meta = (keys) => {
        for (const key of keys) {
            const el = document.querySelector(
                'meta[name="' + key + '"], meta[property="' + key + '"]'
            );
            if (el && el.getAttribute("content")) {
                return el.getAttribute("content");
            }
        }
        return null;
    };

    // Collect any JSON-LD blocks verbatim, deduped, without interpreting them.
    const seen = new Set();
    const structured = [];
    document
        .querySelectorAll('script[type="application/ld+json"]')
        .forEach((script) => {
            const raw = (script.textContent || "").trim();
            if (!raw || seen.has(raw)) {
                return;
            }
            seen.add(raw);
            try {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    structured.push(...parsed);
                } else {
                    structured.push(parsed);
                }
            } catch (err) {
                // Ignore malformed JSON-LD.
            }
        });

    // Choose the content root: semantic tags first, then a density heuristic for
    // pages with no semantic structure, then the body as a last resort. This
    // keeps extraction working across both modern and older HTML.
    let root =
        document.querySelector("main") ||
        document.querySelector("article") ||
        document.querySelector('[role="main"]');
    let source = root ? root.tagName.toLowerCase() : null;

    if (!root) {
        const bodyLength = document.body
            ? (document.body.innerText || "").length
            : 0;
        let best = null;
        let bestScore = 0;

        document
            .querySelectorAll("body div, body section, body td, body table")
            .forEach((el) => {
                const text = el.innerText || "";
                if (text.length < 200) {
                    return;
                }
                // Penalise link-heavy blocks so navigation menus lose to real content.
                let linkLength = 0;
                el.querySelectorAll("a").forEach((a) => {
                    linkLength += (a.innerText || "").length;
                });
                const score = text.length - linkLength * 2;
                if (score > bestScore) {
                    bestScore = score;
                    best = el;
                }
            });

        if (best && bestScore > bodyLength * 0.4) {
            root = best;
            source = "heuristic";
        } else {
            root = document.body;
            source = "body";
        }
    }

    const headings = [];
    (root || document).querySelectorAll("h1, h2, h3, h4, h5, h6").forEach((h) => {
        const text = (h.innerText || "").trim();
        if (text) {
            headings.push({ level: Number(h.tagName[1]), text: text });
        }
    });

    let rootText = root ? root.innerText : "";

    // Peel leading navigation chrome. innerText of the content root can begin
    // with an in-page menu bar (namespace tabs, section nav) that lives inside
    // the root. A nav or aside block is removed only when its text is an exact
    // prefix of the body text, so this never touches prose mid-page and never
    // drops an article's own heading. Header widgets built from plain divs are
    // not landmarks and are left in place.
    const CHROME_SELECTOR = 'nav, aside, [role="navigation"], [role="complementary"]';
    const normalize = (s) => (s || "").replace(/\s+/g, " ").trim();

    // Remove the first `normCount` normalised characters from the original
    // text, where normalisation trims leading whitespace and collapses each
    // internal run to one space. This maps a normalised prefix length back onto
    // the original so the surviving text keeps its own spacing.
    const sliceAfterNormalized = (original, normCount) => {
        let seen = 0;
        let inGap = true; // leading whitespace contributes nothing
        let i = 0;
        for (; i < original.length && seen < normCount; i++) {
            if (/\s/.test(original[i])) {
                if (!inGap) {
                    seen += 1; // one collapsed space per whitespace run
                    inGap = true;
                }
            } else {
                seen += 1;
                inGap = false;
            }
        }
        return original.slice(i);
    };

    const chromeTexts = Array.from((root || document).querySelectorAll(CHROME_SELECTOR))
        .map((el) => normalize(el.innerText))
        .filter((t) => t.length >= 8)
        .sort((a, b) => b.length - a.length);

    let peeled = true;
    while (peeled) {
        peeled = false;
        const normBody = normalize(rootText);
        for (const chromeText of chromeTexts) {
            if (chromeText && normBody.startsWith(chromeText)) {
                rootText = sliceAfterNormalized(rootText, chromeText.length).replace(/^\s+/, "");
                peeled = true;
                break;
            }
        }
    }

    // Near-empty check: a page that yielded almost no text is low signal. This is
    // a high-precision flag, not an attempt to judge full-but-noisy pages.
    const lowSignal = rootText.trim().length < lowSignalMinChars;

    return {
        documentTitle: document.title,
        lang: document.documentElement.getAttribute("lang") || null,
        canonical: attr('link[rel="canonical"]', "href"),
        siteName: meta(["og:site_name"]),
        description: meta(["description", "og:description", "twitter:description"]),
        author: meta(["author", "article:author"]),
        published: meta(["article:published_time", "datePublished", "date"]),
        contentSource: source,
        headings: headings.slice(0, 60),
        structured: structured,
        rawText: rootText,
        lowSignal: lowSignal
    };
}
```

{{< /accordionItem >}}

{{< accordionItem title="Peeling chrome without touching prose" >}}

Removing a leading nav block is easy to get wrong in two directions. Match on raw text and small whitespace differences between the nav element and the body cause the prefix check to miss. Normalize both and cut on the normalized string, and the surviving body loses its own line breaks and indentation. The extractor matches on normalized text but maps the cut back onto the original, so the body keeps its spacing.

```javascript
const sliceAfterNormalized = (original, normCount) => {
    let seen = 0;
    let inGap = true; // leading whitespace contributes nothing
    let i = 0;
    for (; i < original.length && seen < normCount; i++) {
        if (/\s/.test(original[i])) {
            if (!inGap) {
                seen += 1; // one collapsed space per whitespace run
                inGap = true;
            }
        } else {
            seen += 1;
            inGap = false;
        }
    }
    return original.slice(i);
};
```

The walk counts normalized characters through the original string: each non-space character counts one, and each run of whitespace counts one collapsed space, while leading whitespace counts nothing. When the count reaches the length of the matched chrome prefix, the walk stops and everything from that index on is the surviving body. The `while` loop wrapping it peels stacked leading blocks one at a time, longest first, so a page that opens with a skip link, then a primary menu, then a section nav is cleared block by block until the first line of real content sits at the top.

{{< /accordionItem >}}

{{< accordionItem title="Detecting video-only pages" >}}

A video page carries little useful body text; its real content is the `VideoObject` in the structured data. The extractor detects this by walking every JSON-LD block for its Schema.org types, descending into arrays and `@graph` containers, then asking whether the page has a video type but no article type.

```javascript
const ARTICLE_TYPES = [
    "Article",
    "NewsArticle",
    "BlogPosting",
    "TechArticle",
    "Report",
    "ScholarlyArticle"
];

function collectTypes(node, acc) {
    if (!node || typeof node !== "object") {
        return;
    }
    if (Array.isArray(node)) {
        node.forEach((item) => collectTypes(item, acc));
        return;
    }
    if (node["@graph"]) {
        collectTypes(node["@graph"], acc);
    }
    const type = node["@type"];
    if (Array.isArray(type)) {
        type.forEach((t) => acc.add(String(t)));
    } else if (type) {
        acc.add(String(type));
    }
}

function isVideoOnly(structured) {
    const types = schemaTypes(structured);
    const hasVideo = types.has("VideoObject");
    const hasArticle = ARTICLE_TYPES.some((t) => types.has(t));
    return hasVideo && !hasArticle;
}
```

A page carrying both a `VideoObject` and an `Article` is treated as an article, not a video, because it has real prose to read. When a page is video-only and the video-trim setting is on, its text is cut to a short snippet and `text_truncated` is set, while `low_signal` and a `content_type` of `video` tell the consumer to read the structured data instead. The whole judgment rests on the page's own declared types, never on guessing from the body.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** JavaScript (vanilla; no build step, no framework, no dependencies)
- **Platform:** [Chromium Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3), running in Chrome, Brave, Edge, Opera, and other Chromium browsers
- **Chrome APIs:** [`tabs`](https://developer.chrome.com/docs/extensions/reference/api/tabs), [`scripting`](https://developer.chrome.com/docs/extensions/reference/api/scripting), [`downloads`](https://developer.chrome.com/docs/extensions/reference/api/downloads), and [`storage`](https://developer.chrome.com/docs/extensions/reference/api/storage)
- **Extraction:** `innerText` from a semantic or density-scored content root, [JSON-LD](https://json-ld.org/) parsing, and standard [meta](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta), [Open Graph](https://ogp.me/), and [canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) reads
- **Output:** a single JSON document, pretty-printed or compact
- **Accessibility:** [Atkinson Hyperlegible Next](https://www.brailleinstitute.org/freefont/), [WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/) AA to AAA contrast, a brightness-not-hue palette, and [`prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) theming
- **Privacy:** all work local; no network requests, no analytics, no tracking
- **Tests:** a Node unit suite (`test/unit.mjs`) covering text cleaning, field pruning, structured-data sanitizing, and chrome peeling
- **License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Install

[Tabs2JSON on the Chrome Web Store](https://chromewebstore.google.com/detail/tabs2json/bljpjkglinfdphfopjdfoookglelobhj)

Add it and the popup lives in the toolbar. The listing is built from the source below, published under the same license.

## Repo

[github.com/hihipy/tabs-2-json](https://github.com/hihipy/tabs-2-json)
