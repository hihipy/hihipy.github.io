#!/usr/bin/env python3
"""Remove references to the private build script from the published phases.

The chart emitter is a local-machine tool, not a published artifact, so the
three GitHub links to tools/texas_emit_charts.R are removed and the surrounding
prose reworded to keep the reproducibility point without naming or linking the
file. Verify-before-write: each anchor must match exactly once.
"""
from pathlib import Path
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
tx = repo / "content/archivo/texas-synthetic-control"

edits = [
    (
        tx / "02-method.md",
        "The build is in R using tidysynth. The script that performs the fit and emits the figures lives at [`tools/texas_emit_charts.R`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/texas_emit_charts.R) on GitHub; it refuses to run if any predictor cell in the window is missing, so the completeness guarantees above are enforced in code rather than assumed.",
        "The build is in R using tidysynth, with a hard guard that refuses to run if any predictor cell in the window is missing, so the completeness guarantees above are enforced in code rather than assumed.",
    ),
    (
        tx / "04-inference.md",
        "The full fit, including the predictor set, the donor pool, and the figure generation, is reproducible from [`tools/texas_emit_charts.R`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/texas_emit_charts.R). Every number in this case study comes from that script's output against the `texas` panel; anyone running it gets the same estimates, or the case study fails its own reproducibility standard.",
        "The full fit, including the predictor set, the donor pool, and the figure generation, is reproducible: every number in this case study comes from fitting the documented specification against the `texas` panel, and anyone fitting the same specification gets the same estimates, or the case study fails its own reproducibility standard.",
    ),
    (
        tx / "04-inference.md",
        "The fit uses the [`tidysynth`](https://cran.r-project.org/package=tidysynth) package (Dunford), a tidyverse-style interface to the synthetic control estimator. The full fitting and figure-generation script is at [`tools/texas_emit_charts.R`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/texas_emit_charts.R).",
        "The fit uses the [`tidysynth`](https://cran.r-project.org/package=tidysynth) package (Dunford), a tidyverse-style interface to the synthetic control estimator.",
    ),
]

# Group by file so multiple edits to the same file are applied together.
from collections import defaultdict
by_file = defaultdict(list)
for path, old, new in edits:
    by_file[path].append((old, new))

for path, pairs in by_file.items():
    if not path.exists():
        sys.exit(f"ABORT: {path} not found")
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            sys.exit(f"ABORT [{path.name}]: an anchor matched {n} times, expected 1. No changes written to this file.")
    for old, new in pairs:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: removed {len(pairs)} script reference(s)")

# Final check: no references to the script remain in any phase.
remaining = 0
for f in ("01-question.md", "02-method.md", "03-results.md", "04-inference.md"):
    p = tx / f
    if p.exists() and "texas_emit_charts" in p.read_text(encoding="utf-8"):
        print(f"WARNING: {f} still mentions texas_emit_charts")
        remaining += 1
if remaining == 0:
    print("\nClean: no references to texas_emit_charts remain in any phase.")
