# Deterministic Agent Design

## Core Principles
1. **Zero LLM Dependency for Execution**: Remediation choices, graph traversals, and state machine transitions are 100% deterministic code and YAML rules.
2. **Strict Rule Matching**: Signature classification orders rules by explicit priority and regex matching.
3. **Audit Trail**: Every state transition generates an immutable append-only record with correlation ID and actor.
4. **Idempotency**: All runbooks use unique idempotency keys (`idem_{incident_id}_{runbook_id}`).
