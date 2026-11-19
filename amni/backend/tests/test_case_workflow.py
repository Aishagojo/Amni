import pytest
from sqlalchemy import func, select

from app.models import Case, CaseAssignment, CaseEvent, CaseResolution, Notification
from app.services.cases import (PermissionDenied, WorkflowError, assign_case, mark_notification_read,
                                reopen_case, resolve_case, search_resolutions, start_case, submit_case)

pytestmark = pytest.mark.integration


def submitted(db, actors, **changes):
    values = dict(customer_id=actors.customer.id, category_id=actors.category.id,
                  title="HTTPS connection fails", description="The secure website does not load.", affected_target="api.example.test")
    values.update(changes)
    return submit_case(db, **values)


def resolved(db, actors):
    case = submitted(db, actors)
    assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.admin.id)
    start_case(db, case_id=case.id, engineer_id=actors.engineer.id)
    result = resolve_case(db, case_id=case.id, engineer_id=actors.engineer.id,
                          root_cause="Expired TLS certificate on the upstream server",
                          fix_summary="Renewed certificate and reloaded the proxy",
                          customer_summary="Your secure connection has been restored.", prevention_notes="Monitor certificate expiry.")
    return case, result


def test_complete_customer_admin_engineer_workflow(db, actors):
    case, result = resolved(db, actors)
    assert case.status == "resolved" and case.resolved_at == result.resolved_at
    assignment = db.get(CaseAssignment, result.assignment_id)
    assert assignment.assigned_by_id == actors.admin.id and assignment.ended_at is not None
    assert result.resolved_by_id == actors.engineer.id
    events = list(db.scalars(select(CaseEvent).where(CaseEvent.case_id == case.id).order_by(CaseEvent.created_at)))
    assert [e.event_type for e in events] == ["created", "assigned", "started", "resolved"]
    assert "root_cause" not in events[-1].details
    messages = list(db.scalars(select(Notification).where(Notification.case_id == case.id)))
    assert len(messages) == 3
    customer_message = next(n for n in messages if n.recipient_id == actors.customer.id)
    assert customer_message.message == result.customer_summary
    with pytest.raises(PermissionDenied):
        mark_notification_read(db, notification_id=customer_message.id, actor_id=actors.other_customer.id)
    first_read = mark_notification_read(db, notification_id=customer_message.id, actor_id=actors.customer.id).read_at
    assert mark_notification_read(db, notification_id=customer_message.id, actor_id=actors.customer.id).read_at == first_read
    assert search_resolutions(db, actor_id=actors.engineer.id, query="certificate")[0].id == result.id


def test_reassignment_keeps_history_and_revokes_previous_engineers_action(db, actors):
    case = submitted(db, actors)
    first = assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.admin.id)
    second = assign_case(db, case_id=case.id, engineer_id=actors.other_engineer.id, admin_id=actors.admin.id)
    assert first.ended_at is not None and second.ended_at is None
    with pytest.raises(PermissionDenied):
        start_case(db, case_id=case.id, engineer_id=actors.engineer.id)
    assert start_case(db, case_id=case.id, engineer_id=actors.other_engineer.id).status == "in_progress"


def test_same_assignment_is_idempotent(db, actors):
    case = submitted(db, actors)
    first = assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.admin.id)
    assert assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.admin.id).id == first.id
    assert db.scalar(select(func.count()).select_from(CaseAssignment)) == 1
    assert db.scalar(select(func.count()).select_from(CaseEvent)) == 2


def test_reopen_and_resolve_again_preserves_both_fixes(db, actors):
    case, first = resolved(db, actors)
    reopen_case(db, case_id=case.id, actor_id=actors.customer.id)
    assert case.status == "open" and case.resolved_at is None
    assign_case(db, case_id=case.id, engineer_id=actors.other_engineer.id, admin_id=actors.admin.id)
    second = resolve_case(db, case_id=case.id, engineer_id=actors.other_engineer.id, root_cause="Renewal automation was disabled",
                          fix_summary="Enabled automatic certificate renewal", customer_summary="Automatic renewal is now enabled.")
    assert first.id != second.id
    assert db.scalar(select(func.count()).select_from(CaseResolution)) == 2


def test_repeated_issue_links_to_previous_case(db, actors):
    previous, _ = resolved(db, actors)
    repeated = submitted(db, actors, related_case_id=previous.id)
    assert repeated.related_case_id == previous.id
    with pytest.raises(PermissionDenied):
        submitted(db, actors, customer_id=actors.other_customer.id, related_case_id=previous.id)


@pytest.mark.parametrize("action", ["assign", "start", "resolve", "search"])
def test_customer_cannot_take_staff_actions(db, actors, action):
    case = submitted(db, actors)
    with pytest.raises(PermissionDenied):
        if action == "assign":
            assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.customer.id)
        elif action == "start":
            start_case(db, case_id=case.id, engineer_id=actors.customer.id)
        elif action == "resolve":
            resolve_case(db, case_id=case.id, engineer_id=actors.customer.id, root_cause="x", fix_summary="x", customer_summary="x")
        else:
            search_resolutions(db, actor_id=actors.customer.id, query="certificate")


def test_inactive_engineer_cannot_receive_assignment(db, actors):
    case = submitted(db, actors)
    actors.engineer.is_active = False
    db.flush()
    with pytest.raises(PermissionDenied):
        assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.admin.id)


def test_other_customer_cannot_reopen_case(db, actors):
    case, _ = resolved(db, actors)
    with pytest.raises(PermissionDenied):
        reopen_case(db, case_id=case.id, actor_id=actors.other_customer.id)


def test_failed_resolution_validation_leaves_case_assigned(db, actors):
    case = submitted(db, actors)
    assignment = assign_case(db, case_id=case.id, engineer_id=actors.engineer.id, admin_id=actors.admin.id)
    with pytest.raises(WorkflowError):
        resolve_case(db, case_id=case.id, engineer_id=actors.engineer.id, root_cause=" ", fix_summary="fix", customer_summary="fixed")
    assert case.status == "assigned" and assignment.ended_at is None
    assert db.scalar(select(func.count()).select_from(CaseResolution)) == 0


def test_workflow_rollback_removes_case_history_and_notifications_together(db, actors):
    with pytest.raises(RuntimeError):
        with db.begin_nested():
            resolved(db, actors)
            raise RuntimeError("Simulated failure before commit")
    for model in (Case, CaseAssignment, CaseResolution, CaseEvent, Notification):
        assert db.scalar(select(func.count()).select_from(model)) == 0
