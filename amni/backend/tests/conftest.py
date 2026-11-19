"""Integration tests use a disposable PostgreSQL database, not AMNI tables."""
from pathlib import Path
import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.database import create_database_engine

BACKEND = Path(__file__).resolve().parents[1]


def migration_config(connection):
    config = Config(str(BACKEND / "alembic.ini"))
    config.attributes["connection"] = connection
    return config


@pytest.fixture(scope="session")
def database_engine():
    if os.environ.get("AMNI_RUN_DB_TESTS") != "1":
        pytest.skip("Set AMNI_RUN_DB_TESTS=1 to run disposable PostgreSQL tests.")
    settings = get_settings()
    name = "amni_test_" + uuid4().hex
    admin = create_engine(settings.database_url, isolation_level="AUTOCOMMIT", poolclass=NullPool,
                          connect_args={"connect_timeout": 5}, hide_parameters=True)
    created = False
    engine = None
    try:
        with admin.connect() as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{name}"')
        created = True
        engine = create_database_engine(settings.model_copy(update={"postgres_db": name}))
        with engine.connect() as connection:
            command.upgrade(migration_config(connection), "head")
        yield engine
    finally:
        if engine is not None:
            engine.dispose()
        if created:
            with admin.connect() as connection:
                connection.exec_driver_sql(f'DROP DATABASE "{name}" WITH (FORCE)')
        admin.dispose()


@pytest.fixture
def db(database_engine):
    with Session(database_engine) as session:
        try:
            yield session
        finally:
            session.rollback()


@pytest.fixture
def actors(db):
    from types import SimpleNamespace
    from sqlalchemy import select
    from app.models import IssueCategory, User
    people = {}
    for label, role in [("customer", "requester"), ("other_customer", "requester"),
                        ("admin", "admin"), ("engineer", "engineer"), ("other_engineer", "engineer")]:
        people[label] = User(display_name=label, email=label + "@example.test", password_hash="example-hash", role=role)
    db.add_all(people.values())
    db.flush()
    people["category"] = db.scalar(select(IssueCategory).where(IssueCategory.slug == "networking"))
    return SimpleNamespace(**people)


@pytest.fixture
def recorded_case(db, actors):
    from app.models import Case
    row = Case(customer_id=actors.customer.id, category_id=actors.category.id,
               title="Connection problem", description="An example system cannot connect.")
    db.add(row)
    db.flush()
    return row


@pytest.fixture
def assignment(db, actors, recorded_case):
    from app.models import CaseAssignment
    row = CaseAssignment(case_id=recorded_case.id, engineer_id=actors.engineer.id, assigned_by_id=actors.admin.id)
    db.add(row)
    db.flush()
    return row
