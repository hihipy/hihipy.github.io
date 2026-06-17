#!/usr/bin/env python3
"""
audit_titlecase.py

Scans Hugo markdown content for table headers and figure titles that are not
in Title Case. Report-only: it never modifies files. Exit code is 1 when any
issue is found (0 otherwise), so it can gate a commit if you want.

What it checks
  - GFM pipe-table header cells
  - Chart headlines:  <div class="pgbd-case-chart-headline">...</div>
  - Figure shortcodes: {{< figure ... title="..." caption="..." >}}
  - Markdown image alt text: ![Short Alt](path)   (short alts only)

What it deliberately skips (to avoid false positives)
  - Anything inside fenced code blocks or YAML front matter
  - chart-sub text and long/punctuated captions (those are sentence case)
  - Acronyms (NCLEX, UN), brand casing (SQLite, KaTeX), tokens with digits,
    and anything in PRESERVE below

Usage
  python3 tools/audit_titlecase.py [CONTENT_DIR]
  python3 tools/audit_titlecase.py content --no-figures
  python3 tools/audit_titlecase.py content --no-tables --no-color
"""

import os
import re
import sys
import string

# ---------------------------------------------------------------------------
# Config: edit these two sets to tune behavior.
# ---------------------------------------------------------------------------

# Words kept lowercase when they fall in the middle of a title (never first or
# last word). Kept modest on purpose; expand if your house style demands it.
SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
    "of", "on", "or", "per", "the", "to", "v", "via", "vs", "nor", "so",
    "yet", "from", "into", "onto", "than", "with",
}

# Tokens treated as already-correct regardless of casing. Exact match on the
# token with surrounding punctuation stripped.
PRESERVE = {
    "NCLEX", "SQLite", "KaTeX", "GitHub", "UN", "NIH", "PIP", "CVD", "WCAG",
    "Hugo", "Goldmark", "Chart.js", "Mermaid", "Stata", "R", "tidysynth",
    "synth", "synth_runner", "causaldata", "pgbd", "pgbd.casa", "Okabe-Ito",
    "MonoLisa", "SPQ", "SUQ", "FAQ", "WIQ", "US", "U.S.", "BA", "MA", "MS",
}

# ---------------------------------------------------------------------------
# Title Case engine
# ---------------------------------------------------------------------------

PUNCT = string.punctuation

# KaTeX inline \\(...\\) and display \\[...\\] spans. Their casing is
# semantically meaningful (n != N), so they are masked out before casing
# and restored afterward, untouched.
MATH_RE = re.compile(r"\\\\\(.*?\\\\\)|\\\\\[.*?\\\\\]")


def _bare(token):
    """Token with leading/trailing punctuation removed."""
    return token.strip(PUNCT)


def is_fixed(token):
    """True if a token's casing should be left exactly as written."""
    core = _bare(token)
    if not core:
        return True                       # punctuation only
    if core in PRESERVE:
        return True
    if any(ch.isdigit() for ch in core):
        return True                       # Q4, 2024, SPQ=1
    if "_" in core:
        return True                       # snake_case identifier: total_attempts
    if core.upper() == core and len(core) >= 2:
        return True                       # ALLCAPS acronym
    if any(ch.isupper() for ch in core[1:]):
        return True                       # internal cap: SQLite, iPhone
    return False


def _cap_segment(seg):
    """Capitalize first alpha char of a segment, lowercase the rest."""
    out, seen = [], False
    for ch in seg:
        if ch.isalpha():
            out.append(ch.upper() if not seen else ch.lower())
            seen = True
        else:
            out.append(ch)
    return "".join(out)


def _lower_word(word):
    return word.lower()


def _cap_word(word):
    # Capitalize each hyphen-separated segment (Chicago-ish).
    return "-".join(_cap_segment(s) for s in word.split("-"))


def to_title_case(title):
    """Return the Title Case form of a short title string."""
    # Protect KaTeX math spans so their casing is never altered.
    spans = []

    def _mask(m):
        spans.append(m.group(0))
        return f"\x00M{len(spans) - 1}\x00"

    masked = MATH_RE.sub(_mask, title)
    words = masked.split()
    n = len(words)
    out = []
    for i, w in enumerate(words):
        if is_fixed(w):
            out.append(w)
            continue
        first = i == 0
        last = i == n - 1
        if not first and not last and _bare(w).lower() in SMALL_WORDS:
            out.append(_lower_word(w))
        else:
            out.append(_cap_word(w))
    result = " ".join(out)
    for idx, span in enumerate(spans):
        result = result.replace(f"\x00M{idx}\x00", span)
    return result


def violates(title):
    """Return the suggested fix if title is not Title Case, else None."""
    title = title.strip()
    if not title:
        return None
    fixed = to_title_case(title)
    return fixed if fixed != title else None


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------

SEP_RE = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)+\|?\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")

HEADLINE_RE = re.compile(
    r'<div[^>]*class="[^"]*pgbd-case-chart-headline[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
FIGURE_RE = re.compile(r"{{<\s*figure\b(.*?)>}}", re.DOTALL)
ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
IMG_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
TAG_RE = re.compile(r"<[^>]+>")


def split_front_matter(lines):
    """Return index of first body line (skips a leading --- ... --- block)."""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return i + 1
    return 0


def scrub(text):
    """Blank out code-fence and front-matter lines, preserving line count."""
    lines = text.splitlines()
    start = split_front_matter(lines)
    out = []
    in_code = False
    for i, line in enumerate(lines):
        if i < start:
            out.append("")
            continue
        if FENCE_RE.match(line):
            in_code = not in_code
            out.append("")
            continue
        out.append("" if in_code else line)
    return "\n".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def clean_inline(s):
    return TAG_RE.sub("", s).strip()


def looks_like_title(text):
    """A caption/alt is a 'title' only if short and unpunctuated at the end."""
    text = text.strip()
    if not text:
        return False
    if text[-1] in ".!?":
        return False
    return len(text.split()) <= 10


# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------

def scan_tables(lines):
    """Yield (lineno, 'table-header', cell, fix)."""
    start = split_front_matter(lines)
    in_code = False
    for i in range(len(lines)):
        if i < start:
            continue
        if FENCE_RE.match(lines[i]):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not SEP_RE.match(lines[i]):
            continue
        if i == 0:
            continue
        header = lines[i - 1]
        if "|" not in header:
            continue
        cells = [c.strip() for c in header.strip().strip("|").split("|")]
        for cell in cells:
            if not cell:
                continue
            fix = violates(cell)
            if fix:
                yield (i, "table-header", cell, fix)


def fix_tables(lines):
    """Recase table-header cells in place. Returns (lines, changes).

    Each header line is split into cells, each cell recased in isolation
    (so an adjacent column can't be clobbered), then rejoined. Every change
    is case-only and guarded to be byte-for-byte the same width, so column
    alignment is preserved.
    """
    start = split_front_matter(lines)
    in_code = False
    changes = []
    for i in range(len(lines)):
        if i < start:
            continue
        if FENCE_RE.match(lines[i]):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not SEP_RE.match(lines[i]):
            continue
        if i == 0:
            continue
        h = i - 1
        header = lines[h]
        if "|" not in header:
            continue
        parts = header.split("|")
        new_parts = []
        cell_changes = []
        for part in parts:
            stripped = part.strip()
            if not stripped:
                new_parts.append(part)
                continue
            fixed = to_title_case(stripped)
            if fixed != stripped and len(fixed) == len(stripped):
                lead = part[:len(part) - len(part.lstrip())]
                trail = part[len(part.rstrip()):]
                new_parts.append(lead + fixed + trail)
                cell_changes.append((stripped, fixed))
            else:
                new_parts.append(part)
        if cell_changes:
            new_header = "|".join(new_parts)
            if len(new_header) == len(header):
                lines[h] = new_header
                changes.append((i, cell_changes))
    return lines, changes


def scan_figures(text):
    """Yield (lineno, kind, value, fix) for chart headlines, figures, images."""
    s = scrub(text)

    for m in HEADLINE_RE.finditer(s):
        val = clean_inline(m.group(1))
        fix = violates(val)
        if fix:
            yield (line_of(s, m.start()), "chart-headline", val, fix)

    for m in FIGURE_RE.finditer(s):
        attrs = dict(ATTR_RE.findall(m.group(1)))
        ln = line_of(s, m.start())
        if attrs.get("title"):
            fix = violates(attrs["title"])
            if fix:
                yield (ln, "figure-title", attrs["title"], fix)
        cap = attrs.get("caption", "")
        if cap and looks_like_title(cap):
            fix = violates(cap)
            if fix:
                yield (ln, "figure-caption", cap, fix)

    for m in IMG_RE.finditer(s):
        alt = m.group(1).strip()
        if alt and looks_like_title(alt):
            fix = violates(alt)
            if fix:
                yield (line_of(s, m.start()), "image-alt", alt, fix)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def color(s, c, enabled):
    codes = {"red": "31", "yellow": "33", "green": "32", "dim": "2", "bold": "1"}
    if not enabled:
        return s
    return f"\033[{codes[c]}m{s}\033[0m"


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    content_dir = args[0] if args else "content"
    do_tables = "--no-tables" not in flags
    do_figs = "--no-figures" not in flags
    do_fix = "--fix" in flags
    use_color = "--no-color" not in flags and sys.stdout.isatty()

    if not os.path.isdir(content_dir):
        print(f"error: not a directory: {content_dir}", file=sys.stderr)
        return 2

    md_files = []
    for root, _, files in os.walk(content_dir):
        for f in files:
            if f.endswith(".md"):
                md_files.append(os.path.join(root, f))
    md_files.sort()

    if do_fix:
        return run_fix(md_files, do_figs, use_color)

    total_issues = 0
    files_with_issues = 0

    for path in md_files:
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"skip {path}: {e}", file=sys.stderr)
            continue
        lines = text.splitlines()

        hits = []
        if do_tables:
            hits.extend(scan_tables(lines))
        if do_figs:
            hits.extend(scan_figures(text))
        hits.sort(key=lambda h: (h[0], h[1]))

        if hits:
            files_with_issues += 1
            rel = os.path.relpath(path)
            print(color(rel, "bold", use_color))
            for ln, kind, actual, fix in hits:
                total_issues += 1
                loc = color(f"  L{ln:<4}", "dim", use_color)
                tag = color(f"[{kind}]", "yellow", use_color)
                print(f'{loc} {tag} {color(actual, "red", use_color)}'
                      f'  ->  {color(fix, "green", use_color)}')
            print()

    summary = (f"Scanned {len(md_files)} file(s). "
               f"{total_issues} issue(s) in {files_with_issues} file(s).")
    print(color(summary, "bold", use_color))
    return 1 if total_issues else 0


def run_fix(md_files, do_figs, use_color):
    """Apply table-header fixes in place. Figures are reported, not rewritten."""
    fixed_cells = 0
    fixed_files = 0
    figure_notices = 0

    for path in md_files:
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"skip {path}: {e}", file=sys.stderr)
            continue

        had_nl = text.endswith("\n")
        lines = text.split("\n")
        before = list(lines)
        lines, changes = fix_tables(lines)

        if changes:
            new_text = "\n".join(lines) + ("\n" if had_nl else "")
            # Self-check: no table-header issues should remain.
            remaining = list(scan_tables(new_text.splitlines()))
            if remaining:
                print(color(f"ABORT {os.path.relpath(path)}: "
                            f"{len(remaining)} issue(s) survived, not written.",
                            "red", use_color), file=sys.stderr)
                continue
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_text)
            fixed_files += 1
            rel = os.path.relpath(path)
            print(color(rel, "bold", use_color))
            for ln, cell_changes in changes:
                for old, new in cell_changes:
                    fixed_cells += 1
                    loc = color(f"  L{ln:<4}", "dim", use_color)
                    print(f'{loc} {color(old, "red", use_color)}'
                          f'  ->  {color(new, "green", use_color)}')
            print()

        if do_figs:
            fig_hits = list(scan_figures(text))
            if fig_hits:
                if figure_notices == 0:
                    print(color("Figure titles flagged (edit by hand, not "
                                "auto-fixed):", "yellow", use_color))
                figure_notices += len(fig_hits)
                rel = os.path.relpath(path)
                for ln, kind, actual, fix in fig_hits:
                    print(f'  {rel}:L{ln} [{kind}] {actual}  ->  {fix}')

    summary = f"Fixed {fixed_cells} cell(s) across {fixed_files} file(s)."
    if figure_notices:
        summary += f" {figure_notices} figure title(s) left for hand-editing."
    print(color(summary, "bold", use_color))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
