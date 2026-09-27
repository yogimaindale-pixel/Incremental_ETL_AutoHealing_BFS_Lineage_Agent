# Incremental ETL Auto-Healing & BFS Data Lineage Agent

Deterministic, production-grade Incremental ETL Auto-Healing Agent combined with a Breadth-First Search (BFS) Data Lineage and Impact Analysis Engine.

## Features
- **Incremental Ingestion with Watermarking**: Watermark tracking, lookback windows, key deduplication, staging, MERGE/UPSERT, and automatic quarantining of invalid rows.
- **BFS Data Lineage Engine**: Cycle-safe directed property graph supporting upstream root cause analysis and downstream blast radius calculation with deterministic neighbor sorting.
- **Signature Classification & RCA**: Priority-based error signature classifier and evidence-backed root cause candidate scoring.
- **Policy-Governed Runbooks**: Allow-listed runbooks, risk-policy approval gates, idempotency enforcement, validation checks, and automatic rollbacks.
- **Console / CLI Driven**: Fully operated via CLI console runner without requiring a web UI frontend.
- **Immutable Control & Audit Plane**: Append-only state machine transitions and audit events in SQLite.

## Project Structure
```text
.
├── Makefile
├── README.md
├── pyproject.toml
├── requirements.txt
├── run_demo.py
├── config/
│   ├── data_quality_rules.yaml
│   ├── environments.yaml
│   ├── healing_rules.yaml
│   ├── lineage_sources.yaml
│   ├── pipelines.yaml
│   └── risk_policy.yaml
├── docs/
├── knowledge-transfer/
├── scripts/
├── sql/
├── src/
│   ├── api/
│   ├── common/
│   ├── diagnosis/
│   ├── healing/
│   ├── ingestion/
│   ├── lineage/
│   ├── observability/
│   ├── orchestration/
│   ├── reporting/
│   └── validation/
└── tests/
```

## Quick Start
```bash
# Bootstrap Environment
bash scripts/bootstrap.sh

# Run Incremental ETL & All 12 Demo Scenarios in Console
python3 run_demo.py --all-scenarios

# Run Test Suite
bash scripts/run_tests.sh
```

## License
MIT
