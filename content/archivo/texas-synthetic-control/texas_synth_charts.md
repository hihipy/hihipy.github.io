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

