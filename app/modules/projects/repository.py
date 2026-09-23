from typing import Any
from uuid import UUID

from sqlalchemy import select, func, and_, Row, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria, joinedload, aliased

from app.infrastructure.db.models import ProjectMember, Comment, Issue, User
from app.infrastructure.db.models.model_projects import Project
from sqlalchemy import select, func, literal, cast
from sqlalchemy.dialects.postgresql import JSONB


class ProjectRepository:
    @staticmethod
    async def create(db: AsyncSession,project: Project) -> Project:
        db.add(project)
        await db.flush()
        return project

    @staticmethod
    async def get_by_public_id(db: AsyncSession,public_id: UUID) -> Project | None:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),

                selectinload(Project.issues).selectinload(Issue.reporter),
                selectinload(Project.issues).selectinload(Issue.assignee),

                with_loader_criteria(ProjectMember, ProjectMember.deleted_at.is_(None), include_aliases=True),
                with_loader_criteria(Issue, Issue.deleted_at.is_(None), include_aliases=True),
            )
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_public_id_with_current_member_detail( db: AsyncSession,public_id: UUID, user_id: int,
    ) -> tuple[Project, ProjectMember | None] | None:
        stmt = (
            select(Project, ProjectMember)
            .outerjoin(
                ProjectMember,
                (ProjectMember.project_id == Project.id)
                & (ProjectMember.user_id == user_id),
            )
            .options(
                selectinload(Project.members)
                .selectinload(ProjectMember.user),

                selectinload(Project.issues)
                .selectinload(Issue.reporter),

                selectinload(Project.issues)
                .selectinload(Issue.assignee),

                with_loader_criteria(  ProjectMember,  ProjectMember.deleted_at.is_(None),  include_aliases=True),
                with_loader_criteria(Issue, Issue.deleted_at.is_(None), include_aliases=True ),
            )
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)
        row = result.one_or_none()

        if row is None:
            return None

        project, member = row
        return project, member

    @staticmethod
    async def get_by_public_id_detail_aggregate(db: AsyncSession,public_id: UUID) -> tuple[Any, Any, Any] | None:

        Reporter = aliased(User)
        Assignee = aliased(User)

        member_value = func.jsonb_build_object(
                            "public_id", ProjectMember.public_id,
                            "role", ProjectMember.role,
                            "user", func.jsonb_build_object(
                                "public_id", User.public_id,
                                "username", User.username,
                            ),
                        )

        members_subq = (
            select(func.coalesce(func.jsonb_agg(member_value), cast("[]", JSONB)))
            .select_from(ProjectMember)
            .join(User, User.id == ProjectMember.user_id)
            .where(
                ProjectMember.project_id == Project.id,
                ProjectMember.deleted_at.is_(None),
            )
            .correlate(Project)
            .scalar_subquery()
        )

        issue_value = func.jsonb_build_object(
                            "public_id", Issue.public_id,
                            "title", Issue.title,
                            "description", Issue.description,
                            "status", Issue.status,
                            "priority", Issue.priority,
                            "due_date", Issue.due_date,
                            "created_at", Issue.created_at,
                            "updated_at", Issue.updated_at,

                            "reporter", func.jsonb_build_object(
                                "public_id", Reporter.public_id,
                                "username", Reporter.username,
                            ),

                            "assignee", case((
                            Assignee.id.is_not(None),
                                func.jsonb_build_object(
                                    "public_id", Assignee.public_id,
                                    "username", Assignee.username,
                                ),),
                            else_=None,),
                        )

        issues_subq = (
            select(func.coalesce(func.jsonb_agg(issue_value).filter(Issue.id.is_not(None)), cast("[]", JSONB)))
            .select_from(Issue)
            .join(Reporter, Reporter.id == Issue.reporter_id)
            .outerjoin(Assignee, Assignee.id == Issue.assignee_id)
            .where(
                Issue.project_id == Project.id,
                Issue.deleted_at.is_(None),
            )
            .correlate(Project)
            .scalar_subquery()
        )

        stmt = (
            select(
                Project,
                members_subq.label("members"),
                issues_subq.label("issues"),
            )
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        row = result.one_or_none()

        if row is None:
            return None

        project, members, issues = row

        return project, members, issues

    @staticmethod
    def _members_get_query():
        return (
            select(
                ProjectMember.project_id.label("project_id"),
                func.count(ProjectMember.id).label("members_count"),
            )
            .where(ProjectMember.deleted_at.is_(None), )
            .group_by(ProjectMember.project_id)
            .subquery()
        )

    @staticmethod
    def _issues_get_query():
        return (
            select(
                Issue.project_id.label("project_id"),
                func.count(Issue.id).label("issues_count"),
            )
            .where(Issue.deleted_at.is_(None), )
            .group_by(Issue.project_id)
            .subquery()
        )

    @staticmethod
    def _comments_get_query():
        return (
            select(
                Issue.project_id.label("project_id"),
                func.count(Comment.id).label("comments_count"),
            )
            .select_from(Issue)
            .outerjoin(
                Comment,
                and_(
                    Comment.issue_id == Issue.id,
                    Comment.deleted_at.is_(None),
                ),
            )
            .where(Issue.deleted_at.is_(None), )
            .group_by(Issue.project_id)
            .subquery()
        )

    @staticmethod
    async def get_all_by_user(db: AsyncSession, user_id: int,is_admin: bool) -> list[Row[tuple[Any, Any, Any, Any]]]:
        members_subq = ProjectRepository._members_get_query()
        issues_subq = ProjectRepository._issues_get_query()
        comments_subq = ProjectRepository._comments_get_query()

        stmt = (
            select(
                Project,
                func.coalesce(members_subq.c.members_count,0,).label("members_count"),
                func.coalesce(issues_subq.c.issues_count,0,).label("issues_count"),
                func.coalesce(comments_subq.c.comments_count,0,).label("comments_count"),
            )
            .options(joinedload(Project.owner))
            .outerjoin(members_subq, members_subq.c.project_id == Project.id,)
            .outerjoin(issues_subq,issues_subq.c.project_id == Project.id,)
            .outerjoin(comments_subq, comments_subq.c.project_id == Project.id,)
            .where(Project.deleted_at.is_(None),)
        )

        if not is_admin:
            member_exists = (
                select(1)
                .where(
                    ProjectMember.project_id == Project.id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.deleted_at.is_(None),
                )
                .exists()
            )

            stmt = stmt.where(
                or_(
                    Project.owner_id == user_id,
                    member_exists,
                )
            )

        stmt = stmt.order_by(Project.created_at.desc())

        result = await db.execute(stmt)

        return list(result.all())

    @staticmethod
    async def get_by_public_id_no_full(db: AsyncSession, public_id: UUID) -> Project | None:
        stmt = (
            select(Project)
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_public_id_with_current_member(db: AsyncSession,public_id: UUID,user_id: int,
    ) -> tuple[Project, ProjectMember | None] | None:
        stmt = (
            select(Project, ProjectMember)
            .outerjoin(
                ProjectMember,
                (ProjectMember.project_id == Project.id)
                & (ProjectMember.user_id == user_id)
                & (ProjectMember.deleted_at.is_(None)),
            )
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)
        row = result.one_or_none()

        if row is None:
            return None

        return row

    @staticmethod
    async def get_all_with_users(db: AsyncSession) -> list[Project]:
        result = await db.execute(
            select(Project).options(
                selectinload(Project.users)
            )
        )

        return list(result.scalars())