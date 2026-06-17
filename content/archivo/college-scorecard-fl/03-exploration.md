---
title: "Exploration"
weight: 30
description: "First-pass orientation queries to see what the data says about Florida four-year institutions. Counts by sector and year, top institutions by enrollment, cost trajectories, completion rate distributions, and the closure wave forensics."
summary: "First-pass queries to orient the analysis"
tags: ["datasette", "exploratory-analysis", "sql", "sqlite"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< lead >}}
Six queries that cover the obvious dimensions: sector, year, institution, cost, completion, and the closure wave.
{{< /lead >}}

## At a Glance

The schema phase produced a queryable database with three tables and known invariants. The natural first move is breadth before depth: run a handful of queries that cover the obvious dimensions (sector, year, institution, cost, completion, programs) without yet reaching for window functions or CTEs. See what the data says at a glance, then decide which questions are worth following further.

This is the exploration phase the [case study philosophy](/biblioteca/) describes: not the analysis, but the orientation. Findings live in the [next phase](/archivo/college-scorecard-fl/04-findings/). The six queries below are the act of getting bearings, the moments of "what does this dataset actually contain" that shape every deeper question that comes later.

Every SQL block in this phase has a Datasette Lite link below it so the reader can run the query directly in the browser against the same database, no setup required. The expected output shown alongside each query is the actual output from the live database: anyone running the query gets the same numbers shown here, or this case study fails its own [reproducibility-is-the-floor](/biblioteca/#reproducibility-is-the-floor-review-is-the-ceiling) test.

## Counts By Sector And Year

The first query, and the one that anchors most of the later analysis. Florida four-year institution counts by sector across the twenty-one cohort years in the dataset:

```sql
-- Florida four-year institutions by sector and year.
-- Counts non-null annual_metrics rows: an institution is "in"
-- a year if and only if it has a row in annual_metrics for that
-- cohort_year. Sectors translated to display names with CASE WHEN.
SELECT
    am.cohort_year AS "Cohort Year",
    CASE i.sector
        WHEN 'public'            THEN 'Public'
        WHEN 'private_nonprofit' THEN 'Private Nonprofit'
        WHEN 'for_profit'        THEN 'For-Profit'
    END      AS "Sector",
    COUNT(*) AS "Institutions"
FROM annual_metrics am
JOIN institutions   i USING (unitid)
GROUP BY am.cohort_year, i.sector
ORDER BY am.cohort_year, i.sector;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++am.cohort_year+AS+%22Cohort+Year%22%2C%0A++++CASE+i.sector%0A++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++END++++++AS+%22Sector%22%2C%0A++++COUNT%28%2A%29+AS+%22Institutions%22%0AFROM+annual_metrics+am%0AJOIN+institutions+++i+USING+%28unitid%29%0AGROUP+BY+am.cohort_year%2C+i.sector%0AORDER+BY+am.cohort_year%2C+i.sector%3B)

Result (30 rows):

| Cohort Year | Sector | Institutions |
|---:|---|---:|
| 2014 | For-Profit | 26 |
| 2014 | Private Nonprofit | 58 |
| 2014 | Public | 14 |
| 2015 | For-Profit | 27 |
| 2015 | Private Nonprofit | 57 |
| 2015 | Public | 14 |
| 2016 | For-Profit | 28 |
| 2016 | Private Nonprofit | 55 |
| 2016 | Public | 14 |
| 2017 | For-Profit | 26 |
| 2017 | Private Nonprofit | 55 |
| 2017 | Public | 15 |
| 2018 | For-Profit | 21 |
| 2018 | Private Nonprofit | 54 |
| 2018 | Public | 15 |
| 2019 | For-Profit | 21 |
| 2019 | Private Nonprofit | 53 |
| 2019 | Public | 15 |
| 2020 | For-Profit | 23 |
| 2020 | Private Nonprofit | 52 |
| 2020 | Public | 13 |
| 2021 | For-Profit | 22 |
| 2021 | Private Nonprofit | 52 |
| 2021 | Public | 13 |
| 2022 | For-Profit | 23 |
| 2022 | Private Nonprofit | 53 |
| 2022 | Public | 13 |
| 2023 | For-Profit | 23 |
| 2023 | Private Nonprofit | 52 |
| 2023 | Public | 13 |

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">For-profit four-year institutions contracted from 28 in 2016 to 21 in 2018; public and private nonprofit counts barely moved.</p>
<p class="pgbd-case-chart-sub">Florida four-year institutions reporting by sector and cohort year, 2014-2023. Stacked to show total reporting institutions per year. The for-profit closure wave is visible as the shrinking red band in 2017-2019.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
  datasets: [
    {
      label: 'Public',
      data: [14, 14, 14, 15, 15, 15, 13, 13, 13, 13],
      backgroundColor: '#0969DA',
      borderColor: '#0969DA',
      borderWidth: 1,
    },
    {
      label: 'Private Nonprofit',
      data: [58, 57, 55, 55, 54, 53, 52, 52, 53, 52],
      backgroundColor: '#BF8700',
      borderColor: '#BF8700',
      borderWidth: 1,
    },
    {
      label: 'For-Profit',
      data: [26, 27, 28, 26, 21, 21, 23, 22, 23, 23],
      backgroundColor: '#CF222E',
      borderColor: '#CF222E',
      borderWidth: 1,
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'bottom' },
    tooltip: {
      callbacks: {
        label: function(context) {
          return context.dataset.label + ': ' + context.parsed.y + ' institutions';
        }
      }
    }
  },
  scales: {
    x: {
      stacked: true,
      title: { display: true, text: 'Cohort Year' }
    },
    y: {
      stacked: true,
      title: { display: true, text: 'Institutions Reporting' },
      beginAtZero: true
    }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The shape across sectors tells three different stories. The Public sector is essentially flat: 14 institutions in 2014, 13 in 2023. Florida Polytechnic University entered the data in 2017 (it was founded in 2012 and started awarding bachelor's degrees that year), accounting for the brief 15-institution count from 2017 through 2019; the drop to 13 in 2020 reflects the USF consolidation, when the University of South Florida-Sarasota-Manatee and University of South Florida-St Petersburg campuses were merged into the main USF UNITID. The State University System has twelve voting members today, and the database reflects that.

The Private Nonprofit sector contracted modestly: 58 institutions in 2014, 52 in 2023. The decline is gradual across the decade, not concentrated in any one year. Most of the institutions that disappeared were small religious colleges, seminaries, or single-program institutions that had brief appearances in the data and stopped reporting.

The For-Profit sector is the one with a real shape change. 26-28 institutions in 2014-2016, dropping to 21 by 2018, then partial recovery to 22-23 by the early 2020s. The dip is real and concentrated: nine for-profit four-year institutions reported in 2016 but did not appear in 2018. Some of these were the well-publicized for-profit chain collapses of 2016-2017 (Argosy University, Sanford-Brown). [Phase 04](/archivo/college-scorecard-fl/04-findings/) develops the closure-wave thread further.

## Who Does The Work

The second obvious cut: who actually does the educating?

```sql
-- Top 15 institutions by average undergraduate enrollment across
-- all reporting years. AVG(ugds) is computed only over rows where
-- ugds is non-null (the WHERE clause filters out privacy-suppressed
-- and unreported rows). Years Reporting is the count of non-null
-- ugds values per institution, so the reader can see whether the
-- average is across the full window or a partial window.
SELECT
    i.instnm                                                  AS "Institution",
    CASE i.sector
        WHEN 'public'            THEN 'Public'
        WHEN 'private_nonprofit' THEN 'Private Nonprofit'
        WHEN 'for_profit'        THEN 'For-Profit'
    END                                                       AS "Sector",
    printf('%,d', CAST(ROUND(AVG(am.ugds), 0) AS INTEGER))    AS "Avg UG Enrollment",
    COUNT(am.ugds)                                            AS "Years Reporting"
FROM annual_metrics am
JOIN institutions   i USING (unitid)
WHERE am.ugds IS NOT NULL
GROUP BY i.unitid, i.instnm, i.sector
ORDER BY AVG(am.ugds) DESC
LIMIT 15;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++i.instnm+AS+%22Institution%22%2C%0A++++CASE+i.sector%0A++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++END++++++++++++++++++++AS+%22Sector%22%2C%0A++++CAST%28ROUND%28AVG%28am.ugds%29%2C+0%29+AS+INTEGER%29+AS+%22Avg+UG+Enrollment%22%2C%0A++++COUNT%28am.ugds%29+++++++++AS+%22Years+Reporting%22%0AFROM+annual_metrics+am%0AJOIN+institutions+++i+USING+%28unitid%29%0AWHERE+am.ugds+IS+NOT+NULL%0AGROUP+BY+i.unitid%2C+i.instnm%2C+i.sector%0AORDER+BY+AVG%28am.ugds%29+DESC%0ALIMIT+15%3B)

Result:

| Institution | Sector | Avg UG Enrollment | Years Reporting |
|---|---|---:|---:|
| University of Central Florida | Public | 57,345 | 10 |
| Florida International University | Public | 40,507 | 10 |
| University of Florida | Public | 33,636 | 10 |
| University of South Florida | Public | 33,186 | 10 |
| Florida State University | Public | 32,516 | 10 |
| Florida Atlantic University | Public | 23,774 | 10 |
| Full Sail University | For-Profit | 20,579 | 10 |
| University of North Florida | Public | 13,957 | 10 |
| Florida Gulf Coast University | Public | 13,628 | 10 |
| University of Miami | Private Nonprofit | 11,265 | 10 |
| Embry-Riddle Aeronautical University-Worldwide | Private Nonprofit | 9,627 | 10 |
| University of West Florida | Public | 9,333 | 10 |
| Saint Leo University | Private Nonprofit | 8,668 | 10 |
| The University of Tampa | Private Nonprofit | 8,447 | 10 |
| Rasmussen University-Florida | For-Profit | 7,595 | 10 |

The top 15 is dominated by Public institutions. The five largest publics (UCF, FIU, UF, USF, FSU) account for roughly 197,000 average annual undergraduate enrollment, more than the total enrollment of every other Florida four-year institution combined. This concentration is structural: Florida's two-decade-old emphasis on growing the State University System has produced one of the largest public university systems in the country by enrollment, and UCF in particular has expanded so far past traditional flagship size that it consistently ranks among the largest universities in the United States.

The for-profit and private nonprofit sectors are visible too, but at much smaller scales. Full Sail University at #7 is the largest for-profit institution, an Orlando-based digital media school with an unusually concentrated curricular focus. Rasmussen University-Florida at #15 is the second-largest for-profit. The University of Miami at #10 is the largest private nonprofit. Most of the rest of the private nonprofit sector and most of the for-profit sector reports enrollments under 5,000.

## Cost Trajectories

The third orientation: how has the price changed?

```sql
-- Average in-state tuition by sector and cohort year. The query
-- filters out rows where tuitionfee_in is null (most for-profit
-- and private nonprofit institutions don't have an "in-state"
-- distinction; they charge one rate to all students). The Reporting
-- column shows how many institutions per sector contributed to
-- each year's average so the reader can spot small-N risks.
SELECT
    am.cohort_year                                                       AS "Cohort Year",
    CASE i.sector
        WHEN 'public'            THEN 'Public'
        WHEN 'private_nonprofit' THEN 'Private Nonprofit'
        WHEN 'for_profit'        THEN 'For-Profit'
    END                                                                  AS "Sector",
    printf('%,d', CAST(ROUND(AVG(am.tuitionfee_in), 0) AS INTEGER))      AS "Avg In-State Tuition",
    COUNT(am.tuitionfee_in)                                              AS "Reporting"
FROM annual_metrics am
JOIN institutions   i USING (unitid)
WHERE am.tuitionfee_in IS NOT NULL
GROUP BY am.cohort_year, i.sector
ORDER BY am.cohort_year, i.sector;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++am.cohort_year+AS+%22Cohort+Year%22%2C%0A++++CASE+i.sector%0A++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++END+++++++++++++++++++++++++++++AS+%22Sector%22%2C%0A++++CAST%28ROUND%28AVG%28am.tuitionfee_in%29%2C+0%29+AS+INTEGER%29+AS+%22Avg+In-State+Tuition%22%2C%0A++++COUNT%28am.tuitionfee_in%29+++++++++AS+%22Reporting%22%0AFROM+annual_metrics+am%0AJOIN+institutions+++i+USING+%28unitid%29%0AWHERE+am.tuitionfee_in+IS+NOT+NULL%0AGROUP+BY+am.cohort_year%2C+i.sector%0AORDER+BY+am.cohort_year%2C+i.sector%3B)

Result (30 rows):

| Cohort Year | Sector | Avg In-State Tuition | Reporting |
|---:|---|---:|---:|
| 2014 | For-Profit | $15,235 | 20 |
| 2014 | Private Nonprofit | $21,041 | 48 |
| 2014 | Public | $5,984 | 14 |
| 2015 | For-Profit | $14,225 | 20 |
| 2015 | Private Nonprofit | $21,413 | 47 |
| 2015 | Public | $5,994 | 14 |
| 2016 | For-Profit | $13,857 | 21 |
| 2016 | Private Nonprofit | $22,044 | 47 |
| 2016 | Public | $5,994 | 14 |
| 2017 | For-Profit | $14,002 | 20 |
| 2017 | Private Nonprofit | $22,928 | 46 |
| 2017 | Public | $5,867 | 15 |
| 2018 | For-Profit | $14,596 | 16 |
| 2018 | Private Nonprofit | $23,594 | 46 |
| 2018 | Public | $5,867 | 15 |
| 2019 | For-Profit | $15,215 | 16 |
| 2019 | Private Nonprofit | $23,743 | 48 |
| 2019 | Public | $5,870 | 15 |
| 2020 | For-Profit | $15,805 | 18 |
| 2020 | Private Nonprofit | $24,522 | 46 |
| 2020 | Public | $5,896 | 13 |
| 2021 | For-Profit | $16,545 | 19 |
| 2021 | Private Nonprofit | $25,057 | 47 |
| 2021 | Public | $5,896 | 13 |
| 2022 | For-Profit | $16,755 | 20 |
| 2022 | Private Nonprofit | $25,913 | 47 |
| 2022 | Public | $5,896 | 13 |
| 2023 | For-Profit | $18,519 | 20 |
| 2023 | Private Nonprofit | $27,012 | 47 |
| 2023 | Public | $5,896 | 13 |

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Public in-state tuition is nominally lower in 2023 than 2014; private nonprofit climbed 28 percent; for-profit was volatile.</p>
<p class="pgbd-case-chart-sub">Average published in-state tuition by sector and cohort year. The Public sector line ($5,984 to $5,896) is so flat it would compress to a single dot; private nonprofit climbs steadily; for-profit dips in 2015-2016 then rises sharply in the 2020s.</p>
{{< chart >}}
type: 'line',
data: {
  labels: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
  datasets: [
    {
      label: 'Public',
      data: [5984, 5994, 5994, 5867, 5867, 5870, 5896, 5896, 5896, 5896],
      borderColor: '#0969DA',
      backgroundColor: 'rgba(9, 105, 218, 0.10)',
      borderWidth: 2,
      fill: false,
      tension: 0.2,
      pointRadius: 2.5,
      pointHoverRadius: 5,
    },
    {
      label: 'Private Nonprofit',
      data: [21041, 21413, 22044, 22928, 23594, 23743, 24522, 25057, 25913, 27012],
      borderColor: '#BF8700',
      backgroundColor: 'rgba(191, 135, 0, 0.10)',
      borderWidth: 2,
      fill: false,
      tension: 0.2,
      pointRadius: 2.5,
      pointHoverRadius: 5,
    },
    {
      label: 'For-Profit',
      data: [15235, 14225, 13857, 14002, 14596, 15215, 15805, 16545, 16755, 18519],
      borderColor: '#CF222E',
      backgroundColor: 'rgba(207, 34, 46, 0.10)',
      borderWidth: 2,
      fill: false,
      tension: 0.2,
      pointRadius: 2.5,
      pointHoverRadius: 5,
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'bottom' },
    tooltip: {
      callbacks: {
        label: function(context) {
          return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
        }
      }
    }
  },
  scales: {
    x: {
      title: { display: true, text: 'Cohort Year' }
    },
    y: {
      title: { display: true, text: 'In-State Tuition (USD)' },
      beginAtZero: false,
      ticks: {
        callback: function(value) { return '$' + value.toLocaleString(); }
      }
    }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The Public sector tuition number is the headline finding. Florida public four-year in-state tuition was $5,984 in 2014 and $5,896 in 2023. Nominally lower in 2023 than in 2014. Inflation-adjusted, the decline is much steeper: a 2014 dollar is worth roughly $0.78 in 2023, so the real-cost reduction approaches twenty-five percent. This is not because Florida's public universities became cheaper to operate; it is because the state legislature has held the published tuition rate effectively flat while subsidizing operations through Florida Bright Futures scholarships and direct appropriations. The published in-state tuition is a policy instrument, not a market price.

Private Nonprofit tuition climbed from $21,041 to $27,012, up 28 percent in nominal terms. After inflation adjustment, real cost growth is roughly two percent over the decade, essentially flat. Private nonprofits raise tuition, but they also raise institutional aid: the published number is the sticker price, and most students pay less than sticker.

For-Profit tuition is more volatile. $15,235 in 2014, dipping below $14,000 in 2015-2017, then climbing to $18,519 in 2023. The 2015-2017 trough corresponds to the closure wave: as institutions closed, average tuition was dragged toward whatever the surviving institutions charged, and several of the surviving for-profits had below-average tuition. The 2023 average is roughly twenty percent higher than 2014 in nominal terms.

## Completion Rates

The fourth orientation: who actually finishes?

```sql
-- 150-percent-of-normal-time graduation rate distribution by
-- sector. AVG, MIN, MAX show the spread within each sector;
-- "Rows With Data" is the institution-year count that contributed.
-- The c150_4 column reports the fraction (0.0 to 1.0) of an
-- entering cohort that completed within six years (150% of the
-- four-year normal time); we multiply by 100 for display.
SELECT
    CASE i.sector
        WHEN 'public'            THEN 'Public'
        WHEN 'private_nonprofit' THEN 'Private Nonprofit'
        WHEN 'for_profit'        THEN 'For-Profit'
    END                            AS "Sector",
    ROUND(AVG(am.c150_4) * 100, 1) AS "Avg Completion %",
    ROUND(MIN(am.c150_4) * 100, 1) AS "Min %",
    ROUND(MAX(am.c150_4) * 100, 1) AS "Max %",
    COUNT(am.c150_4)               AS "Rows With Data"
FROM annual_metrics am
JOIN institutions   i USING (unitid)
WHERE am.c150_4 IS NOT NULL
GROUP BY i.sector
ORDER BY AVG(am.c150_4) DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++CASE+i.sector%0A++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++END++++++++++++++++++++++++++++AS+%22Sector%22%2C%0A++++ROUND%28AVG%28am.c150_4%29+%2A+100%2C+1%29+AS+%22Avg+Completion+%25%22%2C%0A++++ROUND%28MIN%28am.c150_4%29+%2A+100%2C+1%29+AS+%22Min+%25%22%2C%0A++++ROUND%28MAX%28am.c150_4%29+%2A+100%2C+1%29+AS+%22Max+%25%22%2C%0A++++COUNT%28am.c150_4%29+++++++++++++++AS+%22Rows+With+Data%22%0AFROM+annual_metrics+am%0AJOIN+institutions+++i+USING+%28unitid%29%0AWHERE+am.c150_4+IS+NOT+NULL%0AGROUP+BY+i.sector%0AORDER+BY+AVG%28am.c150_4%29+DESC%3B)

Result:

| Sector | Avg Completion % | Min % | Max % | Rows with Data |
|---|---:|---:|---:|---:|
| Public | 62.8 | 31.8 | 91.5 | 125 |
| Private Nonprofit | 47.6 | 0.0 | 100.0 | 439 |
| For-Profit | 39.7 | 0.0 | 100.0 | 166 |

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Public institutions average 63 percent completion; Private Nonprofit averages 48 percent; For-Profit averages 40 percent.</p>
<p class="pgbd-case-chart-sub">Average 150-percent-of-normal-time graduation rates by sector. The within-sector dispersion (visible in the result table's Min and Max columns and discussed in the prose below) is much wider than the averages suggest.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: ['Public', 'Private Nonprofit', 'For-Profit'],
  datasets: [
    {
      label: 'Average Completion %',
      data: [62.8, 47.6, 39.7],
      backgroundColor: ['#0969DA', '#BF8700', '#CF222E'],
      borderColor: ['#0969DA', '#BF8700', '#CF222E'],
      borderWidth: 1,
    }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: function(context) {
          return 'Average: ' + context.parsed.y.toFixed(1) + '%';
        }
      }
    }
  },
  scales: {
    x: { title: { display: true, text: 'Sector' } },
    y: {
      title: { display: true, text: 'Average Completion Rate (%)' },
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: function(value) { return value + '%'; }
      }
    }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

Three different shapes. Public completion rates average 62.8 percent and span 31.8 to 91.5 percent: a tight distribution by sector standards, with no institution reporting catastrophic failure (below 30 percent) and no institution reporting perfection (100 percent). Florida's public flagships drive the upper end, and regional comprehensives like the University of West Florida and Florida Gulf Coast cluster below the average.

Private Nonprofit completion averages 47.6 percent but ranges from 0 to 100 percent. The bimodal distribution reflects the sector's heterogeneity. The University of Miami, Stetson University, Rollins College, Eckerd College — all selective private four-years — report completion rates well above the sector average. Smaller religious colleges, single-discipline institutions, and online-heavy programs report lower rates, sometimes much lower. The 100 percent maximum is real: a few small institutions report cohorts where every entering student completed, usually because the cohort itself was small enough to make the percentage statistically fragile.

For-Profit completion averages 39.7 percent and shows the same 0-to-100 range. The for-profit sector's lower average is structural: many for-profit four-years serve adult learners, transfer students, and students who entered the institution to complete a credential rather than start one. Their completion rate measures something different from a traditional flagship's graduation rate. The for-profit closure wave further complicates the average: institutions that closed in 2016-2017 contributed final-year completion rates, often distorted by the closing process itself.

The 0.0 percent minimum visible in both the table and the chart deserves a closer look. A literal zero-percent completion rate could mean an institution where every entering cohort fails to graduate, but in this data it almost always means something else. The `c150_4` metric measures specifically first-time, full-time bachelor's-seeking students who completed within 150 percent of normal time (six years for a four-year program). At institutions whose student bodies are mostly part-time, mostly transfer students, or pursuing programs longer than four years, this metric can report zero even when the institution graduates students normally.

The evidence is in the c200_4 column (the 200 percent, eight-year, completion rate) for the same institution-years where c150_4 is zero. A query on these rows shows that students DO graduate, just outside the six-year window:

| Institution | Year | c150_4 (6yr) % | c200_4 (8yr) % |
|---|---:|---:|---:|
| Argosy University-Sarasota | 2016 | 0.0 | 66.7 |
| Polytechnic University of Puerto Rico-Miami | 2022 | 0.0 | 100.0 |
| Chamberlain University-Florida | 2021 | 0.0 | 50.0 |
| Polytechnic University of Puerto Rico-Orlando | 2019 | 0.0 | 50.0 |
| South Florida Bible College and Theological Seminary | 2018 | 0.0 | 33.3 |
| Albizu University-Miami | 2021 | 0.0 | 33.3 |
| Trinity College of Florida | 2023 | 0.0 | 31.3 |
| Polytechnic University of Puerto Rico-Miami | 2018 | 0.0 | 25.0 |

In every case shown, the institution reported zero completion at six years and meaningful completion at eight. Argosy University-Sarasota in 2016 reported a 66.7 percent eight-year completion rate while reporting zero six-year completion in the same year, an institution where most graduates take longer than six years to finish. Polytechnic University of Puerto Rico-Miami in 2022 reported 100 percent eight-year completion, every counted student graduated, just past the six-year window. The 0.0 percent c150_4 values are honest data, but they reflect measurement-artifact constraints (a metric calibrated for traditional first-time-full-time students applied to institutions with mostly non-traditional students), not institutional failure. [Phase 04](/archivo/college-scorecard-fl/04-findings/) filters out small-cohort and statistically-fragile rows where they would distort findings.

## The Closure Wave Forensics

The fifth orientation: what did the for-profit institutions that closed look like in their final reporting year?

```sql
-- For-profit institutions that disappeared from the data before
-- 2023, with their final reporting year's enrollment, completion
-- rate, and three-year cohort default rate. The JOIN matches each
-- institution to its annual_metrics row from its last_year_in_data,
-- giving a snapshot of the institution at the moment it stopped
-- reporting. NULL values in the snapshot reflect privacy
-- suppression or unreported metrics in that final year.
SELECT
    i.instnm                  AS "Institution",
    i.last_year_in_data       AS "Last Year",
    printf('%,d', am.ugds)    AS "Final Enrollment",
    ROUND(am.c150_4 * 100, 1) AS "Completion %",
    ROUND(am.cdr3 * 100, 1)   AS "Default Rate %"
FROM institutions       i
JOIN annual_metrics     am
    ON i.unitid = am.unitid
   AND i.last_year_in_data = am.cohort_year
WHERE i.sector = 'for_profit'
  AND i.last_year_in_data < 2023
ORDER BY i.last_year_in_data, i.instnm;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++i.instnm++++++++++++++++++AS+%22Institution%22%2C%0A++++i.last_year_in_data+++++++AS+%22Last+Year%22%2C%0A++++am.ugds+++++++++++++++++++AS+%22Final+Enrollment%22%2C%0A++++ROUND%28am.c150_4+%2A+100%2C+1%29+AS+%22Completion+%25%22%2C%0A++++ROUND%28am.cdr3+%2A+100%2C+1%29+++AS+%22Default+Rate+%25%22%0AFROM+institutions+++++++i%0AJOIN+annual_metrics+++++am%0A++++ON+i.unitid+%3D+am.unitid%0A+++AND+i.last_year_in_data+%3D+am.cohort_year%0AWHERE+i.sector+%3D+%27for_profit%27%0A++AND+i.last_year_in_data+%3C+2023%0AORDER+BY+i.last_year_in_data%2C+i.instnm%3B)

Result:

| Institution | Last Year | Final Enrollment | Completion % | Default Rate % |
|---|---:|---:|---:|---:|
| American InterContinental University-South Florida | 2014 | 46 | 40.5 | 17.7 |
| Gooding Institute of Nurse Anesthesia | 2014 | NULL | NULL | 0.0 |
| Digital Media Arts College | 2016 | 274 | 34.6 | 19.3 |
| Sanford-Brown College-Orlando | 2016 | 41 | 20.3 | 24.2 |
| Argosy University-Sarasota | 2017 | 95 | NULL | 15.5 |
| Argosy University-Tampa | 2017 | 129 | 50.0 | 15.5 |
| Sanford-Brown College-Online | 2017 | 25 | 25.2 | NULL |
| Sanford-Brown College-Tampa | 2017 | 8 | 28.6 | NULL |
| Wolford College | 2017 | NULL | NULL | 0.0 |
| Florida Coastal School of Law | 2020 | NULL | NULL | NULL |
| University of Phoenix-Florida | 2020 | 38 | 16.7 | 8.7 |
| AI Miami International University of Art and Design | 2022 | 866 | 14.7 | 0.0 |
| Atlantis University-Florida Palms University | 2022 | 107 | NULL | 0.0 |

Thirteen for-profit four-year institutions closed during the window. The names map to several recognizable closure events. The Sanford-Brown chain (parent: Career Education Corporation) closed multiple Florida campuses in 2016-2017 as the parent company exited the for-profit education business. The Argosy University locations closed in 2017 along with the rest of the Education Management Corporation network. Florida Coastal School of Law lost ABA accreditation in 2018 and stopped enrolling new students; it appears in the data through 2020. University of Phoenix-Florida appeared as a locally-reported branch separate from the main University of Phoenix UNITID and stopped reporting in 2020.

The final-year metrics paint a consistent picture: small enrollments at the closure point (most under 300 students), low completion rates where reported (under 40 percent in most cases), and elevated default rates (15-24 percent for several). The institutions that closed were not closing from a position of analytical strength. None of this is causation in the strict sense; the data shows correlation between closure and weak outcomes, not which one drove the other or whether external factors (regulatory pressure, parent company finances) drove both.

## Programs Across The Decade

The sixth orientation: what do Florida four-year institutions actually offer?

```sql
-- Top 10 most-offered programs across all Florida four-year
-- institutions. The grouping is on (CIPCODE, CREDLEV) since a
-- single CIP code can be offered at multiple credential levels
-- (bachelor's, master's, doctoral). "Institutions" counts the
-- distinct UNITIDs offering each program-credential combo;
-- "Program-Year Rows" counts the total reporting rows. A high
-- institutions count means broad availability across the state.
SELECT
    fos.cipdesc                AS "Program",
    fos.creddesc               AS "Credential",
    COUNT(DISTINCT fos.unitid) AS "Institutions",
    printf('%,d', COUNT(*))    AS "Program-Year Rows"
FROM field_of_study fos
GROUP BY fos.cipcode, fos.credlev, fos.cipdesc, fos.creddesc
ORDER BY COUNT(DISTINCT fos.unitid) DESC, COUNT(*) DESC
LIMIT 10;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++fos.cipdesc++++++++++++++++AS+%22Program%22%2C%0A++++fos.creddesc+++++++++++++++AS+%22Credential%22%2C%0A++++COUNT%28DISTINCT+fos.unitid%29+AS+%22Institutions%22%2C%0A++++COUNT%28%2A%29+++++++++++++++++++AS+%22Program-Year+Rows%22%0AFROM+field_of_study+fos%0AGROUP+BY+fos.cipcode%2C+fos.credlev%2C+fos.cipdesc%2C+fos.creddesc%0AORDER+BY+COUNT%28DISTINCT+fos.unitid%29+DESC%2C+COUNT%28%2A%29+DESC%0ALIMIT+10%3B)

Result:

| Program | Credential | Institutions | Program-Year Rows |
|---|---|---:|---:|
| Business Administration, Management and Operations. | Bachelor's Degree | 74 | 532 |
| Business Administration, Management and Operations. | Master's Degree | 61 | 424 |
| Psychology, General. | Bachelor's Degree | 50 | 360 |
| Liberal Arts and Sciences, General Studies and Humanities. | Bachelor's Degree | 47 | 327 |
| Teacher Education and Professional Development, Specific Levels and Methods. | Bachelor's Degree | 44 | 324 |
| Accounting and Related Services. | Bachelor's Degree | 43 | 302 |
| Marketing. | Bachelor's Degree | 43 | 280 |
| Registered Nursing, Nursing Administration, Nursing Research and Clinical Nursing. | Bachelor's Degree | 43 | 272 |
| Criminal Justice and Corrections. | Bachelor's Degree | 40 | 277 |
| Communication and Media Studies. | Bachelor's Degree | 39 | 287 |

Business Administration is the most-offered program, available at 74 of the 108 institutions with field_of_study data (66 percent of the institution set with program-level outcomes). The same program at the master's level reaches 61 institutions. The next most-common bachelor's programs follow a recognizable pattern: Psychology, Liberal Arts, Teacher Education, Accounting, Marketing, Nursing, Criminal Justice, Communication. These are the standard regional-comprehensive bachelor's portfolio: practical degrees with reliable enrollment, offered by most four-year institutions regardless of sector.

The pattern is informative for two reasons. First, it confirms that Florida four-year institutions are broadly comparable in what they offer: most institutions cover the same handful of programs at the bachelor's level, and the variation across institutions is more about quality and depth than about field coverage. Second, the absence of niche programs from the top 10 is itself a finding: STEM disciplines (engineering, computer science, biology) appear lower in the full ranking, partly because they are concentrated at fewer institutions, and partly because they are less commonly offered by the for-profit sector that contributes a meaningful share of the institution count.

## What's Worth Following Further

The first-pass queries give the shape of the data, but they answer single-dimension questions: how many institutions by sector, how much they cost, what they offer, who closed. The interesting questions mostly live at intersections, where two dimensions meet and the cross-tabulation surfaces patterns that neither dimension alone shows.

Three threads worth pulling in [phase 04](/archivo/college-scorecard-fl/04-findings/):

How did cost-vs-outcome ratios shift across the decade? The cost trajectory is documented; the completion rate is documented. The interesting question is the ratio: which institutions deliver the highest completion rate per dollar of net price, and how has that ratio moved over time? Window functions can rank institutions within sector and within year on a constructed "cost per completer" metric, surfacing the institutions that improved their efficiency and the ones that did not.

What did the for-profit closure wave look like as a structural shift in Florida's higher-education marketplace? Phase 03 captured the institutions that closed. Phase 04 can ask the systemic question: what fraction of Florida four-year for-profit enrollment was concentrated in the institutions that closed, and where did those students go? Some closure-wave students transferred to surviving for-profits, others to private nonprofits, others to publics. The data does not directly track student transfers, but enrollment shifts in surviving institutions during and after closure years can be analyzed as a proxy.

How do Florida's HBCUs compare to the broader Florida four-year picture? FAMU is the only public HBCU in the State University System, and Bethune-Cookman, Edward Waters, and Florida Memorial are private nonprofit HBCUs. Their cost, completion, and outcomes profiles are interesting both individually and as a peer group. Phase 04 develops this thread.

These are the questions phase 04 reaches for, with window functions and common table expressions doing the work that group-bys alone cannot.

