import uuid
import sqlite3
from datetime import datetime
from typing import Dict, Any
from src.common.models import Incident, RemediationRun
from src.healing.runbook_registry import RunbookRegistry
from src.healing.rollback import RollbackHandler
from src.common.exceptions import RunbookExecutionError
from src.common.logging import get_logger

logger = get_logger("remediation_executor")

class RemediationExecutor:
    """Executes selected runbook enforcing idempotency keys and safe rollback."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path
        self.registry = RunbookRegistry(db_path)
        self.rollback_handler = RollbackHandler(db_path)

    def execute_remediation(self, incident: Incident, runbook_id: str, context: Dict[str, Any]) -> RemediationRun:
        idempotency_key = f"idem_{incident.incident_id}_{runbook_id}"

        # Check existing remediation run
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT remediation_id, status FROM remediation_run WHERE idempotency_key = ?",
                (idempotency_key,)
            )
            existing = cursor.fetchone()
            if existing and existing[1] == "SUCCESS":
                logger.info(f"Remediation already completed for idempotency_key {idempotency_key}")
                return RemediationRun(
                    remediation_id=existing[0],
                    incident_id=incident.incident_id,
                    runbook_id=runbook_id,
                    idempotency_key=idempotency_key,
                    status="SUCCESS"
                )
        finally:
            conn.close()

        remediation = RemediationRun(
            remediation_id=f"rem_{uuid.uuid4().hex[:12]}",
            incident_id=incident.incident_id,
            runbook_id=runbook_id,
            idempotency_key=idempotency_key,
            status="STARTED",
            start_time=datetime.utcnow()
        )
        self._record_remediation(remediation)

        try:
            success = self.registry.execute_runbook(runbook_id, context)
            if success:
                remediation.status = "SUCCESS"
                remediation.end_time = datetime.utcnow()
                logger.info(f"Remediation {remediation.remediation_id} succeeded for incident {incident.incident_id}")
            else:
                remediation.status = "FAILED"
                remediation.end_time = datetime.utcnow()
                remediation.error_message = "Runbook execution returned False"
                self.rollback_handler.rollback_remediation(remediation, context)
        except Exception as e:
            remediation.status = "FAILED"
            remediation.end_time = datetime.utcnow()
            remediation.error_message = str(e)
            logger.error(f"Remediation {remediation.remediation_id} failed: {str(e)}")
            self.rollback_handler.rollback_remediation(remediation, context)

        self._record_remediation(remediation)
        return remediation

    def _record_remediation(self, rem: RemediationRun):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO remediation_run (remediation_id, incident_id, runbook_id, idempotency_key, status, start_time, end_time, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(remediation_id) DO UPDATE SET
                    status = excluded.status,
                    end_time = excluded.end_time,
                    error_message = excluded.error_message
                """,
                (
                    rem.remediation_id,
                    rem.incident_id,
                    rem.runbook_id,
                    rem.idempotency_key,
                    rem.status,
                    rem.start_time.isoformat(),
                    rem.end_time.isoformat() if rem.end_time else None,
                    rem.error_message
                )
            )
            conn.commit()
        finally:
            conn.close()
