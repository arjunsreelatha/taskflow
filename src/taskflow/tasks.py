from collections.abc import Callable
from typing import Any

from taskflow.errors import DuplicateTask, UnknownTask

registry: dict[str, Callable[..., Any]] = {}


def task(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if name in registry:
            raise DuplicateTask(f"Task '{name}' is already registered")

        registry[name] = func
        return func

    return decorator


def get_task(name: str) -> Callable[..., Any]:
    try:
        return registry[name]
    except KeyError:
        raise UnknownTask(f"Task '{name}' is not registered") from None
