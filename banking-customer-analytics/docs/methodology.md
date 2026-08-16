# Methodology

## Objective
Build an end-to-end churn intelligence workflow that answers: **which active customers should a retention team prioritize today?**

## Synthetic Data Design
The generator creates customers, product relationships, and monthly behavior with a fixed seed. Latent engagement, service-risk, and fee-sensitivity variables are used only to create realistic relationships; they are removed from exported data and never supplied to the model.

## Leakage-safe window
- Snapshot: **30 June 2025**
- Features: April–June 2025
- Target: churn during July–December 2025
- Customers already churned by the snapshot are excluded.

## SQL Layer
SQLite creates account aggregation, a customer-360 modeling view, KPI views, segment/channel analysis, retention cohorts, portfolio trends, and revenue-at-risk analysis.

## Modeling
A stratified 75/25 train-test split uses numeric imputation/scaling, categorical imputation/one-hot encoding, and balanced logistic regression. ROC-AUC evaluates discrimination; top-decile capture and lift translate performance into retention-team capacity.

## Interpretation
Permutation importance is calculated on holdout data using ROC-AUC. This avoids over-interpreting one-hot coefficients and keeps the discussion at business-feature level.

## Validation
Pytest validates key uniqueness, range, referential, and snapshot rules. GitHub Actions runs the suite on changes.
