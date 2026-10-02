from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager, aliased

from app.infrastructure.db.models import Comment, ProjectMember, Issue, Project


class CommentRepository:
    @staticmethod
    async def create(db: AsyncSession, comment: Comment) -> Comment:
        db.add(comment)
        await db.flush()
        return comment

    @staticmethod
    async def get_by_public_id(db: AsyncSession, public_id: UUID) -> Comment:
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(
                Comment.public_id == public_id,
                Comment.deleted_at.is_(None),
            )
        )

        return result.scalar_one()

    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int) -> Comment:
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.id == comment_id)
        )

        return result.scalar_one()

    @staticmethod
    def _get_by_public_id_with_current_member_smt(public_id: UUID, user_id: int):
        return (
            select(Comment, ProjectMember)
            .join(Comment.issue)
            .join(Issue.project)
            .outerjoin(
                ProjectMember,
                (ProjectMember.project_id == Project.id)
                & (ProjectMember.user_id == user_id),
            )
            .options(
                contains_eager(Comment.issue)
                .contains_eager(Issue.project)
            )
            .where(Comment.public_id == public_id,)
        )

    @staticmethod
    async def get_by_public_id_with_current_member(db: AsyncSession, public_id: UUID, user_id: int,
    ) -> tuple[Comment, ProjectMember | None] | None:
        stmt = CommentRepository._get_by_public_id_with_current_member_smt(public_id, user_id)

        result = await db.execute(stmt)

        row = result.one_or_none()

        if row is None:
            return None

        comment, member_current = row

        return comment, member_current

    @staticmethod
    async def get_active_by_public_id_with_current_member(db: AsyncSession, public_id: UUID, user_id: int,
    ) -> tuple[Comment, ProjectMember | None] | None:
        stmt = CommentRepository._get_by_public_id_with_current_member_smt(public_id, user_id)

        stmt = stmt.where(Comment.deleted_at.is_(None))

        result = await db.execute(stmt)

        row = result.one_or_none()

        if row is None:
            return None

        comment, member_current = row

        return comment, member_current

    @staticmethod
    async def get_comments_by_issue_id(db: AsyncSession,issue_id: int,page: int,per_page: int):
        visible_filter = or_(
            Comment.deleted_at.is_(None),
            Comment.replies_count > 0,
        )

        stmt = (
            select(Comment)
            .where(
                Comment.issue_id == issue_id,
                Comment.parent_comment_id.is_(None),
                visible_filter,
            )
            .options(selectinload(Comment.author),)
            .order_by(Comment.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = await db.execute(stmt)

        items = list(result.scalars().all())

        total = await db.scalar(
            select(func.count(Comment.id))
            .where(
                Comment.issue_id == issue_id,
                Comment.parent_comment_id.is_(None),
                visible_filter,
            )
        ) or 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": page * per_page < total,
        }

    @staticmethod
    async def get_replies(db: AsyncSession,comment_id: int,page: int,per_page: int):
        visible_filter = or_(Comment.deleted_at.is_(None),Comment.replies_count > 0)

        stmt = (
            select(Comment)
            .where(Comment.parent_comment_id == comment_id, visible_filter)
            .options(selectinload(Comment.author))
            .order_by(Comment.created_at.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        result = await db.execute(stmt)

        items = list(result.scalars().all())

        total = await db.scalar(
            select(func.count(Comment.id))
            .where(Comment.parent_comment_id == comment_id,visible_filter)
        ) or 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": page * per_page < total,
        }

    @staticmethod
    async def has_alive_descendants(db: AsyncSession,comment_id: int) -> bool:
        descendants = (
            select(
                Comment.id,
                Comment.parent_comment_id,
                Comment.deleted_at,
            )
            .where(Comment.id == comment_id)
            .cte(name="descendants", recursive=True)
        )

        descendants = descendants.union_all(
            select(
                Comment.id,
                Comment.parent_comment_id,
                Comment.deleted_at,
            )
            .join(
                descendants,
                Comment.parent_comment_id == descendants.c.id,
            )
        )

        stmt = (
            select(descendants.c.id)
            .where(
                descendants.c.id != comment_id,
                descendants.c.deleted_at.is_(None),
            )
            .limit(1)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none() is not None