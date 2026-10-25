"""Engine and session factory. One engine per process; sessions are short-lived."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from taskflow.config import Settings


def make_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    # expire_on_commit=False lets us read attributes after commit
    # without triggering a surprise lazy-load.
    return sessionmaker(engine, expire_on_commit=False)