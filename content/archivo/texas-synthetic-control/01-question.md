---
title: "Question"
weight: 10
description: "The natural experiment. Why the 1993 Texas prison-capacity expansion works as a treatment, why incarceration by race is the outcome worth measuring, the framing the data ended up supporting, and a formal statement of the estimand in potential-outcomes notation."
summary: "The natural experiment and the question it answers"
tags: ["causal-inference", "econometrics", "public-data", "synthetic-control"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}
{{< lead >}}
A policy that builds prison cells does not name a race. The question is whether its effects respected that neutrality.
{{< /lead >}}

## At a Glance

In 1993 Texas began building prisons faster than almost any state ever had. Within about three years it nearly doubled the number of people its system could hold. The decision was about space, not sentences: it added cells without changing the laws that decide who goes to prison or for how long.

That makes it a useful thing to study. When one state makes a large, sudden change and the rest of the country does not, you can ask what would have happened to that state without the change, and compare. If incarceration in Texas jumped after 1993 while similar states held steady, the expansion is the most believable reason for the jump. This phase explains why the expansion counts as a clean test, what to measure against it, and how the conclusion shifted once the numbers came in.

The single-outcome version of this analysis, the 1993 Texas expansion estimated for one prisoner series, is the canonical synthetic-control teaching example from Cunningham's Mixtape. What this case study adds is the race split: running Black-male and white-male incarceration as two parallel outcomes and treating the comparison between them as the finding. The method is borrowed and well-trodden; the contribution is what the comparison reveals.

## Why This Is a Natural Experiment

A clean natural experiment needs three things: a treatment that arrives at a known time, a treated unit that can be compared against untreated ones, and a reason to believe the treatment was not itself caused by the outcome it is supposed to affect. The Texas expansion has all three.

The timing is sharp. Construction and the capacity it unlocked are dated to 1993 through 1995, which gives a clear before and after rather than a gradual drift that would be hard to pin to any single year. The treated unit is one state observed against the other forty-nine, the standard setup for the method this case study uses. And the direction of causation is defensible: a state builds cells in anticipation of needing them, but the buildout is a capital and political undertaking on a scale that does not turn on a single year's incarceration figure. The expansion plausibly raised incarceration; incarceration in any one year did not summon a billion-dollar construction program into being.

What the expansion is not is a randomized trial. No one assigned Texas to treatment and Nebraska to control. The whole burden of the analysis is therefore on constructing a credible comparison: a version of Texas that did not expand, built from states that did not. That construction is the work of [the method phase](/archivo/texas-synthetic-control/02-method/).

## The Outcome Worth Measuring

The natural outcome is incarceration, but incarceration measured how, and for whom. This case study measures the number of men in prison, estimated separately for Black and white men, using the prisoner counts in the `texas` panel.

The choice to split by race is the analytical center of the piece, and it is worth being explicit about why. A capacity expansion does not write race into law. It funds concrete and staffing. If the effect of more cells were genuinely neutral, the increase in incarceration it produced would fall on groups in rough proportion to their existing share of the prison population. If instead the effect landed unevenly, that unevenness is not in the text of the policy; it is in how a race-neutral supply increase interacts with the rest of the system that decides who fills the cells.

So the question the outcome is built to answer is not simply "did incarceration rise" but "did it rise evenly." That is a question a single combined count cannot answer and two race-specific counts can.

One caveat travels with these categories: "Black" and "white" are the classifications as recorded in the source prisoner data, not distinctions this analysis drew. The inference phase returns to what they do and do not capture.

## The Framing the Data Supported

The case study began with a sharper hypothesis than the data ended up supporting, and the gap between the two is worth recording rather than hiding.

The initial expectation was a clean racial divide: that the expansion would drive Black male incarceration sharply upward while leaving white male incarceration close to its counterfactual. The estimates did not show that. Both series rose substantially after 1993. The white male increase was real, large, and statistically distinguishable from chance, not the near-null the original framing assumed.

What the data did show is an unequal burden. Both groups' incarceration climbed well above what the synthetic control predicted, but the Black male climb ran about a fifth larger in proportional terms and roughly half again as large in absolute numbers by the end of the window. The honest finding is therefore not that the policy affected one group and spared the other, but that a race-neutral expansion produced a large increase for both groups and a heavier one for Black men. That is a more careful claim than the original, and it is the one [the results phase](/archivo/texas-synthetic-control/03-results/) defends with the actual estimates.

## The Estimand, Stated Formally

For a reader who wants the target defined precisely, the question is an estimand in the potential-outcomes framework. Let \(Y_{it}(1)\) be the incarceration count in state \(i\) at year \(t\) under the expansion, and \(Y_{it}(0)\) the count that would have obtained without it. For Texas in the post-treatment years, the quantity of interest is the difference between the two:

\[ \tau_{t} = Y_{\text{TX},t}(1) - Y_{\text{TX},t}(0), \quad t > 1993 \]

where:
- \(\tau_{t}\) is the treatment effect in year \(t\): how much higher Texas incarceration was because of the expansion
- \(Y_{\text{TX},t}(1)\) is the incarceration count Texas actually recorded, with the expansion
- \(Y_{\text{TX},t}(0)\) is the count Texas would have recorded without the expansion, which is never observed
- \(t > 1993\) restricts attention to the years after the buildout began


The first term is observed: it is what Texas actually recorded. The second term is the counterfactual and is never observed, because Texas did expand. Every other state supplies \(Y_{it}(0)\) only, since none of them received the treatment. The entire methodological problem is the estimation of the single missing term \(Y_{\text{TX},t}(0)\), and synthetic control is one disciplined way to estimate it.

The race split runs the same estimand twice, once for each outcome:

\[ \tau_{t}^{\,b} = Y_{\text{TX},t}^{\,b}(1) - Y_{\text{TX},t}^{\,b}(0), \qquad \tau_{t}^{\,w} = Y_{\text{TX},t}^{\,w}(1) - Y_{\text{TX},t}^{\,w}(0) \]

where:
- The superscript \(b\) marks the Black-male prisoner count and \(w\) the white-male count
- \(\tau_{t}^{\,b}\) and \(\tau_{t}^{\,w}\) are the same treatment effect computed separately for each group
- Everything else matches the single-outcome version above, just run twice


The "unequal burden" finding is a statement about the relationship between \(\tau_{t}^{\,b}\) and \(\tau_{t}^{\,w}\): both are large and positive after 1993, and \(\tau_{t}^{\,b}\) exceeds \(\tau_{t}^{\,w}\) both in proportion to its baseline and in absolute count.
