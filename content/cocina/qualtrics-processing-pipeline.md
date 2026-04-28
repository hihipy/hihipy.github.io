---
title: "qualtrics-processing-pipeline"
weight: 30
description: "A Jupyter Notebook pipeline that turns raw Qualtrics survey exports into a documented, analysis-ready package. Question-aware type detection, non-destructive quality flagging, and an HTML report at the end."
summary: "Cleans Qualtrics survey data."
tags: ["python", "pandas", "qualtrics", "survey-data", "etl", "jupyter"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< katex >}}

{{< lead >}}
A Jupyter Notebook that takes raw Qualtrics survey data and produces a clean, documented dataset ready to analyze.
{{< /lead >}}

## At a Glance

Anyone who has worked with Qualtrics survey data knows that the export is the start of the work, not the finish. The raw `.xlsx` file mixes preview/test responses with real ones, has cryptic column names like `Q5_3_TEXT`, stores numbers and dates as strings, and arrives without a codebook. Every analyst who picks up a fresh export does roughly the same hour of manual cleaning before they can start asking analytical questions of the data.

This pipeline does that hour of work in one click. The user picks the raw Excel file through a file dialog, picks an output folder, and the notebook produces a complete analysis package: cleaned dataset with corrected types, full codebook mapping question codes to question text, quality flags for suspicious responses, an HTML report with the data quality story, and a JSON file pre-formatted for sentiment analysis. The work is transparent (every step is a notebook cell the user can inspect) and non-destructive (suspicious responses are flagged, not deleted).

## The Problem

Survey data has a category of cleaning work that other data sources don't. Three issues are universal across Qualtrics exports.

**Test data is mixed in with real responses.** Qualtrics' Survey Preview feature lets researchers test the survey before launch, and those test responses end up in the same export as real respondents. Some surveys also accumulate spam responses, partial submissions, and accidental duplicate entries. None of this should be in the analytical dataset, but it all looks the same as a real response until you look at the `Status` column.

**Column names are codes, not questions.** A Qualtrics export labels columns with internal identifiers: `Q1`, `Q5_3_TEXT`, `Q12_GROUP_2`. The actual question text lives in row 2 of the Excel file as a separate header row. Without combining the two, the analyst spends every minute of analysis flipping back to the survey instrument to remember what `Q5_3_TEXT` was asking.

**Types are wrong.** Numbers, dates, and durations are exported as strings because Excel's automatic type inference does not handle the export structure cleanly. A column that contains "Strongly Agree", "Agree", "Disagree", "Strongly Disagree" should be an ordered categorical. A column that contains "1995", "2003", "1987" should be an integer year. A column that contains "143.5" should be a float. None of these come through correctly without explicit conversion.

The manual cleaning workflow that addresses these issues is well-known but tedious: filter out preview responses, build a codebook by hand, retype each column, flag suspicious response patterns. Each step is straightforward in isolation; doing all of them, correctly, every time a fresh dataset arrives, is the friction.

## The Approach

A four-step Jupyter Notebook pipeline. Each step is a logical unit the user can run, inspect, and verify before continuing.

{{< mermaid >}}
flowchart TD
    A[User picks raw Qualtrics .xlsx via file dialog] --> B[Step 1: Load file and extract question mapping]
    B --> C[Step 2: Filter test responses, create quality flags]
    C --> D[Step 3: Detect and apply optimal data types per column]
    D --> E[Step 4: Generate output files]
    E --> F[analysis_ready_data.csv/.xlsx]
    E --> G[comprehensive_codebook.csv/.xlsx]
    E --> H[comprehensive_summary_report.html]
    E --> I[sentiment_analysis_data.json]
    E --> J[variable_summaries.xlsx]
{{< /mermaid >}}

Each output file is sized to a different downstream audience. The HTML report is for stakeholders who want to know "is this data trustworthy?" without opening the dataset themselves. The CSV and Excel files are for analysts who'll work in pandas, R, or Tableau. The JSON file is for downstream NLP work where the open-text responses get fed into sentiment analysis or topic modeling. The codebook is for whoever is documenting the analysis or writing it up.

## Why A Notebook

The choice of Jupyter Notebook over a single Python script is deliberate. The notebook is not just the implementation language; it is part of the user-facing experience.

The pipeline runs in four distinct steps separated by markdown cells. Each step produces visible output: dataframes, summary tables, counts of records affected. The user runs Step 1, looks at what was loaded, then runs Step 2, looks at what was filtered, and so on. If anything looks wrong (the test-response count is too high, the type detection misclassified a column), the user can stop and investigate before continuing.

This is the right architecture for survey data specifically because survey data has lots of edge cases. Different surveys collect different question types, in different orders, with different conventions. A "run this script and trust the output" approach inevitably produces silent miscleaning on the first survey that violates an assumption baked into the script. A notebook makes the assumptions visible at every step.

The cost of the notebook approach is one extra prerequisite (the user needs Jupyter installed). The README addresses this with a one-paragraph Anaconda installation guide that gets a non-Python user from "what is Python" to "running the pipeline" in about ten minutes.

## Why Question-Context Type Detection Matters

The most novel piece of the pipeline is its type detection logic. Standard pandas type inference looks at the values in a column and infers a type from the data. This works well for most data sources but fails predictably on survey data, because the same numeric values can mean very different things depending on what the question asked.

Three concrete examples illustrate the problem.

A column with values 1985, 1992, 2001, 2007 statistically looks like a small integer. If the question was "How many years of experience do you have?" the integer interpretation is correct. If the question was "In what year were you born?" the integer is technically correct but the type should preserve the year semantics for downstream filtering and grouping. If the question was "How many participants attended?" the integer is correct but the data should be treated as a count, with appropriate aggregation behavior.

A column with values 1, 2, 3, 4, 5 statistically looks like a small integer. If the question was "How many siblings do you have?" the integer is correct. If the question was "Rate your satisfaction from 1 (very dissatisfied) to 5 (very satisfied)" the values are an ordered categorical, and treating them as numeric will produce nonsensical means in downstream analysis (the average of "satisfied" and "very dissatisfied" is not "neutral").

A column with values "Yes", "No", "Yes", "Yes", "No" statistically looks like a categorical with two levels. If the question was open-ended ("Did you encounter any issues? Please explain"), the column should be text. If the question was a yes/no ("Did you complete the training?"), the column should be a boolean.

The pipeline reads the question text from row 2 of the Excel file, builds a mapping from column code to question text, and uses keyword matching against the question to inform type detection. The keyword categories cover the most common survey patterns: datetime keywords (`date`, `time`, `when`, `year`), year-specific questions (`founded`, `established`, `birth`, `graduation`), numeric questions (`number`, `count`, `amount`, `how many`, `percentage`), binary questions (`yes or no`, `agree`, `do you`, `have you`), and scale questions (`scale`, `rating`, `satisfaction`, `likelihood`, `strongly`, `somewhat`).

When a question matches a category, the pipeline biases toward the type that category suggests. A "year" question gets float64 with a range check (1800-2100). A scale question gets ordered categorical. A binary question gets boolean. The bias only applies when the data also supports the inferred type; if a "year" column actually contains text, the pipeline falls back to standard detection. The end result is type assignment that respects what the question was asking, not just what the values look like.

## Quality Flagging Without Deletion

The pipeline does not delete suspicious responses. It flags them. This is a deliberate philosophical choice that affects every part of the data quality system.

Five flag categories are computed for every response.

**Completion flags.** `flag_incomplete` is True for any response below 100% completion. `flag_very_incomplete` is True for responses below 50%. Survey research norms vary on how to handle incomplete responses; the analyst gets to decide based on their specific cutoff.

**Duration flags.** `flag_duration_too_short` is True for responses under 60 seconds, which is below the time it would take to read most surveys, let alone answer thoughtfully. `flag_duration_too_long` is True for responses over 2 hours (7200 seconds), which usually indicates the respondent left the browser open and came back later.

**Pattern flags.** `flag_potential_straightlining` is True for responses that show suspiciously uniform rating-scale answers. The detection algorithm is in the accordion below.

The flagging philosophy means the analyst is responsible for the destructive decision. The pipeline can say "this response was completed in 23 seconds and gave the same answer to every question on a 1-7 scale." It does not say "I removed this response." The analyst sees the flag, looks at the response, and decides whether to drop, keep, or weight it differently. The decision is recorded in their analysis code, not buried in the cleaning step.

This matters for reproducibility. A pipeline that silently drops responses produces different output every time the suspicious-response thresholds change. A pipeline that flags responses produces stable output, with the threshold-based decisions visible downstream where they belong.

## Straight-lining Detection

Straight-lining is the survey-research term for the pattern where a respondent answers every Likert-scale question with the same value (all 4s, all 6s, all "neither agree nor disagree"). It happens when respondents are not engaging with the questions individually and are clicking through to finish the survey. Detecting it is not foolproof — a respondent who genuinely agrees with everything is indistinguishable from one who is not paying attention — but the pattern is informative enough to flag.

The algorithm has three steps. First, identify which columns are likely to be rating scales: columns that are not metadata fields (Date, Status, IP, Progress, Duration, etc.), have numeric values, have at most 10 unique values, and have all values in the range 0 to 10. Second, for each respondent, collect their values across up to 10 of those scale columns. Third, compute the proportion of those values that are identical to the modal value:

$$P_{\text{straight}} = \frac{\text{count of modal value}}{\text{total scale responses}}$$

If \\(P_{\text{straight}} \geq 0.8\\) and the respondent has at least 3 scale responses, the flag is set. The 80% threshold is conservative; it catches the most egregious cases without false-positiving every respondent who happens to agree with most questions on a coherent topic.

The threshold and the column-detection rules are tuned for the survey designs the pipeline most commonly encounters. They could be lowered or raised; the pipeline exposes them as adjustable inside the relevant cell.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Question-context-aware type detection" >}}

The type detector follows a two-stage strategy: first, check whether the question text suggests a specific type; second, check whether the data supports that suggested type. Only when both agree does the pipeline assign the suggested type. If they disagree, the pipeline falls through to standard data-only detection.

```python
def analyze_column_for_type_with_context(series, col_name, question_text):
    """Use question text to inform type detection; fall back to data-only detection."""
    non_null_data = series.dropna()
    if len(non_null_data) == 0:
        return {'recommended_type': 'object', 'reason': 'all_null'}

    question_lower = question_text.lower()

    # Datetime-suggesting questions
    datetime_keywords = ['date', 'time', 'when', 'year', 'month', 'day', 'timestamp']
    if any(kw in question_lower for kw in datetime_keywords):
        result = detect_datetime_type(non_null_data, col_name)
        if result['is_datetime']:
            return {'recommended_type': 'datetime', 'reason': result['reason'] + '_question_context'}

    # Year-specific questions get a range check (1800-2100)
    year_keywords = ['year', 'founded', 'established', 'est.', 'birth', 'graduation']
    if any(kw in question_lower for kw in year_keywords):
        numeric_result = detect_numeric_type(non_null_data, col_name)
        if numeric_result['is_numeric']:
            valid_nums = pd.to_numeric(series, errors='coerce').dropna()
            if len(valid_nums) > 0 and valid_nums.min() > 1800 and valid_nums.max() < 2100:
                return {'recommended_type': 'float64', 'reason': 'year_values_from_question_context'}

    # Numeric questions
    numeric_keywords = ['number', 'count', 'amount', 'total', 'quantity',
                        'how many', 'percentage', '%', 'rate', 'score']
    if any(kw in question_lower for kw in numeric_keywords):
        numeric_result = detect_numeric_type(non_null_data, col_name)
        if numeric_result['is_numeric']:
            return {'recommended_type': numeric_result['numeric_subtype'],
                    'reason': numeric_result['reason'] + '_question_context'}

    # Binary questions
    binary_keywords = ['yes or no', 'y/n', 'agree', 'disagree',
                       'true or false', 'do you', 'have you', 'are you', 'is there']
    if any(kw in question_lower for kw in binary_keywords):
        boolean_result = detect_boolean_type(non_null_data, col_name)
        if boolean_result['is_boolean']:
            return {'recommended_type': 'category',
                    'reason': boolean_result['reason'] + '_question_context'}

    # Scale/rating questions become categorical even when numeric
    scale_keywords = ['scale', 'rating', 'satisfaction', 'likelihood',
                      'extent', 'strongly', 'somewhat']
    if any(kw in question_lower for kw in scale_keywords):
        categorical_result = detect_categorical_type(non_null_data, col_name)
        if categorical_result['is_categorical']:
            return {'recommended_type': 'category',
                    'reason': categorical_result['reason'] + '_scale_question'}

    # Fall back to data-only detection
    return analyze_column_for_type_standard(series, col_name, non_null_data,
                                             unique_values, sample_values)
```

A few details worth noting.

The `recommended_type` for scale questions is `category` even when the underlying values are numeric. This is the design decision that prevents downstream `mean()` from producing nonsense on Likert scales. An analyst who explicitly wants to compute a Likert mean (a defensible choice in some research traditions) can re-cast the column to numeric in their analysis code; the pipeline's default refuses to make that choice silently.

The year-question check is conservative. Even if the question says "year" and the values are numeric, the pipeline only assigns the year-aware type if the values fall in the plausible year range (1800-2100). A column where the question is "What year did you start using social media?" and the values are 5, 7, 12 (years of experience, not calendar years) will fall through to standard detection and not be misclassified.

The "fall back to standard detection" pattern is what keeps the question-context detection safe. The keyword matching biases the decision but never overrides what the data clearly shows. A column with a "year" question but text values gets treated as text, not as a malformed year. This conservatism is what lets the keyword lists be liberal: false positives in the keyword matcher do not produce wrong types because the data check catches them.

{{< /accordionItem >}}

{{< accordionItem title="Quality flag system" >}}

The flag system creates new boolean columns rather than removing rows. Each flag is independent; a respondent can be flagged on multiple dimensions, and the analyst sees all flags so they can decide which to act on:

```python
def create_quality_flags(df, analysis, cleaning_log):
    flagged_data = df.copy()

    # Flag 1: Completion status
    if analysis.get('has_progress_data'):
        progress_col = next(c for c in df.columns if 'progress' in c.lower())
        flagged_data['flag_incomplete'] = df[progress_col] < 100
        flagged_data['flag_very_incomplete'] = df[progress_col] < 50

    # Flag 2: Duration outliers
    if analysis.get('has_duration_data'):
        duration_col = next(c for c in df.columns if 'duration' in c.lower())
        duration_numeric = pd.to_numeric(df[duration_col], errors='coerce')
        flagged_data['flag_duration_too_short'] = duration_numeric < 60      # < 1 minute
        flagged_data['flag_duration_too_long']  = duration_numeric > 7200   # > 2 hours

    # Flag 3: Response pattern flags (straight-lining)
    pattern_flags = create_response_pattern_flags(df, cleaning_log)
    for flag_name, flag_data in pattern_flags.items():
        flagged_data[flag_name] = flag_data

    return flagged_data
```

The 60-second and 7200-second thresholds are heuristic but defensible. 60 seconds is below the time it takes to read most multi-page surveys at all; a response under that threshold is almost certainly someone clicking through without engaging. 7200 seconds (2 hours) catches the case where a respondent opened the survey, walked away, came back later, and finished — these responses can be valid but their duration values are unreliable, so flagging them lets the analyst decide whether to keep or filter them.

The flag column names follow a consistent prefix convention (`flag_*`) so downstream code can find them with a simple filter. The summary section at the end of cleaning reports both the per-flag counts and the count of responses with any flag, so the analyst sees both the granular and aggregate views.

The decision not to delete is the philosophical core of the system. Many "data cleaning" pipelines silently delete suspicious data, which has two failure modes: it makes the dataset smaller than the analyst expects (sample size questions get harder) and it hides decisions inside the cleaning step. The flag system pushes both into the analyst's hands.

{{< /accordionItem >}}

{{< accordionItem title="Straight-lining detection" >}}

The straight-lining flag combines column identification (which columns are scales?) with response pattern detection (does this respondent give the same answer to all of them?):

```python
def create_response_pattern_flags(df, cleaning_log):
    pattern_flags = {}

    # Identify scale-like columns: not metadata, numeric, ≤10 unique values, range 0-10
    metadata_terms = ['Date', 'Status', 'IP', 'Progress', 'Duration', 'Finished',
                      'Recorded', 'Response', 'Recipient', 'External',
                      'Location', 'Distribution', 'Language']
    question_cols = [col for col in df.columns
                     if not any(term in col for term in metadata_terms)]

    numeric_question_cols = []
    for col in question_cols:
        numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
        if len(numeric_vals) > 0:
            unique_vals = numeric_vals.unique()
            if (len(unique_vals) <= 10
                and numeric_vals.min() >= 0
                and numeric_vals.max() <= 10):
                numeric_question_cols.append(col)

    # For each respondent, compute proportion of identical scale responses
    if len(numeric_question_cols) >= 3:
        straightline_flags = []
        for idx, row in df.iterrows():
            scale_responses = []
            for col in numeric_question_cols[:10]:  # Sample up to 10 columns
                val = pd.to_numeric(row[col], errors='coerce')
                if not pd.isna(val):
                    scale_responses.append(val)

            if len(scale_responses) >= 3:
                most_common = max(set(scale_responses), key=scale_responses.count)
                same_pct = scale_responses.count(most_common) / len(scale_responses)
                straightline_flags.append(same_pct >= 0.8)
            else:
                straightline_flags.append(False)

        pattern_flags['flag_potential_straightlining'] = pd.Series(
            straightline_flags, index=df.index)

    return pattern_flags
```

The column-identification rules cover the most common survey scale patterns. Likert scales are typically 1-5, 1-7, or 1-10 with all values present and uniformly distributed across responses; satisfaction scales are similar; net-promoter-score columns are 0-10. The unique-value cap (10) excludes free-numeric responses (count of items, dollar amounts, ages) which would also pass the range check but would not naturally produce identical responses across questions.

The 10-column sample is a defensive performance measure. A survey with 50 scale questions could trigger the algorithm to compute 50-element identity checks for every respondent, which is fine for hundreds of respondents but slow for tens of thousands. Sampling to 10 columns gives enough signal to detect straight-lining (10 identical responses out of 10 is highly informative) while keeping the algorithm fast.

The minimum-3-responses threshold is what prevents false positives on respondents who only answered a few scale questions. A respondent who answered only one or two scale columns cannot be straight-lining by definition; they have not given enough responses to have a pattern. The threshold makes the algorithm conservative on partial responses while still catching the bad cases.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.8+
- **Notebook environment:** Jupyter Notebook (Anaconda recommended for first-time users)
- **Core libraries:** [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [openpyxl](https://openpyxl.readthedocs.io/) for Excel I/O
- **GUI:** tkinter (built into Python) for the file/folder picker dialogs
- **Output formats:** CSV, XLSX, JSON, HTML

## Repo

[github.com/hihipy/qualtrics-processing-pipeline](https://github.com/hihipy/qualtrics-processing-pipeline)
