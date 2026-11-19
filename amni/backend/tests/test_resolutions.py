import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from app.models import Case, CaseAssignment, CaseResolution

pytestmark = pytest.mark.integration


def resolution(actors, recorded_case, assignment, **changes):
    values = dict(case_id=recorded_case.id, assignment_id=assignment.id, resolved_by_id=actors.engineer.id,
                  root_cause="Expired TLS certificate", fix_summary="Renewed the certificate",
                  customer_summary="Your secure connection works again.")
    values.update(changes)
    return CaseResolution(**values)


def test_resolution_search_matches_saved_cause_and_fix(db, actors, recorded_case, assignment):
    row = resolution(actors, recorded_case, assignment)
    db.add(row)
    db.flush()
    found = list(db.scalars(select(CaseResolution).where(CaseResolution.search_document.match("certificate", postgresql_regconfig="english"))))
    assert found == [row]


def test_resolver_must_match_the_assignment_engineer(db, actors, recorded_case, assignment):
    db.add(resolution(actors, recorded_case, assignment, resolved_by_id=actors.other_engineer.id))
    with pytest.raises(IntegrityError):
        db.flush()


def test_resolution_cannot_use_another_cases_assignment(db, actors, recorded_case, assignment):
    other = Case(customer_id=actors.customer.id, category_id=actors.category.id, title="Another issue", description="Another case.")
    db.add(other)
    db.flush()
    db.add(resolution(actors, recorded_case, assignment, case_id=other.id))
    with pytest.raises(IntegrityError):
        db.flush()


@pytest.mark.parametrize("field", ["root_cause", "fix_summary", "customer_summary", "prevention_notes"])
def test_resolution_fields_cannot_be_blank(db, actors, recorded_case, assignment, field):
    db.add(resolution(actors, recorded_case, assignment, **{field: "  "}))
    with pytest.raises(IntegrityError):
        db.flush()


def test_assignment_referenced_by_resolution_cannot_be_deleted(db, actors, recorded_case, assignment):
    db.add(resolution(actors, recorded_case, assignment))
    db.flush()
    with pytest.raises(IntegrityError):
        db.execute(delete(CaseAssignment).where(CaseAssignment.id == assignment.id))
