#!/usr/bin/env python3
"""Write the five Texas synthetic-control case study files into the repo folder."""
from pathlib import Path

dest = Path.home() / "Library/CloudStorage/ProtonDrive-philgbd@pm.me-folder/Code/coding-workspace/hihipy.github.io/content/archivo/texas-synthetic-control"
dest.mkdir(parents=True, exist_ok=True)

files = {}

files["_index.md"] = r"""---
title: "Texas Prison Expansion"
weight: 10
description: "A synthetic control case study on the 1993 Texas prison-capacity expansion and what it did to incarceration, estimated separately for Black and white men. Cunningham's Mixtape data fit in R with tidysynth, walked through phase by phase so every identification decision is auditable."
summary: "A natural experiment and an unequal burden"
tags: ["causal-inference", "econometrics", "predictive-modeling", "r", "synthetic-control"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A synthetic control case study on the 1993 Texas prison-capacity expansion, walked through phase by phase.
{{< /lead >}}

## At a Glance

In 1993 Texas began roughly doubling its operational prison capacity, a buildout that ran through 1995 and stands as one of the largest state-level carceral expansions in modern American history. This case study treats that buildout as a natural experiment and asks a counterfactual question: how much higher did male incarceration in Texas climb than it would have without the expansion? The estimator is synthetic control, a method built precisely for a single treated unit observed against many untreated ones. The data is the `texas` panel from Scott Cunningham's [Causal Inference: The Mixtape](https://mixtape.scunning.com/), fit in R with [tidysynth](https://github.com/edunford/tidysynth).

The analysis runs two outcomes side by side, Black male and white male incarceration, because the comparison is the finding. A capacity expansion is facially race-neutral: it builds cells, not sentences. Yet the estimated effect is not race-neutral. Both groups' incarceration rose sharply after 1993, but the Black male increase ran consistently larger in proportional terms and far larger in absolute numbers. The full reasoning, including why Texas, why 1993, and why this method, lives across the four phases.

## The Phases
"""

files["01-question.md"] = r"""---
title: "Question"
weight: 10
description: "The natural experiment. Why the 1993 Texas prison-capacity expansion works as a treatment, why incarceration by race is the outcome worth measuring, and the framing the data ended up supporting: unequal burden, not a clean racial divide."
summary: "The natural experiment and the question it answers"
tags: ["causal-inference", "econometrics", "public-data", "synthetic-control"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
A policy that builds prison cells does not name a race. The question is whether its effects respected that neutrality.
{{< /lead >}}

## At a Glance

In 1993 Texas began one of the largest prison-construction efforts any American state has undertaken. Over roughly three years the state added enough capacity to nearly double the number of people its system could hold. The buildout was a supply decision, not a sentencing one: it expanded the number of available cells without, on its face, changing who got sent to them or for how long.

That supply-side character is what makes it useful here. A sudden, large, externally driven change in one state, with no parallel change in the rest of the country, is the shape a natural experiment takes. If incarceration in Texas departed from its prior trajectory after 1993 while comparable states did not, the expansion is the most plausible cause of the departure. This phase lays out why the expansion qualifies as a treatment, what outcome is worth measuring against it, and how the framing of the case study shifted once the estimates were in hand.

## Why This Is a Natural Experiment

A clean natural experiment needs three things: a treatment that arrives at a known time, a treated unit that can be compared against untreated ones, and a reason to believe the treatment was not itself caused by the outcome it is supposed to affect. The Texas expansion has all three.

The timing is sharp. Construction and the capacity it unlocked are dated to 1993 through 1995, which gives a clear before and after rather than a gradual drift that would be hard to pin to any single year. The treated unit is one state observed against the other forty-nine, the standard setup for the method this case study uses. And the direction of causation is defensible: a state builds cells in anticipation of needing them, but the buildout is a capital and political undertaking on a scale that does not turn on a single year's incarceration figure. The expansion plausibly raised incarceration; incarceration in any one year did not summon a billion-dollar construction program into being.

What the expansion is not is a randomized trial. No one assigned Texas to treatment and Nebraska to control. The whole burden of the analysis is therefore on constructing a credible comparison: a version of Texas that did not expand, built from states that did not. That construction is the work of [the method phase](/archivo/texas-synthetic-control/02-method/).

## The Outcome Worth Measuring

The natural outcome is incarceration, but incarceration measured how, and for whom. This case study measures the number of men in prison, estimated separately for Black and white men, using the prisoner counts in the `texas` panel.

The choice to split by race is the analytical center of the piece, and it is worth being explicit about why. A capacity expansion does not write race into law. It funds concrete and staffing. If the effect of more cells were genuinely neutral, the increase in incarceration it produced would fall on groups in rough proportion to their existing share of the prison population. If instead the effect landed unevenly, that unevenness is not in the text of the policy; it is in how a race-neutral supply increase interacts with the rest of the system that decides who fills the cells.

So the question the outcome is built to answer is not simply "did incarceration rise" but "did it rise evenly." That is a question a single combined count cannot answer and two race-specific counts can.

## The Framing the Data Supported

The case study began with a sharper hypothesis than the data ended up supporting, and the gap between the two is worth recording rather than hiding.

The initial expectation was a clean racial divide: that the expansion would drive Black male incarceration sharply upward while leaving white male incarceration close to its counterfactual. The estimates did not show that. Both series rose substantially after 1993. The white male increase was real, large, and statistically distinguishable from chance, not the near-null the original framing assumed.

What the data did show is an unequal burden. Both groups' incarceration climbed well above what the synthetic control predicted, but the Black male climb ran about a fifth larger in proportional terms and roughly half again as large in absolute numbers by the end of the window. The honest finding is therefore not that the policy affected one group and spared the other, but that a race-neutral expansion produced a large increase for both groups and a heavier one for Black men. That is a more careful claim than the original, and it is the one [the results phase](/archivo/texas-synthetic-control/03-results/) defends with the actual estimates.
"""

files["02-method.md"] = r"""---
title: "Method"
weight: 20
description: "What synthetic control does and why it fits a single-state treatment, the donor pool of comparison states, the predictor set, and the data-driven decisions that shaped the fit: the analysis window, the two dropped donors, and a specification selected by what the optimizer could actually solve."
summary: "Synthetic control, the donor pool, and the decisions the data forced"
tags: ["causal-inference", "econometrics", "predictive-modeling", "r", "synthetic-control"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}
{{< lead >}}
There is no untreated Texas to compare against, so the method builds one out of the states that were not treated.
{{< /lead >}}

## At a Glance

The question phase established a treatment (the 1993 expansion) and an outcome (male incarceration by race). What it could not supply is a comparison. There is exactly one Texas, and it was treated, so the effect of the expansion is the difference between what happened and what would have happened without it, and the second half of that difference is never observed.

Synthetic control addresses this by constructing the missing counterfactual. It builds a weighted average of untreated states whose combined pre-1993 trajectory tracks Texas closely, then carries that weighted average forward past 1993 as the estimate of where Texas would have gone on its own. This phase covers how the method works, which states make up the donor pool, what predictors the weighting is built on, and three decisions the data forced once fitting began: the analysis window, two donor states dropped for missing data, and a specification chosen by which version the optimizer could actually solve.

## What Synthetic Control Does

The intuition is that no single state is a good stand-in for Texas, but a weighted combination of states might be. Synthetic control searches for a set of weights, one per donor state, that are non-negative and sum to one, such that the weighted average of the donors matches Texas as closely as possible across the pre-treatment period on both the outcome and a set of predictors.

Formally, the estimator picks donor weights \\(W\\) to minimize the pre-period distance between treated and synthetic units:

\\[ \min_{W} \sum_{m} v_m \left( X_{1m} - \sum_{j} w_j X_{jm} \right)^2 \\]

where \\(X_{1m}\\) is predictor \\(m\\) for Texas, \\(X_{jm}\\) is the same predictor for donor state \\(j\\), the weights \\(w_j\\) are non-negative and sum to one, and \\(v_m\\) is an importance weight on each predictor that the procedure itself chooses. The constraint that weights are non-negative and sum to one is what keeps the synthetic control inside the range of real states rather than extrapolating beyond them, which is the property that makes the counterfactual credible.

Once the weights are fixed on pre-period data, the same weighted combination of donors is carried past 1993. The gap between observed Texas and this synthetic Texas, year by year after treatment, is the estimated effect.

## The Donor Pool

The donor pool is the set of states the synthetic Texas is built from. It is every state except Texas itself, with two removed for reasons explained below, leaving a pool from which the weighting selects a handful of close matches and assigns the rest a weight of zero.

The predictors the weighting is built on, drawn from the `texas` panel, are pre-period averages of median income, the unemployment rate, the poverty rate, alcohol consumption, the AIDS rate per capita, the Black population share, and the share of the population aged 15 to 19, together with the lagged outcome itself at three pre-treatment years. The economic and demographic covariates capture the conditions that drive incarceration independent of prison capacity; the lagged outcome anchors the synthetic control to states that were on a similar incarceration path before 1993.

## The Decisions the Data Forced

Three choices were not free parameters but consequences of what the data contained. Each is the kind of decision that is easy to leave undocumented and that a reviewer can only audit if it is stated.

**The analysis window is 1986 to 1999.** The panel runs 1985 to 2000, but the endpoints are unusable. Texas has no white-male prisoner count for 1985, the first year, so a window starting in 1985 would feed the optimizer a missing value for the treated unit and the fit would fail outright. The year 2000 is the mirror image: several donor states stop reporting before the panel ends, so extending the window to 2000 reintroduces missing values on the donor side. Trimming to 1986 through 1999 keeps every unit complete across the whole window, at the cost of one pre-period year and one post-period year. The pre-treatment window used for fitting the weights is 1986 to 1993.

**Two donor states are dropped.** California and New York carry missing white-male counts inside the analysis window, not at its edges, so trimming the window does not rescue them. Rather than let those gaps propagate into the placebo tests of the [inference phase](/archivo/texas-synthetic-control/04-inference/), both states are removed from the donor pool. That leaves a pool of forty-eight comparison states. Dropping two incomplete donors from a pool of this size is a standard move; the alternative of fitting on partial data would quietly corrupt the inference.

**The specification was selected by what solves.** Synthetic control fits by solving a constrained optimization, and that optimization can fail when the predictors are too collinear: several pre-period covariates and closely spaced outcome lags carry nearly the same information, and the solver cannot invert the resulting near-singular system. Rather than guess at a specification and hope, the analysis defines a ladder of specifications from richest to leanest and accepts the first rung that the optimizer can actually solve for both outcomes. With the window trimmed and the two donors dropped, the richest specification, all seven covariates plus three outcome lags, solves cleanly. The leaner rungs exist as a documented fallback that the final fit did not need.

The build is in R using tidysynth. The script that performs the fit and emits the figures lives at [`tools/texas_emit_charts.R`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/texas_emit_charts.R) on GitHub; it refuses to run if any predictor cell in the window is missing, so the completeness guarantees above are enforced in code rather than assumed.
"""

files["03-results.md"] = r"""---
title: "Results"
weight: 30
description: "The estimated effect of the 1993 expansion. The racial-asymmetry gap shown first in proportional terms, then in absolute prisoner counts, the two underlying fits that establish the counterfactual, and the dual finding the data supports: about a fifth larger proportionally, about half again larger in people."
summary: "What the expansion did, proportionally and in people"
tags: ["causal-inference", "data-visualization", "econometrics", "r", "synthetic-control"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Both groups rose after 1993. The result is in how much, and how unevenly.
{{< /lead >}}

## At a Glance

The method phase built a synthetic Texas for each outcome: a weighted average of donor states that tracks Texas closely before 1993 and then carries forward as the estimate of where Texas would have gone without the expansion. The estimated effect is the gap between observed Texas and its synthetic, year by year after treatment.

This phase reads that gap four ways. First in proportional terms, the gap as a share of the synthetic counterfactual, because that is the fair comparison between two groups at very different incarceration levels. Then in absolute prisoner counts, because percentages hide the human scale. Then the two underlying fits, Black male and white male, which show the pre-period match that makes the counterfactual credible. The framing follows what the estimates show: not a clean divide, but an unequal burden.

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

## The Gap, in Proportional Terms

The lead figure measures the effect the way the two series can fairly be compared: each year's gap expressed as a percentage of that year's synthetic counterfactual. A Black-male gap and a white-male gap measured in raw prisoners are not directly comparable, because the two groups sit at very different base levels. As a share of the counterfactual, they are.

Two things stand out. Before 1993, both lines sit near zero, which is the visual signature of a synthetic control that fits its target: there is little gap to speak of because the synthetic is tracking the real series. After 1993, both jump, and they stay elevated for the rest of the window. The Black-male gap runs above the white-male gap throughout the post-period, and the wedge between them is roughly constant rather than widening, which matters for the framing: this is a steady proportional difference, not a divergence that grows over time.

<!-- PASTE CHART BLOCK 1 (proportional gap, lead) from texas_synth_charts.md here -->

The averages behind the picture: across 1994 to 1999, Black-male incarceration ran about 66 percent above its synthetic counterfactual, white-male incarceration about 55 percent above its own. The Black-male gap is therefore about 1.2 times the white-male gap, and that ratio holds steady across the post-period rather than opening up. Both numbers are large. Neither group's increase is close to the near-zero the case study originally expected for white men.

## The Gap, Measured in People

The proportional view is the fair comparison, but it understates the human scale of the difference, because the same percentage of a larger base is more people. The second figure shows the identical gaps in raw prisoner counts.

<!-- PASTE CHART BLOCK 2 (absolute gap, prisoners) from texas_synth_charts.md here -->

By 1999 the expansion is associated with roughly 25,700 more Black men in prison than the synthetic counterfactual predicts, against roughly 16,900 more white men. In absolute terms the Black-male gap is about 1.5 times the white-male gap, wider than the 1.2 times of the proportional view. The reason is exactly the base-rate effect: Black incarceration started higher, so an equal-or-larger proportional increase translates into a substantially larger number of additional people. The pairing of the two figures is the finding. A facially race-neutral expansion produced a difference that is moderate as a percentage and large as a count, which is how a neutral policy compounds an existing disparity.

## The Underlying Fits

The two gap figures are differences, and a difference is only as trustworthy as the counterfactual it is measured against. The next two figures show the fits themselves: observed Texas against its synthetic, for each outcome. What to look for is the pre-1993 segment, where a good synthetic control hugs the real series closely. The post-1993 separation is the estimated effect.

<!-- PASTE CHART BLOCK 3 (Black male fit) from texas_synth_charts.md here -->

The Black-male fit tracks closely through the pre-period, then separates sharply after 1993 as observed Texas climbs away from its synthetic.

<!-- PASTE CHART BLOCK 4 (white male fit) from texas_synth_charts.md here -->

The white-male fit tells the part of the story the original framing got wrong. Observed and synthetic track closely before 1993, exactly as they should, and then they separate too. The white-male effect is smaller than the Black-male effect but it is not absent, and a reader who expected the white series to stay glued to its counterfactual will see instead a clear, real departure. That departure is the reason the case study frames this as an unequal burden rather than a racial divide: the expansion raised incarceration for both groups, and the question the inference phase takes up is whether those departures are large enough to be distinguished from chance.
"""

files["04-inference.md"] = r"""---
title: "Inference"
weight: 40
description: "Whether the estimated effects are distinguishable from chance. The placebo permutation that reassigns the 1993 treatment to every donor state, the MSPE-ratio test that ranks Texas against that placebo distribution, and an honest accounting of what the design can and cannot establish."
summary: "The placebo test, and what it can and cannot prove"
tags: ["causal-inference", "data-visualization", "econometrics", "r", "synthetic-control"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}
{{< lead >}}
A gap is only evidence if it would be unusual to find one this large by chance. The placebo test asks exactly that.
{{< /lead >}}

## At a Glance

The results phase produced two estimated effects: a large post-1993 gap for Black men and a smaller but real one for white men. An estimate is not yet a result. The question this phase answers is whether gaps of those sizes are unusual, or whether the method would manufacture a gap that large for any state if you asked it to.

Synthetic control answers this with a placebo permutation. The procedure refits the entire method pretending each donor state in turn is the treated unit, reassigning the 1993 treatment to a state that was never expanded. Each placebo state gets its own synthetic control and its own post-1993 gap. The collection of placebo gaps is the distribution of effects the method produces under no real treatment, and the real Texas estimate is meaningful only if it sits at the extreme of that distribution.

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

## The Placebo Permutation

The figure below shows the Black-male prisoner gap for Texas in heavy color against the same gap computed for every donor state in grey, each treated as a placebo. If the Texas line is buried in the grey, the estimated effect is indistinguishable from the gaps the method produces by chance. If it stands clear of the grey, the effect is unusual.

<!-- PASTE CHART BLOCK 5 (placebo spaghetti) from texas_synth_charts.md here -->

The Texas line sits at the edge of the placebo distribution after 1993, which is the visual form of the test. The numeric form is the mean squared prediction error ratio, the post-treatment fit error divided by the pre-treatment fit error:

\\[ \text{MSPE ratio} = \dfrac{\frac{1}{T_{post}} \sum_{t > 1993} (Y_t - \hat{Y}_t)^2}{\frac{1}{T_{pre}} \sum_{t \le 1993} (Y_t - \hat{Y}_t)^2} \\]

A large ratio means a unit that fit well before treatment and badly after, which is the signature of a treatment effect rather than a poor synthetic. Ranking every unit by this ratio places the real treated state in the placebo distribution.

## What the Ranking Says

Texas posts the largest MSPE ratio of all forty-nine units for both outcomes. Its Black-male ratio ranks first of forty-nine, and so does its white-male ratio. In permutation terms, the probability of drawing a ratio this extreme by chance is one in forty-nine for each, the smallest p-value the placebo distribution can produce at this pool size.

This is the result the framing has to respect. On the question of whether an effect exists, there is no asymmetry: both the Black-male and the white-male effects are at the extreme of their placebo distributions, both as unlikely to be chance as the test can register. The asymmetry is entirely in magnitude, where the Black-male effect runs about a fifth larger proportionally and about half again larger in people. The data supports "both effects are real, and the Black-male effect is larger," and it does not support "the effect is real for Black men and absent for white men."

## What This Design Can and Cannot Establish

Every analytical claim has limits worth naming, and synthetic control has specific ones.

**The pre-period is short, and the fit is good but not razor-tight.** The weights are fit on eight years, 1986 to 1993. Both fits track their targets closely across that window, but the pre-period gaps wobble within a few percent of zero rather than sitting exactly on it, and the absolute pre-treatment fit error is not negligible. A longer or cleaner pre-period would make the counterfactual more precise. Eight years is enough to support the result; it is not enough to make the result tight.

**This is an association with a credible counterfactual, not a randomized experiment.** Synthetic control constructs the most defensible available comparison and tests it against placebos, which is far stronger than a raw before-and-after. It is not assignment by lottery. The honest verb throughout is that the expansion is "associated with" the estimated increase, and the placebo ranking is the evidence that the association is unlikely to be noise, not proof of the mechanism that produced it.

**The estimate captures the expansion together with anything else that hit Texas in 1993 and nothing else.** Synthetic control attributes the post-1993 gap to the treatment, but it cannot separate the capacity expansion from any other Texas-specific shock that arrived in the same window. The expansion is the largest and best-documented candidate, which is why it carries the attribution, but the design measures the net departure from the counterfactual, not the expansion in isolation.

**The mechanism behind the unequal burden is outside the data.** The estimates establish that the increase fell more heavily on Black men. They do not explain why a race-neutral capacity increase produced a race-uneven result. That question, how supply interacts with the charging, sentencing, and parole decisions that actually fill cells, is real and important and lives beyond what these counts can answer. Naming it is part of the result; resolving it is not something this design can do.

The full fit, including the predictor set, the donor pool, and the figure generation, is reproducible from [`tools/texas_emit_charts.R`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/texas_emit_charts.R). Every number in this case study comes from that script's output against the `texas` panel; anyone running it gets the same estimates, or the case study fails its own reproducibility standard.
"""

for name, text in files.items():
    p = dest / name
    p.write_text(text, encoding='utf-8')
    print(f'wrote {p}')

print()
print('Done. Five files written into the repo folder.')