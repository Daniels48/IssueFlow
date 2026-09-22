from dataclasses import dataclass

from app.infrastructure.db.models import User, Project, ProjectMember, Issue, Comment


@dataclass
class PermissionContext:
    user: User
    project: Project
    member: ProjectMember | None = None
    resource: Issue | Comment | None = None