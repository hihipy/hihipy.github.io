#!/usr/bin/env python3
"""Re-splice regenerated chart blocks into the phase files by matching headline.

After re-running tools/texas_emit_charts.R, the fresh blocks live in
texas_synth_charts.md. The phase files already contain older versions of those
same blocks (spliced earlier). This script replaces each old block in place by
matching on its headline text, so no PASTE markers are needed.

Mapping (by headline):
  03-results.md   <- proportional, absolute, black fit, white fit
  04-inference.md <- placebo

Verify-before-write: every block must be found exactly once in its target file
or the script aborts that file untouched. Leaves texas_synth_charts.md in place.
"""
from pathlib import Path
import re
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
tx = repo / "content/archivo/texas-synthetic-control"

charts_file = tx / "texas_synth_charts.md"
results_file = tx / "03-results.md"
inference_file = tx / "04-inference.md"

for f in (charts_file, results_file, inference_file):
    if not f.exists():
        sys.exit(f"ABORT: missing {f}")

charts_text = charts_file.read_text(encoding="utf-8")

# A block is <div class="pgbd-case-chart-wrap"> ... </div>
block_re = re.compile(r'<div class="pgbd-case-chart-wrap">.*?</div>', re.DOTALL)
new_blocks = block_re.findall(charts_text)

if len(new_blocks) != 5:
    sys.exit(f"ABORT: expected 5 fresh blocks in texas_synth_charts.md, found {len(new_blocks)}")

def headline_of(block):
    m = re.search(r'pgbd-case-chart-headline">(.*?)</p>', block)
    return m.group(1) if m else None

# Index fresh blocks by headline.
fresh = {}
for b in new_blocks:
    h = headline_of(b)
    if h is None:
        sys.exit("ABORT: a fresh block has no headline")
    fresh[h] = b

print("Fresh blocks found, by headline:")
for h in fresh:
    print("  -", h)

# Which headlines belong in which file.
results_headlines = [
    "Both Groups Rise, Black Men Bear the Larger Share",
    "Measured in People, the Gap Is Wider",
    "Black Male Incarceration: Texas vs Synthetic Texas",
    "White Male Incarceration: Texas vs Synthetic Texas",
]
inference_headlines = [
    "Placebo Inference: Texas Against Every Donor State",
]

for h in results_headlines + inference_headlines:
    if h not in fresh:
        sys.exit(f"ABORT: expected headline not in fresh blocks: {h!r}")

def replace_blocks(path, headlines):
    text = path.read_text(encoding="utf-8")
    # Find all existing blocks in this file.
    existing = block_re.findall(text)
    # Build a map headline -> existing block, requiring exactly one each.
    by_head = {}
    for b in existing:
        h = headline_of(b)
        by_head.setdefault(h, []).append(b)
    for h in headlines:
        hits = by_head.get(h, [])
        if len(hits) != 1:
            sys.exit(f"ABORT [{path.name}]: headline {h!r} found {len(hits)} times, expected 1")
    # Replace each old block with its fresh version.
    for h in headlines:
        old_block = by_head[h][0]
        new_block = fresh[h]
        if old_block == new_block:
            print(f"  [{path.name}] {h[:40]}... unchanged")
            continue
        count = text.count(old_block)
        if count != 1:
            sys.exit(f"ABORT [{path.name}]: old block for {h!r} matched {count} times")
        text = text.replace(old_block, new_block)
        print(f"  [{path.name}] {h[:40]}... replaced")
    path.write_text(text, encoding="utf-8")

print("\nResults file:")
replace_blocks(results_file, results_headlines)
print("Inference file:")
replace_blocks(inference_file, inference_headlines)

print("\nDone. Verify the pages render, then delete texas_synth_charts.md:")
print(f'  rm "{charts_file}"')
