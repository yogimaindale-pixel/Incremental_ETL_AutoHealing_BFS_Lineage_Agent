# 14 Troubleshooting Guide

## Common Symptoms & Actions

| Symptom | Cause | Resolution |
|---|---|---|
| Watermark does not advance | Extraction returned 0 records or run failed | Verify source `updated_at` records exist and check `failure_event` table |
| Duplicate rows in target | Missing primary key index | `IncrementalLoader` deduplicates rows; check quarantine table |
| Incident stuck in `AWAITING_APPROVAL` | High-risk runbook requires sign-off | Call `POST /incidents/{incident_id}/approve` |
| Lineage graph missing nodes | Unregistered lineage source | Add missing nodes/edges in `config/lineage_sources.yaml` |
