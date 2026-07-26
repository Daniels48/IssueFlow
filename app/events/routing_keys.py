class RoutingKeys:
    ISSUE_CREATED = "issue.created"
    ISSUE_UPDATED = "issue.updated"
    ISSUE_DELETED = "issue.deleted"

    ISSUE_ASSIGNED = "issue.assigned"
    ISSUE_UNASSIGNED = "issue.unassigned"

    ISSUE_STATUS_CHANGED = "issue.status.changed"
    ISSUE_PRIORITY_CHANGED = "issue.priority.changed"
    ISSUE_DUE_DATE_CHANGED = "issue.due_date.changed"

    COMMENT_CREATED = "issue.comment.created"
    COMMENT_UPDATED = "issue.comment.updated"
    COMMENT_DELETED = "issue.comment.deleted"

    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"

    PROJECT_MEMBER_ADDED = "project.member.added"
    PROJECT_MEMBER_REMOVED = "project.member.removed"
    PROJECT_MEMBER_ROLE_CHANGED = "project.member.role.changed"

    USER_REGISTERED = "user.registered"
    USER_EMAIL_VERIFIED = "user.email.verified"
    USER_PASSWORD_CHANGED = "user.password.changed"

    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"
    USER_LOGGED_OUT_ALL = "user.logged_out_all"

    USER_DELETED = "user.deleted"