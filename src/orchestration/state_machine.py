import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from src.common.models import IncidentState
from src.common.exceptions import InvalidStateTransitionError
from src.common.logging import get_logger

logger = get_logger("state_machine")

VALID_TRANSITIONS: Dict[IncidentState, List[IncidentState]] = {
    IncidentState.DETECTED: [IncidentState.NORMALIZED, IncidentState.ESCALATED],
    IncidentState.NORMALIZED: [IncidentState.CLASSIFIED, IncidentState.ESCALATED],
    IncidentState.CLASSIFIED: [IncidentState.EVIDENCE_COLLECTED, IncidentState.ESCALATED],
    IncidentState.EVIDENCE_COLLECTED: [IncidentState.LINEAGE_TRAVERSED, IncidentState.ESCALATED],
    IncidentState.LINEAGE_TRAVERSED: [IncidentState.ROOT_CAUSE_IDENTIFIED, IncidentState.ESCALATED],
    IncidentState.ROOT_CAUSE_IDENTIFIED: [IncidentState.REMEDIATION_SELECTED, IncidentState.ESCALATED],
    IncidentState.REMEDIATION_SELECTED: [IncidentState.AWAITING_APPROVAL, IncidentState.REMEDIATING, IncidentState.ESCALATED],
    IncidentState.AWAITING_APPROVAL: [IncidentState.REMEDIATING, IncidentState.ESCALATED],
    IncidentState.REMEDIATING: [IncidentState.VALIDATING, IncidentState.ROLLED_BACK, IncidentState.ESCALATED],
    IncidentState.VALIDATING: [IncidentState.RECOVERED, IncidentState.ROLLED_BACK, IncidentState.ESCALATED],
    IncidentState.RECOVERED: [IncidentState.CLOSED],
    IncidentState.ROLLED_BACK: [IncidentState.ESCALATED, IncidentState.CLOSED],
    IncidentState.ESCALATED: [IncidentState.CLOSED],
    IncidentState.CLOSED: [],
}

class IncidentStateMachine:
    """Enforces explicit state machine transitions and logs append-only audit events."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path

    def transition(self, incident_id: str, current_state: IncidentState, target_state: IncidentState, correlation_id: str, actor: str = "system", reason: str = "") -> IncidentState:
        allowed = VALID_TRANSITIONS.get(current_state, [])
        if target_state not in allowed:
            msg = f"Invalid state transition from {current_state.value} to {target_state.value} for incident {incident_id}"
            logger.error(msg)
            raise InvalidStateTransitionError(msg)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Update incident table
            cursor.execute(
                """
                UPDATE incident
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE incident_id = ?
                """,
                (target_state.value, incident_id)
            )

            # Append audit event
            audit_id = f"aud_{uuid.uuid4().hex[:12]}"
            audit_details = json.dumps({"reason": reason, "incident_id": incident_id})
            cursor.execute(
                """
                INSERT INTO audit_event (audit_id, correlation_id, event_type, state_from, state_to, actor, details, occurred_at)
                VALUES (?, ?, 'INCIDENT_STATE_TRANSITION', ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (audit_id, correlation_id, current_state.value, target_state.value, actor, audit_details)
            )
            conn.commit()
            logger.info(f"Transitioned incident {incident_id} from {current_state.value} -> {target_state.value}")
            return target_state
        finally:
            conn.close()
