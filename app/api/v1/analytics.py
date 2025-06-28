from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Response, status, Query

from app.core.jwt import get_current_payload
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction import AnalyticsService, get_analytics_service


router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get(
    "/total_sum",
    response_model=List[TransactionResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение аналитики по транзакциям",
)
async def get_total_spent(
    date_from: Optional[datetime] = Query(
        None,
        description="Начальная дата фильтра (включительно), формат ISO 8601"
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="Конечная дата фильтра (включительно), формат ISO 8601"
    ),
    payload: dict = Depends(get_current_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Возвращает общую сумму потраченных средств текущего пользователя.
    Дополнительные параметры:
    - date_from: ISO-формат начальной даты (включительно)
    - date_to: ISO-формат конечной даты (включительно)
    """
    user_id = int(payload.get("sub"))
    total_spent = await service.get_total_spent(user_id, date_from, date_to)
    return {"total_spent": total_spent}