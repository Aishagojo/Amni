import pytest
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from app.models import CaseEvent

pytestmark = pytest.mark.integration


def event(actors, recorded_case, **changes):
    values = dict(case_id=recorded_case.id, actor_id=actors.admin.id, event_type="assigned")
    values.update(changes)
    return CaseEvent(**values)


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_case_timeline_is_append_only(db, actors, recorded_case, operation):
    row = event(actors, recorded_case)
    db.add(row)
    db.flush()
    statement = update(CaseEvent).where(CaseEvent.id == row.id).values(details={"changed": True}) if operation == "update" else delete(CaseEvent).where(CaseEvent.id == row.id)
    with pytest.raises(IntegrityError):
        db.execute(statement)


@pytest.mark.parametrize("changes", [{"event_type": "unknown"}, {"visibility": "everyone"}, {"details": []}])
def test_invalid_events_are_rejected(db, actors, recorded_case, changes):
    db.add(event(actors, recorded_case, **changes))
    with pytest.raises(IntegrityError):
        db.flush()
