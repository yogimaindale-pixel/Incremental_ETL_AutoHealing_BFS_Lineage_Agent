from typing import Dict, Any
from src.common.models import RiskLevel
from src.common.config import ConfigManager

class RiskEngine:
    """Evaluates risk policy and determines if human approval is required."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.policy_cfg = config_manager.risk_policy.get("risk_policy", {})
        self.env = config_manager.env

    def requires_approval(self, runbook_risk: RiskLevel, environment: str = None) -> bool:
        target_env = environment or self.env
        risk_str = runbook_risk.value if hasattr(runbook_risk, "value") else str(runbook_risk)

        rule = self.policy_cfg.get(risk_str, {})
        req_by_env = rule.get("requires_approval_by_env", {})

        return req_by_env.get(target_env, True)
