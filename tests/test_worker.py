import pytest

from taskflow.errors import PermanentError
from taskflow.job import Job
from taskflow.states import JobStatus
from taskflow.worker import execute_job


def test_execute_job_success():
    job = Job(id="job-001", task_name="send_email")

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


def test_job_die_after_max_attempts():
    job = Job(id="job-004", task_name="process_file", max_attempts=2)
    attempts = 0

    def task():
        nonlocal attempts
        attempts += 1
        raise RuntimeError("Processing failed")

    with pytest.raises(RuntimeError, match="Processing failed"):
        execute_job(job, task)
    assert attempts == 2
    assert job.retries == 2
    assert job.status == JobStatus.DEAD


def test_max_attempts_zero_is_rejected():
    with pytest.raises(ValueError):
        Job(id="job-005", task_name="process_file", max_attempts=0)


def test_max_attempts_one_dies_on_first_failure():
    job = Job(id="job-006", task_name="process_file", max_attempts=1)
    attempts = 0

    def task():
        nonlocal attempts
        attempts += 1
        raise RuntimeError("Processing failed")

    with pytest.raises(RuntimeError, match="Processing failed"):
        execute_job(job, task)

    assert attempts == 1
    assert job.retries == 1
    assert job.status == JobStatus.DEAD


def test_permanent_error_skips_retries():
    job = Job(id="job-007", task_name="process_file", max_attempts=3)
    attempts = 0

    def task():
        nonlocal attempts
        attempts += 1
        raise PermanentError("bad input")

    with pytest.raises(PermanentError):
        execute_job(job, task)

    assert attempts == 1
    assert job.status == JobStatus.DEAD

def test_permanent_error_does_not_retry():
    job = Job(id="job-008", task_name="process_file", max_attempts=3)
    attempts = 0

    def task():
        nonlocal attempts
        attempts += 1
        raise PermanentError("bad input")

    with pytest.raises(PermanentError):
        execute_job(job, task)

    assert attempts == 1
    assert job.status == JobStatus.DEAD

def test_permanent_error_after_retry():
    job = Job(id="job-009", task_name="process_file", max_attempts=3)
    attempts = 0

    def task():
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise RuntimeError("temporary failure")

        raise PermanentError("bad input")

    with pytest.raises(PermanentError, match="bad input"):
        execute_job(job, task)

    assert attempts == 2
    assert job.retries == 2
    assert job.status == JobStatus.DEAD