#!/usr/bin/env python3
"""Splice the five emitted chart blocks into the phase-file paste markers.

Reads texas_synth_charts.md, extracts the five pgbd-case-chart-wrap blocks in
order, and replaces the <!-- PASTE CHART BLOCK N --> markers:
  blocks 1-4 -> 03-results.md
  block 5    -> 04-inference.md

Verifies every count before writing. Leaves texas_synth_charts.md in place so
the result can be checked before deleting it.
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
        sys.exit(f"ERROR: missing {f}")

charts_text = charts_file.read_text(encoding="utf-8")

# Extract each <div class="pgbd-case-chart-wrap"> ... </div> block.
# The blocks are separated by blank lines; match from the opening div to its
# closing </div> at the end of a block (the wrap div is the outermost).
pattern = re.compile(
    r'<div class="pgbd-case-chart-wrap">.*?</div>',
    re.DOTALL,
)
blocks = pattern.findall(charts_text)

print(f"Found {len(blocks)} chart blocks in texas_synth_charts.md")
if len(blocks) != 5:
    print("Headlines found:")
    for h in re.findall(r'pgbd-case-chart-headline">(.*?)</p>', charts_text):
        print("  -", h)
    sys.exit(f"ERROR: expected 5 blocks, found {len(blocks)}. Aborting, no files changed.")

# Show which block is which so the ordering is auditable.
print("\nBlock order (by headline):")
for i, b in enumerate(blocks, 1):
    m = re.search(r'pgbd-case-chart-headline">(.*?)</p>', b)
    print(f"  block {i}: {m.group(1) if m else '(no headline)'}")

results_text = results_file.read_text(encoding="utf-8")
inference_text = inference_file.read_text(encoding="utf-8")

# Confirm marker counts before any write.
res_markers = re.findall(r'<!-- PASTE CHART BLOCK (\d) [^>]*-->', results_text)
inf_markers = re.findall(r'<!-- PASTE CHART BLOCK (\d) [^>]*-->', inference_text)
print(f"\nMarkers in 03-results.md: {res_markers}")
print(f"Markers in 04-inference.md: {inf_markers}")

expected_res = ["1", "2", "3", "4"]
expected_inf = ["5"]
if res_markers != expected_res:
    sys.exit(f"ERROR: 03-results.md markers {res_markers} != expected {expected_res}. Aborting.")
if inf_markers != expected_inf:
    sys.exit(f"ERROR: 04-inference.md markers {inf_markers} != expected {expected_inf}. Aborting.")

# Replace each marker with its block. Marker line may have trailing text; match the whole line.
def replace_marker(text, n, block):
    marker_re = re.compile(r'<!-- PASTE CHART BLOCK ' + str(n) + r' [^>]*-->')
    new_text, count = marker_re.subn(lambda _: block, text)
    if count != 1:
        sys.exit(f"ERROR: marker {n} matched {count} times, expected 1. Aborting.")
    return new_text

for n in (1, 2, 3, 4):
    results_text = replace_marker(results_text, n, blocks[n - 1])
inference_text = replace_marker(inference_text, 5, blocks[4])

# Final guard: no markers should remain.
if "PASTE CHART BLOCK" in results_text or "PASTE CHART BLOCK" in inference_text:
    sys.exit("ERROR: a paste marker survived the splice. Aborting without writing.")

results_file.write_text(results_text, encoding="utf-8")
inference_file.write_text(inference_text, encoding="utf-8")

print("\nSpliced:")
print(f"  blocks 1-4 -> {results_file.name}")
print(f"  block 5    -> {inference_file.name}")
print("\ntexas_synth_charts.md left in place. Verify the pages render, then delete it:")
print(f'  rm "{charts_file}"')
