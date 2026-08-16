from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]; PROCESSED = ROOT/'data'/'processed'; REPORTS = ROOT/'reports'
st.set_page_config(page_title='Banking Customer Analytics', page_icon='📊', layout='wide')
st.title('Banking Customer Analytics & Churn Intelligence')
st.caption('Portfolio snapshot: 30 June 2025 | Churn horizon: next 6 months | Synthetic, privacy-safe banking data')
required=[PROCESSED/'snapshot_features.csv',PROCESSED/'risk_scores.csv',PROCESSED/'monthly_portfolio_trend.csv',REPORTS/'business_summary.json']
missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    st.error('Missing generated outputs: '+', '.join(missing)); st.code('python src/run_all.py'); st.stop()
features=pd.read_csv(PROCESSED/'snapshot_features.csv'); risk=pd.read_csv(PROCESSED/'risk_scores.csv'); trend=pd.read_csv(PROCESSED/'monthly_portfolio_trend.csv',parse_dates=['activity_month']); summary=json.loads((REPORTS/'business_summary.json').read_text())
with st.sidebar:
    st.header('Filters'); segment=st.selectbox('Segment',['All']+sorted(features['segment'].unique().tolist())); city=st.selectbox('City',['All']+sorted(features['city'].unique().tolist()))
filtered=features.copy()
if segment!='All': filtered=filtered[filtered['segment']==segment]
if city!='All': filtered=filtered[filtered['city']==city]
filtered_risk=risk[risk['customer_id'].isin(filtered['customer_id'])]
c1,c2,c3,c4=st.columns(4); c1.metric('Customers',f'{len(filtered):,}'); c2.metric('Observed 6M Churn',f"{filtered['churned_next_6m'].mean():.1%}"); c3.metric('Avg. Products',f"{filtered['product_count'].mean():.2f}"); c4.metric('Monthly Fee Revenue',f"Rp {filtered['avg_fee_revenue_3m'].sum()/1_000_000:,.1f}M")
st.subheader('Churn Diagnostics'); left,right=st.columns(2)
with left:
    x=filtered.groupby('segment',as_index=False)['churned_next_6m'].mean(); x['churn_rate_pct']=x['churned_next_6m']*100; st.plotly_chart(px.bar(x,x='segment',y='churn_rate_pct',title='Observed churn rate by segment'),use_container_width=True)
with right:
    x=filtered.groupby('preferred_channel',as_index=False)['churned_next_6m'].mean(); x['churn_rate_pct']=x['churned_next_6m']*100; st.plotly_chart(px.bar(x,x='preferred_channel',y='churn_rate_pct',title='Observed churn rate by channel'),use_container_width=True)
st.subheader('Predictive Risk View'); order=['Low','Medium','High','Critical']; dist=filtered_risk['risk_band'].value_counts().reindex(order,fill_value=0).rename_axis('risk_band').reset_index(name='customers'); st.plotly_chart(px.bar(dist,x='risk_band',y='customers',title='Customer distribution by predicted risk band'),use_container_width=True)
high=filtered_risk.sort_values('churn_probability',ascending=False).head(20).copy(); high['churn_probability']=(high['churn_probability']*100).round(1); st.dataframe(high,use_container_width=True,hide_index=True)
st.subheader('Portfolio Trend'); st.plotly_chart(px.line(trend,x='activity_month',y='active_customers',markers=True,title='Monthly active customers'),use_container_width=True)
with st.expander('Model & methodology notes'):
    st.write('Features are observed on or before 30 June 2025; the target is churn during July–December 2025, preventing future-information leakage.'); st.json(summary['model'])
