---
title: "Texas Prison Expansion"
weight: 10
description: "A synthetic control case study on the 1993 Texas prison-capacity expansion and what it did to incarceration, estimated separately for Black and white men. Cunningham's Mixtape data fit in R with tidysynth, walked through phase by phase so every identification decision is auditable."
summary: "A natural experiment and an unequal burden"
tags: ["r", "causal-inference", "econometrics", "predictive-modeling", "synthetic-control", "case-study"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
A synthetic control case study on the 1993 Texas prison-capacity expansion, walked through phase by phase.
{{< /lead >}}

## At a Glance

In 1993 Texas began roughly doubling its operational prison capacity, a buildout that ran through 1995 and stands as one of the largest state-level carceral expansions in modern American history. This case study treats that buildout as a natural experiment and asks a counterfactual question: how much higher did male incarceration in Texas climb than it would have without the expansion? The estimator is synthetic control, a method built precisely for a single treated unit observed against many untreated ones. The data is the `texas` panel from Scott Cunningham's Causal Inference: The Mixtape, fit in R with [tidysynth](https://github.com/edunford/tidysynth).

The analysis runs two outcomes side by side, Black male and white male incarceration, because the comparison is the finding. A capacity expansion is facially race-neutral: it builds cells, not sentences. Yet the estimated effect is not race-neutral. Both groups' incarceration rose sharply after 1993, but the Black male increase ran consistently larger in proportional terms and far larger in absolute numbers. The full reasoning, including why Texas, why 1993, and why this method, lives across the four phases.

## The Phases
