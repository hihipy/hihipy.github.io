#!/usr/bin/env python3
"""Append the Sources section to 04-inference.md. Idempotent: refuses if already present."""
from pathlib import Path
import sys

repo = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io"
target = repo / "content/archivo/texas-synthetic-control/04-inference.md"

if not target.exists():
    sys.exit(f"ERROR: {target} not found")

text = target.read_text(encoding="utf-8")

if "## Sources" in text:
    sys.exit("Sources section already present; nothing appended.")

sources = """

## Sources

The method originates with Abadie, Diamond, and Hainmueller (2010), "Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program," *Journal of the American Statistical Association* 105 (490): 493 to 505. The estimator and its placebo-permutation inference both follow that paper.

The Texas prison-capacity data is the `texas` panel from Scott Cunningham's *Causal Inference: The Mixtape* (Yale University Press, 2021), available online at [mixtape.scunning.com](https://mixtape.scunning.com/). The dataset is distributed in R through the [`causaldata`](https://cran.r-project.org/package=causaldata) package, which is how this analysis loads it.

The fit uses the [`tidysynth`](https://cran.r-project.org/package=tidysynth) package (Dunford), a tidyverse-style interface to the synthetic control estimator. The full fitting and figure-generation script is at [`tools/texas_emit_charts.R`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/texas_emit_charts.R).
"""

# Ensure file ends with a single newline before appending, then append.
text = text.rstrip("\n") + "\n" + sources
target.write_text(text, encoding="utf-8")
print(f"Appended Sources section to {target.name}")
print("Verify with: tail -20 the file, then refresh the Inference page.")
