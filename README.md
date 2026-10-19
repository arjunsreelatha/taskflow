# TaskFlow

TaskFlow is a Python-based task queue project focused on reliable background job execution, task registration, job state management, and failure handling.

The project is developed incrementally, emphasizing clean code, type safety, and automated testing.

## Features

- **Job management:** Create jobs with unique IDs, task names, statuses, and configurable retry limits.
- **State management:** Enforce valid job state transitions using Python enums.
- **Task registry:** Register task handlers by name and retrieve them for execution.
- **Worker execution:** Execute registered task handlers through `execute_job`.
- **Automatic retries:** Retry failed tasks up to the configured `max_attempts`.
- **Permanent errors:** Use `PermanentError` for failures that should not be retried.
- **Unknown task handling:** Treat unregistered tasks as permanent failures using `UnknownTask`.
- **Duplicate task detection:** Use `DuplicateTask` for duplicate task registrations.
- **Automated testing:** Validate functionality and error handling with pytest.
- **Code quality:** Use Ruff for formatting and linting.

## Job States

TaskFlow defines six job statuses:

| Status | Description |
|---|---|
| `PENDING` | Waiting to be executed. |
| `RUNNING` | Currently being executed. |
| `COMPLETED` | Executed successfully. |
| `FAILED` | An execution attempt failed, and another attempt may be made. |
| `DEAD` | Execution stopped because attempts were exhausted or a permanent error occurred. |
| `CANCELLED` | The job was cancelled. |

The state machine validates transitions to prevent invalid job state changes.

## Error Handling and Retries

TaskFlow distinguishes between recoverable execution failures and permanent failures.

- **Recoverable errors:** The worker retries the task until it succeeds or reaches `max_attempts`.
- **Permanent errors:** The worker transitions the job to `DEAD` without retrying.
- **Unknown tasks:** If a task name is not registered, the worker treats it as a permanent error.
- **Retry tracking:** Failed attempts are recorded through the job's retry counter.

The `max_attempts` setting controls the maximum number of execution attempts for a job.

## Project Structure

```text
taskflow/
├── __init__.py
├── errors.py
├── job.py
├── states.py
├── tasks.py
└── worker.py

tests/
├── test_job.py
├── test_states.py
├── test_tasks.py
└── test_worker.py
```

The exact files may evolve as the project develops.

## Requirements

- Python 3.11 or newer
- pytest
- Ruff

Python 3.11 or newer is required because the project uses `enum.StrEnum`.

## Setup

Clone the repository:

```bash
git clone https://github.com/arjunsreelatha/taskflow.git
cd taskflow
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the development tools:

```bash
python -m pip install pytest ruff
```

If the project defines its dependencies in `pyproject.toml`, install the project and its development dependencies according to that configuration.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -q
```

Run a specific test module:

```bash
python -m pytest tests/test_worker.py -v
```

## Code Quality

Format the code:

```bash
ruff format .
```

Check for linting issues:

```bash
ruff check .
```

Before committing changes, run formatting, linting, and the full test suite.

## Development Goals

- Build a reliable background task queue.
- Improve task registration and handler execution.
- Strengthen job validation and state transitions.
- Implement robust retry and permanent-failure handling.
- Expand automated test coverage.
- Introduce persistence and deployment capabilities incrementally.

## Project Status

TaskFlow is an ongoing learning and software engineering project. Current development focuses on job lifecycle management, task registry integration, worker execution, retry policies, and test-driven development.
