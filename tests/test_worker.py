import pytest

from taskflow.job import Job
from taskflow.states import JobStatus
from taskflow.worker import execute_job


def test_execute_job_success():
    job = Job(id=" job-001", task_name="send_email")

    def task():
        return "Email sent"

    result = execute_job(job, task)

    assert result == "Email sent"
    assert job.status == JobStatus.COMPLETED


def test_execute_job_failure():
    job = Job(id="job-002", task_name="process_file")

    def task():
        raise RuntimeError("Processing failed")

    with pytest.raises(RuntimeError, match="Processing failed"):
        execute_job(job, task)

    assert job.status == JobStatus.DEAD


def test_execute_job_retries_after_failure():
    job = Job(id="job-003", task_name="send_email")
    attempts = 0

    def task():
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise RuntimeError("Temporary failure")

        return "processed"

    result = execute_job(job, task)
    assert result == "processed"
    assert attempts == 2
    assert job.status == JobStatus.COMPLETED
