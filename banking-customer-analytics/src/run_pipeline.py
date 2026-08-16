from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
SQL_DIR = ROOT / 'sql'
DB_PATH = ROOT / 'data' / 'banking_analytics.sqlite'
TABLE_FILES = {'customers': RAW / 'customers.csv', 'accounts': RAW / 'accounts.csv', 'monthly_activity': RAW / 'monthly_activity.csv'}
EXPORTS = {
    'snapshot_features': 'SELECT * FROM v_snapshot_features', 'executive_kpis': 'SELECT * FROM v_executive_kpis',
    'churn_by_segment': 'SELECT * FROM v_churn_by_segment', 'churn_by_channel': 'SELECT * FROM v_churn_by_channel',
    'retention_cohorts': 'SELECT * FROM v_retention_cohorts', 'monthly_portfolio_trend': 'SELECT * FROM v_monthly_portfolio_trend',
    'revenue_at_risk_segments': 'SELECT * FROM v_revenue_at_risk_segments',
}


def load_csvs(conn: sqlite3.Connection) -> None:
    for table_name, path in TABLE_FILES.items():
        if not path.exists(): raise FileNotFoundError(f'Missing {path}. Run src/generate_data.py first.')
        parse_dates = ['join_date', 'churn_date'] if table_name == 'customers' else ['open_date'] if table_name == 'accounts' else ['activity_month']
        df = pd.read_csv(path, parse_dates=parse_dates)
        for col in parse_dates:
            if col in df.columns: df[col] = df[col].dt.strftime('%Y-%m-%d')
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_activity_customer_month ON monthly_activity(customer_id, activity_month)')
    conn.commit()


def run_sql(conn: sqlite3.Connection) -> None:
    for sql_file in sorted(SQL_DIR.glob('*.sql')): conn.executescript(sql_file.read_text(encoding='utf-8'))
    conn.commit()


def export_outputs(conn: sqlite3.Connection) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    for output_name, query in EXPORTS.items(): pd.read_sql_query(query, conn).to_csv(PROCESSED / f'{output_name}.csv', index=False)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument('--db-path', type=Path, default=DB_PATH); args = parser.parse_args()
    args.db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(args.db_path) as conn:
        load_csvs(conn); run_sql(conn); export_outputs(conn)
    print(f'Pipeline complete. SQLite database: {args.db_path}')


if __name__ == '__main__': main()
