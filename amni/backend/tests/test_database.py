from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import delete, func, inspect, select, text
from sqlalchemy.exc import IntegrityError

from app.models import Base, Case, IssueCategory, User, UserSession
from conftest import BACKEND, migration_config

pytestmark = pytest.mark.integration


def customer(db):
    row = User(display_name="Example requester", email="requester@example.test", password_hash="example-hash")
    db.add(row)
    db.flush()
    return row


def case(db, **changes):
    owner = customer(db)
    category = db.scalar(select(IssueCategory).where(IssueCategory.slug == "networking"))
    row = Case(customer_id=owner.id, category_id=category.id, title="Connection failure",
               description="The example endpoint is unreachable.")
    for key, value in changes.items():
        setattr(row, key, value)
    db.add(row)
    return row


def test_initial_migration_and_categories(db):
    assert {"users", "sessions", "issue_categories", "cases", "alembic_version"}.issubset(inspect(db.bind).get_table_names())
    assert set(db.scalars(select(IssueCategory.slug))) == {"networking", "linux-docker", "application", "security", "other"}
    assert db.scalar(text("SELECT version_num FROM alembic_version")) == ScriptDirectory.from_config(Config(str(BACKEND / "alembic.ini"))).get_current_head()
    assert compare_metadata(MigrationContext.configure(db.connection(), opts={"compare_server_default": True}), Base.metadata) == []


def test_case_defaults_and_unique_reference(db):
    row = case(db)
    db.flush()
    assert row.id is not None and row.reference.startswith("AMNI-")
    assert row.status == "open" and row.priority == "medium"
    assert row.created_at.tzinfo is not None and row.customer.role == "requester"
    second = Case(customer_id=row.customer_id, category_id=row.category_id, title="Another issue", description="Another example.")
    db.add(second)
    db.flush()
    assert row.reference != second.reference


def test_email_uniqueness_is_case_insensitive(db):
    customer(db)
    db.add(User(display_name="Duplicate", email="REQUESTER@example.test", password_hash="example-hash"))
    with pytest.raises(IntegrityError):
        db.flush()


@pytest.mark.parametrize("field,value", [
    ("status", "unknown"), ("priority", "unknown"), ("title", "   "), ("description", "   "),
    ("status", "resolved"), ("resolved_at", datetime.now(UTC)),
    ("customer_id", uuid4()), ("category_id", uuid4()),
])
def test_case_rejects_invalid_state_and_missing_references(db, field, value):
    case(db, **{field: value})
    with pytest.raises(IntegrityError):
        db.flush()


def test_case_cannot_reference_itself(db):
    row = case(db)
    db.flush()
    row.related_case_id = row.id
    with pytest.raises(IntegrityError):
        db.flush()


def test_resolved_case_retains_record_and_timestamp(db):
    row = case(db)
    db.flush()
    row.status, row.resolved_at = "resolved", datetime.now(UTC)
    db.flush()
    db.expire(row)
    assert row.status == "resolved" and row.resolved_at is not None


def test_case_owner_cannot_be_deleted(db):
    row = case(db)
    db.flush()
    with pytest.raises(IntegrityError):
        db.execute(delete(User).where(User.id == row.customer_id))


def test_unknown_role_is_rejected(db):
    db.add(User(display_name="Example", email="role@example.test", password_hash="example-hash", role="owner"))
    with pytest.raises(IntegrityError):
        db.flush()


@pytest.mark.parametrize("changes", [
    {"token_hash": "raw-session-token"}, {"expires_at": datetime(2000, 1, 1, tzinfo=UTC)},
    {"revoked_at": datetime(2000, 1, 1, tzinfo=UTC)},
])
def test_session_rejects_invalid_hash_and_dates(db, changes):
    owner = customer(db)
    values = dict(user_id=owner.id, token_hash="a" * 64, expires_at=datetime.now(UTC) + timedelta(hours=1))
    values.update(changes)
    db.add(UserSession(**values))
    with pytest.raises(IntegrityError):
        db.flush()


def test_duplicate_session_hash_is_rejected(db):
    owner = customer(db)
    for _ in range(2):
        db.add(UserSession(user_id=owner.id, token_hash="b" * 64, expires_at=datetime.now(UTC) + timedelta(hours=1)))
    with pytest.raises(IntegrityError):
        db.flush()


def test_user_deletion_removes_sessions(db):
    owner = customer(db)
    db.add(UserSession(user_id=owner.id, token_hash="c" * 64, expires_at=datetime.now(UTC) + timedelta(hours=1)))
    db.flush()
    db.execute(delete(User).where(User.id == owner.id))
    assert db.scalar(select(func.count()).select_from(UserSession)) == 0


def test_migration_repeatability_and_round_trip(database_engine):
    with database_engine.connect() as connection:
        config = migration_config(connection)
        command.upgrade(config, "head")
        assert connection.scalar(text("SELECT count(*) FROM issue_categories")) == 5
        connection.commit()

        command.downgrade(config, "base")
        assert set(inspect(connection).get_table_names()) == {"alembic_version"}
        connection.commit()
        command.upgrade(config, "head")
        assert set(inspect(connection).get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
        assert connection.scalar(text("SELECT count(*) FROM issue_categories")) == 5
        connection.commit()


def test_upgrade_preserves_existing_customer_and_case(database_engine):
    # Only the disposable test database is downgraded. Commit real baseline rows
    # so the upgrade proves existing data survives, rather than just empty DDL.
    owner_id, case_id = uuid4(), uuid4()
    with database_engine.connect() as connection:
        config = migration_config(connection)
        command.downgrade(config, "0001_accounts_categories_cases")
        connection.execute(text("""
            INSERT INTO users (id, display_name, email, password_hash)
            VALUES (:id, 'Existing customer', 'migration@example.test', 'example-hash')
        """), {"id": owner_id})
        connection.execute(text("""
            INSERT INTO cases (id, customer_id, category_id, title, description)
            SELECT :id, :owner, id, 'Existing case', 'Preserve this investigation'
            FROM issue_categories WHERE slug = 'networking'
        """), {"id": case_id, "owner": owner_id})
        original_number = connection.scalar(text("SELECT case_number FROM cases WHERE id = :id"), {"id": case_id})
        connection.commit()
        try:
            command.upgrade(config, "head")
            assert connection.scalar(text("SELECT case_number FROM cases WHERE id = :id"), {"id": case_id}) == original_number
            assert connection.scalar(text("SELECT title FROM cases WHERE id = :id"), {"id": case_id}) == "Existing case"
            assert connection.scalar(text("SELECT email FROM users WHERE id = :id"), {"id": owner_id}) == "migration@example.test"
            connection.commit()
        finally:
            connection.rollback()
            connection.execute(text("DELETE FROM cases WHERE id = :id"), {"id": case_id})
            connection.execute(text("DELETE FROM users WHERE id = :id"), {"id": owner_id})
            connection.commit()
