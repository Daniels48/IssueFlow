from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Project
from app.modules.auth.dependencies import DBSession
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import UserShortResponse
from app.modules.users.repository import UserRepository


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



async def get_user_service(db: DBSession) -> UserService:
    return UserService(db=db, repository=UserRepository())

UserService = Annotated[UserService,Depends(get_user_service)]
