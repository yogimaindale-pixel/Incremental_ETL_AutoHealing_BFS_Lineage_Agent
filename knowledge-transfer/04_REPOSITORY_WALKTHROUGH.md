# 04 Repository Walkthrough

## 1. File Structure
```text
.
├── Makefile                     # Helper commands (make test, make demo)
├── README.md                    # Project landing page
├── run_demo.py                  # Console CLI runner
├── config/                      # YAML configuration suite
│   ├── data_quality_rules.yaml
│   ├── environments.yaml
│   ├── healing_rules.yaml
│   ├── lineage_sources.yaml
│   ├── pipelines.yaml
│   └── risk_policy.yaml
├── docs/                        # Architecture and operations documentation
├── knowledge-transfer/          # Complete knowledge transfer package
├── scripts/                     # Shell scripts and database setup
│   ├── bootstrap.sh
│   ├── reset_demo.py
│   ├── run_tests.sh
│   └── seed_demo_data.py
├── sql/                         # Database DDL schemas
│   ├── control_schema.sql
│   ├── sample_source.sql
│   └── sample_target.sql
├── src/                         # Python application source code
└── tests/                       # Unit, integration, and scenario test suite
```

## 2. Request-to-Code Mapping
- To modify failure classification rules -> edit `config/healing_rules.yaml`.
- To add a new runbook -> edit `src/healing/runbook_registry.py` and register rule in `config/healing_rules.yaml`.
- To update BFS lineage traversal -> edit `src/lineage/bfs_traversal.py`.
- To alter risk policy -> edit `config/risk_policy.yaml` and `src/healing/risk_engine.py`.
