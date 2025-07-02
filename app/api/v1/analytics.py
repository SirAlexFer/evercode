from typing import List, Optional, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, Response, status, Query

from app.core.jwt import get_current_payload
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction import AnalyticsService, get_analytics_service


router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get(
    "/total_sum",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Получение общей суммы расходов",
)
async def get_total_spent(
    date_from: Optional[datetime] = Query(
        None, description="Начальная дата фильтра (включительно), формат ISO 8601"
    ),
    date_to: Optional[datetime] = Query(
        None, description="Конечная дата фильтра (включительно), формат ISO 8601"
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


@router.get(
    "/top_categories",
    response_model=List,
    status_code=status.HTTP_200_OK,
    summary="Получение топ категорий по тратам",
)
async def get_top_categories(
    limit: int = Query(
        5, ge=1, le=100, description="Количество категорий для отображения (1-100)"
    ),
    date_from: Optional[datetime] = Query(
        None, description="Начальная дата фильтра (включительно), формат ISO 8601"
    ),
    date_to: Optional[datetime] = Query(
        None, description="Конечная дата фильтра (включительно), формат ISO 8601"
    ),
    payload: dict = Depends(get_current_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Возвращает топ N категорий по сумме трат.
    Дополнительные параметры:
    - limit: количество категорий для отображения (1-100)
    - date_from: ISO-формат начальной даты (включительно)
    - date_to: ISO-формат конечной даты (включительно)
    """
    user_id = int(payload.get("sub"))
    return await service.get_top_categories(user_id, limit, date_from, date_to)


@router.get(
    "/daily_spending",
    response_model=List,
    status_code=status.HTTP_200_OK,
    summary="Получение ежедневных трат",
)
async def get_daily_spending(
    days_back: int = Query(
        30, ge=1, le=365, description="Количество дней назад для анализа (1-365)"
    ),
    payload: dict = Depends(get_current_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Возвращает ежедневные траты текущего пользователя.
    Дополнительные параметры:
    - date_from: ISO-формат начальной даты (включительно)
    - date_to: ISO-формат конечной даты (включительно)
    """
    user_id = int(payload.get("sub"))
    return await service.get_daily_spending(user_id, days_back)


@router.get(
    "/forecast_month_end",
    response_model=float,
    status_code=status.HTTP_200_OK,
    summary="Получение прогноза трат",
)
async def get_forecast_month_end(
    date_from: Optional[datetime] = Query(
        None, description="Начальная дата фильтра (включительно), формат ISO 8601"
    ),
    payload: dict = Depends(get_current_payload),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Возвращает прогноз трат текущего пользователя.
    Дополнительные параметры:
    - date_from: ISO-формат начальной даты (включительно)
    - date_to: ISO-формат конечной даты (включительно)
    """
    user_id = int(payload.get("sub"))
    return await service.forecast_month_end(user_id, date_from)
