"""
Transaction repository for database operations.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class TransactionRepository:
    """Transaction database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        return transaction

    async def get_by_id(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Transaction | None:
        """Get transaction by ID, optionally filtered by user."""
        query = select(Transaction).where(Transaction.id == transaction_id)
        if user_id:
            query = query.where(Transaction.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        type: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaction]:
        """Get transactions for a user with filters."""
        query = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
        )

        if type:
            query = query.where(Transaction.type == type)
        if category:
            query = query.where(Transaction.category == category)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: uuid.UUID,
        type: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Count transactions for a user with filters."""
        query = (
            select(func.count(Transaction.id))
            .where(Transaction.user_id == user_id)
        )

        if type:
            query = query.where(Transaction.type == type)
        if category:
            query = query.where(Transaction.category == category)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_totals_by_user(
        self,
        user_id: uuid.UUID,
        year: int | None = None,
    ) -> dict[str, Decimal]:
        """Get income and expense totals for a user."""
        query = select(
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        ).where(Transaction.user_id == user_id)

        if year:
            query = query.where(
                func.extract("year", Transaction.transaction_date) == year
            )

        query = query.group_by(Transaction.type)
        result = await self.db.execute(query)
        rows = result.all()

        totals = {"income": Decimal("0"), "expense": Decimal("0")}
        for row in rows:
            totals[row.type] = row.total or Decimal("0")

        return totals

    async def get_category_totals(
        self,
        user_id: uuid.UUID,
        type: str = "expense",
        year: int | None = None,
        limit: int = 10,
    ) -> list[tuple[str, Decimal]]:
        """Get spending by category for a user."""
        query = (
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total"),
            )
            .where(Transaction.user_id == user_id)
            .where(Transaction.type == type)
            .where(Transaction.category.isnot(None))
        )

        if year:
            query = query.where(
                func.extract("year", Transaction.transaction_date) == year
            )

        query = (
            query.group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [(row.category, row.total) for row in result.all()]

    async def update(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
        **kwargs,
    ) -> Transaction | None:
        """Update transaction by ID."""
        await self.db.execute(
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .where(Transaction.user_id == user_id)
            .values(**kwargs)
        )
        return await self.get_by_id(transaction_id, user_id)

    async def delete(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete transaction by ID."""
        result = await self.db.execute(
            delete(Transaction)
            .where(Transaction.id == transaction_id)
            .where(Transaction.user_id == user_id)
        )
        return result.rowcount > 0  # type: ignore
