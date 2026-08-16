DROP VIEW IF EXISTS v_account_summary;
CREATE VIEW v_account_summary AS
SELECT customer_id, COUNT(*) AS product_count,
SUM(CASE WHEN product_type = 'Savings' THEN 1 ELSE 0 END) AS savings_accounts,
SUM(CASE WHEN product_type = 'Current Account' THEN 1 ELSE 0 END) AS current_accounts,
SUM(CASE WHEN product_type = 'Credit Card' THEN 1 ELSE 0 END) AS credit_cards,
SUM(CASE WHEN product_type = 'Personal Loan' THEN 1 ELSE 0 END) AS personal_loans,
SUM(CASE WHEN product_type = 'Investment' THEN 1 ELSE 0 END) AS investment_accounts,
SUM(current_balance_idr) AS total_current_balance_idr,
SUM(monthly_fee_idr) AS contracted_monthly_fees_idr
FROM accounts GROUP BY customer_id;

DROP VIEW IF EXISTS v_snapshot_features;
CREATE VIEW v_snapshot_features AS
WITH behavior AS (
SELECT customer_id, AVG(transaction_count) AS avg_transaction_count_3m, AVG(transaction_value_idr) AS avg_transaction_value_3m,
AVG(avg_balance_idr) AS avg_balance_3m, AVG(digital_logins) AS avg_digital_logins_3m, SUM(complaints) AS complaints_3m,
AVG(credit_utilization) AS avg_credit_utilization_3m, AVG(fee_revenue_idr) AS avg_fee_revenue_3m
FROM monthly_activity WHERE activity_month BETWEEN '2025-04-01' AND '2025-06-01' GROUP BY customer_id)
SELECT c.customer_id, c.join_date, CAST((julianday('2025-06-30') - julianday(c.join_date)) / 30.44 AS INTEGER) AS months_on_book,
(2025 - c.birth_year) AS age, c.gender, c.city, c.segment, c.preferred_channel, c.monthly_income_idr, c.credit_score, c.risk_tier,
c.digital_adoption_score, a.*, b.avg_transaction_count_3m, b.avg_transaction_value_3m, b.avg_balance_3m, b.avg_digital_logins_3m,
b.complaints_3m, b.avg_credit_utilization_3m, b.avg_fee_revenue_3m,
CASE WHEN c.churn_date > '2025-06-30' AND c.churn_date <= '2025-12-31' THEN 1 ELSE 0 END AS churned_next_6m, c.churn_date
FROM customers c JOIN v_account_summary a ON c.customer_id = a.customer_id JOIN behavior b ON c.customer_id = b.customer_id
WHERE c.join_date <= '2025-04-01' AND (c.churn_date IS NULL OR c.churn_date > '2025-06-30');
