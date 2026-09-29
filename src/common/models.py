# Import standard datetime module for handling timestamps across models
from datetime import datetime
# Import Enum to create strongly-typed enumerations for states, risk levels, and lineage types
from enum import Enum
# Import typing helpers for type hinting lists, dicts, optional parameters, and arbitrary data
from typing import Dict, List, Optional, Any
# Import Pydantic BaseModel and Field for schema validation, data serialization, and defaults
from pydantic import BaseModel, Field

# Enumeration representing the 14 formal states of an incident lifecycle state machine
class IncidentState(str, Enum):
    # Incident has been detected by monitoring or failure collector
    DETECTED = "DETECTED"
    # Event data has been parsed and normalized into standard internal schema
    NORMALIZED = "NORMALIZED"
    # Signature classifier matched the failure event against known signature rules
    CLASSIFIED = "CLASSIFIED"
    # Evidence collector gathered logs, environment details, and execution parameters
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    # BFS lineage traversal mapped upstream data sources and downstream impact blast radius
    LINEAGE_TRAVERSED = "LINEAGE_TRAVERSED"
    # Root cause engine ranked candidates and identified the most probable root cause node
    ROOT_CAUSE_IDENTIFIED = "ROOT_CAUSE_IDENTIFIED"
    # Automated runbook registry selected a matching remediation strategy
    REMEDIATION_SELECTED = "REMEDIATION_SELECTED"
    # Remediation requires human intervention due to medium/high/destructive risk level
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    # Remediation executor is actively running the selected runbook actions
    REMEDIATING = "REMEDIATING"
    # Post-remediation validation engine is verifying pipeline health, schemas, and metrics
    VALIDATING = "VALIDATING"
    # Incident successfully resolved and target pipeline/data asset fully recovered
    RECOVERED = "RECOVERED"
    # Remediation failed or validation failed, triggering automatic rollback procedure
    ROLLED_BACK = "ROLLED_BACK"
    # Incident escalated to human operator because auto-healing could not resolve it
    ESCALATED = "ESCALATED"
    # Final terminal state indicating incident processing is fully closed
    CLOSED = "CLOSED"

# Enumeration representing safety risk levels assigned to automated runbooks
class RiskLevel(str, Enum):
    # Inspection or query actions that perform no mutations (e.g. read schema, check logs)
    READ_ONLY = "READ_ONLY"
    # Minor low-impact operational changes (e.g. clear temporary cache, restart batch task)
    LOW = "LOW"
    # Moderate impact changes requiring automated validation or approval (e.g. watermark reset)
    MEDIUM = "MEDIUM"
    # Significant operational changes that alter schemas or modify live tables
    HIGH = "HIGH"
    # Potentially destructive changes (e.g. drop table, truncate staging) requiring human approval
    DESTRUCTIVE = "DESTRUCTIVE"

# Enumeration representing the structural classification of nodes in the data lineage graph
class NodeType(str, Enum):
    # Infrastructure system node (e.g. AWS S3, Spark Cluster)
    SYSTEM = "system"
    # Relational or NoSQL database container (e.g. PostgreSQL, SQLite)
    DATABASE = "database"
    # Logical database schema namespace (e.g. public, bronze, silver)
    SCHEMA = "schema"
    # Database table containing structured records
    TABLE = "table"
    # Individual attribute or field within a table
    COLUMN = "column"
    # Physical file asset on storage (e.g. CSV, Parquet, JSON payload)
    FILE = "file"
    # Event stream topic (e.g. Kafka topic)
    TOPIC = "topic"
    # End-to-end data integration pipeline
    PIPELINE = "pipeline"
    # Individual execution job within a pipeline
    JOB = "job"
    # Granular task unit within a job
    TASK = "task"
    # Data transformation step or SQL query execution
    TRANSFORMATION = "transformation"
    # External REST API consumer or microservice interface
    API = "API"
    # Business intelligence report output
    REPORT = "report"
    # Executive interactive visualization dashboard
    DASHBOARD = "dashboard"

# Enumeration representing relationship types between nodes in the lineage graph
class EdgeType(str, Enum):
    # Target node reads input records from source node
    READS_FROM = "READS_FROM"
    # Source node writes output records to target node
    WRITES_TO = "WRITES_TO"
    # Node transforms data structure or content
    TRANSFORMS = "TRANSFORMS"
    # Source node triggers execution of downstream target node
    TRIGGERS = "TRIGGERS"
    # Target node depends on completion of source node
    DEPENDS_ON = "DEPENDS_ON"
    # Process produces output asset
    PRODUCES = "PRODUCES"
    # Process consumes input asset
    CONSUMES = "CONSUMES"
    # Target asset derives its schema or values from source asset
    DERIVES_FROM = "DERIVES_FROM"

# Model representing an individual node entity in the lineage graph
class LineageNode(BaseModel):
    # Unique string identifier for the lineage node
    node_id: str
    # Human-readable descriptive name of the asset or node
    name: str
    # Node classification type from NodeType enumeration
    type: NodeType
    # Deployment environment (e.g. local, staging, production)
    environment: str = "local"
    # Underlying technology adapter (e.g. sqlite, postgres, duckdb)
    source_adapter: str = "sqlite"
    # Timestamp when node state was last verified or observed
    last_observed: datetime = Field(default_factory=datetime.utcnow)
    # Schema version counter for tracking metadata changes
    metadata_version: int = 1
    # Active flag indicating whether node is actively operational
    active: bool = True

# Model representing a directional connection between two lineage nodes
class LineageEdge(BaseModel):
    # Unique string identifier for the edge relationship
    edge_id: str
    # Identifier of the originating source node
    source_id: str
    # Identifier of the destination target node
    target_id: str
    # Relationship type from EdgeType enumeration
    type: EdgeType
    # Active flag indicating whether connection is valid
    active: bool = True

# Model representing a raw failure event captured during pipeline execution
class FailureEvent(BaseModel):
    # Unique string identifier for the failure event
    event_id: str
    # Execution run identifier associated with the failure
    run_id: str
    # Specific step identifier within the pipeline, if applicable
    step_id: Optional[str] = None
    # Categorical error code string (e.g. MISSING_COLUMN, WATERMARK_DRIFT)
    error_code: str
    # Detailed raw error message or exception traceback text
    error_message: str
    # Name of the pipeline job that experienced the error
    job_name: Optional[str] = None
    # Retry attempt counter for the failed task
    attempt: int = 1
    # Correlation tracking identifier linking events across system logs
    correlation_id: str
    # Timestamp when failure occurred in UTC
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    # Flexible dictionary holding normalized context parameters
    normalized_data: Dict[str, Any] = Field(default_factory=dict)

# Model representing the classification output from signature rules engine
class ClassificationResult(BaseModel):
    # Unique identifier of the matching classification rule
    rule_id: str
    # Version counter of the matched rule definition
    rule_version: int
    # Assigned failure classification category string
    classification: str
    # Matched runbook identifier recommended for remediation, if any
    runbook_id: Optional[str] = None
    # Confidence score float ranging from 0.0 (uncertain) to 1.0 (exact match)
    confidence: float
    # List of rule condition strings that successfully evaluated to true
    matched_conditions: List[str]
    # References to logs, line numbers, or metrics supporting classification
    evidence_references: List[str]
    # Timestamp when classification decision was rendered
    classified_at: datetime = Field(default_factory=datetime.utcnow)

# Model representing a root cause candidate evaluated during diagnosis
class RootCauseCandidate(BaseModel):
    # Unique identifier of the suspected root cause node
    node_id: str
    # Human-readable name of the suspected root cause node
    node_name: str
    # Calculated probability score float for root cause likelihood
    score: float
    # Text explanation describing why this candidate was scored
    reason: str

# Model representing an active or historical incident ticket tracked by state machine
class Incident(BaseModel):
    # Unique string identifier for the incident ticket
    incident_id: str
    # Identifier of the originating failure event
    event_id: str
    # Identifier of the affected target pipeline
    pipeline_id: str
    # Trace correlation identifier spanning logs and metrics
    correlation_id: str
    # Current state of the incident from IncidentState enumeration
    status: IncidentState = IncidentState.DETECTED
    # Failure classification category assigned by classifier
    classification: str = "UNKNOWN"
    # Overall classification confidence score float
    confidence_score: float = 0.0
    # Identified root cause node identifier, if resolved
    root_cause_node_id: Optional[str] = None
    # Runbook identifier selected for auto-healing execution
    selected_runbook_id: Optional[str] = None
    # Timestamp when incident was created in UTC
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Timestamp when incident record was last modified
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Model representing an approval request for medium/high risk runbook executions
class ApprovalRequest(BaseModel):
    # Unique identifier for the human approval request
    approval_id: str
    # Associated incident identifier requiring approval
    incident_id: str
    # Runbook identifier submitted for execution approval
    runbook_id: str
    # Safety risk level from RiskLevel enumeration
    risk_level: RiskLevel
    # Environment name (e.g. staging, production)
    environment: str
    # Current status of approval request (PENDING, APPROVED, REJECTED)
    status: str = "PENDING"
    # Timestamp when approval was requested
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    # Timestamp when human operator submitted decision
    responded_at: Optional[datetime] = None
    # Username or system actor who rendered approval decision
    responded_by: Optional[str] = None
    # Reason text provided for approval or rejection
    reason: Optional[str] = None

# Model tracking execution state of an automated remediation runbook
class RemediationRun(BaseModel):
    # Unique string identifier for the remediation execution
    remediation_id: str
    # Associated incident identifier being resolved
    incident_id: str
    # Runbook identifier being executed
    runbook_id: str
    # Idempotency key preventing duplicate concurrent executions
    idempotency_key: str
    # Execution status (STARTED, SUCCESS, FAILED, ROLLED_BACK)
    status: str = "STARTED"
    # Timestamp when remediation started execution
    start_time: datetime = Field(default_factory=datetime.utcnow)
    # Timestamp when remediation completed or failed
    end_time: Optional[datetime] = None
    # Error message text if remediation run encountered a failure
    error_message: Optional[str] = None

# Model representing validation results after remediation execution
class ValidationResultModel(BaseModel):
    # Unique identifier for the validation check run
    validation_id: str
    # Associated remediation run identifier validated
    remediation_id: str
    # Overall Boolean flag indicating if all validation checks passed
    passed: bool
    # Flag indicating whether granular step checks succeeded
    step_checks_passed: bool = True
    # Flag indicating whether data reconciliation checks succeeded
    reconciliation_passed: bool = True
    # Flag indicating whether data quality threshold checks succeeded
    dq_passed: bool = True
    # Detailed dictionary holding metric scores and error text
    details: Dict[str, Any] = Field(default_factory=dict)
    # Timestamp when validation was performed
    checked_at: datetime = Field(default_factory=datetime.utcnow)

# Model representing audit trail log records for compliance and tracking
class AuditEventModel(BaseModel):
    # Unique string identifier for the audit log record
    audit_id: str
    # Correlation identifier linking audit log to incident
    correlation_id: str
    # Categorical event type string (e.g. STATE_TRANSITION, REMEDIATION_EXEC)
    event_type: str
    # Initial state string prior to transition
    state_from: Optional[str] = None
    # Destination state string after transition
    state_to: Optional[str] = None
    # Actor initiating the event (e.g. system, operator_name)
    actor: str = "system"
    # Metadata dictionary storing event context details
    details: Dict[str, Any] = Field(default_factory=dict)
    # Timestamp when audit record was logged in UTC
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

