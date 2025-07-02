from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Response, status, Query, Body, Form

from app.core.jwt import get_current_payload
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.transaction import PaymentMethod, PaymentType
from app.services.transaction import TransactionService, get_transaction_service
from app.services.category import get_category_service, CategoryService

router = APIRouter(prefix="/transactions", tags=["Транзакции"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание транзакции",
)
async def create_transaction(
    data: TransactionCreate = Body(...),
    payload: dict = Depends(get_current_payload),
    service: TransactionService = Depends(get_transaction_service),
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Создает новую транзакцию для текущего пользователя.
    """
    user_id = int(payload.get("sub"))
    return await service.create_transaction(user_id, data)


@router.get(
    "",
    response_model=List[TransactionResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение списка транзакций",
)
async def list_transactions(
    date_from: Optional[datetime] = Query(
        None, description="Начальная дата фильтра (inclusive), формат ISO 8601"
    ),
    date_to: Optional[datetime] = Query(
        None, description="Конечная дата фильтра (inclusive), формат ISO 8601"
    ),
    payload: dict = Depends(get_current_payload),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Возвращает список всех транзакций текущего пользователя.
    Дополнительные параметры:
    - date_from: ISO-формат начальной даты (включительно)
    - date_to: ISO-формат конечной даты (включительно)
    """
    user_id = int(payload.get("sub"))
    return await service.get_transactions(user_id, date_from, date_to)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение транзакции по ID",
)
async def get_transaction(
    transaction_id: int,
    payload: dict = Depends(get_current_payload),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Возвращает одну транзакцию по ID для текущего пользователя.
    """
    user_id = int(payload.get("sub"))
    return await service.get_transaction(transaction_id, user_id)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление транзакции",
)
async def delete_transaction(
    transaction_id: int,
    payload: dict = Depends(get_current_payload),
    service: TransactionService = Depends(get_transaction_service),
):
    """
    Удаляет транзакцию по ID для текущего пользователя.
    """
    user_id = int(payload.get("sub"))
    await service.delete_transaction(transaction_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
