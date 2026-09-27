import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

SENSITIVE_KEYS = {"password", "secret", "token", "credential", "api_key", "ssn", "credit_card"}

class JSONFormatter(logging.Formatter):
    """Formats logs as structured JSON and redacts sensitive data."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = getattr(record, "correlation_id")
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        sanitized = self._redact(log_obj)
        return json.dumps(sanitized)

    def _redact(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            res = {}
            for k, v in obj.items():
                if any(s in k.lower() for s in SENSITIVE_KEYS):
                    res[k] = "***REDACTED***"
                else:
                    res[k] = self._redact(v)
            return res
        elif isinstance(obj, list):
            return [self._redact(item) for item in obj]
        elif isinstance(obj, str):
            for s in SENSITIVE_KEYS:
                if s in obj.lower() and "=" in obj:
                    return "***REDACTED***"
            return obj
        return obj

def get_logger(name: str = "etl_agent", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
