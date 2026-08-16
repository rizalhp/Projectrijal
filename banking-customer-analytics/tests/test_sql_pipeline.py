from __future__ import annotations
import sqlite3, sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from generate_data import generate_accounts, generate_customers, generate_monthly_activity

def test_snapshot_sql_has_binary_target_and_no_duplicate_customers(tmp_path: Path):
    rng=np.random.default_rng(19); customers=generate_customers(700,rng); accounts=generate_accounts(customers,rng); activity=generate_monthly_activity(customers,accounts,rng)
    customers=customers.drop(columns=[c for c in customers.columns if c.startswith('latent_')]); customers['join_date']=customers['join_date'].dt.strftime('%Y-%m-%d'); customers['churn_date']=customers['churn_date'].dt.strftime('%Y-%m-%d'); accounts['open_date']=accounts['open_date'].dt.strftime('%Y-%m-%d'); activity['activity_month']=activity['activity_month'].dt.strftime('%Y-%m-%d')
    with sqlite3.connect(tmp_path/'test.sqlite') as conn:
        customers.to_sql('customers',conn,index=False,if_exists='replace'); accounts.to_sql('accounts',conn,index=False,if_exists='replace'); activity.to_sql('monthly_activity',conn,index=False,if_exists='replace'); conn.executescript((ROOT/'sql'/'01_customer_360.sql').read_text()); snapshot=pd.read_sql_query('SELECT * FROM v_snapshot_features',conn)
    assert snapshot['customer_id'].is_unique; assert set(snapshot['churned_next_6m'].unique()).issubset({0,1}); assert (pd.to_datetime(snapshot['join_date'])<=pd.Timestamp('2025-04-01')).all()
