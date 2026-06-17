#!/usr/bin/env python3
r"""Fix broken KaTeX display delimiters in 03-results.md.

The four display-math formulas in the 'Estimator in Symbols' section were
written with single-backslash delimiters \[ ... \] which Goldmark strips, so
KaTeX never renders them. The working method-phase formulas use double-backslash
\\[ ... \\]. This converts the four broken lines to match.

Targets only lines that START with the display-open delimiter, so inline math
and prose are untouched. Verify-before-write.
"""
from pathlib import Path
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
target = repo / "content/archivo/texas-synthetic-control/03-results.md"

if not target.exists():
    sys.exit(f"ABORT: {target} not found")

lines = target.read_text(encoding="utf-8").splitlines(keepends=True)

# A broken display line starts with exactly one backslash + [ and ends with
# one backslash + ] (before the newline). The working form is two backslashes.
fixed = 0
out = []
for ln in lines:
    stripped = ln.rstrip("\n")
    # single-backslash open: starts with \[ but NOT \\[
    is_open = stripped.startswith("\\[") and not stripped.startswith("\\\\[")
    is_close = stripped.endswith("\\]") and not stripped.endswith("\\\\]")
    if is_open and is_close:
        new = "\\" + stripped[:-2] + "\\\\]"   # double the leading, fix trailing
        # simpler: rebuild explicitly
        body = stripped[2:-2]  # content between \[ and \]
        new_line = "\\\\[" + body + "\\\\]"
        nl = "\n" if ln.endswith("\n") else ""
        out.append(new_line + nl)
        fixed += 1
    else:
        out.append(ln)

if fixed == 0:
    sys.exit("No single-backslash display lines found. Either already fixed or pattern changed; nothing written.")

print(f"Found and fixed {fixed} display-math lines (expected 4).")
if fixed != 4:
    print("WARNING: expected 4. Inspect the file before trusting this.")

target.write_text("".join(out), encoding="utf-8")
print("Written. Verify each formula renders, then the results page is done.")
