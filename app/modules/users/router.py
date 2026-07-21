from uuid import UUID

from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUser
from app.modules.project_members.service import MemberService
from app.modules.projects.schema import UserShortResponse
from app.modules.users.schema import UserResponse
from app.modules.users.service import UserService

router = APIRouter(prefix="/users",tags=["Users"])

@router.get("/me",response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user

@router.get("/search", response_model=list[UserShortResponse])
async def search_users(query: str, project_id: UUID, current_user: CurrentUser, service: UserService):
    return await service.search_users(query=query, project_id=project_id, current_user_id=current_user.id)