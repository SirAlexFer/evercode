from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.database import get_session
from app.services.database import BaseDb
from app.schemas.user import UserCreate, UserResponse
from app.services.database import BaseDb, PostgresqlEngine


class UserService:
    def __init__(self, base_db: BaseDb) -> None:
        self.base_db = base_db

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(**user_create.dict())
        new_user = await self.base_db.create(user, User)
        return UserResponse.from_orm(new_user)


@lru_cache()
def get_user_service(db_session: AsyncSession = Depends(get_session)) -> UserService:

    db_engine = PostgresqlEngine(db_session)
    base_db = BaseDb(db_engine)
    return UserService(base_db)
