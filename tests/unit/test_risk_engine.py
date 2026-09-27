import pytest
from src.common.config import ConfigManager
from src.common.models import RiskLevel
from src.healing.risk_engine import RiskEngine

def test_risk_engine_policy_evaluation():
    config_manager = ConfigManager()
    risk_engine = RiskEngine(config_manager)

    # In local environment, LOW risk does not require approval
    assert risk_engine.requires_approval(RiskLevel.LOW, "local") is False

    # HIGH risk requires approval in prod
    assert risk_engine.requires_approval(RiskLevel.HIGH, "prod") is True
