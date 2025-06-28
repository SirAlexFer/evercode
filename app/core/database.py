from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

DATABASE_URL = settings.database_dsn

engine = create_async_engine(DATABASE_URL, echo=settings.pg_echo)
metadata = MetaData()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()
