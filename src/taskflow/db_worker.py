"""Database-backed worker: claim → execute → report."""

from __future__ import annotations

import socket
import time
import uuid

import taskflow.handlers  # noqa: F401  # register built-in handlers

from taskflow.config import get_settings
from taskflow.db import make_engine, make_session_factory
from taskflow.errors import PermanentError, UnknownTask
from taskflow.executor import execute_in_process
from taskflow.service import claim_job, complete_job, fail_job, recover_expired_leases
from taskflow.tasks import get_task


def _make_worker_id() -> str:
    return f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"


def process_one(
    session_factory,
    *,
    worker_id: str,
    lease_seconds: int = 30,
    use_timeout: bool = True,
) -> bool:
    """Claim and run one job. Returns True if a job was processed."""
    with session_factory() as session:
        job = claim_job(session, worker_id=worker_id, lease_seconds=lease_seconds)

    if job is None:
        return False

    timeout = float(job.timeout_seconds) if use_timeout else None

    try:
        if timeout is None:
            handler = get_task(job.task_name)
            result = handler(job.payload)
        else:
            result = execute_in_process(job.task_name, job.payload, timeout)

        stored = result if isinstance(result, dict) else {"value": result}

        with session_factory() as session:
            complete_job(session, job.id, worker_id=worker_id, result=stored)

    except (PermanentError, UnknownTask) as exc:
        with session_factory() as session:
            fail_job(
                session,
                job.id,
                worker_id=worker_id,
                error=str(exc),
                permanent=True,
            )
    except Exception as exc:
        with session_factory() as session:
            fail_job(
                session,
                job.id,
                worker_id=worker_id,
                error=str(exc),
                permanent=False,
            )

    return True


def run_worker(
    *,
    poll_interval: float = 1.0,
    maintenance_interval: float = 5.0,
    lease_seconds: int = 30,
) -> None:
    """Polling loop with periodic lease recovery. Ctrl+C to stop."""
    settings = get_settings()
    engine = make_engine(settings)
    session_factory = make_session_factory(engine)
    worker_id = _make_worker_id()
    print(f"worker {worker_id} started")

    last_maintenance = 0.0

    try:
        while True:
            now = time.monotonic()
            if now - last_maintenance >= maintenance_interval:
                with session_factory() as session:
                    n = recover_expired_leases(session)
                if n:
                    print(f"recovered {n} expired lease(s)")
                last_maintenance = now

            worked = process_one(
                session_factory,
                worker_id=worker_id,
                lease_seconds=lease_seconds,
            )
            if not worked:
                time.sleep(poll_interval)
    except KeyboardInterrupt:
        print(f"worker {worker_id} stopped")


if __name__ == "__main__":
    run_worker()