from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def run(script: str) -> None:
    cmd = [sys.executable, str(ROOT/'src'/script)]; print('>', ' '.join(cmd)); subprocess.run(cmd, check=True)

def main() -> None:
    run('generate_data.py'); run('run_pipeline.py'); run('analyze_churn.py'); print('End-to-end build completed successfully.')

if __name__ == '__main__': main()
