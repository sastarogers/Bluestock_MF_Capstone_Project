-- 1. Top 5 funds by AUM
SELECT
    f.scheme_name,
    f.fund_house,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT
    d.year,
    d.month,
    f.scheme_name,
    ROUND(AVG(n.nav), 4) AS avg_monthly_nav
FROM fact_nav n
JOIN dim_date d ON d.date_key = n.date_key
JOIN dim_fund f ON f.amfi_code = n.amfi_code
GROUP BY d.year, d.month, f.scheme_name
ORDER BY d.year, d.month, f.scheme_name;

-- 3. SIP YoY growth
SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct
FROM monthly_sip_inflows
ORDER BY month;

-- 4. Transactions by state
SELECT
    state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio below 1 percent
SELECT
    f.scheme_name,
    f.fund_house,
    f.plan,
    f.expense_ratio_pct
FROM dim_fund f
WHERE f.expense_ratio_pct < 1
ORDER BY f.expense_ratio_pct, f.scheme_name;

-- 6. Highest 3-year alpha funds
SELECT
    f.scheme_name,
    f.fund_house,
    p.alpha,
    p.return_3yr_pct,
    p.benchmark_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.alpha DESC
LIMIT 10;

-- 7. Redemption pressure by fund
SELECT
    f.scheme_name,
    COUNT(*) AS redemption_count,
    ROUND(SUM(t.amount_inr), 2) AS redemption_amount_inr
FROM fact_transactions t
JOIN dim_fund f ON f.amfi_code = t.amfi_code
WHERE t.transaction_type = 'Redemption'
GROUP BY f.scheme_name
ORDER BY redemption_amount_inr DESC
LIMIT 10;

-- 8. Category net inflows by month
SELECT
    month,
    category,
    ROUND(net_inflow_crore, 2) AS net_inflow_crore
FROM category_inflows
ORDER BY month, net_inflow_crore DESC;

-- 9. Latest NAV by fund
WITH latest_nav AS (
    SELECT
        amfi_code,
        MAX(date_key) AS latest_date_key
    FROM fact_nav
    GROUP BY amfi_code
)
SELECT
    f.scheme_name,
    d.date,
    n.nav
FROM latest_nav l
JOIN fact_nav n
    ON n.amfi_code = l.amfi_code
   AND n.date_key = l.latest_date_key
JOIN dim_fund f ON f.amfi_code = n.amfi_code
JOIN dim_date d ON d.date_key = n.date_key
ORDER BY f.scheme_name;

-- 10. Portfolio sector exposure
SELECT
    f.scheme_name,
    h.sector,
    ROUND(SUM(h.weight_pct), 2) AS total_weight_pct
FROM portfolio_holdings h
JOIN dim_fund f ON f.amfi_code = h.amfi_code
GROUP BY f.scheme_name, h.sector
ORDER BY f.scheme_name, total_weight_pct DESC;
