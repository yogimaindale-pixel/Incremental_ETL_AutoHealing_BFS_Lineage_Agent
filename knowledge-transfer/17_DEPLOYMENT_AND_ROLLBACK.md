# 17 Deployment and Rollback Guide

## 1. Deployment Steps
1. Checkout code release branch in target environment.
2. Run database migrations: `python3 scripts/seed_demo_data.py`.
3. Start REST API or cron ETL runner.

## 2. Rollback Procedure
If a deployment fails, `RollbackHandler` reverses applied changes and resets watermark states to previous valid checkpoints.
