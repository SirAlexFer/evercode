from abc import ABC, abstractmethod
from typing import Any, List, Optional
from uuid import UUID

from app.models.base import ModelBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncDbEngine(ABC):
    @abstractmethod
    async def get_by_id(self, object_id: UUID, Object: Any) -> Optional[Any]:
        pass

    @abstractmethod
    async def create(self, object_data: Any) -> Any:
        pass

    @abstractmethod
    async def update(self, object_id: UUID, object_data: Any) -> Optional[Any]:
        pass

    @abstractmethod
    async def delete(self, object_id: UUID) -> None:
        pass

    @abstractmethod
    async def list_all(self, Object: Any) -> List[Any]:
        pass


class PostgresqlEngine(AsyncDbEngine):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_id(self, object_id: UUID, Object: Any) -> Optional[Any]:
        query = select(Object).where(Object.id == object_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, object_data: Any, Object: Any) -> Any:
        new_object = object_data
        self.db_session.add(new_object)
        await self.db_session.commit()
        await self.db_session.refresh(new_object)
        return new_object

    async def update(
        self, object_id: UUID, object_data: Any, Object: Any
    ) -> Optional[Any]:
        obj = await self.get_by_id(object_id, Object)
        if obj:
            if hasattr(object_data, "dict"):
                update_data = object_data.dict(exclude_unset=True)
            else:
                update_data = object_data

            for key, value in update_data.items():
                setattr(obj, key, value)

            await self.db_session.commit()
            await self.db_session.refresh(obj)

        return obj

    async def delete(self, object_id: UUID, Object: Any) -> None:
        obj = await self.get_by_id(object_id, Object)
        if obj:
            await self.db_session.delete(obj)
            await self.db_session.commit()

    async def list_all(self, Object: Any) -> List[Any]:
        query = select(Object)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def execute(self, query) -> Any:
        result = await self.db_session.execute(query)
        return result


class BaseDb:
    def __init__(self, db_engine: AsyncDbEngine):
        self.db_engine = db_engine

    async def get_by_id(self, object_id: UUID, Object: Any) -> Optional[Any]:
        return await self.db_engine.get_by_id(object_id, Object)

    async def create(self, object_data: Any, Object: Any) -> Any:
        return await self.db_engine.create(object_data, Object)

    async def update(
        self, object_id: UUID, object_data: Any, Object: Any
    ) -> Optional[Any]:
        return await self.db_engine.update(object_id, object_data, Object)

    async def delete(self, object_id: UUID, Object: Any) -> None:
        await self.db_engine.delete(object_id, Object)

    async def list_all(self, Object: Any) -> List[Any]:
        return await self.db_engine.list_all(Object)

    async def get_by_key(self, key: str, value: Any, Object: Any) -> Optional[Any]:
        query = select(Object).where(getattr(Object, key) == value)
        result = await self.db_engine.execute(query)
        return result.scalars().first()

    async def execute(self, query) -> Any:
        return await self.db_engine.execute(query)
