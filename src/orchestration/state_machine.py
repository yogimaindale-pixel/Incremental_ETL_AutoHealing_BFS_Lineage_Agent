# Import sqlite3 database library for persisting state transitions and audit logs
import sqlite3
# Import json library for formatting audit log details payloads
import json
# Import uuid module for generating unique audit record identifiers
import uuid
# Import datetime for timestamp management
from datetime import datetime
# Import typing hints for dictionaries, lists, and any parameters
from typing import Dict, Any, List
# Import IncidentState enumeration defining 14 formal incident lifecycle states
from src.common.models import IncidentState
# Import InvalidStateTransitionError custom exception class
from src.common.exceptions import InvalidStateTransitionError
# Import structured logger accessor function
from src.common.logging import get_logger

# Obtain logger instance for state machine transition tracking
logger = get_logger("state_machine")

# Master state transition matrix dictionary defining allowed destination states for each IncidentState
VALID_TRANSITIONS: Dict[IncidentState, List[IncidentState]] = {
    # DETECTED can transition to NORMALIZED or directly to ESCALATED
    IncidentState.DETECTED: [IncidentState.NORMALIZED, IncidentState.ESCALATED],
    # NORMALIZED can transition to CLASSIFIED or ESCALATED
    IncidentState.NORMALIZED: [IncidentState.CLASSIFIED, IncidentState.ESCALATED],
    # CLASSIFIED can transition to EVIDENCE_COLLECTED or ESCALATED
    IncidentState.CLASSIFIED: [IncidentState.EVIDENCE_COLLECTED, IncidentState.ESCALATED],
    # EVIDENCE_COLLECTED can transition to LINEAGE_TRAVERSED or ESCALATED
    IncidentState.EVIDENCE_COLLECTED: [IncidentState.LINEAGE_TRAVERSED, IncidentState.ESCALATED],
    # LINEAGE_TRAVERSED can transition to ROOT_CAUSE_IDENTIFIED or ESCALATED
    IncidentState.LINEAGE_TRAVERSED: [IncidentState.ROOT_CAUSE_IDENTIFIED, IncidentState.ESCALATED],
    # ROOT_CAUSE_IDENTIFIED can transition to REMEDIATION_SELECTED or ESCALATED
    IncidentState.ROOT_CAUSE_IDENTIFIED: [IncidentState.REMEDIATION_SELECTED, IncidentState.ESCALATED],
    # REMEDIATION_SELECTED can transition to AWAITING_APPROVAL, REMEDIATING, or ESCALATED
    IncidentState.REMEDIATION_SELECTED: [IncidentState.AWAITING_APPROVAL, IncidentState.REMEDIATING, IncidentState.ESCALATED],
    # AWAITING_APPROVAL can transition to REMEDIATING upon approval or ESCALATED upon rejection
    IncidentState.AWAITING_APPROVAL: [IncidentState.REMEDIATING, IncidentState.ESCALATED],
    # REMEDIATING can transition to VALIDATING, ROLLED_BACK (on failure), or ESCALATED
    IncidentState.REMEDIATING: [IncidentState.VALIDATING, IncidentState.ROLLED_BACK, IncidentState.ESCALATED],
    # VALIDATING can transition to RECOVERED (on pass), ROLLED_BACK (on fail), or ESCALATED
    IncidentState.VALIDATING: [IncidentState.RECOVERED, IncidentState.ROLLED_BACK, IncidentState.ESCALATED],
    # RECOVERED can transition to terminal CLOSED state
    IncidentState.RECOVERED: [IncidentState.CLOSED],
    # ROLLED_BACK can transition to ESCALATED or terminal CLOSED state
    IncidentState.ROLLED_BACK: [IncidentState.ESCALATED, IncidentState.CLOSED],
    # ESCALATED can transition to terminal CLOSED state after manual review
    IncidentState.ESCALATED: [IncidentState.CLOSED],
    # CLOSED state has no further outgoing allowed transitions (terminal state)
    IncidentState.CLOSED: [],
}

# Class enforcing explicit state machine transition contracts and logging audit events
class IncidentStateMachine:
    """Enforces explicit state machine transitions and logs append-only audit events."""

    # Constructor initializing SQLite control plane database file path
    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path

    # Method executing atomic state transition with validation and audit logging
    def transition(self, incident_id: str, current_state: IncidentState, target_state: IncidentState, correlation_id: str, actor: str = "system", reason: str = "") -> IncidentState:
        # Fetch list of allowed destination states from VALID_TRANSITIONS lookup matrix
        allowed = VALID_TRANSITIONS.get(current_state, [])
        # Raise exception if proposed target_state is not in allowed list
        if target_state not in allowed:
            msg = f"Invalid state transition from {current_state.value} to {target_state.value} for incident {incident_id}"
            logger.error(msg)
            raise InvalidStateTransitionError(msg)

        # Connect to SQLite control plane database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Execute SQL UPDATE query to modify incident status column value
            cursor.execute(
                """
                UPDATE incident
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE incident_id = ?
                """,
                (target_state.value, incident_id)
            )

            # Generate unique audit log ID string
            audit_id = f"aud_{uuid.uuid4().hex[:12]}"
            # Format JSON string containing state transition reason and context
            audit_details = json.dumps({"reason": reason, "incident_id": incident_id})
            # Insert immutable audit record into audit_event log table
            cursor.execute(
                """
                INSERT INTO audit_event (audit_id, correlation_id, event_type, state_from, state_to, actor, details, occurred_at)
                VALUES (?, ?, 'INCIDENT_STATE_TRANSITION', ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (audit_id, correlation_id, current_state.value, target_state.value, actor, audit_details)
            )
            # Commit transaction to database
            conn.commit()
            logger.info(f"Transitioned incident {incident_id} from {current_state.value} -> {target_state.value}")
            # Return new target state upon success
            return target_state
        finally:
            # Ensure database connection is closed
            conn.close()

