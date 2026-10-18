import pytest

from taskflow import tasks
from taskflow.errors import DuplicateTask, UnknownTask
from taskflow.tasks import get_task, task


@pytest.fixture(autouse=True)
def clean_registry():

    tasks.registry.clear()
    yield
    tasks.registry.clear()


def test_register_task():
    def sample_task():
        return "success"

    task("sample")(sample_task)

    assert get_task("sample") is sample_task


def test_unknown_task():
    with pytest.raises(UnknownTask):
        get_task("unknown_task")


def test_duplicate_task_registration():
    def sample_task():
        return "success"

    task("sample")(sample_task)

    with pytest.raises(DuplicateTask):
        task("sample")(sample_task)


def test_decorated_functions_works_driectly():
    @task("sample")
    def sample_task():
        return "success"

    assert get_task("sample") is sample_task
    assert sample_task() == "success"
