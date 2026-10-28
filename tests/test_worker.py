from typing import Any

from taskflow.errors import PermanentError
from taskflow.executor import execute_in_process
from taskflow.job import Job
from taskflow.states import JobStatus
from taskflow.tasks import get_task


def execute_job(
    job: Job,
    timeout: float | None = None,
) -> Any:
    """Execute a task with a configurable maximum number of attempts."""
    max_attempts = job.max_attempts

    for attempt in range(max_attempts):
        job.transition_to(JobStatus.RUNNING)

        try:
            if timeout is None:
                handler = get_task(job.task_name)
                result = handler(job.payload)
            else:
                result = execute_in_process(
                    job.task_name,
                    job.payload,
                    timeout,
                )

        except PermanentError as exc:
            job.increase_retries()
            job.last_error = str(exc)
            job.transition_to(JobStatus.DEAD)
            raise

        except Exception as exc:
            job.increase_retries()
            job.last_error = str(exc)
            job.transition_to(JobStatus.FAILED)

            if attempt == max_attempts - 1:
                job.transition_to(JobStatus.DEAD)
                raise

            job.transition_to(JobStatus.PENDING)

        else:
            # Store a JSON-friendly result on the job
            if isinstance(result, dict):
                job.result = result
            else:
                job.result = {"value": result}

            job.transition_to(JobStatus.COMPLETED)
            return result