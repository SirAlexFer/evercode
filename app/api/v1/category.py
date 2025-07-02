from typing import List

from fastapi import APIRouter, Depends, status, Response
from pydantic import BaseModel, ConfigDict

from app.services.category import CategoryService, get_category_service
from app.core.jwt import get_current_payload
from app.schemas.category import CategoryCreate, CategoryResponse


router = APIRouter(prefix="/categories", tags=["Категории"])


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание категории",
)
async def create_category(
    data: CategoryCreate,
    payload: dict = Depends(get_current_payload),
    service: CategoryService = Depends(get_category_service),
):
    """
    Создает новую категорию для аутентифицированного пользователя.
    """
    user_id = int(payload.get("sub"))
    return await service.create_category(user_id, data.name, data.color)


@router.get(
    "/",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение списка категорий",
)
async def list_categories(
    payload: dict = Depends(get_current_payload),
    service: CategoryService = Depends(get_category_service),
):
    """
    Возвращает список всех категорий текущего пользователя.
    """
    user_id = int(payload.get("sub"))
    return await service.get_categories(user_id)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление категории",
)
async def delete_category(
    category_id: int,
    payload: dict = Depends(get_current_payload),
    service: CategoryService = Depends(get_category_service),
):
    """
    Удаляет категорию по ID для текущего пользователя.
    """
    # Можно сюда добавить проверку, что категория принадлежит именно этому user_id
    await service.delete_category(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
