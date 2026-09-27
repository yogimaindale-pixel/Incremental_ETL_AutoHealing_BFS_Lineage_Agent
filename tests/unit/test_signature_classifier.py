import pytest
from src.common.config import ConfigManager
from src.common.models import FailureEvent
from src.diagnosis.signature_classifier import SignatureClassifier

def test_signature_classifier_matches_rules():
    config_manager = ConfigManager()
    classifier = SignatureClassifier(config_manager)

    evt = FailureEvent(
        event_id="evt_test_001",
        run_id="run_001",
        error_code="TIMEOUT",
        error_message="Query timeout connection reset",
        job_name="pipe_orders_incremental",
        correlation_id="corr_001"
    )

    res = classifier.classify(evt)
    assert res.classification == "TRANSIENT_CONNECTION"
    assert res.runbook_id == "RB-RETRY-001"
    assert res.confidence > 0.8
