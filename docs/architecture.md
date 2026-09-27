# System Architecture

## Architecture Overview
The **Incremental ETL Auto-Healing & BFS Data Lineage Agent** combines incremental data ingestion with deterministic failure classification, graph-based root-cause analysis, risk-policy enforcement, allow-listed runbooks, validation checks, and append-only audit logging.

```
[Source DB] ---> (Extractor) ---> [Staging/Loader] ---> [Target DB]
                       |
                  (Failure)
                       v
               (Event Collector)
                       v
             (Signature Classifier)
                       v
             (BFS Lineage Engine) ---> [Root Cause Analysis]
                       v
             (Risk Policy Engine)
                       v
            (Remediation Executor) ---> [Validation Engine]
                       v
               [Audit Event Log]
```

## Key Components
1. **Ingestion Engine**: Extractor, Watermark Manager, Incremental Loader.
2. **Observability Engine**: Event Collector, Failure Detector, Metrics Calculator.
3. **Diagnosis Engine**: Signature Classifier, Evidence Collector, Root Cause Engine.
4. **Lineage Engine**: Directed Property Graph, Metadata Parser, Graph Builder, BFS Traversal, Impact Analyzer.
5. **Healing Engine**: Rule Engine, Risk Engine, Runbook Registry, Remediation Executor, Rollback Handler.
6. **Validation Engine**: Technical Validator, Reconciliation Engine, Data Quality Validator.
7. **Orchestration**: Incident Coordinator, State Machine.
