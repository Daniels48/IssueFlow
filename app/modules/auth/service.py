from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User
from app.modules.auth.jwt import JWTService
from app.modules.auth.password import PasswordService
from app.modules.auth.schemas import UserLogin, Token
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository, db: AsyncSession):
        self.repository = repository
        self.db = db

    async def register(self, data: UserCreate) -> User:
        if await self.repository.get_by_email(self.db, data.email):
            raise ValueError("Email already exists")

        if await self.repository.get_by_username(self.db, data.username):
            raise ValueError("Username already exists")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=PasswordService.hash_password(data.password)
        )

        user = await self.repository.create(db=self.db, user=user)

        await self.db.commit()

        return user

    async def login(self, username: str, password: str) -> Token:
        user = await self.repository.get_by_username(self.db, username)

        if not user:
            raise ValueError("Invalid credentials")

        if not PasswordService.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        access_token = JWTService.create_access_token(user.public_id)

        return Token(access_token=access_token)