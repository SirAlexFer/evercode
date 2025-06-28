from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.core.database import get_session


class TransactionService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_transactions(self, user_id: int) -> List[Transaction]:
        """
        Возвращает все транзакции пользователя.
        """
        result = await self.db.execute(
            select(Transaction).where(Transaction.user_id == user_id)
        )
        return result.scalars().all()

    async def get_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        """
        Возвращает одну транзакцию по ID, проверяя, что она принадлежит пользователю.
        """
        txn = await self.db.get(Transaction, transaction_id)
        if not txn or txn.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return txn

    async def create_transaction(self, user_id: int, data: TransactionCreate) -> Transaction:
        """
        Создаёт новую транзакцию для пользователя.
        """
        txn = Transaction(
            user_id=user_id,
            category_id=data.category_id,
            amount=data.amount,
            timestamp=data.timestamp or datetime.utcnow(),
            payment_method=data.payment_method,
            payment_type=data.payment_type,
        )
        self.db.add(txn)
        await self.db.commit()
        await self.db.refresh(txn)
        return txn

    async def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        """
        Удаляет транзакцию по ID, если она принадлежит пользователю.
        """
        txn = await self.get_transaction(transaction_id, user_id)
        await self.db.delete(txn)
        await self.db.commit()


# Dependency провайдер

def get_transaction_service(
    db_session: AsyncSession = Depends(get_session)
) -> TransactionService:
    return TransactionService(db_session)
