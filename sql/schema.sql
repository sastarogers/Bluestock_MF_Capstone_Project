PRAGMA foreign_keys = ON;

CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend INTEGER NOT NULL
);

CREATE TABLE fact_nav (
    amfi_code INTEGER NOT NULL,
    date DATE NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL CHECK (nav > 0),
    PRIMARY KEY (amfi_code, date_key),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY,
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr REAL NOT NULL CHECK (amount_inr > 0),
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT NOT NULL CHECK (kyc_status IN ('Verified', 'Pending', 'Rejected')),
    date_key INTEGER NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL CHECK (expense_ratio_pct BETWEEN 0.1 AND 2.5),
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    date DATE NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL NOT NULL CHECK (aum_crore > 0),
    num_schemes INTEGER,
    date_key INTEGER NOT NULL,
    PRIMARY KEY (date_key, fund_house),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE monthly_sip_inflows (
    month DATE PRIMARY KEY,
    sip_inflow_crore REAL NOT NULL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL,
    month_key INTEGER NOT NULL
);

CREATE TABLE category_inflows (
    month DATE NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL,
    month_key INTEGER NOT NULL,
    PRIMARY KEY (month, category)
);

CREATE TABLE industry_folio_count (
    month DATE PRIMARY KEY,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL,
    month_key INTEGER NOT NULL
);

CREATE TABLE portfolio_holdings (
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE NOT NULL,
    date_key INTEGER NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol, portfolio_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE benchmark_indices (
    date DATE NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL CHECK (close_value > 0),
    date_key INTEGER NOT NULL,
    PRIMARY KEY (date, index_name),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
