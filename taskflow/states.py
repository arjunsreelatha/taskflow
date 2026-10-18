from enum import StrEnum

from .errors import InvalidTransition


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"
    CANCELLED = "cancelled"


ALLOWED: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.PENDING: frozenset({
        JobStatus.RUNNING,
        JobStatus.CANCELLED,
    }),
    JobStatus.RUNNING: frozenset({
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.DEAD,
        JobStatus.CANCELLED,
    }),
    JobStatus.FAILED: frozenset({
        JobStatus.PENDING,
        JobStatus.CANCELLED,
        JobStatus.DEAD,
    }),
    JobStatus.COMPLETED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
    JobStatus.DEAD: frozenset({
        JobStatus.PENDING,
    }),
}

CLAIMABLE = (JobStatus.PENDING, JobStatus.FAILED)

TERMINAL = frozenset({
    JobStatus.COMPLETED,
    JobStatus.CANCELLED,
    JobStatus.DEAD,
})


def can_transition(
    current: JobStatus,
    new: JobStatus,
) -> bool:
    return new in ALLOWED[current]


def assert_transition(
    current: JobStatus,
    new: JobStatus,
) -> None:
    if not can_transition(current, new):
        raise InvalidTransition(
            f"cannot move job from {current.value} to {new.value}"
        )