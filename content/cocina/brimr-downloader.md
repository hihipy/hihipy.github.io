---
title: "brimr-downloader"
weight: 20
description: "A Python tool that automates the download and organization of NIH funding ranking data from the BRIMR website. Built for academic medical center analysts who need years of data without spending an afternoon clicking links."
summary: "Downloads NIH funding rankings."
tags: ["python", "selenium", "browser-automation", "etl", "nih", "higher-ed"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Automatically downloads NIH funding ranking data from the BRIMR website, saving hours of manual clicking each year.
{{< /lead >}}

## At a Glance

The [Blue Ridge Institute for Medical Research](https://brimr.org/) publishes annual rankings of NIH funding across U.S. institutions. The data is invaluable for any analyst working at an academic medical center: it shows where the money goes, by school, department, principal investigator, and geography. Anyone who has ever tried to assemble multiple years of this data has run into the same wall: every Excel file has to be downloaded by hand, and there are seventy-plus files per year across nearly two decades.

This tool reduces that work from an afternoon of clicking to a single Download button. It uses browser automation to visit each year's page, downloads every Excel file the page links to, and sorts them into a clean folder structure on the way out.

## The Problem

The friction with BRIMR data is not that it is hard to access. It is that accessing it at scale requires repetitive manual work that compounds quickly.

**Every file is its own download.** Clicking a link in the browser opens a save dialog; saving the file requires picking a name and a location. Multiply by seventy files per year, multiply by the number of years you need, and the math gets ugly.

**The filenames are inconsistent.** Some files have descriptive names (`Medical_Schools_Only.xlsx`), others have year suffixes (`pi_2023.xlsx`), and some have query strings appended that confuse the browser save dialog. Files arrive in your Downloads folder with no relationship to each other.

**It is easy to miss files.** A page can have over a hundred links across seventy distinct files, and visually distinguishing "Excel file I need" from "navigation link I do not need" is tedious. Skipping a file silently means a dataset with a hole in it, which is worse than a dataset that is obviously incomplete.

**It is easy to download files twice.** Different pages cross-link to the same datasets. Without bookkeeping, you end up with `medical_schools.xlsx` and `medical_schools (1).xlsx` and have to figure out which is which.

Each of these is fixable manually, but doing the manual fix every time you want to refresh the dataset is the kind of overhead that makes people stop refreshing the dataset.

## The Approach

A single Python script with a Tkinter GUI for year selection, backed by a Selenium-driven Chrome browser doing the actual downloading. The work happens in three phases:

1. **Year detection.** The tool figures out which years of data are available before the user picks anything, so the year list in the GUI reflects what BRIMR actually has rather than what was hardcoded.
2. **Per-year download.** For each selected year, the browser visits the page, finds the file links, and downloads each one to a temporary location.
3. **Categorization.** Each downloaded file is moved to a numbered folder based on what its filename indicates: school rankings, department summaries, PI rankings, and so on.

The result is a clean tree under `Downloads/BRIMR_Data/<year>/<category>/<file>` that any downstream tool can walk without surprises.

## Walking Through the Pipeline

### Detecting Available Years

A naive approach would be to hardcode the years the tool supports. That works until BRIMR publishes a new year and the tool silently drops it. The detector instead asks BRIMR, with a three-strategy cascade designed around the failure modes of each strategy:

{{< mermaid >}}
flowchart TD
    Start[User opens GUI] --> S1{Strategy 1: scrape homepage nav menu}
    S1 -- success --> Done[Populate year checkboxes]
    S1 -- failed or empty --> S2{Strategy 2: probe individual year URLs}
    S2 -- success --> Done
    S2 -- failed --> S3[Strategy 3: dynamic range, current year minus 1 down to 2006]
    S3 --> Done
{{< /mermaid >}}

Strategy 1 is fastest because the homepage already lists every published year in its navigation menu. A regex against the HTML extracts them in one HTTP request. Strategy 2 is the fallback for the case where BRIMR's site structure changes and the regex stops matching: the tool issues `HEAD` requests against each plausible year URL and keeps the ones that respond `200`. Strategy 3 is the floor: even if every network call fails, the tool still presents a sensible range of years rather than an empty list.

### Categorizing Downloaded Files

Once a file lands on disk, the tool decides which category folder it belongs in based on its filename. This is harder than it sounds. BRIMR's filenames are inconsistent across years (`pi_2023.xlsx`, `pi-rankings.xlsx`, `PIByDept.xlsx` are all PI files), and many filenames contain multiple recognizable terms (a PI ranking file for the medicine department contains both "pi" and "medicine").

The categorizer handles this with two passes. The first pass checks for PI files specifically, because they need to win against department-name patterns that would otherwise capture them. The second pass walks every other category's patterns, sorted longest-first so that more specific patterns get priority over shorter substring matches.

```python
# Check PI files first (they often contain department names too)
if "pi" in norm:
    if any(tag in raw for tag in ["_pi_", "_pi.", "pi_2", "contractspi"]):
        return "06_PI_Rankings"
    if any(tag in norm for tag in ["allorgdeptpi", "deptschoolpi", "schooldeptpi"]):
        return "06_PI_Rankings"

# Build list of (pattern, category) sorted by pattern length descending
all_patterns: list[tuple[str, str]] = []
for category, patterns in FILE_CATEGORIES.items():
    if category == "06_PI_Rankings":
        continue
    for pattern in patterns:
        clean_pattern = pattern.replace("-", "").replace("_", "")
        all_patterns.append((clean_pattern, category))

all_patterns.sort(key=lambda x: len(x[0]), reverse=True)

for pattern, category in all_patterns:
    if pattern in norm:
        return category

return "09_Uncategorized"
```

A file that cannot be categorized goes into `09_Uncategorized` rather than being silently dropped or misfiled. This is deliberate: a file in `Uncategorized` is a signal that the categorizer needs a new pattern added, and acting on that signal is far easier than discovering six months later that some files were quietly going to the wrong place.

### Skipping Existing Files

The tool checks the destination folder before downloading. If a file is already there, it is skipped. This makes incremental updates fast: re-running the tool after BRIMR publishes a new year only downloads the new year's files, leaving the rest untouched.

This is a small feature with an outsized effect on usability. Without it, a user who wants to add 2024 data to an existing 2006-2023 dataset would either re-download 18 years of redundant files or have to manually deselect the years they already have. With it, "give me the latest" is a single click.

## Why Browser Automation

A reasonable first instinct for a download script is `requests` plus a little HTML parsing. That approach does not work here, for two specific reasons.

**The file lists load dynamically.** BRIMR's pages render their Excel file links via JavaScript after the initial HTML loads. A `requests.get()` against the page URL returns the document shell, but the table of file links is empty until a browser executes the page's JavaScript. Selenium drives a real Chrome instance, which means the page renders exactly as it would for a human visitor, and the file links are present by the time the tool starts looking for them.

**Real browsers handle authentication, cookies, and redirects without special handling.** Some BRIMR file URLs redirect through tracking endpoints. Some respond differently to requests that do not include a full browser fingerprint. Driving an actual Chrome instance means none of these edge cases need code: the browser does what a browser does, and the tool just observes the result.

The cost is that Chrome has to be installed on the user's machine, and the download is slower than a pure HTTP fetch would be. Both costs are accepted because the alternative is a tool that breaks every time BRIMR's site evolves.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Three-strategy year detection with progressive resilience" >}}

The three strategies are not redundancy for its own sake; each one fails in a different way and the next one picks up.

```python
# Strategy 1: Scrape the homepage navigation menu (one HTTP request, regex extract)
response = requests.get("https://brimr.org/", headers=headers, timeout=10)
nav_years = set(
    int(m)
    for m in re.findall(
        r"brimr-rankings-of-nih-funding-in-(\d{4})",
        response.text,
    )
)
if nav_years:
    return sorted(nav_years, reverse=True)
```

If the homepage layout changes and the regex stops matching, Strategy 1 returns an empty set rather than incorrect years. The tool falls through to Strategy 2:

```python
# Strategy 2: Probe individual year URLs with HEAD requests
for year in range(latest_possible, 2005, -1):
    url = BASE_URL_TEMPLATE.format(year=year)
    response = requests.head(url, headers=headers, timeout=6, allow_redirects=True)
    if response.status_code == 200:
        years.add(year)
    elif response.status_code in (403, 405):
        # Some servers reject HEAD; fall back to streamed GET
        response = requests.get(url, headers=headers, timeout=8, stream=True)
        if response.status_code == 200:
            years.add(year)
```

`HEAD` is the right verb here: the tool only needs to know whether a URL exists, not what it contains. Using `GET` would download every page just to check existence, which is wasteful. Some servers return `403` or `405` for `HEAD` requests because the site builder did not anticipate them; the streamed `GET` fallback handles those cases without downloading the body.

Strategy 3 is the final floor: a hardcoded range from the latest possible publication year down to 2006, generated dynamically so the tool keeps working into the future even if every network call fails:

```python
# Strategy 3: Dynamic range fallback
latest_possible = current_year - 1   # BRIMR publishes the prior fiscal year
return list(range(latest_possible, 2005, -1))
```

The `current_year - 1` calculation reflects a domain detail: BRIMR ranks NIH fiscal years that end September 30, and rankings publish months after that, so the most recent ranking year is always the prior calendar year. Hardcoding `2024` would have made the tool stale; computing it from `datetime.now()` keeps it current.

{{< /accordionItem >}}

{{< accordionItem title="Pattern-priority categorization with PI special-case" >}}

The categorizer has to assign each file to exactly one category, even when the filename matches multiple patterns. Two design decisions make this work.

**PI files get checked first.** A file named `Medicine_PI_2023.xlsx` contains both "medicine" (a clinical department) and "pi" (a PI ranking). Without special handling, whichever pattern is checked first wins. The categorizer makes the call explicit:

```python
if "pi" in norm:
    if any(tag in raw for tag in ["_pi_", "_pi.", "pi_2", "contractspi"]):
        return "06_PI_Rankings"
    if any(tag in norm for tag in ["allorgdeptpi", "deptschoolpi", "schooldeptpi"]):
        return "06_PI_Rankings"
```

Note that the inner check has two flavors: one against the raw filename (preserving underscores and hyphens, looking for `_pi_` or `_pi.`), and one against a normalized version with separators stripped (looking for compound patterns like `allorgdeptpi`). This is because BRIMR uses both styles across years, and a single check would miss half the files.

**Other patterns are checked longest-first.** If the patterns include both `medicine` and `emergencymedicine`, an emergency medicine file should match the more specific pattern, not the more general one. Sorting by length descending guarantees this:

```python
all_patterns.sort(key=lambda x: len(x[0]), reverse=True)
for pattern, category in all_patterns:
    if pattern in norm:
        return category
```

The categorizer never uses regex for these matches, only substring containment. Substrings are cheaper to evaluate, and for filename-style matching they are accurate enough as long as the pattern list is well-chosen. The pattern list is currently around 130 entries across nine categories, all written by reading actual BRIMR filenames over the years.

{{< /accordionItem >}}

{{< accordionItem title="Browser-driven downloading with synchronized completion" >}}

Selenium provides the browser; getting files out of it cleanly requires a few specific moves.

The download directory is set on the running browser via Chrome DevTools Protocol, which means the directory can change between downloads without restarting the browser. That matters because the tool reuses one Chrome instance across years, sending each year's downloads to a different folder:

```python
def set_download_directory(driver: webdriver.Chrome, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": str(directory)},
    )
```

Knowing when a download has finished is harder than it looks. Chrome writes downloads with a `.crdownload` extension while in progress, then renames them to the final filename when complete. The tool watches for that rename:

```python
def wait_for_download_complete(directory: Path, timeout: int = 120) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        in_progress = list(directory.glob("*.crdownload"))
        if not in_progress:
            return True
        time.sleep(0.5)
    return False
```

Polling every half second is a reasonable trade between responsiveness and CPU load: a half-second delay is invisible to a human, and the polling thread is doing nothing but a directory glob in the meantime. The 120-second timeout protects against hung downloads without giving up too early on legitimately large files.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.10+
- **Browser automation:** [Selenium](https://www.selenium.dev/) with Chrome
- **Driver management:** [webdriver-manager](https://pypi.org/project/webdriver-manager/) (auto-downloads the matching ChromeDriver)
- **HTTP for year detection:** [requests](https://requests.readthedocs.io/)
- **GUI:** tkinter (built into Python)

## Repo

[github.com/hihipy/brimr-downloader](https://github.com/hihipy/brimr-downloader)
