# 03 Architecture and Component Details

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
