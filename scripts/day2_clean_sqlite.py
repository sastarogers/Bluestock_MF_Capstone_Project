"""
Day 2 - Clean raw datasets and load the SQLite warehouse.
"""

from pathlib import Path
import sqlite3

import pandas as pd
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
DB_PATH = BASE_DIR / "bluestock_mf.db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def date_key(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.strftime("%Y%m%d").astype("int64")


def clean_fund_master() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "01_fund_master.csv")
    df = df.drop_duplicates(subset=["amfi_code"]).copy()
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    numeric_cols = [
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values("amfi_code").reset_index(drop=True)
    return df


def clean_nav_history() -> tuple[pd.DataFrame, dict[str, int]]:
    df = pd.read_csv(RAW_DIR / "02_nav_history.csv")
    raw_rows = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["amfi_code", "date"])
    df = df[df["nav"] > 0]
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")
    df = df.sort_values(["amfi_code", "date"])

    filled_parts = []
    inserted_rows = 0
    for amfi_code, group in df.groupby("amfi_code", sort=True):
        group = group.set_index("date").sort_index()
        full_index = pd.date_range(group.index.min(), group.index.max(), freq="D")
        expanded = group.reindex(full_index)
        inserted_rows += len(expanded) - len(group)
        expanded["amfi_code"] = amfi_code
        expanded["nav"] = expanded["nav"].ffill()
        expanded = expanded.dropna(subset=["nav"])
        expanded.index.name = "date"
        filled_parts.append(expanded.reset_index())

    cleaned = pd.concat(filled_parts, ignore_index=True)
    cleaned["nav"] = cleaned["nav"].astype(float)
    cleaned["date_key"] = date_key(cleaned["date"])
    cleaned = cleaned[["amfi_code", "date", "date_key", "nav"]]
    cleaned = cleaned.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    metrics = {"raw_rows": raw_rows, "processed_rows": len(cleaned), "filled_calendar_rows": inserted_rows}
    return cleaned, metrics


def clean_aum() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv")
    df = df.drop_duplicates(subset=["date", "fund_house"]).copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_key"] = date_key(df["date"])
    for col in ["aum_lakh_crore", "aum_crore", "num_schemes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["aum_crore"] > 0]
    return df.sort_values(["date", "fund_house"]).reset_index(drop=True)


def clean_monthly_sip() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
    df = df.drop_duplicates(subset=["month"]).copy()
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df["month_key"] = df["month"].dt.strftime("%Y%m").astype("int64")
    for col in df.columns:
        if col not in ["month"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("month").reset_index(drop=True)


def clean_category_inflows() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "05_category_inflows.csv")
    df = df.drop_duplicates(subset=["month", "category"]).copy()
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df["month_key"] = df["month"].dt.strftime("%Y%m").astype("int64")
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")
    return df.sort_values(["month", "category"]).reset_index(drop=True)


def clean_industry_folio_count() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "06_industry_folio_count.csv")
    df = df.drop_duplicates(subset=["month"]).copy()
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df["month_key"] = df["month"].dt.strftime("%Y%m").astype("int64")
    for col in df.columns:
        if col not in ["month"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("month").reset_index(drop=True)


def clean_scheme_performance() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")
    numeric_cols = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    anomaly_rows = []
    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct"]
    for col in return_cols:
        bad = df[df[col].isna() | (df[col] < -100) | (df[col] > 100)]
        for _, row in bad.iterrows():
            anomaly_rows.append({"amfi_code": row["amfi_code"], "column": col, "value": row[col], "issue": "Return outside -100 to 100 or non-numeric"})

    bad_expense = df[df["expense_ratio_pct"].isna() | (df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    for _, row in bad_expense.iterrows():
        anomaly_rows.append({"amfi_code": row["amfi_code"], "column": "expense_ratio_pct", "value": row["expense_ratio_pct"], "issue": "Expense ratio outside 0.1 to 2.5 pct"})

    anomalies = pd.DataFrame(anomaly_rows, columns=["amfi_code", "column", "value", "issue"])
    df = df.drop_duplicates(subset=["amfi_code"]).sort_values("amfi_code").reset_index(drop=True)
    return df, anomalies


def clean_transactions() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(RAW_DIR / "08_investor_transactions.csv")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["date_key"] = date_key(df["transaction_date"])
    type_map = {
        "sip": "SIP",
        "s i p": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "redemption": "Redemption",
        "redeem": "Redemption",
    }
    df["transaction_type"] = (
        df["transaction_type"].astype(str).str.strip().str.lower().map(type_map).fillna(df["transaction_type"])
    )
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df["annual_income_lakh"] = pd.to_numeric(df["annual_income_lakh"], errors="coerce")

    valid_types = {"SIP", "Lumpsum", "Redemption"}
    valid_kyc = {"Verified", "Pending", "Rejected"}
    invalid = df[
        df["transaction_date"].isna()
        | ~df["transaction_type"].isin(valid_types)
        | (df["amount_inr"] <= 0)
        | df["amount_inr"].isna()
        | ~df["kyc_status"].isin(valid_kyc)
    ].copy()

    df = df[
        df["transaction_date"].notna()
        & df["transaction_type"].isin(valid_types)
        & (df["amount_inr"] > 0)
        & df["kyc_status"].isin(valid_kyc)
    ].copy()
    df = df.drop_duplicates().sort_values(["transaction_date", "investor_id", "amfi_code"]).reset_index(drop=True)
    df.insert(0, "transaction_id", range(1, len(df) + 1))
    return df, invalid


def clean_portfolio_holdings() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "09_portfolio_holdings.csv")
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce")
    df["date_key"] = date_key(df["portfolio_date"])
    for col in ["weight_pct", "market_value_cr", "current_price_inr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates(subset=["amfi_code", "stock_symbol", "portfolio_date"])
    return df.sort_values(["amfi_code", "stock_symbol"]).reset_index(drop=True)


def clean_benchmark_indices() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "10_benchmark_indices.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_key"] = date_key(df["date"])
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    df = df[df["close_value"] > 0].drop_duplicates(subset=["date", "index_name"])
    return df.sort_values(["date", "index_name"]).reset_index(drop=True)


def save_processed(datasets: dict[str, pd.DataFrame]) -> None:
    for file_name, df in datasets.items():
        out = df.copy()
        for col in out.select_dtypes(include=["datetime64[ns]"]).columns:
            out[col] = out[col].dt.strftime("%Y-%m-%d")
        out.to_csv(PROCESSED_DIR / file_name, index=False)


def build_dim_date(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    dates = []
    date_columns = [
        ("01_fund_master_clean.csv", "launch_date"),
        ("02_nav_history_clean.csv", "date"),
        ("03_aum_by_fund_house_clean.csv", "date"),
        ("08_investor_transactions_clean.csv", "transaction_date"),
        ("09_portfolio_holdings_clean.csv", "portfolio_date"),
        ("10_benchmark_indices_clean.csv", "date"),
    ]
    for dataset_name, column in date_columns:
        dates.extend(pd.to_datetime(datasets[dataset_name][column], errors="coerce").dropna().tolist())
    for dataset_name in ["04_monthly_sip_inflows_clean.csv", "05_category_inflows_clean.csv", "06_industry_folio_count_clean.csv"]:
        dates.extend(pd.to_datetime(datasets[dataset_name]["month"], errors="coerce").dropna().tolist())

    dim = pd.DataFrame({"date": sorted(pd.Series(dates).dropna().drop_duplicates())})
    dim["date_key"] = date_key(dim["date"])
    dim["year"] = dim["date"].dt.year
    dim["quarter"] = dim["date"].dt.quarter
    dim["month"] = dim["date"].dt.month
    dim["month_name"] = dim["date"].dt.month_name()
    dim["day"] = dim["date"].dt.day
    dim["day_of_week"] = dim["date"].dt.day_name()
    dim["is_weekend"] = dim["date"].dt.dayofweek >= 5
    return dim[["date_key", "date", "year", "quarter", "month", "month_name", "day", "day_of_week", "is_weekend"]]


def load_sqlite(datasets: dict[str, pd.DataFrame], dim_date: pd.DataFrame) -> pd.DataFrame:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_PATH.read_text())
    conn.close()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        dim_fund = datasets["01_fund_master_clean.csv"].copy()
        dim_fund.to_sql("dim_fund", conn, if_exists="append", index=False)
        dim_date.to_sql("dim_date", conn, if_exists="append", index=False)

        datasets["02_nav_history_clean.csv"].to_sql("fact_nav", conn, if_exists="append", index=False)
        datasets["08_investor_transactions_clean.csv"].to_sql("fact_transactions", conn, if_exists="append", index=False)
        datasets["07_scheme_performance_clean.csv"].to_sql("fact_performance", conn, if_exists="append", index=False)
        datasets["03_aum_by_fund_house_clean.csv"].to_sql("fact_aum", conn, if_exists="append", index=False)

        datasets["04_monthly_sip_inflows_clean.csv"].to_sql("monthly_sip_inflows", conn, if_exists="append", index=False)
        datasets["05_category_inflows_clean.csv"].to_sql("category_inflows", conn, if_exists="append", index=False)
        datasets["06_industry_folio_count_clean.csv"].to_sql("industry_folio_count", conn, if_exists="append", index=False)
        datasets["09_portfolio_holdings_clean.csv"].to_sql("portfolio_holdings", conn, if_exists="append", index=False)
        datasets["10_benchmark_indices_clean.csv"].to_sql("benchmark_indices", conn, if_exists="append", index=False)

        table_to_source = {
            "dim_fund": "01_fund_master_clean.csv",
            "dim_date": "dim_date",
            "fact_nav": "02_nav_history_clean.csv",
            "fact_transactions": "08_investor_transactions_clean.csv",
            "fact_performance": "07_scheme_performance_clean.csv",
            "fact_aum": "03_aum_by_fund_house_clean.csv",
            "monthly_sip_inflows": "04_monthly_sip_inflows_clean.csv",
            "category_inflows": "05_category_inflows_clean.csv",
            "industry_folio_count": "06_industry_folio_count_clean.csv",
            "portfolio_holdings": "09_portfolio_holdings_clean.csv",
            "benchmark_indices": "10_benchmark_indices_clean.csv",
        }
        rows = []
        for table, source in table_to_source.items():
            db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            source_count = len(dim_date) if source == "dim_date" else len(datasets[source])
            rows.append({"table_name": table, "source_name": source, "source_rows": source_count, "sqlite_rows": db_count, "matches": source_count == db_count})
    return pd.DataFrame(rows)


def write_quality_report(
    datasets: dict[str, pd.DataFrame],
    nav_metrics: dict[str, int],
    performance_anomalies: pd.DataFrame,
    invalid_transactions: pd.DataFrame,
    row_counts: pd.DataFrame,
) -> None:
    summary = pd.DataFrame(
        [
            {
                "check": "nav_history_positive_nav",
                "result": bool((datasets["02_nav_history_clean.csv"]["nav"] > 0).all()),
                "details": "All cleaned NAV values are greater than zero.",
            },
            {
                "check": "nav_history_calendar_fill",
                "result": True,
                "details": f"Expanded {nav_metrics['raw_rows']} raw rows to {nav_metrics['processed_rows']} daily rows; inserted {nav_metrics['filled_calendar_rows']} forward-filled calendar rows.",
            },
            {
                "check": "transaction_amount_positive",
                "result": bool((datasets["08_investor_transactions_clean.csv"]["amount_inr"] > 0).all()),
                "details": f"{len(invalid_transactions)} invalid transaction rows excluded.",
            },
            {
                "check": "transaction_type_enum",
                "result": set(datasets["08_investor_transactions_clean.csv"]["transaction_type"]).issubset({"SIP", "Lumpsum", "Redemption"}),
                "details": "Allowed values: SIP, Lumpsum, Redemption.",
            },
            {
                "check": "kyc_status_enum",
                "result": set(datasets["08_investor_transactions_clean.csv"]["kyc_status"]).issubset({"Verified", "Pending", "Rejected"}),
                "details": "Allowed values: Verified, Pending, Rejected.",
            },
            {
                "check": "scheme_performance_anomalies",
                "result": performance_anomalies.empty,
                "details": f"{len(performance_anomalies)} return/expense anomalies flagged.",
            },
            {
                "check": "sqlite_row_count_match",
                "result": bool(row_counts["matches"].all()),
                "details": "SQLite table counts match the processed datasets.",
            },
        ]
    )
    summary.to_csv(REPORTS_DIR / "day2_data_quality_summary.csv", index=False)
    performance_anomalies.to_csv(REPORTS_DIR / "day2_scheme_performance_anomalies.csv", index=False)
    invalid_transactions.to_csv(REPORTS_DIR / "day2_invalid_transactions.csv", index=False)
    row_counts.to_csv(REPORTS_DIR / "day2_sqlite_row_counts.csv", index=False)


def main() -> None:
    fund_master = clean_fund_master()
    nav_history, nav_metrics = clean_nav_history()
    aum = clean_aum()
    monthly_sip = clean_monthly_sip()
    category_inflows = clean_category_inflows()
    folio_count = clean_industry_folio_count()
    scheme_performance, performance_anomalies = clean_scheme_performance()
    transactions, invalid_transactions = clean_transactions()
    portfolio_holdings = clean_portfolio_holdings()
    benchmark_indices = clean_benchmark_indices()

    datasets = {
        "01_fund_master_clean.csv": fund_master,
        "02_nav_history_clean.csv": nav_history,
        "03_aum_by_fund_house_clean.csv": aum,
        "04_monthly_sip_inflows_clean.csv": monthly_sip,
        "05_category_inflows_clean.csv": category_inflows,
        "06_industry_folio_count_clean.csv": folio_count,
        "07_scheme_performance_clean.csv": scheme_performance,
        "08_investor_transactions_clean.csv": transactions,
        "09_portfolio_holdings_clean.csv": portfolio_holdings,
        "10_benchmark_indices_clean.csv": benchmark_indices,
    }

    dim_date = build_dim_date(datasets)
    save_processed(datasets)
    row_counts = load_sqlite(datasets, dim_date)
    write_quality_report(datasets, nav_metrics, performance_anomalies, invalid_transactions, row_counts)

    print("Day 2 processing complete.")
    print(f"Processed CSVs: {PROCESSED_DIR}")
    print(f"SQLite database: {DB_PATH}")
    print(row_counts.to_string(index=False))


if __name__ == "__main__":
    main()
