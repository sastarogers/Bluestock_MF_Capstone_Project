"""
Day 1 — Data Ingestion Script
==============================
Bluestock Mutual Fund Capstone Project

Loads all 10 raw CSV datasets, prints schema summaries,
explores fund-master metadata, and validates AMFI codes
between fund_master and nav_history.

Usage:
    python3 scripts/data_ingestion.py
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def load_and_profile(file_path: Path) -> pd.DataFrame:
    """Load a single CSV and log its shape, dtypes, missing values, and duplicate count.

    Parameters
    ----------
    file_path : Path
        Absolute path to the CSV file.

    Returns
    -------
    pd.DataFrame
        The loaded DataFrame.
    """
    df = pd.read_csv(file_path)
    log.info("Shape: %s", df.shape)
    log.info("Dtypes:\n%s", df.dtypes)
    log.info("Missing values:\n%s", df.isnull().sum())
    log.info("Duplicate rows: %d", df.duplicated().sum())
    return df


def explore_fund_master(df: pd.DataFrame) -> None:
    """Log unique values for fund houses, categories, sub-categories, and risk grades.

    Parameters
    ----------
    df : pd.DataFrame
        The fund_master DataFrame.
    """
    log.info("Unique fund houses: %s", sorted(df["fund_house"].unique()))
    log.info("Unique categories: %s", sorted(df["category"].unique()))
    log.info("Unique sub-categories: %s", sorted(df["sub_category"].unique()))
    log.info("Unique risk grades: %s", sorted(df["risk_category"].unique()))


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> None:
    """Check that all AMFI codes in fund_master also appear in nav_history.

    Parameters
    ----------
    fund_master : pd.DataFrame
        Fund master DataFrame.
    nav_history : pd.DataFrame
        NAV history DataFrame.
    """
    fund_codes = set(fund_master["amfi_code"].astype(str))
    nav_codes = set(nav_history["amfi_code"].astype(str))
    missing = fund_codes - nav_codes

    if not missing:
        log.info("All AMFI codes from fund_master exist in nav_history.")
    else:
        log.warning("Missing AMFI codes: %s", missing)


def main() -> None:
    """Run the full Day 1 data-ingestion pipeline."""
    log.info("=" * 50)
    log.info("BLUESTOCK MF DATA INGESTION")
    log.info("=" * 50)

    for file_name in DATASETS:
        file_path = RAW_DATA_DIR / file_name
        log.info("Loading: %s", file_name)
        try:
            load_and_profile(file_path)
        except Exception as exc:
            log.error("Error loading %s: %s", file_name, exc)

    log.info("=" * 50)
    log.info("FUND MASTER EXPLORATION")
    log.info("=" * 50)
    fund_master = pd.read_csv(RAW_DATA_DIR / "01_fund_master.csv")
    explore_fund_master(fund_master)

    log.info("=" * 50)
    log.info("AMFI CODE VALIDATION")
    log.info("=" * 50)
    nav_history = pd.read_csv(RAW_DATA_DIR / "02_nav_history.csv")
    validate_amfi_codes(fund_master, nav_history)

    log.info("Data ingestion completed successfully.")


if __name__ == "__main__":
    main()
