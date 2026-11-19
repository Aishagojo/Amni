from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Case, CaseEvent, Notification

pytestmark = pytest.mark.integration


def make_event(db, actors, recorded_case):
    row = CaseEvent(case_id=recorded_case.id, actor_id=actors.customer.id, event_type="created", visibility="customer")
    db.add(row)
    db.flush()
    return row


def notification(actors, recorded_case, event, **changes):
    values = dict(recipient_id=actors.admin.id, case_id=recorded_case.id, event_id=event.id,
                  kind="case_created", message="New support case.")
    values.update(changes)
    return Notification(**values)


def test_event_is_not_duplicated_for_the_same_recipient(db, actors, recorded_case):
    event = make_event(db, actors, recorded_case)
    db.add_all([notification(actors, recorded_case, event), notification(actors, recorded_case, event)])
    with pytest.raises(IntegrityError):
        db.flush()


def test_notification_must_reference_its_events_case(db, actors, recorded_case):
    event = make_event(db, actors, recorded_case)
    other = Case(customer_id=actors.customer.id, category_id=actors.category.id, title="Other issue", description="Other case.")
    db.add(other)
    db.flush()
    db.add(notification(actors, recorded_case, event, case_id=other.id))
    with pytest.raises(IntegrityError):
        db.flush()


@pytest.mark.parametrize("changes", [{"message": " "}, {"kind": "unknown"}, {"read_at": datetime(2000, 1, 1, tzinfo=UTC)}])
def test_invalid_notifications_are_rejected(db, actors, recorded_case, changes):
    event = make_event(db, actors, recorded_case)
    db.add(notification(actors, recorded_case, event, **changes))
    with pytest.raises(IntegrityError):
        db.flush()
