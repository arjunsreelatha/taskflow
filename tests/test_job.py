import pytest
from pydantic import ValidationError

from taskflow.errors import InvalidTransition
from taskflow.job import Job, create_job
from taskflow.states import JobStatus


def test_create_Job():
    job_id = "job-001"
    task = "send_email"

    job = create_job(job_id, task)

    assert job.id == job_id
    assert job.task_name == task
    assert job.status == JobStatus.PENDING
    assert job.retries == 0


def test_create_job_rejects_empty_task_name():
    with pytest.raises(ValidationError):
        create_job("job-002", "")


def test_Job_rejects_empty_id():
    with pytest.raises(ValidationError):
        Job(id="", task_name="send_email")


def test_Job_rejects_negative_retries():
    with pytest.raises(ValidationError):
        Job(
            id="job-003",
            task_name="send_email",
            retries=-1,
        )


def test_Job_rejects_whitespace_only_task_name():
    with pytest.raises(ValidationError):
        Job(id="job-004", task_name="   ")


def test_task_name_is_stripped():
    job = Job(id="1", task_name="  send_email  ")
    assert job.task_name == "send_email"


def test_negative_retries_rejected_on_assignment():
    job = Job(id="1", task_name="send_email")

    with pytest.raises(ValidationError):
        job.retries = -5


def test_invalid_transition_rejected():
    job = Job(id="1", task_name="send_email")

    with pytest.raises(InvalidTransition):
        job.transition_to(JobStatus.COMPLETED)


def test_direct_status_assignment_rejected():
    job = Job(id="1", task_name="send_email")

    with pytest.raises(InvalidTransition):
        job.status = JobStatus.COMPLETED
