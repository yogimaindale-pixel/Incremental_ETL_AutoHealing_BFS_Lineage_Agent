# 15 Testing Guide

## 1. Test Suite Structure
- `tests/unit/`: Unit tests for watermarking, BFS lineage, classification, state machine, and risk rules.
- `tests/integration/`: Integration tests for ETL pipeline, incident coordinator, and FastAPI endpoints.
- `tests/failure_scenarios/`: End-to-end tests for all 12 failure scenarios.

## 2. Execution Command
```bash
bash scripts/run_tests.sh
```
