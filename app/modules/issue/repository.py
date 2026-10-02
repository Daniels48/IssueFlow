from datetime import datetime, timezone, timedelta, time
from uuid import UUID

from sqlalchemy import select, or_, nulls_last, case, func
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
    def _apply_issue_sort(stmt, sort: list[IssueSort] | None):
        if not sort:
            return stmt

        priority_order = case(
            (Issue.priority == IssuePriority.LOW, 1),
            (Issue.priority == IssuePriority.MEDIUM, 2),
            (Issue.priority == IssuePriority.HIGH, 3),
            (Issue.priority == IssuePriority.CRITICAL, 4),
        )

        for item in sort:

            if item == IssueSort.STATUS_ASC:
                stmt = stmt.order_by(Issue.status.asc())

            elif item == IssueSort.STATUS_DESC:
                stmt = stmt.order_by(Issue.status.desc())

            elif item == IssueSort.PRIORITY_ASC:
                stmt = stmt.order_by(priority_order.asc())

            elif item == IssueSort.PRIORITY_DESC:
                stmt = stmt.order_by(priority_order.desc())

            elif item == IssueSort.DUE_DATE_ASC:
                stmt = stmt.order_by(nulls_last(Issue.due_date.asc()))

            elif item == IssueSort.DUE_DATE_DESC:
                stmt = stmt.order_by(nulls_last(Issue.due_date.desc()))

        return stmt

    @staticmethod
    async def get_all_by_project(db: AsyncSession,project_id: int,filters: IssueFilters):
        offset = (filters.page - 1) * filters.per_page

        # Items
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

        stmt = stmt.offset(offset).limit(filters.per_page)

        # Total
        total_count_stmt = (
            select(func.count(Issue.id))
            .where(
                Issue.project_id == project_id,
                Issue.deleted_at.is_(None),
            )
        )

        # Filtered total
        filtered_count_stmt = (
            select(func.count(Issue.id))
            .where(
                Issue.project_id == project_id,
                Issue.deleted_at.is_(None),
            )
        )

        filtered_count_stmt = IssueRepository._apply_issue_filters(filtered_count_stmt,filters)

        result_items = await db.execute(stmt)
        result_total = await db.execute(total_count_stmt)
        result_filtered = await db.execute(filtered_count_stmt)

        return {
            "items": list(result_items.scalars().all()),
            "total": result_total.scalar_one(),
            "filtered_total": result_filtered.scalar_one(),
            "page": filters.page,
            "per_page": filters.per_page,
        }
