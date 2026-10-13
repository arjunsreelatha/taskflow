from taskflow.states import JobStatus, can_transition

def test_pending_can_transition_to_running():
    assert can_transition(JobStatus.PENDING,JobStatus.RUNNING,)

def test_pending_cannot_transition_to_completed():
    assert not can_transition(
        JobStatus.PENDING,
        JobStatus.COMPLETED,
    )
