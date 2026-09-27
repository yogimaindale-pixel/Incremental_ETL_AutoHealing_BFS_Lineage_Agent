# 05 Data Model and Control Tables

## 1. Control Plane Schemas (`data/control_plane.db`)
- `pipeline_definition`: Pipeline metadata (`pipeline_id`, `name`, `source_table`, `target_table`, `watermark_column`, `lookback_minutes`, `batch_size`).
- `watermark_state`: Current high-watermark state (`pipeline_id`, `last_watermark`, `batch_id`, `updated_at`).
- `pipeline_run` & `pipeline_step_run`: Execution runtime tracking and step status logs.
- `failure_event`: Normalized failure event records.
- `incident`: Incident tracking state (`incident_id`, `status`, `classification`, `confidence_score`, `root_cause_node_id`, `selected_runbook_id`).
- `approval_request`: Human sign-off requests for high-risk actions (`approval_id`, `incident_id`, `risk_level`, `status`).
- `remediation_run`: Runbook execution record with `idempotency_key` enforcement.
- `audit_event`: Append-only transition log with `correlation_id` and `actor`.
- `lineage_node` & `lineage_edge`: Direct graph node and edge metadata tables.
