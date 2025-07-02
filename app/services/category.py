from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import Category
from app.core.database import get_session
from app.core.settings import default_categories


class CategoryService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_categories(self, user_id: int) -> List[Category]:
        """
        Возвращает список объектов Category для заданного пользователя.
        """
        result = await self.db.execute(
            select(Category).where(Category.user_id == user_id)
        )
        return result.scalars().all()

    async def get_category_names(self, user_id: int) -> List[str]:
        """
        Возвращает список имён категорий для заданного пользователя.
        """
        categories = await self.get_categories(user_id)
        return [cat.name for cat in categories]

    async def create_category(self, user_id: int, name: str, color: str) -> Category:
        """
        Создаёт новую категорию для пользователя.
        """
        # Проверим, что такой категории ещё нет
        existing = await self.db.execute(
            select(Category).where(Category.user_id == user_id, Category.name == name)
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists",
            )
        new_cat = Category(user_id=user_id, name=name, color=color)
        self.db.add(new_cat)
        await self.db.commit()
        await self.db.refresh(new_cat)
        return new_cat

    async def delete_category(self, category_id: int) -> None:
        """
        Удаляет категорию по её ID.
        """
        category = await self.db.get(Category, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        await self.db.delete(category)
        await self.db.commit()

    async def create_default_categories(self, user_id: int) -> List[Category]:
        """
        Добавляет набор категорий по умолчанию для нового пользователя и возвращает их.
        """
        default_names = default_categories
        created = []
        for name in default_names:
            cat = Category(user_id=user_id, name=name)
            self.db.add(cat)
            created.append(cat)
        await self.db.commit()
        for cat in created:
            await self.db.refresh(cat)
        return created


# Dependency


def get_category_service(
    db_session: AsyncSession = Depends(get_session),
) -> CategoryService:
    return CategoryService(db_session)
