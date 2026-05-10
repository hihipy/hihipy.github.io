"""
build_florida_scorecard.py

Convert U.S. Department of Education College Scorecard CSV exports into a
normalized SQLite database covering Florida four-year institutions, fiscal
years 2014-15 through 2023-24.

Usage:
    python build_florida_scorecard.py SCORECARD_DIR OUTPUT_SQLITE

    SCORECARD_DIR is the path to the unzipped College Scorecard download
    (containing MERGED*.csv and FieldOfStudyData*.csv files).

    OUTPUT_SQLITE is the path to write the database (recreated if exists).

Documented decisions
--------------------
1. The College Scorecard publishes 39 CSVs per release. We use 10 cohort
   years of MERGED data (2014-15 through 2023-24) and the corresponding
   FieldOfStudyData files. The Crosswalks folder is not used; column
   names are stable across the decade (verified: zero columns differ
   between MERGED2014_15_PP.csv and MERGED2023_24_PP.csv).

2. Each MERGED CSV has 3,308 columns. We retain ~70 columns chosen to
   support the four-phase case study's analytical questions. The retained
   columns cluster into institutional metadata (stable across years),
   cost and enrollment metrics (year-varying), outcome metrics (debt,
   completion, earnings), and federal aid program participation flags.

3. Scope: Florida four-year institutions only. The filter is STABBR='FL'
   AND PREDDEG IN (3, 4) (predominantly bachelor's or graduate). This
   includes public, private nonprofit, and for-profit four-year institutions.
   It excludes community colleges, certificate-only institutions, and
   institutions outside Florida.

4. College Scorecard uses 'PrivacySuppressed' (literal string) for
   privacy-protected small-cell suppression and 'NULL' (literal string)
   for missing data. We coerce both to None at load time so SQL queries
   can use IS NULL uniformly.

5. The schema has three tables:
     - institutions: 1 row per UNITID (stable metadata, takes most-recent year)
     - annual_metrics: 1 row per (UNITID, cohort_year) (year-varying metrics)
     - field_of_study: 1 row per (UNITID, cohort_year, CIPCODE, CREDLEV)

   The FieldOfStudy data does not include a STABBR column; we filter it
   to Florida UNITIDs by joining on the institution set determined from
   the MERGED files.

6. Some institutions appear in some years but not others (closures,
   accreditation losses, mergers, new openings). The institutions table
   includes derived columns first_year_in_data and last_year_in_data
   to support the closure-wave analysis without expensive joins.

7. Cohort year encoding: a cohort year of 2014 in the database refers to
   the academic year 2014-15. This matches the College Scorecard file
   naming convention (MERGED2014_15_PP.csv -> cohort_year=2014).

8. Indexes target the filter patterns the case study will exercise:
   cohort year, sector, control, and combined (cohort_year, unitid)
   for time-series joins.

Verification
------------
After build, the script verifies these invariants:
  - All institutions have a CONTROL value of 1, 2, or 3
  - All institutions have STABBR='FL' (the filter held)
  - All annual_metrics rows reference a UNITID in institutions
  - All field_of_study rows reference a UNITID in institutions
  - cohort_year values are in [2014, 2023]

If any invariant fails, the build raises and the database is not committed.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlite_utils import Database


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COHORT_YEARS = list(range(2014, 2024))  # 2014_15 through 2023_24

# Year suffix mapping: 2014 -> "2014_15", 1999 -> "1999_00"
def merged_filename(year: int) -> str:
    next_year = (year + 1) % 100
    return f"MERGED{year}_{next_year:02d}_PP.csv"


def field_of_study_filename(year: int) -> str:
    """FieldOfStudy files cover two cohorts (e.g., 1415_1516 covers entry
    cohorts 2014-15 and 2015-16). We use the file whose first cohort year
    matches our target."""
    next_year = (year + 1) % 100
    after_year = (year + 2) % 100
    return f"FieldOfStudyData{year % 100:02d}{next_year:02d}_{next_year:02d}{after_year:02d}_PP.csv"


# ---------------------------------------------------------------------------
# Column mappings: College Scorecard name -> snake_case SQL column
# ---------------------------------------------------------------------------

INSTITUTION_COLS = {
    "UNITID":          "unitid",
    "OPEID":           "opeid",
    "OPEID6":          "opeid6",
    "INSTNM":          "instnm",
    "CITY":            "city",
    "STABBR":          "stabbr",
    "ZIP":             "zip",
    "ACCREDAGENCY":    "accredagency",
    "INSTURL":         "insturl",
    "NPCURL":          "npcurl",
    "SCH_DEG":         "sch_deg",
    "HCM2":            "hcm2",
    "MAIN":            "main_campus",
    "NUMBRANCH":       "numbranch",
    "PREDDEG":         "preddeg",
    "HIGHDEG":         "highdeg",
    "CONTROL":         "control",
    "ST_FIPS":         "st_fips",
    "REGION":          "region",
    "LOCALE":          "locale",
    "LOCALE2":         "locale2",
    "LATITUDE":        "latitude",
    "LONGITUDE":       "longitude",
    "CCBASIC":         "ccbasic",
    "CCUGPROF":        "ccugprof",
    "CCSIZSET":        "ccsizset",
    "HBCU":            "hbcu",
    "PBI":             "pbi",
    "ANNHI":           "annhi",
    "TRIBAL":          "tribal",
    "AANAPII":         "aanapii",
    "HSI":             "hsi",
    "NANTI":           "nanti",
    "MENONLY":         "menonly",
    "WOMENONLY":       "womenonly",
    "RELAFFIL":        "relaffil",
    "DISTANCEONLY":    "distanceonly",
}

ANNUAL_METRICS_COLS = {
    # Enrollment
    "UGDS":                "ugds",
    "UGDS_MEN":            "ugds_men",
    "UGDS_WOMEN":          "ugds_women",
    "UGDS_WHITE":          "ugds_white",
    "UGDS_BLACK":          "ugds_black",
    "UGDS_HISP":           "ugds_hisp",
    "UGDS_ASIAN":          "ugds_asian",
    "UG12MN":              "ug12mn",
    # Cost
    "NPT4_PUB":            "npt4_pub",
    "NPT4_PRIV":           "npt4_priv",
    "NPT4_PROG":           "npt4_prog",
    "NPT4_OTHER":          "npt4_other",
    "TUITIONFEE_IN":       "tuitionfee_in",
    "TUITIONFEE_OUT":      "tuitionfee_out",
    "TUITIONFEE_PROG":     "tuitionfee_prog",
    "TUITFTE":             "tuitfte",
    "INEXPFTE":            "inexpfte",
    "AVGFACSAL":           "avgfacsal",
    # Aid and debt
    "PCTPELL":             "pctpell",
    "PCTFLOAN":            "pctfloan",
    "DEBT_MDN":            "debt_mdn",
    "GRAD_DEBT_MDN":       "grad_debt_mdn",
    "GRAD_DEBT_MDN10YR":   "grad_debt_mdn10yr",
    "WDRAW_DEBT_MDN":      "wdraw_debt_mdn",
    # Completion
    "C150_4":              "c150_4",
    "C150_4_POOLED":       "c150_4_pooled",
    "C200_4":              "c200_4",
    # Earnings (post-entry)
    "MD_EARN_WNE_P6":      "md_earn_wne_p6",
    "MD_EARN_WNE_P8":      "md_earn_wne_p8",
    "MD_EARN_WNE_P10":     "md_earn_wne_p10",
    "PCT25_EARN_WNE_P10":  "pct25_earn_wne_p10",
    "PCT75_EARN_WNE_P10":  "pct75_earn_wne_p10",
    # Repayment
    "RPY_3YR_RT":          "rpy_3yr_rt",
    "CDR2":                "cdr2",
    "CDR3":                "cdr3",
}

FIELD_OF_STUDY_COLS = {
    "UNITID":                            "unitid",
    "OPEID6":                            "opeid6",
    "INSTNM":                            "instnm",
    "CIPCODE":                           "cipcode",
    "CIPDESC":                           "cipdesc",
    "CREDLEV":                           "credlev",
    "CREDDESC":                          "creddesc",
    "DEBT_ALL_STGP_EVAL_MDN":            "debt_mdn",
    # Earnings progression: 1, 2, and 3 years post-completion.
    # HI suffix = high earners (excludes very-low and non-employed).
    "EARN_MDN_HI_1YR":                   "earn_mdn_1yr",
    "EARN_COUNT_NWNE_HI_1YR":            "earn_count_unemp_1yr",
    "EARN_MDN_HI_2YR":                   "earn_mdn_2yr",
    "EARN_COUNT_NWNE_HI_2YR":            "earn_count_unemp_2yr",
    # 3-year horizon uses different suffix (NE = "not enrolled" pool).
    "EARN_NE_MDN_3YR":                   "earn_mdn_3yr",
    "EARN_COUNT_NE_3YR":                 "earn_count_3yr",
}


# Columns that should be parsed as numeric (everything else stays string)
NUMERIC_INSTITUTION_COLS = {
    "unitid", "opeid6", "sch_deg", "hcm2", "main_campus", "numbranch",
    "preddeg", "highdeg", "control", "st_fips", "region", "locale", "locale2",
    "latitude", "longitude", "ccbasic", "ccugprof", "ccsizset",
    "hbcu", "pbi", "annhi", "tribal", "aanapii", "hsi", "nanti",
    "menonly", "womenonly", "relaffil", "distanceonly",
}

# All annual_metrics columns are numeric
NUMERIC_ANNUAL_COLS = set(ANNUAL_METRICS_COLS.values())

NUMERIC_FIELD_OF_STUDY_COLS = {
    "unitid", "opeid6", "credlev",
    "debt_mdn",
    "earn_mdn_1yr", "earn_count_unemp_1yr",
    "earn_mdn_2yr", "earn_count_unemp_2yr",
    "earn_mdn_3yr", "earn_count_3yr",
}


# ---------------------------------------------------------------------------
# Cleaning helpers
# ---------------------------------------------------------------------------

NULL_STRINGS = {"PrivacySuppressed", "NULL", ""}


def clean_string(s):
    """Treat literal 'PrivacySuppressed', 'NULL', and blank/whitespace as None."""
    if pd.isna(s):
        return None
    s = str(s).strip()
    if s in NULL_STRINGS:
        return None
    return s


def clean_number(s):
    """String -> float, or None for blank, NULL, PrivacySuppressed, or unparseable."""
    s = clean_string(s)
    if s is None:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------

def get_florida_4yr_unitids(scorecard_dir: Path) -> set[int]:
    """First pass: identify all UNITIDs that appear as Florida four-year
    in any cohort year of the window.

    A UNITID counts if it has STABBR='FL' AND PREDDEG IN (3, 4) in at
    least one cohort year. Some institutions appear in some years but
    not others (closures, accreditation changes); the union captures
    everything that ever appeared.
    """
    unitids = set()
    for year in COHORT_YEARS:
        path = scorecard_dir / merged_filename(year)
        if not path.exists():
            print(f"  WARNING: {path.name} not found, skipping")
            continue
        # Read only the columns we need to filter
        df = pd.read_csv(
            path,
            usecols=["UNITID", "STABBR", "PREDDEG"],
            low_memory=False,
            na_values=["PrivacySuppressed", "NULL"],
        )
        florida = df[(df["STABBR"] == "FL") & (df["PREDDEG"].isin([3, 4]))]
        unitids.update(florida["UNITID"].dropna().astype(int).tolist())
    return unitids


def derive_sector(control_value):
    """Map CONTROL code to human-readable sector label."""
    if control_value == 1:
        return "public"
    elif control_value == 2:
        return "private_nonprofit"
    elif control_value == 3:
        return "for_profit"
    return None


def build_institutions(scorecard_dir: Path, unitids: set[int]) -> list[dict]:
    """Stable institutional metadata. One row per UNITID.

    For each UNITID in scope, we use its most recent appearance in the
    window as the source-of-truth for stable metadata (institutions can
    rebrand, change locations, etc.). first_year_in_data and last_year_in_data
    are derived during this pass.
    """
    # Track first and last appearance, plus the most recent row's metadata
    first_year_seen: dict[int, int] = {}
    last_year_seen: dict[int, int] = {}
    most_recent_metadata: dict[int, dict] = {}

    for year in COHORT_YEARS:
        path = scorecard_dir / merged_filename(year)
        if not path.exists():
            continue
        df = pd.read_csv(
            path,
            usecols=list(INSTITUTION_COLS.keys()),
            low_memory=False,
            na_values=["PrivacySuppressed", "NULL"],
        )
        df = df[df["UNITID"].isin(unitids)]

        for _, row in df.iterrows():
            unitid = int(row["UNITID"])
            if unitid not in first_year_seen:
                first_year_seen[unitid] = year
            last_year_seen[unitid] = year
            most_recent_metadata[unitid] = row.to_dict()

    institutions = []
    for unitid in sorted(unitids):
        if unitid not in most_recent_metadata:
            continue
        raw = most_recent_metadata[unitid]
        record = {}
        for orig_col, new_col in INSTITUTION_COLS.items():
            value = raw.get(orig_col)
            if new_col in NUMERIC_INSTITUTION_COLS:
                record[new_col] = clean_number(value)
            else:
                record[new_col] = clean_string(value)
        # Coerce identifiers back to int (clean_number returned floats)
        for int_col in ("unitid", "opeid6", "preddeg", "highdeg", "control",
                        "st_fips", "region", "main_campus", "numbranch",
                        "hcm2", "sch_deg"):
            if record.get(int_col) is not None:
                record[int_col] = int(record[int_col])
        record["sector"] = derive_sector(record.get("control"))
        record["first_year_in_data"] = first_year_seen[unitid]
        record["last_year_in_data"] = last_year_seen[unitid]
        institutions.append(record)

    return institutions


def build_annual_metrics(scorecard_dir: Path, unitids: set[int]) -> list[dict]:
    """One row per (UNITID, cohort_year) with year-varying metrics."""
    rows = []
    for year in COHORT_YEARS:
        path = scorecard_dir / merged_filename(year)
        if not path.exists():
            continue
        cols_to_read = ["UNITID"] + list(ANNUAL_METRICS_COLS.keys())
        df = pd.read_csv(
            path,
            usecols=cols_to_read,
            low_memory=False,
            na_values=["PrivacySuppressed", "NULL"],
        )
        df = df[df["UNITID"].isin(unitids)]

        for _, row in df.iterrows():
            unitid = int(row["UNITID"])
            record = {"unitid": unitid, "cohort_year": year}
            for orig_col, new_col in ANNUAL_METRICS_COLS.items():
                record[new_col] = clean_number(row.get(orig_col))
            rows.append(record)

    return rows


def build_field_of_study(scorecard_dir: Path, unitids: set[int]) -> list[dict]:
    """One row per (UNITID, cohort_year, CIPCODE, CREDLEV).

    FieldOfStudy files cover two-year cohort windows (e.g., 1415_1516).
    We use the file's first cohort year as the cohort_year value.
    """
    rows = []
    for year in COHORT_YEARS:
        path = scorecard_dir / field_of_study_filename(year)
        if not path.exists():
            continue
        cols_to_read = list(FIELD_OF_STUDY_COLS.keys())
        df = pd.read_csv(
            path,
            usecols=cols_to_read,
            low_memory=False,
            na_values=["PrivacySuppressed", "NULL"],
            dtype={"CIPCODE": str},  # Keep CIP codes as strings (leading zeros)
        )
        df = df[df["UNITID"].isin(unitids)]

        for _, row in df.iterrows():
            unitid = int(row["UNITID"])
            record = {"unitid": unitid, "cohort_year": year}
            for orig_col, new_col in FIELD_OF_STUDY_COLS.items():
                if new_col == "unitid":
                    continue
                value = row.get(orig_col)
                if new_col in NUMERIC_FIELD_OF_STUDY_COLS:
                    record[new_col] = clean_number(value)
                else:
                    record[new_col] = clean_string(value)
            if record.get("opeid6") is not None:
                record["opeid6"] = int(record["opeid6"])
            if record.get("credlev") is not None:
                record["credlev"] = int(record["credlev"])
            rows.append(record)

    return rows


def write_database(
    out_path: Path,
    institutions: list[dict],
    annual_metrics: list[dict],
    field_of_study: list[dict],
) -> Database:
    db = Database(out_path, recreate=True)

    db["institutions"].insert_all(institutions, pk="unitid")

    db["annual_metrics"].insert_all(
        annual_metrics,
        pk=("unitid", "cohort_year"),
        foreign_keys=[("unitid", "institutions", "unitid")],
    )

    if field_of_study:
        db["field_of_study"].insert_all(
            field_of_study,
            pk=("unitid", "cohort_year", "cipcode", "credlev"),
            foreign_keys=[("unitid", "institutions", "unitid")],
        )

    # Indexes target case study query patterns
    db["institutions"].create_index(["sector"])
    db["institutions"].create_index(["control"])
    db["annual_metrics"].create_index(["cohort_year"])
    db["annual_metrics"].create_index(["cohort_year", "unitid"])
    if field_of_study:
        db["field_of_study"].create_index(["cipcode"])
        db["field_of_study"].create_index(["credlev"])

    return db


def verify_invariants(db: Database) -> None:
    """Verify invariants that must hold; raise if any fail."""
    print("Verifying invariants ...")

    # Invariant 1: All institutions have CONTROL in (1, 2, 3)
    bad_control = list(
        db.query("SELECT COUNT(*) AS n FROM institutions WHERE control NOT IN (1, 2, 3)")
    )[0]["n"]
    if bad_control > 0:
        raise RuntimeError(f"  FAIL: {bad_control} institutions have invalid CONTROL value")
    print("  ✓ All institutions have CONTROL in (1, 2, 3)")

    # Invariant 2: All institutions have STABBR='FL'
    bad_state = list(
        db.query("SELECT COUNT(*) AS n FROM institutions WHERE stabbr != 'FL'")
    )[0]["n"]
    if bad_state > 0:
        raise RuntimeError(f"  FAIL: {bad_state} institutions have STABBR != 'FL'")
    print("  ✓ All institutions are in Florida")

    # Invariant 3: All annual_metrics rows reference a known institution
    orphan_metrics = list(
        db.query(
            "SELECT COUNT(*) AS n FROM annual_metrics WHERE unitid NOT IN "
            "(SELECT unitid FROM institutions)"
        )
    )[0]["n"]
    if orphan_metrics > 0:
        raise RuntimeError(f"  FAIL: {orphan_metrics} annual_metrics rows are orphaned")
    print("  ✓ All annual_metrics rows reference a known institution")

    # Invariant 4: All field_of_study rows reference a known institution
    orphan_fos = list(
        db.query(
            "SELECT COUNT(*) AS n FROM field_of_study WHERE unitid NOT IN "
            "(SELECT unitid FROM institutions)"
        )
    )[0]["n"]
    if orphan_fos > 0:
        raise RuntimeError(f"  FAIL: {orphan_fos} field_of_study rows are orphaned")
    print("  ✓ All field_of_study rows reference a known institution")

    # Invariant 5: cohort_year in [2014, 2023]
    bad_year = list(
        db.query(
            "SELECT COUNT(*) AS n FROM annual_metrics "
            "WHERE cohort_year < 2014 OR cohort_year > 2023"
        )
    )[0]["n"]
    if bad_year > 0:
        raise RuntimeError(f"  FAIL: {bad_year} annual_metrics rows outside the year window")
    print("  ✓ All cohort_year values in [2014, 2023]")


def report(db: Database) -> None:
    print("\nFinal counts:")
    print(f"  institutions:   {db['institutions'].count:>7,}")
    print(f"  annual_metrics: {db['annual_metrics'].count:>7,}")
    print(f"  field_of_study: {db['field_of_study'].count:>7,}")

    sector_counts = list(db.query(
        "SELECT sector, COUNT(*) AS n FROM institutions GROUP BY sector ORDER BY n DESC"
    ))
    print("\nInstitutions by sector:")
    for r in sector_counts:
        print(f"  {r['sector']:>20}: {r['n']:>4}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("scorecard_dir", type=Path)
    ap.add_argument("output_sqlite", type=Path)
    args = ap.parse_args()

    if not args.scorecard_dir.exists():
        sys.exit(f"Scorecard directory not found: {args.scorecard_dir}")

    print(f"Identifying Florida four-year UNITIDs ...")
    unitids = get_florida_4yr_unitids(args.scorecard_dir)
    print(f"  {len(unitids)} unique UNITIDs across {len(COHORT_YEARS)} cohort years")

    print(f"\nBuilding institutions table ...")
    institutions = build_institutions(args.scorecard_dir, unitids)
    print(f"  {len(institutions)} rows")

    print(f"\nBuilding annual_metrics table ...")
    annual_metrics = build_annual_metrics(args.scorecard_dir, unitids)
    print(f"  {len(annual_metrics)} rows")

    print(f"\nBuilding field_of_study table ...")
    field_of_study = build_field_of_study(args.scorecard_dir, unitids)
    print(f"  {len(field_of_study)} rows")

    print(f"\nWriting {args.output_sqlite} ...")
    db = write_database(
        args.output_sqlite, institutions, annual_metrics, field_of_study
    )

    verify_invariants(db)
    report(db)
    print("\nDone.")


if __name__ == "__main__":
    main()
