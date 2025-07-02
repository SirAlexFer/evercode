# app/api/v1/goals.py
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.core.jwt import get_current_payload
from app.services.goals import GoalsService, get_goals_service

router = APIRouter(prefix="/goals", tags=["Цели"])


class GoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    amount: Decimal
    date_goals: datetime


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    date_goals: Optional[datetime] = None


class GoalResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    amount: Decimal
    date_goals: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую цель",
)
async def create_goal(
    data: GoalCreate,
    payload: dict = Depends(get_current_payload),
    service: GoalsService = Depends(get_goals_service),
):
    user_id = int(payload["sub"])
    return await service.create_goal(user_id, data)


@router.get(
    "",
    response_model=List[GoalResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все цели пользователя",
)
async def list_goals(
    payload: dict = Depends(get_current_payload),
    service: GoalsService = Depends(get_goals_service),
):
    user_id = int(payload["sub"])
    return await service.get_goals(user_id)


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить одну цель по ID",
)
async def get_goal(
    goal_id: int,
    payload: dict = Depends(get_current_payload),
    service: GoalsService = Depends(get_goals_service),
):
    user_id = int(payload["sub"])
    goal = await service.get_goal(goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.put(
    "/{goal_id}",
    response_model=GoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить данные цели",
)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    payload: dict = Depends(get_current_payload),
    service: GoalsService = Depends(get_goals_service),
):
    user_id = int(payload["sub"])
    updated = await service.update_goal(goal_id, user_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return updated


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить цель",
)
async def delete_goal(
    goal_id: int,
    payload: dict = Depends(get_current_payload),
    service: GoalsService = Depends(get_goals_service),
):
    user_id = int(payload["sub"])
    success = await service.delete_goal(goal_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return
