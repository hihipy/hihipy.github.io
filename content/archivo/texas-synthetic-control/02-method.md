---
title: "Method"
weight: 20
description: "What synthetic control does and why it fits a single-state treatment, the donor pool, the predictor set, the data-driven decisions that shaped the fit, and the full formal estimator: predictor balance, the weight simplex, and the nested optimization that selects predictor importances."
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

The question phase ended on a missing number: what incarceration in Texas would have been without the 1993 expansion. That number cannot be looked up, because Texas expanded. Synthetic control is a way to estimate it.

The idea is simple to state. No single other state looks enough like Texas to stand in for it. But a blend of several states, weighted so the blend matches Texas closely in the years before 1993, can serve as a stand-in. You build that blend on the pre-1993 data, then carry it forward. Where the real Texas pulls away from the blend after 1993 is the estimated effect. This phase covers the method in plain terms, the pool of states it draws from, the predictors it matches on, the three decisions the data forced, and, at the end, the full formal version for a reader who wants it.

## What Synthetic Control Does

The intuition is that no single state is a good stand-in for Texas, but a weighted combination of states might be. Synthetic control searches for a set of weights, one per donor state, that are non-negative and sum to one, such that the weighted average of the donors matches Texas as closely as possible across the pre-treatment period on both the outcome and a set of predictors.

Once those weights are fixed on pre-period data, the same weighted combination of donors is carried past 1993. The gap between observed Texas and this synthetic Texas, year by year after treatment, is the estimated effect. The constraint that the weights are non-negative and sum to one matters: it keeps the synthetic control inside the range of real states rather than extrapolating beyond them, which is what makes the counterfactual credible rather than a curve fit.

## The Donor Pool

The donor pool is the set of states the synthetic Texas is built from. It is every state except Texas itself, with two removed for reasons explained below, leaving a pool from which the weighting selects a handful of close matches and assigns the rest a weight of zero.

The predictors the weighting is built on, drawn from the `texas` panel, are pre-period averages of median income, the unemployment rate, the poverty rate, alcohol consumption, the AIDS rate per capita, the Black population share, and the share of the population aged 15 to 19, together with the lagged outcome itself at three pre-treatment years. The economic and demographic covariates capture the conditions that drive incarceration independent of prison capacity; the lagged outcome anchors the synthetic control to states that were on a similar incarceration path before 1993.

## The Decisions the Data Forced

Three choices were not free parameters but consequences of what the data contained. Each is the kind of decision that is easy to leave undocumented and that a reviewer can only audit if it is stated.

**The analysis window is 1986 to 1999.** The panel runs 1985 to 2000, but the endpoints are unusable. Texas has no white-male prisoner count for 1985, the first year, so a window starting in 1985 would feed the optimizer a missing value for the treated unit and the fit would fail outright. The year 2000 is the mirror image: several donor states stop reporting before the panel ends, so extending the window to 2000 reintroduces missing values on the donor side. Trimming to 1986 through 1999 keeps every unit complete across the whole window, at the cost of one pre-period year and one post-period year. The pre-treatment window used for fitting the weights is 1986 to 1993.

**Two donor states are dropped.** California and New York carry missing white-male counts inside the analysis window, not at its edges, so trimming the window does not rescue them. Rather than let those gaps propagate into the placebo tests of the [inference phase](/archivo/texas-synthetic-control/04-inference/), both states are removed from the donor pool. That leaves a pool of forty-eight comparison states. Dropping two incomplete donors from a pool of this size is a standard move; the alternative of fitting on partial data would quietly corrupt the inference.

**The specification was selected by what solves.** Synthetic control fits by solving a constrained optimization, and that optimization can fail when the predictors are too collinear: several pre-period covariates and closely spaced outcome lags carry nearly the same information, and the solver cannot invert the resulting near-singular system. Rather than guess at a specification and hope, the analysis defines a ladder of specifications from richest to leanest and accepts the first rung that the optimizer can actually solve for both outcomes. With the window trimmed and the two donors dropped, the richest specification, all seven covariates plus three outcome lags, solves cleanly. The leaner rungs exist as a documented fallback that the final fit did not need.

## The Fit, in Code

The estimator above is implemented with [`tidysynth`](https://cran.r-project.org/package=tidysynth), whose pipeline mirrors the steps almost exactly: declare the treated unit and treatment year, supply the predictors, solve for the weights on the pre-period, then generate the synthetic control and its placebo distribution. The core of the fit, for the Black-male outcome, reads:

```r
library(tidysynth)

sc_black <- texas_panel |>
  synthetic_control(
    outcome    = bmprison,
    unit       = state,
    time       = year,
    i_unit     = "Texas",
    i_time     = 1993,
    generate_placebos = TRUE
  ) |>
  # one generate_predictor() call per covariate, averaged over the pre-window
  generate_predictor(time_window = 1986:1993, income = mean(income, na.rm = TRUE)) |>
  generate_predictor(time_window = 1986:1993, ur     = mean(ur, na.rm = TRUE)) |>
  # ... remaining covariates and the three outcome lags ...
  generate_weights(optimization_window = 1986:1993) |>
  generate_control()
```

`generate_weights()` is where the nested optimization runs: it solves for the donor weights and the predictor-importance matrix together. `generate_control()` then carries the weighted donor blend across the full window, and `generate_placebos = TRUE` reruns the whole fit with each donor state cast as the treated unit, which is what the [inference phase](/archivo/texas-synthetic-control/04-inference/) uses for the permutation test. The white-male fit is identical with `wmprison` in place of `bmprison`.

## The Estimator, in Full

For the technical reader, here is the estimator stated precisely. Index the treated unit as \(j = 1\) (Texas) and the donor states as \(j = 2, \dots, J+1\). Let \(X_1\) be the \(k \times 1\) vector of pre-treatment predictors for Texas, and \(X_0\) the \(k \times J\) matrix stacking the same predictors for the donors. The synthetic control is a weight vector \(W = (w_2, \dots, w_{J+1})'\) chosen to make the donor blend match Texas on those predictors.

The weights are restricted to the unit simplex, which is the constraint that gives the method its credibility:

\[ w_j \geq 0 \quad \text{for all } j, \qquad \sum_{j=2}^{J+1} w_j = 1 \]

where:
- \(w_j\) is the weight given to donor state \(j\) in the synthetic blend
- The first condition forces every weight to be zero or positive, so no state is subtracted
- The second condition forces the weights to sum to one, so the blend is a genuine weighted average and cannot extrapolate beyond the real states
- \(J\) is the number of donor states (Texas is unit 1; donors are units 2 through \(J+1\))


Within that constraint, the weights minimize a weighted distance between Texas and the donor blend on the predictors:

\[ W^{*}(V) = \arg\min_{W} \; (X_1 - X_0 W)' \, V \, (X_1 - X_0 W) \]

where:
- \(W\) is the full set of donor weights the method solves for; \(W^{*}(V)\) is the best set given an importance matrix \(V\)
- \(X_1\) is the column of Texas's pre-1993 predictor values (income, poverty, the outcome lags, and the rest)
- \(X_0\) is the same predictors for every donor state, stacked into a matrix
- \(V\) is a diagonal matrix of importances, one per predictor, saying how much each predictor counts toward the match
- \(\arg\min_{W}\) means "the choice of \(W\) that makes the bracketed distance as small as possible"


The matrix \(V\) is diagonal and assigns an importance to each predictor. It is not chosen by hand. It is selected by an outer optimization that picks the \(V\) whose resulting weights produce the smallest prediction error on the pre-treatment outcome path. Writing \(Z_1\) for Texas's pre-period outcome vector and \(Z_0\) for the donors':

\[ V^{*} = \arg\min_{V} \; \big( Z_1 - Z_0 \, W^{*}(V) \big)' \big( Z_1 - Z_0 \, W^{*}(V) \big) \]

where:
- \(V^{*}\) is the importance matrix the outer optimization settles on
- \(Z_1\) is Texas's actual pre-1993 incarceration path (the outcome itself, year by year)
- \(Z_0\) is the same pre-1993 paths for the donor states
- \(W^{*}(V)\) is the weight solution from the inner problem above, which depends on \(V\)
- In words: pick the predictor importances whose resulting weights track Texas's real pre-1993 path most closely


This is the nested structure that makes the fit both data-driven and prone to the singular-matrix failures the specification ladder was built to handle: the inner problem solves the constrained quadratic program for \(W\) given \(V\), and the outer problem searches over \(V\). When predictors are near-collinear, the inner program's matrix is near-singular and the solver fails, which is exactly the symptom the ladder steps around.

With \(W^{*}\) fixed, the synthetic control's outcome in any year is the weighted donor average, and the estimated effect is the gap between observed Texas and that synthetic value:

\[ \hat{Y}_{\text{TX},t}(0) = \sum_{j=2}^{J+1} w_j^{*} \, Y_{jt}, \qquad \hat{\tau}_t = Y_{\text{TX},t} - \hat{Y}_{\text{TX},t}(0) \]

where:
- \(\hat{Y}_{\text{TX},t}(0)\) is the synthetic counterfactual: the weighted blend of donor states, the estimate of where Texas would have gone without the expansion
- \(w_j^{*}\) is the final solved weight for donor state \(j\), and \(Y_{jt}\) is that state's incarceration in year \(t\)
- \(Y_{\text{TX},t}\) is Texas's actual incarceration in year \(t\)
- \(\hat{\tau}_t\) is the estimated effect: the gap between real Texas and its synthetic, year by year


The build is in R using tidysynth, with a hard guard that refuses to run if any predictor cell in the window is missing, so the completeness guarantees above are enforced in code rather than assumed.
