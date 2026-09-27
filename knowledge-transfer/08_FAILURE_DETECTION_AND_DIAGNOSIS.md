# 08 Failure Detection and Diagnosis

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
