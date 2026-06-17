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
    # Dataset field codes: identifiers wherever they appear (incl. inside a
    # phrase like "ugds (enrollment)"), so they stay at the token level.
    "ugds", "aanapii", "annhi", "hbcu", "hsi", "pbi", "tribal",
}

# Whole-cell identifiers: table names, SQL types, and type labels. Preserved
# ONLY when they are the entire cell (a type/name column), so the same word in
# prose ("descriptive alt text") still title-cases. Matched case-insensitively.
CELL_PRESERVE = {
    "institutions", "attempts", "students", "int", "text",
    "currency", "datetime", "boolean", "numeric", "categorical",
}

# ---------------------------------------------------------------------------
# Title Case engine
# ---------------------------------------------------------------------------

PUNCT = string.punctuation

# KaTeX inline \\(...\\) and display \\[...\\] spans. Their casing is
# semantically meaningful (n != N), so they are masked out before casing
# and restored afterward, untouched. Inline code `...` spans are masked too:
# code is never prose, so it must not be recased.
MATH_RE = re.compile(r"\\\\\(.*?\\\\\)|\\\\\[.*?\\\\\]")
CODE_RE = re.compile(r"`[^`]*`")
PROTECT_RE = re.compile(MATH_RE.pattern + r"|" + CODE_RE.pattern)


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
    if "/" in core:
        return True                       # n/a, km/h, and/or: don't mangle
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
    """Return the Title Case form of a title, preserving internal whitespace.

    Math and inline-code spans are masked out so their contents are never
    recased. Whitespace between words is preserved exactly, so the result is
    a pure case-only transform (same character width).
    """
    spans = []

    def _mask(m):
        spans.append(m.group(0))
        return f"\x00M{len(spans) - 1}\x00"

    masked = PROTECT_RE.sub(_mask, title)
    # Split keeping whitespace runs so spacing is preserved on rejoin.
    parts = re.split(r"(\s+)", masked)
    word_pos = [i for i, p in enumerate(parts) if p and not p.isspace()]
    n = len(word_pos)
    for k, i in enumerate(word_pos):
        w = parts[i]
        if is_fixed(w):
            continue
        first = k == 0
        last = k == n - 1
        if not first and not last and _bare(w).lower() in SMALL_WORDS:
            parts[i] = _lower_word(w)
        else:
            parts[i] = _cap_word(w)
    result = "".join(parts)
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

def always(_cell):
    return True


def table_rows(lines, sep_idx):
    """Given a separator-line index, return (header_idx, [body_idx, ...]).

    Body rows run from just after the separator until the first blank line,
    code fence, or line without a pipe (GFM table termination).
    """
    header_idx = sep_idx - 1
    body = []
    j = sep_idx + 1
    while j < len(lines):
        line = lines[j]
        if FENCE_RE.match(line) or line.strip() == "" or "|" not in line:
            break
        body.append(j)
        j += 1
    return header_idx, body


def scan_row(line, gate):
    """Return [(cell, fix), ...] for cells that fail Title Case and pass gate."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    out = []
    for cell in cells:
        if not cell or not gate(cell):
            continue
        if cell.lower() in CELL_PRESERVE:
            continue
        fix = violates(cell)
        if fix:
            out.append((cell, fix))
    return out


def recase_row(line, gate):
    """Return (new_line, [(old, new), ...]). Each cell recased in isolation
    so neighbors can't be clobbered; every change is guarded to keep the row
    byte-for-byte the same width, so column alignment is preserved."""
    parts = line.split("|")
    new_parts = []
    changes = []
    for part in parts:
        stripped = part.strip()
        if not stripped or not gate(stripped) or stripped.lower() in CELL_PRESERVE:
            new_parts.append(part)
            continue
        fixed = to_title_case(stripped)
        if fixed != stripped and len(fixed) == len(stripped):
            lead = part[:len(part) - len(part.lstrip())]
            trail = part[len(part.rstrip()):]
            new_parts.append(lead + fixed + trail)
            changes.append((stripped, fixed))
        else:
            new_parts.append(part)
    new_line = "|".join(new_parts)
    if changes and len(new_line) == len(line):
        return new_line, changes
    return line, []


def scan_tables(lines):
    """Yield (lineno, kind, cell, fix) for header cells and body cells.

    Header cells are checked unconditionally. Body cells are gated by
    looks_like_title so prose cells (sentences, long text) stay sentence case.
    """
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
        if not SEP_RE.match(lines[i]) or i == 0:
            continue
        header_idx, body = table_rows(lines, i)
        if "|" not in lines[header_idx]:
            continue
        for cell, fix in scan_row(lines[header_idx], always):
            yield (header_idx + 1, "table-header", cell, fix)
        for j in body:
            for cell, fix in scan_row(lines[j], looks_like_title):
                yield (j + 1, "table-cell", cell, fix)


def fix_tables(lines):
    """Recase table header and body cells in place. Returns (lines, changes).

    Headers recase unconditionally; body cells are gated by looks_like_title
    so prose stays sentence case. All changes are case-only and width-guarded.
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
        if not SEP_RE.match(lines[i]) or i == 0:
            continue
        header_idx, body = table_rows(lines, i)
        if "|" not in lines[header_idx]:
            continue
        new_h, ch = recase_row(lines[header_idx], always)
        if ch:
            lines[header_idx] = new_h
            changes.append((header_idx + 1, ch))
        for j in body:
            new_b, cb = recase_row(lines[j], looks_like_title)
            if cb:
                lines[j] = new_b
                changes.append((j + 1, cb))
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

        lines = text.split("\n")
        lines, changes = fix_tables(lines)

        if changes:
            new_text = "\n".join(lines)  # split/join round-trips newlines exactly
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
            # Any cell that still violates couldn't be fixed without changing
            # width (e.g. a Unicode case-mapping length change). Report it.
            remaining = list(scan_tables(new_text.splitlines()))
            for ln, kind, actual, fix in remaining:
                print(color(f"  L{ln:<4} (manual) {actual}  ->  {fix}",
                            "yellow", use_color))
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
