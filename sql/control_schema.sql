-- Control Schema for Incremental ETL Auto-Healing & Lineage Agent

CREATE TABLE IF NOT EXISTS pipeline_definition (
    pipeline_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_table TEXT NOT NULL,
    target_table TEXT NOT NULL,
    watermark_column TEXT NOT NULL,
    lookback_minutes INTEGER DEFAULT 60,
    batch_size INTEGER DEFAULT 1000,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pipeline_run (
    run_id TEXT PRIMARY KEY,
    pipeline_id TEXT NOT NULL,
    status TEXT NOT NULL, -- STARTED, SUCCESS, FAILED, REMEDIATING, RECOVERED, ESCALATED
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    records_extracted INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_id) REFERENCES pipeline_definition(pipeline_id)
);

CREATE TABLE IF NOT EXISTS pipeline_step_run (
    step_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    step_name TEXT NOT NULL, -- EXTRACT, STAGE, VALIDATE, MERGE, COMMIT
    status TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    error_code TEXT,
    error_message TEXT,
    FOREIGN KEY (run_id) REFERENCES pipeline_run(run_id)
);

CREATE TABLE IF NOT EXISTS watermark_state (
    pipeline_id TEXT PRIMARY KEY,
    last_watermark TIMESTAMP NOT NULL,
    high_watermark TIMESTAMP,
    batch_id TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_id) REFERENCES pipeline_definition(pipeline_id)
);

CREATE TABLE IF NOT EXISTS failure_event (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    step_id TEXT,
    error_code TEXT NOT NULL,
    error_message TEXT NOT NULL,
    job_name TEXT,
    attempt INTEGER DEFAULT 1,
    correlation_id TEXT NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    normalized_data TEXT -- JSON string
);

CREATE TABLE IF NOT EXISTS incident (
    incident_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    status TEXT NOT NULL, -- DETECTED, CLASSIFIED, AWAITING_APPROVAL, REMEDIATING, RECOVERED, ESCALATED, ROLLED_BACK
    classification TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    root_cause_node_id TEXT,
    selected_runbook_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES failure_event(event_id)
);

CREATE TABLE IF NOT EXISTS approval_request (
    approval_id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    runbook_id TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    environment TEXT NOT NULL,
    status TEXT NOT NULL, -- PENDING, APPROVED, REJECTED
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    responded_by TEXT,
    reason TEXT,
    FOREIGN KEY (incident_id) REFERENCES incident(incident_id)
);

CREATE TABLE IF NOT EXISTS remediation_run (
    remediation_id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    runbook_id TEXT NOT NULL,
    idempotency_key TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL, -- STARTED, SUCCESS, FAILED, ROLLED_BACK
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (incident_id) REFERENCES incident(incident_id)
);

CREATE TABLE IF NOT EXISTS validation_result (
    validation_id TEXT PRIMARY KEY,
    remediation_id TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    step_checks_passed BOOLEAN,
    reconciliation_passed BOOLEAN,
    dq_passed BOOLEAN,
    details TEXT, -- JSON
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (remediation_id) REFERENCES remediation_run(remediation_id)
);

CREATE TABLE IF NOT EXISTS audit_event (
    audit_id TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    state_from TEXT,
    state_to TEXT,
    actor TEXT NOT NULL,
    details TEXT, -- JSON
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lineage_node (
    node_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    environment TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    metadata_version INTEGER DEFAULT 1,
    last_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lineage_edge (
    edge_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    FOREIGN KEY (source_id) REFERENCES lineage_node(node_id),
    FOREIGN KEY (target_id) REFERENCES lineage_node(node_id)
);
