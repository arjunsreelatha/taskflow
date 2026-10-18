import importlib

from taskflow import handlers, tasks
from taskflow.job import Job
from taskflow.states import JobStatus
from taskflow.tasks import get_task
from taskflow.worker import execute_job


def test_execute_job_runs_registered_handler():
    tasks.registry.clear()
    importlib.reload(handlers)

    job = Job(id="job-001", task_name="example")

    assert get_task("example") is handlers.example_handler

    result = execute_job(job)

    assert result == "success"
    assert job.status == JobStatus.COMPLETED
