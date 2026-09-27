from typing import Dict, Any, Optional, Tuple
from src.common.models import ClassificationResult, RiskLevel
from src.common.config import ConfigManager

class HealingRuleEngine:
    """Maps classified failure results to allow-listed runbook IDs and determines risk levels."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.rules = config_manager.healing_rules.get("rules", [])

    def select_runbook(self, classification: ClassificationResult) -> Tuple[Optional[str], RiskLevel]:
        runbook_id = classification.runbook_id or "RB-ESCALATE-001"

        risk_level = RiskLevel.LOW
        if runbook_id in ["RB-RESET-CHK-002", "RB-REPLAY-WINDOW-001"]:
            risk_level = RiskLevel.HIGH
        elif runbook_id in ["RB-QUARANTINE-001", "RB-CREATE-PART-001", "RB-ADD-SCHEMA-001"]:
            risk_level = RiskLevel.MEDIUM
        elif runbook_id in ["RB-ESCALATE-001"]:
            risk_level = RiskLevel.HIGH

        return runbook_id, risk_level
