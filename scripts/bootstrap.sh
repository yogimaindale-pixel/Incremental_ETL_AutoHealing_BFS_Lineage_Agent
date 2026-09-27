#!/usr/bin/env bash
set -e

echo "=== Initializing Incremental ETL Auto-Healing Agent Environment ==="

mkdir -p data/input data/output data/quarantine data/checkpoints artifacts

python3 -m pip install --quiet -r requirements.txt || true

echo "Seeding demo data and control schemas..."
python3 scripts/seed_demo_data.py

echo "=== Environment Bootstrap Completed Successfully ==="
