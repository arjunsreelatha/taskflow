# TaskFlow

TaskFlow is a Python task queue built step by step to learn how background jobs are validated, executed, retried and tracked reliably. It is a work in progress: the core job lifecycle runs in memory today, and persistence, concurrency and an API are planned.

## What works today

- **Jobs:** a validated `Job` model (id, task name, status, retry count, `max_attempts`) with JSON serialization.
- **State machine:** six statuses with enforced transitions. Invalid changes raise `InvalidTransition`, including direct assignment to `job.status`.
- **Task registry:** register handlers by name with the `@task("name")` decorator and look them up with `get_task`.
- **Worker:** `execute_job(job)` finds the job's handler, runs it, and retries failures up to `max_attempts`.
- **Failure handling:** `PermanentError` and `UnknownTask` skip retries and send the job straight to `DEAD`.
- **Tests and tooling:** pytest suite, with Ruff for linting and formatting.

## Job lifecycle

| Status | Meaning |
|---|---|
| `PENDING` | Waiting to run |
| `RUNNING` | Being executed |
| `COMPLETED` | Finished successfully |
| `FAILED` | An attempt failed; the job will retry or die |
| `DEAD` | Attempts exhausted, or a permanent error occurred |
| `CANCELLED` | Cancelled |

Allowed transitions:

```text
PENDING -> RUNNING, CANCELLED
RUNNING -> COMPLETED, FAILED, DEAD, CANCELLED
FAILED  -> PENDING (retry), DEAD, CANCELLED
DEAD    -> PENDING (manual requeue)
COMPLETED, CANCELLED: terminal
```

## Usage

Register a handler, create a job with the same task name, and execute it:

```python
from taskflow.job import create_job
from taskflow.tasks import task
from taskflow.worker import execute_job


@task("send_email")
def send_email():
    return "sent"


job = create_job("job-001", "send_email")
print(execute_job(job))  # "sent"
print(job.status)        # completed
```

Failure rules:

- Any normal exception is retried until `max_attempts` is reached, then the job is `DEAD` and the exception is re-raised.
- Raise `PermanentError` in a handler to fail without retrying.
- A job whose `task_name` is not registered fails permanently with `UnknownTask`.
- Registering two handlers under the same name raises `DuplicateTask`.

## Project structure

```text
src/taskflow/
    errors.py     domain exceptions
    states.py     JobStatus and allowed transitions
    job.py        Job model and create_job
    tasks.py      @task decorator and registry
    handlers.py   built-in example handler
    worker.py     execute_job (retry logic)
tests/
    test_states.py  test_job.py  test_tasks.py
    test_handlers.py  test_worker.py
```

## Getting started

Requires Python 3.11 or newer.

```bash
git clone https://github.com/arjunsreelatha/taskflow.git
cd taskflow
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run the checks before committing:

```bash
pytest -q
ruff check .
ruff format .
```

## Roadmap

- [x] Job states, validation and transitions
- [x] Retries, `max_attempts`, permanent errors
- [x] Task registry
- [ ] Handler payloads (pass job data to handlers)
- [ ] Run handlers in a child process with timeouts
- [ ] REST API (FastAPI)
- [ ] PostgreSQL persistence and migrations
- [ ] Safe job claiming for multiple workers
- [ ] Retry backoff and idempotency keys
- [ ] Docker, CI and deployment