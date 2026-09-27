import sqlite3
from typing import Dict, Any, List
from src.common.models import FailureEvent

class EvidenceCollector:
    """Collects historical runs, watermark logs, and step records for incident correlation."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path

    def collect_evidence(self, event: FailureEvent) -> Dict[str, Any]:
        evidence = {
            "event_id": event.event_id,
            "error_code": event.error_code,
            "error_message": event.error_message,
            "correlation_id": event.correlation_id,
            "recent_runs": [],
            "watermark_state": None
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Fetch recent pipeline runs for job
            cursor.execute(
                """
                SELECT run_id, status, start_time, end_time, error_message
                FROM pipeline_run
                WHERE pipeline_id = ?
                ORDER BY start_time DESC LIMIT 5
                """,
                (event.job_name,)
            )
            rows = cursor.fetchall()
            for r in rows:
                evidence["recent_runs"].append({
                    "run_id": r[0],
                    "status": r[1],
                    "start_time": r[2],
                    "end_time": r[3],
                    "error_message": r[4]
                })

            # Fetch watermark state
            cursor.execute(
                "SELECT last_watermark, batch_id, updated_at FROM watermark_state WHERE pipeline_id = ?",
                (event.job_name,)
            )
            wm = cursor.fetchone()
            if wm:
                evidence["watermark_state"] = {
                    "last_watermark": wm[0],
                    "batch_id": wm[1],
                    "updated_at": wm[2]
                }
        except Exception:
            pass
        finally:
            conn.close()

        return evidence
