from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models import CaseAssignment

pytestmark = pytest.mark.integration


def test_only_one_active_assignment_is_allowed(db, actors, recorded_case, assignment):
    db.add(CaseAssignment(case_id=recorded_case.id, engineer_id=actors.other_engineer.id, assigned_by_id=actors.admin.id))
    with pytest.raises(IntegrityError):
        db.flush()


def test_reassignment_preserves_the_previous_engineer(db, actors, recorded_case, assignment):
    assignment.ended_at = datetime.now(UTC)
    db.flush()
    replacement = CaseAssignment(case_id=recorded_case.id, engineer_id=actors.other_engineer.id,
                                 assigned_by_id=actors.admin.id, assigned_at=datetime.now(UTC))
    db.add(replacement)
    db.flush()
    rows = list(db.scalars(select(CaseAssignment).where(CaseAssignment.case_id == recorded_case.id)))
    assert len(rows) == 2
    assert assignment.ended_at is not None and replacement.ended_at is None
    assert replacement.assigned_by_id == actors.admin.id


@pytest.mark.parametrize("field,value", [("ended_at", datetime(2000, 1, 1, tzinfo=UTC)), ("notes", "   ")])
def test_invalid_assignment_history_is_rejected(db, assignment, field, value):
    setattr(assignment, field, value)
    with pytest.raises(IntegrityError):
        db.flush()
