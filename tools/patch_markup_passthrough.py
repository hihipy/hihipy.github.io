#!/usr/bin/env python3
r"""Enable Goldmark passthrough for SINGLE-backslash math delimiters.

Adds [goldmark.extensions.passthrough] matching \[...\] (block) and \(...\)
(inline). With passthrough on, Goldmark leaves math verbatim (no underscore
to emphasis), and KaTeX's DEFAULT delimiters (\[ and \() match directly, so
no theme JS override is needed. Pairs with normalize_math_delims.py which
converts the formulas from \\[ to \[.

Verify-before-write.
"""
from pathlib import Path
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
target = repo / "config/_default/markup.toml"

if not target.exists():
    sys.exit(f"ABORT: {target} not found")

text = target.read_text(encoding="utf-8")

if "passthrough" in text:
    sys.exit("passthrough already configured; nothing changed.")

anchor = """[goldmark]
  [goldmark.renderer]
    unsafe = true   # allows raw HTML in markdown (needed for some shortcodes)"""

if text.count(anchor) != 1:
    sys.exit("ABORT: [goldmark] anchor not found exactly once; inspect markup.toml.")

# Single-quoted TOML literals; one backslash each to match \[ \] \( \) on disk.
block = (
    anchor
    + "\n\n"
    + "  # Pass math through verbatim so underscores inside formulas are not\n"
    + "  # parsed as emphasis (retires BUG-029). Math uses SINGLE-backslash\n"
    + "  # delimiters: \\[ ... \\] and \\( ... \\), which KaTeX matches by default.\n"
    + "  [goldmark.extensions.passthrough]\n"
    + "    enable = true\n"
    + "    [goldmark.extensions.passthrough.delimiters]\n"
    + "      block = [['\\[', '\\]'], ['$$', '$$']]\n"
    + "      inline = [['\\(', '\\)']]"
)

text = text.replace(anchor, block)
target.write_text(text, encoding="utf-8")
print("markup.toml patched: passthrough enabled for single-backslash math.")
