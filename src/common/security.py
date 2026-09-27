import re
from typing import Any, Dict, List
from src.common.exceptions import ETLAgentError

ALLOWED_SQL_COMMANDS = {"SELECT", "INSERT", "UPDATE", "DELETE", "MERGE", "CREATE", "ALTER", "DROP"}

def validate_sql_allowlist(sql: str) -> bool:
    """Validates that SQL statements start with an allowed command."""
    cleaned = sql.strip().upper()
    first_word = cleaned.split()[0] if cleaned else ""
    if first_word not in ALLOWED_SQL_COMMANDS:
        raise ETLAgentError(f"Security Policy Breach: SQL command '{first_word}' is not allow-listed.")
    return True

def sanitize_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures parameter dictionary values are safe for parameterized execution."""
    sanitized = {}
    for key, val in params.items():
        if isinstance(val, str):
            # Strip null bytes
            sanitized[key] = val.replace("\x00", "")
        else:
            sanitized[key] = val
    return sanitized

def mask_pii(text: str) -> str:
    """Masks emails, credit cards, and SSNs in log or error strings."""
    if not text:
        return ""
    # Mask emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[MASKED_EMAIL]', text)
    # Mask 16-digit credit cards
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[MASKED_CARD]', text)
    return text
