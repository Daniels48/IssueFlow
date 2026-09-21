from datetime import datetime, timezone, timedelta, time
from uuid import UUID

from sqlalchemy import select, or_, nulls_last, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria, joinedload, contains_eager

from app.infrastructure.db.models import Issue, Comment, Project, ProjectMember
from app.modules.issue.priority import IssuePriority
from app.modules.issue.schema import IssueFilters, DueDateFilter, IssueSort
from app.utils.func_utils import get_now_dt


class IssueRepository:
    @staticmethod
    async def create(db: AsyncSession,issue: Issue) -> Issue:
        db.add(issue)
        await db.flush()
        return issue


    @staticmethod
    async def get_by_public_id_with_current_member(db: AsyncSession, public_id: UUID, user_id: int,
    ) -> tuple[Issue, ProjectMember | None] | None:
        stmt = (
            select(Issue, ProjectMember)
            .join(Issue.project)
            .outerjoin(
                ProjectMember,
                (ProjectMember.project_id == Project.id)
                & (ProjectMember.user_id == user_id),
            )
            .options(
                contains_eager(Issue.project),
            )
            .where(
                Issue.public_id == public_id,
                Issue.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        row = result.one_or_none()
        if row is None:
            return None

        issue, member_current = row

        return issue, member_current

    @staticmethod
    async def get_by_public_id_with_current_member_and_assignee(db: AsyncSession,public_id: UUID, user_id: int,
    ) -> tuple[Issue, ProjectMember | None] | None:

        stmt = (
            select(Issue, ProjectMember)
            .join(Issue.project)
            .outerjoin(
                ProjectMember,
                (ProjectMember.project_id == Project.id)
                & (ProjectMember.user_id == user_id),
            )
            .options(
                contains_eager(Issue.project),
                selectinload(Issue.assignee),
            )
            .where(
                Issue.public_id == public_id,
                Issue.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        row = result.one_or_none()

        if row is None:
            return None

        issue, member_current = row

        return issue, member_current

    @staticmethod
    async def get_by_public_id_full(db: AsyncSession, public_id: UUID) -> Issue | None:
        stmt = (
            select(Issue)
            .options(
                joinedload(Issue.project)
                .selectinload(Project.members)
                .selectinload(ProjectMember.user),

                selectinload(Issue.reporter),
                selectinload(Issue.assignee),

                selectinload(Issue.comments).selectinload(Comment.author),

                with_loader_criteria(
                    Comment,
                    Comment.deleted_at.is_(None),
                    include_aliases=True,
                ),
            )
            .where(
                Issue.public_id == public_id,
                Issue.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    def _apply_issue_filters(stmt, filters: IssueFilters):
        if filters.search:
            search = (
                filters.search
                .replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )

            pattern = f"%{search}%"

            stmt = stmt.where(
                or_(
                    Issue.title.ilike(pattern, escape="\\"),
                    Issue.description.ilike(pattern, escape="\\"),
                )
            )

        if filters.status:
            stmt = stmt.where(Issue.status == filters.status)

        if filters.priority:
            stmt = stmt.where(Issue.priority == filters.priority)

        if filters.due_date:
            now = get_now_dt()

            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

            if filters.due_date == DueDateFilter.OVERDUE:
                stmt = stmt.where(Issue.due_date < now)

            elif filters.due_date == DueDateFilter.TODAY:
                stmt = stmt.where(
                    Issue.due_date >= start,
                    Issue.due_date < end,
                )

            elif filters.due_date == DueDateFilter.UPCOMING:
                stmt = stmt.where(Issue.due_date >= end )

        return stmt

    @staticmethod
    def _apply_issue_sort(stmt, sort: IssueSort | None):
        priority_order = case(
            (Issue.priority == IssuePriority.LOW, 1),
            (Issue.priority == IssuePriority.MEDIUM, 2),
            (Issue.priority == IssuePriority.HIGH, 3),
            (Issue.priority == IssuePriority.CRITICAL, 4),
        )

        if sort == IssueSort.DUE_DATE_ASC:
            stmt = stmt.order_by(nulls_last(Issue.due_date.asc()))

        elif sort == IssueSort.DUE_DATE_DESC:
            stmt = stmt.order_by(nulls_last(Issue.due_date.desc()))

        elif sort == IssueSort.PRIORITY_ASC:
            stmt = stmt.order_by(priority_order.asc())

        elif sort == IssueSort.PRIORITY_DESC:
            stmt = stmt.order_by(priority_order.desc())

        elif sort == IssueSort.NEWEST:
            stmt = stmt.order_by(Issue.created_at.desc())

        elif sort == IssueSort.OLDEST:
            stmt = stmt.order_by(Issue.created_at.asc())

        return stmt

    @staticmethod
    async def get_all_by_project(db: AsyncSession, project_id: int, filters: IssueFilters) -> list[Issue]:
        stmt = (
            select(Issue)
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
            )
            .where(
                Issue.project_id == project_id,
                Issue.deleted_at.is_(None),
            )
        )

        stmt = IssueRepository._apply_issue_filters(stmt, filters)
        stmt = IssueRepository._apply_issue_sort(stmt, filters.sort)

        result = await db.execute(stmt)

        return list(result.scalars().all())