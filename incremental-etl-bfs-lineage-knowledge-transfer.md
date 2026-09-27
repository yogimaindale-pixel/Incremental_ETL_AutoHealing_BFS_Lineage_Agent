---
name: incremental-etl-bfs-lineage-knowledge-transfer
description: Analyze an Incremental ETL Auto-Healing and BFS Data Lineage project and generate a complete beginner-friendly knowledge-transfer package covering project purpose, architecture, repository, setup, execution, operations, troubleshooting, rule configuration, runbooks, lineage traversal, security, testing, deployment, maintenance, demonstrations, and handover. Use when a junior engineer, support analyst, developer, tester, architect, or owner needs to understand and operate the entire project step by step.
version: 1.0.0
---

# Project Knowledge Transfer Skill

## 1. Objective
Create an accurate, end-to-end knowledge-transfer package for the Incremental ETL Auto-Healing and BFS Data Lineage project. The output must enable a new engineer to:

- understand the business and technical problem
- explain the architecture
- set up the project
- run the happy path and failure demonstrations
- inspect incremental loads and watermarks
- understand BFS lineage and impact analysis
- operate and monitor the agent
- approve or reject controlled remediation
- troubleshoot failures safely
- add a new pipeline, lineage source, failure rule, and runbook
- run tests and interpret results
- deploy, rollback, and maintain the solution
- follow security, audit, data-privacy, and governance requirements

Do not create generic documentation from assumptions. Derive content from the actual repository and clearly label any gaps or recommendations.

## 2. Mandatory Analysis Procedure
Before writing documentation:

1. Read every top-level file and directory.
2. Inspect application entry points and runtime commands.
3. Inspect configuration files and schemas.
4. Trace the complete code path for:
   - normal incremental load
   - failure detection
   - classification
   - BFS lineage traversal
   - root-cause identification
   - risk decision
   - approval
   - remediation
   - validation
   - rollback or escalation
5. Inspect tests to confirm intended behavior.
6. Run the documented setup, tests, and demo commands when the environment permits.
7. Capture actual outputs without secrets.
8. Identify inconsistencies between code and existing documentation.
9. Update documentation to match code, not the reverse, unless fixing an obvious defect is required.
10. Record unverified instructions as `Not verified`.

## 3. Required KT Deliverables
Create a `knowledge-transfer/` folder containing:

```text
knowledge-transfer/
  00_KT_INDEX.md
  01_PROJECT_OVERVIEW.md
  02_BUSINESS_PROBLEM_AND_VALUE.md
  03_ARCHITECTURE_AND_COMPONENTS.md
  04_REPOSITORY_WALKTHROUGH.md
  05_DATA_MODEL_AND_CONTROL_TABLES.md
  06_INCREMENTAL_ETL_FLOW.md
  07_BFS_LINEAGE_AND_IMPACT_ANALYSIS.md
  08_FAILURE_DETECTION_AND_DIAGNOSIS.md
  09_HEALING_RULES_AND_RUNBOOKS.md
  10_SETUP_AND_CONFIGURATION.md
  11_HOW_TO_RUN.md
  12_OPERATIONS_RUNBOOK.md
  13_MONITORING_AND_ALERTING.md
  14_TROUBLESHOOTING_GUIDE.md
  15_TESTING_GUIDE.md
  16_SECURITY_GOVERNANCE_AND_AUDIT.md
  17_DEPLOYMENT_AND_ROLLBACK.md
  18_DEVELOPER_EXTENSION_GUIDE.md
  19_SUPPORT_HANDOVER_CHECKLIST.md
  20_DEMO_SCRIPT.md
  21_FAQ_AND_GLOSSARY.md
  22_KNOWN_LIMITATIONS_AND_ROADMAP.md
  diagrams/
    architecture.mmd
    incremental_etl_sequence.mmd
    auto_healing_sequence.mmd
    bfs_lineage_flow.mmd
    state_machine.mmd
  examples/
    sample_failure_event.json
    sample_incident_report.md
    sample_lineage_report.csv
    sample_approval_request.json
```

If the project already has similar documents, improve and link them rather than duplicating inconsistent content.

## 4. Documentation Style
- Write for a junior engineer first, then add advanced notes.
- Explain every acronym on first use.
- Use meaningful paragraphs, not one word per line.
- Include exact file paths, function/class names, configuration keys, commands, inputs, and outputs.
- Use numbered procedures for setup and operations.
- Use Mermaid source for diagrams.
- Include expected output and common failure output for commands.
- Mark environment-specific values with placeholders such as `<DB_HOST>`.
- Never include credentials, tokens, customer data, or internal secrets.
- Distinguish `Implemented`, `Configured`, `Optional`, and `Recommended` features.

## 5. Content Requirements by Deliverable

### 00_KT_INDEX.md
Include:
- learning path by role: junior developer, support engineer, tester, architect, product owner
- recommended reading order
- document map
- quick links to setup, run, operations, troubleshooting, and demo
- KT completion checklist

### 01_PROJECT_OVERVIEW.md
Explain:
- one-paragraph project description
- goals and non-goals
- supported workflows
- deterministic-agent principle
- major inputs and outputs
- expected users
- boundary between automation and human approval

### 02_BUSINESS_PROBLEM_AND_VALUE.md
Cover:
- recurring ETL failure problem
- manual investigation and dependency discovery
- incremental-load risks
- downstream blast-radius problem
- proposed operational value
- measurable KPIs as definitions only, unless actual values exist

KPIs may include:
- detection-to-classification time
- mean time to recovery
- percentage auto-healed
- validation pass rate
- repeat-incident rate
- manual escalation rate
- lineage coverage
- false remediation count

### 03_ARCHITECTURE_AND_COMPONENTS.md
Document:
- context, container, and component views
- control plane versus data plane
- event, classifier, lineage, diagnosis, policy, remediation, validation, audit, API, and dashboard components
- interfaces and data contracts
- state persistence
- external dependencies
- failure boundaries

### 04_REPOSITORY_WALKTHROUGH.md
For every major folder and important file explain:
- purpose
- key classes/functions
- who changes it
- runtime usage
- related tests

Include a request-to-code map such as: “To change retry policy, start with `config/healing_rules.yaml`, then review...”

### 05_DATA_MODEL_AND_CONTROL_TABLES.md
For each table/model explain:
- purpose
- primary and foreign keys
- significant columns
- lifecycle
- sample sanitized row
- retention and audit considerations

Include lineage node and edge examples.

### 06_INCREMENTAL_ETL_FLOW.md
Explain step by step:
- previous watermark
- fixed upper bound
- optional lookback
- extraction predicate
- staging
- schema checks
- deduplication
- merge/upsert
- reconciliation
- watermark commit
- retry and replay
- late-arriving data
- idempotency

Show one worked example with sample timestamps and rows from seeded data.

### 07_BFS_LINEAGE_AND_IMPACT_ANALYSIS.md
Explain:
- graph concepts in simple language
- nodes, edges, direction, and environment
- why BFS is used
- queue, visited set, depth, deterministic ordering, and path reconstruction
- upstream RCA traversal
- downstream blast-radius traversal
- shortest dependency path
- cycle handling
- maximum depth
- complexity at a high level
- how lineage metadata is loaded and refreshed
- how to run lineage API/CLI examples
- how to interpret reports

Include pseudocode matching the actual implementation.

### 08_FAILURE_DETECTION_AND_DIAGNOSIS.md
Explain:
- event format
- normalization
- failure signatures
- rule precedence
- conflict handling
- evidence collection
- root-cause candidate ordering
- conditions that force manual review

Trace at least three actual demo failures.

### 09_HEALING_RULES_AND_RUNBOOKS.md
For every configured rule/runbook document:
- ID and version
- triggering conditions
- risk level
- supported environments
- prerequisites
- prechecks
- action
- timeout and retry limit
- success and validation criteria
- rollback
- escalation owner/route placeholder
- example incident

Include a matrix of failure category to allowed action.

### 10_SETUP_AND_CONFIGURATION.md
Provide exact procedures for:
- prerequisites
- repository checkout or folder access
- virtual environment
- dependency installation
- environment file creation
- local database initialization
- sample data seeding
- configuration validation
- Docker Compose option if available
- troubleshooting setup errors

### 11_HOW_TO_RUN.md
Include:
- normal ETL run
- full local demo
- one failure scenario
- API server
- dashboard
- test suite
- reset command
- expected output locations
- clean shutdown

### 12_OPERATIONS_RUNBOOK.md
Cover daily operations:
- start-of-day checks
- pipeline status review
- incident review
- approval queue
- watermark checks
- audit validation
- replay method
- escalation method
- end-of-day checks
- evidence retention

Include severity and responsibility placeholders without inventing organizational assignments.

### 13_MONITORING_AND_ALERTING.md
Document available metrics and logs:
- health
- pipeline state
- latency
- failure category
- remediation attempts
- validation result
- lineage refresh status
- approval age
- circuit breaker

Show log search examples based on the actual format.

### 14_TROUBLESHOOTING_GUIDE.md
Use symptom → checks → likely cause → safe action → escalation format for:
- no new records loaded
- duplicate target records
- watermark does not move
- watermark moves incorrectly
- missing file
- schema drift
- permission failure
- BFS returns no path
- unexpected lineage cycle
- rule does not match
- multiple rules match
- remediation repeatedly fails
- dashboard/API unavailable
- audit record missing

Never advise destructive fixes without backup, approval, and validation.

### 15_TESTING_GUIDE.md
Explain:
- test layers
- test data
- commands
- how to run one test
- how to run all tests
- expected reports
- how to add tests for a new rule or connector
- failure-injection scenarios
- release quality gate

Report actual pass/fail results only when verified.

### 16_SECURITY_GOVERNANCE_AND_AUDIT.md
Explain:
- trust boundaries
- least privilege
- secret management
- data masking
- parameterized SQL
- command allow-list
- role separation
- approval model
- audit event contents
- log redaction
- production kill switch
- retention placeholders
- secure incident evidence handling

### 17_DEPLOYMENT_AND_ROLLBACK.md
Document actual supported methods. Cover:
- environment configuration
- build/package
- database migration
- deployment
- smoke test
- health check
- canary or controlled rollout recommendation
- rollback of application and schema
- post-rollback verification

Do not claim cloud deployment is implemented if only local deployment exists.

### 18_DEVELOPER_EXTENSION_GUIDE.md
Step-by-step tutorials for:
- adding a new source/target adapter
- onboarding a new pipeline
- adding a lineage node or edge parser
- adding a new failure rule
- adding a new allow-listed runbook
- adding validation
- adding dashboard fields
- adding API endpoints
- maintaining backward compatibility

Include required tests and documentation updates for each extension.

### 19_SUPPORT_HANDOVER_CHECKLIST.md
Include sign-off items for:
- access
- setup
- operations
- alert ownership
- approval ownership
- escalation contacts as placeholders
- runbook dry run
- backup and recovery
- test evidence
- known risks
- documentation review

### 20_DEMO_SCRIPT.md
Create a presenter-ready demonstration:
1. explain the problem
2. show repository and architecture
3. run successful incremental load
4. inject supported failure
5. show classification
6. show upstream BFS path
7. show downstream impact
8. show policy decision
9. approve if required
10. run remediation
11. show validation and watermark
12. show incident report and audit trail
13. inject unsupported failure and show safe escalation

Include presenter narration and expected visible result.

### 21_FAQ_AND_GLOSSARY.md
Include terms such as:
- ETL, ELT, CDC, watermark, checkpoint, idempotency
- lineage, node, edge, BFS, upstream, downstream, blast radius
- runbook, remediation, rollback, circuit breaker
- data quality, reconciliation, quarantine
- deterministic agent, human in the loop, audit evidence

### 22_KNOWN_LIMITATIONS_AND_ROADMAP.md
Separate:
- confirmed limitations from code inspection
- environment dependencies
- missing connectors
- unsupported failure categories
- operational risks
- prioritized recommendations

Do not invent delivery dates.

## 6. Required Diagrams
Generate Mermaid definitions for:

1. System architecture.
2. Successful incremental ETL sequence.
3. Failure-to-healing sequence with approval branch.
4. BFS upstream and downstream traversal.
5. Incident state machine.

Ensure diagrams use actual component names from the code.

## 7. Hands-On Exercises
Add exercises to the relevant documents:

### Beginner
- run the sample pipeline
- inspect source, target, and watermark
- query one upstream and one downstream lineage path
- read an incident evidence bundle

### Intermediate
- create a new deterministic rule
- add a data-quality check
- add a lineage edge
- test an approval-required remediation

### Advanced
- onboard a new adapter
- design a new reversible runbook
- add rollback and contract tests
- assess blast radius before a schema change

Each exercise must include objective, prerequisites, steps, expected result, and cleanup.

## 8. KT Quality Gates
The KT package is complete only when:

- all required files exist or are mapped to better existing documents
- all commands correspond to repository scripts or are labeled recommendations
- all important configuration keys are explained
- the happy path and at least three failure paths are traced end to end
- BFS logic, cycle handling, and report interpretation are covered
- every active healing rule and runbook is documented
- security and approval boundaries are explicit
- actual tests and demo have been attempted
- unverified steps are clearly marked
- no secret or sensitive data is present
- a junior engineer can follow setup and demo without hidden tribal knowledge

## 9. Final KT Summary
After generating the package, report:

1. documents created or updated
2. code paths analyzed
3. commands executed
4. tests and demos verified
5. documentation gaps or code/doc inconsistencies
6. unresolved dependencies
7. suggested KT session agenda
8. handover readiness status: READY, READY WITH GAPS, or NOT READY, with evidence
