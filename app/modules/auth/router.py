from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.dependencies import DBSession
from app.modules.auth.schemas import Token
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

login_form = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate,db: DBSession):
    service = AuthService(db=db, repository=UserRepository())
    user = await service.register(data)
    return user


@router.post("/login",response_model=Token,status_code=status.HTTP_200_OK,)
async def login(form_data: login_form,db: DBSession):
    service = AuthService(repository=UserRepository(), db=db)
    return await service.login(username=form_data.username,password=form_data.password)