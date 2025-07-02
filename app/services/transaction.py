from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import Transaction, Category
from app.schemas.transaction import TransactionCreate
from app.core.database import get_session
from app.core.settings import default_categories


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
        category_id: Optional[int] = None
        if data.category_name:
            q = select(Category).where(
                Category.user_id == user_id, Category.name == data.category_name
            )
            res = await self.db.execute(q)
            category = res.scalars().first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{data.category_name}' not found for user",
                )
            category_id = category.id
        txn = Transaction(
            user_id=user_id,
            category_id=category_id,
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

    async def get_top_categories(
        self,
        user_id: int,
        n: int = 10,
        date_from: datetime = None,
        date_to: datetime = None,
    ) -> List[Dict[str, float]]:
        """
        Возвращает топ N категорий по сумме трат.
        Формат: [{'category_id': int, 'total_spent': float}, ...]
        """

        stmt = (
            select(
                Category.name.label('category_name'),
                func.sum(Transaction.amount).label('total_spent')
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
        )
        if date_from:
            stmt = stmt.where(Transaction.timestamp >= date_from)
        if date_to:
            stmt = stmt.where(Transaction.timestamp <= date_to)
        stmt = stmt.group_by(Category.name)
        stmt = stmt.order_by(func.sum(Transaction.amount).desc())
        stmt = stmt.limit(n)

        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {'category_name': row.category_name, 'total_spent': float(row.total_spent)}
            for row in rows
        ]

    async def get_daily_spending(
        self, user_id: int, days_back: int = 30
    ) -> List[Dict[str, float]]:
        """
        Динамика ежедневных трат за последние days_back дней.
        Формат: [{'date': 'YYYY-MM-DD', 'total_spent': float}, ...]
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        stmt = (
            select(
                func.date(Transaction.timestamp).label("date"),
                func.sum(Transaction.amount).label("total_spent"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.timestamp
                >= datetime.combine(start_date, datetime.min.time()),
                Transaction.timestamp
                <= datetime.combine(end_date, datetime.max.time()),
            )
            .group_by(func.date(Transaction.timestamp))
        )

        stmt = stmt.order_by(func.date(Transaction.timestamp))
        result = await self.db.execute(stmt)
        rows = result.all()
        # заполняем пропущенные дни
        date_map = {row.date: float(row.total_spent) for row in rows}
        output = []
        for i in range(days_back + 1):
            day = start_date + timedelta(days=i)
            output.append(
                {"date": day.isoformat(), "total_spent": date_map.get(day, 0.0)}
            )
        return output

    async def forecast_month_end(
        self, user_id: int, date_from: datetime = None
    ) -> float:
        """
        Прогноз суммы трат до конца текущего месяца на основе среднего дневного расхода.
        Если date_from указан, расчёт от этой даты; иначе — с начала месяца.
        """
        today = date.today()
        # начало расчёта
        if date_from:
            start = date_from.date()
        else:
            start = today.replace(day=1)

        # получаем реальные траты с start по today
        stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.timestamp >= datetime.combine(start, datetime.min.time()),
            Transaction.timestamp <= datetime.combine(today, datetime.max.time()),
        )
        result = await self.db.execute(stmt)
        total_spent = result.scalar() or 0.0

        days_used = (today - start).days + 1
        avg_per_day = total_spent / days_used if days_used > 0 else 0.0

        # сколько дней осталось до конца месяца
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        days_left = (next_month - today).days

        forecast = avg_per_day * days_left
        return float(forecast)


def get_transaction_service(
    db_session: AsyncSession = Depends(get_session),
) -> TransactionService:
    return TransactionService(db_session)


def get_analytics_service(
    db_session: AsyncSession = Depends(get_session),
) -> AnalyticsService:
    return AnalyticsService(db_session)
