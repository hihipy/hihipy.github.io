"""
build_kentucky_nih.py

Convert an NIH RePORTER export CSV (Kentucky 2005-2025) into a normalized
SQLite database with three tables: projects, project_funders, project_categories.

Usage:
    python build_kentucky_nih.py INPUT_CSV OUTPUT_SQLITE

Documented decisions
--------------------
1. The CSV starts with a 6-row "Search Criteria" preamble before the header.
   We skip it. A trailing comma on every row produces a phantom 55th column
   ("Unnamed: 54") which we drop.

2. NIH RePORTER uses blank strings and single spaces for missing values, not
   NULL. We coerce both to None at load time so SQL queries can use IS NULL.

3. Dates arrive as MM/DD/YYYY. We convert to ISO 8601 (YYYY-MM-DD) so that
   string sorting in SQL also sorts them chronologically.

4. The export is one row per (Application ID, Funding IC) pair, NOT one row
   per project. Co-funded projects appear multiple times. Verified invariants
   on this file:
     - Total Cost is identical across all funder rows of any one project
       (0 violations across 13,876 applications)
     - (Application ID, Funding IC) is unique (0 duplicates)
     - 3,580 rows (25.2%) have no Funding IC; these are projects from
       agencies that do not report cost data via NIH (per ExPORTER FAQ:
       cost data is only available for NIH, CDC, FDA, and ACF)

   So we split the data three ways:
     - projects (1 row per Application ID, project-level fields)
     - project_funders (1 row per (Application ID, Funding IC), cost split)
     - project_categories (1 row per (Application ID, Category), exploded)

5. NIH Spending Categorization is a semicolon-delimited multi-valued field.
   We explode it. We KEEP the value "No NIH Category available" because it is
   a meaningful NIH state (the project predates RCDC categorization or has
   not been categorized). Filter at query time if you want to exclude it.

6. Indexes target the filter patterns the case study will exercise:
   fiscal year, organization, IC, activity code, PI person ID, category.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlite_utils import Database


# ---------------------------------------------------------------------------
# Column mappings: NIH RePORTER export name -> snake_case SQL column
# ---------------------------------------------------------------------------

PROJECT_COLS = {
    "Application ID":           "application_id",
    "Project Number":           "project_number",
    "Project Title":            "project_title",
    "Project Abstract":         "project_abstract",
    "Project Terms":            "project_terms",
    "Public Health Relevance":  "public_health_relevance",
    "Administering IC":         "administering_ic",
    "Award Notice Date":        "award_notice_date",
    "Opportunity Number":       "opportunity_number",
    "Type":                     "application_type",
    "Activity":                 "activity_code",
    "IC":                       "ic",
    "Serial Number":            "serial_number",
    "Support Year":             "support_year",
    "Suffix":                   "suffix",
    "Program Official Information": "program_official",
    "Project Start Date":       "project_start_date",
    "Project End Date":         "project_end_date",
    "Study Section":            "study_section",
    "Subproject Number":        "subproject_number",
    "Contact PI Person ID":     "contact_pi_person_id",
    "Contact PI / Project Leader": "contact_pi",
    "Other PI or Project Leader(s)": "other_pis",
    "Congressional District":   "congressional_district",
    "Department":               "department",
    "Primary DUNS":             "primary_duns",
    "Primary UEI":              "primary_uei",
    "DUNS Number":              "duns_number",
    "UEI":                      "uei",
    "FIPS":                     "fips",
    "Latitude":                 "latitude",
    "Longitude":                "longitude",
    "Organization ID (IPF)":    "organization_id",
    "Organization Name":        "organization_name",
    "Organization City":        "organization_city",
    "Organization State":       "organization_state",
    "Organization Type":        "organization_type",
    "Organization Zip":         "organization_zip",
    "Organization Country":     "organization_country",
    "ARRA Indicator":           "arra_indicator",
    "Budget Start Date":        "budget_start_date",
    "Budget End Date":          "budget_end_date",
    "Post Award Action Type":   "post_award_action_type",
    "Assistance Listing Number": "assistance_listing_number",
    "Funding Mechanism":        "funding_mechanism",
    "Fiscal Year":              "fiscal_year",
    "Total Cost":               "total_cost",
    "Total Cost(Sub Projects)": "total_cost_subprojects",
    "NIH COVID-19 Response":    "nih_covid_response",
}

DATE_COLS = [
    "award_notice_date",
    "project_start_date",
    "project_end_date",
    "budget_start_date",
    "budget_end_date",
]

NUMERIC_COLS = [
    "latitude",
    "longitude",
    "total_cost",
    "total_cost_subprojects",
    "fiscal_year",
    "support_year",
]


# ---------------------------------------------------------------------------
# Cleaning helpers
# ---------------------------------------------------------------------------

def clean_string(s):
    """Treat blank or whitespace-only strings as None."""
    if pd.isna(s):
        return None
    s = str(s).strip()
    return s if s else None


def clean_date(s):
    """MM/DD/YYYY -> YYYY-MM-DD, blank -> None."""
    s = clean_string(s)
    if s is None:
        return None
    try:
        return pd.to_datetime(s, format="%m/%d/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def clean_number(s):
    """String -> float, blank -> None."""
    s = clean_string(s)
    if s is None:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=6, low_memory=False)
    if "Unnamed: 54" in df.columns:
        df = df.drop(columns=["Unnamed: 54"])
    return df


def build_projects(df: pd.DataFrame) -> list[dict]:
    """One row per Application ID.

    Project-level fields are constant across funder rows for any one
    application (verified). We take the first row per application_id.
    """
    project_cols = list(PROJECT_COLS.keys())
    projects = (
        df[project_cols]
        .rename(columns=PROJECT_COLS)
        .drop_duplicates(subset=["application_id"], keep="first")
        .copy()
    )

    for col in projects.columns:
        if col in DATE_COLS:
            projects[col] = projects[col].apply(clean_date)
        elif col in NUMERIC_COLS:
            projects[col] = projects[col].apply(clean_number)
        else:
            projects[col] = projects[col].apply(clean_string)

    return projects.to_dict(orient="records")


def build_project_funders(df: pd.DataFrame) -> list[dict]:
    """One row per (Application ID, Funding IC).

    Skips rows with no Funding IC (the 25% that come from non-cost-reporting
    agencies). Cost columns are coerced to float; blanks become None.
    """
    funders = df[[
        "Application ID", "Funding IC(s)",
        "Direct Cost IC", "Indirect Cost IC", "Total Cost IC",
    ]].rename(columns={
        "Application ID":   "application_id",
        "Funding IC(s)":    "funding_ic",
        "Direct Cost IC":   "direct_cost_ic",
        "Indirect Cost IC": "indirect_cost_ic",
        "Total Cost IC":    "total_cost_ic",
    }).copy()

    funders["funding_ic"] = funders["funding_ic"].apply(clean_string)
    funders = funders[funders["funding_ic"].notna()].copy()

    for col in ["direct_cost_ic", "indirect_cost_ic", "total_cost_ic"]:
        funders[col] = funders[col].apply(clean_number)

    return funders.to_dict(orient="records")


def build_project_categories(df: pd.DataFrame) -> list[dict]:
    """One row per (Application ID, Category), exploded from the
    semicolon-delimited NIH Spending Categorization field."""
    cats = df[["Application ID", "NIH Spending Categorization"]].rename(columns={
        "Application ID":             "application_id",
        "NIH Spending Categorization": "category",
    }).copy()

    cats["category"] = cats["category"].apply(clean_string)
    cats = cats[cats["category"].notna()].copy()
    cats["category"] = cats["category"].str.split(";")
    cats = cats.explode("category")
    cats["category"] = cats["category"].str.strip()
    cats = cats[cats["category"] != ""].drop_duplicates()

    return cats.to_dict(orient="records")


def write_database(out_path: Path, projects, funders, categories) -> Database:
    db = Database(out_path, recreate=True)

    db["projects"].insert_all(projects, pk="application_id")
    db["project_funders"].insert_all(
        funders,
        pk=("application_id", "funding_ic"),
        foreign_keys=[("application_id", "projects", "application_id")],
    )
    db["project_categories"].insert_all(
        categories,
        pk=("application_id", "category"),
        foreign_keys=[("application_id", "projects", "application_id")],
    )

    # Indexes for the queries the case study will exercise
    db["projects"].create_index(["fiscal_year"])
    db["projects"].create_index(["organization_name"])
    db["projects"].create_index(["administering_ic"])
    db["projects"].create_index(["activity_code"])
    db["projects"].create_index(["contact_pi_person_id"])
    db["projects"].create_index(["fiscal_year", "organization_name"])
    db["project_funders"].create_index(["funding_ic"])
    db["project_categories"].create_index(["category"])

    return db


def report(db: Database) -> None:
    print(f"  projects:           {db['projects'].count:>7,}")
    print(f"  project_funders:    {db['project_funders'].count:>7,}")
    print(f"  project_categories: {db['project_categories'].count:>7,}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("output_sqlite", type=Path)
    args = ap.parse_args()

    if not args.input_csv.exists():
        sys.exit(f"Input not found: {args.input_csv}")

    print(f"Reading {args.input_csv} ...")
    df = load_csv(args.input_csv)
    print(f"  {len(df):,} rows, {len(df.columns)} columns")

    print("Building tables ...")
    projects   = build_projects(df)
    funders    = build_project_funders(df)
    categories = build_project_categories(df)

    print(f"Writing {args.output_sqlite} ...")
    db = write_database(args.output_sqlite, projects, funders, categories)

    print("Done. Row counts:")
    report(db)


if __name__ == "__main__":
    main()
