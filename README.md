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

## Day 3: Exploratory Data Analysis

Completed:

- Built `notebooks/EDA_Analysis.ipynb`.
- Exported 18 PNG charts for the final report.
- Plotted daily NAV trends for all 40 schemes with 2023 bull-run and 2024 correction windows.
- Created AUM growth, SIP inflow, category inflow, demographics, geography, folio growth, NAV correlation, sector allocation, and risk-return visuals.
- Documented 10 EDA findings in notebook Markdown cells.

Run Day 3 EDA generation:

```bash
python3 scripts/day3_eda.py
```

Day 3 deliverables:

- `notebooks/EDA_Analysis.ipynb`
- `reports/charts/day3/*.png`

Exported chart set:

- Daily NAV trend for all 40 schemes
- Indexed NAV growth
- AUM growth by fund house
- Latest AUM ranking
- SIP inflow time series
- SIP inflow vs active accounts
- Category inflow heatmap
- Total category inflows
- Age group distribution
- SIP amount by age group
- Gender split
- SIP amount by state
- T30 vs B30 city tier split
- Folio count growth
- NAV return correlation heatmap
- Sector allocation donut
- Risk-return scatter
- Expense ratio vs 3-year return

## Day 4: Performance Analytics

Completed:

- Computed daily returns for all 40 schemes using `nav_t / nav_t-1 - 1`.
- Validated daily return distributions for reasonable mean, volatility, min, and max ranges.
- Computed 1-year and 3-year NAV CAGR for all funds.
- Flagged true 5-year NAV CAGR as unavailable because the cleaned NAV history starts on `2022-01-03`.
- Computed Sharpe Ratio using a `6.5%` annual risk-free rate proxy.
- Computed Sortino Ratio using downside daily volatility.
- Computed alpha and beta against `NIFTY100` using `scipy.stats.linregress`.
- Computed maximum drawdown and drawdown date ranges for every fund.
- Built a 0-100 composite fund scorecard.
- Generated a 3-year benchmark comparison chart for the top 5 scorecard funds against `NIFTY50` and `NIFTY100`.
- Computed tracking error versus `NIFTY50` and `NIFTY100`.

Run Day 4 performance analytics:

```bash
python3 scripts/day4_performance_analytics.py
```

Day 4 deliverables:

- `notebooks/Performance_Analytics.ipynb`
- `reports/fund_scorecard.csv`
- `reports/alpha_beta.csv`
- `reports/charts/day4/benchmark_comparison_top5_vs_indices.png`

Additional Day 4 outputs:

- `reports/daily_returns.csv`
- `reports/daily_return_distribution.csv`
- `reports/cagr_comparison.csv`
- `reports/risk_ratios.csv`
- `reports/max_drawdown.csv`
- `reports/benchmark_tracking_error.csv`

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
Update README with Day 2 workflow
Day 3: EDA analysis and chart exports
Day 4: Performance analytics scorecard
```
