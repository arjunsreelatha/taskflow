"""Database operations for jobs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.errors import JobNotFound
from taskflow.models import Job, JobEvent
from taskflow.states import JobStatus


def utcnow() -> datetime:
    return datetime.now(UTC)


def create_job(
    session: Session,
    *,
    task_name: str,
    payload: dict[str, Any] | None = None,
    max_attempts: int = 3,
    timeout_seconds: int = 300,
    priority: int = 5,
    idempotency_key: str | None = None,
    run_at: datetime | None = None,
) -> Job:
    """Insert a new job and record the initial status event."""
    now = utcnow()
    job = Job(
        id=uuid.uuid4(),
        task_name=task_name,
        payload=payload or {},
        status=JobStatus.PENDING.value,
        priority=priority,
        attempts=0,
        max_attempts=max_attempts,
        timeout_seconds=timeout_seconds,
        run_at=run_at or now,
        idempotency_key=idempotency_key,
        cancel_requested=False,
        created_at=now,
        updated_at=now,
    )
    session.add(job)
    session.flush()  # get job.id before event

    session.add(
        JobEvent(
            job_id=job.id,
            from_status=None,
            to_status=JobStatus.PENDING.value,
            at=now,
            note="created",
        )
    )
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: uuid.UUID) -> Job:
    job = session.get(Job, job_id)
    if job is None:
        raise JobNotFound(f"job {job_id} not found")
    return job


def list_jobs(
    session: Session,
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[Job]:
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
    if status is not None:
        stmt = stmt.where(Job.status == status)
    return list(session.scalars(stmt).all())