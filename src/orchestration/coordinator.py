import uuid
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional
from src.common.models import FailureEvent, Incident, IncidentState, ApprovalRequest
from src.common.config import ConfigManager
from src.diagnosis.signature_classifier import SignatureClassifier
from src.diagnosis.evidence_collector import EvidenceCollector
from src.diagnosis.root_cause_engine import RootCauseEngine
from src.lineage.graph_builder import GraphBuilder
from src.healing.rule_engine import HealingRuleEngine
from src.healing.risk_engine import RiskEngine
from src.healing.remediation_executor import RemediationExecutor
from src.validation.technical_validator import TechnicalValidator
from src.validation.reconciliation import ReconciliationEngine
from src.validation.data_quality_validator import DataQualityValidator
from src.orchestration.state_machine import IncidentStateMachine
from src.common.logging import get_logger

logger = get_logger("coordinator")

class IncidentCoordinator:
    """Master orchestrator driving detection, diagnosis, remediation, validation, and audit flow."""

    def __init__(self, config_manager: ConfigManager, db_path: str = "data/control_plane.db"):
        self.config_manager = config_manager
        self.db_path = db_path
        self.classifier = SignatureClassifier(config_manager)
        self.evidence_collector = EvidenceCollector(db_path)
        self.graph = GraphBuilder(db_path).build_from_yaml()
        self.root_cause_engine = RootCauseEngine(self.graph, db_path)
        self.healing_rule_engine = HealingRuleEngine(config_manager)
        self.risk_engine = RiskEngine(config_manager)
        self.executor = RemediationExecutor(db_path)
        self.technical_validator = TechnicalValidator()
        self.reconciliation_engine = ReconciliationEngine()
        self.dq_validator = DataQualityValidator(config_manager)
        self.state_machine = IncidentStateMachine(db_path)

    def handle_failure_event(self, event: FailureEvent, pipeline_id: str, source_node_id: str = "source_orders") -> Incident:
        logger.info(f"Coordinator processing failure event {event.event_id} for pipeline {pipeline_id}")

        incident_id = f"inc_{uuid.uuid4().hex[:12]}"
        incident = Incident(
            incident_id=incident_id,
            event_id=event.event_id,
            pipeline_id=pipeline_id,
            correlation_id=event.correlation_id,
            status=IncidentState.DETECTED
        )
        self._record_incident(incident)

        # 1. Normalize
        self.state_machine.transition(incident_id, IncidentState.DETECTED, IncidentState.NORMALIZED, event.correlation_id)

        # 2. Classify
        classification = self.classifier.classify(event)
        incident.classification = classification.classification
        incident.confidence_score = classification.confidence
        self.state_machine.transition(incident_id, IncidentState.NORMALIZED, IncidentState.CLASSIFIED, event.correlation_id)

        # 3. Collect Evidence
        evidence = self.evidence_collector.collect_evidence(event)
        self.state_machine.transition(incident_id, IncidentState.CLASSIFIED, IncidentState.EVIDENCE_COLLECTED, event.correlation_id)

        # 4. Lineage Traversal & Root Cause Identification
        root_causes = self.root_cause_engine.find_root_cause(event, source_node_id)
        if root_causes:
            incident.root_cause_node_id = root_causes[0].node_id
        self.state_machine.transition(incident_id, IncidentState.EVIDENCE_COLLECTED, IncidentState.LINEAGE_TRAVERSED, event.correlation_id)
        self.state_machine.transition(incident_id, IncidentState.LINEAGE_TRAVERSED, IncidentState.ROOT_CAUSE_IDENTIFIED, event.correlation_id)

        # 5. Runbook Selection & Risk Evaluation
        runbook_id, risk_level = self.healing_rule_engine.select_runbook(classification)
        incident.selected_runbook_id = runbook_id
        self.state_machine.transition(incident_id, IncidentState.ROOT_CAUSE_IDENTIFIED, IncidentState.REMEDIATION_SELECTED, event.correlation_id)

        if classification.classification == "MANUAL_REVIEW_REQUIRED" or runbook_id == "RB-ESCALATE-001":
            logger.warning(f"Incident {incident_id} requires escalation due to unsupported/uncertain classification.")
            self.state_machine.transition(incident_id, IncidentState.REMEDIATION_SELECTED, IncidentState.ESCALATED, event.correlation_id)
            incident.status = IncidentState.ESCALATED
            self._record_incident(incident)
            return incident

        requires_app = self.risk_engine.requires_approval(risk_level)

        if requires_app:
            logger.info(f"Incident {incident_id} requires human approval for runbook {runbook_id} (Risk: {risk_level.value})")
            self._create_approval_request(incident_id, runbook_id, risk_level.value)
            self.state_machine.transition(incident_id, IncidentState.REMEDIATION_SELECTED, IncidentState.AWAITING_APPROVAL, event.correlation_id)
            incident.status = IncidentState.AWAITING_APPROVAL
            self._record_incident(incident)
            return incident

        # 6. Execute Remediation directly
        self.state_machine.transition(incident_id, IncidentState.REMEDIATION_SELECTED, IncidentState.REMEDIATING, event.correlation_id)
        rem_context = {"pipeline_id": pipeline_id, "event": event, "incident_id": incident_id}
        rem_run = self.executor.execute_remediation(incident, runbook_id, rem_context)

        # 7. Validate
        self.state_machine.transition(incident_id, IncidentState.REMEDIATING, IncidentState.VALIDATING, event.correlation_id)
        if rem_run.status == "SUCCESS":
            self.state_machine.transition(incident_id, IncidentState.VALIDATING, IncidentState.RECOVERED, event.correlation_id)
            self.state_machine.transition(incident_id, IncidentState.RECOVERED, IncidentState.CLOSED, event.correlation_id)
            incident.status = IncidentState.CLOSED
        else:
            self.state_machine.transition(incident_id, IncidentState.VALIDATING, IncidentState.ROLLED_BACK, event.correlation_id)
            self.state_machine.transition(incident_id, IncidentState.ROLLED_BACK, IncidentState.ESCALATED, event.correlation_id)
            incident.status = IncidentState.ESCALATED

        self._record_incident(incident)
        return incident

    def process_approval(self, incident_id: str, approved: bool, responder: str = "operator") -> Incident:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, pipeline_id, correlation_id, selected_runbook_id FROM incident WHERE incident_id = ?", (incident_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Incident {incident_id} not found")

        event_id, pipeline_id, correlation_id, runbook_id = row

        incident = Incident(
            incident_id=incident_id,
            event_id=event_id,
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            status=IncidentState.AWAITING_APPROVAL,
            selected_runbook_id=runbook_id
        )

        if not approved:
            logger.info(f"Approval rejected for incident {incident_id}")
            self.state_machine.transition(incident_id, IncidentState.AWAITING_APPROVAL, IncidentState.ESCALATED, correlation_id, actor=responder, reason="Human rejected remediation")
            incident.status = IncidentState.ESCALATED
            self._record_incident(incident)
            return incident

        logger.info(f"Approval granted for incident {incident_id}. Proceeding with remediation.")
        self.state_machine.transition(incident_id, IncidentState.AWAITING_APPROVAL, IncidentState.REMEDIATING, correlation_id, actor=responder, reason="Human approved remediation")

        rem_context = {"pipeline_id": pipeline_id, "incident_id": incident_id}
        rem_run = self.executor.execute_remediation(incident, runbook_id, rem_context)

        self.state_machine.transition(incident_id, IncidentState.REMEDIATING, IncidentState.VALIDATING, correlation_id)
        if rem_run.status == "SUCCESS":
            self.state_machine.transition(incident_id, IncidentState.VALIDATING, IncidentState.RECOVERED, correlation_id)
            self.state_machine.transition(incident_id, IncidentState.RECOVERED, IncidentState.CLOSED, correlation_id)
            incident.status = IncidentState.CLOSED
        else:
            self.state_machine.transition(incident_id, IncidentState.VALIDATING, IncidentState.ROLLED_BACK, correlation_id)
            self.state_machine.transition(incident_id, IncidentState.ROLLED_BACK, IncidentState.ESCALATED, correlation_id)
            incident.status = IncidentState.ESCALATED

        self._record_incident(incident)
        return incident

    def _create_approval_request(self, incident_id: str, runbook_id: str, risk_level: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            app_id = f"appr_{uuid.uuid4().hex[:12]}"
            cursor.execute(
                """
                INSERT INTO approval_request (approval_id, incident_id, runbook_id, risk_level, environment, status, requested_at)
                VALUES (?, ?, ?, ?, ?, 'PENDING', CURRENT_TIMESTAMP)
                """,
                (app_id, incident_id, runbook_id, risk_level, self.config_manager.env)
            )
            conn.commit()
        finally:
            conn.close()

    def _record_incident(self, incident: Incident):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO incident (incident_id, event_id, pipeline_id, correlation_id, status, classification, confidence_score, root_cause_node_id, selected_runbook_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(incident_id) DO UPDATE SET
                    status = excluded.status,
                    classification = excluded.classification,
                    confidence_score = excluded.confidence_score,
                    root_cause_node_id = excluded.root_cause_node_id,
                    selected_runbook_id = excluded.selected_runbook_id,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    incident.incident_id,
                    incident.event_id,
                    incident.pipeline_id,
                    incident.correlation_id,
                    incident.status.value,
                    incident.classification,
                    incident.confidence_score,
                    incident.root_cause_node_id,
                    incident.selected_runbook_id,
                    incident.created_at.isoformat(),
                    datetime.utcnow().isoformat()
                )
            )
            conn.commit()
        finally:
            conn.close()
