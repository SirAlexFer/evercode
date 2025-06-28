from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import Transaction
from app.schemas.transaction import TransactionCreate
from app.core.database import get_session


class TransactionService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_transactions(
        self,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Transaction]:
        """
        Возвращает все транзакции пользователя,
        опционально отфильтрованные по диапазону дат.
        :param user_id: ID пользователя
        :param date_from: начальная дата (включительно)
        :param date_to: конечная дата (включительно)
        """
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        if date_from and date_to:
            stmt = stmt.where(
                Transaction.timestamp >= date_from, Transaction.timestamp <= date_to
            )
        elif date_from:
            stmt = stmt.where(Transaction.timestamp >= date_from)
        elif date_to:
            stmt = stmt.where(Transaction.timestamp <= date_to)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        """
        Возвращает одну транзакцию по ID, проверяя, что она принадлежит пользователю.
        """
        txn = await self.db.get(Transaction, transaction_id)
        if not txn or txn.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
        return txn

    async def create_transaction(
        self, user_id: int, data: TransactionCreate
    ) -> Transaction:
        """
        Создаёт новую транзакцию для пользователя.
        """
        txn = Transaction(
            user_id=user_id,
            category_id=data.category_id,
            item=data.item,
            quantity=data.quantity,
            location=data.location,
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


class AnalyticsService(TransactionService):
    """
    Сервис для аналитики транзакций.
    Наследуется от TransactionService для доступа к транзакциям.
    """

    async def get_total_spent(
        self,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> float:
        """
        Возвращает общую сумму потраченных средств пользователем.
        """
        transactions = await self.get_transactions(user_id, date_from, date_to)
        return sum(txn.amount for txn in transactions)


def get_transaction_service(
    db_session: AsyncSession = Depends(get_session),
) -> TransactionService:
    return TransactionService(db_session)


def get_analytics_service(
    db_session: AsyncSession = Depends(get_session),
) -> AnalyticsService:
    return AnalyticsService(db_session)
