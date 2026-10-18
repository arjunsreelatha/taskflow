from collections.abc import Callable
from typing import TypeVar

from taskflow.job import Job
from taskflow.states import JobStatus

T = TypeVar("T")


def execute_job(job: Job, task: Callable[[], T]) -> T:
    """Execute a task and retry up to two times."""
    max_attempts = 3

    for attempt in range(max_attempts):
        job.transition_to(JobStatus.RUNNING)

        try:
            result = task()
        except Exception:
            job.increase_retires()
            job.transition_to(JobStatus.FAILED)

            if attempt == max_attempts - 1:
                job.transition_to(JobStatus.DEAD)
                raise

            job.transition_to(JobStatus.PENDING)
        else:
            job.transition_to(JobStatus.COMPLETED)
            return result

    raise RuntimeError("Task failed after maximum retries")
