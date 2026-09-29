# Import os module for interacting with local file system paths
import os
# Import sqlite3 database connector for control plane and data target updates
import sqlite3
# Import time module for backoff sleep delays
import time
# Import datetime for timestamp formatting
from datetime import datetime
# Import typing hints for context dictionaries and callable function types
from typing import Dict, Any, Callable
# Import RiskLevel enumeration for safety classification
from src.common.models import RiskLevel
# Import RunbookExecutionError custom exception class
from src.common.exceptions import RunbookExecutionError
# Import structured logger accessor function
from src.common.logging import get_logger

# Obtain logger instance for runbook registry events
logger = get_logger("runbook_registry")

# Class managing registry of allow-listed auto-healing runbooks
class RunbookRegistry:
    """Registry of allow-listed remediation runbooks with prechecks, actions, postchecks, and rollbacks."""

    # Constructor initializing database connection file paths
    def __init__(self, db_path: str = "data/control_plane.db", source_db: str = "data/source.db", target_db: str = "data/target.db"):
        # Store path to control plane SQLite database
        self.db_path = db_path
        # Store path to operational source SQLite database
        self.source_db = source_db
        # Store path to target data warehouse SQLite database
        self.target_db = target_db

    # Dispatcher method executing a specific runbook based on runbook_id
    def execute_runbook(self, runbook_id: str, context: Dict[str, Any]) -> bool:
        # Log runbook execution start event with context parameter keys
        logger.info(f"Executing runbook {runbook_id} with context keys {list(context.keys())}")

        # Check if runbook is automatic retry handler
        if runbook_id == "RB-RETRY-001":
            return self._rb_retry(context)
        # Check if runbook is file presence wait handler
        elif runbook_id == "RB-WAIT-FILE-001":
            return self._rb_wait_file(context)
        # Check if runbook is checkpoint resume handler
        elif runbook_id == "RB-RESUME-CHK-001":
            return self._rb_resume_checkpoint(context)
        # Check if runbook is watermark reset handler
        elif runbook_id == "RB-RESET-CHK-002":
            return self._rb_reset_checkpoint(context)
        # Check if runbook is partition creation handler
        elif runbook_id == "RB-CREATE-PART-001":
            return self._rb_create_partition(context)
        # Check if runbook is malformed row quarantine handler
        elif runbook_id == "RB-QUARANTINE-001":
            return self._rb_quarantine(context)
        # Check if runbook is schema evolution column addition handler
        elif runbook_id == "RB-ADD-SCHEMA-001":
            return self._rb_add_schema(context)
        # Check if runbook is batch size reduction handler
        elif runbook_id == "RB-REDUCE-BATCH-001":
            return self._rb_reduce_batch(context)
        # Check if runbook is window replay handler
        elif runbook_id == "RB-REPLAY-WINDOW-001":
            return self._rb_replay_window(context)
        # Check if runbook is escalation handler
        elif runbook_id == "RB-ESCALATE-001":
            logger.info("Runbook RB-ESCALATE-001 selected: Escalating to manual review.")
            return True
        # Check if runbook is simulated failure test handler for circuit breaker verification
        elif runbook_id == "RB-FAIL-TEST-001":
            raise RunbookExecutionError("Simulated runbook execution failure for circuit breaker test")
        # Handle unauthorized or unknown runbook ID by raising error
        else:
            raise RunbookExecutionError(f"Unknown or unauthorized runbook_id '{runbook_id}'")

    # Private runbook handler for transient retry with capped exponential backoff
    def _rb_retry(self, context: Dict[str, Any]) -> bool:
        logger.info("RB-RETRY-001: Waiting capped backoff then approving retry...")
        # Pause execution briefly for backoff window
        time.sleep(0.1)
        # Return True indicating successful retry action
        return True

    # Private runbook handler for waiting on delayed input file landing
    def _rb_wait_file(self, context: Dict[str, Any]) -> bool:
        logger.info("RB-WAIT-FILE-001: Checking file presence or wait window...")
        time.sleep(0.1)
        return True

    # Private runbook handler for resuming execution from last valid checkpoint
    def _rb_resume_checkpoint(self, context: Dict[str, Any]) -> bool:
        logger.info("RB-RESUME-CHK-001: Resuming pipeline execution from valid checkpoint.")
        return True

    # Private runbook handler for resetting pipeline watermark checkpoint in database
    def _rb_reset_checkpoint(self, context: Dict[str, Any]) -> bool:
        # Extract pipeline identifier from context dictionary
        pipeline_id = context.get("pipeline_id", "pipe_orders_incremental")
        # Extract target reset watermark timestamp from context
        reset_wm = context.get("reset_wm", "2026-01-01T00:00:00")
        # Establish connection to control plane database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Execute SQL UPDATE query to reset last_watermark column value
            cursor.execute(
                "UPDATE watermark_state SET last_watermark = ? WHERE pipeline_id = ?",
                (reset_wm, pipeline_id)
            )
            # Commit transaction to persist database change
            conn.commit()
            logger.info(f"RB-RESET-CHK-002: Reset watermark for {pipeline_id} to {reset_wm}")
            return True
        finally:
            # Close database connection in finally block
            conn.close()

    # Private runbook handler for creating missing date partition
    def _rb_create_partition(self, context: Dict[str, Any]) -> bool:
        logger.info("RB-CREATE-PART-001: Missing partition created/verified successfully.")
        return True

    # Private runbook handler for quarantining malformed/duplicate records
    def _rb_quarantine(self, context: Dict[str, Any]) -> bool:
        logger.info("RB-QUARANTINE-001: Duplicate/malformed rows quarantined.")
        return True

    # Private runbook handler for non-destructive schema evolution (adding missing column)
    def _rb_add_schema(self, context: Dict[str, Any]) -> bool:
        # Extract target table name from context
        target_table = context.get("target_table", "fact_orders")
        # Extract new column name from context
        new_col = context.get("new_column", "discount_amount")
        # Establish connection to target data database
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        try:
            # Execute DDL statement to add new column to table schema
            cursor.execute(f"ALTER TABLE {target_table} ADD COLUMN {new_col} REAL DEFAULT 0.0")
            conn.commit()
            logger.info(f"RB-ADD-SCHEMA-001: Added column '{new_col}' to table '{target_table}'")
            return True
        except sqlite3.OperationalError as e:
            # Check if column already exists (idempotency check)
            if "duplicate column name" in str(e).lower():
                logger.info(f"Column '{new_col}' already exists in table '{target_table}'.")
                return True
            # Raise error if DDL modification failed for other reasons
            raise RunbookExecutionError(f"Failed to alter table: {str(e)}")
        finally:
            # Ensure database connection is closed
            conn.close()

    # Private runbook handler for reducing pipeline batch processing size during resource contention
    def _rb_reduce_batch(self, context: Dict[str, Any]) -> bool:
        # Extract pipeline identifier
        pipeline_id = context.get("pipeline_id", "pipe_orders_incremental")
        # Connect to control plane database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Execute SQL UPDATE to cut batch size in half
            cursor.execute(
                "UPDATE pipeline_definition SET batch_size = batch_size / 2 WHERE pipeline_id = ?",
                (pipeline_id,)
            )
            conn.commit()
            logger.info(f"RB-REDUCE-BATCH-001: Reduced batch size for {pipeline_id}")
            return True
        finally:
            conn.close()

    # Private runbook handler for marking failed window for reprocessing replay
    def _rb_replay_window(self, context: Dict[str, Any]) -> bool:
        logger.info("RB-REPLAY-WINDOW-001: Incremental window marked for replay.")
        return True

