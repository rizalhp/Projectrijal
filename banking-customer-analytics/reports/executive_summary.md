# Executive Summary

**Snapshot:** 30 June 2025  
**Target horizon:** July–December 2025  
**Eligible active customers:** 7,266

The six-month observed churn rate is **6.22%**. The simulated portfolio produces approximately **Rp5.56 billion** in annualized fee revenue, with about **Rp319.36 million** associated with customers who subsequently churn.

Branch-first customers churn at **10.28%**, versus **4.90%** for Mobile-first customers. SME has the highest segment churn rate at **7.04%**, while Mass contributes the largest observed annualized revenue at risk at approximately **Rp176.33 million**.

The logistic-regression model reaches **0.7238 ROC-AUC** on holdout data. The highest-risk 10% contain **34.29%** of observed churners, equivalent to **3.43× lift** over random targeting.

## Recommended Priorities
1. Use the highest-risk decile as the first retention queue, then refine using customer value.
2. Create a service and digital-adoption journey for high-risk Branch-first customers.
3. Escalate customers with recent complaints and falling transaction activity.
4. Treat SME as a high-rate problem and Mass as a high-total-value problem.
5. Validate interventions with controlled experiments before scaling.
