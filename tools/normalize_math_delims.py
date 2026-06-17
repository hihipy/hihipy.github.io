#!/usr/bin/env python3
r"""Normalize math delimiters from double-backslash to single in the phase files.

With Goldmark passthrough enabled (see patch_markup_passthrough.py), math is
protected from emphasis parsing, so the double-backslash BUG-029 workaround is
no longer needed and in fact must be removed: passthrough and KaTeX both match
SINGLE backslash \[ \] \( \).

Converts on disk:
  \\[  -> \[      \\]  -> \]
  \\(  -> \(      \\)  -> \)

Only these four exact two-char sequences are touched. Other backslashes in the
math (\hat, \sum, \tau, etc.) are single already and are left alone.

Runs across all four phase files. Verify-before/after counts printed.
"""
from pathlib import Path
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
tx = repo / "content/archivo/texas-synthetic-control"

files = ["01-question.md", "02-method.md", "03-results.md", "04-inference.md"]

# Map of double-backslash delimiter -> single. Order matters: do the 2-backslash
# forms only. These are literal strings as they appear on disk.
repls = [
    ("\\\\[", "\\["),
    ("\\\\]", "\\]"),
    ("\\\\(", "\\("),
    ("\\\\)", "\\)"),
]

total = 0
for name in files:
    p = tx / name
    if not p.exists():
        print(f"skip (missing): {name}")
        continue
    text = p.read_text(encoding="utf-8")
    before = sum(text.count(a) for a, _ in repls)
    for a, b in repls:
        text = text.replace(a, b)
    after = sum(text.count(a) for a, _ in repls)
    p.write_text(text, encoding="utf-8")
    converted = before - after
    total += converted
    print(f"{name}: converted {converted} double-backslash delimiters (residual {after})")

print(f"\nTotal converted: {total}")
print("Now: rebuild clean (rm -rf public resources/_gen) and hard-refresh.")
