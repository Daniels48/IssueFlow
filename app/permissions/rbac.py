from app.core.exceptions import AppException, ErrorCode
from app.infrastructure.db.models import User, Project, ProjectMember, Comment, Issue
from app.modules.project_members.project_role import ProjectRole
from app.permissions.context import PermissionContext
from app.permissions.enums import Permission, Role



class ProjectRBAC:
    @staticmethod
    def get_permissions_for_global_admin() -> set[Permission]:
        return set(Permission)

    @staticmethod
    def get_permissions_for_project_owner() -> set[Permission]:
        return set(Permission)

    @staticmethod
    def get_permissions_for_project_admin() -> set[Permission]:
        permissions = set(Permission)
        permissions.discard(Permission.PROJECT_DELETE)
        return permissions

    @staticmethod
    def get_permissions_for_project_member() -> set[Permission]:
        return {
            Permission.PROJECT_VIEW,

            Permission.ISSUE_VIEW,
            Permission.ISSUE_CREATE,

            Permission.COMMENT_VIEW,
            Permission.COMMENT_CREATE,

            Permission.MEMBER_VIEW,
        }

    @staticmethod
    def get_permissions_for_issue_owner() -> set[Permission]:
        return {
            Permission.ISSUE_VIEW,
            Permission.ISSUE_UPDATE,
            Permission.ISSUE_DELETE,
        }

    @staticmethod
    def get_permissions_for_comment_owner() -> set[Permission]:
        return {
            Permission.COMMENT_VIEW,
            Permission.COMMENT_UPDATE,
            Permission.COMMENT_DELETE,
        }

    @staticmethod
    def get_permissions_for_role(role: Role) -> set[Permission]:
        return PERMISSION_GETTERS[role]()


    @staticmethod
    def get_roles(context: PermissionContext) -> set[Role]:
        user = context.user
        project = context.project
        member = context.member
        resource = context.resource

        if user.is_superuser:
            return {Role.GLOBAL_ADMIN}

        if project.owner_id == user.id:
            return {Role.PROJECT_OWNER}

        if member is None:
            return set()

        roles = set()

        if member.role == ProjectRole.ADMIN:
            roles.add(Role.PROJECT_ADMIN)

        elif member.role == ProjectRole.MEMBER:
            roles.add(Role.PROJECT_MEMBER)

        if isinstance(resource, Issue):
            if resource.reporter_id == user.id:
                roles.add(Role.ISSUE_OWNER)

        elif isinstance(resource, Comment):
            if resource.author_id == user.id:
                roles.add(Role.COMMENT_OWNER)

        return roles

    @staticmethod
    def require(permission: Permission, context: PermissionContext) -> None:

        roles = ProjectRBAC.get_roles(context)

        permissions = (permission in ProjectRBAC.get_permissions_for_role(role) for role in roles)

        if any(permissions):
            return

        raise AppException(ErrorCode.PERMISSION_DENIED,"Permission denied")


PERMISSION_GETTERS = {
    Role.GLOBAL_ADMIN: ProjectRBAC.get_permissions_for_global_admin,
    Role.PROJECT_OWNER: ProjectRBAC.get_permissions_for_project_owner,
    Role.PROJECT_ADMIN: ProjectRBAC.get_permissions_for_project_admin,
    Role.PROJECT_MEMBER: ProjectRBAC.get_permissions_for_project_member,
    Role.ISSUE_OWNER: ProjectRBAC.get_permissions_for_issue_owner,
    Role.COMMENT_OWNER: ProjectRBAC.get_permissions_for_comment_owner,
}
