from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
from fastapi import Form


class PaymentMethod(str, Enum):
    debit_card = "Debit Card"
    digital_wallet = "Digital Wallet"
    cash = "Cash"


class PaymentType(str, Enum):
    expense = "Expense"
    income  = "Income"


class TransactionCreate(BaseModel):
    category_name: Optional[str]
    item: str
    quantity: int
    location: Optional[str] = None
    amount: Decimal
    timestamp: Optional[datetime] = None
    payment_method: PaymentMethod
    payment_type: PaymentType


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


class AnalyticsResponse(BaseModel):
    total_spent: Decimal

    model_config = ConfigDict(from_attributes=True)
