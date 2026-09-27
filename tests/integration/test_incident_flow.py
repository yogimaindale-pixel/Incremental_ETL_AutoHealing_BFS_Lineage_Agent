import pytest
from src.common.config import ConfigManager
from src.common.models import FailureEvent, IncidentState
from src.orchestration.coordinator import IncidentCoordinator
from scripts.seed_demo_data import seed

def test_incident_flow_detection_to_recovery():
    seed()
    config_manager = ConfigManager()
    coordinator = IncidentCoordinator(config_manager)

    evt = FailureEvent(
        event_id="evt_flow_001",
        run_id="run_flow_001",
        error_code="TIMEOUT",
        error_message="Connection timed out",
        job_name="pipe_orders_incremental",
        correlation_id="corr_flow_001"
    )

    incident = coordinator.handle_failure_event(evt, "pipe_orders_incremental")
    assert incident.classification == "TRANSIENT_CONNECTION"
    assert incident.status in [IncidentState.CLOSED, IncidentState.RECOVERED]
