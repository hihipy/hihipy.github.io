---
title: "decode-for-humans"
weight: 20
description: "A desktop tool that translates source code into plain-English explanations using one of five AI providers. Built for the people who own the decisions code makes but can't read code themselves."
summary: "AI source-code translator."
tags: ["python", "ai", "llm", "multi-provider", "documentation", "customtkinter"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Takes a piece of source code and uses an AI to explain what it does in plain English, with five providers to choose from.
{{< /lead >}}

## At a Glance

Most code is written by technical people and read only by other technical people. But code makes decisions, handles data, processes payments, sends notifications, and otherwise affects real workflows. The people accountable for those workflows (managers, auditors, compliance officers, executives) are often unable to read the code that drives them.

This tool closes that gap. Drop in a source file, pick an AI provider, and get back a structured explanation written in plain English: what the file does, how it works step by step, what its inputs and outputs are, what assumptions it makes, what risks it creates, and a paragraph-length executive summary at the end. Output comes in two formats: Markdown for technical reviewers (renders cleanly in GitHub, Obsidian, VS Code, Notion) and plain text for everyone else (paste straight into Word, Google Docs, email).

## The Problem

The gap between "people who write code" and "people who own what code does" is older than software itself. Three failure modes show up repeatedly.

**Compliance documentation.** A regulated environment requires written explanations of how systems work. Producing those explanations by hand is slow, gets out of date the moment the code changes, and gives no guarantee of accuracy. Most compliance docs end up describing what the code was supposed to do rather than what it actually does.

**Code review by non-developers.** When a non-technical stakeholder needs to sign off on a piece of code (a workflow change, a data pipeline modification, a new automation), they cannot read the diff. They depend on the developer's verbal summary, which is necessarily filtered through the developer's perspective on what matters.

**Auditing decisions made by code.** A claim is denied. A loan is rejected. A user is flagged. The decision was made by code. The person reviewing the decision needs to understand what the code did and why, but cannot read it.

Every existing solution has the same shape: a developer has to translate. That works at small scale and breaks at any larger scale, because developers are the bottleneck, and translating code into prose is exactly the kind of work that nobody wants to do every time it is needed.

## The Approach

A desktop application that wraps any of five AI providers (Claude, ChatGPT, Gemini, Mistral, Groq) behind a uniform interface, reads source files in 55 languages including Jupyter and Quarto notebooks, builds a structured prompt asking for a specific output format, and produces two output files designed for different audiences.

The pipeline is straightforward but each step does specific work:

{{< mermaid >}}
flowchart TD
    A[User selects file] --> B[Detect language and read content]
    B --> C[Build structured prompt]
    C --> D[Estimate token count and display cost preview]
    D -- user confirms --> E[Send prompt to chosen AI provider]
    E --> F[Parse response into sections]
    F --> G[Write Markdown output]
    F --> H[Write plain-text output]
    G --> Done[Files appear in Downloads]
    H --> Done
{{< /mermaid >}}

The estimate-before-call step is what distinguishes this from a naive "send to API and hope" tool. Every API call has a cost. Letting the user see that cost (and decide not to pay it) before any request fires is the difference between a tool you trust and a tool you use cautiously.

## Walking Through the Pipeline

### Detecting the Language

Language detection runs in two phases. First, a fast extension lookup against a 55-language map handles the common case (`.py` is Python, `.rs` is Rust, `.ipynb` is Jupyter). When the extension is ambiguous or missing, the tool falls back to content inspection: it checks for shebangs (`#!/usr/bin/env python3`), distinctive syntax markers, and (for Julia files) a check for Pluto reactive notebook headers, which look like regular Julia but require different handling.

Files that look binary are rejected before any read attempt, and files that look minified (long lines, single-character variable names, no whitespace) trigger a warning because the explanation quality drops sharply when the source has been deliberately obfuscated.

### Reading Notebooks

Notebooks are not source files. They are JSON documents containing alternating cells of markdown narrative and code. A naive read that ignores cell structure throws away the most useful context: the developer's own explanation of what each step is doing.

The notebook reader walks each cell in order and emits a flattened representation that preserves the alternation:

```python
for i, cell in enumerate(data.get("cells", []), 1):
    cell_type = cell.get("cell_type", "code")
    source    = "".join(cell.get("source", []))
    if not source.strip():
        continue
    if cell_type == "markdown":
        # Prefix each markdown line with #  so it reads clearly
        md_lines = [f"# {l}" if l.strip() else "#" for l in source.splitlines()]
        cells.append(f"# ── Cell {i}: Markdown ──\n" + "\n".join(md_lines))
    elif cell_type == "code":
        cells.append(f"# ── Cell {i}: Code ──\n{source}")
    elif cell_type == "raw":
        cells.append(f"# ── Cell {i}: Raw ──\n# {source}")
```

Markdown cells become commented-out prose with a cell-number header. Code cells get the same header treatment but their source is preserved verbatim. The LLM sees the original analyst's narrative interleaved with the code that implements each step, which produces noticeably better explanations than feeding raw cells in any other order.

### Building the Prompt

The prompt is structured to force a consistent output schema. Every explanation comes back with the same six sections:

1. **What This File Does** — plain-language summary of the purpose
2. **How It Works — Step by Step** — numbered walkthrough of the logic
3. **Key Things to Know** — inputs, outputs, risks, assumptions
4. **Dependencies & Setup** — what needs to be installed (only when relevant)
5. **Plain-English Summary** — executive-ready paragraph
6. **Original Source Code** — the full source, appended for reference

The structure is deliberate. Predictable section headers mean the output renders consistently regardless of which provider was used, and the markdown writer can produce a working table of contents from any response. Without enforced structure, every provider's output would have different formatting, and downstream tools would have to deal with that variability.

### Estimating Cost Before Calling

Before any API request fires, the tool computes an estimated token count for the prompt and adds an estimate for the expected response. The estimate is intentionally rough but transparent:

```python
# Input tokens + estimated output (~2000 tokens of explanation)
est = len(prompt) // 4 + 2000
```

Dividing character count by four is the standard tokenization approximation across major LLM tokenizers. The fixed `+ 2000` reserves space for the expected explanation. The result is shown in the GUI before the user clicks Decode, and is also rolled up across all selected files in batch mode so the user sees the total estimated cost of a folder before approving the run.

The 2000-token reserve is chosen against observed output sizes; explanations of typical files run between 1500 and 2500 tokens. The estimate tends to overshoot by 10-20% for short files and undershoot slightly for very long ones, but neither error is large enough to misrepresent cost in a way that would surprise the user.

### Producing Two Outputs

Markdown is the natural format for technical readers. It renders correctly on GitHub, Obsidian, VS Code preview, Notion, and any other tool that handles markdown. But pasting markdown into Microsoft Word produces a wall of asterisks and pound signs, and pasting it into an email is similarly ugly.

The tool generates both formats from the same response. The plain-text version strips markdown syntax, expands link targets inline, replaces bullet characters with simple dashes, and re-flows paragraphs so they read cleanly in any text editor. The markdown version keeps everything: heading anchors, code fences, inline emphasis, and an auto-generated table of contents at the top.

The result is one explanation, two presentations, no manual conversion.

## Why The Provider Abstraction Matters

The tool supports five AI providers (Claude, ChatGPT, Gemini, Mistral, Groq) through a single abstract interface. This is a design decision worth being explicit about, because most code-explanation tools lock the user into one provider and quietly punish them for it.

Three reasons the abstraction matters:

**Cost varies dramatically.** Groq has a generous free tier; Claude and ChatGPT do not. A user explaining a one-off file might prefer the speed of a paid tier, while a user batch-decoding a folder of fifty files would rather use the free option. Locking the user into one provider takes that choice away.

**Quality varies by language and task.** Different models handle different languages with different fluency. A user explaining Rust might find one provider's output clearly better; a user explaining R might prefer a different one. The abstraction lets the user pick per-task.

**API access changes.** Providers raise prices, deprecate models, restrict access, or shut down. A tool that hardcodes one provider becomes useless when that provider becomes unavailable. The abstraction means switching providers is one dropdown change in the GUI, with no code modification.

The cost of this abstraction is roughly fifty lines of code per provider plus an abstract base class. That is a small price for the long-term flexibility it buys.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The provider abstraction with a registry pattern" >}}

The abstract base class defines the contract every provider must satisfy:

```python
class BaseProvider:
    name: str = "base"
    model: str = ""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def explain(self, prompt: str) -> str:
        raise NotImplementedError(
            f"{self.name} provider must implement explain()"
        )

    def test_connection(self) -> bool:
        try:
            result = self.explain("Say the word OK and nothing else.")
            return bool(result and result.strip())
        except Exception:
            return False
```

Every concrete provider subclasses this and implements just one method (`explain`). The `test_connection` method is shared because the test is the same regardless of provider: send a minimal prompt, check that the response is non-empty.

A central registry maps display names to provider classes:

```python
PROVIDERS: dict[str, Type[BaseProvider]] = {
    "Claude": AnthropicProvider,
    "ChatGPT": OpenAIProvider,
    "Gemini": GoogleProvider,
    "Mistral": MistralProvider,
    "Groq": GroqProvider,
}

def get_provider(name: str, api_key: str) -> BaseProvider:
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider '{name}'. Choose from: {list(PROVIDERS.keys())}")
    return PROVIDERS[name](api_key)
```

This is a textbook strategy pattern. The GUI populates its dropdown from `PROVIDERS.keys()`, the rest of the application calls `get_provider(name, key).explain(prompt)`, and the concrete provider class is the only place that knows about the specific HTTP shape of any given API.

Adding a sixth provider is a self-contained addition: write a class that subclasses `BaseProvider` and implements `explain()`, register it in `PROVIDERS`, done. No other file in the codebase needs to change.

{{< /accordionItem >}}

{{< accordionItem title="Notebook handling with cell-aware preservation" >}}

A notebook is structurally a JSON document with a `cells` array. Each cell has a `cell_type` (`code`, `markdown`, or `raw`) and a `source` field holding the actual content. The reader walks the cells in order and produces a single representative string that preserves the cell structure for the LLM:

```python
def _read_notebook(path: Path) -> tuple[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    kernel_lang = (
        data.get("metadata", {})
            .get("kernelspec", {})
            .get("language", "python")
    )

    cells: list[str] = []
    for i, cell in enumerate(data.get("cells", []), 1):
        cell_type = cell.get("cell_type", "code")
        source    = "".join(cell.get("source", []))
        if not source.strip():
            continue
        if cell_type == "markdown":
            md_lines = [f"# {l}" if l.strip() else "#" for l in source.splitlines()]
            cells.append(f"# ── Cell {i}: Markdown ──\n" + "\n".join(md_lines))
        elif cell_type == "code":
            cells.append(f"# ── Cell {i}: Code ──\n{source}")
        elif cell_type == "raw":
            cells.append(f"# ── Cell {i}: Raw ──\n# {source}")

    return "\n\n".join(cells), lang_name
```

Two design choices are doing real work here.

The first is that markdown cells are not stripped. They are kept as commented-out prose, which means the LLM sees the original author's intent for each section in context. Without this, the model has to infer what each block of code is *for* purely from the code itself, which is a much harder task.

The second is the cell-number prefix on every block. Notebooks often refer to themselves ("the previous cell loaded the data"; "we'll come back to this later"). Numbering each cell explicitly preserves those references, so the LLM's explanation can refer back to specific cells when describing the flow.

Quarto and R Markdown notebooks are handled separately because their format is different — markdown with embedded code chunks rather than JSON cells — but the same principle applies: preserve the alternation of prose and code rather than collapsing everything into raw source.

{{< /accordionItem >}}

{{< accordionItem title="Token estimation as a cost guard before API calls" >}}

Every API call has a cost. Some providers charge per token, some have rate limits expressed in tokens per minute, and all of them eventually impose hard caps. A tool that calls these APIs without showing the user what each call will cost is a tool that produces unpleasant surprises.

The estimator runs before any API request is fired:

```python
def _estimate_all(self, files: list):
    """Estimate tokens for each file using the real prompt — matches console display."""
    for path in files:
        try:
            code = read_file(path)
            language = detect_language(path, content=code)
            prompt = build_prompt(path.name, language, code)
            # Input tokens + estimated output (~2000 tokens of explanation)
            est = len(prompt) // 4 + 2000
        except Exception:
            try:
                # Fallback: raw byte size / 4
                est = path.stat().st_size // 4 + 2000
            except Exception:
                est = 2000
        self._token_ests[path] = est

    self.after(0, self._update_summary)
```

The estimation deliberately uses the *real* prompt that will be sent, not a sketch. Building the prompt for the estimate costs almost nothing (it is local string concatenation) and guarantees the displayed estimate matches what actually goes to the API. A shortcut estimate based on file size alone would be inaccurate, because the prompt scaffolding adds a fixed overhead per file and the language-specific instructions vary.

The double-fallback (real prompt → file size → flat 2000) handles the rare case where a file fails to read for some reason, ensuring the estimate column always shows a number rather than an empty cell. An imperfect estimate is more useful than no estimate, because the user can still see that *some* cost is implied by the operation.

The estimates are computed in a background thread so the GUI stays responsive on large folders. When estimation completes, the summary label updates with the total token count and an estimated minutes-to-completion, both of which scale linearly with the number of selected files.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.10+
- **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (modern themed Tkinter widgets)
- **Image handling:** [Pillow](https://pillow.readthedocs.io/) (provider brand icons in the settings dialog)
- **AI providers:** Anthropic, OpenAI, Google Gemini, Mistral, Groq (each via their official Python SDK)
- **Notebooks:** Native JSON parsing for `.ipynb`; markdown parsing for `.qmd` and `.rmd`

## Repo

[github.com/hihipy/decode-for-humans](https://github.com/hihipy/decode-for-humans)
