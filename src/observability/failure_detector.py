import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from src.common.models import FailureEvent
from src.common.security import mask_pii
from src.common.logging import get_logger

logger = get_logger("failure_detector")

class FailureDetector:
    """Detects and normalizes step-level exceptions into structured FailureEvent models."""

    def normalize_exception(
        self,
        exception: Exception,
        run_id: str,
        pipeline_id: str,
        step_id: Optional[str],
        correlation_id: str,
        error_code: Optional[str] = None,
        attempt: int = 1,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> FailureEvent:
        msg = mask_pii(str(exception))
        derived_code = error_code or getattr(exception, "code", "UNKNOWN_ERROR")

        if not error_code:
            msg_lower = msg.lower()
            if "timeout" in msg_lower or "connection" in msg_lower:
                derived_code = "TIMEOUT"
            elif "file not found" in msg_lower or "no such file" in msg_lower:
                derived_code = "FILE_NOT_FOUND"
            elif "duplicate" in msg_lower or "unique constraint" in msg_lower:
                derived_code = "DUPLICATE_KEY"
            elif "stale" in msg_lower or "watermark" in msg_lower:
                derived_code = "STALE_WATERMARK"
            elif "partition" in msg_lower:
                derived_code = "PARTITION_NOT_FOUND"
            elif "permission" in msg_lower or "access denied" in msg_lower:
                derived_code = "ACCESS_DENIED"
            elif "memory" in msg_lower or "oom" in msg_lower:
                derived_code = "OUT_OF_MEMORY"

        event = FailureEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            step_id=step_id,
            error_code=derived_code,
            error_message=msg,
            job_name=pipeline_id,
            attempt=attempt,
            correlation_id=correlation_id,
            occurred_at=datetime.utcnow(),
            normalized_data=additional_context or {}
        )
        logger.info(f"Normalized FailureEvent {event.event_id} with error code {event.error_code}")
        return event
