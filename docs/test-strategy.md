# Testing Strategy

## Test Layers
1. **Unit Tests** (`tests/unit/`): Watermark bounds, BFS traversal, classifier matching, state machine transitions, risk policy, runbook execution.
2. **Integration Tests** (`tests/integration/`): Ingestion flow, incident lifecycle, FastAPI endpoints.
3. **Failure Scenario Tests** (`tests/failure_scenarios/`): All 12 demonstration scenarios tested end-to-end.
