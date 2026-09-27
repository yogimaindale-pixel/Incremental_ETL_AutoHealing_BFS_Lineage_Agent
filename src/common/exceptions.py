class ETLAgentError(Exception):
    """Base exception for all ETL Auto-Healing Agent errors."""
    pass

class ConfigurationError(ETLAgentError):
    """Raised when configuration validation or loading fails."""
    pass

class IngestionError(ETLAgentError):
    """Raised during extraction or staging failures."""
    pass

class WatermarkError(ETLAgentError):
    """Raised when watermark operations fail."""
    pass

class ClassificationError(ETLAgentError):
    """Raised when failure classification rules fail or conflict."""
    pass

class LineageGraphError(ETLAgentError):
    """Raised during graph building or BFS traversal failures."""
    pass

class RunbookExecutionError(ETLAgentError):
    """Raised during runbook execution or rollback."""
    pass

class ValidationError(ETLAgentError):
    """Raised when technical or data quality validations fail."""
    pass

class InvalidStateTransitionError(ETLAgentError):
    """Raised when an invalid state transition is requested."""
    pass

class EscalationRequired(ETLAgentError):
    """Raised when an incident requires manual escalation."""
    pass
