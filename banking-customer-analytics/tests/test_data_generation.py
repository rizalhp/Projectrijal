from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from generate_data import generate_accounts, generate_customers, generate_monthly_activity

def test_generated_data_respects_core_quality_rules():
    rng=np.random.default_rng(7); customers=generate_customers(250,rng); accounts=generate_accounts(customers,rng); activity=generate_monthly_activity(customers,accounts,rng)
    assert customers['customer_id'].is_unique; assert accounts['account_id'].is_unique
    assert set(accounts['customer_id']).issubset(set(customers['customer_id'])); assert set(activity['customer_id']).issubset(set(customers['customer_id']))
    assert customers['credit_score'].between(300,850).all(); assert customers['digital_adoption_score'].between(0,1).all(); assert activity['credit_utilization'].between(0,1).all(); assert (activity['transaction_count']>=0).all(); assert (activity['avg_balance_idr']>=0).all()

def test_churn_never_precedes_join_date():
    rng=np.random.default_rng(11); customers=generate_customers(500,rng); churners=customers[customers['churn_date'].notna()]; assert (churners['churn_date']>=churners['join_date']).all()
