from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
DATA_START = pd.Timestamp('2024-01-01')
DATA_END = pd.Timestamp('2025-12-01')
SNAPSHOT_DATE = pd.Timestamp('2025-06-30')

CITIES = ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Makassar', 'Semarang', 'Yogyakarta', 'Denpasar']
CITY_WEIGHTS = [0.31, 0.14, 0.14, 0.10, 0.09, 0.08, 0.08, 0.06]
SEGMENTS = ['Mass', 'Emerging Affluent', 'Affluent', 'SME']
SEGMENT_WEIGHTS = [0.57, 0.24, 0.10, 0.09]
CHANNELS = ['Mobile-first', 'Mixed', 'Branch-first', 'Web-first']
CHANNEL_WEIGHTS = [0.45, 0.31, 0.15, 0.09]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def month_start(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(ts.year, ts.month, 1)


def generate_customers(n_customers: int, rng: np.random.Generator) -> pd.DataFrame:
    customer_ids = [f'C{idx:06d}' for idx in range(1, n_customers + 1)]
    segment = rng.choice(SEGMENTS, n_customers, p=SEGMENT_WEIGHTS)
    city = rng.choice(CITIES, n_customers, p=CITY_WEIGHTS)
    gender = rng.choice(['Female', 'Male'], n_customers, p=[0.49, 0.51])
    channel = rng.choice(CHANNELS, n_customers, p=CHANNEL_WEIGHTS)
    age = np.clip(np.rint(rng.normal(38, 11, n_customers)), 18, 70).astype(int)
    birth_year = 2025 - age
    join_ord = rng.integers(pd.Timestamp('2019-01-01').value // 10**9, pd.Timestamp('2025-03-01').value // 10**9, n_customers)
    join_date = pd.to_datetime(join_ord, unit='s').to_period('M').to_timestamp()

    income_base = {'Mass': 7_000_000, 'Emerging Affluent': 16_000_000, 'Affluent': 38_000_000, 'SME': 28_000_000}
    income = np.array([income_base[s] for s in segment], dtype=float)
    income *= rng.lognormal(mean=0, sigma=0.38, size=n_customers)
    income = np.round(income / 100_000) * 100_000
    credit_score = np.clip(610 + (np.log1p(income) - np.log(7_000_000)) * 28 + rng.normal(0, 65, n_customers), 300, 850).round().astype(int)

    digital_base = np.select([channel == 'Mobile-first', channel == 'Web-first', channel == 'Mixed'], [0.80, 0.72, 0.62], default=0.34)
    digital_adoption = np.clip(digital_base + rng.normal(0, 0.13, n_customers), 0.02, 0.99)
    engagement = np.clip(0.48 + 0.33 * digital_adoption + rng.normal(0, 0.16, n_customers), 0.03, 0.99)
    service_risk = np.clip(rng.beta(1.8, 4.5, n_customers) + rng.normal(0, 0.05, n_customers), 0, 1)
    fee_sensitivity = np.clip(rng.beta(2.2, 3.5, n_customers), 0, 1)

    churn_logit = (-2.65 + 1.45 * (1 - engagement) + 1.00 * service_risk + 0.70 * fee_sensitivity + 0.48 * (credit_score < 560) + 0.32 * (channel == 'Branch-first') - 0.40 * digital_adoption)
    churn_flag = rng.random(n_customers) < sigmoid(churn_logit)
    churn_date = pd.Series(pd.NaT, index=np.arange(n_customers), dtype='datetime64[ns]')
    churnable_months = pd.date_range('2024-04-01', DATA_END, freq='MS')
    weights = np.linspace(0.65, 1.35, len(churnable_months)); weights = weights / weights.sum()
    selected = rng.choice(churnable_months, size=int(churn_flag.sum()), p=weights)
    churn_date.loc[np.flatnonzero(churn_flag)] = selected
    too_early = churn_date.notna() & (churn_date < join_date)
    churn_date.loc[too_early] = join_date[too_early].to_period('M').to_timestamp() + pd.offsets.MonthBegin(2)
    churn_date = churn_date.where(churn_date <= DATA_END, pd.NaT)

    risk_tier = pd.cut(credit_score, bins=[0, 520, 620, 720, 900], labels=['High', 'Medium', 'Low', 'Very Low'], include_lowest=True).astype(str)
    return pd.DataFrame({
        'customer_id': customer_ids, 'join_date': join_date, 'birth_year': birth_year, 'gender': gender, 'city': city,
        'segment': segment, 'preferred_channel': channel, 'monthly_income_idr': income.astype(int), 'credit_score': credit_score,
        'risk_tier': risk_tier, 'digital_adoption_score': np.round(digital_adoption, 4), 'churn_date': churn_date,
        'latent_engagement': engagement, 'latent_service_risk': service_risk, 'latent_fee_sensitivity': fee_sensitivity,
    })


def generate_accounts(customers: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    records = []; account_counter = 1
    for row in customers.itertuples(index=False):
        products = ['Savings']; income = row.monthly_income_idr; engagement = row.latent_engagement
        if rng.random() < 0.46: products.append('Current Account')
        if rng.random() < np.clip(0.30 + (row.credit_score - 550) / 600, 0.18, 0.72): products.append('Credit Card')
        if rng.random() < np.clip(0.10 + (income / 80_000_000), 0.08, 0.38): products.append('Personal Loan')
        if row.segment in ('Emerging Affluent', 'Affluent') and rng.random() < 0.36: products.append('Investment')
        for product in products:
            if product == 'Savings':
                balance = income * rng.uniform(0.8, 5.5) * (0.7 + engagement); fee = rng.choice([0, 5_000, 10_000, 15_000], p=[0.15, 0.25, 0.45, 0.15])
            elif product == 'Current Account':
                balance = income * rng.uniform(0.3, 2.3); fee = rng.choice([10_000, 15_000, 20_000, 25_000])
            elif product == 'Credit Card':
                balance = -income * rng.uniform(0.03, 0.35); fee = rng.choice([0, 25_000, 50_000], p=[0.55, 0.30, 0.15])
            elif product == 'Personal Loan':
                balance = -income * rng.uniform(2.0, 12.0); fee = rng.choice([20_000, 30_000, 40_000])
            else:
                balance = income * rng.uniform(2.5, 16.0); fee = rng.choice([0, 10_000, 20_000], p=[0.65, 0.25, 0.10])
            open_date = max(row.join_date, pd.Timestamp('2019-01-01')) + pd.DateOffset(months=int(rng.integers(0, 13)))
            open_date = min(open_date, DATA_END)
            records.append({'account_id': f'A{account_counter:07d}', 'customer_id': row.customer_id, 'product_type': product, 'open_date': month_start(open_date), 'current_balance_idr': int(round(balance / 1_000) * 1_000), 'monthly_fee_idr': int(fee), 'is_active': int(pd.isna(row.churn_date) or row.churn_date > DATA_END)})
            account_counter += 1
    return pd.DataFrame(records)


def generate_monthly_activity(customers: pd.DataFrame, accounts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    account_agg = accounts.groupby('customer_id').agg(product_count=('account_id', 'count'), monthly_account_fees=('monthly_fee_idr', 'sum'))
    rows = []; all_months = pd.date_range(DATA_START, DATA_END, freq='MS')
    for c in customers.itertuples(index=False):
        start = max(month_start(c.join_date), DATA_START)
        end = DATA_END if pd.isna(c.churn_date) else min(month_start(c.churn_date), DATA_END)
        if start > DATA_END: continue
        customer_months = all_months[(all_months >= start) & (all_months <= end)]; acc = account_agg.loc[c.customer_id]
        base_balance = max(750_000, c.monthly_income_idr * rng.uniform(0.7, 3.2) * (0.65 + c.latent_engagement))
        base_txn = 5 + 30 * c.latent_engagement + 0.00000045 * c.monthly_income_idr
        base_ticket = 145_000 + 0.025 * c.monthly_income_idr
        for m in customer_months:
            months_to_churn = None if pd.isna(c.churn_date) else (c.churn_date.year - m.year) * 12 + (c.churn_date.month - m.month)
            decay = max(0.33, 1 - (5 - months_to_churn) * 0.11) if months_to_churn is not None and 0 <= months_to_churn <= 4 else 1.0
            seasonal = 1 + 0.08 * np.sin((m.month - 1) / 12 * 2 * np.pi)
            tx_count = max(0, int(round(rng.normal(base_txn * seasonal * decay, 4))))
            avg_ticket = max(25_000, rng.normal(base_ticket, base_ticket * 0.20)); tx_value = tx_count * avg_ticket
            avg_balance = max(20_000, rng.normal(base_balance * decay, base_balance * 0.18))
            digital_logins = max(0, int(round(rng.normal((2 + 19 * c.digital_adoption_score * c.latent_engagement) * decay, 3))))
            complaint_lambda = 0.05 + 0.72 * c.latent_service_risk + 0.28 * c.latent_fee_sensitivity + (0.38 if months_to_churn is not None and 0 <= months_to_churn <= 3 else 0)
            complaints = int(rng.poisson(complaint_lambda)); utilization = np.clip(rng.beta(2.0 + 2.5 * c.latent_service_risk, 3.5), 0.01, 0.99)
            fee_revenue = float(acc.monthly_account_fees + tx_count * rng.uniform(650, 1_250))
            rows.append({'customer_id': c.customer_id, 'activity_month': m, 'transaction_count': tx_count, 'transaction_value_idr': int(round(tx_value / 1_000) * 1_000), 'avg_balance_idr': int(round(avg_balance / 1_000) * 1_000), 'digital_logins': digital_logins, 'complaints': complaints, 'credit_utilization': round(float(utilization), 4), 'fee_revenue_idr': int(round(fee_revenue / 1_000) * 1_000), 'product_count': int(acc.product_count)})
    return pd.DataFrame(rows)


def write_outputs(customers, accounts, activity, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    customers.drop(columns=[c for c in customers.columns if c.startswith('latent_')]).to_csv(output_dir / 'customers.csv', index=False, date_format='%Y-%m-%d')
    accounts.to_csv(output_dir / 'accounts.csv', index=False, date_format='%Y-%m-%d')
    activity.to_csv(output_dir / 'monthly_activity.csv', index=False, date_format='%Y-%m-%d')


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a reproducible synthetic retail-banking dataset.')
    parser.add_argument('--customers', type=int, default=8000); parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'data' / 'raw'); parser.add_argument('--seed', type=int, default=SEED)
    args = parser.parse_args(); rng = np.random.default_rng(args.seed)
    customers = generate_customers(args.customers, rng); accounts = generate_accounts(customers, rng); activity = generate_monthly_activity(customers, accounts, rng)
    write_outputs(customers, accounts, activity, args.output_dir)
    print(f'Generated {len(customers):,} customers, {len(accounts):,} accounts, {len(activity):,} monthly activity rows.')
    print(f'Portfolio churn by end of data window: {customers["churn_date"].notna().mean():.1%}')
    print(f'Customers with churn after snapshot: {((customers["churn_date"] > SNAPSHOT_DATE) & (customers["churn_date"] <= DATA_END)).mean():.1%}')


if __name__ == '__main__':
    main()
