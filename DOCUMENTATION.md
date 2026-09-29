# Incremental ETL Auto-Healing BFS Lineage Agent - Technical Specification

This document details the architecture, data schemas, signature classification matrix, state machine transitions, and auto-healing runbook catalog for the **Incremental ETL Auto-Healing BFS Lineage Agent Platform**.

---

## 1. System Architecture & Components

The platform consists of 7 decoupled micro-modules:

1. **Observability & Failure Detection (`src/observability/`)**: Captures raw pipeline execution errors, extracts stack traces, normalizes failure events into structured payloads.
2. **Signature Classifier (`src/diagnosis/signature_classifier.py`)**: Evaluates regex rules against normalized error messages to classify failure patterns (e.g. `SCHEMA_EVOLUTION_MISSING_COLUMN`, `WATERMARK_DRIFT`, `PERMISSION_DENIED`).
3. **BFS Lineage Traversal Engine (`src/lineage/`)**: Builds directed dependency graph across systems, databases, pipelines, tables, and reports using NetworkX and executes cycle-safe BFS upstream/downstream impact analysis.
4. **Root Cause Engine (`src/diagnosis/root_cause_engine.py`)**: Ranks candidate root-cause nodes by calculating likelihood scores based on lineage proximity, error signatures, and execution timestamps.
5. **Auto-Healing Runbook Registry (`src/healing/runbook_registry.py`)**: Holds allow-listed remediation strategies mapped to failure categories.
6. **Remediation & Rollback Engine (`src/healing/`)**: Executes selected runbooks safely and triggers circuit breaker rollbacks if remediation fails.
7. **Incident State Machine (`src/orchestration/state_machine.py`)**: Enforces 14 formal incident lifecycle state transitions with immutable SQLite audit logging.

---

## 2. 14 Incident Lifecycle States

| State | Description | Next Allowed States |
|---|---|---|
| `DETECTED` | Raw error captured by failure detector | `NORMALIZED`, `ESCALATED` |
| `NORMALIZED` | Event parsed into standard schema | `CLASSIFIED`, `ESCALATED` |
| `CLASSIFIED` | Signature matched against rule catalog | `EVIDENCE_COLLECTED`, `ESCALATED` |
| `EVIDENCE_COLLECTED` | Logs and system state gathered | `LINEAGE_TRAVERSED`, `ESCALATED` |
| `LINEAGE_TRAVERSED` | Upstream/downstream impact mapped via BFS | `ROOT_CAUSE_IDENTIFIED`, `ESCALATED` |
| `ROOT_CAUSE_IDENTIFIED` | Suspected root cause node selected | `REMEDIATION_SELECTED`, `ESCALATED` |
| `REMEDIATION_SELECTED` | Auto-healing runbook assigned | `AWAITING_APPROVAL`, `REMEDIATING`, `ESCALATED` |
| `AWAITING_APPROVAL` | High-risk runbook pending human review | `REMEDIATING`, `ESCALATED` |
| `REMEDIATING` | Runbook action executing | `VALIDATING`, `ROLLED_BACK`, `ESCALATED` |
| `VALIDATING` | Post-healing validation running | `RECOVERED`, `ROLLED_BACK`, `ESCALATED` |
| `RECOVERED` | Healing verified successfully | `CLOSED` |
| `ROLLED_BACK` | Circuit breaker executed rollback | `ESCALATED`, `CLOSED` |
| `ESCALATED` | Human operator intervention required | `CLOSED` |
| `CLOSED` | Final terminal state | None |

---

## 3. Database Schemas (`control_plane.db`)

### Table: `incident`
* `incident_id` (TEXT PRIMARY KEY)
* `event_id` (TEXT)
* `pipeline_id` (TEXT)
* `correlation_id` (TEXT)
* `status` (TEXT)
* `classification` (TEXT)
* `confidence_score` (REAL)
* `root_cause_node_id` (TEXT)
* `selected_runbook_id` (TEXT)
* `created_at` (TIMESTAMP)
* `updated_at` (TIMESTAMP)

### Table: `audit_event`
* `audit_id` (TEXT PRIMARY KEY)
* `correlation_id` (TEXT)
* `event_type` (TEXT)
* `state_from` (TEXT)
* `state_to` (TEXT)
* `actor` (TEXT)
* `details` (TEXT JSON)
* `occurred_at` (TIMESTAMP)

---

## 4. Runbook Catalog & Risk Matrix

| Runbook ID | Title | Risk Level | Target Incident Category | Auto-Approval |
|---|---|---|---|---|
| `RB-RETRY-001` | Transient Retry with Backoff | `LOW` | Network timeout / Lock contention | Yes |
| `RB-WAIT-FILE-001` | Delayed File Landing Wait | `LOW` | File missing / S3 delay | Yes |
| `RB-RESET-CHK-002` | Reset Watermark Checkpoint | `MEDIUM` | Watermark drift / Dup keys | Yes |
| `RB-QUARANTINE-001` | Quarantine Malformed Rows | `MEDIUM` | Data quality threshold breach | Yes |
| `RB-ADD-SCHEMA-001` | Non-Destructive DDL Schema Add | `HIGH` | Missing target table column | Yes |
| `RB-ESCALATE-001` | Escalate to Human Operator | `READ_ONLY` | Permission denied / Fatal | Yes |
