---
name: incremental-etl-autohealing-bfs-lineage
description: Build, test, operate, and document a deterministic Incremental ETL Auto-Healing Agent combined with a BFS Data Lineage and impact-analysis engine. Use when creating a production-style Python data engineering project that detects pipeline failures, classifies known failure signatures, finds upstream/downstream dependencies through breadth-first graph traversal, executes allow-listed recovery actions with safety gates, validates recovery, preserves audit evidence, and escalates unsupported cases.
version: 1.0.0
---

# Incremental ETL Auto-Healing and BFS Data Lineage Skill

## 1. Mission
Create a complete, runnable, deterministic data engineering solution that:

1. Executes incremental ETL using watermark or CDC-style metadata.
2. Monitors every pipeline run and step.
3. Detects and classifies supported failure conditions using explicit rules.
4. Builds table, file, job, column, report, and API lineage as a directed graph.
5. Uses breadth-first search (BFS) for upstream root-cause search and downstream impact analysis.
6. Selects only allow-listed remediation runbooks.
7. applies human approval gates according to risk policy.
8. Executes safe remediation, validates data and control state, and retries idempotently.
9. Escalates uncertain, unsupported, or high-risk cases without guessing.
10. Produces complete operational evidence, audit logs, reports, tests, and documentation.

This is primarily a deterministic agent. Do not use an LLM for execution decisions. An optional LLM may explain already-produced structured evidence, but it must never choose or execute a remediation.

## 2. Mandatory Working Method
When this skill is invoked:

1. Inspect the entire project folder before creating or changing files.
2. Read requirements, README files, existing code, schemas, configuration, tests, logs, sample data, and deployment files.
3. Create an inventory of existing assets and identify gaps.
4. Preserve working code and interfaces unless a requirement demands change.
5. Build the smallest complete vertical slice first.
6. Use configuration-driven rules rather than hardcoded environment logic.
7. Generate sanitized sample data when real data is unavailable.
8. Run tests and demonstration scenarios locally.
9. Record assumptions and unresolved dependencies.
10. Never claim that code is complete unless the documented acceptance checks pass.

## 3. Required Repository Structure
Create or align the project to the following structure:

```text
project-root/
  README.md
  pyproject.toml
  requirements.txt
  .env.example
  .gitignore
  docker-compose.yml
  Makefile
  run_demo.py
  config/
    environments.yaml
    pipelines.yaml
    healing_rules.yaml
    risk_policy.yaml
    data_quality_rules.yaml
    lineage_sources.yaml
  data/
    input/
    output/
    quarantine/
    checkpoints/
    samples/
  src/
    common/
      config.py
      logging.py
      models.py
      security.py
      exceptions.py
    ingestion/
      extractor.py
      watermark_manager.py
      incremental_loader.py
    observability/
      event_collector.py
      failure_detector.py
      metrics.py
    diagnosis/
      signature_classifier.py
      evidence_collector.py
      root_cause_engine.py
    lineage/
      graph_model.py
      metadata_parser.py
      graph_builder.py
      bfs_traversal.py
      impact_analyzer.py
    healing/
      rule_engine.py
      risk_engine.py
      runbook_registry.py
      remediation_executor.py
      rollback.py
    validation/
      technical_validator.py
      reconciliation.py
      data_quality_validator.py
    orchestration/
      state_machine.py
      coordinator.py
    api/
      app.py
      schemas.py
    dashboard/
      streamlit_app.py
    reporting/
      incident_report.py
      lineage_report.py
  sql/
    control_schema.sql
    sample_source.sql
    sample_target.sql
  tests/
    unit/
    integration/
    contract/
    failure_scenarios/
  docs/
    architecture.md
    deterministic-design.md
    lineage-model.md
    runbooks.md
    security.md
    operations.md
    test-strategy.md
    demo-guide.md
    assumptions.md
  scripts/
    bootstrap.sh
    run_tests.sh
    seed_demo_data.py
    reset_demo.py
  artifacts/
```

## 4. Reference Technology Stack
Default implementation unless the existing project specifies otherwise:

- Python 3.11+
- FastAPI for health, incident, lineage, and manual-approval endpoints
- SQLite for local demonstration; adapter interfaces for PostgreSQL, Oracle, BigQuery, or cloud warehouses
- NetworkX or an internal adjacency-list implementation for the lineage graph
- pandas and SQLAlchemy for sample ETL and reconciliation
- Pydantic for typed contracts
- YAML for pipeline and healing configuration
- pytest for unit, integration, and scenario testing
- Streamlit for a local operational dashboard
- structured JSON logging
- Docker Compose for reproducible local execution

Do not require any external API for the default demo.

## 5. Deterministic Agent Architecture
Implement the following logical components.

### 5.1 Event and Monitoring Agent
Responsibilities:
- read pipeline-run and step-run events
- normalize error code, error text, source, target, job, attempt, timestamps, and correlation ID
- detect failed, stalled, late, skipped, or data-quality-breached states
- emit one normalized `FailureEvent`

It must not remediate.

### 5.2 Failure Classification Agent
Classify using ordered rules from `healing_rules.yaml`.

Required initial categories:
- transient connection or timeout
- source file late or missing
- duplicate business key
- watermark ahead of source
- stale checkpoint
- target partition missing
- schema additive drift
- schema breaking drift
- data-quality threshold breach
- insufficient permission or credential error
- resource exhaustion
- unknown failure

Every classification must include:
- rule ID and rule version
- matched conditions
- confidence derived from rule completeness, not model probability
- evidence references
- classification timestamp

If zero or multiple conflicting high-priority rules match, classify as `MANUAL_REVIEW_REQUIRED`.

### 5.3 BFS Lineage Agent
Maintain a directed property graph.

Required node types:
- system
- database
- schema
- table
- column
- file
- topic
- pipeline
- job
- task
- transformation
- API
- report
- dashboard

Required edge types:
- READS_FROM
- WRITES_TO
- TRANSFORMS
- TRIGGERS
- DEPENDS_ON
- PRODUCES
- CONSUMES
- DERIVES_FROM

Each node and edge must contain:
- stable ID
- display name
- type
- environment
- source adapter
- last observed timestamp
- metadata version
- active flag

BFS requirements:
- upstream traversal for root-cause candidates
- downstream traversal for blast-radius analysis
- configurable maximum depth
- cycle-safe visited set
- deterministic ordering of neighbors
- path reconstruction
- support for filters by environment, node type, and active status
- return shortest dependency paths in edge count
- stop conditions for source boundary, known failed node, or maximum depth

Example APIs:

```python
def bfs_upstream(graph, start_id, max_depth=10, filters=None): ...
def bfs_downstream(graph, start_id, max_depth=10, filters=None): ...
def shortest_dependency_path(graph, source_id, target_id): ...
```

### 5.4 Root Cause Agent
Use the failure event, run history, and upstream BFS result.

Deterministic scoring order:
1. exact failed step or dataset
2. failed upstream node in the same correlation window
3. freshness or row-count violation at the nearest upstream level
4. recently changed schema or metadata version
5. known failure signature on the traversed path

Return ranked candidates only when ordering is explainable. Do not invent a root cause. If evidence is insufficient, return `UNDETERMINED`.

### 5.5 Risk and Policy Agent
Map each candidate remediation to:
- read-only
- reversible low risk
- reversible medium risk
- destructive or high risk

Default policy:
- read-only diagnosis is automatic
- low-risk remediation may run automatically in local/dev
- medium-risk remediation requires approval in test/prod
- destructive actions are disabled by default
- production checkpoint reset, delete, truncate, broad update, or DDL change always requires approval
- credential and permission failures are escalation-only
- unknown failures are escalation-only

### 5.6 Remediation Agent
Execute only registered runbooks. Initial allow-listed runbooks:

- retry failed task with capped exponential backoff
- wait and recheck late file
- resume from last valid checkpoint
- reset a stale demo checkpoint after approval
- create a missing demo partition after validation and approval
- quarantine malformed or duplicate rows
- regenerate an additive target schema in non-production after approval
- reduce safe batch size on resource exhaustion
- replay only the impacted incremental window
- skip remediation and escalate

Each runbook must define:
- unique ID and version
- supported failure categories
- prerequisites
- prechecks
- command or callable
- timeout
- maximum attempts
- idempotency key
- success criteria
- postchecks
- rollback procedure
- allowed environments
- approval requirement
- owner

Never execute arbitrary shell, SQL, or code generated from an error message.

### 5.7 Validation Agent
A remediation is successful only after all applicable checks pass:
- pipeline step completed
- target reachable
- expected partition or object exists
- watermark moved correctly
- source-to-target count within configured tolerance
- primary/business key uniqueness
- null and schema checks
- checksum or aggregate reconciliation
- no duplicate processed batch ID
- downstream impacted assets are in a valid or intentionally paused state

If validation fails, rollback when safe and escalate.

### 5.8 Audit and Reporting Agent
Create immutable append-only records for:
- incoming event
- classification
- lineage paths
- root-cause candidates
- selected rule and policy decision
- approval request and response
- remediation attempts
- validation results
- rollback
- final state

Produce:
- JSON incident evidence bundle
- Markdown incident summary
- CSV lineage path report
- CSV downstream impact report
- dashboard-ready metrics

## 6. State Machine
Implement explicit states:

```text
DETECTED
NORMALIZED
CLASSIFIED
EVIDENCE_COLLECTED
LINEAGE_TRAVERSED
ROOT_CAUSE_IDENTIFIED
REMEDIATION_SELECTED
AWAITING_APPROVAL
REMEDIATING
VALIDATING
RECOVERED
ROLLED_BACK
ESCALATED
CLOSED
```

Reject invalid transitions. Persist state changes with correlation ID, actor, timestamp, and reason.

## 7. Control-Plane Data Model
Create tables or equivalent stores for:

- `pipeline_definition`
- `pipeline_run`
- `pipeline_step_run`
- `watermark_state`
- `failure_event`
- `failure_rule`
- `lineage_node`
- `lineage_edge`
- `incident`
- `root_cause_candidate`
- `remediation_run`
- `approval_request`
- `validation_result`
- `audit_event`

Use unique constraints for pipeline run IDs, batch IDs, event IDs, and idempotency keys.

## 8. Incremental ETL Requirements
Implement at least one working incremental demonstration:

1. Source table contains `updated_at` and stable business key.
2. Watermark is read before extraction.
3. Extract records where `updated_at > previous_watermark` and `updated_at <= run_upper_bound`.
4. Stage data before target merge.
5. Validate schema and required columns.
6. Deduplicate by business key and latest timestamp.
7. MERGE or UPSERT into target.
8. Commit the watermark only after target validation succeeds.
9. On failure, leave the prior watermark unchanged.
10. Make reruns idempotent using batch ID and merge keys.

Include late-arriving data handling with a configurable lookback window.

## 9. Configuration Contracts
Example healing rule:

```yaml
rules:
  - id: ETL-TRANSIENT-001
    version: 1
    priority: 10
    match:
      error_codes: [TIMEOUT, CONNECTION_RESET]
      message_regex: '(?i)(timeout|connection reset)'
    classification: TRANSIENT_CONNECTION
    runbook_id: RB-RETRY-001
    allowed_environments: [local, dev, test, prod]
    approval:
      local: false
      dev: false
      test: false
      prod: false
```

Example BFS policy:

```yaml
lineage:
  upstream_max_depth: 10
  downstream_max_depth: 15
  deterministic_sort: true
  include_inactive: false
  stop_at_system_boundary: false
```

Validate all YAML at startup and fail fast on invalid or duplicate rule IDs.

## 10. API Requirements
Create endpoints equivalent to:

- `GET /health`
- `POST /events/failures`
- `GET /incidents/{incident_id}`
- `POST /incidents/{incident_id}/approve`
- `POST /incidents/{incident_id}/reject`
- `GET /lineage/{node_id}/upstream`
- `GET /lineage/{node_id}/downstream`
- `GET /lineage/path?source_id=&target_id=`
- `GET /metrics`

Use typed request/response models. Do not expose credentials, raw sensitive values, or internal stack traces.

## 11. Dashboard Requirements
Show:
- pipeline health by environment
- active incidents by state and severity
- auto-healed versus escalated incidents
- mean detection-to-recovery time from demo records
- retry and rollback counts
- root-cause node and evidence
- upstream BFS path
- downstream impact graph or table
- manual approval queue
- watermark state
- audit timeline

The dashboard is evidence-based and read-only except for explicit approve/reject actions.

## 12. Safety, Security, and Governance
Mandatory controls:

- no credentials in source, logs, samples, or configuration
- `.env.example` contains placeholders only
- least-privilege adapters
- read-only access for lineage and diagnosis wherever possible
- parameterized SQL
- command and SQL allow-lists
- masking of account, customer, employee, and other sensitive identifiers
- correlation IDs for all actions
- tamper-evident or append-only audit storage
- separation of diagnosis, approval, execution, and validation
- environment-aware controls
- circuit breaker when repeated healing fails
- maximum retry count and runtime
- kill switch to disable automated remediation
- no autonomous destructive production action

## 13. Required Demonstration Scenarios
Create deterministic seeded scenarios for:

1. Transient connection failure, auto-retry succeeds.
2. Late source file, bounded wait then success.
3. Duplicate rows, quarantine then successful load.
4. Stale watermark, approval then checkpoint correction and replay.
5. Missing target partition, approval then creation and retry.
6. Additive schema drift in dev, validated adjustment then retry.
7. Breaking schema drift, no auto-heal and escalation.
8. Permission error, no auto-heal and escalation.
9. Data-quality failure, quarantine or escalation according to threshold.
10. Downstream impact analysis from a changed column or failed job using BFS.
11. Circular lineage edge proving cycle-safe traversal.
12. Failed remediation proving rollback and circuit-breaker behavior.

## 14. Testing Requirements
Minimum test groups:

### Unit
- watermark boundaries
- deduplication
- merge idempotency
- rule priority and conflict handling
- state transition validation
- BFS upstream and downstream traversal
- cycle handling
- max-depth behavior
- deterministic neighbor ordering
- shortest-path reconstruction
- policy decisions
- redaction

### Integration
- source to target incremental load
- event to incident flow
- incident to remediation flow
- remediation to validation flow
- approval gate
- rollback
- API contracts

### Scenario and Chaos
- all twelve required scenarios
- repeated same event
- event delivered out of order
- control database unavailable
- malformed configuration
- lineage node missing
- rule references unknown runbook

All tests must run from one documented command.

## 15. Acceptance Criteria
The build is accepted only when:

- a clean local setup command works
- the sample incremental ETL succeeds
- at least six known failure types follow deterministic rules
- unsupported failure is escalated safely
- BFS upstream and downstream reports are generated
- cycles do not cause infinite traversal
- the same batch can be replayed without duplicate target rows
- watermark is unchanged after an unsuccessful run
- approval policy is enforced
- audit evidence exists for every state transition and action
- remediation validation is separate from remediation execution
- tests pass
- README, architecture, runbook, security, operations, and demo documents exist

## 16. Antigravity Build Sequence
Perform these phases without pausing for confirmation:

### Phase 1: Discover
- inspect repository
- summarize assets and gaps in `docs/assumptions.md`
- identify target runtime and available connectors

### Phase 2: Scaffold
- create package structure
- create typed models, config loader, logging, and control schema

### Phase 3: Build Incremental ETL
- source, staging, merge, watermark, reconciliation, idempotency

### Phase 4: Build Lineage
- parsers, graph storage, BFS traversal, path/impact reports

### Phase 5: Build Detection and Diagnosis
- normalized events, rules, evidence, root-cause candidates

### Phase 6: Build Healing
- runbook registry, risk policy, approvals, execution, rollback

### Phase 7: Build Validation
- technical, data-quality, and reconciliation checks

### Phase 8: Expose and Visualize
- API, dashboard, incident and lineage reports

### Phase 9: Test
- unit, integration, scenario, security, and failure-injection tests

### Phase 10: Document and Package
- complete README and documents
- include exact commands
- create demo artifacts
- verify clean setup from scratch

## 17. Definition of Done Output
At completion provide:

1. concise implementation summary
2. created/modified file list
3. architecture and data-flow description
4. exact setup and run commands
5. test command and actual result
6. demonstration scenario results
7. supported and unsupported healing matrix
8. security and governance controls
9. known limitations
10. recommended next increments

Never report fabricated metrics. Use only results created by the local tests and demo.
