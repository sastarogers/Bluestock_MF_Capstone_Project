#!/usr/bin/env python3
"""
Simple Mutual Fund Recommender
===============================
Input : Risk appetite — Low / Moderate / High
Output: Top 3 funds by Sharpe Ratio within the matching risk grade.

Usage:
    python recommender.py              # interactive prompt
    python recommender.py --risk High  # command-line
"""

import argparse
import os
import sqlite3
import pandas as pd
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

# ── Risk mapping ──────────────────────────────────────────────
# dim_fund.risk_category has: Low, Moderate, Moderately High, High, Very High
# We map user input to matching DB risk categories.
RISK_MAP = {
    "Low":      ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High"],
}

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "bluestock_mf.db")
SCORECARD_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "fund_scorecard.csv")


def load_data():
    """Load fund metadata and performance scorecard."""
    conn = sqlite3.connect(DB_PATH)
    funds = pd.read_sql_query(
        "SELECT amfi_code, scheme_name, fund_house, category, sub_category, "
        "plan, risk_category FROM dim_fund",
        conn,
    )
    conn.close()

    if os.path.exists(SCORECARD_PATH):
        scorecard = pd.read_csv(SCORECARD_PATH)
    else:
        conn = sqlite3.connect(DB_PATH)
        scorecard = pd.read_sql_query("SELECT * FROM fact_performance", conn)
        conn.close()

    # Merge to get risk_category alongside performance metrics
    merged = scorecard.merge(
        funds[["amfi_code", "risk_category"]],
        on="amfi_code",
        how="left",
    )
    return merged


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    """
    Return top N funds by Sharpe Ratio for the given risk appetite.

    Parameters
    ----------
    risk_appetite : str
        One of 'Low', 'Moderate', 'High'.
    top_n : int
        Number of recommendations (default 3).

    Returns
    -------
    pd.DataFrame with recommendation details.
    """
    risk_appetite = risk_appetite.strip().title()
    if risk_appetite not in RISK_MAP:
        raise ValueError(
            f"Invalid risk appetite '{risk_appetite}'. "
            f"Choose from: {', '.join(RISK_MAP.keys())}"
        )

    data = load_data()
    matching_risks = RISK_MAP[risk_appetite]
    filtered = data[data["risk_category"].isin(matching_risks)].copy()

    if filtered.empty:
        print(f"No funds found for risk appetite: {risk_appetite}")
        return pd.DataFrame()

    # Sort by Sharpe Ratio (descending) and pick top N
    filtered = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)

    result = filtered[
        [
            "scheme_name",
            "fund_house",
            "category",
            "risk_category",
            "sharpe_ratio",
            "cagr_3yr_pct",
            "annualized_volatility_pct",
            "score_0_100",
        ]
    ].copy()

    result.columns = [
        "Scheme Name",
        "Fund House",
        "Category",
        "Risk Grade",
        "Sharpe Ratio",
        "CAGR 3Y (%)",
        "Volatility (%)",
        "Score (0-100)",
    ]
    result = result.reset_index(drop=True)
    result.index = result.index + 1  # 1-indexed ranking
    result.index.name = "Rank"
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Simple Mutual Fund Recommender based on risk appetite."
    )
    parser.add_argument(
        "--risk",
        type=str,
        choices=["Low", "Moderate", "High"],
        help="Risk appetite level",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  BLUESTOCK — Simple Mutual Fund Recommender")
    print("=" * 70)

    if args.risk:
        risk = args.risk
    else:
        print("\nRisk Appetite Options:")
        print("  1. Low       — Debt / liquid funds, capital preservation")
        print("  2. Moderate  — Balanced / hybrid, moderate growth")
        print("  3. High      — Equity / sectoral, aggressive growth")
        risk = input("\nEnter your risk appetite (Low / Moderate / High): ").strip()

    print(f"\n🔍 Searching for top funds matching risk appetite: {risk}\n")

    try:
        recs = recommend(risk)
    except ValueError as e:
        print(f"Error: {e}")
        return

    if recs.empty:
        return

    if HAS_TABULATE:
        print(tabulate(recs, headers="keys", tablefmt="fancy_grid", floatfmt=".2f"))
    else:
        print(recs.to_string(float_format="{:.2f}".format))
    print(f"\n✅ Top {len(recs)} recommendations for '{risk}' risk appetite shown above.")
    print("   (Ranked by Sharpe Ratio — higher is better risk-adjusted return)\n")


if __name__ == "__main__":
    main()
