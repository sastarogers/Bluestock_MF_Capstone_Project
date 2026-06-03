# Bluestock Mutual Fund Capstone

Data engineering and analytics project for Indian mutual fund datasets. The project ingests raw CSVs, fetches live NAV data, cleans Day 2 datasets, builds a SQLite star schema, and provides analytical SQL queries.

## Project Structure

```text
data/
  raw/          Raw source CSVs and fetched live NAV files
  processed/    Cleaned Day 2 CSV outputs
dashboard/      Future dashboard assets
notebooks/      Exploratory notebooks
reports/        Data quality and validation reports
scripts/        Ingestion, live NAV, and cleaning scripts
sql/            SQLite schema and analytical queries
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

If `python` is not available on your machine, use `python3` in the commands below.

## Day 1: Data Ingestion

Completed:

- Created project folder structure.
- Added `requirements.txt`.
- Loaded all 10 provided raw CSV datasets using Pandas.
- Printed shape, dtypes, head, missing values, and duplicate counts.
- Explored fund master values for fund houses, categories, sub-categories, and risk grades.
- Validated AMFI codes between `fund_master` and `nav_history`.
- Fetched live NAV data from `mfapi.in` for HDFC Top 100 Direct and five key schemes.

Run Day 1 ingestion:

```bash
python3 scripts/data_ingestion.py
```

Fetch live NAV data:

```bash
python3 scripts/live_nav_fetch.py
```

Day 1 report:

- `reports/day1_data_quality_summary.csv`

## Day 2: Cleaned Data and SQLite Warehouse

Completed:

- Cleaned `nav_history.csv`:
  - parsed dates
  - sorted by `amfi_code` and date
  - removed duplicate scheme-date rows
  - validated NAV values greater than zero
  - forward-filled missing calendar dates within each scheme
- Cleaned `investor_transactions.csv`:
  - parsed transaction dates
  - standardized transaction types to `SIP`, `Lumpsum`, and `Redemption`
  - validated positive transaction amounts
  - validated KYC status enum values
- Cleaned `scheme_performance.csv`:
  - converted return and risk metrics to numeric values
  - checked return anomalies
  - validated expense ratio range from `0.1%` to `2.5%`
- Wrote SQLite star schema with:
  - `dim_fund`
  - `dim_date`
  - `fact_nav`
  - `fact_transactions`
  - `fact_performance`
  - `fact_aum`
- Loaded cleaned data into `bluestock_mf.db`.
- Verified SQLite row counts against processed datasets.
- Added 10 analytical SQL queries.
- Added a Markdown data dictionary.

Run Day 2 cleaning and database build:

```bash
python3 scripts/day2_clean_sqlite.py
```

Day 2 deliverables:

- `data/processed/01_fund_master_clean.csv`
- `data/processed/02_nav_history_clean.csv`
- `data/processed/03_aum_by_fund_house_clean.csv`
- `data/processed/04_monthly_sip_inflows_clean.csv`
- `data/processed/05_category_inflows_clean.csv`
- `data/processed/06_industry_folio_count_clean.csv`
- `data/processed/07_scheme_performance_clean.csv`
- `data/processed/08_investor_transactions_clean.csv`
- `data/processed/09_portfolio_holdings_clean.csv`
- `data/processed/10_benchmark_indices_clean.csv`
- `bluestock_mf.db`
- `sql/schema.sql`
- `sql/queries.sql`
- `data_dictionary.md`

Day 2 reports:

- `reports/day2_data_quality_summary.csv`
- `reports/day2_sqlite_row_counts.csv`
- `reports/day2_scheme_performance_anomalies.csv`
- `reports/day2_invalid_transactions.csv`

## Validation Snapshot

Latest Day 2 run:

- NAV rows expanded from `46,000` raw rows to `64,320` daily cleaned rows.
- `18,320` missing calendar rows were forward-filled.
- `0` invalid transaction rows were excluded.
- `0` scheme performance anomalies were flagged.
- SQLite row counts matched all processed source datasets.

## SQL Usage

Open the SQLite database:

```bash
sqlite3 bluestock_mf.db
```

Run analytical queries from:

```bash
sql/queries.sql
```

Included examples:

- Top 5 funds by AUM
- Average NAV per month
- SIP YoY growth
- Transactions by state
- Funds with expense ratio below 1%
- Highest alpha funds
- Redemption pressure by fund
- Category inflows by month
- Latest NAV by fund
- Portfolio sector exposure

## Git History

Current milestone commits:

```bash
DAY 1: Project Setup + Data Ingestion (ETL)
Day 2: Cleaned data + SQLite DB loaded
```
