
"""
Day 1 - Data Ingestion Script
Bluestock Mutual Fund Capstone Project
"""

from pathlib import Path
import pandas as pd

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
    "10_benchmark_indices.csv"
]

print("\n==============================")
print(" BLUESTOCK MF DATA INGESTION ")
print("==============================\n")

for file_name in DATASETS:
    file_path = RAW_DATA_DIR / file_name

    print(f"\nLoading: {file_name}")

    try:
        df = pd.read_csv(file_path)

        print("-" * 60)
        print("Shape:")
        print(df.shape)

        print("\nDtypes:")
        print(df.dtypes)

        print("\nHead:")
        print(df.head())

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

        print("-" * 60)

    except Exception as e:
        print(f"Error loading {file_name}: {e}")

# Explore fund master
fund_master = pd.read_csv(RAW_DATA_DIR / "01_fund_master.csv")

print("\n==============================")
print(" FUND MASTER EXPLORATION ")
print("==============================\n")

print("Unique Fund Houses:")
print(sorted(fund_master["fund_house"].unique()))

print("\nUnique Categories:")
print(sorted(fund_master["category"].unique()))

print("\nUnique Sub-Categories:")
print(sorted(fund_master["sub_category"].unique()))

print("\nUnique Risk Grades:")
print(sorted(fund_master["risk_category"].unique()))

# Validate AMFI codes
nav_history = pd.read_csv(RAW_DATA_DIR / "02_nav_history.csv")

fund_codes = set(fund_master["amfi_code"].astype(str))
nav_codes = set(nav_history["amfi_code"].astype(str))

missing_codes = fund_codes - nav_codes

print("\n==============================")
print(" AMFI CODE VALIDATION ")
print("==============================\n")

if len(missing_codes) == 0:
    print("All AMFI codes from fund_master exist in nav_history.")
else:
    print("Missing AMFI Codes:")
    print(missing_codes)

print("\nData ingestion completed successfully.")
