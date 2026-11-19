"""Transactional case workflows for the future API.

Functions flush but never commit. Run a complete operation inside session_scope()
or Session.begin(). actor_id must come from the authenticated server-side user,
not a client-selected account identifier. Role checks here supplement that future
HTTP authentication layer.
"""
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, literal_column, select
from sqlalchemy.orm import Session

from app.models import Case, CaseAssignment, CaseEvent, CaseResolution, IssueCategory, Notification, User
from app.models.enums import CasePriority, CaseStatus, UserRole
from app.models.event import CaseEventType
from app.models.notification import NotificationType


class WorkflowError(ValueError):
    """A workflow action cannot be completed."""


class PermissionDenied(WorkflowError):
    pass


class RecordNotFound(WorkflowError):
    pass


class InvalidCaseState(WorkflowError):
    pass


def _actor(session: Session, actor_id: UUID, roles: set[str]) -> User:
    actor = session.scalar(select(User).where(User.id == actor_id).execution_options(populate_existing=True))
    if actor is None or not actor.is_active or actor.role not in roles:
        raise PermissionDenied("An active account with the required role is needed.")
    return actor


def _locked_case(session: Session, case_id: UUID) -> Case:
    row = session.scalar(select(Case).where(Case.id == case_id).with_for_update().execution_options(populate_existing=True))
    if row is None:
        raise RecordNotFound("Case not found.")
    return row


def _active_assignment(session: Session, case_id: UUID) -> CaseAssignment | None:
    return session.scalar(select(CaseAssignment).where(CaseAssignment.case_id == case_id, CaseAssignment.ended_at.is_(None)))


def _engineer_assignment(session: Session, case_id: UUID, engineer_id: UUID) -> CaseAssignment:
    assignment = _active_assignment(session, case_id)
    if assignment is None or assignment.engineer_id != engineer_id:
        raise PermissionDenied("Only the currently assigned engineer can perform this action.")
    return assignment


def _text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(f"{label} must not be blank.")
    return value.strip()


def _event(session: Session, case: Case, actor_id: UUID, kind: str, now: datetime,
           details: dict | None = None, visibility: str = "internal") -> CaseEvent:
    event = CaseEvent(case_id=case.id, actor_id=actor_id, event_type=kind,
                      created_at=now, details=details or {}, visibility=visibility)
    session.add(event)
    session.flush()
    return event


def _notify(session: Session, event: CaseEvent, recipient_id: UUID, kind: str, message: str) -> None:
    session.add(Notification(case_id=event.case_id, event_id=event.id, recipient_id=recipient_id,
                             kind=kind, message=message, created_at=event.created_at))


def _notify_admins(session: Session, event: CaseEvent, kind: str, message: str) -> None:
    for user_id in session.scalars(select(User.id).where(User.role == UserRole.ADMIN, User.is_active.is_(True))):
        _notify(session, event, user_id, kind, message)


def submit_case(session: Session, *, customer_id: UUID, category_id: UUID, title: str,
                description: str, affected_target: str | None = None,
                priority: str = CasePriority.MEDIUM, related_case_id: UUID | None = None) -> Case:
    _actor(session, customer_id, {UserRole.REQUESTER})
    category = session.get(IssueCategory, category_id)
    if category is None or not category.is_active:
        raise WorkflowError("Select an active issue category.")
    try:
        selected_priority = CasePriority(priority).value
    except ValueError as error:
        raise WorkflowError("Unknown case priority.") from error
    if related_case_id is not None:
        previous = session.get(Case, related_case_id)
        if previous is None or previous.customer_id != customer_id:
            raise PermissionDenied("The related case must belong to this customer.")
    now = datetime.now(UTC)
    row = Case(customer_id=customer_id, category_id=category_id, title=_text(title, "Title"),
               description=_text(description, "Description"), affected_target=affected_target,
               priority=selected_priority, related_case_id=related_case_id,
               created_at=now, updated_at=now)
    session.add(row)
    session.flush()
    event = _event(session, row, customer_id, CaseEventType.CREATED, now,
                   {"status_to": CaseStatus.OPEN}, visibility="customer")
    _notify_admins(session, event, NotificationType.CASE_CREATED, f"New support case {row.reference} needs assignment.")
    session.flush()
    return row


def assign_case(session: Session, *, case_id: UUID, engineer_id: UUID, admin_id: UUID,
                notes: str | None = None) -> CaseAssignment:
    _actor(session, admin_id, {UserRole.ADMIN})
    _actor(session, engineer_id, {UserRole.ENGINEER})
    case = _locked_case(session, case_id)
    if case.status == CaseStatus.RESOLVED:
        raise InvalidCaseState("Reopen the case before assigning it again.")
    previous = _active_assignment(session, case_id)
    if previous is not None and previous.engineer_id == engineer_id:
        return previous
    now = datetime.now(UTC)
    if previous is not None:
        previous.ended_at = now
        # Release the partial unique index before inserting the replacement.
        session.flush()
    assignment = CaseAssignment(case_id=case_id, engineer_id=engineer_id, assigned_by_id=admin_id,
                                assigned_at=now, notes=notes.strip() if notes and notes.strip() else None)
    session.add(assignment)
    case.status, case.updated_at = CaseStatus.ASSIGNED, now
    session.flush()
    event = _event(session, case, admin_id,
                   CaseEventType.REASSIGNED if previous else CaseEventType.ASSIGNED, now,
                   {"assignment_id": str(assignment.id), "engineer_id": str(engineer_id),
                    "previous_engineer_id": str(previous.engineer_id) if previous else None})
    _notify(session, event, engineer_id, NotificationType.CASE_ASSIGNED, f"You are assigned to {case.reference}.")
    session.flush()
    return assignment


def start_case(session: Session, *, case_id: UUID, engineer_id: UUID) -> Case:
    _actor(session, engineer_id, {UserRole.ENGINEER})
    case = _locked_case(session, case_id)
    _engineer_assignment(session, case_id, engineer_id)
    if case.status == CaseStatus.IN_PROGRESS:
        return case
    if case.status != CaseStatus.ASSIGNED:
        raise InvalidCaseState("Only an assigned case can begin investigation.")
    now = datetime.now(UTC)
    case.status, case.updated_at = CaseStatus.IN_PROGRESS, now
    _event(session, case, engineer_id, CaseEventType.STARTED, now, {"status_to": CaseStatus.IN_PROGRESS}, visibility="customer")
    return case


def resolve_case(session: Session, *, case_id: UUID, engineer_id: UUID, root_cause: str,
                 fix_summary: str, customer_summary: str, prevention_notes: str | None = None) -> CaseResolution:
    _actor(session, engineer_id, {UserRole.ENGINEER})
    case = _locked_case(session, case_id)
    assignment = _engineer_assignment(session, case_id, engineer_id)
    if case.status not in {CaseStatus.ASSIGNED, CaseStatus.IN_PROGRESS}:
        raise InvalidCaseState("Only an assigned or in-progress case can be resolved.")
    cause, fix, summary = _text(root_cause, "Root cause"), _text(fix_summary, "Fix"), _text(customer_summary, "Customer summary")
    now = datetime.now(UTC)
    resolution = CaseResolution(case_id=case_id, assignment_id=assignment.id, resolved_by_id=engineer_id,
                                root_cause=cause, fix_summary=fix, customer_summary=summary,
                                prevention_notes=prevention_notes.strip() if prevention_notes and prevention_notes.strip() else None,
                                resolved_at=now)
    session.add(resolution)
    assignment.ended_at = now
    case.status, case.resolved_at, case.updated_at = CaseStatus.RESOLVED, now, now
    session.flush()
    event = _event(session, case, engineer_id, CaseEventType.RESOLVED, now,
                   {"resolution_id": str(resolution.id), "status_to": CaseStatus.RESOLVED}, visibility="customer")
    _notify(session, event, case.customer_id, NotificationType.CASE_RESOLVED, summary)
    session.flush()
    return resolution


def reopen_case(session: Session, *, case_id: UUID, actor_id: UUID) -> Case:
    actor = _actor(session, actor_id, {UserRole.REQUESTER, UserRole.ADMIN})
    case = _locked_case(session, case_id)
    if actor.role == UserRole.REQUESTER and case.customer_id != actor.id:
        raise PermissionDenied("Customers can reopen only their own cases.")
    if case.status != CaseStatus.RESOLVED:
        raise InvalidCaseState("Only a resolved case can be reopened.")
    now = datetime.now(UTC)
    previous = _active_assignment(session, case_id)
    if previous is not None:
        previous.ended_at = now
    case.status, case.resolved_at, case.updated_at = CaseStatus.OPEN, None, now
    event = _event(session, case, actor.id, CaseEventType.REOPENED, now, {"status_to": CaseStatus.OPEN}, visibility="customer")
    _notify_admins(session, event, NotificationType.CASE_REOPENED, f"{case.reference} was reopened and needs assignment.")
    session.flush()
    return case


def mark_notification_read(session: Session, *, notification_id: UUID, actor_id: UUID) -> Notification:
    _actor(session, actor_id, {UserRole.REQUESTER, UserRole.ENGINEER, UserRole.ADMIN})
    notification = session.get(Notification, notification_id)
    if notification is None:
        raise RecordNotFound("Notification not found.")
    if notification.recipient_id != actor_id:
        raise PermissionDenied("A notification belongs to its recipient.")
    if notification.read_at is None:
        notification.read_at = datetime.now(UTC)
        session.flush()
    return notification


def search_resolutions(session: Session, *, actor_id: UUID, query: str, limit: int = 20) -> list[CaseResolution]:
    _actor(session, actor_id, {UserRole.ENGINEER, UserRole.ADMIN})
    if not 1 <= limit <= 50:
        raise WorkflowError("Search limit must be between 1 and 50.")
    if not query.strip():
        return []
    search = func.websearch_to_tsquery(literal_column("'english'::regconfig"), query)
    return list(session.scalars(select(CaseResolution).where(CaseResolution.search_document.op("@@")(search))
                               .order_by(CaseResolution.resolved_at.desc()).limit(limit)))
