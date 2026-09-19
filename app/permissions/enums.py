from enum import StrEnum


class Role(StrEnum):
    GLOBAL_ADMIN = "global_admin"

    PROJECT_OWNER = "project_owner"
    PROJECT_ADMIN = "project_admin"
    PROJECT_MEMBER = "project_member"

    ISSUE_OWNER = "issue_owner"
    COMMENT_OWNER = "comment_owner"


class Permission(StrEnum):
    PROJECT_VIEW = "project:view"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    ISSUE_VIEW = "issue:view"
    ISSUE_CREATE = "issue:create"
    ISSUE_UPDATE = "issue:update"
    ISSUE_DELETE = "issue:delete"

    ISSUE_CHANGE_DUE_DATE = "issue:change:due_date"
    ISSUE_CHANGE_PRIORITY = "issue:change:priority"
    ISSUE_CHANGE_STATUS = "issue:change:status"
    ISSUE_CLOSE = "issue:close"
    ISSUE_REOPEN = "issue:reopen"
    ISSUE_ASSIGNED = "issue:assigned"

    COMMENT_VIEW = "comment:view"
    COMMENT_CREATE = "comment:create"
    COMMENT_UPDATE = "comment:update"
    COMMENT_DELETE = "comment:delete"

    MEMBER_VIEW = "member:view"
    MEMBER_ADD = "member:add"
    MEMBER_ROLE_UPDATE = "member:role_update"
    MEMBER_REMOVE = "member:remove"