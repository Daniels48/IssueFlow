from typing import Annotated

from fastapi import APIRouter, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.cookie import set_access_cookie, set_refresh_cookie, clear_auth_cookies
from app.modules.auth.dependencies import DBSession
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

login_form = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate,db: DBSession):
    service = AuthService(db=db, repository=UserRepository())
    user = await service.register(data)
    return user


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(data: LoginRequest, db: DBSession):
    service = AuthService(repository=UserRepository(), db=db)
    token_access = await service.login(username=data.username,password=data.password)
    response = Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
    set_access_cookie(response, token_access)
    # set_refresh_cookie(response, token_access)
    return response

@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response)
    return response
