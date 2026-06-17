---
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

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Placebo Inference: Texas Against Every Donor State</p>
<p class="pgbd-case-chart-sub">Each grey line reassigns the 1993 treatment to a donor state, on the raw prisoner gap used for the permutation test. Texas posts the largest post-to-pre MSPE ratio of all 49 units (rank 1).</p>

{{< chart >}}

  "type": "line",
  "data": {
    "datasets": [
      {
        "label": "Texas",
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
        "borderWidth": 2.8,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 0
      },
      {
        "label": "Alabama",
        "data": [
          {
            "x": 1986,
            "y": -5
          },
          {
            "x": 1987,
            "y": 465
          },
          {
            "x": 1988,
            "y": -119
          },
          {
            "x": 1989,
            "y": -165
          },
          {
            "x": 1990,
            "y": 193
          },
          {
            "x": 1991,
            "y": 302
          },
          {
            "x": 1992,
            "y": -21
          },
          {
            "x": 1993,
            "y": -173
          },
          {
            "x": 1994,
            "y": -1328
          },
          {
            "x": 1995,
            "y": -3288
          },
          {
            "x": 1996,
            "y": -3218
          },
          {
            "x": 1997,
            "y": -3423
          },
          {
            "x": 1998,
            "y": -3911
          },
          {
            "x": 1999,
            "y": -2910
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Alaska",
        "data": [
          {
            "x": 1986,
            "y": -126
          },
          {
            "x": 1987,
            "y": -135
          },
          {
            "x": 1988,
            "y": -132
          },
          {
            "x": 1989,
            "y": -162
          },
          {
            "x": 1990,
            "y": -245
          },
          {
            "x": 1991,
            "y": -236
          },
          {
            "x": 1992,
            "y": -236
          },
          {
            "x": 1993,
            "y": -337
          },
          {
            "x": 1994,
            "y": -283
          },
          {
            "x": 1995,
            "y": -336
          },
          {
            "x": 1996,
            "y": -290
          },
          {
            "x": 1997,
            "y": -352
          },
          {
            "x": 1998,
            "y": -407
          },
          {
            "x": 1999,
            "y": -484
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Arizona",
        "data": [
          {
            "x": 1986,
            "y": -129
          },
          {
            "x": 1987,
            "y": 8
          },
          {
            "x": 1988,
            "y": -50
          },
          {
            "x": 1989,
            "y": -55
          },
          {
            "x": 1990,
            "y": -37
          },
          {
            "x": 1991,
            "y": -23
          },
          {
            "x": 1992,
            "y": 54
          },
          {
            "x": 1993,
            "y": 78
          },
          {
            "x": 1994,
            "y": 30
          },
          {
            "x": 1995,
            "y": -279
          },
          {
            "x": 1996,
            "y": -274
          },
          {
            "x": 1997,
            "y": -246
          },
          {
            "x": 1998,
            "y": -228
          },
          {
            "x": 1999,
            "y": -193
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Arkansas",
        "data": [
          {
            "x": 1986,
            "y": -344
          },
          {
            "x": 1987,
            "y": -98
          },
          {
            "x": 1988,
            "y": -190
          },
          {
            "x": 1989,
            "y": -332
          },
          {
            "x": 1990,
            "y": -9
          },
          {
            "x": 1991,
            "y": 18
          },
          {
            "x": 1992,
            "y": 117
          },
          {
            "x": 1993,
            "y": -59
          },
          {
            "x": 1994,
            "y": -736
          },
          {
            "x": 1995,
            "y": -1111
          },
          {
            "x": 1996,
            "y": -1463
          },
          {
            "x": 1997,
            "y": -1572
          },
          {
            "x": 1998,
            "y": -1925
          },
          {
            "x": 1999,
            "y": -3678
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Colorado",
        "data": [
          {
            "x": 1986,
            "y": -307
          },
          {
            "x": 1987,
            "y": -182
          },
          {
            "x": 1988,
            "y": -16
          },
          {
            "x": 1989,
            "y": 105
          },
          {
            "x": 1990,
            "y": -10
          },
          {
            "x": 1991,
            "y": 77
          },
          {
            "x": 1992,
            "y": 15
          },
          {
            "x": 1993,
            "y": 204
          },
          {
            "x": 1994,
            "y": 279
          },
          {
            "x": 1995,
            "y": 301
          },
          {
            "x": 1996,
            "y": 386
          },
          {
            "x": 1997,
            "y": 629
          },
          {
            "x": 1998,
            "y": 500
          },
          {
            "x": 1999,
            "y": 744
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Connecticut",
        "data": [
          {
            "x": 1986,
            "y": 56
          },
          {
            "x": 1987,
            "y": -151
          },
          {
            "x": 1988,
            "y": 8
          },
          {
            "x": 1989,
            "y": -64
          },
          {
            "x": 1990,
            "y": 158
          },
          {
            "x": 1991,
            "y": -148
          },
          {
            "x": 1992,
            "y": -198
          },
          {
            "x": 1993,
            "y": 645
          },
          {
            "x": 1994,
            "y": 821
          },
          {
            "x": 1995,
            "y": 784
          },
          {
            "x": 1996,
            "y": 386
          },
          {
            "x": 1997,
            "y": 1273
          },
          {
            "x": 1998,
            "y": 1190
          },
          {
            "x": 1999,
            "y": 1412
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Delaware",
        "data": [
          {
            "x": 1986,
            "y": 38
          },
          {
            "x": 1987,
            "y": 11
          },
          {
            "x": 1988,
            "y": 50
          },
          {
            "x": 1989,
            "y": -12
          },
          {
            "x": 1990,
            "y": -161
          },
          {
            "x": 1991,
            "y": -87
          },
          {
            "x": 1992,
            "y": 12
          },
          {
            "x": 1993,
            "y": -47
          },
          {
            "x": 1994,
            "y": -22
          },
          {
            "x": 1995,
            "y": 79
          },
          {
            "x": 1996,
            "y": 186
          },
          {
            "x": 1997,
            "y": 173
          },
          {
            "x": 1998,
            "y": 104
          },
          {
            "x": 1999,
            "y": 932
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "District of Columbia",
        "data": [
          {
            "x": 1986,
            "y": -306
          },
          {
            "x": 1987,
            "y": -15
          },
          {
            "x": 1988,
            "y": 562
          },
          {
            "x": 1989,
            "y": 871
          },
          {
            "x": 1990,
            "y": -31
          },
          {
            "x": 1991,
            "y": -660
          },
          {
            "x": 1992,
            "y": -646
          },
          {
            "x": 1993,
            "y": -1342
          },
          {
            "x": 1994,
            "y": -1879
          },
          {
            "x": 1995,
            "y": -3690
          },
          {
            "x": 1996,
            "y": -4759
          },
          {
            "x": 1997,
            "y": -5519
          },
          {
            "x": 1998,
            "y": -6344
          },
          {
            "x": 1999,
            "y": -7660
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Florida",
        "data": [
          {
            "x": 1986,
            "y": 542
          },
          {
            "x": 1987,
            "y": 537
          },
          {
            "x": 1988,
            "y": 814
          },
          {
            "x": 1989,
            "y": 1656
          },
          {
            "x": 1990,
            "y": 1526
          },
          {
            "x": 1991,
            "y": 2668
          },
          {
            "x": 1992,
            "y": -280
          },
          {
            "x": 1993,
            "y": 619
          },
          {
            "x": 1994,
            "y": -8251
          },
          {
            "x": 1995,
            "y": -19952
          },
          {
            "x": 1996,
            "y": -20834
          },
          {
            "x": 1997,
            "y": -23036
          },
          {
            "x": 1998,
            "y": -23053
          },
          {
            "x": 1999,
            "y": -23375
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Georgia",
        "data": [
          {
            "x": 1986,
            "y": -631
          },
          {
            "x": 1987,
            "y": 175
          },
          {
            "x": 1988,
            "y": 86
          },
          {
            "x": 1989,
            "y": 495
          },
          {
            "x": 1990,
            "y": 90
          },
          {
            "x": 1991,
            "y": 388
          },
          {
            "x": 1992,
            "y": -62
          },
          {
            "x": 1993,
            "y": 260
          },
          {
            "x": 1994,
            "y": 1079
          },
          {
            "x": 1995,
            "y": -2572
          },
          {
            "x": 1996,
            "y": -2679
          },
          {
            "x": 1997,
            "y": -2640
          },
          {
            "x": 1998,
            "y": -1630
          },
          {
            "x": 1999,
            "y": 276
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Hawaii",
        "data": [
          {
            "x": 1986,
            "y": -277
          },
          {
            "x": 1987,
            "y": -279
          },
          {
            "x": 1988,
            "y": -358
          },
          {
            "x": 1989,
            "y": -466
          },
          {
            "x": 1990,
            "y": -464
          },
          {
            "x": 1991,
            "y": -519
          },
          {
            "x": 1992,
            "y": -516
          },
          {
            "x": 1993,
            "y": -520
          },
          {
            "x": 1994,
            "y": -573
          },
          {
            "x": 1995,
            "y": -607
          },
          {
            "x": 1996,
            "y": -635
          },
          {
            "x": 1997,
            "y": -625
          },
          {
            "x": 1998,
            "y": -550
          },
          {
            "x": 1999,
            "y": -516
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Idaho",
        "data": [
          {
            "x": 1986,
            "y": -36
          },
          {
            "x": 1987,
            "y": -49
          },
          {
            "x": 1988,
            "y": -51
          },
          {
            "x": 1989,
            "y": -62
          },
          {
            "x": 1990,
            "y": -60
          },
          {
            "x": 1991,
            "y": -56
          },
          {
            "x": 1992,
            "y": -72
          },
          {
            "x": 1993,
            "y": -55
          },
          {
            "x": 1994,
            "y": -77
          },
          {
            "x": 1995,
            "y": -85
          },
          {
            "x": 1996,
            "y": -97
          },
          {
            "x": 1997,
            "y": -94
          },
          {
            "x": 1998,
            "y": -114
          },
          {
            "x": 1999,
            "y": -112
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Illinois",
        "data": [
          {
            "x": 1986,
            "y": 294
          },
          {
            "x": 1987,
            "y": 196
          },
          {
            "x": 1988,
            "y": -252
          },
          {
            "x": 1989,
            "y": 205
          },
          {
            "x": 1990,
            "y": 67
          },
          {
            "x": 1991,
            "y": 655
          },
          {
            "x": 1992,
            "y": 137
          },
          {
            "x": 1993,
            "y": 1022
          },
          {
            "x": 1994,
            "y": -3528
          },
          {
            "x": 1995,
            "y": -11043
          },
          {
            "x": 1996,
            "y": -10718
          },
          {
            "x": 1997,
            "y": -11204
          },
          {
            "x": 1998,
            "y": -10411
          },
          {
            "x": 1999,
            "y": -10160
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Indiana",
        "data": [
          {
            "x": 1986,
            "y": 232
          },
          {
            "x": 1987,
            "y": 14
          },
          {
            "x": 1988,
            "y": -34
          },
          {
            "x": 1989,
            "y": 463
          },
          {
            "x": 1990,
            "y": 57
          },
          {
            "x": 1991,
            "y": -192
          },
          {
            "x": 1992,
            "y": -19
          },
          {
            "x": 1993,
            "y": -121
          },
          {
            "x": 1994,
            "y": -144
          },
          {
            "x": 1995,
            "y": 226
          },
          {
            "x": 1996,
            "y": 299
          },
          {
            "x": 1997,
            "y": 456
          },
          {
            "x": 1998,
            "y": 498
          },
          {
            "x": 1999,
            "y": 239
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Iowa",
        "data": [
          {
            "x": 1986,
            "y": -104
          },
          {
            "x": 1987,
            "y": -105
          },
          {
            "x": 1988,
            "y": -99
          },
          {
            "x": 1989,
            "y": -23
          },
          {
            "x": 1990,
            "y": 6
          },
          {
            "x": 1991,
            "y": 3
          },
          {
            "x": 1992,
            "y": 54
          },
          {
            "x": 1993,
            "y": 129
          },
          {
            "x": 1994,
            "y": 184
          },
          {
            "x": 1995,
            "y": 175
          },
          {
            "x": 1996,
            "y": 184
          },
          {
            "x": 1997,
            "y": 258
          },
          {
            "x": 1998,
            "y": 334
          },
          {
            "x": 1999,
            "y": 249
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Kansas",
        "data": [
          {
            "x": 1986,
            "y": 210
          },
          {
            "x": 1987,
            "y": 324
          },
          {
            "x": 1988,
            "y": 235
          },
          {
            "x": 1989,
            "y": -49
          },
          {
            "x": 1990,
            "y": -119
          },
          {
            "x": 1991,
            "y": -50
          },
          {
            "x": 1992,
            "y": -91
          },
          {
            "x": 1993,
            "y": -374
          },
          {
            "x": 1994,
            "y": -327
          },
          {
            "x": 1995,
            "y": -466
          },
          {
            "x": 1996,
            "y": -390
          },
          {
            "x": 1997,
            "y": -550
          },
          {
            "x": 1998,
            "y": -602
          },
          {
            "x": 1999,
            "y": -612
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Kentucky",
        "data": [
          {
            "x": 1986,
            "y": -119
          },
          {
            "x": 1987,
            "y": -163
          },
          {
            "x": 1988,
            "y": 46
          },
          {
            "x": 1989,
            "y": 43
          },
          {
            "x": 1990,
            "y": -30
          },
          {
            "x": 1991,
            "y": 93
          },
          {
            "x": 1992,
            "y": 5
          },
          {
            "x": 1993,
            "y": -97
          },
          {
            "x": 1994,
            "y": 234
          },
          {
            "x": 1995,
            "y": 294
          },
          {
            "x": 1996,
            "y": 473
          },
          {
            "x": 1997,
            "y": 1024
          },
          {
            "x": 1998,
            "y": 937
          },
          {
            "x": 1999,
            "y": 1071
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Louisiana",
        "data": [
          {
            "x": 1986,
            "y": 736
          },
          {
            "x": 1987,
            "y": 1147
          },
          {
            "x": 1988,
            "y": 1047
          },
          {
            "x": 1989,
            "y": 516
          },
          {
            "x": 1990,
            "y": -218
          },
          {
            "x": 1991,
            "y": 602
          },
          {
            "x": 1992,
            "y": -106
          },
          {
            "x": 1993,
            "y": -189
          },
          {
            "x": 1994,
            "y": -4236
          },
          {
            "x": 1995,
            "y": -10501
          },
          {
            "x": 1996,
            "y": -9931
          },
          {
            "x": 1997,
            "y": -9639
          },
          {
            "x": 1998,
            "y": -9077
          },
          {
            "x": 1999,
            "y": -9760
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Maine",
        "data": [
          {
            "x": 1986,
            "y": -52
          },
          {
            "x": 1987,
            "y": -49
          },
          {
            "x": 1988,
            "y": -53
          },
          {
            "x": 1989,
            "y": -57
          },
          {
            "x": 1990,
            "y": -47
          },
          {
            "x": 1991,
            "y": -40
          },
          {
            "x": 1992,
            "y": -56
          },
          {
            "x": 1993,
            "y": -55
          },
          {
            "x": 1994,
            "y": -85
          },
          {
            "x": 1995,
            "y": -103
          },
          {
            "x": 1996,
            "y": -99
          },
          {
            "x": 1997,
            "y": -108
          },
          {
            "x": 1998,
            "y": -121
          },
          {
            "x": 1999,
            "y": -129
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Maryland",
        "data": [
          {
            "x": 1986,
            "y": 1102
          },
          {
            "x": 1987,
            "y": 492
          },
          {
            "x": 1988,
            "y": 319
          },
          {
            "x": 1989,
            "y": 57
          },
          {
            "x": 1990,
            "y": 217
          },
          {
            "x": 1991,
            "y": -420
          },
          {
            "x": 1992,
            "y": -226
          },
          {
            "x": 1993,
            "y": -1127
          },
          {
            "x": 1994,
            "y": -2181
          },
          {
            "x": 1995,
            "y": -2799
          },
          {
            "x": 1996,
            "y": -2414
          },
          {
            "x": 1997,
            "y": -2858
          },
          {
            "x": 1998,
            "y": -3846
          },
          {
            "x": 1999,
            "y": -2148
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Massachusetts",
        "data": [
          {
            "x": 1986,
            "y": 17
          },
          {
            "x": 1987,
            "y": 137
          },
          {
            "x": 1988,
            "y": 18
          },
          {
            "x": 1989,
            "y": 61
          },
          {
            "x": 1990,
            "y": 3
          },
          {
            "x": 1991,
            "y": -123
          },
          {
            "x": 1992,
            "y": -30
          },
          {
            "x": 1993,
            "y": -732
          },
          {
            "x": 1994,
            "y": -977
          },
          {
            "x": 1995,
            "y": -1271
          },
          {
            "x": 1996,
            "y": -755
          },
          {
            "x": 1997,
            "y": -1376
          },
          {
            "x": 1998,
            "y": -1559
          },
          {
            "x": 1999,
            "y": -1988
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Michigan",
        "data": [
          {
            "x": 1986,
            "y": -1033
          },
          {
            "x": 1987,
            "y": 123
          },
          {
            "x": 1988,
            "y": 906
          },
          {
            "x": 1989,
            "y": 724
          },
          {
            "x": 1990,
            "y": 298
          },
          {
            "x": 1991,
            "y": -393
          },
          {
            "x": 1992,
            "y": -540
          },
          {
            "x": 1993,
            "y": -2584
          },
          {
            "x": 1994,
            "y": -3943
          },
          {
            "x": 1995,
            "y": -6540
          },
          {
            "x": 1996,
            "y": -6242
          },
          {
            "x": 1997,
            "y": -5825
          },
          {
            "x": 1998,
            "y": -5907
          },
          {
            "x": 1999,
            "y": -5276
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Minnesota",
        "data": [
          {
            "x": 1986,
            "y": -88
          },
          {
            "x": 1987,
            "y": -60
          },
          {
            "x": 1988,
            "y": -28
          },
          {
            "x": 1989,
            "y": -66
          },
          {
            "x": 1990,
            "y": -137
          },
          {
            "x": 1991,
            "y": -2
          },
          {
            "x": 1992,
            "y": 106
          },
          {
            "x": 1993,
            "y": 144
          },
          {
            "x": 1994,
            "y": 176
          },
          {
            "x": 1995,
            "y": 282
          },
          {
            "x": 1996,
            "y": 392
          },
          {
            "x": 1997,
            "y": 291
          },
          {
            "x": 1998,
            "y": 374
          },
          {
            "x": 1999,
            "y": 460
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Mississippi",
        "data": [
          {
            "x": 1986,
            "y": 127
          },
          {
            "x": 1987,
            "y": -91
          },
          {
            "x": 1988,
            "y": -9
          },
          {
            "x": 1989,
            "y": 1
          },
          {
            "x": 1990,
            "y": 60
          },
          {
            "x": 1991,
            "y": -102
          },
          {
            "x": 1992,
            "y": -605
          },
          {
            "x": 1993,
            "y": -219
          },
          {
            "x": 1994,
            "y": 17
          },
          {
            "x": 1995,
            "y": 764
          },
          {
            "x": 1996,
            "y": 1144
          },
          {
            "x": 1997,
            "y": 700
          },
          {
            "x": 1998,
            "y": 1499
          },
          {
            "x": 1999,
            "y": 2416
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Missouri",
        "data": [
          {
            "x": 1986,
            "y": -786
          },
          {
            "x": 1987,
            "y": -696
          },
          {
            "x": 1988,
            "y": 33
          },
          {
            "x": 1989,
            "y": 242
          },
          {
            "x": 1990,
            "y": 51
          },
          {
            "x": 1991,
            "y": 69
          },
          {
            "x": 1992,
            "y": -55
          },
          {
            "x": 1993,
            "y": -555
          },
          {
            "x": 1994,
            "y": 155
          },
          {
            "x": 1995,
            "y": -866
          },
          {
            "x": 1996,
            "y": -94
          },
          {
            "x": 1997,
            "y": 178
          },
          {
            "x": 1998,
            "y": 162
          },
          {
            "x": 1999,
            "y": 631
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Montana",
        "data": [
          {
            "x": 1986,
            "y": -86
          },
          {
            "x": 1987,
            "y": -97
          },
          {
            "x": 1988,
            "y": -113
          },
          {
            "x": 1989,
            "y": -118
          },
          {
            "x": 1990,
            "y": -118
          },
          {
            "x": 1991,
            "y": -122
          },
          {
            "x": 1992,
            "y": -136
          },
          {
            "x": 1993,
            "y": -146
          },
          {
            "x": 1994,
            "y": -161
          },
          {
            "x": 1995,
            "y": -191
          },
          {
            "x": 1996,
            "y": -196
          },
          {
            "x": 1997,
            "y": -218
          },
          {
            "x": 1998,
            "y": -219
          },
          {
            "x": 1999,
            "y": -233
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Nebraska",
        "data": [
          {
            "x": 1986,
            "y": -21
          },
          {
            "x": 1987,
            "y": -54
          },
          {
            "x": 1988,
            "y": -36
          },
          {
            "x": 1989,
            "y": 77
          },
          {
            "x": 1990,
            "y": 48
          },
          {
            "x": 1991,
            "y": 38
          },
          {
            "x": 1992,
            "y": 7
          },
          {
            "x": 1993,
            "y": 1
          },
          {
            "x": 1994,
            "y": -78
          },
          {
            "x": 1995,
            "y": -78
          },
          {
            "x": 1996,
            "y": -105
          },
          {
            "x": 1997,
            "y": -134
          },
          {
            "x": 1998,
            "y": -178
          },
          {
            "x": 1999,
            "y": -161
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Nevada",
        "data": [
          {
            "x": 1986,
            "y": 267
          },
          {
            "x": 1987,
            "y": 79
          },
          {
            "x": 1988,
            "y": 92
          },
          {
            "x": 1989,
            "y": -149
          },
          {
            "x": 1990,
            "y": 17
          },
          {
            "x": 1991,
            "y": -26
          },
          {
            "x": 1992,
            "y": -59
          },
          {
            "x": 1993,
            "y": 5
          },
          {
            "x": 1994,
            "y": 99
          },
          {
            "x": 1995,
            "y": 291
          },
          {
            "x": 1996,
            "y": 506
          },
          {
            "x": 1997,
            "y": 541
          },
          {
            "x": 1998,
            "y": 666
          },
          {
            "x": 1999,
            "y": 829
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "New Hampshire",
        "data": [
          {
            "x": 1986,
            "y": -758
          },
          {
            "x": 1987,
            "y": -725
          },
          {
            "x": 1988,
            "y": -819
          },
          {
            "x": 1989,
            "y": -763
          },
          {
            "x": 1990,
            "y": -860
          },
          {
            "x": 1991,
            "y": -860
          },
          {
            "x": 1992,
            "y": -893
          },
          {
            "x": 1993,
            "y": -951
          },
          {
            "x": 1994,
            "y": -1029
          },
          {
            "x": 1995,
            "y": -1055
          },
          {
            "x": 1996,
            "y": -1170
          },
          {
            "x": 1997,
            "y": -1219
          },
          {
            "x": 1998,
            "y": -1368
          },
          {
            "x": 1999,
            "y": -1385
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "New Jersey",
        "data": [
          {
            "x": 1986,
            "y": -666
          },
          {
            "x": 1987,
            "y": 142
          },
          {
            "x": 1988,
            "y": -27
          },
          {
            "x": 1989,
            "y": 332
          },
          {
            "x": 1990,
            "y": 164
          },
          {
            "x": 1991,
            "y": 778
          },
          {
            "x": 1992,
            "y": 49
          },
          {
            "x": 1993,
            "y": -558
          },
          {
            "x": 1994,
            "y": -1114
          },
          {
            "x": 1995,
            "y": -903
          },
          {
            "x": 1996,
            "y": -353
          },
          {
            "x": 1997,
            "y": -351
          },
          {
            "x": 1998,
            "y": 567
          },
          {
            "x": 1999,
            "y": 114
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "New Mexico",
        "data": [
          {
            "x": 1986,
            "y": -351
          },
          {
            "x": 1987,
            "y": -315
          },
          {
            "x": 1988,
            "y": -324
          },
          {
            "x": 1989,
            "y": -339
          },
          {
            "x": 1990,
            "y": -400
          },
          {
            "x": 1991,
            "y": -431
          },
          {
            "x": 1992,
            "y": -411
          },
          {
            "x": 1993,
            "y": -480
          },
          {
            "x": 1994,
            "y": -529
          },
          {
            "x": 1995,
            "y": -659
          },
          {
            "x": 1996,
            "y": -705
          },
          {
            "x": 1997,
            "y": -752
          },
          {
            "x": 1998,
            "y": -932
          },
          {
            "x": 1999,
            "y": -1010
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "North Carolina",
        "data": [
          {
            "x": 1986,
            "y": 1617
          },
          {
            "x": 1987,
            "y": 739
          },
          {
            "x": 1988,
            "y": 511
          },
          {
            "x": 1989,
            "y": -209
          },
          {
            "x": 1990,
            "y": -162
          },
          {
            "x": 1991,
            "y": -546
          },
          {
            "x": 1992,
            "y": -135
          },
          {
            "x": 1993,
            "y": -54
          },
          {
            "x": 1994,
            "y": -974
          },
          {
            "x": 1995,
            "y": 1921
          },
          {
            "x": 1996,
            "y": 2355
          },
          {
            "x": 1997,
            "y": 2205
          },
          {
            "x": 1998,
            "y": 1212
          },
          {
            "x": 1999,
            "y": -440
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "North Dakota",
        "data": [
          {
            "x": 1986,
            "y": -26
          },
          {
            "x": 1987,
            "y": -29
          },
          {
            "x": 1988,
            "y": -28
          },
          {
            "x": 1989,
            "y": -38
          },
          {
            "x": 1990,
            "y": -41
          },
          {
            "x": 1991,
            "y": -39
          },
          {
            "x": 1992,
            "y": -44
          },
          {
            "x": 1993,
            "y": -41
          },
          {
            "x": 1994,
            "y": -54
          },
          {
            "x": 1995,
            "y": -55
          },
          {
            "x": 1996,
            "y": -63
          },
          {
            "x": 1997,
            "y": -78
          },
          {
            "x": 1998,
            "y": -73
          },
          {
            "x": 1999,
            "y": -77
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Ohio",
        "data": [
          {
            "x": 1986,
            "y": 94
          },
          {
            "x": 1987,
            "y": -503
          },
          {
            "x": 1988,
            "y": -234
          },
          {
            "x": 1989,
            "y": 247
          },
          {
            "x": 1990,
            "y": -281
          },
          {
            "x": 1991,
            "y": 1004
          },
          {
            "x": 1992,
            "y": 483
          },
          {
            "x": 1993,
            "y": 1288
          },
          {
            "x": 1994,
            "y": -1973
          },
          {
            "x": 1995,
            "y": -4332
          },
          {
            "x": 1996,
            "y": -4040
          },
          {
            "x": 1997,
            "y": -4367
          },
          {
            "x": 1998,
            "y": -5280
          },
          {
            "x": 1999,
            "y": -6056
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Oklahoma",
        "data": [
          {
            "x": 1986,
            "y": 32
          },
          {
            "x": 1987,
            "y": -12
          },
          {
            "x": 1988,
            "y": 29
          },
          {
            "x": 1989,
            "y": -11
          },
          {
            "x": 1990,
            "y": -29
          },
          {
            "x": 1991,
            "y": -138
          },
          {
            "x": 1992,
            "y": 11
          },
          {
            "x": 1993,
            "y": 182
          },
          {
            "x": 1994,
            "y": -472
          },
          {
            "x": 1995,
            "y": -1074
          },
          {
            "x": 1996,
            "y": -1019
          },
          {
            "x": 1997,
            "y": -1462
          },
          {
            "x": 1998,
            "y": -1570
          },
          {
            "x": 1999,
            "y": -1716
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Oregon",
        "data": [
          {
            "x": 1986,
            "y": 9
          },
          {
            "x": 1987,
            "y": 142
          },
          {
            "x": 1988,
            "y": 60
          },
          {
            "x": 1989,
            "y": 145
          },
          {
            "x": 1990,
            "y": 45
          },
          {
            "x": 1991,
            "y": -21
          },
          {
            "x": 1992,
            "y": -70
          },
          {
            "x": 1993,
            "y": -134
          },
          {
            "x": 1994,
            "y": -225
          },
          {
            "x": 1995,
            "y": -174
          },
          {
            "x": 1996,
            "y": -227
          },
          {
            "x": 1997,
            "y": -303
          },
          {
            "x": 1998,
            "y": -195
          },
          {
            "x": 1999,
            "y": -180
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Pennsylvania",
        "data": [
          {
            "x": 1986,
            "y": 738
          },
          {
            "x": 1987,
            "y": 665
          },
          {
            "x": 1988,
            "y": 417
          },
          {
            "x": 1989,
            "y": 72
          },
          {
            "x": 1990,
            "y": -138
          },
          {
            "x": 1991,
            "y": -345
          },
          {
            "x": 1992,
            "y": -103
          },
          {
            "x": 1993,
            "y": -109
          },
          {
            "x": 1994,
            "y": 3063
          },
          {
            "x": 1995,
            "y": 2085
          },
          {
            "x": 1996,
            "y": 2838
          },
          {
            "x": 1997,
            "y": 2336
          },
          {
            "x": 1998,
            "y": 2626
          },
          {
            "x": 1999,
            "y": 2699
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Rhode Island",
        "data": [
          {
            "x": 1986,
            "y": -157
          },
          {
            "x": 1987,
            "y": -157
          },
          {
            "x": 1988,
            "y": 0
          },
          {
            "x": 1989,
            "y": 69
          },
          {
            "x": 1990,
            "y": -45
          },
          {
            "x": 1991,
            "y": -9
          },
          {
            "x": 1992,
            "y": -74
          },
          {
            "x": 1993,
            "y": -145
          },
          {
            "x": 1994,
            "y": -107
          },
          {
            "x": 1995,
            "y": -165
          },
          {
            "x": 1996,
            "y": -92
          },
          {
            "x": 1997,
            "y": -150
          },
          {
            "x": 1998,
            "y": -408
          },
          {
            "x": 1999,
            "y": -539
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "South Carolina",
        "data": [
          {
            "x": 1986,
            "y": -892
          },
          {
            "x": 1987,
            "y": -820
          },
          {
            "x": 1988,
            "y": -339
          },
          {
            "x": 1989,
            "y": -182
          },
          {
            "x": 1990,
            "y": 242
          },
          {
            "x": 1991,
            "y": 297
          },
          {
            "x": 1992,
            "y": 46
          },
          {
            "x": 1993,
            "y": -858
          },
          {
            "x": 1994,
            "y": -2749
          },
          {
            "x": 1995,
            "y": -3044
          },
          {
            "x": 1996,
            "y": -2979
          },
          {
            "x": 1997,
            "y": -3100
          },
          {
            "x": 1998,
            "y": -3849
          },
          {
            "x": 1999,
            "y": -5382
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "South Dakota",
        "data": [
          {
            "x": 1986,
            "y": -130
          },
          {
            "x": 1987,
            "y": -148
          },
          {
            "x": 1988,
            "y": -161
          },
          {
            "x": 1989,
            "y": -185
          },
          {
            "x": 1990,
            "y": -178
          },
          {
            "x": 1991,
            "y": -194
          },
          {
            "x": 1992,
            "y": -200
          },
          {
            "x": 1993,
            "y": -205
          },
          {
            "x": 1994,
            "y": -214
          },
          {
            "x": 1995,
            "y": -232
          },
          {
            "x": 1996,
            "y": -238
          },
          {
            "x": 1997,
            "y": -222
          },
          {
            "x": 1998,
            "y": -230
          },
          {
            "x": 1999,
            "y": -252
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Tennessee",
        "data": [
          {
            "x": 1986,
            "y": 157
          },
          {
            "x": 1987,
            "y": -83
          },
          {
            "x": 1988,
            "y": -319
          },
          {
            "x": 1989,
            "y": 479
          },
          {
            "x": 1990,
            "y": -9
          },
          {
            "x": 1991,
            "y": 254
          },
          {
            "x": 1992,
            "y": 188
          },
          {
            "x": 1993,
            "y": 236
          },
          {
            "x": 1994,
            "y": 788
          },
          {
            "x": 1995,
            "y": 1093
          },
          {
            "x": 1996,
            "y": 1223
          },
          {
            "x": 1997,
            "y": 1282
          },
          {
            "x": 1998,
            "y": 1517
          },
          {
            "x": 1999,
            "y": 5023
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Utah",
        "data": [
          {
            "x": 1986,
            "y": -380
          },
          {
            "x": 1987,
            "y": -410
          },
          {
            "x": 1988,
            "y": -459
          },
          {
            "x": 1989,
            "y": -536
          },
          {
            "x": 1990,
            "y": -599
          },
          {
            "x": 1991,
            "y": -674
          },
          {
            "x": 1992,
            "y": -762
          },
          {
            "x": 1993,
            "y": -886
          },
          {
            "x": 1994,
            "y": -1012
          },
          {
            "x": 1995,
            "y": -1078
          },
          {
            "x": 1996,
            "y": -1140
          },
          {
            "x": 1997,
            "y": -1244
          },
          {
            "x": 1998,
            "y": -1340
          },
          {
            "x": 1999,
            "y": -1230
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Vermont",
        "data": [
          {
            "x": 1986,
            "y": -48
          },
          {
            "x": 1987,
            "y": -52
          },
          {
            "x": 1988,
            "y": -60
          },
          {
            "x": 1989,
            "y": -70
          },
          {
            "x": 1990,
            "y": -77
          },
          {
            "x": 1991,
            "y": -85
          },
          {
            "x": 1992,
            "y": -92
          },
          {
            "x": 1993,
            "y": -92
          },
          {
            "x": 1994,
            "y": -78
          },
          {
            "x": 1995,
            "y": -106
          },
          {
            "x": 1996,
            "y": -114
          },
          {
            "x": 1997,
            "y": -98
          },
          {
            "x": 1998,
            "y": -91
          },
          {
            "x": 1999,
            "y": -89
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Virginia",
        "data": [
          {
            "x": 1986,
            "y": -218
          },
          {
            "x": 1987,
            "y": -102
          },
          {
            "x": 1988,
            "y": -165
          },
          {
            "x": 1989,
            "y": -148
          },
          {
            "x": 1990,
            "y": -229
          },
          {
            "x": 1991,
            "y": 165
          },
          {
            "x": 1992,
            "y": 268
          },
          {
            "x": 1993,
            "y": 865
          },
          {
            "x": 1994,
            "y": 3193
          },
          {
            "x": 1995,
            "y": 3025
          },
          {
            "x": 1996,
            "y": 2598
          },
          {
            "x": 1997,
            "y": 2696
          },
          {
            "x": 1998,
            "y": 3641
          },
          {
            "x": 1999,
            "y": 950
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Washington",
        "data": [
          {
            "x": 1986,
            "y": 192
          },
          {
            "x": 1987,
            "y": 74
          },
          {
            "x": 1988,
            "y": -73
          },
          {
            "x": 1989,
            "y": -253
          },
          {
            "x": 1990,
            "y": -156
          },
          {
            "x": 1991,
            "y": -43
          },
          {
            "x": 1992,
            "y": 147
          },
          {
            "x": 1993,
            "y": 111
          },
          {
            "x": 1994,
            "y": 152
          },
          {
            "x": 1995,
            "y": 253
          },
          {
            "x": 1996,
            "y": 316
          },
          {
            "x": 1997,
            "y": 261
          },
          {
            "x": 1998,
            "y": 572
          },
          {
            "x": 1999,
            "y": 699
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "West Virginia",
        "data": [
          {
            "x": 1986,
            "y": -191
          },
          {
            "x": 1987,
            "y": -240
          },
          {
            "x": 1988,
            "y": -310
          },
          {
            "x": 1989,
            "y": -362
          },
          {
            "x": 1990,
            "y": -375
          },
          {
            "x": 1991,
            "y": -435
          },
          {
            "x": 1992,
            "y": -465
          },
          {
            "x": 1993,
            "y": -485
          },
          {
            "x": 1994,
            "y": -561
          },
          {
            "x": 1995,
            "y": -513
          },
          {
            "x": 1996,
            "y": -591
          },
          {
            "x": 1997,
            "y": -627
          },
          {
            "x": 1998,
            "y": -592
          },
          {
            "x": 1999,
            "y": -637
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Wisconsin",
        "data": [
          {
            "x": 1986,
            "y": 141
          },
          {
            "x": 1987,
            "y": 199
          },
          {
            "x": 1988,
            "y": -44
          },
          {
            "x": 1989,
            "y": -257
          },
          {
            "x": 1990,
            "y": -175
          },
          {
            "x": 1991,
            "y": -255
          },
          {
            "x": 1992,
            "y": 140
          },
          {
            "x": 1993,
            "y": -19
          },
          {
            "x": 1994,
            "y": 225
          },
          {
            "x": 1995,
            "y": 534
          },
          {
            "x": 1996,
            "y": 1331
          },
          {
            "x": 1997,
            "y": 2481
          },
          {
            "x": 1998,
            "y": 3481
          },
          {
            "x": 1999,
            "y": 4455
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "Wyoming",
        "data": [
          {
            "x": 1986,
            "y": -66
          },
          {
            "x": 1987,
            "y": -72
          },
          {
            "x": 1988,
            "y": -65
          },
          {
            "x": 1989,
            "y": -84
          },
          {
            "x": 1990,
            "y": -86
          },
          {
            "x": 1991,
            "y": -95
          },
          {
            "x": 1992,
            "y": -105
          },
          {
            "x": 1993,
            "y": -101
          },
          {
            "x": 1994,
            "y": -131
          },
          {
            "x": 1995,
            "y": -141
          },
          {
            "x": 1996,
            "y": -153
          },
          {
            "x": 1997,
            "y": -170
          },
          {
            "x": 1998,
            "y": -170
          },
          {
            "x": 1999,
            "y": -172
          }
        ],
        "borderColor": "rgba(140,140,140,0.30)",
        "backgroundColor": "rgba(140,140,140,0.30)",
        "borderWidth": 1,
        "pointRadius": 0,
        "tension": 0.15,
        "fill": false,
        "order": 50
      },
      {
        "label": "1993: prison expansion begins",
        "data": [
          {
            "x": 1993,
            "y": -30000
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
        "min": -30000,
        "max": 30000,
        "title": {
          "display": true,
          "text": "Prisoners (Gap vs Synthetic)"
        }
      }
    },
    "plugins": {
      "legend": {
        "display": false,
        "position": "bottom"
      },
      "tooltip": {
        "enabled": false
      }
    }
  }
{{< /chart >}}

</div>

The Texas line sits at the edge of the placebo distribution after 1993, which is the visual form of the test. The numeric form is the mean squared prediction error ratio. For any unit, define the pre- and post-treatment mean squared prediction error as the average squared gap in each window:

\[ \text{MSPE}_{\text{pre}} = \frac{1}{T_{\text{pre}}} \sum_{t \le 1993} \big( Y_t - \hat{Y}_t \big)^2, \qquad \text{MSPE}_{\text{post}} = \frac{1}{T_{\text{post}}} \sum_{t > 1993} \big( Y_t - \hat{Y}_t \big)^2 \]

where:
- MSPE is mean squared prediction error: the average squared gap between a unit and its synthetic
- \(\text{MSPE}_{\text{pre}}\) measures fit before 1993; \(\text{MSPE}_{\text{post}}\) measures it after
- \(Y_t\) is the observed count in year \(t\) and \(\hat{Y}_t\) is the synthetic count
- \(T_{\text{pre}}\) and \(T_{\text{post}}\) are the number of years in each window, so each term is an average


The test statistic is the ratio of the two:

\[ r = \dfrac{\text{MSPE}_{\text{post}}}{\text{MSPE}_{\text{pre}}} \]

where:
- \(r\) is the test statistic: how much worse a unit fits after 1993 than before
- A large \(r\) means a tight pre-period fit followed by a big post-period departure, the signature of a real effect
- Dividing by the pre-period error is what keeps the statistic fair: a unit that never fit well cannot post a high ratio just by being noisy


A large \(r\) means a unit that fit well before treatment and badly after, which is the signature of a treatment effect rather than a poor synthetic. Dividing by the pre-period error is what makes the statistic fair across units: a state whose synthetic never fit well has a large denominator and cannot post a high ratio just by being noisy. Ranking every unit by \(r\) places the real treated state in the placebo distribution.

## What the Ranking Says

Texas posts the largest MSPE ratio of all forty-nine units for both outcomes. Its Black-male ratio ranks first of forty-nine, and so does its white-male ratio.

The permutation p-value formalizes what "rank first" buys. With \(J+1\) units in the pool (the treated unit plus \(J\) donors), the p-value is the share of units whose MSPE ratio is at least as large as the treated unit's:

\[ p = \dfrac{1}{J+1} \sum_{j=1}^{J+1} \mathbb{1}\big( r_j \ge r_{\text{TX}} \big) \]

where:
- \(p\) is the permutation p-value: the share of all units whose MSPE ratio is at least as large as Texas's
- \(J+1\) is the total number of units (Texas plus \(J\) donors), here 49
- \(r_j\) is unit \(j\)'s MSPE ratio and \(r_{\text{TX}}\) is Texas's
- \(\mathbb{1}(\cdot)\) counts 1 when the condition holds and 0 otherwise; when Texas ranks first the sum is 1, giving \(p = 1/49\)


where \(\mathbb{1}(\cdot)\) is the indicator function and \(r_{\text{TX}}\) is Texas's ratio. When Texas has the single largest ratio, the sum equals one (only Texas satisfies the inequality), so \(p = 1/(J+1) = 1/49 \approx 0.02\). That is the smallest p-value the placebo distribution can produce at this pool size: with forty-nine units, no result can be more extreme than rank one, and both outcomes reach it.

This is the result the framing has to respect. On the question of whether an effect exists, there is no asymmetry: both the Black-male and the white-male effects are at the extreme of their placebo distributions, both as unlikely to be chance as the test can register. The asymmetry is entirely in magnitude, where the Black-male effect runs about a fifth larger proportionally and about half again larger in people. The data supports "both effects are real, and the Black-male effect is larger," and it does not support "the effect is real for Black men and absent for white men."

## How Much the Specification Matters

A fair objection to the specification ladder is that choosing "the richest spec that solves" could, in principle, be a way to land on a preferred answer. The defense is to show the answer barely moves as the specification changes. Refitting the post-1993 proportional gap on every rung of the ladder, from the full seven-covariate fit down to a bare specification matching only on outcome lags, gives this:

| Rung | Specification | Black Gap | White Gap |
|------|---------------|-----------|-----------|
| 1 | 7 Covariates, 3 Lags (Chosen) | 66% | 55% |
| 2 | 7 Covariates, 1 Lag | 67% | 56% |
| 3 | 4 Covariates, 2 Lags | 66% | 55% |
| 4 | 3 Covariates, 1 Lag | 67% | 55% |
| 5 | Lags Only, 3 Lags | 66% | 59% |
| 6 | Lags Only, 2 Lags | 65% | 51% |

The Black-male gap holds between 65 and 67 percent across every rung. The white-male gap is slightly more sensitive, ranging from 51 to 59 percent, but it never collapses toward zero and never approaches the Black-male figure. The chosen specification is not a lucky draw; it sits in the middle of a tight band. The unequal-burden finding survives the choice of predictors.

## What This Design Can and Cannot Establish

Every analytical claim has limits worth naming, and synthetic control has specific ones.

**The pre-period is short, but the pre-fit is tight.** The weights are fit on eight years, 1986 to 1993. A skeptic might worry that Texas ranks first only because its post-period error is large, not because its pre-fit is good, since a unit that was always a poor match would post a high ratio for the wrong reason. The pre-period MSPE rules that out. Texas's pre-treatment fit error sits at the 4th percentile of the donor pool for Black men and the 19th for white men, meaning the synthetic tracks Texas more tightly before 1993 than almost every placebo does for its own state. The rank-1 result is driven by a genuinely close pre-fit followed by a real post-1993 departure, not by a loose match inflating the ratio. The white-male pre-fit, at the 19th percentile, is looser than the Black-male fit, but the test design absorbs this: because the ratio divides post-period error by pre-period error, a looser pre-fit raises the denominator and works against a high ratio, not for it. That white still ranks first of forty-nine despite the looser pre-fit is the test confirming the effect rather than an artifact of the fit. Eight years is still a short pre-period, and a longer one would sharpen the counterfactual further, but the fit it produces is among the tightest in the pool.

**This is an association with a credible counterfactual, not a randomized experiment.** Synthetic control constructs the most defensible available comparison and tests it against placebos, which is far stronger than a raw before-and-after. It is not assignment by lottery. The honest verb throughout is that the expansion is "associated with" the estimated increase, and the placebo ranking is the evidence that the association is unlikely to be noise, not proof of the mechanism that produced it.

**The estimate captures the expansion together with anything else that hit Texas in 1993 and nothing else.** Synthetic control attributes the post-1993 gap to the treatment, but it cannot separate the capacity expansion from any other Texas-specific shock that arrived in the same window. The expansion is the largest and best-documented candidate, which is why it carries the attribution, but the design measures the net departure from the counterfactual, not the expansion in isolation.

**The mechanism behind the unequal burden is outside the data.** The estimates establish that the increase fell more heavily on Black men. They do not explain why a race-neutral capacity increase produced a race-uneven result. That question, how supply interacts with the charging, sentencing, and parole decisions that actually fill cells, is real and important and lives beyond what these counts can answer. Naming it is part of the result; resolving it is not something this design can do.

**The racial categories are the source data's, with its limitations.** "Black" and "white" here are the classifications as recorded in the underlying Bureau of Justice Statistics prisoner data, not categories this analysis defined. They carry that data's limitations. The counts do not resolve Hispanic ethnicity, which BJS tracked separately and inconsistently across this period, so a prisoner counted as Black or white may also be Hispanic; and "male" reflects the sex recorded in the administrative data. The analysis can only measure the categories the source actually recorded, and the unequal-burden finding is a statement about those recorded categories, not about race as a fuller social reality.

The full fit, including the predictor set, the donor pool, and the figure generation, is reproducible: every number in this case study comes from fitting the documented specification against the `texas` panel, and anyone fitting the same specification gets the same estimates, or the case study fails its own reproducibility standard.


## Sources

The method originates with Abadie, Diamond, and Hainmueller (2010), "Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program," *Journal of the American Statistical Association* 105 (490): 493 to 505. The estimator and its placebo-permutation inference both follow that paper.

The Texas prison-capacity data is the `texas` panel from Scott Cunningham's *Causal Inference: The Mixtape* (Yale University Press, 2021), available online at [mixtape.scunning.com](https://mixtape.scunning.com/). The dataset is distributed in R through the [`causaldata`](https://cran.r-project.org/package=causaldata) package, which is how this analysis loads it.

The fit uses the [`tidysynth`](https://cran.r-project.org/package=tidysynth) package (Dunford), a tidyverse-style interface to the synthetic control estimator.
