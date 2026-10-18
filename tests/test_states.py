import pytest

from taskflow.errors import InvalidTransition, TaskFlowError
from taskflow.states import (
    ALLOWED,
    JobStatus,
    assert_transition,
    can_transition,
)


def test_pending_can_transition_to_running():
    assert can_transition(
        JobStatus.PENDING,
        JobStatus.RUNNING,
    )


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


def test_completed_job_cannot_transition_to_running():
    assert not can_transition(JobStatus.COMPLETED, JobStatus.RUNNING)


def test_invalid_transition_is_taskflow_error():
    error = InvalidTransition("Bad transition")
    assert isinstance(error, TaskFlowError)


def test_all_allowed_transitions():
    allowed_transitions = [
        (JobStatus.PENDING, JobStatus.RUNNING),
        (JobStatus.PENDING, JobStatus.CANCELLED),
        (JobStatus.RUNNING, JobStatus.COMPLETED),
        (JobStatus.RUNNING, JobStatus.FAILED),
        (JobStatus.RUNNING, JobStatus.DEAD),
        (JobStatus.RUNNING, JobStatus.CANCELLED),
        (JobStatus.FAILED, JobStatus.PENDING),
        (JobStatus.FAILED, JobStatus.CANCELLED),
        (JobStatus.DEAD, JobStatus.PENDING),
    ]

    for current, new in allowed_transitions:
        assert can_transition(current, new), f"{current.value} -> {new.value} should be allowed"


def test_forbidden_transitions():
    forbidden_transitions = [
        (JobStatus.PENDING, JobStatus.COMPLETED),
        (JobStatus.PENDING, JobStatus.FAILED),
        (JobStatus.RUNNING, JobStatus.PENDING),
        (JobStatus.COMPLETED, JobStatus.RUNNING),
        (JobStatus.COMPLETED, JobStatus.FAILED),
        (JobStatus.CANCELLED, JobStatus.PENDING),
        (JobStatus.DEAD, JobStatus.RUNNING),
    ]

    for current, new in forbidden_transitions:
        assert not can_transition(current, new), (
            f"{current.value} -> {new.value} should be forbidden"
        )


def test_allowed_transitions_are_correct():
    expected = {
        JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.CANCELLED},
        JobStatus.RUNNING: {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.DEAD,
            JobStatus.CANCELLED,
        },
        JobStatus.FAILED: {JobStatus.PENDING, JobStatus.CANCELLED, JobStatus.DEAD},
        JobStatus.COMPLETED: set(),
        JobStatus.CANCELLED: set(),
        JobStatus.DEAD: {JobStatus.PENDING},
    }

    for status, expected_next_states in expected.items():
        assert ALLOWED[status] == expected_next_states
