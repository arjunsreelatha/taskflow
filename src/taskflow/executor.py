import multiprocessing
from typing import Any

from taskflow.errors import (
    DuplicateTask,
    IdempotencyConflict,
    InvalidTransition,
    JobNotFound,
    PermanentError,
    TaskFlowError,
    UnknownTask,
)
from taskflow.tasks import get_task


TASKFLOW_ERRORS: dict[str, type[TaskFlowError]] = {
    error.__name__: error
    for error in (
        DuplicateTask,
        IdempotencyConflict,
        InvalidTransition,
        JobNotFound,
        PermanentError,
        UnknownTask,
    )
}


def _run_handler(task_name, payload, result_queue):
    try:
        handler = get_task(task_name)
        result = handler(payload)
        result_queue.put(("success", result))
    except Exception as exc:
        result_queue.put(
            (
                "error",
                type(exc).__module__,
                type(exc).__name__,
                str(exc),
            )
        )


def execute_in_process(
    task_name: str,
    payload: dict[str, Any],
    timeout: float,
) -> Any:
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue()

    process = context.Process(
        target=_run_handler,
        args=(task_name, payload, result_queue),
    )

    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        result_queue.close()
        result_queue.join_thread()
        raise TimeoutError("Task execution timed out")

    try:
        result = result_queue.get(timeout=1)
    except Exception as exc:
        raise RuntimeError("Task process exited without returning a result") from exc
    finally:
        result_queue.close()

    if result[0] == "success":
        return result[1]

    _, module, name, message = result

    if module == "taskflow.errors" and name in TASKFLOW_ERRORS:
        raise TASKFLOW_ERRORS[name](message)

    raise RuntimeError(f"{name}: {message}")
