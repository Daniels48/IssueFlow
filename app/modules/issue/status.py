from enum import StrEnum


class IssueStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CLOSED = "closed"