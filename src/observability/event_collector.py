import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any
from src.common.logging import get_logger

logger = get_logger("event_collector")

class EventCollector:
    """Records pipeline runs, step runs, and failure events in SQLite control plane."""

    def __init__(self, db_path: str = "data/control_plane.db"):
        self.db_path = db_path

    def record_pipeline_run(self, run_id: str, pipeline_id: str, status: str, start_time: datetime, end_time: Optional[datetime] = None, records_extracted: int = 0, records_loaded: int = 0, error_message: Optional[str] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO pipeline_run (run_id, pipeline_id, status, start_time, end_time, records_extracted, records_loaded, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status = excluded.status,
                    end_time = excluded.end_time,
                    records_extracted = excluded.records_extracted,
                    records_loaded = excluded.records_loaded,
                    error_message = excluded.error_message
                """,
                (run_id, pipeline_id, status, start_time.isoformat(), end_time.isoformat() if end_time else None, records_extracted, records_loaded, error_message)
            )
            conn.commit()
        finally:
            conn.close()

    def record_step_run(self, step_id: str, run_id: str, step_name: str, status: str, start_time: datetime, end_time: Optional[datetime] = None, error_code: Optional[str] = None, error_message: Optional[str] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO pipeline_step_run (step_id, run_id, step_name, status, start_time, end_time, error_code, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(step_id) DO UPDATE SET
                    status = excluded.status,
                    end_time = excluded.end_time,
                    error_code = excluded.error_code,
                    error_message = excluded.error_message
                """,
                (step_id, run_id, step_name, status, start_time.isoformat(), end_time.isoformat() if end_time else None, error_code, error_message)
            )
            conn.commit()
        finally:
            conn.close()

    def record_failure_event(self, event_id: str, run_id: str, step_id: Optional[str], error_code: str, error_message: str, job_name: str, correlation_id: str, attempt: int = 1, normalized_data: Optional[Dict[str, Any]] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO failure_event (event_id, run_id, step_id, error_code, error_message, job_name, attempt, correlation_id, occurred_at, normalized_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """,
                (event_id, run_id, step_id, error_code, error_message, job_name, attempt, correlation_id, json.dumps(normalized_data or {}))
            )
            conn.commit()
            logger.info(f"Recorded failure event {event_id} (Code: {error_code}, Job: {job_name})")
        finally:
            conn.close()
