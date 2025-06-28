import jwt
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Optional
from functools import lru_cache

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import Depends, status

from app.core.settings import settings
from app.core.database import get_session
from app.services.database import BaseDb, PostgresqlEngine
from app.models.user import User
from app.schemas.user import TwoTokens


class AuthService:
    def __init__(self, base_db: BaseDb):
        self.base_db = base_db
        self.pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.secret_key = settings.authjwt_secret_key
        self.algorithm = settings.authjwt_algorithm

        # параметры жизни токенов можно вынести в Settings
        self.access_expires = timedelta(minutes=15)
        self.refresh_expires = timedelta(days=7)

    # ——— Работа с паролями ———
    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_ctx.verify(plain, hashed)

    def hash_password(self, password: str) -> str:
        return self.pwd_ctx.hash(password)

    # ——— Получение пользователя ———
    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self.base_db.get_by_key("email", email, User)
        return user

    async def login(self, email, hashed_password) -> Optional[TwoTokens]:
        user = await self.get_user_by_email(email)
        print(f"User found: {user}")
        if user:
            if user.check_password(hashed_password):
                return await self.create_tokens_pair(user)

        return None

    # ——— Генерация JWT ———
    def _create_token(self, user_data: dict, expires_delta: timedelta) -> str:
        now = datetime.now(tz=timezone.utc)
        expires_time = now + expires_delta

        payload = {
            "sub": str(user_data["id"]),    # уникальный идентификатор пользователя
            "email": user_data["email"],    # почта — опционально, если нужна
            "iat": now,                     # issued at
            "exp": expires_time,            # expiration time
        }

        token = jwt.encode(
            payload,
            key=self.secret_key,
            algorithm=self.algorithm,
        )
        return token

    def create_access_token(self, user_data) -> str:
        return self._create_token(user_data, self.access_expires)

    def create_refresh_token(self, user_data) -> str:
        return self._create_token(user_data, self.refresh_expires)

    # ——— Создание пары токенов без хранения ———
    async def create_tokens_pair(self, user: User) -> TwoTokens:
        user_data = {
            "email": user.email,
            "username": user.username,
            'id': user.id,
        }
        access = self.create_access_token(user_data)
        refresh = self.create_refresh_token(user_data)
        return TwoTokens(access_token=access, refresh_token=refresh)

    def verify_jwt(self, token: str) -> dict:
        """Декодирует JWT, проверяет подпись и срок, возвращает payload."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload


@lru_cache()
def get_auth_service(
    db_session: AsyncSession = Depends(get_session),
) -> AuthService:

    db_engine = PostgresqlEngine(db_session)
    base_db = BaseDb(db_engine)
    return AuthService(base_db)
