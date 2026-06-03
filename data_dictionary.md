# Bluestock MF Data Dictionary

This dictionary documents the cleaned Day 2 datasets in `data/processed/` and the SQLite warehouse in `bluestock_mf.db`.

## Source Mapping

| Processed file | SQLite table | Raw source | Business grain |
|---|---|---|---|
| `01_fund_master_clean.csv` | `dim_fund` | `data/raw/01_fund_master.csv` | One row per AMFI scheme code |
| `02_nav_history_clean.csv` | `fact_nav` | `data/raw/02_nav_history.csv` | One row per AMFI scheme per calendar date |
| `03_aum_by_fund_house_clean.csv` | `fact_aum` | `data/raw/03_aum_by_fund_house.csv` | One row per fund house per reporting date |
| `04_monthly_sip_inflows_clean.csv` | `monthly_sip_inflows` | `data/raw/04_monthly_sip_inflows.csv` | One row per month |
| `05_category_inflows_clean.csv` | `category_inflows` | `data/raw/05_category_inflows.csv` | One row per month and category |
| `06_industry_folio_count_clean.csv` | `industry_folio_count` | `data/raw/06_industry_folio_count.csv` | One row per month |
| `07_scheme_performance_clean.csv` | `fact_performance` | `data/raw/07_scheme_performance.csv` | One row per AMFI scheme code |
| `08_investor_transactions_clean.csv` | `fact_transactions` | `data/raw/08_investor_transactions.csv` | One row per investor transaction |
| `09_portfolio_holdings_clean.csv` | `portfolio_holdings` | `data/raw/09_portfolio_holdings.csv` | One row per scheme, stock, and portfolio date |
| `10_benchmark_indices_clean.csv` | `benchmark_indices` | `data/raw/10_benchmark_indices.csv` | One row per benchmark index per date |

## Shared Keys

| Column | Type | Definition |
|---|---|---|
| `amfi_code` | Integer | AMFI scheme identifier. Used as the primary key in `dim_fund` and foreign key in fund-level facts. |
| `date_key` | Integer | Calendar date key in `YYYYMMDD` format. Used to join facts to `dim_date`. |
| `month_key` | Integer | Calendar month key in `YYYYMM` format for monthly auxiliary tables. |

## `dim_fund`

| Column | Type | Business definition |
|---|---|---|
| `amfi_code` | Integer | Unique AMFI scheme code. |
| `fund_house` | Text | Asset management company or fund house. |
| `scheme_name` | Text | Full mutual fund scheme name. |
| `category` | Text | High-level category such as Equity or Debt. |
| `sub_category` | Text | SEBI-style product sub-category such as Large Cap, Liquid, ELSS, or Flexi Cap. |
| `plan` | Text | Plan type, usually Regular or Direct. |
| `launch_date` | Date | Scheme launch date. |
| `benchmark` | Text | Benchmark index used for comparison. |
| `expense_ratio_pct` | Real | Annual expense ratio percentage. |
| `exit_load_pct` | Real | Exit load percentage. |
| `min_sip_amount` | Real | Minimum SIP investment amount in INR. |
| `min_lumpsum_amount` | Real | Minimum one-time investment amount in INR. |
| `fund_manager` | Text | Named fund manager. |
| `risk_category` | Text | Risk label for the scheme. |
| `sebi_category_code` | Text | Internal category code aligned to SEBI-style classification. |

## `dim_date`

| Column | Type | Business definition |
|---|---|---|
| `date_key` | Integer | Primary date key in `YYYYMMDD` format. |
| `date` | Date | Calendar date. |
| `year` | Integer | Calendar year. |
| `quarter` | Integer | Calendar quarter. |
| `month` | Integer | Calendar month number. |
| `month_name` | Text | Calendar month name. |
| `day` | Integer | Day of month. |
| `day_of_week` | Text | Weekday name. |
| `is_weekend` | Boolean | Weekend flag based on Saturday/Sunday. |

## `fact_nav`

| Column | Type | Business definition |
|---|---|---|
| `amfi_code` | Integer | Fund scheme key. |
| `date` | Date | NAV calendar date. |
| `date_key` | Integer | Foreign key to `dim_date`. |
| `nav` | Real | Net asset value. Cleaned NAV values must be greater than zero. Missing calendar dates are forward-filled within each scheme. |

## `fact_transactions`

| Column | Type | Business definition |
|---|---|---|
| `transaction_id` | Integer | Generated unique transaction key. |
| `investor_id` | Text | Investor identifier. |
| `transaction_date` | Date | Transaction date. |
| `amfi_code` | Integer | Fund scheme key. |
| `transaction_type` | Text | Standardized transaction type: `SIP`, `Lumpsum`, or `Redemption`. |
| `amount_inr` | Real | Transaction amount in INR. Must be greater than zero. |
| `state` | Text | Investor state. |
| `city` | Text | Investor city. |
| `city_tier` | Text | T30/B30 city tier label. |
| `age_group` | Text | Investor age band. |
| `gender` | Text | Investor gender category. |
| `annual_income_lakh` | Real | Annual investor income in INR lakh. |
| `payment_mode` | Text | Payment method. |
| `kyc_status` | Text | KYC status. Allowed values: `Verified`, `Pending`, `Rejected`. |
| `date_key` | Integer | Foreign key to `dim_date`. |

## `fact_performance`

| Column | Type | Business definition |
|---|---|---|
| `amfi_code` | Integer | Fund scheme key. |
| `scheme_name` | Text | Scheme name copied from performance source. |
| `fund_house` | Text | Fund house. |
| `category` | Text | Performance category. |
| `plan` | Text | Plan type. |
| `return_1yr_pct` | Real | One-year trailing return percentage. |
| `return_3yr_pct` | Real | Three-year trailing return percentage. |
| `return_5yr_pct` | Real | Five-year trailing return percentage. |
| `benchmark_3yr_pct` | Real | Three-year benchmark return percentage. |
| `alpha` | Real | Excess return measure versus benchmark. |
| `beta` | Real | Market sensitivity measure. |
| `sharpe_ratio` | Real | Risk-adjusted return ratio. |
| `sortino_ratio` | Real | Downside-risk-adjusted return ratio. |
| `std_dev_ann_pct` | Real | Annualized standard deviation percentage. |
| `max_drawdown_pct` | Real | Maximum drawdown percentage. |
| `aum_crore` | Real | Scheme AUM in INR crore. |
| `expense_ratio_pct` | Real | Expense ratio percentage. Validated range: 0.1 to 2.5. |
| `morningstar_rating` | Integer | Rating score. |
| `risk_grade` | Text | Risk grade from performance source. |

## `fact_aum`

| Column | Type | Business definition |
|---|---|---|
| `date` | Date | AUM reporting date. |
| `fund_house` | Text | Fund house. |
| `aum_lakh_crore` | Real | AUM in INR lakh crore. |
| `aum_crore` | Real | AUM in INR crore. Must be greater than zero. |
| `num_schemes` | Integer | Number of schemes for the fund house. |
| `date_key` | Integer | Foreign key to `dim_date`. |

## Auxiliary Tables

| Table | Column | Type | Business definition |
|---|---|---|---|
| `monthly_sip_inflows` | `month` | Date | First day of reporting month. |
| `monthly_sip_inflows` | `sip_inflow_crore` | Real | Monthly SIP inflow in INR crore. |
| `monthly_sip_inflows` | `active_sip_accounts_crore` | Real | Active SIP accounts in crore. |
| `monthly_sip_inflows` | `new_sip_accounts_lakh` | Real | New SIP accounts in lakh. |
| `monthly_sip_inflows` | `sip_aum_lakh_crore` | Real | SIP AUM in INR lakh crore. |
| `monthly_sip_inflows` | `yoy_growth_pct` | Real | Year-over-year SIP inflow growth percentage. |
| `category_inflows` | `category` | Text | Mutual fund category. |
| `category_inflows` | `net_inflow_crore` | Real | Category-level monthly net inflow in INR crore. |
| `industry_folio_count` | `total_folios_crore` | Real | Total industry folio count in crore. |
| `industry_folio_count` | `equity_folios_crore` | Real | Equity folio count in crore. |
| `industry_folio_count` | `debt_folios_crore` | Real | Debt folio count in crore. |
| `industry_folio_count` | `hybrid_folios_crore` | Real | Hybrid folio count in crore. |
| `industry_folio_count` | `others_folios_crore` | Real | Other folio count in crore. |
| `portfolio_holdings` | `stock_symbol` | Text | Listed security ticker. |
| `portfolio_holdings` | `stock_name` | Text | Security name. |
| `portfolio_holdings` | `sector` | Text | Security sector. |
| `portfolio_holdings` | `weight_pct` | Real | Portfolio weight percentage. |
| `portfolio_holdings` | `market_value_cr` | Real | Holding market value in INR crore. |
| `portfolio_holdings` | `current_price_inr` | Real | Current security price in INR. |
| `portfolio_holdings` | `portfolio_date` | Date | Portfolio disclosure date. |
| `benchmark_indices` | `index_name` | Text | Benchmark index name. |
| `benchmark_indices` | `close_value` | Real | Benchmark closing value. |

## Day 2 Validation Rules

| Area | Rule |
|---|---|
| NAV history | Dates parsed, rows sorted by `amfi_code` and `date`, duplicate scheme-date rows removed, calendar gaps forward-filled, NAV must be greater than zero. |
| Investor transactions | Dates parsed, transaction type standardized, amount must be greater than zero, KYC status must be one of the allowed enum values. |
| Scheme performance | Return and risk fields parsed as numeric, returns outside -100 to 100 flagged, expense ratio must be between 0.1 and 2.5 percent. |
| SQLite load | Row counts are verified between processed CSVs and SQLite tables in `reports/day2_sqlite_row_counts.csv`. |
