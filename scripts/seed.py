import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import AsyncSessionLocal
from app.infrastructure.db.models import (
    Comment,
    Issue,
    Project,
    ProjectMember,
    User,
)
from app.modules.auth.password import PasswordService
from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus


DEMO_PASSWORD = "DemoPass123!"


def _enum_member(enum_type, *candidate_names: str):
    """Find an enum member by its Python name or value."""
    for candidate in candidate_names:
        for member in enum_type:
            if member.name.lower() == candidate.lower():
                return member
            if str(member.value).lower() == candidate.lower():
                return member

    available = ", ".join(
        f"{member.name}={member.value!r}" for member in enum_type
    )
    raise ValueError(
        f"Cannot find any of {candidate_names!r} in {enum_type.__name__}. "
        f"Available values: {available}"
    )


def _project_role_enum():
    """Get ProjectMember.role's Python enum from SQLAlchemy metadata."""
    column_type = ProjectMember.__table__.columns["role"].type
    enum_type = getattr(column_type, "enum_class", None)
    if enum_type is None:
        raise RuntimeError(
            "Could not determine ProjectRole from ProjectMember.role. "
            "Import ProjectRole directly in seed.py if your model does not "
            "expose enum_class."
        )
    return enum_type


async def _get_or_create_user(
    session: AsyncSession,
    *,
    username: str,
    email: str,
    password_hash: str,
    is_superuser: bool = False,
) -> User:
    result = await session.execute(
        select(User).where(
            (User.username == username) | (User.email == email)
        )
    )
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    now = datetime.now(timezone.utc)
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=True,
        is_superuser=is_superuser,
        email_verified_at=now,
        password_changed_at=now,
    )
    session.add(user)
    await session.flush()
    return user


async def _get_or_create_project(
    session: AsyncSession,
    *,
    name: str,
    description: str,
    owner: User,
) -> Project:
    result = await session.execute(
        select(Project).where(Project.name == name)
    )
    project = result.scalar_one_or_none()

    if project is None:
        project = Project(
            name=name,
            description=description,
            owner_id=owner.id,
        )
        session.add(project)
        await session.flush()

    return project


async def _ensure_membership(
    session: AsyncSession,
    *,
    project: Project,
    user: User,
    role,
) -> None:
    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id,
        )
    )
    if result.scalar_one_or_none() is None:
        session.add(
            ProjectMember(
                project_id=project.id,
                user_id=user.id,
                role=role,
            )
        )


async def _get_or_create_issue(
    session: AsyncSession,
    *,
    project: Project,
    title: str,
    description: str,
    reporter: User,
    assignee: User | None,
    status: IssueStatus,
    priority: IssuePriority,
    due_date: datetime,
    closed_by: User | None = None,
) -> Issue:
    result = await session.execute(
        select(Issue).where(
            Issue.project_id == project.id,
            Issue.title == title,
        )
    )
    issue = result.scalar_one_or_none()

    if issue is not None:
        return issue

    is_closed = status in (IssueStatus.DONE, IssueStatus.CLOSED)
    issue = Issue(
        project_id=project.id,
        reporter_id=reporter.id,
        assignee_id=assignee.id if assignee else None,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        closed_at=datetime.now(timezone.utc) if is_closed else None,
        closed_by_id=closed_by.id if is_closed and closed_by else None,
    )
    session.add(issue)
    await session.flush()
    return issue


async def _ensure_comment(
    session: AsyncSession,
    *,
    issue: Issue,
    author: User,
    content: str,
) -> None:
    result = await session.execute(
        select(Comment).where(
            Comment.issue_id == issue.id,
            Comment.author_id == author.id,
            Comment.content == content,
        )
    )
    if result.scalar_one_or_none() is None:
        session.add(
            Comment(
                issue_id=issue.id,
                author_id=author.id,
                content=content,
            )
        )


async def seed() -> None:
    password_hash = PasswordService.hash_password(DEMO_PASSWORD)

    role_enum = _project_role_enum()
    member_role = _enum_member(role_enum, "member")
    admin_role = _enum_member(role_enum, "admin")

    # Use the actual enums defined by this project.
    status_open = IssueStatus.OPEN
    status_in_progress = IssueStatus.IN_PROGRESS
    status_review = IssueStatus.REVIEW
    status_done = IssueStatus.DONE
    status_closed = IssueStatus.CLOSED

    priority_low = IssuePriority.LOW
    priority_medium = IssuePriority.MEDIUM
    priority_high = IssuePriority.HIGH
    priority_critical = IssuePriority.CRITICAL

    async with AsyncSessionLocal() as session:
        try:
            # 1. Demo users
            admin = await _get_or_create_user(
                session,
                username="demo_admin",
                email="demo_admin@example.com",
                password_hash=password_hash,
            )
            developer = await _get_or_create_user(
                session,
                username="demo_developer",
                email="demo_developer@example.com",
                password_hash=password_hash,
            )
            qa = await _get_or_create_user(
                session,
                username="demo_qa",
                email="demo_qa@example.com",
                password_hash=password_hash,
            )
            manager = await _get_or_create_user(
                session,
                username="demo_manager",
                email="demo_manager@example.com",
                password_hash=password_hash,
            )
            reporter = await _get_or_create_user(
                session,
                username="demo_reporter",
                email="demo_reporter@example.com",
                password_hash=password_hash,
            )
            developer2 = await _get_or_create_user(
                session,
                username="demo_developer2",
                email="demo_developer2@example.com",
                password_hash=password_hash,
            )

            # 2. Demo projects. Ownership is represented by Project.owner_id.
            backend_project = await _get_or_create_project(
                session,
                name="IssueFlow Backend",
                description=(
                    "API, database, authorization, and background tasks."
                ),
                owner=admin,
            )
            frontend_project = await _get_or_create_project(
                session,
                name="IssueFlow Frontend",
                description="UI, board, forms, and issue details.",
                owner=manager,
            )
            qa_project = await _get_or_create_project(
                session,
                name="QA and Testing",
                description="Test plans, regression checks, and bug reports.",
                owner=qa,
            )

            # 3. Memberships. ProjectRole has only member/admin.
            # Owners are also listed as admins here so they appear in the
            # membership relation if the UI uses project_members to list users.
            memberships = [
                (backend_project, admin, admin_role),
                (backend_project, developer, member_role),
                (backend_project, qa, member_role),
                (backend_project, developer2, member_role),
                (frontend_project, manager, admin_role),
                (frontend_project, admin, member_role),
                (frontend_project, reporter, member_role),
                (frontend_project, developer, member_role),
                (qa_project, qa, admin_role),
                (qa_project, admin, member_role),
                (qa_project, manager, member_role),
                (qa_project, reporter, member_role),
            ]
            for project, user, role in memberships:
                await _ensure_membership(
                    session,
                    project=project,
                    user=user,
                    role=role,
                )

            # 4. Demo issues. All five IssueStatus values and all four
            # IssuePriority values are represented.
            now = datetime.now(timezone.utc)
            issue_specs = [
                (
                    backend_project,
                    "Implement refresh-token rotation",
                    "Rotate refresh tokens after successful renewal.",
                    reporter,
                    developer,
                    status_in_progress,
                    priority_high,
                    now + timedelta(days=5),
                ),
                (
                    backend_project,
                    "Validate issue status transitions",
                    "Reject status changes that are not allowed by workflow.",
                    qa,
                    developer2,
                    status_open,
                    priority_medium,
                    now + timedelta(days=8),
                ),
                (
                    backend_project,
                    "Add pagination to issue list",
                    "Support pagination for large projects.",
                    reporter,
                    developer2,
                    status_review,
                    priority_low,
                    now + timedelta(days=3),
                ),
                (
                    backend_project,
                    "Fix project owner permission check",
                    "Verify access based on Project.owner_id.",
                    qa,
                    admin,
                    status_in_progress,
                    priority_critical,
                    now + timedelta(days=2),
                ),
                (
                    backend_project,
                    "Write API integration tests",
                    "Cover project membership, issue CRUD, and comments.",
                    developer,
                    qa,
                    status_done,
                    priority_medium,
                    now - timedelta(days=2),
                ),
                (
                    frontend_project,
                    "Build issue details page",
                    "Show description, status, priority, assignee, and comments.",
                    reporter,
                    developer,
                    status_in_progress,
                    priority_high,
                    now + timedelta(days=6),
                ),
                (
                    frontend_project,
                    "Add board filters",
                    "Filter issues by status, priority, and assignee.",
                    developer2,
                    manager,
                    status_open,
                    priority_medium,
                    now + timedelta(days=10),
                ),
                (
                    frontend_project,
                    "Improve empty states",
                    "Show guidance when a board or issue list is empty.",
                    admin,
                    manager,
                    status_closed,
                    priority_low,
                    now - timedelta(days=1),
                ),
                (
                    qa_project,
                    "Test expired access token",
                    "Protected endpoints must reject expired access tokens.",
                    qa,
                    developer2,
                    status_review,
                    priority_high,
                    now + timedelta(days=3),
                ),
                (
                    qa_project,
                    "Check duplicate project membership",
                    "A user must not be added to the same project twice.",
                    reporter,
                    qa,
                    status_open,
                    priority_critical,
                    now + timedelta(days=4),
                ),
                (
                    qa_project,
                    "Document issue status rules",
                    "Document status transitions and closure behavior.",
                    developer,
                    admin,
                    status_done,
                    priority_medium,
                    now - timedelta(days=4),
                ),
            ]

            seeded_issues: list[tuple[Issue, User, User]] = []
            for (
                project,
                title,
                description,
                issue_reporter,
                assignee,
                status,
                priority,
                due_date,
            ) in issue_specs:
                issue = await _get_or_create_issue(
                    session,
                    project=project,
                    title=title,
                    description=description,
                    reporter=issue_reporter,
                    assignee=assignee,
                    status=status,
                    priority=priority,
                    due_date=due_date,
                    closed_by=admin,
                )
                seeded_issues.append((issue, issue_reporter, assignee))

            # 5. Two comments per issue; existing matching comments are kept.
            for index, (issue, issue_reporter, assignee) in enumerate(
                seeded_issues, start=1
            ):
                await _ensure_comment(
                    session,
                    issue=issue,
                    author=issue_reporter,
                    content=(
                        f"Demo comment {index}: please review the requirements."
                    ),
                )
                await _ensure_comment(
                    session,
                    issue=issue,
                    author=assignee,
                    content=(
                        f"Demo comment {index}: I will check this and report back."
                    ),
                )

            await session.commit()

            print("Seed completed successfully.")
            print("Users: 6")
            print("Projects: 3")
            print(f"Issues: {len(seeded_issues)}")
            print(f"Password for newly created demo users: {DEMO_PASSWORD}")

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed())
