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

    COMMENT_VIEW = "comment:view"
    COMMENT_CREATE = "comment:create"
    COMMENT_UPDATE = "comment:update"
    COMMENT_DELETE = "comment:delete"

    MEMBER_VIEW = "member:view"
    MEMBER_ADD = "member:add"
    MEMBER_ROLE_UPDATE = "member:role_update"
    MEMBER_REMOVE = "member:remove"