from fastapi import APIRouter, Response, status

from app.modules.auth.cookie import (
    ACCESS_COOKIE,
    REFRESH_COOKIE,
    clear_auth_cookies,
    set_access_cookie,
    set_refresh_cookie,
)
from app.modules.auth.dependencies import CurrentUser, DBSession, ValidRefreshToken
from app.modules.auth.schemas import SessionModel
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.schema import LoginRequest, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, response: Response, db: DBSession):
    service = AuthService(db=db, repository=UserRepository())
    data_auth = await service.register(data)
    set_access_cookie(response, data_auth["data"][ACCESS_COOKIE])
    set_refresh_cookie(response, data_auth["data"][REFRESH_COOKIE])
    return data_auth["user"]


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(data: LoginRequest, response: Response, db: DBSession):
    service = AuthService(repository=UserRepository(), db=db)
    data_dict = await service.login(username=data.username,password=data.password)
    set_access_cookie(response, data_dict[ACCESS_COOKIE])
    set_refresh_cookie(response, data_dict[REFRESH_COOKIE])


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(token_refresh: ValidRefreshToken, response: Response, db: DBSession):
    service = AuthService(repository=UserRepository(), db=db)
    token_access = await service.refresh(refresh_token=token_refresh)
    set_access_cookie(response, token_access)


@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
async def logout(token_refresh: ValidRefreshToken, db: DBSession, response: Response, user: CurrentUser):
    service = AuthService(repository=UserRepository(), db=db)
    await service.logout_current(refresh_token=token_refresh, user=user)
    clear_auth_cookies(response)


@router.get("/all_session",response_model=list[SessionModel])
async def get_all_session(db: DBSession, user: CurrentUser):
    service = AuthService(repository=UserRepository(), db=db)
    return await service.get_all_session(user=user)