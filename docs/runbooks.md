# Allow-Listed Runbooks Specification

| Runbook ID | Title | Risk Level | Description |
|---|---|---|---|
| `RB-RETRY-001` | Exponential Backoff Retry | LOW | Retries failed task after exponential wait |
| `RB-WAIT-FILE-001` | Late File Wait & Recheck | LOW | Waits for late source file arrival |
| `RB-RESUME-CHK-001` | Resume Checkpoint | LOW | Resumes execution from last valid checkpoint |
| `RB-RESET-CHK-002` | Reset Stale Checkpoint | HIGH | Resets watermark/checkpoint to valid point |
| `RB-CREATE-PART-001` | Create Missing Partition | MEDIUM | Creates missing target partition |
| `RB-QUARANTINE-001` | Quarantine Bad Rows | MEDIUM | Quarantines malformed/duplicate rows |
| `RB-ADD-SCHEMA-001` | Additive Schema DDL | MEDIUM | Adds new column to target table |
| `RB-REDUCE-BATCH-001` | Reduce Batch Size | LOW | Decreases batch size on OOM/resource errors |
| `RB-REPLAY-WINDOW-001` | Replay Window | HIGH | Replays incremental window |
| `RB-ESCALATE-001` | Manual Escalation | HIGH | Skips auto-heal and escalates to human |
