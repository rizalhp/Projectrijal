# Banking Customer Analytics & Churn Intelligence

End-to-end retail banking analytics case study combining **SQL, Python, machine learning, business analysis, automated testing, and Streamlit** to identify churn risk and prioritize retention actions.

> **Data note:** all data is synthetic and privacy-safe. The generator uses a fixed random seed so the analysis is reproducible without representing any real bank or customer.

## Executive Summary

The project uses a fixed **30 June 2025** customer snapshot. Only information available up to that date is used for modeling, while the target is churn during **July–December 2025**.

Key reproducible findings:

- **8,000** synthetic customers generated across 4 customer segments.
- **7,266** customers remain active and eligible at the snapshot.
- Observed six-month churn is **6.22%**.
- **Branch-first** customers churn at **10.28%**, versus **4.90%** for Mobile-first customers.
- **SME** has the highest segment churn rate at **7.04%**.
- **Mass** has the largest observed annualized fee revenue at risk at approximately **Rp176.3 million**.
- Logistic regression reaches **0.7238 ROC-AUC** on a stratified holdout set.
- The highest-risk **10%** of customers capture **34.29%** of observed churners, a **3.43× lift** over random targeting.

## Business Problem

A bank cannot contact every customer with the same retention strategy. This case study answers four practical questions:

1. Which customer groups have the highest churn risk?
2. Where is the largest revenue exposure?
3. Which recent behavior is most useful for ranking churn risk?
4. How can a retention team focus limited capacity on the customers most likely to leave?

## Leakage-safe Analytical Design

| Period | Purpose |
|---|---|
| Before Apr 2025 | Customer and account history |
| Apr–Jun 2025 | Three-month behavior feature window |
| 30 Jun 2025 | Scoring snapshot |
| Jul–Dec 2025 | Six-month churn target |

Customers who already churned before the snapshot are excluded from training. This prevents the model from using information from the future.

## Architecture

```text
Synthetic data generator
        |
        v
Customers + Accounts + Monthly Activity
        |
        v
SQLite / SQL analytics layer
        |
        +--> Customer 360 snapshot
        +--> KPI & segment views
        +--> Retention cohorts
        +--> Revenue-at-risk views
        |
        v
Logistic Regression
        |
        +--> Churn probabilities
        +--> Risk bands
        +--> Top-decile lift
        |
        v
Streamlit Executive Dashboard
```

## Model Performance

| Metric | Result |
|---|---:|
| ROC-AUC | **0.7238** |
| Recall @ 0.50 | **69.03%** |
| Top-decile churn capture | **34.29%** |
| Top-decile lift | **3.43×** |
| Holdout rows | **1,817** |

The model is treated primarily as a **ranking system**, not as a claim that 0.50 is the ideal operational cutoff. With churn prevalence of only 6.22%, retention capacity and intervention cost should determine the final targeting threshold.

## Strongest Predictive Signals

Holdout permutation importance ranks recent transaction activity as the strongest signal, followed by transaction value, complaints, digital engagement, credit score, and customer segment.

This interpretation uses permutation importance instead of relying only on one-hot logistic coefficients so the discussion stays at the original business-feature level.

## Business Recommendations

1. **Start with the top risk decile.** A team contacting only the highest-scored 10% can cover roughly one-third of future churners in this simulation.
2. **Create a Branch-first digital activation journey.** Branch-first churn is roughly 2.1× Mobile-first churn; combine service recovery with assisted digital onboarding.
3. **Escalate recent complaints.** Complaints plus declining transaction activity should trigger proactive service recovery before generic promotions.
4. **Separate rate risk from value risk.** SME has the highest churn percentage, while Mass has the highest total fee-revenue exposure.
5. **Validate interventions experimentally.** A real deployment should use controlled experiments before scaling retention offers.

## Project Structure

```text
banking-customer-analytics/
├── README.md
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/          # generated locally, ignored by git
│   └── processed/    # generated locally, ignored by git
├── docs/
│   ├── data_dictionary.md
│   └── methodology.md
├── reports/
│   ├── business_summary.json
│   ├── executive_summary.md
│   ├── model_metrics.json
│   └── permutation_importance.csv
├── sql/
│   ├── 01_customer_360.sql
│   ├── 02_kpi_analysis.sql
│   ├── 03_retention_cohorts.sql
│   └── 04_revenue_at_risk.sql
├── src/
│   ├── generate_data.py
│   ├── run_pipeline.py
│   ├── analyze_churn.py
│   └── run_all.py
├── tests/
├── requirements.txt
└── LICENSE
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/run_all.py
streamlit run dashboard/app.py
```

`python src/run_all.py` generates the raw data, builds the SQLite analytics layer, exports curated tables, trains the churn model, calculates risk scores, and refreshes the business outputs.

## SQL Skills Demonstrated

- multi-table joins;
- conditional aggregation;
- CTEs;
- reusable analytical views;
- customer-level feature engineering;
- date-window filtering;
- cohort analysis;
- segment KPI analysis;
- revenue-at-risk calculations.

## Testing

```bash
pytest -q
```

Local end-to-end validation completed successfully with **3 tests passed**.

## Why Logistic Regression?

The objective is a credible analytical baseline, not leaderboard performance. Logistic regression is fast, reproducible, interpretable, and appropriate for demonstrating how predicted risk connects to retention capacity and customer value. A production extension could compare gradient boosting, probability calibration, survival analysis, and cost-sensitive thresholds.

## Limitations

- Findings are based on synthetic data and are not claims about a real bank.
- Fee revenue is a simplified customer-value proxy rather than complete lifetime value.
- Churn is framed as a six-month binary target rather than time-to-event modeling.
- Real production use would require governance, fairness review, monitoring, privacy controls, calibration, retraining policy, and experimental validation.

## Tech Stack

**Python · Pandas · NumPy · scikit-learn · SQLite · SQL · Matplotlib · Plotly · Streamlit · Pytest · GitHub Actions**
