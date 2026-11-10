"""Database operations for jobs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from taskflow.errors import JobNotFound
from taskflow.models import Job, JobAttempt, JobEvent
from taskflow.states import JobStatus, assert_transition


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
    session.flush()

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


def _transition(
    session: Session,
    job: Job,
    new: JobStatus,
    now: datetime,
    note: str | None = None,
) -> None:
    old = JobStatus(job.status)
    assert_transition(old, new)
    job.status = new.value
    job.updated_at = now
    session.add(
        JobEvent(
            job_id=job.id,
            from_status=old.value,
            to_status=new.value,
            at=now,
            note=note,
        )
    )


def claim_job(
    session: Session,
    *,
    worker_id: str,
    lease_seconds: int = 30,
) -> Job | None:
    """
    Atomically claim one due job for this worker.

    Uses FOR UPDATE SKIP LOCKED so multiple workers never take the same row.
    """
    now = utcnow()

    # Pick one claimable job that is due
    stmt = (
        select(Job)
        .where(
            Job.status.in_([JobStatus.PENDING.value, JobStatus.FAILED.value]),
            Job.run_at <= now,
        )
        .order_by(Job.priority.desc(), Job.run_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = session.scalars(stmt).first()
    if job is None:
        return None

    # Move to running and set lease
    job.attempts += 1
    job.locked_by = worker_id
    job.lease_expires_at = now + timedelta(seconds=lease_seconds)
    job.started_at = now
    _transition(session, job, JobStatus.RUNNING, now, f"claimed by {worker_id}")

    # Record this attempt
    session.add(
        JobAttempt(
            job_id=job.id,
            attempt_number=job.attempts,
            worker_id=worker_id,
            started_at=now,
        )
    )
    session.commit()
    session.refresh(job)
    return job


def complete_job(
    session: Session,
    job_id: uuid.UUID,
    *,
    worker_id: str,
    result: dict[str, Any] | None,
) -> Job:
    """Mark a running job as completed. Only the claiming worker may do this."""
    now = utcnow()
    job = session.scalars(
        select(Job).where(Job.id == job_id).with_for_update()
    ).first()
    if job is None:
        raise JobNotFound(f"job {job_id} not found")

    if job.status != JobStatus.RUNNING.value or job.locked_by != worker_id:
        raise JobNotFound(f"job {job_id} is not owned by {worker_id}")

    job.result = result
    job.last_error = None
    job.finished_at = now
    job.locked_by = None
    job.lease_expires_at = None

    # Close the attempt row
    attempt = session.scalars(
        select(JobAttempt).where(
            JobAttempt.job_id == job.id,
            JobAttempt.attempt_number == job.attempts,
        )
    ).first()
    if attempt is not None:
        attempt.finished_at = now
        attempt.outcome = "success"

    _transition(session, job, JobStatus.COMPLETED, now, "handler succeeded")
    session.commit()
    session.refresh(job)
    return job


def fail_job(
    session: Session,
    job_id: uuid.UUID,
    *,
    worker_id: str,
    error: str,
    permanent: bool = False,
    backoff_seconds: float = 2.0,
) -> Job:
    """
    Record a failed attempt.
    Retry (status=failed, run_at in the future) or dead-letter.
    """
    now = utcnow()
    job = session.scalars(
        select(Job).where(Job.id == job_id).with_for_update()
    ).first()
    if job is None:
        raise JobNotFound(f"job {job_id} not found")

    if job.status != JobStatus.RUNNING.value or job.locked_by != worker_id:
        raise JobNotFound(f"job {job_id} is not owned by {worker_id}")

    job.last_error = error
    job.locked_by = None
    job.lease_expires_at = None

    attempt = session.scalars(
        select(JobAttempt).where(
            JobAttempt.job_id == job.id,
            JobAttempt.attempt_number == job.attempts,
        )
    ).first()
    if attempt is not None:
        attempt.finished_at = now
        attempt.outcome = "error"
        attempt.error = error

    if permanent or job.attempts >= job.max_attempts:
        job.finished_at = now
        _transition(session, job, JobStatus.DEAD, now, f"dead: {error}")
    else:
        # Simple fixed backoff for Day 4 (exponential comes later)
        job.run_at = now + timedelta(seconds=backoff_seconds * job.attempts)
        _transition(
            session,
            job,
            JobStatus.FAILED,
            now,
            f"retry at {job.run_at.isoformat()}: {error}",
        )

    session.commit()
    session.refresh(job)
    return job