---
title: "qualtrics-report-generator"
weight: 40
description: "A Python utility that turns Qualtrics CSV exports into formatted, readable HTML reports. Built for administrative data intake (rankings, accreditation, compliance) where every individual response matters and aggregate statistics don't."
summary: "Renders Qualtrics surveys as HTML."
tags: ["python", "qualtrics", "html", "reporting", "higher-ed", "etl"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< lead >}}
Turns Qualtrics survey exports into a printable HTML report so reviewers can read each response without scrolling through a giant spreadsheet.
{{< /lead >}}

## At a Glance

Qualtrics is built for traditional surveys: many people, the same questions, aggregate statistics. The Reports tab in Qualtrics is excellent at producing pie charts and percentage breakdowns from data that has 500 respondents answering the same 20 questions. But there is an entirely different category of Qualtrics work that the Reports tab handles poorly, and most institutions do this category of work all the time.

Administrative data intake is the difference. An institutional rankings survey for U.S. News has seven administrators each filling out their assigned section (Admissions answers Admissions questions, Financial Aid answers Financial Aid questions, Research answers Research questions). An accreditation self-study has fifteen department heads each completing different parts of a 200-question survey. Each individual response matters. The aggregate (the average answer to each question) is meaningless because there is only one answer per question, supplied by the responsible administrator.

This tool generates HTML reports for that use case. It reads the CSV export, optionally combines it with the QSF survey-definition file for perfect labeling, and produces a single HTML document that organizes responses by question with proper formatting for each value type. The output is for review, validation, and sharing before the data goes anywhere external.

## The Problem

Three things make administrative data intake awkward in Qualtrics' default Reports tab.

**The data shape is wrong for aggregation.** A typical Qualtrics report shows what percentage of respondents picked each option. With only one respondent answering a given question, that percentage is always 100%. The report has nothing useful to say. The information that actually matters (what was the answer? does it look right? does it match what we expect?) is buried under a layout designed for multi-respondent statistics.

**The CSV export is hard to review at scale.** Every Qualtrics CSV has at least three header rows: the column ID (`Q5_3_TEXT`), the question text (`In the past year, how many...`), and a JSON metadata block. Below those is a wide table where each respondent is a row and each column is a question. Reviewing this in Excel means scrolling horizontally through hundreds of columns to find specific responses, with no good way to see one respondent's complete submission together.

**Question metadata gets lost in translation.** A multiple-choice question in Qualtrics has labeled choices ("Excellent", "Good", "Fair", "Poor"). The CSV export contains the choice text, but only if the user remembers to check the right export option. A matrix question has row labels and column labels that the CSV header partially preserves and partially obscures. A QSF (Qualtrics Survey Format) file contains the complete survey definition with every label, every ordering, every type. The CSV alone is a reduction of that schema. The report tool restores it.

The administrative-review workflow needs a different output: a document where each question is presented in context, with its respondent and their answer, formatted appropriately for what the answer actually is. That is what this tool produces.

## The Approach

A single Python script with two modes (CLI for automation, GUI for occasional users) and an optional second input file (the QSF survey definition).

The pipeline runs in five stages:

{{< mermaid >}}
flowchart TD
    A["User selects CSV (and optionally QSF)"] --> B["Parse QSF if provided: extract question types, choices, answers"]
    B --> C["Read CSV with pandas, validate structure"]
    C --> D["For each question column: combine QSF metadata with CSV data"]
    D --> E["For each cell value: detect type and apply appropriate formatter"]
    E --> F["Render question-by-question HTML report with embedded CSS"]
    F --> G["Single HTML file: review, share, host"]
{{< /mermaid >}}

Each stage handles a class of survey-data complexity that the previous stage cannot fully resolve.

QSF parsing extracts question types, choice labels, and answer labels from the survey definition. With this metadata, a multiple-choice question in the report shows the actual choice text from the survey rather than what landed in the CSV. A matrix question gets its row and column headers from the QSF, rendered as a proper HTML table.

CSV parsing reads the response data with pandas, applying defensive handling for the multi-header structure that Qualtrics uses. The combined output of these two stages is a structured representation of every question with its responses.

Value-type detection runs against every cell. URLs become clickable links. File paths render as file references. Coordinates get parsed and displayed properly. JSON values get pretty-printed. Long text values get rendered as paragraphs rather than table cells. The result is HTML that respects what each value actually is.

## Why QSF Matters (and Why It's Optional)

The QSF file is the survey-definition source of truth. It contains the complete schema: question types with their selectors and sub-selectors, choice labels in their authored order, answer labels for matrix columns, recode values, and display logic. The CSV is a reduction of that schema combined with response data.

With both files, the tool produces near-perfect reports. A matrix question shows up as a real HTML table with its row labels in QSF-defined order and its column labels in QSF-defined order. A multiple-choice question shows the actual choice text the survey designer wrote. A scale question carries its endpoint labels.

Without QSF, the tool falls back to inferring metadata from CSV header patterns. This is workable but lossy. A matrix question still gets recognized as a matrix (because the column naming pattern `Q5_1`, `Q5_2`, `Q5_3` is identifiable), but the row labels come from whatever Qualtrics put in the second header row, which is sometimes truncated or generic ("Row 1", "Row 2"). A multiple-choice question shows the choice text that ended up in the CSV, which is correct as long as the user exported with "Use choice text" enabled.

The optional QSF design lets the tool work on any Qualtrics CSV (because QSF is a separate download some users skip) while producing better output when both files are available. Same workflow either way, with quality scaling on input completeness. The tool auto-detects QSF presence by looking for a file with the same base name (`my_survey.csv` plus `my_survey.qsf` in the same folder), so the user does not have to flag the additional input.

## Why The Cell-Level Type Detection Matters

A Qualtrics CSV cell can contain almost anything. The same column might hold a multi-line essay response in row 3, a comma-separated list of selected options in row 7, a URL in row 12, a JSON-encoded matrix value in row 18, a file upload reference in row 22, and a "1" representing a numeric code in row 30. Rendering all of these as plain text in an HTML table produces an unreadable report.

The tool runs every cell through a 13-way type detector that classifies the value before formatting it. The categories cover the patterns survey responses actually take: empty, code, url, file, coordinate, timing, json, hierarchical, pipe_list, semicolon_list, comma_list, long_text, text. Each category has its own HTML formatter that renders the value appropriately:

- **URLs** become clickable links that open in new tabs
- **File paths** get a distinctive file icon prefix
- **Coordinates** get parsed and displayed in standard latitude/longitude format
- **JSON values** get pretty-printed with proper indentation
- **Multi-value lists** get rendered as bulleted lists with the appropriate separator (pipe, semicolon, comma)
- **Long text** becomes a multi-paragraph block rather than a cramped table cell
- **Empty values** become a styled "No response" placeholder so missing data is visually distinct from short answers

The detection logic is conservative: it tries the most specific patterns first (URL, file, coordinate, JSON, hierarchical), then falls back to multi-value detection with different separators, then long-text vs short-text classification, with a final fallback to plain text. Each detector returns a yes/no answer rather than a confidence score, and the categories are exclusive (a value gets one type, not several). This keeps the formatter selection deterministic.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="The QSF type map" >}}

Qualtrics question types are not a flat list. Each question has a `QuestionType` (Matrix, MC, TE, Slider, etc.), a `Selector` (the layout variant: SAVR, MAVR, Likert, Form, etc.), and an optional `SubSelector` (further specialization: SingleAnswer, MultipleAnswer, Long, Short). The combination of these three values determines how the question should be rendered in the report.

The tool maps QSF types to internal display types via a 26-entry lookup table:

```python
QSF_TYPE_MAP = {
    # Matrix questions: rows × columns grid format
    ('Matrix', 'TE', 'Long'): 'matrix_text',
    ('Matrix', 'TE', 'Short'): 'matrix_text',
    ('Matrix', 'TE', None): 'matrix_text',
    ('Matrix', 'Likert', 'SingleAnswer'): 'matrix_likert',
    ('Matrix', 'Likert', 'MultipleAnswer'): 'matrix_multi',
    ('Matrix', 'Likert', None): 'matrix_likert',
    ('Matrix', 'Profile', None): 'matrix_likert',
    ('Matrix', 'Bipolar', None): 'matrix_likert',
    ('Matrix', 'MaxDiff', None): 'matrix_likert',

    # Text entry questions: free-form text responses
    ('TE', 'FORM', None): 'form',          # Multi-field form
    ('TE', 'SL',   None): 'single_text',   # Single line
    ('TE', 'ML',   None): 'multi_text',    # Multi-line
    ('TE', 'ESTB', None): 'essay',         # Essay box
    ('TE', None,   None): 'single_text',

    # Multiple choice: single or multi-select
    ('MC', 'SAVR',  'TX'): 'single_choice',  # Single answer vertical
    ('MC', 'SAVR',  None): 'single_choice',
    ('MC', 'SAHR',  None): 'single_choice',  # Single answer horizontal
    ('MC', 'SACOL', None): 'single_choice',  # Single answer column
    ('MC', 'MAVR',  'TX'): 'multi_choice',   # Multiple answer vertical
    ('MC', 'MAVR',  None): 'multi_choice',
    ('MC', 'MAHR',  None): 'multi_choice',   # Multiple answer horizontal
    ('MC', 'MACOL', None): 'multi_choice',   # Multiple answer column
    ('MC', 'DL',    None): 'single_choice',  # Dropdown list
    ('MC', 'RB',    None): 'single_choice',  # Radio button
    ('MC', 'NPS',   None): 'single_choice',  # Net Promoter Score

    # Display blocks: informational, not real questions
    ('DB', 'TB',  None): 'display',  # Text block
    ('DB', 'GRB', None): 'display',  # Graphic block

    # Slider: continuous scale input (rendered as text in reports)
    ('Slider', 'HBAR',    None): 'single_text',
    ('Slider', 'HSLIDER', None): 'single_text',

    # Side by Side: complex multi-column format
    ('SBS', None, None): 'matrix_text',
}
```

A few things worth noting.

The lookup tries the full three-tuple `(qtype, selector, subselector)` first, then falls back to `(qtype, selector, None)` if the subselector-specific entry is missing. This handles QSF files where the subselector field is sometimes present and sometimes omitted depending on the survey designer's choices.

The map collapses several variant types into shared internal types. `Profile`, `Bipolar`, and `MaxDiff` matrices all render as `matrix_likert` because their visual presentation in the report is the same: a grid of single-answer responses. This collapse is intentional; the report does not need to distinguish between the underlying Qualtrics matrix variants because they all produce the same kind of cell.

`DB` (display block) entries get a `display` type, which the renderer treats as a no-op for response purposes. Display blocks are informational text shown to respondents (instructions, section headers); they never collect data, so there is nothing to report. The renderer optionally surfaces them as section dividers in the report; they never produce response rows.

The `SBS` (Side by Side) entry is a special case. SBS questions are complex multi-column composites that the Qualtrics CSV does not export cleanly; the tool currently treats them as matrix-like and produces a best-effort rendering. The map entry exists primarily to prevent the question type from falling through to the generic `unknown` handler.

{{< /accordionItem >}}

{{< accordionItem title="QSF parsing with ordered choice extraction" >}}

The QSF file is JSON, but the question metadata is not at the top level. Each question lives inside a `SurveyElements` array entry with `Element: 'SQ'`, and the actual metadata is in the entry's `Payload`. The parser walks this structure and pulls out the fields needed for rendering:

```python
def parse_qsf(qsf_path):
    with open(qsf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = {}

    for element in data.get('SurveyElements', []):
        if element.get('Element') != 'SQ':
            continue

        payload = element.get('Payload', {})
        export_tag = payload.get('DataExportTag', '')

        # Skip questions without export tags (internal/hidden questions)
        if not export_tag:
            continue

        # Resolve the question's internal display type via the type map
        type_key = (payload.get('QuestionType', ''),
                    payload.get('Selector', ''),
                    payload.get('SubSelector'))
        internal_type = QSF_TYPE_MAP.get(type_key)
        if not internal_type:
            internal_type = QSF_TYPE_MAP.get(
                (type_key[0], type_key[1], None), 'unknown')

        # Extract choices in the survey designer's authored order
        choices = {}
        choice_order = payload.get('ChoiceOrder', [])
        raw_choices = payload.get('Choices', {})

        for choice_id in choice_order:
            choice_data = raw_choices.get(str(choice_id), {})
            if isinstance(choice_data, dict):
                display = choice_data.get('Display',
                                          choice_data.get('Text', f'Choice {choice_id}'))
                choices[str(choice_id)] = clean_html_text(display)

        # Same pattern for answers (matrix column headers)
        # ... (parallel logic) ...

        questions[export_tag] = {
            'qid': payload.get('PrimaryAttribute', ''),
            'export_tag': export_tag,
            'text': clean_html_text(payload.get('QuestionText', '')),
            'internal_type': internal_type,
            'choices': choices,
            'choice_order': [str(c) for c in choice_order],
            'answers': answers,
            'answer_order': [str(a) for a in answer_order],
        }

    return questions
```

The `choice_order` field matters more than it first appears. Qualtrics survey designers carefully arrange choices in a specific order (worst-to-best, alphabetical, frequency-weighted, etc.). The CSV does not preserve this order in any reliable way; choices appear as columns in whatever sequence Qualtrics chose for the export. Without the QSF, choices in the report appear in CSV-export order, which often differs from authored order.

With the QSF, the parser captures the authored order through `ChoiceOrder` and uses it to drive the report's display sequence. A Likert-scale question rendered with choices in the wrong order ("Strongly Agree, Strongly Disagree, Agree, Neutral, Disagree") is dramatically harder to read than the same question with choices in proper order. The QSF parsing step is what makes the tool's matrix tables actually look like surveys.

The `Display` vs `Text` fallback handles a quirk of the QSF format: some choices store their visible label in `Display` (the field meant for the rendered value), others store it in `Text` (the field meant for the underlying text). The fallback chain (`Display` → `Text` → generic placeholder) ensures every choice gets a label even when the QSF format is inconsistent.

The `clean_html_text` step handles another QSF quirk: question text and choice labels can contain inline HTML (formatting, line breaks, embedded styles) because Qualtrics' editor allows rich text input. The cleaner strips out the HTML markup and returns plain text, which the renderer then re-wraps with its own formatting. Without this step, the report's HTML would have nested HTML inside its content, which produces unpredictable rendering and security issues.

{{< /accordionItem >}}

{{< accordionItem title="The 13-way value type detector with priority ordering" >}}

Every cell value goes through a single function that returns one of 13 type tags. The order of checks is deliberate: the most specific patterns are tested first, with progressively more permissive fallbacks toward the end:

```python
def detect_value_type(value, question_text='', column_id=''):
    """Detect the type of value for appropriate formatting."""

    # 1. Empty values: must be detected first to avoid downstream errors
    if is_empty(value):
        return 'empty'

    # 2. Timing columns: detected by column_id, not value content
    if is_timing_column(column_id):
        return 'timing'

    # 3. URLs and file paths: most specific patterns checked first
    if is_url(value):
        return 'file' if is_file_path(value) else 'url'

    if is_file_path(value):
        return 'file'

    # 4. Structured value types
    if is_coordinate(value):
        return 'coordinate'

    if is_json(value):
        return 'json'

    if is_hierarchical(value):
        return 'hierarchical'

    # 5. Multi-value lists: separators tested in priority order
    if is_multi_value(value, '|'):
        return 'pipe_list'

    if is_multi_value(value, ';'):
        return 'semicolon_list'

    if is_multi_value(value, ','):
        return 'comma_list'

    # 6. Length-based fallbacks
    if is_long_text(value):
        return 'long_text'

    # 7. Numeric codes (recognized via question context)
    if is_numeric_code(value, question_text):
        return 'code'

    # 8. Default: plain text
    return 'text'
```

The ordering matters because some value patterns overlap. A URL containing a comma technically matches both `is_url` and `is_multi_value(',')`. By checking URLs first, the tool gets the right answer (one URL, not three comma-separated fragments).

The pipe-semicolon-comma ordering for multi-value detection is deliberate. Pipe (`|`) is rare in natural text and almost always indicates a deliberate Qualtrics-style multi-value separator (Qualtrics uses pipes for "select all that apply" responses). Semicolon is the second-most-deliberate separator. Comma is most ambiguous because plenty of plain text contains commas; checking it last means the tool only treats commas as a separator when nothing else applies.

The `is_numeric_code` check at the end uses the question text as context, similar to the type detection in qualtrics-processing-pipeline. A pure number like "3" might be a code (Likert response, ranking) or a count (number of items), and the question text is usually the only way to tell. The function compares the question text against keyword lists for each interpretation and returns `True` only when the text suggests a coding context.

The `text` fallback is intentional: any value that does not match any pattern gets rendered as plain text with newlines preserved. This is the safe default. A misclassified text value (rare but possible) just renders as text instead of getting some special formatter applied to it. The renderer never crashes on an unknown type because all types map to a defined formatter.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.8+
- **Core libraries:** [pandas](https://pandas.pydata.org/) for CSV handling
- **GUI:** tkinter (built into Python; optional, CLI works without it)
- **Output format:** Self-contained HTML with embedded CSS, no external dependencies
- **Accessibility:** Colorblind-friendly palette (blue/teal/orange) verified safe for all common forms of color vision deficiency

## Repo

[github.com/hihipy/qualtrics-report-generator](https://github.com/hihipy/qualtrics-report-generator)
