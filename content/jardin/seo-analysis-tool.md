---
title: "seo-analysis-tool"
weight: 40
description: "A small Python script that analyzes a webpage's SEO health and produces a PDF report with calibrated recommendations. Built for the case where you want to teach someone what's wrong, not just tell them their score."
summary: "SEO analyzer with teaching reports."
tags: ["python", "seo", "beautifulsoup", "pdf", "side-project"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Analyzes a webpage's search-engine optimization and produces a PDF report that explains what each metric means in plain English.
{{< /lead >}}

## At a Glance

Most SEO tools tell you a score. You enter a URL, the tool gives you a number from 0 to 100, and you have to take it on faith that the score reflects something real. There is rarely an explanation of *why* the score is what it is, and there is almost never an explanation of why the underlying metrics matter in the first place.

This is a small Python script that takes a different approach. Enter a URL; get a PDF report. The report is structured around nine SEO metrics (title length, meta description, word count, link count, alt tags, H1 tags, mobile-friendliness, canonical tag, load time), and for each metric the report includes the actual measured value, the best-practice criteria, and a calibrated recommendation telling the user whether the value is too low, too high, or correct. Each metric also carries a one-paragraph explanation of what it is and why it matters.

The audience is people who do not already know what these terms mean. The output is a document they can read once, learn from, and then go fix the page themselves.

## The Design

Three choices distinguish the script from a generic SEO checker.

**Embedded metric documentation.** Every analyzed metric has a `definition`, `importance`, and `criteria` triplet baked directly into the code as a `METRIC_DETAILS` dictionary. The PDF report uses these to explain each metric in context. A user looking at "Word Count: 247 words" sees not just the number but the explanation that search engines favor pages with sufficient content, and the criterion that 600+ words is good while under 300 is bad. The metric is not just measured; it is taught.

**Calibrated recommendations, not binary pass/fail.** A title of 30 characters and a title of 75 characters are both wrong, but they are wrong in opposite directions. The recommendations engine handles this with three-state feedback per metric: too short, too long, or well-optimized. A title at 30 characters gets "Title is too short (30 characters). Aim for 50-60." A title at 75 characters gets "Title is too long (75 characters). Keep it under 60." A title at 55 characters gets "Title is well-optimized (55 characters)." The actionable next step is always specific.

**One PDF per run, saved to Downloads.** The output is a single self-contained PDF written to the user's Downloads folder. No web app, no SaaS account, no database of historical runs. Each analysis is a discrete artifact. If the user wants to track changes over time, they keep the PDFs. The simplicity is intentional: a small focused tool that does one thing reliably.

## What Gets Analyzed

Nine metrics, each with the same structure of value plus best-practice criteria.

| Metric | Best Practice |
|---|---|
| Page title | 50-60 characters |
| Meta description | 50-160 characters |
| Word count | 600+ words for main pages, 300+ minimum |
| Total links | 50-150 for main pages |
| Alt tags | All images have descriptive alt text |
| H1 tags | Exactly one H1 per page |
| Mobile-friendly | Viewport meta tag present |
| Canonical tag | Implemented and pointing to the master URL |
| Load time | Under 2 seconds |

The thresholds are not novel — these are well-established SEO conventions. What the script adds is the pairing of measurement with explanation in a single artifact, so the user does not have to research the conventions separately.

## How It Runs

The script is a single Python file driven by a command-line prompt. It uses BeautifulSoup to parse the HTML, the `requests` library to fetch the page (with elapsed time used as the load-time measurement), and `pdfkit` (which wraps `wkhtmltopdf`) to convert the generated HTML report into a PDF.

A typical run looks like this:

```
$ python seo_analyzer.py
Enter the URL to analyze: example.com

2026-04-27 10:42:13 - INFO - Analyzing URL: https://example.com
2026-04-27 10:42:14 - INFO - PDF report saved to: ~/Downloads/seo_analysis_report.pdf

Analysis completed. Check your Downloads folder for the report.
```

The script auto-prepends `https://` if the user enters a bare domain, sets a custom user-agent (`SEO Analyzer Bot`) so the request is identifiable to receiving servers, and times out after 10 seconds on unresponsive pages. Errors are logged with a timestamp and routed to an internal errors list rather than crashing the run, so a partial analysis still produces a partial report.

## The Docker Option

A `Dockerfile` is included for users who do not want to install `wkhtmltopdf` and its system dependencies on their machine. The image is based on `python:3.12-slim`, installs `wkhtmltopdf` via `apt-get`, copies in the requirements and the script, and exposes the analyzer as the container's entrypoint. The result is a one-line invocation:

```bash
docker run -it --rm -v ~/Downloads:/app/output seo-analyzer
```

The volume mount maps the container's output directory back to the host's Downloads folder, so the PDF lands where the user expects it regardless of what's installed on their system. This is a small but real quality-of-life improvement over the bare-metal install, especially for users who are getting onboarded to SEO work and do not want to debug `wkhtmltopdf` installation on the way.

## Stack

- **Language:** Python 3.6+
- **HTML parsing:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- **HTTP:** [requests](https://docs.python-requests.org/)
- **PDF generation:** [pdfkit](https://pypi.org/project/pdfkit/) (wraps [wkhtmltopdf](https://wkhtmltopdf.org/))
- **Markdown processing:** [markdown2](https://pypi.org/project/markdown2/)
- **Optional:** Docker for dependency-free deployment

## Repo

[github.com/hihipy/seo-analysis-tool](https://github.com/hihipy/seo-analysis-tool)
