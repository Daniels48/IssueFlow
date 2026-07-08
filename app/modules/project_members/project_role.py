from enum import StrEnum


class ProjectRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
