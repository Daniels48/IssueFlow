from fastapi import APIRouter, status, Response

from app.modules.auth.cookie import (
    set_access_cookie, set_refresh_cookie, clear_auth_cookies, ACCESS_COOKIE, REFRESH_COOKIE
)
from app.modules.auth.dependencies import DBSession, ValidRefreshToken
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserResponse, LoginRequest


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: DBSession):
    service = AuthService(db=db, repository=UserRepository())
    user = await service.register(data)
    return user


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(data: LoginRequest, db: DBSession):
    service = AuthService(repository=UserRepository(), db=db)
    data_dict = await service.login(username=data.username,password=data.password)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    set_access_cookie(response, data_dict[ACCESS_COOKIE])
    set_refresh_cookie(response, data_dict[REFRESH_COOKIE])
    return response


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(token_refresh: ValidRefreshToken, db: DBSession):
    service = AuthService(repository=UserRepository(), db=db)
    token_access = await service.refresh(refresh_token=token_refresh)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    set_access_cookie(response, token_access)
    return response


@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
async def logout(token_refresh: ValidRefreshToken, db: DBSession) -> Response:
    service = AuthService(repository=UserRepository(), db=db)
    await service.logout(refresh_token=token_refresh)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response)
    return response
