from functools import lru_cache

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.database import get_session
from app.services.database import BaseDb
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.database import BaseDb, PostgresqlEngine


class UserService:
    def __init__(self, base_db: BaseDb) -> None:
        self.base_db = base_db

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(**user_create.dict())
        new_user = await self.base_db.create(user, User)
        return UserResponse.from_orm(new_user)


async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
    # достаем существующего пользователя
    user = await self.base_db.get_by_pk(user_id, User)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # применяем только те поля, что пришли
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    await self.base_db.commit()
    await self.base_db.refresh(user)
    return UserResponse.from_orm(user)


@lru_cache()
def get_user_service(db_session: AsyncSession = Depends(get_session)) -> UserService:

    db_engine = PostgresqlEngine(db_session)
    base_db = BaseDb(db_engine)
    return UserService(base_db)
