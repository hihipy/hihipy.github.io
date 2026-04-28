---
title: "dialogorithm"
weight: 20
description: "A Python desktop app that turns phone numbers into PhD-level mathematical art. Each digit becomes a graduate-level expression that provably evaluates to that digit, rendered as a clean PNG suitable for email signatures."
summary: "Phone numbers as PhD math."
tags: ["python", "tkinter", "latex", "mathematics", "side-project"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< katex >}}

{{< lead >}}
A side project that takes a phone number and replaces each digit with a graduate-level mathematical equation that equals that digit.
{{< /lead >}}

## At a Glance

This started as a joke and ended as a moderately rigorous piece of software. It takes a phone number, replaces each digit with a verified mathematical expression that evaluates to that digit, typesets the result in LaTeX, and renders it as a PNG suitable for an email signature, a business card, or anywhere else you want to look unreasonably impressive.

The catch (and the fun) is that every expression is real math. Not parlor tricks, not made-up notation: actual results from Lie theory, algebraic geometry, topology, number theory, complex analysis, and mathematical physics. The phone number `(555) 867-5309` becomes a sequence of expressions where each one independently evaluates to its corresponding digit, and no expression repeats within a single number.

## The Idea

Phone numbers are everywhere in our daily lives but contain no information beyond their numeric value. Adding a constraint (every digit must be replaced by a different mathematical expression that proves it equals that digit) turns the same string of numbers into something with substance, while still being recoverable: anyone with a graduate math background can decode the original number by evaluating each expression.

The project sits at the intersection of two things I find genuinely interesting: rigorous mathematics, and the small craft of building tools that produce something visually distinctive. Neither half would have been satisfying alone. A tool that just spits out random-looking equations would be cheap; a math review with no practical output would be inert. Putting them together makes both halves work harder.

## What Each Digit Becomes

The equation bank contains over 200 verified expressions, with 22 to 25 distinct templates per digit. A small sample, by digit:

For \\(0\\), a classical result in analytic number theory:

$$\sum_{N=1}^{\infty} \frac{\mu(N)}{N} = 0$$

For \\(1\\), the residue of the Riemann zeta function at its only pole:

$$\lim_{s \to 1} (s-1)\zeta(s) = 1$$

For \\(3\\), the dimension of the Lie algebra of the rotation group, equal to the number of independent rotations in three-dimensional space:

$$\dim(\mathfrak{so}(3)) = 3$$

For \\(7\\), the dimension of the imaginary octonions:

$$\dim_{\mathbb{R}}(\mathbb{O}) - 1 = 7$$

The expressions are organized within each digit by mathematical area: differential and algebraic geometry, homological algebra and topology, Lie theory and representation theory, number theory and analysis, and theoretical physics. Selection within a digit is random within constraints, which keeps results unpredictable across runs.

## Combinatorics

A natural question: how many distinct outputs can the tool produce for a given phone number?

Each digit position draws independently from its pool of expressions, with the constraint that no expression repeats within a single number. For a phone number where digit \\(d\\) appears \\(m_d\\) times and has a template pool of size \\(N_d\\), the count of unique outputs is:

$$\prod_{d=0}^{9} \frac{N_d!}{(N_d - m_d)!}$$

This is a product of falling factorials, one per digit value, capturing the "no repeats within a number" constraint. The numbers grow alarmingly fast as phone numbers get longer.

| Country | Number | Unique outputs |
|---|---|---|
| United States | +1 (555) 867-5309 | ~1.16 quadrillion |
| France | +33 6 12 34 56 78 | ~1.45 quadrillion |
| Australia | +61 412 345 678 | ~1.32 quadrillion |
| United Kingdom | +44 7700 900123 | ~25.2 quadrillion |
| India | +91 98765 43210 | ~33.1 quadrillion |
| Brazil | +55 11 91234-5678 | ~606 quadrillion |
| Germany | +49 151 2345 6789 | ~793 quadrillion |

Germany and Brazil top the list because their numbers carry more total digits, and each additional digit multiplies the output space by another 22-25.

## The Pipeline

From phone number to rendered PNG, the tool runs through a fixed sequence:

{{< mermaid >}}
flowchart TD
    A[User enters number and picks country] --> B[Strip formatting and extract digits]
    B --> C[For each digit, pick a unique template from its pool]
    C --> D[Assemble templates into a single LaTeX document]
    D --> E[Compile via pdflatex to PDF]
    E --> F[Convert PDF to PNG via pdftoppm]
    F --> G[Auto-crop PNG to content boundaries]
    G --> H[Show preview popout]
    H -- user clicks Save --> I[Copy to chosen location]
    H -- user discards --> J[Delete temp file]
{{< /mermaid >}}

The temp-file dance at the end is deliberate. Generated images live in a system temp folder until the user explicitly clicks Save. A discarded run leaves nothing on disk. Saved runs go wherever the user picks, with whatever filename the user types. The tool never assumes the user wants any given output kept.

## Walking Through the Generation

### Picking Expressions Without Repeats

For each digit in the phone number, the tool selects a template from that digit's pool. The constraint is that no template can be used twice within a single number, which means a number containing the digit `5` four times needs four distinct templates from the `5` pool.

```python
def _get_unique_latex_for_digit(digit_char: str, used_formulas: Set[str]) -> str:
    """Return a LaTeX expression for digit_char not already in used_formulas.

    Tries up to MAX_UNIQUE_ATTEMPTS times to find a fresh template.
    Falls back to a random (possibly repeated) choice if the pool is exhausted.
    """
    if not digit_char.isdigit():
        return equation_bank.eq_placeholder(digit_char)
```

The fallback to allowing repeats only triggers if a digit appears more times than its pool size, which is rare: digit pools are 22-25 templates each, and very few real phone numbers contain the same digit more than 22 times.

The deduplication uses a simple set membership check rather than something more elaborate. Random selection with rejection works because the pool is small (low double digits), the number of digits per phone number is small (around 10), and the failure rate is therefore low. A fancier algorithm would not run noticeably faster and would obscure what is happening.

### Building the LaTeX Document

The template strings are raw LaTeX fragments. The document assembler wraps them in a standalone document with appropriate math mode and spacing. The `standalone` document class crops the output to exactly the content size, so the resulting PDF has no white margins to clean up later. Bold parentheses around each digit-expression are added in code (not in the templates) so the templates themselves can be reused in any context.

### Rendering to PNG

The compilation runs as a subprocess, with the output captured for log purposes. Two flags matter.

`-interaction=nonstopmode` keeps pdflatex from prompting on errors. By default, pdflatex is interactive; without this flag, an error in a template would cause the subprocess to hang waiting for a keystroke that never comes. Nonstopmode logs the error and continues, which means a malformed expression produces a logged failure rather than a frozen process.

`-r 250` tells `pdftoppm` to render at 250 DPI. Email signature images are sometimes displayed at higher resolutions than expected, so over-rendering once is cheaper than re-running for sharper output later.

## Why International Number Handling

A naive implementation would assume US-style ten-digit numbers and call it done. The tool supports 249 countries because phone-number conventions vary in ways that matter for the output:

- Digit count varies. A French mobile number is ten digits including the country code; an Indian mobile is twelve; a Brazilian is thirteen.
- Formatting conventions vary. The same nine digits get displayed as `+33 6 12 34 56 78` in France, `+34 612 345 678` in Spain, `+39 612 345 678` in Italy.
- Special prefixes vary. Toll-free, premium-rate, and shared-cost prefixes differ by country and need to be flagged because they are not the same kind of number as a regular line.

The country list follows the UN M49 geoscheme (continent → subregion → country) so the dropdown UI mirrors a familiar geographic hierarchy rather than dumping 249 names alphabetically. A user picking United States picks Americas → Northern America → United States; a user picking Vietnam picks Asia → South-eastern Asia → Vietnam.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The equation bank with verified evaluations" >}}

Each digit has a function that returns its template pool. The pool is split into thematic blocks, with comment headers indicating which mathematical area each cluster of templates belongs to. A truncated version of the `0` pool:

```python
def _get_0_templates() -> list:
    """Return the full pool of LaTeX expressions that evaluate to 0."""
    n = get_rand_int(1, 3)

    templates = [
        # --- Differential & Algebraic Geometry ---
        r"\left( d^2\omega \right)",
        r"\left( H^1(\mathbb{P}^2, \mathcal{O}(-" + str(n) + r")) \right)",
        r"\left( c_1(SU(n)) \right)",

        # --- Homological Algebra & Topology ---
        r"\left( \partial_n \circ \partial_{n+1} \right)",
        r"\left( H_1(\mathbb{S}^2; \mathbb{Z}) \right)",
        r"\left( \chi(SU(n)) \right)",

        # --- Lie Theory & Representation Theory ---
        r"\left( [X, [Y, Z]] + [Y, [Z, X]] + [Z, [X, Y]] \right)",
        r"\left( \operatorname{Tr}(T^a_{\mathfrak{su}(n)}) \right)",

        # --- Advanced Number Theory & Analysis ---
        r"\left( \sum_{N=1}^{\infty} \frac{\mu(N)}{N} \right)",
        r"\left( \Gamma(z)\Gamma(1-z)\sin(\pi z) - \pi \right)",

        # --- Theoretical & Mathematical Physics ---
        rf"\left( J_{{{n}}}(z) Y_{{{n}-1}}(z) - J_{{{n}-1}}(z) Y_{{{n}}}(z) + \frac{{2}}{{\pi z}} \right)",
        r"\left( \langle[\hat{x}, \hat{p}_x]\rangle - i\hbar \right)",
        r"\left( \nabla_\mu g^{\alpha \beta} \right)",
    ]
    return templates
```

A few things worth noting.

Some templates are parameterized. The line bundle cohomology template uses a randomly chosen `n` between 1 and 3, all of which produce zero (this is a known result about projective space). The randomization adds variety within a single template without breaking its mathematical validity.

The Bessel-function template uses Python f-string syntax with escaped braces (`{{n}}` for a literal `{n}` in LaTeX, with the inner `{n}` being a Python format substitution). This is fiddly but necessary because LaTeX uses `{}` for grouping and Python f-strings use `{}` for substitution.

The verification step happens at log time. Every expression is paired with its expected digit value, and the log writes a table mapping `[index] expected=N latex=...` for every position in the number. If a template is ever inserted in the wrong digit's pool, the log surfaces the mismatch immediately.

{{< /accordionItem >}}

{{< accordionItem title="International phone number formatting via UN M49" >}}

The country data is structured around the UN M49 geoscheme, which is the same hierarchical classification the United Nations uses for its statistics. Continents contain subregions, which contain countries, with each country carrying its own digit-count rules and formatting template.

A simplified view of the structure for one country looks like this:

```python
"United States": {
    "code": "+1",
    "digits": 10,
    "format": "+1 ({d3}) {d3}-{d4}",
    "special_prefixes": {
        "Toll-free": ["800", "833", "844", "855", "866", "877", "888"],
        "Premium": ["900"],
    },
}
```

The `format` string uses placeholders that the formatter fills as the user types. A US number gets parenthesis-and-hyphen formatting; a French number gets space-separated pairs; a Brazilian number gets the area-code-then-hyphen treatment its locals expect.

The special prefixes dropdown is populated dynamically. Selecting United States and then choosing Toll-free pre-fills `800` (or 833, 844, etc., one of the eight US toll-free prefixes), leaving the user to type the remaining seven digits.

Smart-paste handling is the last piece. A user pastes `+1 (786) 212-6394` or `786.212.6394` or any other format; the input is stripped to digits, the country is inferred from the leading digits when possible, and the formatted display matches the country's convention regardless of how the source was formatted. This is one of those features that takes longer to write than to describe, but the alternative (forcing the user to manually clean up before typing) would have been a constant friction point.

{{< /accordionItem >}}

{{< accordionItem title="Subprocess-driven LaTeX with auto-crop" >}}

The rendering pipeline composes two external tools, both run as subprocesses, both capturing their output for diagnostic logging:

```python
with tempfile.TemporaryDirectory() as temp_dir:
    tex_path = Path(temp_dir) / "doc.tex"
    tex_path.write_text(latex_source, encoding="utf-8")

    # Compile to PDF
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode",
         "-output-directory", temp_dir, str(tex_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logger.error("pdflatex failed:\n%s", result.stdout)
        raise RuntimeError("LaTeX compilation failed")

    pdf_path = Path(temp_dir) / "doc.pdf"

    # Convert to PNG at high DPI
    subprocess.run(
        ["pdftoppm", "-r", str(DEFAULT_DPI),
         "-png", str(pdf_path), str(output_path.with_suffix(""))],
        check=True,
    )
```

The temp directory is created with `tempfile.TemporaryDirectory()`, which means the directory is automatically deleted when the `with` block exits regardless of whether the rendering succeeded. Failed runs leave nothing on disk; successful runs have already copied the final PNG to a separate location.

The auto-crop comes for free from the `standalone` LaTeX document class. Standalone documents size themselves to their content with a configurable border, so the resulting PDF has no excess whitespace and the PNG produced from it is exactly the size of the math expression itself. Without standalone, the output would be a full-page PDF with an equation in the middle, requiring a separate cropping step.

The error-handling philosophy here is that the user should never see a cryptic LaTeX error. The detailed error from pdflatex goes to the log; the user sees a friendly "LaTeX rendering failed, check the log for details" message in the GUI. The log is rich enough that diagnosing a failure is straightforward when one happens.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.10+
- **GUI:** tkinter (built into Python)
- **Image handling:** [Pillow](https://pillow.readthedocs.io/) (preview popout)
- **LaTeX rendering:** TeX Live or MacTeX, via `pdflatex` and `pdftoppm` subprocesses

## Repo

[github.com/hihipy/dialogorithm](https://github.com/hihipy/dialogorithm)
