from collections.abc import Callable
from typing import TypeVar

from taskflow.errors import PermanentError
from taskflow.job import Job
from taskflow.states import JobStatus

T = TypeVar("T")


def execute_job(job: Job, task: Callable[[], T]) -> T:
    """Execute a task with a configurable maximum number of attempts."""
    max_attempts = job.max_attempts

    for attempt in range(max_attempts):
        job.transition_to(JobStatus.RUNNING)

        try:
            result = task()
        except PermanentError:
            job.increase_retries()
            job.transition_to(JobStatus.DEAD)
            raise
        except Exception:
            job.increase_retries()
            job.transition_to(JobStatus.FAILED)

            if attempt == max_attempts - 1:
                job.transition_to(JobStatus.DEAD)
                raise

            job.transition_to(JobStatus.PENDING)
        else:
            job.transition_to(JobStatus.COMPLETED)
            return result


