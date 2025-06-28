from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    category_id: Optional[int]
    item: str
    quantity: int
    location: Optional[str] = None
    amount: Decimal
    timestamp: Optional[datetime] = None
    payment_method: str
    payment_type: str


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    item: str
    quantity: int
    location: Optional[str]
    amount: Decimal
    timestamp: datetime
    payment_method: str
    payment_type: str

    model_config = ConfigDict(from_attributes=True)
