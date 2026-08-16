DROP VIEW IF EXISTS v_executive_kpis;
CREATE VIEW v_executive_kpis AS SELECT COUNT(*) AS active_customers_at_snapshot, SUM(churned_next_6m) AS churned_within_6m,
ROUND(100.0 * AVG(churned_next_6m), 2) AS churn_rate_6m_pct, ROUND(AVG(product_count), 2) AS avg_products_per_customer,
ROUND(AVG(avg_balance_3m), 0) AS avg_balance_3m_idr, ROUND(AVG(avg_fee_revenue_3m), 0) AS avg_monthly_fee_revenue_idr,
ROUND(SUM(avg_fee_revenue_3m) * 12, 0) AS annualized_portfolio_fee_revenue_idr,
ROUND(SUM(CASE WHEN churned_next_6m = 1 THEN avg_fee_revenue_3m * 12 ELSE 0 END), 0) AS observed_revenue_at_risk_idr FROM v_snapshot_features;

DROP VIEW IF EXISTS v_churn_by_segment;
CREATE VIEW v_churn_by_segment AS SELECT segment, COUNT(*) AS customers, SUM(churned_next_6m) AS churners,
ROUND(100.0 * AVG(churned_next_6m), 2) AS churn_rate_pct, ROUND(AVG(avg_fee_revenue_3m), 0) AS avg_monthly_fee_revenue_idr
FROM v_snapshot_features GROUP BY segment ORDER BY churn_rate_pct DESC;

DROP VIEW IF EXISTS v_churn_by_channel;
CREATE VIEW v_churn_by_channel AS SELECT preferred_channel, COUNT(*) AS customers, ROUND(100.0 * AVG(churned_next_6m), 2) AS churn_rate_pct,
ROUND(AVG(avg_digital_logins_3m), 2) AS avg_digital_logins_3m, ROUND(AVG(complaints_3m), 2) AS avg_complaints_3m
FROM v_snapshot_features GROUP BY preferred_channel ORDER BY churn_rate_pct DESC;
