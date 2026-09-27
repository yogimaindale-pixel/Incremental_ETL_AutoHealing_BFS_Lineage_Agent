from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class FailureEventRequest(BaseModel):
    run_id: str
    pipeline_id: str
    error_code: str
    error_message: str
    step_id: Optional[str] = None
    correlation_id: Optional[str] = None

class ApprovalDecisionRequest(BaseModel):
    approved: bool
    responder: Optional[str] = "operator"
    reason: Optional[str] = None
