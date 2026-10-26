
from app.services.workflow_service import can_transition
def test_workflow_transitions():
    assert can_transition("SUBMITTED", "DATA_CHECK")
    assert can_transition("SCORING", "RESULT_READY")
    assert not can_transition("RESULT_READY", "SUBMITTED")
