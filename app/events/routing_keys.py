class RoutingKeys:
    # Issue
    ISSUE_CREATED = "issue.created"
    ISSUE_UPDATED = "issue.updated"
    ISSUE_DELETED = "issue.deleted"

    ISSUE_ASSIGNED = "issue.assigned"
    ISSUE_UNASSIGNED = "issue.unassigned"

    ISSUE_STATUS_CHANGED = "issue.status.changed"
    ISSUE_PRIORITY_CHANGED = "issue.priority.changed"
    ISSUE_DUE_DATE_CHANGED = "issue.due_date.changed"

    ISSUE_CLOSED = "issue.closed"
    ISSUE_REOPENED = "issue.reopened"

    # Comments
    COMMENT_CREATED = "issue.comment.created"
    COMMENT_UPDATED = "issue.comment.updated"
    COMMENT_DELETED = "issue.comment.deleted"

    # Project
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"

    PROJECT_MEMBER_ADDED = "project.member.added"
    PROJECT_MEMBER_REMOVED = "project.member.removed"
    PROJECT_MEMBER_ROLE_CHANGED = "project.member.role.changed"

    # User
    USER_REGISTERED = "user.registered"
    USER_EMAIL_VERIFIED = "user.email.verified"
    USER_EMAIL_CHANGED = "user.email.changed"
    USER_PASSWORD_CHANGED = "user.password.changed"
    USER_EMAIL_VERIFICATION_REQUESTED = "user.email.verification.requested"
    USER_PASSWORD_RESET_REQUESTED = "user.password.reset.requested"

    USER_LOGGED_IN = "user.logged.in"
    USER_LOGGED_OUT = "user.logged.out"
    USER_LOGGED_OUT_ALL = "user.logged.out.all"

    USER_DELETED = "user.deleted"