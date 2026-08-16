DROP VIEW IF EXISTS v_revenue_at_risk_segments;
CREATE VIEW v_revenue_at_risk_segments AS SELECT segment, COUNT(*) AS customers, SUM(churned_next_6m) AS observed_churners,
ROUND(SUM(CASE WHEN churned_next_6m = 1 THEN avg_fee_revenue_3m * 12 ELSE 0 END), 0) AS annualized_observed_revenue_at_risk_idr,
ROUND(AVG(CASE WHEN churned_next_6m = 1 THEN avg_fee_revenue_3m END), 0) AS avg_monthly_revenue_per_churner_idr
FROM v_snapshot_features GROUP BY segment ORDER BY annualized_observed_revenue_at_risk_idr DESC;
