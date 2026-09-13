from app.modules.issue.status import IssueStatus


ALLOWED_STATUS_TRANSITIONS = {
    IssueStatus.OPEN: {
        IssueStatus.IN_PROGRESS,
    },
    IssueStatus.IN_PROGRESS: {
        IssueStatus.OPEN,
        IssueStatus.REVIEW,
    },
    IssueStatus.REVIEW: {
        IssueStatus.IN_PROGRESS,
        IssueStatus.DONE,
    },
    IssueStatus.DONE: {
        IssueStatus.REVIEW,
    },
}

ALLOWED_STATUS_TRANSITIONS_FRONT = {
    IssueStatus.OPEN: {
        "next": IssueStatus.IN_PROGRESS,
    },
    IssueStatus.IN_PROGRESS: {
        "previous": IssueStatus.OPEN,
        "next": IssueStatus.REVIEW,
    },
    IssueStatus.REVIEW: {
        "previous": IssueStatus.IN_PROGRESS,
        "next": IssueStatus.DONE,
    },
    IssueStatus.DONE: {
        "previous": IssueStatus.REVIEW,
    },
}