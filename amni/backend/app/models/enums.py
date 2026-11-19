"""Stable string values used by the API and database constraints."""

from enum import StrEnum


class UserRole(StrEnum):
    REQUESTER = "requester"
    ENGINEER = "engineer"
    ADMIN = "admin"


class CaseStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class CasePriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
