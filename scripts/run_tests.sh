#!/usr/bin/env bash
set -e

echo "=== Running Incremental ETL Auto-Healing & Lineage Test Suite ==="

if [ -f ".venv/bin/pytest" ]; then
    .venv/bin/pytest tests/ -v --tb=short
else
    python3 -m pytest tests/ -v --tb=short
fi

echo "=== All Tests Passed Successfully ==="
