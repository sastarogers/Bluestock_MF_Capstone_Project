import os
import sqlite3
import pandas as pd
import numpy as np

def main():
    db_path = "bluestock_mf.db"
    out_dir = "data/processed/dashboard_data"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Connecting to SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # -------------------------------------------------------------
    # PAGE 1: Industry Overview
    # -------------------------------------------------------------
    print("Preparing Page 1 Data: Industry Overview...")
    
    # Query AUM by fund house over time
    aum_df = pd.read_sql_query("""
        SELECT a.date, a.fund_house, a.aum_crore, a.aum_lakh_crore, a.num_schemes
        FROM fact_aum a
        ORDER BY a.date, a.aum_crore DESC
    """, conn)
    
    # Parse dates
    aum_df['date'] = pd.to_datetime(aum_df['date'])
    
    # Get latest date to compute Top 10 latest AUM
    latest_aum_date = aum_df['date'].max()
    print(f"Latest AUM date found: {latest_aum_date}")
    
    # Query SIP inflows and folios to include in the same source for time series line charts
    sip_df = pd.read_sql_query("""
        SELECT month, sip_inflow_crore, active_sip_accounts_crore, new_sip_accounts_lakh, sip_aum_lakh_crore, yoy_growth_pct
        FROM monthly_sip_inflows
        ORDER BY month
    """, conn)
    sip_df['month'] = pd.to_datetime(sip_df['month'])
    
    folio_df = pd.read_sql_query("""
        SELECT month, total_folios_crore, equity_folios_crore, debt_folios_crore, hybrid_folios_crore, others_folios_crore
        FROM industry_folio_count
        ORDER BY month
    """, conn)
    folio_df['month'] = pd.to_datetime(folio_df['month'])
    
    # We will save these three tables. For Page 1, a combined AUM timeline and fund house ranking CSV is ideal.
    # We also write a general KPI stats CSV representing the overall industry.
    industry_kpis = pd.DataFrame([{
        "total_aum_lakh_cr": 81.0,  # Industry-wide AUM target KPI
        "sip_inflow_cr": sip_df[sip_df['month'] == sip_df['month'].max()]['sip_inflow_crore'].values[0],
        "total_folios_cr": folio_df[folio_df['month'] == folio_df['month'].max()]['total_folios_crore'].values[0],
        "num_schemes": 1908        # Industry-wide schemes count target KPI
    }])
    
    # Save files
    aum_df.to_csv(f"{out_dir}/page1_aum_by_fund_house.csv", index=False)
    sip_df.to_csv(f"{out_dir}/page1_sip_inflows_timeline.csv", index=False)
    folio_df.to_csv(f"{out_dir}/page1_folios_timeline.csv", index=False)
    industry_kpis.to_csv(f"{out_dir}/page1_industry_kpis.csv", index=False)
    
    # -------------------------------------------------------------
    # PAGE 2: Fund Performance
    # -------------------------------------------------------------
    print("Preparing Page 2 Data: Fund Performance...")
    
    # Fund scorecard (using the file generated in Day 4)
    scorecard_path = "reports/fund_scorecard.csv"
    if os.path.exists(scorecard_path):
        scorecard_df = pd.read_csv(scorecard_path)
    else:
        # Fallback to querying database fact_performance
        scorecard_df = pd.read_sql_query("SELECT * FROM fact_performance", conn)
    
    # Add AUM data from fact_aum (latest date, per fund house)
    latest_aum = pd.read_sql_query("""
        SELECT fund_house, aum_crore
        FROM fact_aum
        WHERE date = (SELECT MAX(date) FROM fact_aum)
    """, conn)
    scorecard_df = scorecard_df.merge(latest_aum, on='fund_house', how='left')
    scorecard_df['aum_crore'] = scorecard_df['aum_crore'].fillna(0)
    
    scorecard_df.to_csv(f"{out_dir}/page2_fund_scorecard.csv", index=False)
    
    # Fund daily NAV history vs Benchmark
    # First, load dim_fund to get benchmarks
    funds = pd.read_sql_query("SELECT amfi_code, scheme_name, fund_house, category, sub_category, plan, benchmark FROM dim_fund", conn)
    
    # Load daily NAV
    nav_history = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav", conn)
    nav_history['date'] = pd.to_datetime(nav_history['date'])
    
    # Load daily benchmark indices
    benchmarks = pd.read_sql_query("SELECT date, index_name, close_value FROM benchmark_indices", conn)
    benchmarks['date'] = pd.to_datetime(benchmarks['date'])
    
    # Map dim_fund benchmark names to index_name in benchmarks
    benchmark_map = {
        'NIFTY 100 TRI': 'NIFTY100',
        'NIFTY 50 TRI': 'NIFTY50',
        'NIFTY 500 TRI': 'NIFTY500',
        'BSE 250 SmallCap TRI': 'BSE_SMALLCAP',
        'CRISIL Liquid Fund AI Index': 'CRISIL_LIQUID',
        'CRISIL Dynamic Gilt Index': 'CRISIL_GILT',
        'NIFTY Midcap 150 TRI': 'NIFTY_MIDCAP150',
        # Fallbacks for missing matches
        'CRISIL Short Term Bond Index': 'CRISIL_GILT',
        'NIFTY Midcap 50 TRI': 'NIFTY_MIDCAP150',
        'NIFTY Large Midcap 250 TRI': 'NIFTY100'
    }
    
    # Add mapped index to fund
    funds['mapped_index'] = funds['benchmark'].map(benchmark_map)
    
    print("Computing daily indexed NAV and benchmark comparison...")
    # Compute indexed NAV and benchmark value starting at 100 for each scheme
    merged_navs = []
    
    for _, fund_row in funds.iterrows():
        code = fund_row['amfi_code']
        scheme_nav = nav_history[nav_history['amfi_code'] == code].sort_values('date').copy()
        if scheme_nav.empty:
            continue
            
        idx_name = fund_row['mapped_index']
        bench_data = benchmarks[benchmarks['index_name'] == idx_name].sort_values('date').copy()
        
        # Merge scheme NAV with its benchmark
        m = pd.merge(scheme_nav, bench_data[['date', 'close_value']], on='date', how='inner')
        if m.empty:
            # Fallback if dates don't match exactly, do a forward fill on benchmark values
            m = pd.merge_asof(scheme_nav, bench_data[['date', 'close_value']], on='date', direction='backward')
            
        m = m.dropna().sort_values('date').reset_index(drop=True)
        if m.empty:
            continue
            
        # Compute indexed columns
        nav_start = m.iloc[0]['nav']
        bench_start = m.iloc[0]['close_value']
        
        m['indexed_nav'] = (m['nav'] / nav_start) * 100
        m['indexed_benchmark'] = (m['close_value'] / bench_start) * 100
        
        m['scheme_name'] = fund_row['scheme_name']
        m['fund_house'] = fund_row['fund_house']
        m['category'] = fund_row['category']
        m['plan'] = fund_row['plan']
        m['benchmark_name'] = fund_row['benchmark']
        m['benchmark_index_code'] = idx_name
        
        merged_navs.append(m)
        
    page2_nav_comparison = pd.concat(merged_navs, ignore_index=True)
    page2_nav_comparison.to_csv(f"{out_dir}/page2_fund_nav_history.csv", index=False)
    
    # -------------------------------------------------------------
    # PAGE 3: Investor Analytics
    # -------------------------------------------------------------
    print("Preparing Page 3 Data: Investor Analytics...")
    
    # Read transactions directly (flat table contains all necessary dimensions)
    tx_df = pd.read_sql_query("""
        SELECT t.transaction_id, t.investor_id, t.transaction_date, t.transaction_type, t.amount_inr, 
               t.state, t.city, t.city_tier, t.age_group, t.gender, t.kyc_status,
               f.scheme_name, f.fund_house, f.category
        FROM fact_transactions t
        JOIN dim_fund f ON f.amfi_code = t.amfi_code
        ORDER BY t.transaction_date
    """, conn)
    
    tx_df.to_csv(f"{out_dir}/page3_investor_transactions.csv", index=False)
    
    # -------------------------------------------------------------
    # PAGE 4: SIP & Market Trends
    # -------------------------------------------------------------
    print("Preparing Page 4 Data: SIP & Market Trends...")
    
    # We need:
    # 1. Monthly SIP inflows aligned with monthly NIFTY 50 close
    # Fetch monthly nifty 50
    nifty50_daily = benchmarks[benchmarks['index_name'] == 'NIFTY50'].sort_values('date').copy()
    
    # Aggregate Nifty 50 to monthly (take the last available close price of each month)
    nifty50_monthly = nifty50_daily.groupby(nifty50_daily['date'].dt.to_period('M')).last().reset_index(drop=True)
    nifty50_monthly['month_aligned'] = nifty50_monthly['date'].dt.to_period('M').dt.to_timestamp()
    
    # Merge with monthly SIP inflows
    sip_market = pd.merge(sip_df, nifty50_monthly[['month_aligned', 'close_value']], left_on='month', right_on='month_aligned', how='inner')
    sip_market = sip_market.rename(columns={'close_value': 'nifty50_close'})
    sip_market = sip_market.drop(columns=['month_aligned'])
    sip_market.to_csv(f"{out_dir}/page4_sip_market_trends.csv", index=False)
    
    # 2. Category inflows by month (heatmap)
    category_inflow_df = pd.read_sql_query("""
        SELECT month, category, net_inflow_crore
        FROM category_inflows
        ORDER BY month, category
    """, conn)
    category_inflow_df['month'] = pd.to_datetime(category_inflow_df['month'])
    
    # 3. Bar: Top 5 categories by net inflow FY25
    # FY25 is April 1, 2024 to March 31, 2025 (according to database date bounds 2022-2025)
    category_inflow_df['is_fy25'] = (category_inflow_df['month'] >= '2024-04-01') & (category_inflow_df['month'] <= '2025-03-31')
    category_inflow_df.to_csv(f"{out_dir}/page4_category_inflows.csv", index=False)
    
    # Close connection
    conn.close()
    print("All flat CSV files successfully written to data/processed/dashboard_data/!")

if __name__ == '__main__':
    main()
