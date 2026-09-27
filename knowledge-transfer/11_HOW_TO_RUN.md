# 11 How to Run Guide

## 1. Console CLI Commands
```bash
# Run happy-path incremental ETL + all 12 failure scenario demonstrations
python3 run_demo.py --all-scenarios

# Run normal incremental ETL pipeline only
python3 run_demo.py --etl-only

# Query upstream lineage for a table
python3 run_demo.py --lineage-upstream fact_orders

# Query downstream lineage for a source
python3 run_demo.py --lineage-downstream source_orders

# Run test suite
bash scripts/run_tests.sh
```

## 2. API Server
To launch the FastAPI REST server:
```bash
.venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```
