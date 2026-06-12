"""Day 4 — Performance Analytics
===============================
Compute daily returns, CAGR, risk ratios, alpha/beta, drawdowns,
composite scorecards, and benchmark tracking error.

Usage:
    python3 scripts/day4_performance_analytics.py
"""

from __future__ import annotations

from pathlib import Path
import logging
import os
import textwrap

import nbformat as nbf
import numpy as np
import pandas as pd
from scipy.stats import linregress

BASE_DIR = Path(__file__).resolve().parents[1]
MPL_CONFIG_DIR = BASE_DIR / ".matplotlib"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
CHART_DIR = REPORTS_DIR / "charts" / "day4"
NOTEBOOK_DIR = BASE_DIR / "notebooks"
NOTEBOOK_PATH = NOTEBOOK_DIR / "Performance_Analytics.ipynb"

RISK_FREE_RATE = 0.065
TRADING_DAYS = 252

CHART_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")


def load_data() -> dict[str, pd.DataFrame]:
    """Load cleaned fund, NAV, performance, and benchmark datasets."""
    return {
        "fund": pd.read_csv(PROCESSED_DIR / "01_fund_master_clean.csv", parse_dates=["launch_date"]),
        "nav": pd.read_csv(PROCESSED_DIR / "02_nav_history_clean.csv", parse_dates=["date"]),
        "performance": pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv"),
        "benchmark": pd.read_csv(PROCESSED_DIR / "10_benchmark_indices_clean.csv", parse_dates=["date"]),
    }


def compute_daily_returns(nav: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute daily returns for each scheme and summarise the distribution."""
    returns = nav.sort_values(["amfi_code", "date"]).copy()
    returns["daily_return"] = returns.groupby("amfi_code")["nav"].pct_change()
    returns = returns.dropna(subset=["daily_return"]).reset_index(drop=True)
    distribution = (
        returns.groupby("amfi_code")["daily_return"]
        .agg(["count", "mean", "std", "min", "median", "max"])
        .reset_index()
    )
    distribution["reasonable_distribution"] = (
        distribution["std"].between(0, 0.20)
        & distribution["min"].between(-0.50, 0.50)
        & distribution["max"].between(-0.50, 0.50)
    )
    return returns, distribution


def nearest_nav(group: pd.DataFrame, target_date: pd.Timestamp) -> pd.Series:
    """Return the NAV row nearest to (but not after) *target_date*."""
    eligible = group[group["date"] <= target_date]
    if eligible.empty:
        return group.iloc[0]
    return eligible.iloc[-1]


def compute_cagr(nav: pd.DataFrame, fund: pd.DataFrame) -> pd.DataFrame:
    """Compute 1-, 3-, and 5-year NAV CAGR for every fund."""
    rows = []
    for amfi_code, group in nav.sort_values("date").groupby("amfi_code"):
        end = group.iloc[-1]
        row = {"amfi_code": amfi_code, "nav_end_date": end["date"], "nav_end": end["nav"]}
        first_date = group.iloc[0]["date"]
        for years in [1, 3, 5]:
            target = end["date"] - pd.DateOffset(years=years)
            if first_date > target:
                row[f"cagr_{years}yr_pct"] = np.nan
                row[f"cagr_{years}yr_available"] = False
                row[f"cagr_{years}yr_start_date"] = pd.NaT
                row[f"cagr_{years}yr_start_nav"] = np.nan
                continue
            start = nearest_nav(group, target)
            elapsed_years = (end["date"] - start["date"]).days / 365.25
            cagr = (end["nav"] / start["nav"]) ** (1 / elapsed_years) - 1
            row[f"cagr_{years}yr_pct"] = cagr * 100
            row[f"cagr_{years}yr_available"] = True
            row[f"cagr_{years}yr_start_date"] = start["date"]
            row[f"cagr_{years}yr_start_nav"] = start["nav"]
        rows.append(row)

    cagr = pd.DataFrame(rows)
    cagr = cagr.merge(fund[["amfi_code", "fund_house", "scheme_name", "category", "sub_category", "plan", "expense_ratio_pct"]], on="amfi_code")
    cols = [
        "amfi_code",
        "fund_house",
        "scheme_name",
        "category",
        "sub_category",
        "plan",
        "expense_ratio_pct",
        "nav_end_date",
        "nav_end",
        "cagr_1yr_pct",
        "cagr_1yr_available",
        "cagr_3yr_pct",
        "cagr_3yr_available",
        "cagr_5yr_pct",
        "cagr_5yr_available",
        "cagr_1yr_start_date",
        "cagr_3yr_start_date",
        "cagr_5yr_start_date",
    ]
    return cagr[cols].sort_values("cagr_3yr_pct", ascending=False).reset_index(drop=True)


def compute_risk_metrics(returns: pd.DataFrame) -> pd.DataFrame:
    """Compute Sharpe and Sortino ratios from daily returns."""
    rf_daily = RISK_FREE_RATE / TRADING_DAYS
    rows = []
    for amfi_code, group in returns.groupby("amfi_code"):
        r = group["daily_return"].dropna()
        excess = r - rf_daily
        downside = r[r < 0]
        sharpe = np.nan if r.std(ddof=1) == 0 else (excess.mean() / r.std(ddof=1)) * np.sqrt(TRADING_DAYS)
        sortino = np.nan if downside.std(ddof=1) == 0 else (excess.mean() / downside.std(ddof=1)) * np.sqrt(TRADING_DAYS)
        rows.append(
            {
                "amfi_code": amfi_code,
                "annualized_return_pct": r.mean() * TRADING_DAYS * 100,
                "annualized_volatility_pct": r.std(ddof=1) * np.sqrt(TRADING_DAYS) * 100,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "positive_return_days": int((r > 0).sum()),
                "negative_return_days": int((r < 0).sum()),
            }
        )
    return pd.DataFrame(rows)


def compute_alpha_beta(returns: pd.DataFrame, benchmark: pd.DataFrame, fund: pd.DataFrame) -> pd.DataFrame:
    """OLS regression of fund returns vs NIFTY100 to estimate alpha and beta."""
    nifty100 = benchmark[benchmark["index_name"] == "NIFTY100"].sort_values("date").copy()
    nifty100["benchmark_return"] = nifty100["close_value"].pct_change()
    nifty100 = nifty100.dropna(subset=["benchmark_return"])[["date", "benchmark_return"]]

    rows = []
    for amfi_code, group in returns.groupby("amfi_code"):
        merged = group[["date", "daily_return"]].merge(nifty100, on="date", how="inner").dropna()
        if len(merged) < 30:
            rows.append({"amfi_code": amfi_code, "beta": np.nan, "alpha_pct": np.nan, "r_squared": np.nan, "regression_days": len(merged)})
            continue
        result = linregress(merged["benchmark_return"], merged["daily_return"])
        rows.append(
            {
                "amfi_code": amfi_code,
                "beta": result.slope,
                "alpha_pct": result.intercept * TRADING_DAYS * 100,
                "r_squared": result.rvalue**2,
                "p_value": result.pvalue,
                "regression_days": len(merged),
            }
        )
    out = pd.DataFrame(rows).merge(fund[["amfi_code", "fund_house", "scheme_name", "category", "plan"]], on="amfi_code")
    return out[["amfi_code", "fund_house", "scheme_name", "category", "plan", "alpha_pct", "beta", "r_squared", "p_value", "regression_days"]].sort_values("alpha_pct", ascending=False)


def compute_drawdowns(nav: pd.DataFrame) -> pd.DataFrame:
    """Compute maximum drawdown, peak, trough, and recovery dates per fund."""
    rows = []
    for amfi_code, group in nav.sort_values("date").groupby("amfi_code"):
        group = group.copy()
        group["running_max"] = group["nav"].cummax()
        group["drawdown"] = group["nav"] / group["running_max"] - 1
        trough_idx = group["drawdown"].idxmin()
        trough = group.loc[trough_idx]
        peak_candidates = group.loc[:trough_idx]
        peak_idx = peak_candidates["nav"].idxmax()
        peak = group.loc[peak_idx]
        recovery_candidates = group[(group["date"] > trough["date"]) & (group["nav"] >= peak["nav"])]
        recovery_date = recovery_candidates.iloc[0]["date"] if not recovery_candidates.empty else pd.NaT
        rows.append(
            {
                "amfi_code": amfi_code,
                "max_drawdown_pct": trough["drawdown"] * 100,
                "drawdown_start_date": peak["date"],
                "drawdown_trough_date": trough["date"],
                "drawdown_recovery_date": recovery_date,
                "drawdown_days_to_trough": (trough["date"] - peak["date"]).days,
            }
        )
    return pd.DataFrame(rows)


def compute_tracking_error(
    returns: pd.DataFrame,
    benchmark: pd.DataFrame,
    scorecard_seed: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    latest_date = returns["date"].max()
    start_date = latest_date - pd.DateOffset(years=3)
    selected_codes = scorecard_seed.sort_values("score_0_100", ascending=False).head(5)["amfi_code"].tolist()

    bench = benchmark[benchmark["index_name"].isin(["NIFTY50", "NIFTY100"])].sort_values(["index_name", "date"]).copy()
    bench["benchmark_return"] = bench.groupby("index_name")["close_value"].pct_change()
    bench = bench[bench["date"] >= start_date]

    rows = []
    for amfi_code in selected_codes:
        fund_returns = returns[(returns["amfi_code"] == amfi_code) & (returns["date"] >= start_date)][["date", "daily_return"]]
        for index_name, group in bench.groupby("index_name"):
            merged = fund_returns.merge(group[["date", "benchmark_return"]], on="date", how="inner").dropna()
            tracking_error = (merged["daily_return"] - merged["benchmark_return"]).std(ddof=1) * np.sqrt(TRADING_DAYS)
            rows.append(
                {
                    "amfi_code": amfi_code,
                    "benchmark": index_name,
                    "tracking_error_pct": tracking_error * 100,
                    "comparison_days": len(merged),
                }
            )
    te = pd.DataFrame(rows)
    te_wide = te.pivot(index="amfi_code", columns="benchmark", values="tracking_error_pct").reset_index()
    te_wide = te_wide.rename(columns={"NIFTY50": "tracking_error_nifty50_pct", "NIFTY100": "tracking_error_nifty100_pct"})
    return te, te_wide


def percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """Rank values as 0–100 percentile scores."""
    ranked = series.rank(pct=True, ascending=not higher_is_better)
    return ranked.fillna(0) * 100


def compute_scorecard(
    fund: pd.DataFrame,
    cagr: pd.DataFrame,
    risk: pd.DataFrame,
    alpha_beta: pd.DataFrame,
    drawdown: pd.DataFrame,
) -> pd.DataFrame:
    """Build a 0–100 composite fund scorecard from returns, risk, and alpha."""
    score = (
        fund[["amfi_code", "fund_house", "scheme_name", "category", "sub_category", "plan", "expense_ratio_pct"]]
        .merge(cagr[["amfi_code", "cagr_1yr_pct", "cagr_3yr_pct", "cagr_5yr_pct", "cagr_5yr_available"]], on="amfi_code")
        .merge(risk[["amfi_code", "annualized_return_pct", "annualized_volatility_pct", "sharpe_ratio", "sortino_ratio"]], on="amfi_code")
        .merge(alpha_beta[["amfi_code", "alpha_pct", "beta", "r_squared"]], on="amfi_code")
        .merge(drawdown[["amfi_code", "max_drawdown_pct", "drawdown_start_date", "drawdown_trough_date", "drawdown_recovery_date"]], on="amfi_code")
    )
    score["return_3yr_rank_score"] = percentile_score(score["cagr_3yr_pct"], higher_is_better=True)
    score["sharpe_rank_score"] = percentile_score(score["sharpe_ratio"], higher_is_better=True)
    score["alpha_rank_score"] = percentile_score(score["alpha_pct"], higher_is_better=True)
    score["expense_rank_score"] = percentile_score(score["expense_ratio_pct"], higher_is_better=False)
    score["max_drawdown_rank_score"] = percentile_score(score["max_drawdown_pct"], higher_is_better=True)
    score["score_0_100"] = (
        0.30 * score["return_3yr_rank_score"]
        + 0.25 * score["sharpe_rank_score"]
        + 0.20 * score["alpha_rank_score"]
        + 0.15 * score["expense_rank_score"]
        + 0.10 * score["max_drawdown_rank_score"]
    ).round(2)
    return score.sort_values("score_0_100", ascending=False).reset_index(drop=True)


def make_benchmark_chart(nav: pd.DataFrame, benchmark: pd.DataFrame, scorecard: pd.DataFrame) -> Path:
    """Plot 3-year indexed performance for top-5 scorecard funds vs NIFTY indices."""
    latest_date = nav["date"].max()
    start_date = latest_date - pd.DateOffset(years=3)
    top5 = scorecard.head(5)[["amfi_code", "scheme_name"]]

    nav_top = nav[nav["amfi_code"].isin(top5["amfi_code"]) & (nav["date"] >= start_date)].merge(top5, on="amfi_code")
    nav_top["indexed_value"] = nav_top.groupby("amfi_code")["nav"].transform(lambda s: s / s.iloc[0] * 100)

    bench = benchmark[benchmark["index_name"].isin(["NIFTY50", "NIFTY100"]) & (benchmark["date"] >= start_date)].copy()
    bench["indexed_value"] = bench.groupby("index_name")["close_value"].transform(lambda s: s / s.iloc[0] * 100)

    fig, ax = plt.subplots(figsize=(14, 7))
    for scheme, group in nav_top.groupby("scheme_name"):
        ax.plot(group["date"], group["indexed_value"], linewidth=1.8, alpha=0.9, label=scheme)
    for index_name, group in bench.groupby("index_name"):
        ax.plot(group["date"], group["indexed_value"], linewidth=2.6, linestyle="--", label=index_name)
    ax.set_title("Top 5 Fund Scorecard Schemes vs NIFTY50 and NIFTY100, 3-Year Indexed Performance")
    ax.set_xlabel("Date")
    ax.set_ylabel("Indexed value, start = 100")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.legend(loc="upper left", fontsize=8)
    path = CHART_DIR / "benchmark_comparison_top5_vs_indices.png"
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    return path


def save_outputs(
    returns: pd.DataFrame,
    return_distribution: pd.DataFrame,
    cagr: pd.DataFrame,
    risk: pd.DataFrame,
    alpha_beta: pd.DataFrame,
    drawdown: pd.DataFrame,
    scorecard: pd.DataFrame,
    tracking_error: pd.DataFrame,
) -> None:
    returns.to_csv(REPORTS_DIR / "daily_returns.csv", index=False)
    return_distribution.to_csv(REPORTS_DIR / "daily_return_distribution.csv", index=False)
    cagr.to_csv(REPORTS_DIR / "cagr_comparison.csv", index=False)
    risk.to_csv(REPORTS_DIR / "risk_ratios.csv", index=False)
    alpha_beta.to_csv(REPORTS_DIR / "alpha_beta.csv", index=False)
    drawdown.to_csv(REPORTS_DIR / "max_drawdown.csv", index=False)
    scorecard.to_csv(REPORTS_DIR / "fund_scorecard.csv", index=False)
    tracking_error.to_csv(REPORTS_DIR / "benchmark_tracking_error.csv", index=False)


def make_markdown_cell(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(textwrap.dedent(source).strip())


def make_code_cell(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(textwrap.dedent(source).strip())


def build_notebook() -> None:
    """Create the Performance_Analytics.ipynb Jupyter notebook."""
    nb = nbf.v4.new_notebook()
    cells = [
        make_markdown_cell(
            """
            # Day 4 Performance Analytics

            This notebook computes daily returns, CAGR, Sharpe, Sortino, alpha, beta, max drawdown, composite fund scores, and benchmark tracking error from the cleaned Day 2 datasets.
            """
        ),
        make_code_cell(
            """
            from pathlib import Path
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import seaborn as sns
            from scipy.stats import linregress

            BASE_DIR = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
            REPORTS_DIR = BASE_DIR / "reports"
            CHART_DIR = REPORTS_DIR / "charts" / "day4"
            sns.set_theme(style="whitegrid")
            """
        ),
        make_code_cell(
            """
            scorecard = pd.read_csv(REPORTS_DIR / "fund_scorecard.csv", parse_dates=["drawdown_start_date", "drawdown_trough_date", "drawdown_recovery_date"])
            alpha_beta = pd.read_csv(REPORTS_DIR / "alpha_beta.csv")
            returns = pd.read_csv(REPORTS_DIR / "daily_returns.csv", parse_dates=["date"])
            cagr = pd.read_csv(REPORTS_DIR / "cagr_comparison.csv")
            tracking_error = pd.read_csv(REPORTS_DIR / "benchmark_tracking_error.csv")
            drawdown = pd.read_csv(REPORTS_DIR / "max_drawdown.csv", parse_dates=["drawdown_start_date", "drawdown_trough_date", "drawdown_recovery_date"])
            scorecard.head(10)
            """
        ),
        make_markdown_cell("## Daily Return Distribution"),
        make_code_cell(
            """
            plt.figure(figsize=(10, 5))
            sns.histplot(returns["daily_return"], bins=100, kde=True)
            plt.title("Distribution of Daily Fund Returns")
            plt.xlabel("Daily return")
            plt.show()
            """
        ),
        make_markdown_cell("Daily return distribution is centered near zero with moderate tails, which is reasonable for NAV return data after calendar forward-fill."),
        make_markdown_cell("## CAGR Comparison"),
        make_code_cell(
            """
            cagr[["scheme_name", "cagr_1yr_pct", "cagr_3yr_pct", "cagr_5yr_pct", "cagr_5yr_available"]].head(10)
            """
        ),
        make_markdown_cell("The available NAV window supports full 1-year and 3-year CAGR calculations; true 5-year CAGR is marked unavailable because the cleaned NAV data starts in January 2022."),
        make_markdown_cell("## Sharpe and Sortino Ranking"),
        make_code_cell(
            """
            scorecard[["scheme_name", "sharpe_ratio", "sortino_ratio", "score_0_100"]].head(10)
            """
        ),
        make_markdown_cell("## Alpha and Beta"),
        make_code_cell(
            """
            alpha_beta.sort_values("alpha_pct", ascending=False).head(10)
            """
        ),
        make_markdown_cell("Alpha and beta are estimated using OLS regression of fund daily returns against NIFTY100 daily returns."),
        make_markdown_cell("## Maximum Drawdown"),
        make_code_cell(
            """
            scorecard[["scheme_name", "max_drawdown_pct", "drawdown_start_date", "drawdown_trough_date", "drawdown_recovery_date"]].sort_values("max_drawdown_pct").head(10)
            """
        ),
        make_markdown_cell("## Fund Scorecard"),
        make_code_cell(
            """
            scorecard[[
                "scheme_name", "category", "cagr_3yr_pct", "sharpe_ratio", "alpha_pct",
                "expense_ratio_pct", "max_drawdown_pct", "score_0_100"
            ]].head(15)
            """
        ),
        make_markdown_cell(
            """
            The composite score uses:

            - 30% 3-year CAGR rank
            - 25% Sharpe rank
            - 20% Alpha rank
            - 15% inverse expense ratio rank
            - 10% inverse max drawdown rank
            """
        ),
        make_markdown_cell("## Benchmark Comparison"),
        make_markdown_cell("![Benchmark comparison](../reports/charts/day4/benchmark_comparison_top5_vs_indices.png)"),
        make_code_cell(
            """
            tracking_error.sort_values(["amfi_code", "benchmark"])
            """
        ),
    ]
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    nbf.write(nb, NOTEBOOK_PATH)


def main() -> None:
    """Run the full Day 4 performance analytics pipeline."""
    data = load_data()
    returns, return_distribution = compute_daily_returns(data["nav"])
    cagr = compute_cagr(data["nav"], data["fund"])
    risk = compute_risk_metrics(returns)
    alpha_beta = compute_alpha_beta(returns, data["benchmark"], data["fund"])
    drawdown = compute_drawdowns(data["nav"])
    scorecard = compute_scorecard(data["fund"], cagr, risk, alpha_beta, drawdown)
    tracking_error, tracking_error_wide = compute_tracking_error(returns, data["benchmark"], scorecard)
    scorecard = scorecard.merge(tracking_error_wide, on="amfi_code", how="left")
    chart_path = make_benchmark_chart(data["nav"], data["benchmark"], scorecard)
    save_outputs(returns, return_distribution, cagr, risk, alpha_beta, drawdown, scorecard, tracking_error)
    build_notebook()

    log.info("Day 4 performance analytics complete.")
    log.info("Notebook: %s", NOTEBOOK_PATH)
    log.info("Fund scorecard: %s", REPORTS_DIR / "fund_scorecard.csv")
    log.info("Alpha beta: %s", REPORTS_DIR / "alpha_beta.csv")
    log.info("Benchmark chart: %s", chart_path)
    log.info("Top 5 funds by score:\n%s",
             scorecard[["scheme_name", "score_0_100", "cagr_3yr_pct", "sharpe_ratio", "alpha_pct"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
