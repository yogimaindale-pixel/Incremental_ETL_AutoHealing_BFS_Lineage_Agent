import pytest
from src.common.models import IncidentState
from src.common.exceptions import InvalidStateTransitionError
from src.orchestration.state_machine import IncidentStateMachine
from scripts.seed_demo_data import seed

def test_state_machine_valid_and_invalid_transitions():
    seed()
    sm = IncidentStateMachine("data/control_plane.db")
    inc_id = "inc_test_sm_001"

    # Valid transition DETECTED -> NORMALIZED
    s1 = sm.transition(inc_id, IncidentState.DETECTED, IncidentState.NORMALIZED, "corr_sm")
    assert s1 == IncidentState.NORMALIZED

    # Invalid transition NORMALIZED -> RECOVERED directly should raise error
    with pytest.raises(InvalidStateTransitionError):
        sm.transition(inc_id, IncidentState.NORMALIZED, IncidentState.RECOVERED, "corr_sm")
