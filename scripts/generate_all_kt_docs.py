import os
import json

def generate():
    kt_dir = "knowledge-transfer"
    diagrams_dir = os.path.join(kt_dir, "diagrams")
    examples_dir = os.path.join(kt_dir, "examples")

    os.makedirs(kt_dir, exist_ok=True)
    os.makedirs(diagrams_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)

    docs = {
        "02_BUSINESS_PROBLEM_AND_VALUE.md": """# 02 Business Problem and Technical Value

## 1. Context & Business Problem
In modern enterprise data platforms, incremental ETL pipelines process millions of events per hour. When data pipelines fail due to transient network resets, late arriving source files, duplicate primary keys, or schema drift:
- Data engineering teams spend hours manually inspecting logs and SQL queries.
- Upstream root causes and downstream business dashboard impacts remain hidden without automated lineage mapping.
- Uncoordinated retries or manual patches risk data corruption, duplicate loads, or broken financial reports.

## 2. Technical Value Proposition
The **Incremental ETL Auto-Healing & BFS Data Lineage Agent** solves these challenges by providing:
1. **Deterministic Auto-Healing**: Zero-LLM error signature classification and automated allow-listed runbooks.
2. **BFS Lineage Traversal**: Cycle-safe Breadth-First Search (BFS) graph traversal to isolate upstream root causes and calculate downstream blast radius.
3. **Risk-Policy Governed Approvals**: Automated execution for low-risk actions and human sign-off gates for high-risk actions.
4. **Immutable Audit Plane**: Append-only state machine transitions logged in SQLite.

## 3. Operational KPIs
- **Detection-to-Classification Time**: < 100 milliseconds
- **Mean Time To Recovery (MTTR)**: Reduced from hours to < 10 seconds for auto-healed incidents
- **Auto-Heal Rate**: 80%+ of deterministic pipeline failures
- **False Remediation Count**: 0 (governed by idempotency keys and precheck validation)
""",

        "03_ARCHITECTURE_AND_COMPONENTS.md": """# 03 Architecture and Component Details

## 1. System Architecture
The platform is organized into 8 modular packages under `src/`:

1. **`src/ingestion/`**: Handles watermark state tracking (`WatermarkManager`), lookback window extraction (`IncrementalExtractor`), deduplication, quarantining, and target table UPSERT (`IncrementalLoader`).
2. **`src/observability/`**: Normalizes exceptions (`FailureDetector`), logs pipeline/step runs (`EventCollector`), and computes operational MTTR metrics (`MetricsCalculator`).
3. **`src/lineage/`**: Parses YAML lineage metadata (`MetadataParser`), builds NetworkX property graph (`GraphBuilder`), performs cycle-safe BFS traversal (`BFSTraversal`), and calculates blast radius (`ImpactAnalyzer`).
4. **`src/diagnosis/`**: Matches error signatures against regex rules (`SignatureClassifier`), collects historical run logs (`EvidenceCollector`), and ranks root cause candidates (`RootCauseEngine`).
5. **`src/healing/`**: Selects runbooks (`HealingRuleEngine`), evaluates risk policy (`RiskEngine`), executes allow-listed runbooks (`RunbookRegistry`, `RemediationExecutor`), and handles rollbacks (`RollbackHandler`).
6. **`src/validation/`**: Performs technical reachability checks (`TechnicalValidator`), source-to-target reconciliation (`ReconciliationEngine`), and data quality threshold checks (`DataQualityValidator`).
7. **`src/orchestration/`**: Drives state machine transitions (`IncidentStateMachine`) and orchestrates end-to-end incident resolution (`IncidentCoordinator`).
8. **`src/api/`**: Provides FastAPI REST endpoints (`src/api/app.py`).

## 2. Control Plane vs Data Plane
- **Control Plane**: `data/control_plane.db` stores pipeline definitions, watermark states, run logs, failure events, incidents, approval requests, remediation runs, validation results, and audit events.
- **Data Plane**: `data/source.db` (source data) and `data/target.db` (data warehouse tables).
""",

        "04_REPOSITORY_WALKTHROUGH.md": """# 04 Repository Walkthrough

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
""",

        "05_DATA_MODEL_AND_CONTROL_TABLES.md": """# 05 Data Model and Control Tables

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
""",

        "06_INCREMENTAL_ETL_FLOW.md": """# 06 Incremental ETL Workflow

## 1. Step-by-Step Execution Sequence
1. **Read Watermark**: `WatermarkManager.get_watermark(pipeline_id)` retrieves the last committed timestamp (e.g. `2026-09-26T19:00:00`).
2. **Determine Bounds**: Fixed upper bound = `datetime.utcnow()`. Lower bound = `last_watermark - lookback_minutes` (e.g. 60 minute lookback window).
3. **Extract Batch**: `IncrementalExtractor.extract_batch()` executes parameterized SQL query `SELECT * FROM source_table WHERE updated_at >= ? AND updated_at <= ?`.
4. **Deduplicate**: `IncrementalLoader.deduplicate()` drops duplicate primary key rows within batch, quarantining invalid duplicates.
5. **UPSERT Target**: `IncrementalLoader.upsert_target()` executes atomic SQLite `INSERT INTO target_table VALUES (...) ON CONFLICT(key) DO UPDATE`.
6. **Commit Watermark**: `WatermarkManager.commit_watermark()` updates watermark timestamp in `watermark_state` table.
""",

        "07_BFS_LINEAGE_AND_IMPACT_ANALYSIS.md": """# 07 BFS Data Lineage and Impact Analysis

## 1. Breadth-First Search (BFS) Traversal
BFS is used for deterministic, level-by-level dependency discovery across the lineage property graph.

### Upstream Traversal (Root Cause Search)
- Traverses in-edges (`predecessors`) from a target node.
- Uses a `queue` and a `visited` set to guarantee cycle safety.
- Sorts neighbor nodes alphabetically by `node_id` to guarantee reproducible execution order.

### Downstream Traversal (Blast Radius Calculation)
- Traverses out-edges (`successors`) from a source/failed node.
- Identifies all downstream pipelines, target tables, REST APIs, and executive report dashboards that will be impacted by the failure.

## 2. Shortest Dependency Path
`BFSTraversal.shortest_dependency_path(graph, start_id, end_id)` finds the shortest directed path between two nodes in the graph.
""",

        "08_FAILURE_DETECTION_AND_DIAGNOSIS.md": """# 08 Failure Detection and Diagnosis

## 1. Exception Normalization
When a pipeline step raises an unhandled exception, `FailureDetector.normalize_exception()` converts it into a standardized `FailureEvent` object containing:
- `event_id`, `run_id`, `step_id`, `job_name`
- `error_code` (e.g., `TIMEOUT`, `FILE_NOT_FOUND`, `DUPLICATE_KEY`)
- `error_message`, `occurred_at`, `correlation_id`

## 2. Error Signature Classification
`SignatureClassifier` evaluates the event against regex rules in `config/healing_rules.yaml` ordered by priority.
Matches return a `ClassificationResult` containing:
- `classification` (e.g. `TRANSIENT_CONNECTION`, `SOURCE_FILE_LATE`)
- `confidence` score (e.g. `1.0`)
- `runbook_id` (e.g. `RB-RETRY-001`, `RB-WAIT-FILE-001`)
""",

        "09_HEALING_RULES_AND_RUNBOOKS.md": """# 09 Healing Rules and Runbooks Catalog

## Runbook Catalog Matrix

| Rule ID | Failure Signature | Runbook ID | Action Summary | Risk Level |
|---|---|---|---|---|
| `ETL-CONN-001` | `TRANSIENT_CONNECTION` | `RB-RETRY-001` | Exponential backoff retry | `LOW` |
| `ETL-FILE-001` | `SOURCE_FILE_LATE` | `RB-WAIT-FILE-001` | Wait window recheck | `LOW` |
| `ETL-DUP-001` | `DUPLICATE_BUSINESS_KEY` | `RB-QUARANTINE-001` | Quarantine duplicate rows | `MEDIUM` |
| `ETL-STALE-001` | `STALE_CHECKPOINT` | `RB-RESET-CHK-002` | Reset watermark to checkpoint | `HIGH` |
| `ETL-PART-001` | `TARGET_PARTITION_MISSING` | `RB-CREATE-PART-001` | Create target partition | `MEDIUM` |
| `ETL-SCHEMA-ADD-001` | `SCHEMA_ADDITIVE_DRIFT` | `RB-ADD-SCHEMA-001` | Alter target table add column | `MEDIUM` |
| `ETL-SCHEMA-BRK-001` | `SCHEMA_BREAKING_DRIFT` | `RB-ESCALATE-001` | Manual review escalation | `HIGH` |
| `ETL-AUTH-001` | `INSUFFICIENT_PERMISSION` | `RB-ESCALATE-001` | Escalation to security | `HIGH` |
| `ETL-DQ-BREACH-001` | `DATA_QUALITY_THRESHOLD_BREACH` | `RB-QUARANTINE-001` | Quarantine breaching rows | `MEDIUM` |
""",

        "10_SETUP_AND_CONFIGURATION.md": """# 10 Setup and Configuration Guide

## 1. Prerequisites
- Python 3.11+ (Python 3.14 tested)
- SQLite3
- Git

## 2. Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/yogimaindale-pixel/Incremental_ETL_AutoHealing_BFS_Lineage_Agent.git
cd Incremental_ETL_AutoHealing_BFS_Lineage_Agent

# 2. Run bootstrap script
bash scripts/bootstrap.sh
```
""",

        "11_HOW_TO_RUN.md": """# 11 How to Run Guide

## 1. Console CLI Commands
```bash
# Run happy-path incremental ETL + all 12 failure scenario demonstrations
python3 run_demo.py --all-scenarios

# Run normal incremental ETL pipeline only
python3 run_demo.py --etl-only

# Query upstream lineage for a table
python3 run_demo.py --lineage-upstream fact_orders

# Query downstream lineage for a source
python3 run_demo.py --lineage-downstream source_orders

# Run test suite
bash scripts/run_tests.sh
```

## 2. API Server
To launch the FastAPI REST server:
```bash
.venv/bin/uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```
""",

        "12_OPERATIONS_RUNBOOK.md": """# 12 Operations Runbook

## 1. Daily Operations Checklist
1. **Health Check**: Run `curl http://localhost:8000/health` or `python3 run_demo.py --etl-only`.
2. **Review Incidents**: Inspect `data/control_plane.db` table `incident` for status `ESCALATED` or `AWAITING_APPROVAL`.
3. **Approval Queue**: Approve pending incidents via API `POST /incidents/{incident_id}/approve`.
4. **Audit Validation**: Check table `audit_event` for transition records.
""",

        "13_MONITORING_AND_ALERTING.md": """# 13 Monitoring and Alerting

## 1. Observability Metrics
- `total_runs`: Total pipeline executions
- `successful_runs`: Count of successful runs
- `total_incidents`: Count of detected failure incidents
- `healed_incidents`: Incidents resolved via auto-healing
- `escalated_incidents`: Incidents escalated for manual review
- `auto_heal_rate_percent`: Percentage of incidents auto-healed
""",

        "14_TROUBLESHOOTING_GUIDE.md": """# 14 Troubleshooting Guide

## Common Symptoms & Actions

| Symptom | Cause | Resolution |
|---|---|---|
| Watermark does not advance | Extraction returned 0 records or run failed | Verify source `updated_at` records exist and check `failure_event` table |
| Duplicate rows in target | Missing primary key index | `IncrementalLoader` deduplicates rows; check quarantine table |
| Incident stuck in `AWAITING_APPROVAL` | High-risk runbook requires sign-off | Call `POST /incidents/{incident_id}/approve` |
| Lineage graph missing nodes | Unregistered lineage source | Add missing nodes/edges in `config/lineage_sources.yaml` |
""",

        "15_TESTING_GUIDE.md": """# 15 Testing Guide

## 1. Test Suite Structure
- `tests/unit/`: Unit tests for watermarking, BFS lineage, classification, state machine, and risk rules.
- `tests/integration/`: Integration tests for ETL pipeline, incident coordinator, and FastAPI endpoints.
- `tests/failure_scenarios/`: End-to-end tests for all 12 failure scenarios.

## 2. Execution Command
```bash
bash scripts/run_tests.sh
```
""",

        "16_SECURITY_GOVERNANCE_AND_AUDIT.md": """# 16 Security, Governance, and Audit

## 1. Security Architecture
- **No Hardcoded Credentials**: Loaded via `.env` / environment variables.
- **SQL Parameterization & Allowlist**: All queries use parameterized parameters and SQL command allowlisting.
- **PII Masking**: Automatic regex masking of sensitive data in logs.
- **Approval Gates**: High-risk runbooks require manual approval.
""",

        "17_DEPLOYMENT_AND_ROLLBACK.md": """# 17 Deployment and Rollback Guide

## 1. Deployment Steps
1. Checkout code release branch in target environment.
2. Run database migrations: `python3 scripts/seed_demo_data.py`.
3. Start REST API or cron ETL runner.

## 2. Rollback Procedure
If a deployment fails, `RollbackHandler` reverses applied changes and resets watermark states to previous valid checkpoints.
""",

        "18_DEVELOPER_EXTENSION_GUIDE.md": """# 18 Developer Extension Guide

## 1. Adding a New Failure Signature Rule
1. Open `config/healing_rules.yaml`.
2. Add a new rule entry with `rule_id`, `error_code_pattern`, `error_message_pattern`, `classification`, `confidence`, and `runbook_id`.
3. Add corresponding unit test in `tests/unit/test_signature_classifier.py`.

## 2. Adding a New Runbook
1. Implement the runbook handler method in `src/healing/runbook_registry.py`.
2. Map rule in `config/healing_rules.yaml`.
3. Add unit test in `tests/unit/test_runbooks.py`.
""",

        "19_SUPPORT_HANDOVER_CHECKLIST.md": """# 19 Support Handover Checklist

- [x] Repository pushed to public GitHub.
- [x] Bootstrap script verified.
- [x] Test suite passing 100%.
- [x] Console demo script verified.
- [x] Control plane schema DDL documented.
- [x] Operations runbook provided.
""",

        "20_DEMO_SCRIPT.md": """# 20 Presenter Demonstration Script

## Step-by-Step Demonstration Walkthrough

1. **Environment Setup**:
   ```bash
   bash scripts/bootstrap.sh
   ```

2. **Execute Full Demo**:
   ```bash
   python3 run_demo.py --all-scenarios
   ```

3. **Query BFS Upstream Lineage**:
   ```bash
   python3 run_demo.py --lineage-upstream fact_orders
   ```

4. **Query BFS Downstream Lineage & Blast Radius**:
   ```bash
   python3 run_demo.py --lineage-downstream source_orders
   ```

5. **Run Test Suite**:
   ```bash
   bash scripts/run_tests.sh
   ```
""",

        "21_FAQ_AND_GLOSSARY.md": """# 21 FAQ and Glossary

## Glossary
- **Watermark**: The timestamp tracking the high-watermark point of processed data.
- **BFS (Breadth-First Search)**: Graph traversal algorithm that visits nodes level by level.
- **Blast Radius**: The set of all downstream assets impacted by an upstream node failure.
- **Idempotency Key**: Unique token ensuring an operation produces the same result if executed multiple times.
"""
    }

    for fname, content in docs.items():
        fpath = os.path.join(kt_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {fpath}")

    # Generate extra diagrams
    seq_inc = """sequenceDiagram
    autonumber
    participant Source
    participant Extractor
    participant Loader
    participant Target
    participant Watermark

    Extractor->>Watermark: Read last_watermark
    Watermark-->>Extractor: watermark timestamp
    Extractor->>Source: Query incremental batch
    Source-->>Extractor: Dataframe batch
    Extractor->>Loader: Deduplicate & stage
    Loader->>Target: UPSERT records
    Loader->>Watermark: Commit new watermark
"""
    with open(os.path.join(diagrams_dir, "incremental_etl_sequence.mmd"), "w", encoding="utf-8") as f:
        f.write(seq_inc)

    seq_heal = """sequenceDiagram
    autonumber
    participant Pipeline
    participant Detector
    participant Classifier
    participant BFSLineage
    participant RiskEngine
    participant Executor
    participant Validator

    Pipeline->>Detector: Exception
    Detector->>Classifier: FailureEvent
    Classifier->>BFSLineage: Upstream RCA search
    BFSLineage-->>Classifier: Root Cause Node
    Classifier->>RiskEngine: Check risk policy
    RiskEngine-->>Executor: Risk approved
    Executor->>Validator: Runbook remediation
    Validator-->>Pipeline: Recovered
"""
    with open(os.path.join(diagrams_dir, "auto_healing_sequence.mmd"), "w", encoding="utf-8") as f:
        f.write(seq_heal)

    # Generate sample json / csv examples
    sample_evt = {
        "event_id": "evt_sample_001",
        "run_id": "run_sample_001",
        "error_code": "TIMEOUT",
        "error_message": "Database query timed out waiting for connection socket",
        "job_name": "pipe_orders_incremental",
        "correlation_id": "corr_sample_001"
    }
    with open(os.path.join(examples_dir, "sample_failure_event.json"), "w", encoding="utf-8") as f:
        json.dump(sample_evt, f, indent=2)

    sample_appr = {
        "approval_id": "appr_sample_001",
        "incident_id": "inc_sample_001",
        "runbook_id": "RB-RESET-CHK-002",
        "risk_level": "HIGH",
        "status": "PENDING"
    }
    with open(os.path.join(examples_dir, "sample_approval_request.json"), "w", encoding="utf-8") as f:
        json.dump(sample_appr, f, indent=2)

    sample_csv = "Node ID,Name,Type,Depth,Path\npipe_orders_incremental,Incremental Orders Loader,pipeline,1,source_orders -> pipe_orders_incremental\nfact_orders,Fact Orders Table,table,2,source_orders -> pipe_orders_incremental -> fact_orders\n"
    with open(os.path.join(examples_dir, "sample_lineage_report.csv"), "w", encoding="utf-8") as f:
        f.write(sample_csv)

    print("All Knowledge Transfer documents, diagrams, and examples generated successfully.")

if __name__ == "__main__":
    generate()
