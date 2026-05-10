---
title: "Findings"
weight: 40
description: "Window functions, CTEs, and the patterns that emerge when ten years of Florida four-year outcomes get cross-cut by sector, cost, and time. The for-profit closure wave, the cost-vs-outcome ratios, and the HBCU thread."
summary: "Five findings worth surfacing"
tags: ["sql", "sqlite", "window-functions", "ctes", "datasette"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}
{{< lead >}}
The exploration phase gave the shape; the findings phase reaches for window functions and CTEs to surface what changed.
{{< /lead >}}

## At a Glance

The orientation queries in [phase 03](/archivo/college-scorecard-fl/03-exploration/) covered single-dimension questions: how many institutions per sector, what they cost, who completed, what programs they offer. The findings phase asks the intersection questions, the ones a single GROUP BY cannot answer. Five threads follow, each pulled with window functions or common table expressions, each rooted in a question phase 03 raised but did not answer.

The framing is deliberately narrow. This case study is not a comprehensive analysis of Florida's four-year higher-education sector. It is a demonstration of how SQL on a verified dataset can surface specific structural patterns: the cost-per-completer ranking inside each sector, the fraction of for-profit enrollment that closure absorbed, what survivors did with the displaced students, where Florida's HBCUs sit relative to their sector peers, and where the highest reported earnings cluster. Each thread ends with a "what this doesn't tell you" boundary, because every analytical claim has limits worth naming.

<style>
  .pgbd-case-chart-wrap { margin: 1.5rem 0 2rem; }
  .pgbd-case-chart-wrap > .chart { height: 360px; }
  .pgbd-case-chart-headline { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.25rem; line-height: 1.3; }
  .pgbd-case-chart-sub { font-size: 0.85rem; opacity: 0.7; margin: 0 0 1rem; }
</style>

## Cost Per Completer Across The Sectors

The exploration phase showed that public, private nonprofit, and for-profit institutions report different average completion rates and different average net prices. The ratio of those two numbers is the more useful metric: cost per completer, defined as average net price divided by average completion rate. Lower ratios mean more completion per dollar.

\\[\text{cost per completer} = \dfrac{\overline{\text{net price}}}{\overline{c_{150,4}}}\\]

where \\(\overline{\text{net price}}\\) is the institution's average annual net price across all years with reported data, and \\(\overline{c_{150,4}}\\) is the institution's average six-year completion rate (the College Scorecard's `c150_4` metric) across all years with reported data. The bar notation indicates a mean across the available year-rows; institutions reporting fewer than five years of data are excluded by the query's HAVING clause so the averages are not built from a single partial year.

```sql
-- Cost-per-completer ranking within each sector, computed as average
-- net price divided by average completion rate. The CTE first builds
-- per-institution averages across years where both metrics are non-null;
-- HAVING COUNT >= 5 requires at least 5 years of data so the average is
-- not built from a single partial year. COALESCE on npt4_pub, npt4_priv,
-- npt4_other handles the schema reality that net price is reported in
-- different columns by sector. The outer query applies RANK() OVER
-- PARTITION BY sector so each sector has its own ranked list.
WITH institution_summary AS (
    SELECT
        i.unitid,
        i.instnm,
        CASE i.sector
            WHEN 'public'            THEN 'Public'
            WHEN 'private_nonprofit' THEN 'Private Nonprofit'
            WHEN 'for_profit'        THEN 'For-Profit'
        END AS sector_display,
        AVG(COALESCE(am.npt4_pub, am.npt4_priv, am.npt4_other)) AS avg_net_price,
        AVG(am.c150_4) AS avg_completion
    FROM institutions       i
    JOIN annual_metrics     am USING (unitid)
    WHERE am.c150_4 IS NOT NULL
      AND COALESCE(am.npt4_pub, am.npt4_priv, am.npt4_other) IS NOT NULL
    GROUP BY i.unitid, i.instnm, i.sector
    HAVING COUNT(am.c150_4) >= 5
)
SELECT
    instnm AS "Institution",
    sector_display AS "Sector",
    CAST(ROUND(avg_net_price, 0) AS INTEGER) AS "Avg Net Price",
    ROUND(avg_completion * 100, 1) AS "Avg Completion %",
    CAST(ROUND(avg_net_price / NULLIF(avg_completion, 0), 0) AS INTEGER) AS "Cost / Completer",
    RANK() OVER (PARTITION BY sector_display ORDER BY avg_net_price / NULLIF(avg_completion, 0) ASC) AS "Sector Rank"
FROM institution_summary
ORDER BY sector_display, avg_net_price / NULLIF(avg_completion, 0) ASC
LIMIT 30;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=WITH+institution_summary+AS+%28%0A++++SELECT%0A++++++++i.unitid%2C%0A++++++++i.instnm%2C%0A++++++++CASE+i.sector%0A++++++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++++++END+AS+sector_display%2C%0A++++++++AVG%28COALESCE%28am.npt4_pub%2C+am.npt4_priv%2C+am.npt4_other%29%29+AS+avg_net_price%2C%0A++++++++AVG%28am.c150_4%29+AS+avg_completion%0A++++FROM+institutions+++++++i%0A++++JOIN+annual_metrics+++++am+USING+%28unitid%29%0A++++WHERE+am.c150_4+IS+NOT+NULL%0A++++++AND+COALESCE%28am.npt4_pub%2C+am.npt4_priv%2C+am.npt4_other%29+IS+NOT+NULL%0A++++GROUP+BY+i.unitid%2C+i.instnm%2C+i.sector%0A++++HAVING+COUNT%28am.c150_4%29+%3E%3D+5%0A%29%0ASELECT%0A++++instnm+AS+%22Institution%22%2C%0A++++sector_display+AS+%22Sector%22%2C%0A++++CAST%28ROUND%28avg_net_price%2C+0%29+AS+INTEGER%29+AS+%22Avg+Net+Price%22%2C%0A++++ROUND%28avg_completion+%2A+100%2C+1%29+AS+%22Avg+Completion+%25%22%2C%0A++++CAST%28ROUND%28avg_net_price+%2F+NULLIF%28avg_completion%2C+0%29%2C+0%29+AS+INTEGER%29+AS+%22Cost+%2F+Completer%22%2C%0A++++RANK%28%29+OVER+%28PARTITION+BY+sector_display+ORDER+BY+avg_net_price+%2F+NULLIF%28avg_completion%2C+0%29+ASC%29+AS+%22Sector+Rank%22%0AFROM+institution_summary%0AORDER+BY+sector_display%2C+avg_net_price+%2F+NULLIF%28avg_completion%2C+0%29+ASC%0ALIMIT+30%3B)

Result (top 30 by lowest cost-per-completer, ranked within each sector):

| Institution | Sector | Avg Net Price | Avg Completion % | Cost / Completer | Sector Rank |
|---|---|---:|---:|---:|---:|
| San Ignacio University | For-Profit | $8,795 | 74.6 | $11,789 | 1 |
| Atlantis University | For-Profit | $18,306 | 78.0 | $23,472 | 2 |
| Acupuncture and Massage College | For-Profit | $25,840 | 73.6 | $35,129 | 3 |
| Florida National University-Main Campus | For-Profit | $20,935 | 50.6 | $41,369 | 4 |
| Rasmussen University-Florida | For-Profit | $18,385 | 31.6 | $58,150 | 5 |
| Full Sail University | For-Profit | $29,242 | 41.5 | $70,397 | 6 |
| AI Miami International University of Art and Design | For-Profit | $22,835 | 30.9 | $74,011 | 7 |
| Strayer University-Florida | For-Profit | $23,330 | 28.2 | $82,869 | 8 |
| DeVry University-Florida | For-Profit | $27,825 | 27.4 | $101,512 | 9 |
| Schiller International University | For-Profit | $24,630 | 22.6 | $108,770 | 10 |
| South University-West Palm Beach | For-Profit | $21,459 | 18.9 | $113,749 | 11 |
| South University-Tampa | For-Profit | $21,961 | 15.4 | $142,752 | 12 |
| Hobe Sound Bible College | Private Nonprofit | $8,759 | 51.8 | $16,915 | 1 |
| Baptist University of Florida | Private Nonprofit | $9,690 | 54.1 | $17,909 | 2 |
| Talmudic College of Florida | Private Nonprofit | $14,653 | 57.4 | $25,519 | 3 |
| Ave Maria University | Private Nonprofit | $18,988 | 54.5 | $34,857 | 4 |
| Stetson University | Private Nonprofit | $24,008 | 63.2 | $37,985 | 5 |
| Florida Southern College | Private Nonprofit | $25,706 | 65.0 | $39,548 | 6 |
| Florida College | Private Nonprofit | $21,210 | 52.9 | $40,063 | 7 |
| Saint Leo University | Private Nonprofit | $18,997 | 47.4 | $40,118 | 8 |
| Rollins College | Private Nonprofit | $30,030 | 74.3 | $40,416 | 9 |
| Flagler College | Private Nonprofit | $23,924 | 57.3 | $41,739 | 10 |
| University of Miami | Private Nonprofit | $35,042 | 82.8 | $42,338 | 11 |
| Polytechnic University of Puerto Rico-Miami | Private Nonprofit | $23,477 | 55.0 | $42,686 | 12 |
| Warner University | Private Nonprofit | $17,754 | 39.8 | $44,664 | 13 |
| St. John Vianney College Seminary | Private Nonprofit | $31,388 | 69.8 | $44,961 | 14 |
| Trinity Baptist College | Private Nonprofit | $16,169 | 35.4 | $45,726 | 15 |
| Bethune-Cookman University | Private Nonprofit | $16,081 | 34.7 | $46,380 | 16 |
| Johnson University Florida | Private Nonprofit | $17,146 | 36.9 | $46,496 | 17 |
| Palm Beach Atlantic University | Private Nonprofit | $25,347 | 54.5 | $46,543 | 18 |

The for-profit ranking is the most striking. San Ignacio University delivers cost per completer of $11,789, the lowest in the entire result set across all sectors. South University-Tampa delivers $142,752, more than twelve times worse. The two institutions are in the same sector, charge in the same neighborhood ($21,961 vs $18,306 net price), but their completion rates differ by a factor of five (15.4 vs 78.0 percent). The sector aggregate from phase 03 (39.7 percent average completion) hides this dispersion completely.

The private nonprofit ranking shows a different shape. The top 18 institutions cluster between $16,000 and $47,000 cost per completer, an order of magnitude tighter than the for-profit ranking. The University of Miami appears at rank 11 despite having the highest absolute net price ($35,042) because its 82.8 percent completion rate is also the highest in the list. The bottom of the private nonprofit ranking (not shown here, but visible in the full result on Datasette Lite) reaches into the $80,000-plus range for institutions that combine moderate price with low completion.

What this doesn't tell you: cost per completer is a constructed metric, not an outcome. It says nothing about what completers earn after graduation, what they study, or whether they would have completed at any institution. A high cost per completer ratio at an institution that serves Pell-eligible students with low academic preparation is not the same kind of finding as a high ratio at an institution that recruits the same population as flagship publics. The metric is useful for surfacing dispersion within a sector, not for ranking institutional value.

## The Closure-Wave Concentration

Phase 03 documented that thirteen for-profit four-year institutions disappeared from the data between 2014 and 2022. The next question is the systemic one: what fraction of the for-profit sector's enrollment did those thirteen institutions represent at their closure point, and how did the share evolve as closures progressed?

```sql
-- For-profit closure-wave concentration. What fraction of for-profit
-- enrollment was concentrated in institutions that subsequently closed?
-- The CTE classifies every for-profit by whether it stopped reporting
-- before 2023 (Closed) or made it through to 2023 (Survived). The outer
-- query aggregates enrollment by year and status, with a window function
-- (SUM(SUM(ugds)) OVER PARTITION BY cohort_year) computing each year's
-- total as the denominator for the percentage share calculation.
WITH for_profit_classification AS (
    SELECT
        unitid,
        CASE
            WHEN last_year_in_data < 2023 THEN 'Closed'
            ELSE 'Survived'
        END AS closure_status
    FROM institutions
    WHERE sector = 'for_profit'
)
SELECT
    am.cohort_year AS "Cohort Year",
    fpc.closure_status AS "Status",
    COUNT(*) AS "Institutions",
    SUM(am.ugds) AS "Total UG Enrollment",
    ROUND(100.0 * SUM(am.ugds) / SUM(SUM(am.ugds)) OVER (PARTITION BY am.cohort_year), 1) AS "% of Year Total"
FROM annual_metrics am
JOIN for_profit_classification fpc USING (unitid)
WHERE am.ugds IS NOT NULL
GROUP BY am.cohort_year, fpc.closure_status
ORDER BY am.cohort_year, fpc.closure_status DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=WITH+for_profit_classification+AS+%28%0A++++SELECT%0A++++++++unitid%2C%0A++++++++CASE%0A++++++++++++WHEN+last_year_in_data+%3C+2023+THEN+%27Closed%27%0A++++++++++++ELSE+%27Survived%27%0A++++++++END+AS+closure_status%0A++++FROM+institutions%0A++++WHERE+sector+%3D+%27for_profit%27%0A%29%0ASELECT%0A++++am.cohort_year+AS+%22Cohort+Year%22%2C%0A++++fpc.closure_status+AS+%22Status%22%2C%0A++++COUNT%28%2A%29+AS+%22Institutions%22%2C%0A++++SUM%28am.ugds%29+AS+%22Total+UG+Enrollment%22%2C%0A++++ROUND%28100.0+%2A+SUM%28am.ugds%29+%2F+SUM%28SUM%28am.ugds%29%29+OVER+%28PARTITION+BY+am.cohort_year%29%2C+1%29+AS+%22%25+of+Year+Total%22%0AFROM+annual_metrics+am%0AJOIN+for_profit_classification+fpc+USING+%28unitid%29%0AWHERE+am.ugds+IS+NOT+NULL%0AGROUP+BY+am.cohort_year%2C+fpc.closure_status%0AORDER+BY+am.cohort_year%2C+fpc.closure_status+DESC%3B)

Result (19 rows; for-profit enrollment by closure status across the decade):

| Cohort Year | Status | Institutions | Total UG Enrollment | % of Year Total |
|---:|---|---:|---:|---:|
| 2014 | Survived | 13 | 31,801 | 79.8 |
| 2014 | Closed | 9 | 8,037 | 20.2 |
| 2015 | Survived | 16 | 33,253 | 85.3 |
| 2015 | Closed | 8 | 5,719 | 14.7 |
| 2016 | Survived | 17 | 33,801 | 90.1 |
| 2016 | Closed | 8 | 3,715 | 9.9 |
| 2017 | Survived | 17 | 34,372 | 93.8 |
| 2017 | Closed | 6 | 2,268 | 6.2 |
| 2018 | Survived | 17 | 36,437 | 96.0 |
| 2018 | Closed | 2 | 1,512 | 4.0 |
| 2019 | Survived | 16 | 37,809 | 97.2 |
| 2019 | Closed | 2 | 1,080 | 2.8 |
| 2020 | Survived | 18 | 41,651 | 98.0 |
| 2020 | Closed | 2 | 858 | 2.0 |
| 2021 | Survived | 19 | 41,373 | 98.0 |
| 2021 | Closed | 1 | 857 | 2.0 |
| 2022 | Survived | 19 | 42,203 | 97.7 |
| 2022 | Closed | 2 | 973 | 2.3 |
| 2023 | Survived | 21 | 36,475 | 100.0 |

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Closing for-profits represented 20 percent of for-profit enrollment in 2014, dropping below 5 percent by 2018.</p>
<p class="pgbd-case-chart-sub">Share of Florida four-year for-profit undergraduate enrollment by closure status across cohort years 2014 to 2023.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
  datasets: [
    {
      label: 'Survived (% of year)',
      data: [79.8, 85.3, 90.1, 93.8, 96.0, 97.2, 98.0, 98.0, 97.7, 100.0],
      backgroundColor: '#1A7F37',
      borderColor: '#1A7F37',
      borderWidth: 1,
    },
    {
      label: 'Closed (% of year)',
      data: [20.2, 14.7, 9.9, 6.2, 4.0, 2.8, 2.0, 2.0, 2.3, 0.0],
      backgroundColor: '#8250DF',
      borderColor: '#8250DF',
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
          return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
        }
      }
    }
  },
  scales: {
    x: { stacked: true, title: { display: true, text: 'Cohort Year' } },
    y: { stacked: true, title: { display: true, text: 'Share of For-Profit Enrollment (%)' }, beginAtZero: true, max: 100, ticks: { callback: function(value) { return value + '%'; } } }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

In 2014, the institutions that would later close represented 20.2 percent of for-profit four-year enrollment in Florida, about 8,037 students. By 2017 the share had dropped to 6.2 percent, and by 2018 it was 4.0 percent. The closure wave was not just an event; it was a multi-year contraction with most of the displaced enrollment occurring in the first three years.

The cumulative count of displaced students is harder to compute exactly because students who appeared in 2014 at a closing institution may have transferred and been counted in subsequent years' surviving-institution rows. The minimum estimate (sum of "Closed" enrollments across all years) is roughly 25,000 student-years; the actual count of unique displaced students is somewhere between 8,000 and 25,000 depending on transfer patterns the data does not capture.

What this doesn't tell you: the closure wave's policy context. The Department of Education's Borrower Defense rules, the closure of Education Management Corporation (parent of Argosy and the Sanford-Brown chain), the Federal Student Aid program's gainful employment regulations, and the ongoing scrutiny of for-profit higher education by state attorneys general all happened in this window. The data shows the closures; it does not explain them.

## Where Did The Students Go

If 8,037 for-profit students lost their institution in 2014 alone, where did they go? The data does not directly track student transfers, but the surviving for-profit enrollment trajectory is suggestive: if survivors grew during and after closure years, that is consistent with student migration toward the surviving institutions. If survivors stayed flat, the closures represent net market contraction.

```sql
-- Surviving for-profit enrollment trajectory across the decade. The
-- survivors CTE filters to for-profits that reported in both 2014 and
-- 2023 (the institutions that endured the closure wave). The outer
-- query aggregates their annual undergraduate enrollment, showing
-- whether displaced students re-enrolled at survivors (growing
-- trajectory) or whether the closures represented net market
-- contraction (flat trajectory). The actual shape is rise then fall.
WITH survivors AS (
    SELECT unitid, instnm
    FROM institutions
    WHERE sector = 'for_profit'
      AND first_year_in_data <= 2014
      AND last_year_in_data = 2023
)
SELECT
    am.cohort_year            AS "Cohort Year",
    COUNT(DISTINCT am.unitid) AS "Survivors Reporting",
    SUM(am.ugds)              AS "Total Enrollment",
    CAST(ROUND(AVG(am.ugds), 0) AS INTEGER)    AS "Avg Enrollment"
FROM annual_metrics am
JOIN survivors s USING (unitid)
WHERE am.ugds IS NOT NULL
GROUP BY am.cohort_year
ORDER BY am.cohort_year;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=WITH+survivors+AS+%28%0A++++SELECT+unitid%2C+instnm%0A++++FROM+institutions%0A++++WHERE+sector+%3D+%27for_profit%27%0A++++++AND+first_year_in_data+%3C%3D+2014%0A++++++AND+last_year_in_data+%3D+2023%0A%29%0ASELECT%0A++++am.cohort_year++++++++++++AS+%22Cohort+Year%22%2C%0A++++COUNT%28DISTINCT+am.unitid%29+AS+%22Survivors+Reporting%22%2C%0A++++SUM%28am.ugds%29++++++++++++++AS+%22Total+Enrollment%22%2C%0A++++CAST%28ROUND%28AVG%28am.ugds%29%2C+0%29+AS+INTEGER%29++++AS+%22Avg+Enrollment%22%0AFROM+annual_metrics+am%0AJOIN+survivors+s+USING+%28unitid%29%0AWHERE+am.ugds+IS+NOT+NULL%0AGROUP+BY+am.cohort_year%0AORDER+BY+am.cohort_year%3B)

Result:

| Cohort Year | Survivors Reporting | Total Enrollment | Avg Enrollment |
|---:|---:|---:|---:|
| 2014 | 13 | 31,801 | 2,446 |
| 2015 | 13 | 32,976 | 2,537 |
| 2016 | 13 | 33,414 | 2,570 |
| 2017 | 13 | 33,792 | 2,599 |
| 2018 | 13 | 35,775 | 2,752 |
| 2019 | 12 | 37,262 | 3,105 |
| 2020 | 12 | 40,953 | 3,413 |
| 2021 | 12 | 40,059 | 3,338 |
| 2022 | 12 | 40,595 | 3,383 |
| 2023 | 12 | 34,700 | 2,892 |

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Surviving for-profit enrollment grew 29 percent from 2014 to a 2020 peak, then contracted 18 percent in three years.</p>
<p class="pgbd-case-chart-sub">Total undergraduate enrollment at Florida for-profit four-year institutions that reported every year from 2014 through 2023.</p>
{{< chart >}}
type: 'line',
data: {
  labels: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
  datasets: [
    {
      label: 'Survivor Total Enrollment',
      data: [31801, 32976, 33414, 33792, 35775, 37262, 40953, 40059, 40595, 34700],
      borderColor: '#1A7F37',
      backgroundColor: 'rgba(26, 127, 55, 0.10)',
      borderWidth: 2.5,
      fill: true,
      tension: 0.2,
      pointRadius: 3,
      pointHoverRadius: 6,
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
          return 'Enrollment: ' + context.parsed.y.toLocaleString();
        }
      }
    }
  },
  scales: {
    x: { title: { display: true, text: 'Cohort Year' } },
    y: { title: { display: true, text: 'Total Undergraduate Enrollment' }, beginAtZero: false, ticks: { callback: function(value) { return value.toLocaleString(); } } }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The pattern is real and visible. Survivor enrollment grew from 31,801 in 2014 to a peak of 40,953 in 2020, a 29 percent increase across six years that coincides almost exactly with the active closure window. Average per-institution enrollment grew similarly. Some of the closure-displaced students did re-enroll at surviving for-profits.

The 2023 drop is also worth noting. Survivor enrollment fell to 34,700 from a 40,953 peak, an 18 percent decline in three years. This is a recent contraction. The for-profit four-year sector did not simply consolidate during the closure wave and then stabilize; it consolidated, expanded, and is now contracting again. Whether this reflects pandemic enrollment effects, Federal Student Aid regulatory changes, or broader demographic pressure is not visible in the College Scorecard data alone.

What this doesn't tell you: the survivor-growth pattern is consistent with student migration but does not prove it. The growth could equally reflect new students entering the sector, the surviving institutions opening new programs that attracted enrollment from other sectors, or simply institutions reporting more aggressively for federal aid purposes. Establishing that displaced students migrated to specific surviving institutions requires student-level data the College Scorecard does not provide.

## The HBCU Thread

Florida has four Historically Black Colleges and Universities by the Higher Education Act of 1965 designation: Florida A&M University (the only public HBCU in the state), Bethune-Cookman University, Edward Waters University, and Florida Memorial University (the three private nonprofit HBCUs). The orientation queries in phase 03 did not single them out. The findings phase asks: how do they compare to their sector peers on the metrics most relevant to a recruiter or a policymaker?

The query filters by UNITID rather than by the `hbcu` flag, because [phase 02 documents](/archivo/college-scorecard-fl/02-schema/#a-build-gap-worth-documenting) that the flag column is unreliable in this database. The four UNITIDs are the verified institution numbers from the database itself, and the HBCU designation is a matter of external authoritative record (the U.S. Department of Education's [HBCU list](https://sites.ed.gov/whhbcu/one-hundred-and-five-historically-black-colleges-and-universities/)) rather than a derived classification.

```sql
-- HBCU comparison filtered by UNITID rather than the i.hbcu flag.
-- Phase 02 documents that the HBCU column is empty in this database
-- due to a build script gap. Florida's four HBCUs are well-known by
-- the Higher Education Act of 1965 designation; we hardcode their
-- UNITIDs (verified from the institutions table by INSTNM) to do
-- the comparison reliably.
SELECT
    i.instnm AS "Institution",
    CASE i.sector
        WHEN 'public'            THEN 'Public'
        WHEN 'private_nonprofit' THEN 'Private Nonprofit'
        WHEN 'for_profit'        THEN 'For-Profit'
    END                             AS "Sector",
    CAST(ROUND(AVG(am.ugds), 0) AS INTEGER)          AS "Avg Enrollment",
    CAST(ROUND(AVG(am.tuitionfee_in), 0) AS INTEGER) AS "Avg In-State Tuition",
    ROUND(AVG(am.pctpell) * 100, 1) AS "Avg Pell %",
    ROUND(AVG(am.c150_4) * 100, 1)  AS "Avg Completion %",
    ROUND(AVG(am.cdr3) * 100, 1)    AS "Avg Default Rate %"
FROM institutions       i
JOIN annual_metrics     am USING (unitid)
WHERE i.unitid IN (132602, 133526, 133650, 133979)
GROUP BY i.unitid, i.instnm, i.sector
ORDER BY AVG(am.ugds) DESC;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++i.instnm+AS+%22Institution%22%2C%0A++++CASE+i.sector%0A++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++END+++++++++++++++++++++++++++++AS+%22Sector%22%2C%0A++++CAST%28ROUND%28AVG%28am.ugds%29%2C+0%29+AS+INTEGER%29++++++++++AS+%22Avg+Enrollment%22%2C%0A++++CAST%28ROUND%28AVG%28am.tuitionfee_in%29%2C+0%29+AS+INTEGER%29+AS+%22Avg+In-State+Tuition%22%2C%0A++++ROUND%28AVG%28am.pctpell%29+%2A+100%2C+1%29+AS+%22Avg+Pell+%25%22%2C%0A++++ROUND%28AVG%28am.c150_4%29+%2A+100%2C+1%29++AS+%22Avg+Completion+%25%22%2C%0A++++ROUND%28AVG%28am.cdr3%29+%2A+100%2C+1%29++++AS+%22Avg+Default+Rate+%25%22%0AFROM+institutions+++++++i%0AJOIN+annual_metrics+++++am+USING+%28unitid%29%0AWHERE+i.unitid+IN+%28132602%2C+133526%2C+133650%2C+133979%29%0AGROUP+BY+i.unitid%2C+i.instnm%2C+i.sector%0AORDER+BY+AVG%28am.ugds%29+DESC%3B)

Result:

| Institution | Sector | Avg Enrollment | Avg In-State Tuition | Avg Pell % | Avg Completion % | Avg Default Rate % |
|---|---|---:|---:|---:|---:|---:|
| Florida Agricultural and Mechanical University | Public | 7,487 | $5,785 | 59.3 | 49.4 | 7.7 |
| Bethune-Cookman University | Private Nonprofit | 3,191 | $14,644 | 76.3 | 34.7 | 13.7 |
| Florida Memorial University | Private Nonprofit | 1,173 | $16,186 | 71.8 | 35.9 | 12.0 |
| Edward Waters University | Private Nonprofit | 995 | $14,002 | 49.1 | 25.7 | 16.3 |

The peer-group baseline (sector benchmarks, all 112 Florida four-year institutions):

```sql
-- Sector benchmarks for the HBCU comparison: average enrollment,
-- in-state tuition, Pell percentage, completion rate, and default rate
-- by sector across all 112 Florida four-year institutions. The HBCU
-- values from the previous query are read alongside these baselines
-- to show how each HBCU's metrics compare to its sector peers. ALL
-- enrolled institutions contribute to these averages, including the
-- HBCUs themselves (so the public sector average includes FAMU).
SELECT
    CASE i.sector
        WHEN 'public'            THEN 'Public'
        WHEN 'private_nonprofit' THEN 'Private Nonprofit'
        WHEN 'for_profit'        THEN 'For-Profit'
    END                             AS "Sector",
    CAST(ROUND(AVG(am.ugds), 0) AS INTEGER)          AS "Avg Enrollment",
    CAST(ROUND(AVG(am.tuitionfee_in), 0) AS INTEGER) AS "Avg In-State Tuition",
    ROUND(AVG(am.pctpell) * 100, 1) AS "Avg Pell %",
    ROUND(AVG(am.c150_4) * 100, 1)  AS "Avg Completion %",
    ROUND(AVG(am.cdr3) * 100, 1)    AS "Avg Default Rate %"
FROM institutions       i
JOIN annual_metrics     am USING (unitid)
GROUP BY i.sector
ORDER BY i.sector;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=SELECT%0A++++CASE+i.sector%0A++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++END+++++++++++++++++++++++++++++AS+%22Sector%22%2C%0A++++CAST%28ROUND%28AVG%28am.ugds%29%2C+0%29+AS+INTEGER%29++++++++++AS+%22Avg+Enrollment%22%2C%0A++++CAST%28ROUND%28AVG%28am.tuitionfee_in%29%2C+0%29+AS+INTEGER%29+AS+%22Avg+In-State+Tuition%22%2C%0A++++ROUND%28AVG%28am.pctpell%29+%2A+100%2C+1%29+AS+%22Avg+Pell+%25%22%2C%0A++++ROUND%28AVG%28am.c150_4%29+%2A+100%2C+1%29++AS+%22Avg+Completion+%25%22%2C%0A++++ROUND%28AVG%28am.cdr3%29+%2A+100%2C+1%29++++AS+%22Avg+Default+Rate+%25%22%0AFROM+institutions+++++++i%0AJOIN+annual_metrics+++++am+USING+%28unitid%29%0AGROUP+BY+i.sector%0AORDER+BY+i.sector%3B)

Result:

| Sector | Avg Enrollment | Avg In-State Tuition | Avg Pell % | Avg Completion % | Avg Default Rate % |
|---|---:|---:|---:|---:|---:|
| For-Profit | 1,851 | $15,482 | 49.0 | 39.7 | 7.2 |
| Private Nonprofit | 2,105 | $23,721 | 41.2 | 47.6 | 5.8 |
| Public | 19,690 | $5,915 | 36.0 | 62.8 | 3.4 |

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Florida HBCUs serve substantially higher Pell-eligible populations than their sector peers, with completion and default outcomes that reflect that population difference.</p>
<p class="pgbd-case-chart-sub">Three metrics compared across each Florida HBCU and its sector benchmark.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: ['Pell %', 'Completion %', 'Default Rate %'],
  datasets: [
    { label: 'FAMU (Public HBCU)', data: [59.3, 49.4, 7.7], backgroundColor: '#0969DA', borderColor: '#0969DA', borderWidth: 1 },
    { label: 'Public Sector Avg', data: [36.0, 62.8, 3.4], backgroundColor: 'rgba(9, 105, 218, 0.4)', borderColor: '#0969DA', borderWidth: 1 },
    { label: 'Bethune-Cookman', data: [76.3, 34.7, 13.7], backgroundColor: '#BF8700', borderColor: '#BF8700', borderWidth: 1 },
    { label: 'Florida Memorial', data: [71.8, 35.9, 12.0], backgroundColor: '#CF222E', borderColor: '#CF222E', borderWidth: 1 },
    { label: 'Edward Waters', data: [49.1, 25.7, 16.3], backgroundColor: '#8250DF', borderColor: '#8250DF', borderWidth: 1 },
    { label: 'Private NP Sector Avg', data: [41.2, 47.6, 5.8], backgroundColor: 'rgba(191, 135, 0, 0.4)', borderColor: '#BF8700', borderWidth: 1 }
  ]
},
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'bottom' },
    tooltip: { callbacks: { label: function(context) { return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%'; } } }
  },
  scales: {
    x: { title: { display: true, text: 'Metric' } },
    y: { title: { display: true, text: 'Percentage' }, beginAtZero: true, ticks: { callback: function(value) { return value + '%'; } } }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The comparison surfaces a real pattern. Florida HBCUs serve dramatically higher-poverty student populations than their sector peers. Bethune-Cookman's 76 percent Pell-eligible enrollment is roughly twice the Private Nonprofit sector average of 41 percent. FAMU's 59 percent Pell rate is roughly two-thirds higher than the Public sector average of 36 percent. The mission of these institutions is reflected in who attends them.

The downstream metrics reflect the population difference. Completion rates run lower than sector averages: FAMU 49 percent vs Public 63; the private HBCUs 26-36 percent vs Private Nonprofit 48 percent. Default rates run higher: FAMU 7.7 vs Public 3.4; the private HBCUs 12-16 percent vs Private Nonprofit 6 percent. The private HBCUs are also smaller than their sector peers (995 to 3,191 enrolled vs 2,105 sector average) and charge less than the sector mean ($14,000 to $16,000 vs $23,721).

This is not a story of HBCU underperformance. It is a story of mission-aligned institutions serving lower-income student populations than their sector peers, with cost, completion, and default outcomes that reflect that population difference. A graduate from Bethune-Cookman who entered with a high Pell-eligibility rate, took on substantial debt, and completed in five or six years has a different higher-education experience than a graduate from a flagship state university with high parental income, a National Merit Scholarship, and a four-year completion. The College Scorecard's outcome metrics flatten these student-population differences into a single completion rate or a single default rate; the comparison without that context is incomplete.

What this doesn't tell you: the institutional value HBCUs provide that does not show up in completion rates or default rates. The cultural significance, the alumni networks, the role in producing graduates who serve specific communities, the historical mission of access for students excluded from majority-white institutions for most of American history. None of this is in the College Scorecard data. Any reader who concludes from the table above that HBCUs are inferior institutions is reading the data outside the population context that defines them.

## The Top Of The Earnings Distribution

Phase 02 documented that 10-year-out median earnings (`md_earn_wne_p10`) is reported only in cohort years 2014 and 2020. Phase 04 uses the 2020 snapshot to identify the institutions whose alumni report the highest earnings ten years after entry, framed as a window-function ranking across the entire Florida four-year landscape.

The cohort year 2020 reports earnings for students who entered around 2009-10. These are pre-pandemic earnings reflecting careers that started during the post-Great-Recession recovery and matured through the 2010s.

```sql
-- Top 15 Florida four-year institutions by 10-year-out median earnings
-- (cohort year 2020 snapshot, the most recent year md_earn_wne_p10 is
-- reported). The CTE filters to non-null earnings rows for this single
-- year; the outer query applies RANK() OVER ORDER BY earnings DESC for
-- statewide ranking. Sector is included so the reader can see the
-- for-profit nursing schools and aviation programs that occupy the top
-- of the distribution alongside the broad-curriculum publics that
-- cluster in the $58K-$72K range.
WITH earnings_2020 AS (
    SELECT
        i.unitid,
        i.instnm,
        CASE i.sector
            WHEN 'public'            THEN 'Public'
            WHEN 'private_nonprofit' THEN 'Private Nonprofit'
            WHEN 'for_profit'        THEN 'For-Profit'
        END AS sector_display,
        am.md_earn_wne_p10
    FROM institutions       i
    JOIN annual_metrics     am USING (unitid)
    WHERE am.cohort_year = 2020
      AND am.md_earn_wne_p10 IS NOT NULL
)
SELECT
    instnm                                      AS "Institution",
    sector_display                              AS "Sector",
    md_earn_wne_p10                             AS "10-Year Earnings",
    RANK() OVER (ORDER BY md_earn_wne_p10 DESC) AS "Statewide Rank"
FROM earnings_2020
ORDER BY md_earn_wne_p10 DESC
LIMIT 15;
```

[Run this query in Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite#/college-scorecard-fl?sql=WITH+earnings_2020+AS+%28%0A++++SELECT%0A++++++++i.unitid%2C%0A++++++++i.instnm%2C%0A++++++++CASE+i.sector%0A++++++++++++WHEN+%27public%27++++++++++++THEN+%27Public%27%0A++++++++++++WHEN+%27private_nonprofit%27+THEN+%27Private+Nonprofit%27%0A++++++++++++WHEN+%27for_profit%27++++++++THEN+%27For-Profit%27%0A++++++++END+AS+sector_display%2C%0A++++++++am.md_earn_wne_p10%0A++++FROM+institutions+++++++i%0A++++JOIN+annual_metrics+++++am+USING+%28unitid%29%0A++++WHERE+am.cohort_year+%3D+2020%0A++++++AND+am.md_earn_wne_p10+IS+NOT+NULL%0A%29%0ASELECT%0A++++instnm++++++++++++++++++++++++++++++++++++++AS+%22Institution%22%2C%0A++++sector_display++++++++++++++++++++++++++++++AS+%22Sector%22%2C%0A++++md_earn_wne_p10+++++++++++++++++++++++++++++AS+%2210-Year+Earnings%22%2C%0A++++RANK%28%29+OVER+%28ORDER+BY+md_earn_wne_p10+DESC%29+AS+%22Statewide+Rank%22%0AFROM+earnings_2020%0AORDER+BY+md_earn_wne_p10+DESC%0ALIMIT+15%3B)

Result (top 15 by 10-year-out median earnings, 2020 cohort report):

| Institution | Sector | 10-Year Earnings | Statewide Rank |
|---|---|---:|---:|
| West Coast University-Miami | For-Profit | $102,672 | 1 |
| Chamberlain University-Florida | For-Profit | $92,405 | 2 |
| Embry-Riddle Aeronautical University-Daytona Beach | Private Nonprofit | $84,131 | 3 |
| Embry-Riddle Aeronautical University-Worldwide | Private Nonprofit | $84,131 | 3 |
| University of Miami | Private Nonprofit | $75,328 | 5 |
| AdventHealth University | Private Nonprofit | $72,282 | 6 |
| University of Florida | Public | $71,588 | 7 |
| University of Florida-Online | Public | $71,588 | 7 |
| Jacksonville University | Private Nonprofit | $68,010 | 9 |
| Florida State University | Public | $61,675 | 10 |
| Florida International University | Public | $60,249 | 11 |
| The University of Tampa | Private Nonprofit | $59,436 | 12 |
| Nova Southeastern University | Private Nonprofit | $59,209 | 13 |
| University of Central Florida | Public | $58,308 | 14 |
| Rollins College | Private Nonprofit | $58,295 | 15 |

<div class="pgbd-case-chart-wrap">
<p class="pgbd-case-chart-headline">Career-focused for-profit nursing institutions and Embry-Riddle's aviation programs lead the 10-year earnings ranking; the public flagships cluster in the $58K-$72K range.</p>
<p class="pgbd-case-chart-sub">Top 10 Florida four-year institutions by reported 10-year-out median earnings (cohort year 2020 snapshot). Bars colored by sector. The full top 15 ranking is in the Result table above.</p>
{{< chart >}}
type: 'bar',
data: {
  labels: ['West Coast U-Miami', 'Chamberlain-Florida', 'ERAU Daytona', 'ERAU Worldwide', 'UMiami', 'AdventHealth', 'UF', 'UF-Online', 'Jacksonville', 'FSU'],
  datasets: [{
    label: '10-Year Median Earnings',
    data: [102672, 92405, 84131, 84131, 75328, 72282, 71588, 71588, 68010, 61675],
    backgroundColor: ['#CF222E', '#CF222E', '#BF8700', '#BF8700', '#BF8700', '#BF8700', '#0969DA', '#0969DA', '#BF8700', '#0969DA'],
    borderWidth: 1
  }]
},
options: {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: function(context) { return '$' + context.parsed.x.toLocaleString(); } } }
  },
  scales: {
    x: { title: { display: true, text: '10-Year Median Earnings (USD)' }, beginAtZero: false, ticks: { callback: function(value) { return '$' + (value / 1000) + 'K'; } } },
    y: { title: { display: false } }
  },
  interaction: { mode: 'nearest', intersect: false }
}
{{< /chart >}}
</div>

The top of the ranking reveals what happens when an institution's curriculum is concentrated in one high-earning field. West Coast University-Miami and Chamberlain University-Florida are nursing-focused for-profit institutions; their alumni report median 10-year earnings of $102,672 and $92,405 respectively, well above the rest of the list. Embry-Riddle (aeronautical engineering) tied for third at $84,131 across both campus and worldwide programs. These three institutions occupy four of the top five slots not because they are exceptional schools in absolute terms but because their graduates are concentrated in fields with reliably high salaries.

The University of Miami at fifth ($75,328) is the highest-earning broad-curriculum private nonprofit. The University of Florida at seventh ($71,588) is the highest-earning public, edged out by AdventHealth University (a healthcare-focused private nonprofit) at $72,282. Florida State, FIU, and UCF round out the public flagships, all in the $58,000-$62,000 range.

What this doesn't tell you: the comparison treats earnings as institutional output, but earnings reflect both the institution and the field of study. A career-focused institution like West Coast University with a nursing-only curriculum will outrank a broad-curriculum university even if the broad-curriculum university produces stronger graduates in absolute terms, because the earnings number is averaged across fields and most fields pay less than nursing. The Department of Education publishes earnings data by program (CIPCODE × CREDLEV) precisely to address this; institution-level earnings are useful for ranking but should not be read as institutional quality metrics.

## What The Findings Add Up To

Five threads pulled, each rooted in a specific question phase 03 raised. The for-profit closure wave was real and concentrated in the first three years of the window, with surviving for-profits absorbing a meaningful share of the displaced enrollment before contracting again in 2023. Cost-per-completer dispersion within sectors is wider than the sector averages suggest, with twelvefold ranges visible in the for-profit data. Florida's HBCUs serve substantially higher-poverty populations than their sector peers, with outcome metrics that reflect the population difference rather than institutional quality. The top of the 10-year earnings distribution is dominated by career-focused institutions in nursing and aviation, not by the flagship publics that dominate undergraduate enrollment.

None of these findings is a definitive analysis. Each one names what the data shows and what it does not show, what it can support and what would require additional data sources to defend. The case study is not the analysis; it is the worked example of how a verified dataset, queried with documented SQL, can surface specific structural patterns that a single GROUP BY would not.

The full database is at `https://pgbd.casa/data/college-scorecard-fl.sqlite` and queryable directly in the browser via [Datasette Lite](https://lite.datasette.io/?url=https://pgbd.casa/data/college-scorecard-fl.sqlite). The build script is at [`tools/build_florida_scorecard.py`](https://github.com/hihipy/hihipy.github.io/blob/main/tools/build_florida_scorecard.py). The questions a reader might ask of this database are not bounded by what this case study chose to ask. The reproducibility-is-the-floor commitment from the [case study philosophy](/biblioteca/) is satisfied: anyone can re-run every query in this case study, change the parameters, and ask their own questions.
