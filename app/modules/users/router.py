from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUser
from app.modules.users.schema import UserResponse

router = APIRouter(prefix="/users",tags=["Users"])

@router.get("/me",response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user