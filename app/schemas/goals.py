from pydantic import BaseModel, ConfigDict
from typing import Optional

from datetime import datetime
from decimal import Decimal


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
