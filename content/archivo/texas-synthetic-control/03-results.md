---
title: "Results"
weight: 30
description: "The estimated effect of the 1993 expansion. The racial-asymmetry gap shown first in proportional terms, then in absolute prisoner counts, the two underlying fits that establish the counterfactual, and the dual finding the data supports: about a fifth larger proportionally, about half again larger in people."
summary: "What the expansion did, proportionally and in people"
tags: ["r", "causal-inference", "data-visualization", "econometrics", "synthetic-control", "case-study"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}
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

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Both Groups Rise, Black Men Bear the Larger Share</p>
<p class="pgbd-case-chart-sub">Gap between observed Texas and its synthetic control, as a share of the counterfactual. Both groups jump after 1993, averaging about 66% above synthetic for Black men and 55% for white men through 1999. The Black male gap runs about 1.2 times the white gap, and that ratio holds steady across the post-period.</p>

{{< chart >}}

  "type": "line",
  "data": {
    "datasets": [
      {
        "label": "Black male gap (% of synthetic)",
        "data": [
          {
            "x": 1986,
            "y": 0.8
          },
          {
            "x": 1987,
            "y": 0.6
          },
          {
            "x": 1988,
            "y": -0.6
          },
          {
            "x": 1989,
            "y": -3.8
          },
          {
            "x": 1990,
            "y": -1.8
          },
          {
            "x": 1991,
            "y": -6.2
          },
          {
            "x": 1992,
            "y": 6
          },
          {
            "x": 1993,
            "y": 2.8
          },
          {
            "x": 1994,
            "y": 33.2
          },
          {
            "x": 1995,
            "y": 67.6
          },
          {
            "x": 1996,
            "y": 71
          },
          {
            "x": 1997,
            "y": 76.7
          },
          {
            "x": 1998,
            "y": 73.6
          },
          {
            "x": 1999,
            "y": 73.2
          }
        ],
        "borderColor": "#D55E00",
        "backgroundColor": "#D55E00",
        "borderWidth": 2.5,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false
      },
      {
        "label": "White male gap (% of synthetic)",
        "data": [
          {
            "x": 1986,
            "y": 1.9
          },
          {
            "x": 1987,
            "y": 8.3
          },
          {
            "x": 1988,
            "y": 3.1
          },
          {
            "x": 1989,
            "y": -3.6
          },
          {
            "x": 1990,
            "y": -4.5
          },
          {
            "x": 1991,
            "y": -6.3
          },
          {
            "x": 1992,
            "y": 5.6
          },
          {
            "x": 1993,
            "y": -1
          },
          {
            "x": 1994,
            "y": 39.9
          },
          {
            "x": 1995,
            "y": 51.8
          },
          {
            "x": 1996,
            "y": 51.2
          },
          {
            "x": 1997,
            "y": 56.8
          },
          {
            "x": 1998,
            "y": 60.3
          },
          {
            "x": 1999,
            "y": 68.1
          }
        ],
        "borderColor": "#0072B2",
        "backgroundColor": "#0072B2",
        "borderWidth": 2.5,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false
      },
      {
        "label": "1993: prison expansion begins",
        "data": [
          {
            "x": 1993,
            "y": -20
          },
          {
            "x": 1993,
            "y": 90
          }
        ],
        "borderColor": "#888888",
        "borderWidth": 1.5,
        "borderDash": [6, 4],
        "pointRadius": 0,
        "pointHitRadius": 0,
        "fill": false,
        "order": 99
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "interaction": {
      "mode": "index",
      "intersect": false
    },
    "scales": {
      "x": {
        "type": "linear",
        "min": 1986,
        "max": 1999,
        "ticks": {
          "stepSize": 3,
          "precision": 0,
          "format": {
            "useGrouping": false
          }
        },
        "title": {
          "display": true,
          "text": "Year"
        }
      },
      "y": {
        "min": -20,
        "max": 90,
        "title": {
          "display": true,
          "text": "Gap vs Synthetic (%)"
        }
      }
    },
    "plugins": {
      "legend": {
        "display": true,
        "position": "bottom"
      },
      "tooltip": {
        "enabled": true
      }
    }
  }
{{< /chart >}}

</div>

The averages behind the picture: across 1994 to 1999, Black-male incarceration ran about 66 percent above its synthetic counterfactual, white-male incarceration about 55 percent above its own. The Black-male gap is therefore about 1.2 times the white-male gap, and that ratio holds steady across the post-period rather than opening up. Both numbers are large. Neither group's increase is close to the near-zero the case study originally expected for white men.

## The Gap, Measured in People

The proportional view is the fair comparison, but it understates the human scale of the difference, because the same percentage of a larger base is more people. The second figure shows the identical gaps in raw prisoner counts.

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Measured in People, the Gap Is Wider</p>
<p class="pgbd-case-chart-sub">The same gap measured in prisoners. By 1999 the expansion is associated with roughly 25,700 additional Black male prisoners against 16,900 white, an absolute gap of about 1.5 times. It is wider than the proportional gap because Black incarceration started from a higher base.</p>

{{< chart >}}

  "type": "line",
  "data": {
    "datasets": [
      {
        "label": "Black male gap (prisoners)",
        "data": [
          {
            "x": 1986,
            "y": 122
          },
          {
            "x": 1987,
            "y": 96
          },
          {
            "x": 1988,
            "y": -107
          },
          {
            "x": 1989,
            "y": -757
          },
          {
            "x": 1990,
            "y": -409
          },
          {
            "x": 1991,
            "y": -1543
          },
          {
            "x": 1992,
            "y": 1564
          },
          {
            "x": 1993,
            "y": 796
          },
          {
            "x": 1994,
            "y": 10093
          },
          {
            "x": 1995,
            "y": 22417
          },
          {
            "x": 1996,
            "y": 23168
          },
          {
            "x": 1997,
            "y": 25350
          },
          {
            "x": 1998,
            "y": 25305
          },
          {
            "x": 1999,
            "y": 25692
          }
        ],
        "borderColor": "#D55E00",
        "backgroundColor": "#D55E00",
        "borderWidth": 2.5,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false
      },
      {
        "label": "White male gap (prisoners)",
        "data": [
          {
            "x": 1986,
            "y": 251
          },
          {
            "x": 1987,
            "y": 999
          },
          {
            "x": 1988,
            "y": 394
          },
          {
            "x": 1989,
            "y": -498
          },
          {
            "x": 1990,
            "y": -667
          },
          {
            "x": 1991,
            "y": -947
          },
          {
            "x": 1992,
            "y": 873
          },
          {
            "x": 1993,
            "y": -176
          },
          {
            "x": 1994,
            "y": 7477
          },
          {
            "x": 1995,
            "y": 11124
          },
          {
            "x": 1996,
            "y": 11411
          },
          {
            "x": 1997,
            "y": 12862
          },
          {
            "x": 1998,
            "y": 14289
          },
          {
            "x": 1999,
            "y": 16877
          }
        ],
        "borderColor": "#0072B2",
        "backgroundColor": "#0072B2",
        "borderWidth": 2.5,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false
      },
      {
        "label": "1993: prison expansion begins",
        "data": [
          {
            "x": 1993,
            "y": -5000
          },
          {
            "x": 1993,
            "y": 30000
          }
        ],
        "borderColor": "#888888",
        "borderWidth": 1.5,
        "borderDash": [6, 4],
        "pointRadius": 0,
        "pointHitRadius": 0,
        "fill": false,
        "order": 99
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "interaction": {
      "mode": "index",
      "intersect": false
    },
    "scales": {
      "x": {
        "type": "linear",
        "min": 1986,
        "max": 1999,
        "ticks": {
          "stepSize": 3,
          "precision": 0,
          "format": {
            "useGrouping": false
          }
        },
        "title": {
          "display": true,
          "text": "Year"
        }
      },
      "y": {
        "min": -5000,
        "max": 30000,
        "title": {
          "display": true,
          "text": "Prisoners (Gap vs Synthetic)"
        }
      }
    },
    "plugins": {
      "legend": {
        "display": true,
        "position": "bottom"
      },
      "tooltip": {
        "enabled": true
      }
    }
  }
{{< /chart >}}

</div>

By 1999 the expansion is associated with roughly 25,700 more Black men in prison than the synthetic counterfactual predicts, against roughly 16,900 more white men. In absolute terms the Black-male gap is about 1.5 times the white-male gap, wider than the 1.2 times of the proportional view. The reason is exactly the base-rate effect: Black incarceration started higher, so an equal-or-larger proportional increase translates into a substantially larger number of additional people. The pairing of the two figures is the finding. A facially race-neutral expansion produced a difference that is moderate as a percentage and large as a count, which is how a neutral policy compounds an existing disparity.

## The Underlying Fits

The two gap figures are differences, and a difference is only as trustworthy as the counterfactual it is measured against. The next two figures show the fits themselves: observed Texas against its synthetic, for each outcome. What to look for is the pre-1993 segment, where a good synthetic control hugs the real series closely. The post-1993 separation is the estimated effect.

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Black Male Incarceration: Texas vs Synthetic Texas</p>
<p class="pgbd-case-chart-sub">Pre-1993 fit and post-1993 divergence for the Black male series.</p>

{{< chart >}}

  "type": "line",
  "data": {
    "datasets": [
      {
        "label": "Texas (observed)",
        "data": [
          {
            "x": 1986,
            "y": 15207
          },
          {
            "x": 1987,
            "y": 15780
          },
          {
            "x": 1988,
            "y": 16956
          },
          {
            "x": 1989,
            "y": 19366
          },
          {
            "x": 1990,
            "y": 22634
          },
          {
            "x": 1991,
            "y": 23249
          },
          {
            "x": 1992,
            "y": 27568
          },
          {
            "x": 1993,
            "y": 29260
          },
          {
            "x": 1994,
            "y": 40451
          },
          {
            "x": 1995,
            "y": 55602
          },
          {
            "x": 1996,
            "y": 55810
          },
          {
            "x": 1997,
            "y": 58393
          },
          {
            "x": 1998,
            "y": 59709
          },
          {
            "x": 1999,
            "y": 60785
          }
        ],
        "borderColor": "#D55E00",
        "backgroundColor": "#D55E00",
        "borderWidth": 2.5,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false
      },
      {
        "label": "Synthetic Texas",
        "data": [
          {
            "x": 1986,
            "y": 15085
          },
          {
            "x": 1987,
            "y": 15684
          },
          {
            "x": 1988,
            "y": 17063
          },
          {
            "x": 1989,
            "y": 20123
          },
          {
            "x": 1990,
            "y": 23043
          },
          {
            "x": 1991,
            "y": 24792
          },
          {
            "x": 1992,
            "y": 26004
          },
          {
            "x": 1993,
            "y": 28464
          },
          {
            "x": 1994,
            "y": 30358
          },
          {
            "x": 1995,
            "y": 33185
          },
          {
            "x": 1996,
            "y": 32642
          },
          {
            "x": 1997,
            "y": 33043
          },
          {
            "x": 1998,
            "y": 34404
          },
          {
            "x": 1999,
            "y": 35093
          }
        ],
        "borderColor": "#CC79A7",
        "backgroundColor": "#CC79A7",
        "borderWidth": 2,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "borderDash": [7, 4]
      },
      {
        "label": "1993: prison expansion begins",
        "data": [
          {
            "x": 1993,
            "y": 10000
          },
          {
            "x": 1993,
            "y": 65000
          }
        ],
        "borderColor": "#888888",
        "borderWidth": 1.5,
        "borderDash": [6, 4],
        "pointRadius": 0,
        "pointHitRadius": 0,
        "fill": false,
        "order": 99
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "interaction": {
      "mode": "index",
      "intersect": false
    },
    "scales": {
      "x": {
        "type": "linear",
        "min": 1986,
        "max": 1999,
        "ticks": {
          "stepSize": 3,
          "precision": 0,
          "format": {
            "useGrouping": false
          }
        },
        "title": {
          "display": true,
          "text": "Year"
        }
      },
      "y": {
        "min": 10000,
        "max": 65000,
        "title": {
          "display": true,
          "text": "Black Male Prisoners"
        }
      }
    },
    "plugins": {
      "legend": {
        "display": true,
        "position": "bottom"
      },
      "tooltip": {
        "enabled": true
      }
    }
  }
{{< /chart >}}

</div>

The Black-male fit tracks closely through the pre-period, then separates sharply after 1993 as observed Texas climbs away from its synthetic.

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">White Male Incarceration: Texas vs Synthetic Texas</p>
<p class="pgbd-case-chart-sub">The same construction for white men. The effect is large here too, not absent, which is the point: the expansion raised incarceration for both groups.</p>

{{< chart >}}

  "type": "line",
  "data": {
    "datasets": [
      {
        "label": "Texas (observed)",
        "data": [
          {
            "x": 1986,
            "y": 13423
          },
          {
            "x": 1987,
            "y": 13108
          },
          {
            "x": 1988,
            "y": 13192
          },
          {
            "x": 1989,
            "y": 13383
          },
          {
            "x": 1990,
            "y": 14253
          },
          {
            "x": 1991,
            "y": 14168
          },
          {
            "x": 1992,
            "y": 16594
          },
          {
            "x": 1993,
            "y": 17184
          },
          {
            "x": 1994,
            "y": 26201
          },
          {
            "x": 1995,
            "y": 32594
          },
          {
            "x": 1996,
            "y": 33676
          },
          {
            "x": 1997,
            "y": 35504
          },
          {
            "x": 1998,
            "y": 37973
          },
          {
            "x": 1999,
            "y": 41668
          }
        ],
        "borderColor": "#0072B2",
        "backgroundColor": "#0072B2",
        "borderWidth": 2.5,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false
      },
      {
        "label": "Synthetic Texas",
        "data": [
          {
            "x": 1986,
            "y": 13172
          },
          {
            "x": 1987,
            "y": 12109
          },
          {
            "x": 1988,
            "y": 12798
          },
          {
            "x": 1989,
            "y": 13881
          },
          {
            "x": 1990,
            "y": 14920
          },
          {
            "x": 1991,
            "y": 15115
          },
          {
            "x": 1992,
            "y": 15721
          },
          {
            "x": 1993,
            "y": 17360
          },
          {
            "x": 1994,
            "y": 18724
          },
          {
            "x": 1995,
            "y": 21470
          },
          {
            "x": 1996,
            "y": 22265
          },
          {
            "x": 1997,
            "y": 22642
          },
          {
            "x": 1998,
            "y": 23684
          },
          {
            "x": 1999,
            "y": 24791
          }
        ],
        "borderColor": "#CC79A7",
        "backgroundColor": "#CC79A7",
        "borderWidth": 2,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "borderDash": [7, 4]
      },
      {
        "label": "1993: prison expansion begins",
        "data": [
          {
            "x": 1993,
            "y": 10000
          },
          {
            "x": 1993,
            "y": 45000
          }
        ],
        "borderColor": "#888888",
        "borderWidth": 1.5,
        "borderDash": [6, 4],
        "pointRadius": 0,
        "pointHitRadius": 0,
        "fill": false,
        "order": 99
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "interaction": {
      "mode": "index",
      "intersect": false
    },
    "scales": {
      "x": {
        "type": "linear",
        "min": 1986,
        "max": 1999,
        "ticks": {
          "stepSize": 3,
          "precision": 0,
          "format": {
            "useGrouping": false
          }
        },
        "title": {
          "display": true,
          "text": "Year"
        }
      },
      "y": {
        "min": 10000,
        "max": 45000,
        "title": {
          "display": true,
          "text": "White Male Prisoners"
        }
      }
    },
    "plugins": {
      "legend": {
        "display": true,
        "position": "bottom"
      },
      "tooltip": {
        "enabled": true
      }
    }
  }
{{< /chart >}}

</div>

The white-male fit tells the part of the story the original framing got wrong. Observed and synthetic track closely before 1993, exactly as they should, and then they separate too. The white-male effect is smaller than the Black-male effect but it is not absent, and a reader who expected the white series to stay glued to its counterfactual will see instead a clear, real departure. That departure is the reason the case study frames this as an unequal burden rather than a racial divide: the expansion raised incarceration for both groups, and the question the inference phase takes up is whether those departures are large enough to be distinguished from chance.


## The Estimator in Symbols

The figures above are all built from a single quantity: the gap between observed Texas and its synthetic counterfactual in each post-treatment year. With the donor weights \(w_j^{*}\) fixed on the pre-period as described in [the method phase](/archivo/texas-synthetic-control/02-method/), the estimated effect in year \(t\) is

\[ \hat{\tau}_t = Y_{\text{TX},t} - \sum_{j=2}^{J+1} w_j^{*} \, Y_{jt} \]

where:
- \(\hat{\tau}_t\) is the absolute gap in year \(t\), measured in prisoners
- \(Y_{\text{TX},t}\) is Texas's observed count and the sum is the synthetic counterfactual
- \(w_j^{*}\) is the solved weight for donor \(j\); \(Y_{jt}\) is that donor's count in year \(t\)


where \(Y_{\text{TX},t}\) is the observed Texas count and the sum is the synthetic value. This is the absolute gap, the quantity plotted in prisoners.

The proportional gap divides that difference by the synthetic counterfactual, which is what makes the Black-male and white-male series comparable across their very different baselines:

\[ \hat{\pi}_t = \dfrac{\hat{\tau}_t}{\sum_{j=2}^{J+1} w_j^{*} \, Y_{jt}} = \dfrac{Y_{\text{TX},t} - \hat{Y}_{\text{TX},t}(0)}{\hat{Y}_{\text{TX},t}(0)} \]

where:
- \(\hat{\pi}_t\) is the proportional gap: the absolute gap divided by the synthetic counterfactual, so it reads as a percentage
- The denominator \(\hat{Y}_{\text{TX},t}(0)\) is the synthetic count, the same weighted blend as above
- Dividing by the counterfactual is what makes the Black and white gaps comparable despite very different baselines


The two summary ratios the case study reports are functions of these quantities, averaged over the post-period \(t \in \{1994, \dots, 1999\}\). The proportional ratio compares the mean proportional gaps of the two outcomes:

\[ R_{\pi} = \dfrac{\overline{\hat{\pi}}^{\,b}}{\overline{\hat{\pi}}^{\,w}} \approx \dfrac{0.66}{0.55} \approx 1.2 \]

where:
- \(R_{\pi}\) is the ratio of the two groups' proportional gaps
- \(\overline{\hat{\pi}}^{\,b}\) and \(\overline{\hat{\pi}}^{\,w}\) are the average proportional gaps for Black and white men across 1994 to 1999
- The result, about 1.2, means the Black-male gap runs roughly a fifth larger in proportional terms


while the absolute ratio compares the end-of-window gaps in people:

\[ R_{\tau} = \dfrac{\hat{\tau}_{1999}^{\,b}}{\hat{\tau}_{1999}^{\,w}} \approx \dfrac{25{,}692}{16{,}877} \approx 1.5 \]

where:
- \(R_{\tau}\) is the ratio of the two groups' absolute gaps, in people
- \(\hat{\tau}_{1999}^{\,b}\) and \(\hat{\tau}_{1999}^{\,w}\) are the end-of-window prisoner gaps for Black and white men
- The result, about 1.5, is larger than the proportional ratio because Black incarceration starts from a higher base


The gap between \(R_{\pi} \approx 1.2\) and \(R_{\tau} \approx 1.5\) is the base-rate effect stated exactly: the same effect is a fifth larger proportionally but half again larger in people, because the denominator \(\hat{Y}^{\,b}(0)\) for Black men is itself far larger than \(\hat{Y}^{\,w}(0)\) for white men.
