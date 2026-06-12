# Bluestock Mutual Fund Capstone

A comprehensive data engineering and analytics project for the Indian mutual fund industry. The project ingests 10 raw CSV datasets, fetches live NAV data, cleans and validates all sources, builds a SQLite star-schema warehouse, performs exploratory and performance analytics, and delivers an interactive Tableau dashboard.

## Features

- **ETL Pipeline** — Automated ingestion, cleaning, and loading of 10 datasets
- **Star-Schema Warehouse** — SQLite database with 2 dimensions and 9 fact/auxiliary tables
- **Exploratory Data Analysis** — 18 publication-quality charts with key findings
- **Performance Scorecard** — Composite 0–100 fund scoring (CAGR, Sharpe, Alpha, Expense, Drawdown)
- **Risk Analytics** — VaR/CVaR, rolling Sharpe, alpha/beta regression, max drawdown
- **Advanced Analytics** — Investor cohort analysis, SIP continuity, sector HHI concentration
- **Fund Recommender** — Rule-based recommendation engine by risk appetite
- **Tableau Dashboard** — 4-page interactive dashboard with 17 visualisations
- **Master Pipeline** — Single-command execution of all pipeline stages

## Project Structure

```text
bluestock_mf_capstone/
├── data/
│   ├── raw/                     10 source CSVs + live NAV files
│   └── processed/               Cleaned CSV outputs + dashboard data
├── dashboard/                   Tableau workbook, screenshots, logo
├── notebooks/
│   ├── EDA_Analysis.ipynb       Day 3 exploratory analysis
│   ├── Performance_Analytics.ipynb  Day 4 performance metrics
│   └── Advanced_Analytics.ipynb Day 6 advanced analytics
├── reports/
│   ├── charts/day3/             18 EDA charts (PNG)
│   ├── charts/day4/             Benchmark comparison chart
│   ├── Final_Report.pdf         15-20 page final report
│   ├── Bluestock_MF_Presentation.pptx  12-slide presentation
│   ├── fund_scorecard.csv       Composite fund scores
│   ├── alpha_beta.csv           Alpha/beta regression results
│   └── ...                      Additional analytics CSVs
├── scripts/
│   ├── run_pipeline.py          Master execution script
│   ├── data_ingestion.py        Day 1: data loading & profiling
│   ├── live_nav_fetch.py        Day 1: live NAV from mfapi.in
│   ├── day2_clean_sqlite.py     Day 2: cleaning + SQLite load
│   ├── day3_eda.py              Day 3: EDA charts + notebook
│   ├── day4_performance_analytics.py  Day 4: returns & scorecard
│   ├── build_tableau_data.py    Day 5: Tableau data export
│   ├── generate_tableau_workbook.py   Day 5: Tableau .twb generation
│   ├── generate_advanced_notebook.py  Day 6: advanced analytics
│   ├── recommender.py           Fund recommender engine
│   ├── generate_final_report.py Final PDF report generator
│   └── generate_presentation.py PPTX presentation generator
├── sql/
│   ├── schema.sql               Star-schema DDL
│   └── queries.sql              10 analytical SQL queries
├── data_dictionary.md           Full data dictionary
├── requirements.txt             Python dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.9+
- Tableau Desktop or Tableau Public (for dashboard)

### Installation

```bash
# Clone the repository
git clone https://github.com/sastarogers/Bluestock_MF_Capstone_Project.git
cd Bluestock_MF_Capstone_Project

# Install dependencies
pip install -r requirements.txt
```

## How to Run

### Full Pipeline (All Stages)

Run the entire pipeline from ingestion to report generation:

```bash
python3 scripts/run_pipeline.py
```

### Selective Execution

```bash
# List all pipeline stages
python3 scripts/run_pipeline.py --list

# Run from a specific stage onwards
python3 scripts/run_pipeline.py --stage 3

# Run only a single stage
python3 scripts/run_pipeline.py --only 4

# Skip optional stages (e.g., live NAV fetch)
python3 scripts/run_pipeline.py --skip-optional
```

### Pipeline Stages

| Stage | Script | Description |
|-------|--------|-------------|
| 1 | `data_ingestion.py` | Load and profile 10 raw CSV datasets |
| 2 | `live_nav_fetch.py` | Fetch live NAV from mfapi.in (optional, requires network) |
| 3 | `day2_clean_sqlite.py` | Clean datasets + build SQLite star schema |
| 4 | `day3_eda.py` | Generate 18 EDA charts + Jupyter notebook |
| 5 | `day4_performance_analytics.py` | Compute CAGR, Sharpe, alpha/beta, scorecard |
| 6 | `build_tableau_data.py` | Export flat CSVs for Tableau |
| 7 | `generate_tableau_workbook.py` | Generate .twb Tableau workbook |
| 8 | `generate_advanced_notebook.py` | Build Advanced Analytics notebook |
| 9 | `generate_final_report.py` | Generate Final_Report.pdf |
| 10 | `generate_presentation.py` | Generate 12-slide PPTX presentation |

### Individual Scripts

```bash
# Day 1: Data ingestion
python3 scripts/data_ingestion.py

# Day 1: Fetch live NAV
python3 scripts/live_nav_fetch.py

# Day 2: Clean + SQLite
python3 scripts/day2_clean_sqlite.py

# Day 3: EDA charts
python3 scripts/day3_eda.py

# Day 4: Performance analytics
python3 scripts/day4_performance_analytics.py

# Fund recommender (interactive or CLI)
python3 scripts/recommender.py
python3 scripts/recommender.py --risk High
```

## How to Open the Dashboard

The project includes a pre-built Tableau workbook at `dashboard/bluestock_mutual_funds_dashboard.twb`.

### Using Tableau Desktop

1. Open Tableau Desktop
2. File → Open → select `dashboard/bluestock_mutual_funds_dashboard.twb`
3. Data sources connect to CSVs in `data/processed/dashboard_data/`
4. Navigate between the 4 dashboard tabs

### Dashboard Pages

| Page | Title | Key Visuals |
|------|-------|-------------|
| 1 | Industry Overview | KPI cards, AUM timeline, fund house ranking |
| 2 | Fund Performance | Risk-return scatter, scorecard table, NAV vs benchmark |
| 3 | Investor Analytics | State map, transaction types, age groups, monthly volume |
| 4 | SIP & Market Trends | SIP vs Nifty overlay, category heatmap, YoY growth |

### Dashboard Screenshots

Screenshots are available in the `dashboard/` directory:
- `1. Industry Overview.png`
- `2. Fund Performance.png`
- `3. Investor Analytics.png`
- `4. SIP & Market Trends.png`

A PDF export is also available: `dashboard/bluestock_mutual_funds_dashboard.pdf`

## Dataset Descriptions

| # | Dataset | Records | Description |
|---|---------|---------|-------------|
| 01 | Fund Master | 40 | Scheme metadata: fund house, category, risk grade, expense ratio, manager |
| 02 | NAV History | 46,000 → 64,320 | Daily NAV values per scheme (calendar forward-filled) |
| 03 | AUM by Fund House | ~80 | Quarterly AUM in crore and lakh crore |
| 04 | Monthly SIP Inflows | 48 | Monthly SIP inflow, active accounts, YoY growth |
| 05 | Category Inflows | ~240 | Net inflows by fund category per month |
| 06 | Industry Folio Count | 12 | Total, equity, debt, hybrid folio counts |
| 07 | Scheme Performance | 40 | Returns, alpha, beta, Sharpe, Sortino, expense ratio |
| 08 | Investor Transactions | 50,000 | Individual transactions with demographics |
| 09 | Portfolio Holdings | ~400 | Stock-level fund compositions with weights |
| 10 | Benchmark Indices | ~4,000 | NIFTY50, NIFTY100, and other index daily closes |

Full field-level documentation: [`data_dictionary.md`](data_dictionary.md)

## Reports & Deliverables

| Deliverable | Path | Description |
|-------------|------|-------------|
| Final Report | `reports/Final_Report.pdf` | 15-20 page comprehensive PDF report |
| Presentation | `reports/Bluestock_MF_Presentation.pptx` | 12-slide capstone presentation |
| Fund Scorecard | `reports/fund_scorecard.csv` | Composite 0-100 scores for all 40 funds |
| Alpha/Beta | `reports/alpha_beta.csv` | OLS regression results vs NIFTY100 |
| CAGR Comparison | `reports/cagr_comparison.csv` | 1/3/5-year CAGR for all funds |
| Risk Ratios | `reports/risk_ratios.csv` | Sharpe, Sortino, annualised metrics |
| Max Drawdown | `reports/max_drawdown.csv` | Drawdown peaks, troughs, recovery |
| VaR/CVaR | `reports/var_cvar_report.csv` | Value-at-Risk and Expected Shortfall |
| EDA Charts | `reports/charts/day3/*.png` | 18 exploratory analysis charts |
| Data Quality | `reports/day2_data_quality_summary.csv` | Validation check results |

## SQL Usage

Open the SQLite database directly:

```bash
sqlite3 bluestock_mf.db
```

Run the included analytical queries:

```sql
-- Example: Top 5 funds by AUM
SELECT f.scheme_name, f.fund_house, p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;
```

All 10 queries are in [`sql/queries.sql`](sql/queries.sql).

## Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| Database | SQLite, SQLAlchemy |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Statistics | SciPy |
| Notebooks | Jupyter, nbformat |
| Dashboard | Tableau Desktop |
| Report Generation | fpdf2, python-pptx |
| API | requests (mfapi.in) |

## Git History

```text
DAY 1: Project Setup + Data Ingestion (ETL)
Day 2: Cleaned data + SQLite DB loaded
Day 3: EDA analysis and chart exports
Day 4: Performance analytics scorecard
Day 5: Tableau Dashboard (4-page interactive)
Day 6: Advanced Analytics (VaR, Sharpe, Cohort, HHI)
Final: Complete Bluestock MF Capstone
```

## License

This project is developed as a capstone project for educational purposes.
