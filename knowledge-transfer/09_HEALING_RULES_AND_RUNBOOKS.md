# 09 Healing Rules and Runbooks Catalog

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
