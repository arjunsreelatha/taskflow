# TaskFlow

TaskFlow is a Python-based task queue project designed to explore how background jobs are managed, validated, and executed reliably.

The project is being developed incrementally, with a focus on clean code, automated testing, and reliable job state management.

## Current Features

- Job status definitions using Python enums.
- Validation of allowed job state transitions.
- Custom exceptions for TaskFlow domain errors.
- Automated tests using pytest.

## Job States

TaskFlow currently defines six job statuses:

| Status | Meaning |
|---|---|
| `PENDING` | Waiting to be processed |
| `RUNNING` | Currently being processed |
| `COMPLETED` | Finished successfully |
| `FAILED` | An execution attempt failed |
| `DEAD` | Stopped after retries are exhausted or a permanent error occurs |
| `CANCELLED` | Cancelled |

The state machine defines which transitions are allowed and rejects invalid transitions.

## Project Structure

taskflow/
    __init__.py
    errors.py
    job.py
    states.py

tests/
    test_job.py
    test_states.py

## Requirements

- Python 3.11 or newer
- pytest

Python 3.11 or newer is required because the project uses `enum.StrEnum`.

## Run the Tests

Install pytest:

```bash
python -m pip install pytest
```

Run the test suite from the repository root:

```bash
python -m pytest -v
```

## Development Status

TaskFlow is a work in progress. The current focus is job state management, exception handling, and automated testing. Additional queue, worker, storage, and deployment capabilities may be added as development continues.

## Goals

- Build a reliable background task queue.
- Practice Python software engineering and testing.
- Explore asynchronous job execution and retry handling.
- Add persistence and deployment capabilities incrementally.
