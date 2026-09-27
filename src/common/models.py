from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class IncidentState(str, Enum):
    DETECTED = "DETECTED"
    NORMALIZED = "NORMALIZED"
    CLASSIFIED = "CLASSIFIED"
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    LINEAGE_TRAVERSED = "LINEAGE_TRAVERSED"
    ROOT_CAUSE_IDENTIFIED = "ROOT_CAUSE_IDENTIFIED"
    REMEDIATION_SELECTED = "REMEDIATION_SELECTED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    REMEDIATING = "REMEDIATING"
    VALIDATING = "VALIDATING"
    RECOVERED = "RECOVERED"
    ROLLED_BACK = "ROLLED_BACK"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"

class RiskLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    DESTRUCTIVE = "DESTRUCTIVE"

class NodeType(str, Enum):
    SYSTEM = "system"
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    FILE = "file"
    TOPIC = "topic"
    PIPELINE = "pipeline"
    JOB = "job"
    TASK = "task"
    TRANSFORMATION = "transformation"
    API = "API"
    REPORT = "report"
    DASHBOARD = "dashboard"

class EdgeType(str, Enum):
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    TRANSFORMS = "TRANSFORMS"
    TRIGGERS = "TRIGGERS"
    DEPENDS_ON = "DEPENDS_ON"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"
    DERIVES_FROM = "DERIVES_FROM"

class LineageNode(BaseModel):
    node_id: str
    name: str
    type: NodeType
    environment: str = "local"
    source_adapter: str = "sqlite"
    last_observed: datetime = Field(default_factory=datetime.utcnow)
    metadata_version: int = 1
    active: bool = True

class LineageEdge(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    type: EdgeType
    active: bool = True

class FailureEvent(BaseModel):
    event_id: str
    run_id: str
    step_id: Optional[str] = None
    error_code: str
    error_message: str
    job_name: Optional[str] = None
    attempt: int = 1
    correlation_id: str
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    normalized_data: Dict[str, Any] = Field(default_factory=dict)

class ClassificationResult(BaseModel):
    rule_id: str
    rule_version: int
    classification: str
    runbook_id: Optional[str] = None
    confidence: float
    matched_conditions: List[str]
    evidence_references: List[str]
    classified_at: datetime = Field(default_factory=datetime.utcnow)

class RootCauseCandidate(BaseModel):
    node_id: str
    node_name: str
    score: float
    reason: str

class Incident(BaseModel):
    incident_id: str
    event_id: str
    pipeline_id: str
    correlation_id: str
    status: IncidentState = IncidentState.DETECTED
    classification: str = "UNKNOWN"
    confidence_score: float = 0.0
    root_cause_node_id: Optional[str] = None
    selected_runbook_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApprovalRequest(BaseModel):
    approval_id: str
    incident_id: str
    runbook_id: str
    risk_level: RiskLevel
    environment: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    responded_by: Optional[str] = None
    reason: Optional[str] = None

class RemediationRun(BaseModel):
    remediation_id: str
    incident_id: str
    runbook_id: str
    idempotency_key: str
    status: str = "STARTED"  # STARTED, SUCCESS, FAILED, ROLLED_BACK
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class ValidationResultModel(BaseModel):
    validation_id: str
    remediation_id: str
    passed: bool
    step_checks_passed: bool = True
    reconciliation_passed: bool = True
    dq_passed: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)
    checked_at: datetime = Field(default_factory=datetime.utcnow)

class AuditEventModel(BaseModel):
    audit_id: str
    correlation_id: str
    event_type: str
    state_from: Optional[str] = None
    state_to: Optional[str] = None
    actor: str = "system"
    details: Dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
