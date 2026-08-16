from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / 'data' / 'processed'
REPORTS = ROOT / 'reports'
FIGURES = REPORTS / 'figures'
MODELS = ROOT / 'models'
TARGET = 'churned_next_6m'
CATEGORICAL = ['gender', 'city', 'segment', 'preferred_channel']
NUMERIC = ['months_on_book','age','credit_score','digital_adoption_score','product_count','total_current_balance_idr','avg_transaction_count_3m','avg_transaction_value_3m','avg_balance_3m','avg_digital_logins_3m','complaints_3m','avg_credit_utilization_3m','avg_fee_revenue_3m']


def build_model() -> Pipeline:
    numeric = Pipeline([('imputer', SimpleImputer(strategy='median')), ('scale', StandardScaler())])
    categorical = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))])
    preprocess = ColumnTransformer([('num', numeric, NUMERIC), ('cat', categorical, CATEGORICAL)])
    return Pipeline([('preprocess', preprocess), ('model', LogisticRegression(max_iter=1500, class_weight='balanced', random_state=42))])


def save_figures(scored: pd.DataFrame, importance_df: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    segment = scored.groupby('segment', as_index=False)[TARGET].mean().sort_values(TARGET, ascending=False)
    plt.figure(figsize=(8,4.5)); plt.bar(segment['segment'], segment[TARGET] * 100); plt.ylabel('6-month churn rate (%)'); plt.title('Observed churn rate by segment'); plt.xticks(rotation=15); plt.tight_layout(); plt.savefig(FIGURES/'churn_by_segment.svg'); plt.close()
    top = importance_df.head(10).sort_values('importance')
    plt.figure(figsize=(9,5.5)); plt.barh(top['feature'], top['importance']); plt.xlabel('Mean decrease in holdout ROC-AUC when shuffled'); plt.title('Permutation importance on holdout data'); plt.tight_layout(); plt.savefig(FIGURES/'model_feature_importance.svg'); plt.close()
    risk = scored.assign(risk_decile=pd.qcut(scored['churn_probability'], 10, labels=False, duplicates='drop') + 1)
    deciles = risk.groupby('risk_decile', as_index=False)[TARGET].mean()
    plt.figure(figsize=(8,4.5)); plt.bar(deciles['risk_decile'].astype(str), deciles[TARGET] * 100); plt.xlabel('Predicted risk decile (10 = highest)'); plt.ylabel('Observed churn rate (%)'); plt.title('Model ranking quality by risk decile'); plt.tight_layout(); plt.savefig(FIGURES/'risk_decile_lift.svg'); plt.close()


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True); MODELS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED / 'snapshot_features.csv')
    X = df[NUMERIC + CATEGORICAL]; y = df[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    model = build_model(); model.fit(X_train, y_train)
    p = model.predict_proba(X_test)[:,1]; pred = (p >= 0.5).astype(int)
    metrics = {'roc_auc': round(float(roc_auc_score(y_test,p)),4), 'precision_at_0_5': round(float(precision_score(y_test,pred,zero_division=0)),4), 'recall_at_0_5': round(float(recall_score(y_test,pred,zero_division=0)),4), 'f1_at_0_5': round(float(f1_score(y_test,pred,zero_division=0)),4), 'test_rows': int(len(y_test)), 'test_churn_rate': round(float(y_test.mean()),4)}
    scored = df.copy(); scored['churn_probability'] = model.predict_proba(X)[:,1]
    scored['risk_band'] = pd.cut(scored['churn_probability'], [-np.inf,.35,.55,.72,np.inf], labels=['Low','Medium','High','Critical']).astype(str)
    top = scored[scored['churn_probability'] >= scored['churn_probability'].quantile(.90)]
    metrics['top_decile_churn_capture'] = round(float(top[TARGET].sum()/max(scored[TARGET].sum(),1)),4)
    metrics['top_decile_lift'] = round(float(top[TARGET].mean()/max(scored[TARGET].mean(),1e-9)),2)
    perm = permutation_importance(model, X_test, y_test, n_repeats=8, random_state=42, scoring='roc_auc')
    importance = pd.DataFrame({'feature': X_test.columns, 'importance': perm.importances_mean}).sort_values('importance', ascending=False)
    importance.to_csv(REPORTS/'permutation_importance.csv', index=False)
    scored[['customer_id','segment','city',TARGET,'churn_probability','risk_band','avg_fee_revenue_3m']].to_csv(PROCESSED/'risk_scores.csv', index=False)
    kpis = pd.read_csv(PROCESSED/'executive_kpis.csv').iloc[0].to_dict(); segment = pd.read_csv(PROCESSED/'churn_by_segment.csv'); risk_seg = pd.read_csv(PROCESSED/'revenue_at_risk_segments.csv')
    worst = segment.sort_values('churn_rate_pct', ascending=False).iloc[0]; highest = risk_seg.sort_values('annualized_observed_revenue_at_risk_idr', ascending=False).iloc[0]
    summary = {'snapshot_date':'2025-06-30','prediction_horizon':'6 months','active_customers':int(kpis['active_customers_at_snapshot']),'observed_churn_rate_6m_pct':float(kpis['churn_rate_6m_pct']),'annualized_fee_revenue_idr':int(kpis['annualized_portfolio_fee_revenue_idr']),'observed_revenue_at_risk_idr':int(kpis['observed_revenue_at_risk_idr']),'highest_churn_segment':str(worst['segment']),'highest_churn_segment_rate_pct':float(worst['churn_rate_pct']),'highest_revenue_risk_segment':str(highest['segment']),'model':metrics}
    (REPORTS/'business_summary.json').write_text(json.dumps(summary,indent=2)); (REPORTS/'model_metrics.json').write_text(json.dumps(metrics,indent=2)); save_figures(scored, importance); print(json.dumps(summary,indent=2))


if __name__ == '__main__': main()
