"""Small, lazy connection pool and explicit application transaction boundaries."""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings


def create_database_engine(settings: Settings | None = None) -> Engine:
    selected = settings if settings is not None else get_settings()
    return create_engine(
        selected.database_url,
        pool_size=3,
        max_overflow=2,
        pool_timeout=5,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
        hide_parameters=True,
    )


@lru_cache
def get_engine() -> Engine:
    return create_database_engine()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Commit a successful unit of work; roll back if it raises an exception."""
    with Session(get_engine(), expire_on_commit=False) as session:
        with session.begin():
            yield session
