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