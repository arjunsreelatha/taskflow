import pytest

from src.taskflow.errors import DuplicateTask, UnknownTask
from src.taskflow.tasks import get_task, task


@pytest.fixture(autouse=True)
def clean_registry():
    from taskflow import tasks

    tasks.regitry.clear()
    yield
    tasks.regitry.clear()

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
