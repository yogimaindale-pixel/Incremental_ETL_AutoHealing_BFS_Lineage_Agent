# Console Demo Guide

## Quick Start
```bash
# 1. Environment Bootstrap
bash scripts/bootstrap.sh

# 2. Run All Demo Scenarios & ETL
python3 run_demo.py --all-scenarios

# 3. Query Lineage in Console
python3 run_demo.py --lineage-upstream fact_orders
python3 run_demo.py --lineage-downstream source_orders

# 4. Run Test Suite
bash scripts/run_tests.sh
```
