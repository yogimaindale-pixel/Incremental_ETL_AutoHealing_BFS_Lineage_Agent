# Operations Guide

## Daily Operational Tasks
1. **Monitor Health**: `GET /health` or `python3 run_demo.py --etl-only`
2. **Review Metrics**: `GET /metrics`
3. **Approve Incidents**: `POST /incidents/{incident_id}/approve`
4. **Inspect Lineage**: `python3 run_demo.py --lineage-upstream fact_orders`
