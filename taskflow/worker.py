
from collections.abc import Callable
from typing import TypeVar

from taskflow.job import Job
from taskflow.states import JobStatus

T = TypeVar("T")


def execute_job(job: Job, task: Callable[[], T]) -> T:
    """Execute a task and update the job's status."""
    job.transition_to(JobStatus.RUNNING)
    
    try:
        result = task()
    except Exception:
        job.increase_retires()
        job.transition_to(JobStatus.FAILED)
        raise

    job.transition_to(JobStatus.COMPLETED)
    return result
