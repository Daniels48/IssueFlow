from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User
from app.infrastructure.reddis.verify_email import VerifyEmailCache
from app.modules.auth.dependencies import DBSession
from app.modules.auth.email import EmailVerificationService
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserShortResponse, ChangeEmailRequest


class UserService:
    def __init__(self, db: AsyncSession, repository: UserRepository):
        self.db = db
        self.repository = repository

    async def search_users(self, query: str, project_id: UUID, current_user_id:int) -> list[UserShortResponse]:
        project = await ProjectRepository.get_by_public_id_no_full(self.db, project_id)
        if not project:
            return []
        Member_is = await ProjectMemberRepository.user_in_project(self.db, project.id, current_user_id)
        if not Member_is:
            pass
        return await self.repository.get_list_users_in_project(self.db, query, project.id, current_user_id)

    async def verify_email(self,user: User, code: str) -> None:
        if user.email_verified_at:
            return

        saved_code = await VerifyEmailCache.get(user.public_id)

        if saved_code is None:
            raise HTTPException(status_code=401)

        if saved_code != code:
            raise HTTPException(status_code=403)

        # user.email_verified_at = datetime.now(UTC)

        await VerifyEmailCache.delete(user.public_id)

        await self.db.commit()

    @staticmethod
    async def resend_verification_email(user: User):
        if user.email_verified_at:
            return

        await EmailVerificationService.send(user)

    async def change_email(self,user: User, email: str) -> None:
        if user.email == email:
            return

        if await self.repository.get_by_email(self.db, email):
            raise ValueError("Email already exists")

        user.email = email
        user.email_verified_at = None

        await self.db.commit()

        await EmailVerificationService.send(user)


async def get_user_service(db: DBSession) -> UserService:
    return UserService(db=db, repository=UserRepository())

UserService = Annotated[UserService,Depends(get_user_service)]
