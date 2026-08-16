DROP VIEW IF EXISTS v_retention_cohorts;
CREATE VIEW v_retention_cohorts AS
WITH joined AS (SELECT customer_id, join_date, printf('%04d-Q%d', CAST(strftime('%Y', join_date) AS INTEGER), ((CAST(strftime('%m', join_date) AS INTEGER) - 1) / 3) + 1) AS join_cohort FROM customers WHERE join_date >= '2023-01-01'),
months AS (SELECT a.customer_id, a.activity_month, j.join_date, j.join_cohort, CAST((julianday(a.activity_month) - julianday(j.join_date)) / 30.44 AS INTEGER) AS months_since_join FROM monthly_activity a JOIN joined j ON a.customer_id = j.customer_id)
SELECT join_cohort, months_since_join, COUNT(DISTINCT customer_id) AS retained_customers FROM months WHERE months_since_join BETWEEN 0 AND 23
GROUP BY join_cohort, months_since_join ORDER BY join_cohort, months_since_join;

DROP VIEW IF EXISTS v_monthly_portfolio_trend;
CREATE VIEW v_monthly_portfolio_trend AS SELECT activity_month, COUNT(DISTINCT customer_id) AS active_customers,
SUM(transaction_value_idr) AS transaction_value_idr, SUM(fee_revenue_idr) AS fee_revenue_idr, SUM(complaints) AS complaints,
ROUND(AVG(digital_logins), 2) AS avg_digital_logins FROM monthly_activity GROUP BY activity_month ORDER BY activity_month;
