#!/usr/bin/env python3
"""Patch tools/texas_emit_charts.R: clean rounded axis bounds + bottom legend.

Two edits, each verify-before-write (anchor must match exactly once):
  1. Replace pad_range so axis min/max round outward to clean steps.
  2. Move the legend from top to bottom so 3 entries don't crowd.
"""
from pathlib import Path
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
emitter = repo / "tools/texas_emit_charts.R"

if not emitter.exists():
    sys.exit(f"ABORT: {emitter} not found")

text = emitter.read_text(encoding="utf-8")

# --- Edit 1: pad_range -------------------------------------------------------

old_pad = """pad_range <- function(v, frac = 0.06) {
  v <- v[is.finite(v)]
  lo <- min(v)
  hi <- max(v)
  span <- hi - lo
  if (span == 0) span <- abs(hi) + 1
  c(lo - span * frac, hi + span * frac)
}"""

new_pad = """pad_range <- function(v, frac = 0.06) {
  v <- v[is.finite(v)]
  lo <- min(v)
  hi <- max(v)
  span <- hi - lo
  if (span == 0) span <- abs(hi) + 1
  lo_pad <- lo - span * frac
  hi_pad <- hi + span * frac
  # round bounds outward to a clean step scaled to the data magnitude,
  # so axes land on round numbers instead of arbitrary decimals
  step <- 10^floor(log10(span))
  if (span / step < 2) {
    step <- step / 5
  } else if (span / step < 5) {
    step <- step / 2
  }
  c(floor(lo_pad / step) * step, ceiling(hi_pad / step) * step)
}"""

n = text.count(old_pad)
if n != 1:
    sys.exit(f"ABORT [pad_range]: anchor matched {n} times, expected 1. No changes written.")
text = text.replace(old_pad, new_pad)
print("patched pad_range (clean rounded bounds)")

# --- Edit 2: legend position -------------------------------------------------

old_leg = '        legend = list(display = legend_display, position = "top"),'
new_leg = '        legend = list(display = legend_display, position = "bottom"),'

n = text.count(old_leg)
if n != 1:
    sys.exit(f"ABORT [legend]: anchor matched {n} times, expected 1. No changes written.")
text = text.replace(old_leg, new_leg)
print("patched legend (top -> bottom)")

emitter.write_text(text, encoding="utf-8")
print("\nEmitter patched. Next: re-run it in Positron, then run resplice_by_headline.py.")
