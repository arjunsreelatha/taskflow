from taskflow.states import JobStatus, can_transition

import pytest

from taskflow.errors import InvalidTransition
from taskflow.states import JobStatus, can_transition, assert_transition



def test_pending_can_transition_to_running():
    assert can_transition(JobStatus.PENDING,JobStatus.RUNNING,)

def test_pending_cannot_transition_to_completed():
    assert not can_transition(
        JobStatus.PENDING,
        JobStatus.COMPLETED,
    )


def test_invalid_transition_raises_exception():
    with pytest.raises(InvalidTransition):
        assert_transition(
            JobStatus.PENDING,
            JobStatus.COMPLETED,
        )