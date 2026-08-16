# Data Dictionary

## customers
`customer_id`, `join_date`, `birth_year`, `gender`, `city`, `segment`, `preferred_channel`, `monthly_income_idr`, `credit_score`, `risk_tier`, `digital_adoption_score`, `churn_date`.

## accounts
`account_id`, `customer_id`, `product_type`, `open_date`, `current_balance_idr`, `monthly_fee_idr`, `is_active`.

## monthly_activity
`customer_id`, `activity_month`, `transaction_count`, `transaction_value_idr`, `avg_balance_idr`, `digital_logins`, `complaints`, `credit_utilization`, `fee_revenue_idr`, `product_count`.

## v_snapshot_features
Leakage-safe customer-level modeling view restricted to customers active at 30 June 2025. Behavioral features aggregate April–June 2025; `churned_next_6m` uses July–December 2025 outcomes.
