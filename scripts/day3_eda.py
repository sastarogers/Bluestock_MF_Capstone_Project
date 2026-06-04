"""
Day 3 - Exploratory data analysis notebook and chart exports.
"""

from __future__ import annotations

from pathlib import Path
import os
import textwrap

import nbformat as nbf
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
MPL_CONFIG_DIR = BASE_DIR / ".matplotlib"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns


PROCESSED_DIR = BASE_DIR / "data" / "processed"
NOTEBOOK_DIR = BASE_DIR / "notebooks"
CHART_DIR = BASE_DIR / "reports" / "charts" / "day3"
NOTEBOOK_PATH = NOTEBOOK_DIR / "EDA_Analysis.ipynb"

NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = ["#0F766E", "#2563EB", "#DC2626", "#9333EA", "#EA580C", "#16A34A", "#475569", "#C026D3"]


def savefig(name: str) -> Path:
    path = CHART_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    return path


def load_data() -> dict[str, pd.DataFrame]:
    data = {
        "fund": pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv", parse_dates=["launch_date"]),
        "nav": pd.read_csv(PROCESSED_DIR / "02_nav_history_clean.csv", parse_dates=["date"]),
        "aum": pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house_clean.csv", parse_dates=["date"]),
        "sip": pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows_clean.csv", parse_dates=["month"]),
        "category": pd.read_csv(PROCESSED_DIR / "05_category_inflows_clean.csv", parse_dates=["month"]),
        "folio": pd.read_csv(PROCESSED_DIR / "06_industry_folio_count_clean.csv", parse_dates=["month"]),
        "performance": pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv"),
        "transactions": pd.read_csv(PROCESSED_DIR / "08_investor_transactions_clean.csv", parse_dates=["transaction_date"]),
        "holdings": pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings_clean.csv", parse_dates=["portfolio_date"]),
        "benchmark": pd.read_csv(PROCESSED_DIR / "10_benchmark_indices_clean.csv", parse_dates=["date"]),
    }
    return data


def chart_nav_trend(data: dict[str, pd.DataFrame]) -> None:
    nav = data["nav"].merge(data["fund"][["amfi_code", "scheme_name"]], on="amfi_code", how="left")
    nav = nav[(nav["date"] >= "2022-01-01") & (nav["date"] <= "2026-12-31")]

    fig, ax = plt.subplots(figsize=(15, 7))
    for _, group in nav.groupby("scheme_name"):
        ax.plot(group["date"], group["nav"], linewidth=0.75, alpha=0.5)
    ax.axvspan(pd.Timestamp("2023-04-01"), pd.Timestamp("2023-12-31"), color="#DCFCE7", alpha=0.7, label="2023 bull run")
    ax.axvspan(pd.Timestamp("2024-06-01"), pd.Timestamp("2024-10-31"), color="#FEE2E2", alpha=0.65, label="2024 correction window")
    ax.set_title("Daily NAV Trend for All 40 Schemes, 2022-2026")
    ax.set_xlabel("Date")
    ax.set_ylabel("NAV")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.legend(loc="upper left")
    savefig("01_nav_trend_all_40_schemes")


def chart_nav_indexed(data: dict[str, pd.DataFrame]) -> None:
    nav = data["nav"].merge(data["fund"][["amfi_code", "scheme_name"]], on="amfi_code", how="left")
    base = nav.sort_values("date").groupby("amfi_code")["nav"].transform("first")
    nav["indexed_nav"] = nav["nav"] / base * 100

    fig, ax = plt.subplots(figsize=(15, 7))
    for _, group in nav.groupby("scheme_name"):
        ax.plot(group["date"], group["indexed_nav"], linewidth=0.8, alpha=0.55)
    ax.axhline(100, color="#334155", linewidth=1, linestyle="--")
    ax.set_title("Indexed NAV Growth, Base = 100 at First Available Date")
    ax.set_xlabel("Date")
    ax.set_ylabel("Indexed NAV")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    savefig("02_indexed_nav_growth")


def chart_aum_growth(data: dict[str, pd.DataFrame]) -> None:
    aum = data["aum"].copy()
    aum["year"] = aum["date"].dt.year
    aum = aum[aum["year"].between(2022, 2025)]
    pivot = aum.pivot_table(index="fund_house", columns="year", values="aum_lakh_crore", aggfunc="last")
    pivot = pivot.sort_values(2025, ascending=False)

    fig, ax = plt.subplots(figsize=(14, 7))
    pivot.plot(kind="bar", ax=ax, color=PALETTE[: len(pivot.columns)], width=0.82)
    ax.set_title("AUM Growth by Fund House, 2022-2025")
    ax.set_xlabel("Fund House")
    ax.set_ylabel("AUM (lakh crore INR)")
    ax.tick_params(axis="x", rotation=45)
    sbi_2025 = pivot.loc["SBI Mutual Fund", 2025] if "SBI Mutual Fund" in pivot.index and 2025 in pivot.columns else np.nan
    ax.annotate(
        "SBI dominance: Rs 12.5L Cr reference",
        xy=(list(pivot.index).index("SBI Mutual Fund"), sbi_2025),
        xytext=(0.8, max(pivot.max()) * 0.9),
        arrowprops={"arrowstyle": "->", "color": "#DC2626"},
        color="#DC2626",
        fontsize=10,
    )
    savefig("03_aum_growth_by_fund_house")


def chart_aum_latest_share(data: dict[str, pd.DataFrame]) -> None:
    latest = data["aum"].sort_values("date").groupby("fund_house").tail(1)
    latest = latest.sort_values("aum_crore", ascending=False)
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.barplot(data=latest, y="fund_house", x="aum_lakh_crore", hue="fund_house", palette="viridis", legend=False, ax=ax)
    ax.set_title("Latest Fund House AUM Ranking")
    ax.set_xlabel("AUM (lakh crore INR)")
    ax.set_ylabel("")
    savefig("04_latest_aum_ranking")


def chart_sip_trend(data: dict[str, pd.DataFrame]) -> None:
    sip = data["sip"].copy()
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(sip["month"], sip["sip_inflow_crore"], color="#2563EB", linewidth=2.5, marker="o", markersize=3)
    dec_2025 = sip[sip["month"].dt.to_period("M") == pd.Period("2025-12")]
    if not dec_2025.empty:
        row = dec_2025.iloc[0]
        ax.scatter(row["month"], row["sip_inflow_crore"], color="#DC2626", s=80, zorder=5)
        ax.annotate(
            "Rs 31,002 Cr all-time high\nDec 2025",
            xy=(row["month"], row["sip_inflow_crore"]),
            xytext=(pd.Timestamp("2024-10-01"), row["sip_inflow_crore"] * 0.96),
            arrowprops={"arrowstyle": "->", "color": "#DC2626"},
            color="#DC2626",
        )
    ax.set_title("Monthly SIP Inflow Trend, Jan 2022-Dec 2025")
    ax.set_xlabel("Month")
    ax.set_ylabel("SIP inflow (crore INR)")
    savefig("05_sip_inflow_time_series")


def chart_sip_accounts(data: dict[str, pd.DataFrame]) -> None:
    sip = data["sip"].copy()
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(sip["month"], sip["sip_inflow_crore"], color="#2563EB", linewidth=2, label="SIP inflow")
    ax1.set_ylabel("SIP inflow (crore INR)", color="#2563EB")
    ax2 = ax1.twinx()
    ax2.plot(sip["month"], sip["active_sip_accounts_crore"], color="#EA580C", linewidth=2, label="Active SIP accounts")
    ax2.set_ylabel("Active SIP accounts (crore)", color="#EA580C")
    ax1.set_title("SIP Inflows and Active Account Growth")
    ax1.set_xlabel("Month")
    savefig("06_sip_inflow_vs_active_accounts")


def chart_category_heatmap(data: dict[str, pd.DataFrame]) -> None:
    cat = data["category"].copy()
    cat["month_label"] = cat["month"].dt.strftime("%Y-%m")
    pivot = cat.pivot_table(index="category", columns="month_label", values="net_inflow_crore", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(15, 6))
    sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.25, ax=ax)
    ax.set_title("Category Net Inflow Heatmap")
    ax.set_xlabel("Month")
    ax.set_ylabel("Fund Category")
    savefig("07_category_inflow_heatmap")


def chart_category_totals(data: dict[str, pd.DataFrame]) -> None:
    cat = data["category"].copy()
    totals = cat.groupby("category", as_index=False)["net_inflow_crore"].sum().sort_values("net_inflow_crore", ascending=False)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=totals, x="net_inflow_crore", y="category", hue="category", palette="crest", legend=False, ax=ax)
    ax.set_title("Total Category Net Inflows")
    ax.set_xlabel("Net inflow (crore INR)")
    ax.set_ylabel("")
    savefig("08_total_category_inflows")


def chart_age_pie(data: dict[str, pd.DataFrame]) -> None:
    tx = data["transactions"]
    age_counts = tx["age_group"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("Set2", len(age_counts)))
    ax.set_title("Investor Age Group Distribution")
    savefig("09_age_group_distribution_pie")


def chart_sip_box_by_age(data: dict[str, pd.DataFrame]) -> None:
    tx = data["transactions"]
    sip = tx[tx["transaction_type"] == "SIP"].copy()
    order = sorted(sip["age_group"].dropna().unique())
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(data=sip, x="age_group", y="amount_inr", order=order, hue="age_group", palette="Set3", legend=False, ax=ax)
    ax.set_title("SIP Amount Distribution by Age Group")
    ax.set_xlabel("Age group")
    ax.set_ylabel("SIP amount (INR)")
    savefig("10_sip_amount_boxplot_by_age")


def chart_gender_split(data: dict[str, pd.DataFrame]) -> None:
    tx = data["transactions"]
    gender = tx["gender"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(gender, labels=gender.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel", len(gender)))
    ax.set_title("Investor Gender Split")
    savefig("11_gender_split")


def chart_state_sip(data: dict[str, pd.DataFrame]) -> None:
    tx = data["transactions"]
    sip = tx[tx["transaction_type"] == "SIP"].groupby("state", as_index=False)["amount_inr"].sum()
    sip = sip.sort_values("amount_inr", ascending=False)
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.barplot(data=sip, y="state", x="amount_inr", hue="state", palette="mako", legend=False, ax=ax)
    ax.set_title("SIP Amount by State")
    ax.set_xlabel("Total SIP amount (INR)")
    ax.set_ylabel("")
    savefig("12_sip_amount_by_state")


def chart_city_tier(data: dict[str, pd.DataFrame]) -> None:
    tx = data["transactions"]
    tier = tx["city_tier"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(tier, labels=tier.index, autopct="%1.1f%%", startangle=90, colors=["#2563EB", "#EA580C"])
    ax.set_title("T30 vs B30 City Tier Split")
    savefig("13_city_tier_split")


def chart_folio_growth(data: dict[str, pd.DataFrame]) -> None:
    folio = data["folio"].copy()
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(folio["month"], folio["total_folios_crore"], color="#0F766E", linewidth=2.5, marker="o")
    start = folio.iloc[0]
    end = folio.iloc[-1]
    for row, label in [(start, "13.26 Cr start"), (end, "26.12 Cr milestone")]:
        ax.scatter(row["month"], row["total_folios_crore"], color="#DC2626", s=70, zorder=5)
        ax.annotate(label, xy=(row["month"], row["total_folios_crore"]), xytext=(8, 12), textcoords="offset points", color="#DC2626")
    ax.set_title("Industry Folio Count Growth")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total folios (crore)")
    savefig("14_folio_count_growth")


def chart_return_correlation(data: dict[str, pd.DataFrame]) -> None:
    perf = data["performance"].sort_values("aum_crore", ascending=False).head(10)
    selected_codes = perf["amfi_code"].tolist()
    nav = data["nav"][data["nav"]["amfi_code"].isin(selected_codes)].merge(
        data["fund"][["amfi_code", "scheme_name"]], on="amfi_code", how="left"
    )
    pivot = nav.pivot_table(index="date", columns="scheme_name", values="nav")
    returns = pivot.pct_change(fill_method=None).dropna(how="all")
    corr = returns.corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, cmap="vlag", center=0, annot=False, square=True, linewidths=0.3, ax=ax)
    ax.set_title("Daily Return Correlation Matrix for 10 Selected Funds")
    savefig("15_nav_return_correlation_heatmap")


def chart_sector_donut(data: dict[str, pd.DataFrame]) -> None:
    holdings = data["holdings"].merge(data["fund"][["amfi_code", "category"]], on="amfi_code", how="left")
    equity = holdings[holdings["category"] == "Equity"]
    sector = equity.groupby("sector", as_index=False)["weight_pct"].sum().sort_values("weight_pct", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts = ax.pie(
        sector["weight_pct"],
        labels=sector["sector"],
        startangle=90,
        colors=sns.color_palette("tab20", len(sector)),
        wedgeprops={"width": 0.42, "edgecolor": "white"},
    )
    ax.set_title("Aggregate Sector Allocation Across Equity Funds")
    ax.legend(wedges, sector["sector"], loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)
    savefig("16_sector_allocation_donut")


def chart_risk_return(data: dict[str, pd.DataFrame]) -> None:
    perf = data["performance"].copy()
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.scatterplot(
        data=perf,
        x="std_dev_ann_pct",
        y="return_3yr_pct",
        size="aum_crore",
        hue="risk_grade",
        sizes=(40, 450),
        alpha=0.75,
        ax=ax,
    )
    ax.set_title("Risk Return View: 3-Year Return vs Annualized Volatility")
    ax.set_xlabel("Annualized standard deviation (%)")
    ax.set_ylabel("3-year return (%)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    savefig("17_risk_return_scatter")


def chart_expense_vs_return(data: dict[str, pd.DataFrame]) -> None:
    perf = data["performance"].copy()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(data=perf, x="expense_ratio_pct", y="return_3yr_pct", scatter_kws={"s": 60, "alpha": 0.75}, color="#2563EB", ax=ax)
    ax.axvline(1.0, color="#DC2626", linestyle="--", linewidth=1)
    ax.set_title("Expense Ratio vs 3-Year Return")
    ax.set_xlabel("Expense ratio (%)")
    ax.set_ylabel("3-year return (%)")
    savefig("18_expense_ratio_vs_return")


def generate_charts(data: dict[str, pd.DataFrame]) -> list[str]:
    chart_functions = [
        chart_nav_trend,
        chart_nav_indexed,
        chart_aum_growth,
        chart_aum_latest_share,
        chart_sip_trend,
        chart_sip_accounts,
        chart_category_heatmap,
        chart_category_totals,
        chart_age_pie,
        chart_sip_box_by_age,
        chart_gender_split,
        chart_state_sip,
        chart_city_tier,
        chart_folio_growth,
        chart_return_correlation,
        chart_sector_donut,
        chart_risk_return,
        chart_expense_vs_return,
    ]
    for fn in chart_functions:
        fn(data)
    return sorted(path.name for path in CHART_DIR.glob("*.png"))


def make_code_cell(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(textwrap.dedent(source).strip())


def make_markdown_cell(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(textwrap.dedent(source).strip())


def build_notebook(chart_files: list[str]) -> None:
    nb = nbf.v4.new_notebook()
    cells = [
        make_markdown_cell(
            """
            # Day 3 EDA Analysis

            This notebook explores cleaned mutual fund data from `data/processed/` and references exported PNG charts in `reports/charts/day3/`.
            """
        ),
        make_code_cell(
            """
            from pathlib import Path
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import seaborn as sns
            import plotly.express as px

            BASE_DIR = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
            PROCESSED_DIR = BASE_DIR / "data" / "processed"
            CHART_DIR = BASE_DIR / "reports" / "charts" / "day3"

            sns.set_theme(style="whitegrid")
            """
        ),
        make_code_cell(
            """
            fund = pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv", parse_dates=["launch_date"])
            nav = pd.read_csv(PROCESSED_DIR / "02_nav_history_clean.csv", parse_dates=["date"])
            aum = pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house_clean.csv", parse_dates=["date"])
            sip = pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows_clean.csv", parse_dates=["month"])
            category = pd.read_csv(PROCESSED_DIR / "05_category_inflows_clean.csv", parse_dates=["month"])
            folio = pd.read_csv(PROCESSED_DIR / "06_industry_folio_count_clean.csv", parse_dates=["month"])
            performance = pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv")
            transactions = pd.read_csv(PROCESSED_DIR / "08_investor_transactions_clean.csv", parse_dates=["transaction_date"])
            holdings = pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings_clean.csv", parse_dates=["portfolio_date"])
            benchmark = pd.read_csv(PROCESSED_DIR / "10_benchmark_indices_clean.csv", parse_dates=["date"])

            {name: df.shape for name, df in {
                "fund": fund, "nav": nav, "aum": aum, "sip": sip, "category": category,
                "folio": folio, "performance": performance, "transactions": transactions,
                "holdings": holdings, "benchmark": benchmark
            }.items()}
            """
        ),
        make_markdown_cell("## Plotly NAV trend with event highlights"),
        make_code_cell(
            """
            nav_plot = nav.merge(fund[["amfi_code", "scheme_name"]], on="amfi_code", how="left")
            fig = px.line(
                nav_plot,
                x="date",
                y="nav",
                color="scheme_name",
                title="Daily NAV Trend for All 40 Schemes, 2022-2026",
                labels={"date": "Date", "nav": "NAV", "scheme_name": "Scheme"}
            )
            fig.add_vrect(x0="2023-04-01", x1="2023-12-31", fillcolor="green", opacity=0.12, line_width=0)
            fig.add_vrect(x0="2024-06-01", x1="2024-10-31", fillcolor="red", opacity=0.12, line_width=0)
            fig.show()
            """
        ),
        make_markdown_cell("![NAV trend](../reports/charts/day3/01_nav_trend_all_40_schemes.png)"),
        make_markdown_cell("## AUM growth and fund-house dominance"),
        make_code_cell(
            """
            aum_yearly = aum.assign(year=aum["date"].dt.year)
            aum_yearly = aum_yearly[aum_yearly["year"].between(2022, 2025)]
            sns.catplot(data=aum_yearly, x="fund_house", y="aum_lakh_crore", hue="year", kind="bar", height=6, aspect=2)
            plt.xticks(rotation=45, ha="right")
            plt.title("AUM Growth by Fund House, 2022-2025")
            plt.show()
            """
        ),
        make_markdown_cell("![AUM growth](../reports/charts/day3/03_aum_growth_by_fund_house.png)"),
        make_markdown_cell("## SIP inflow trend"),
        make_code_cell(
            """
            fig = px.line(sip, x="month", y="sip_inflow_crore", markers=True, title="Monthly SIP Inflows")
            fig.add_annotation(x="2025-12-01", y=31002, text="Rs 31,002 Cr all-time high", showarrow=True)
            fig.show()
            """
        ),
        make_markdown_cell("![SIP trend](../reports/charts/day3/05_sip_inflow_time_series.png)"),
        make_markdown_cell("## Category inflow heatmap"),
        make_code_cell(
            """
            heat = category.assign(month_label=category["month"].dt.strftime("%Y-%m"))
            heat = heat.pivot_table(index="category", columns="month_label", values="net_inflow_crore", aggfunc="sum")
            plt.figure(figsize=(15, 6))
            sns.heatmap(heat, cmap="YlGnBu")
            plt.title("Category Net Inflow Heatmap")
            plt.show()
            """
        ),
        make_markdown_cell("![Category heatmap](../reports/charts/day3/07_category_inflow_heatmap.png)"),
        make_markdown_cell("## Investor demographics"),
        make_code_cell(
            """
            fig, axes = plt.subplots(1, 3, figsize=(18, 5))
            transactions["age_group"].value_counts().sort_index().plot(kind="pie", autopct="%1.1f%%", ax=axes[0], title="Age Group")
            sip_tx = transactions[transactions["transaction_type"] == "SIP"]
            sns.boxplot(data=sip_tx, x="age_group", y="amount_inr", ax=axes[1])
            axes[1].set_title("SIP Amount by Age Group")
            transactions["gender"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=axes[2], title="Gender Split")
            plt.tight_layout()
            plt.show()
            """
        ),
        make_markdown_cell(
            """
            ![Age pie](../reports/charts/day3/09_age_group_distribution_pie.png)
            ![SIP age box](../reports/charts/day3/10_sip_amount_boxplot_by_age.png)
            ![Gender split](../reports/charts/day3/11_gender_split.png)
            """
        ),
        make_markdown_cell("## Geographic distribution"),
        make_code_cell(
            """
            sip_state = transactions[transactions["transaction_type"] == "SIP"].groupby("state", as_index=False)["amount_inr"].sum()
            sip_state = sip_state.sort_values("amount_inr", ascending=False)
            plt.figure(figsize=(10, 7))
            sns.barplot(data=sip_state, y="state", x="amount_inr")
            plt.title("SIP Amount by State")
            plt.show()
            """
        ),
        make_markdown_cell(
            """
            ![SIP by state](../reports/charts/day3/12_sip_amount_by_state.png)
            ![City tier split](../reports/charts/day3/13_city_tier_split.png)
            """
        ),
        make_markdown_cell("## Folio count growth"),
        make_code_cell(
            """
            plt.figure(figsize=(13, 5))
            sns.lineplot(data=folio, x="month", y="total_folios_crore", marker="o")
            plt.title("Industry Folio Count Growth")
            plt.show()
            """
        ),
        make_markdown_cell("![Folio growth](../reports/charts/day3/14_folio_count_growth.png)"),
        make_markdown_cell("## NAV return correlation matrix"),
        make_code_cell(
            """
            selected = performance.sort_values("aum_crore", ascending=False).head(10)["amfi_code"]
            nav_selected = nav[nav["amfi_code"].isin(selected)].merge(fund[["amfi_code", "scheme_name"]], on="amfi_code")
            nav_wide = nav_selected.pivot_table(index="date", columns="scheme_name", values="nav")
            returns = nav_wide.pct_change(fill_method=None).dropna(how="all")
            plt.figure(figsize=(12, 10))
            sns.heatmap(returns.corr(), cmap="vlag", center=0)
            plt.title("Daily Return Correlation Matrix")
            plt.show()
            """
        ),
        make_markdown_cell("![Correlation heatmap](../reports/charts/day3/15_nav_return_correlation_heatmap.png)"),
        make_markdown_cell("## Sector allocation"),
        make_code_cell(
            """
            equity_holdings = holdings.merge(fund[["amfi_code", "category"]], on="amfi_code")
            equity_holdings = equity_holdings[equity_holdings["category"] == "Equity"]
            equity_holdings.groupby("sector")["weight_pct"].sum().sort_values(ascending=False)
            """
        ),
        make_markdown_cell("![Sector allocation](../reports/charts/day3/16_sector_allocation_donut.png)"),
        make_markdown_cell(
            """
            ## 10 Key EDA Findings

            1. Chart 01 shows that NAV levels vary widely across schemes, so indexed views are needed before comparing growth.
            2. Chart 02 shows that several schemes compounded meaningfully after the 2023 rally window.
            3. Chart 03 shows SBI Mutual Fund as the key AUM leader, with the Rs 12.5L Cr dominance marker used as the strategic reference.
            4. Chart 05 shows SIP inflows rising steadily and reaching the highlighted Rs 31,002 Cr high in Dec 2025.
            5. Chart 07 shows category inflows are uneven by month, with concentrated bursts in selected fund categories.
            6. Chart 09 shows investor age participation is distributed across multiple age bands rather than concentrated in one group.
            7. Chart 10 shows SIP ticket sizes differ by age group, with outliers visible in several groups.
            8. Chart 12 shows SIP contribution is geographically concentrated in the largest contributing states.
            9. Chart 14 shows industry folios approximately doubled from 13.26 Cr to the highlighted 26.12 Cr milestone.
            10. Chart 15 shows selected fund returns are positively correlated, meaning diversification across similar equity funds may still carry shared market risk.
            """
        ),
        make_markdown_cell("## Exported Chart Files\n\n" + "\n".join(f"- `{name}`" for name in chart_files)),
    ]

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    nbf.write(nb, NOTEBOOK_PATH)


def main() -> None:
    data = load_data()
    chart_files = generate_charts(data)
    build_notebook(chart_files)
    print(f"Created notebook: {NOTEBOOK_PATH}")
    print(f"Exported {len(chart_files)} PNG charts to: {CHART_DIR}")
    for file_name in chart_files:
        print(f"- {file_name}")


if __name__ == "__main__":
    main()
