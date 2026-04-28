---
title: "linkedin-banner-wordcloud-generator"
weight: 30
description: "A Python desktop app that reads a resume and produces a LinkedIn banner word cloud weighted by what actually matters in the document. Multi-provider AI extraction, interactive term editing, multi-language font support."
summary: "AI résumé wordcloud generator."
tags: ["python", "tkinter", "ai", "llm", "word-cloud", "matplotlib", "side-project"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Reads your résumé, asks an AI which skills matter most, and generates a LinkedIn banner image showing them at the right sizes.
{{< /lead >}}

## At a Glance

Word cloud generators have been around forever. The default ones do something simple: count word frequencies in a document, draw the words at sizes proportional to their counts. Run a resume through one of those tools and the output is the words "and," "the," "experience," and "responsible" in giant letters surrounded by every job title and skill rendered tiny because none of them appears more than once.

This tool generates word clouds that work for resumes. It reads the document (PDF, DOCX, or TXT), sends the text to an AI provider, and asks the model to identify the person's industry, extract the terms that actually represent their professional identity, and assign each term a weight that reflects how central it is rather than how often it appears. The output is a LinkedIn banner sized at 1584×396 pixels with the user's signature skills front and center.

Five AI providers are supported (Claude, ChatGPT, Gemini, Mistral, Groq), the user's API key stays on their machine, and the term list is fully editable before the cloud renders.

## The Problem

A frequency-based word cloud measures the wrong thing. In a resume, words appear once or twice and never repeat. A surgeon mentions "cardiothoracic" once in their headline and never again, because everything below the headline is implied by it. A litigator mentions "first-chair trial experience" once because every bullet that follows expands on what it means. Word frequency does not tell the reader what the document is about; the structure and prose do.

There are three failure modes this creates for a frequency-based approach.

**Low-signal terms dominate.** "Experience," "team," "managed," "developed," and a dozen other resume action words appear more often than any actual skill. The cloud renders those at giant size and the real content tiny.

**The professional vocabulary is uneven.** A data scientist might mention "Python" five times across different bullets and "stochastic gradient descent" once. The frequency model would size Python five times larger than SGD, even though the latter is more revealing about the person's expertise.

**Compound terms get split.** A frequency counter sees "machine learning" as the words "machine" and "learning," which appear separately throughout the document because both are common English words. The compound that actually matters never gets surfaced.

The right model for resume word clouds is not frequency but importance: how central is each term to this person's professional identity? That question is what humans answer when reading a resume, and it is what the AI prompt is designed to elicit.

## The Approach

A Tkinter desktop app with a clear five-stage pipeline.

The tool reads the resume file using a format-appropriate library: `pdfplumber` for PDFs, `python-docx` for Word documents, plain text for everything else. The extracted text is validated (must be at least 150 characters, must not contain more than 5% unreadable bytes) and truncated to 15,000 characters before being sent to the AI provider.

The AI returns up to 60 main terms plus 30 runner-ups, each as a `{term, weight}` pair in JSON. The weights span 1,000 to 10,000, with carefully calibrated bands the prompt instructs the model to use: signature skills at 9,000-10,000 (the things that would appear in the person's elevator pitch), core competencies at 7,000-8,999, and so on down to peripheral mentions at 1,000-2,999.

A deduplication pass removes single-word terms that are already represented by higher-weight compounds. If the model returns both "Power BI" at 9,800 and "BI" at 7,400, the standalone "BI" gets dropped because the compound covers it. If the model returns "Python" at 8,700 alongside "Python GUI" at 2,000, "Python" stays because the compound has lower weight and clearly does not subsume it.

The user reviews the deduplicated terms in an interactive table: sort by weight or name, remove anything they disagree with (auto-backfilling from runner-ups), manually add anything the model missed, promote runner-ups into the main list. Once the list looks right, the user picks an appearance (light or dark background, one of eight color palettes) and clicks Generate. The cloud renders to a temp file first so the user can preview it before saving anywhere permanent.

The pipeline:

{{< mermaid >}}
flowchart TD
    A[User selects resume PDF/DOCX/TXT] --> B[Extract raw text via format-specific library]
    B --> C[Validate text: length, garbage ratio]
    C -->|Valid| D[Truncate to 15,000 chars and send to AI provider]
    C -->|Invalid| E[Show user-friendly error]
    D --> F[Parse JSON response: 60 main terms + 30 runner-ups]
    F --> G[Deduplicate single-word terms covered by compounds]
    G --> H[User reviews and edits term list]
    H --> I[Render word cloud to temp PNG]
    I --> J{PNG size over 3MB?}
    J -->|Yes| K[Quantize to 256 colors via Pillow]
    J -->|No| L[Final PNG]
    K --> L
    L --> M[User clicks Save As to commit]
{{< /mermaid >}}

## Why The Prompt Matters

The quality of the output depends almost entirely on the quality of the extraction prompt. A casual prompt ("extract the important skills from this resume") returns plausible-looking results that are subtly wrong: degree terms get included, action verbs sneak in, casing is inconsistent, weights are arbitrary. A carefully-engineered prompt produces results that are usable without much editing.

The prompt for this tool is roughly 100 lines and has five distinct sections. It asks the model to identify the person's industry first, before extracting anything, so the rest of the analysis is calibrated to that field. It enumerates what counts as a relevant term across diverse industries (with concrete examples spanning law, medicine, marketing, engineering, finance, and creative fields) so the model does not anchor on any one professional vocabulary. It defines the weighting bands explicitly and tells the model to calibrate weights relative to each other, not in absolute terms. It enforces casing conventions: all-caps for initialisms, brand casing for products, lowercase for libraries that style themselves lowercase. And it has a substantial exclusion list (no personal info, no section headings, no action verbs, no degree terms, no generic filler) that catches the categories of false positive most likely to slip through.

The prompt also requires the response to be valid JSON with no markdown fences and no preamble. This matters because the parsing code on the Python side needs to deserialize the response cleanly; a response that wraps the JSON in `` ```json ` blocks or includes an explanatory paragraph would fail to parse. Different models handle this instruction differently, but the prompt gives every model the same explicit constraint.

## Why The Deduplication Matters

When the AI returns "Power BI" alongside "BI," or "Machine Learning" alongside "Learning," or "Patient Care" alongside "Care," a frequency-based word cloud would render both. The compound term and its single-word component compete for visual space, the cloud looks redundant, and the user has to manually clean up.

The deduplication algorithm runs before the term list is ever shown to the user. For each single-word term, it checks whether any compound term in the same set has the standalone word as a component AND has weight greater than or equal to the standalone term's weight. If so, the single-word term is dropped silently. Compound terms are always kept regardless.

The algorithm correctly handles edge cases. "SQL" stays in the list even when "PostgreSQL" is also present, because they are different things, not a compound containing SQL as a separate word. "Python" stays alongside "Python GUI" because the compound has lower weight, indicating that Python carries independent meaning beyond the compound. The dedupe runs against both the main terms and the runner-ups together, so a runner-up "BI" gets dropped if a main term "Power BI" has higher weight.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The extraction prompt with weighting bands and casing rules" >}}

The prompt is structured as a sequence of instructions, each addressing a specific failure mode the author has seen across many test resumes. A condensed view of the structure:

```
You are an expert resume analyst with deep knowledge across all professional
fields...

Your task: read the resume below, identify the person's industry and role,
then extract the terms that best represent their professional identity for a
LinkedIn banner word cloud.

Return ONLY a JSON object — no markdown fences, no preamble, no explanation.
Your entire response must be valid JSON and nothing else.

━━━  WEIGHTING GUIDE  ━━━

Weight reflects how central a skill is to the person's professional identity
— not just how often it appears.

  9000–10000  Signature skills: what this person IS known for. The things
              that would appear in their headline or elevator pitch.
              These should be few (3–8 terms).
  7000–8999   Core competencies: used regularly, clearly demonstrated with
              results, central to their day-to-day role.
  5000–6999   Strong supporting skills: mentioned with specifics, part of
              their toolkit but not the headline.
  3000–4999   Relevant but secondary: present and genuine, adds breadth.
  1000–2999   Peripheral: briefly mentioned, supporting context.

━━━  CASING  ━━━

Use each term's real-world official casing — not blind title-case:
• All-caps for initialisms and acronyms: SQL, API, CPA, MBA, HIPAA, ...
• Brand/product casing: PowerPoint, QuickBooks, LinkedIn, GitHub, ...
• Lowercase brands that style themselves lowercase: pandas, numpy, npm, ...
• Title Case for multi-word domain terms: Financial Modeling, Patient Care, ...
```

Three sections deserve particular attention.

The weighting guide gives explicit numerical bands with descriptions in plain language. Without these bands, models tend to compress all weights into a narrow middle range, making the resulting word cloud visually flat. With the bands, the model produces the kind of distribution that renders well: a few large terms, many medium terms, and a long tail of small ones.

The casing instruction is unusual but important. AI models default to title-casing everything, which produces "Sql" and "Hipaa" and "Pandas" — all wrong. The explicit instruction to preserve real-world casing fixes this, but only when the prompt is detailed enough to cover the three distinct conventions (all-caps, brand casing, lowercase brands).

The exclusion list catches what would otherwise slip in: degree terms ("Bachelor," "MBA"), action verbs ("Managed," "Developed"), generic filler ("Various," "Multiple"), and unsupported soft skills ("Team Player," "Hard Worker"). Without explicit exclusions, models include these in the main term list because they appear prominently in resumes. With the list, they get dropped at the source rather than during post-processing.

The runner-ups field at the end has a specific instruction: runner-ups must be genuine terms from the document, not invented filler. This addresses a common failure mode where models, asked to produce a fixed-size list, pad with plausible-sounding terms that do not actually appear in the source.

{{< /accordionItem >}}

{{< accordionItem title="The compound-aware deduplication algorithm" >}}

The deduplication runs against the union of main terms and runner-ups, treating them as a single pool for the purpose of detecting compound coverage:

```python
def _dedupe_subword_terms(
    terms: dict[str, int],
    reference: dict[str, int] | None = None,
) -> dict[str, int]:
    """Remove single-word terms already represented by a higher-weight compound."""
    pool = dict(terms)
    if reference:
        pool.update(reference)

    result: dict[str, int] = {}
    for term, weight in terms.items():
        parts = re.split(r"[ _]+", term)
        if len(parts) != 1:
            # Compound terms are always kept.
            result[term] = weight
            continue

        t_lower = term.lower()
        covered = any(
            other != term
            and len(re.split(r"[ _]+", other)) > 1
            and t_lower in [p.lower() for p in re.split(r"[ _]+", other)]
            and other_w >= weight
            for other, other_w in pool.items()
        )
        if not covered:
            result[term] = weight
        else:
            log.debug("Deduped subword '%s' (covered by a compound)", term)

    return result
```

The split on `[ _]+` handles both the user-facing space-separated form ("Power BI") and the underscore-separated internal form ("Power_BI"). The tool toggles between these representations at display time, so the dedupe needs to work regardless of which form the term currently has.

The case-insensitive comparison (`t_lower` against `[p.lower() for p in ...]`) ensures that "BI" gets recognized as a component of "Power BI" even though the casing differs from how the compound was returned. Without case-insensitivity, the compound's `BI` would not match the standalone term's `BI` if either was spelled differently.

The weight comparison (`other_w >= weight`) is the central heuristic. A compound covers a single-word component only when the compound is at least as important. This protects against cases where the model legitimately lists both because they carry different meanings: if "Python" weighs 8,700 and "Python GUI" weighs 2,000, the compound is clearly subsidiary and the standalone Python should stay. If "Power BI" weighs 9,800 and "BI" weighs 7,400, the compound clearly subsumes the standalone and BI should drop.

The `other != term` guard prevents the algorithm from ever matching a term against itself. This sounds like a paranoid check but it matters: if the term list contains both "Python" and "python" (unlikely but possible), the case-insensitive comparison would otherwise consider each one a "match" for the other.

{{< /accordionItem >}}

{{< accordionItem title="PNG size cap with Pillow quantization fallback" >}}

LinkedIn enforces an upload size limit on banner images. The wordcloud library produces lossless PNGs that can comfortably exceed that limit when the cloud is busy, the colors are varied, and the text has many small elements. The tool handles this by detecting oversized output after rendering and quantizing it down if needed:

```python
wc = WordCloud(**wc_kwargs).generate_from_frequencies(jittered)
fig, ax = plt.subplots(figsize=(15.84, 3.96))
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
plt.tight_layout(pad=0)
plt.savefig(output_path, format="png", dpi=300,
            bbox_inches="tight", pad_inches=0)
plt.close(fig)

# Quantise to 256 colours if the lossless PNG is above the size cap.
file_mb = os.path.getsize(output_path) / (1024 * 1024)
if file_mb > MAX_FILE_SIZE_MB:
    log.info("PNG too large (%.2f MB), quantising to 256 colours", file_mb)
    img = Image.open(output_path)
    img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    img.save(output_path, format="png", optimize=True)
    file_mb = os.path.getsize(output_path) / (1024 * 1024)
```

The initial render is lossless and high-DPI (300 DPI). For most resumes, this produces a PNG well under 3MB and the quantization branch never triggers. The check happens only after the file is on disk, so the cost of the test is one file-size lookup.

When the file exceeds the cap, Pillow's `quantize` method reduces the color palette to 256 distinct colors using the median-cut algorithm. Median-cut works by recursively splitting the color cube into halves containing equal numbers of pixels, picking representative colors from each half. The result is a palette that preserves visual fidelity better than naive uniform quantization, especially for word clouds where the colors are concentrated in a few hue regions rather than spread evenly across the spectrum.

The `optimize=True` flag on the second save tells Pillow to use the smallest possible PNG encoding (best Huffman trees, etc.). Combined with the reduced palette, this typically cuts file size by 60-80% with minimal visible quality loss for word cloud content. The text edges remain crisp because PNG quantization preserves the high-contrast boundaries that make text readable.

The fallback is silent. The user does not know whether their cloud was quantized or not; the file just lands at a size LinkedIn will accept. The decision to quantize is logged for debugging but not surfaced in the UI, on the principle that a fallback the user cannot meaningfully act on does not need to be a user-facing concern.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.9+
- **GUI:** tkinter (built into Python)
- **AI providers:** [anthropic](https://pypi.org/project/anthropic/), [openai](https://pypi.org/project/openai/), [google-genai](https://pypi.org/project/google-genai/), [mistralai](https://pypi.org/project/mistralai/), [groq](https://pypi.org/project/groq/), via a shared `BaseProvider` interface
- **Document parsing:** [pdfplumber](https://github.com/jsvine/pdfplumber) for PDFs, [python-docx](https://python-docx.readthedocs.io/) for DOCX, plain text for TXT
- **Word cloud rendering:** [wordcloud](https://github.com/amueller/word_cloud), [matplotlib](https://matplotlib.org/) for PNG output
- **Image post-processing:** [Pillow](https://pillow.readthedocs.io/) for size checks and quantization
- **OS theming:** [darkdetect](https://pypi.org/project/darkdetect/) for system light/dark mode detection
- **Storage:** plain JSON config in `~/.wordcloud_generator/`

## Repo

[github.com/hihipy/linkedin-banner-wordcloud-generator](https://github.com/hihipy/linkedin-banner-wordcloud-generator)
