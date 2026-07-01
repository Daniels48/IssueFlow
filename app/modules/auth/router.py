from fastapi import APIRouter, status

from app.modules.auth.dependencies import DBSession
from app.modules.auth.schemas import UserLogin, Token
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate,db: DBSession):
    service = AuthService(db=db, repository=UserRepository())
    user = await service.register(data)
    return user


@router.post("/login", response_model=Token,status_code=status.HTTP_200_OK)
async def login(data: UserLogin, db: DBSession):
    service = AuthService(repository=UserRepository(),db=db)
    return await service.login(data)