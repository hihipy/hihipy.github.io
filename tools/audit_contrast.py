#!/usr/bin/env python3
"""
Audits color contrast for /taller/ in both light and dark mode.

Single source of truth: parses the dark-mode swap map directly out of the
inline <script> tag in content/taller/_index.md, so future swap-map changes
auto-propagate. No hardcoded color lists.

Run from repo root:
    python3 audit_contrast.py
"""
import re
import sys
from collections import OrderedDict
from pathlib import Path

LIGHT_BG = "#FFFFFF"
DARK_BG = "#0D1117"


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    l1 = relative_luminance(hex_to_rgb(fg))
    l2 = relative_luminance(hex_to_rgb(bg))
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def grade(ratio):
    if ratio >= 7.0:
        return "AAA-text"
    if ratio >= 4.5:
        return "AA-text"
    if ratio >= 3.0:
        return "AA-large/non-text"
    return "FAIL"


def visible(g):
    if "AAA" in g:
        return f"\033[92m{g}\033[0m"
    if "AA-text" in g:
        return f"\033[32m{g}\033[0m"
    if "AA-large" in g:
        return f"\033[33m{g}\033[0m"
    if "FAIL" in g:
        return f"\033[91m{g}\033[0m"
    return g


def parse_swap_map(text):
    """Extract the lightToDark color swap map from the inline theme adapter."""
    block = re.search(
        r"var\s+lightToDark\s*=\s*\{(.*?)\};",
        text,
        flags=re.DOTALL,
    )
    if not block:
        print("warning: could not find lightToDark map; assuming no theme swap",
              file=sys.stderr)
        return {}
    body = block.group(1)
    swaps = {}
    for m in re.finditer(
        r"'(#[0-9A-Fa-f]{3,8})'\s*:\s*'(#[0-9A-Fa-f]{3,8})'",
        body,
    ):
        swaps[m.group(1).upper()] = m.group(2).upper()
    return swaps


def extract_hex_colors(text):
    """Pull every hex color used as a chart series color, with usage context."""
    found = OrderedDict()
    for m in re.finditer(
        r"(borderColor|backgroundColor|pointBackgroundColor|pointBorderColor)\s*:\s*'(#[0-9A-Fa-f]{3,6})'",
        text,
    ):
        prop, color = m.group(1), m.group(2).upper()
        if color not in found:
            found[color] = []
        before = text[max(0, m.start() - 400):m.start()]
        lbl = re.search(r"label:\s*'([^']+)'", before[::-1])
        if lbl:
            found[color].append(f"{prop} on {lbl.group(1)[::-1]}")
        else:
            found[color].append(prop)
    return found


def print_report(title, fgs, bg, swaps=None):
    print(f"\n{'='*78}")
    print(f"  {title}")
    print(f"  Background: {bg}")
    print(f"{'='*78}")
    print(f"  {'COLOR':<10} {'RATIO':<10} {'GRADE':<28} USAGE")
    print(f"  {'-'*10} {'-'*10} {'-'*28} {'-'*30}")
    rows = []
    for c, u in fgs.items():
        actual = swaps.get(c, c) if swaps else c
        r = contrast_ratio(actual, bg)
        rows.append((actual, r, grade(r),
                     "; ".join(u[:2]) + ("..." if len(u) > 2 else "")))
    rows.sort(key=lambda x: -x[1])
    for color, ratio, g, usage in rows:
        print(f"  {color:<10} {ratio:>5.2f}:1   {visible(g):<37} {usage}")


def main():
    p = Path("content/taller/_index.md")
    if not p.is_file():
        print(f"error: {p} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    text = p.read_text()
    fgs = extract_hex_colors(text)
    swaps = parse_swap_map(text)

    print(f"\nParsed {len(swaps)} swap-map entries from inline theme adapter:")
    for k, v in swaps.items():
        print(f"  {k} -> {v}")

    print_report("LIGHT MODE — chart series colors against #FFFFFF",
                 fgs, LIGHT_BG)
    print_report(
        "DARK MODE — chart series colors against #0D1117 (after theme swap)",
        fgs, DARK_BG, swaps=swaps,
    )

    print(f"\n{'='*78}")
    print("  WCAG REFERENCE")
    print(f"{'='*78}")
    print("  AAA-text:           7.0:1 or higher")
    print("  AA-text:            4.5:1 to 6.99:1")
    print("  AA-large/non-text:  3.0:1 to 4.49:1 (mirador's chart-element floor)")
    print("  FAIL:               below 3.0:1")
    print()


if __name__ == "__main__":
    main()
