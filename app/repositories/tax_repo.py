"""
Tax repository for database operations.
"""
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax import TaxFiling, TaxObligation


class TaxRepository:
    """Tax filing database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Tax Filing operations

    async def create_filing(self, filing: TaxFiling) -> TaxFiling:
        """Create a new tax filing."""
        self.db.add(filing)
        await self.db.flush()
        await self.db.refresh(filing)
        return filing

    async def get_filing_by_id(
        self,
        filing_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> TaxFiling | None:
        """Get tax filing by ID."""
        query = select(TaxFiling).where(TaxFiling.id == filing_id)
        if user_id:
            query = query.where(TaxFiling.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_filings_by_user(
        self,
        user_id: uuid.UUID,
        tax_type: str | None = None,
        year: int | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TaxFiling]:
        """Get tax filings for a user."""
        query = (
            select(TaxFiling)
            .where(TaxFiling.user_id == user_id)
            .order_by(TaxFiling.filed_at.desc())
        )

        if tax_type:
            query = query.where(TaxFiling.tax_type == tax_type)
        if year:
            query = query.where(TaxFiling.tax_year == year)
        if status:
            query = query.where(TaxFiling.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_filings_by_user(
        self,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        """Count tax filings for a user."""
        query = (
            select(func.count(TaxFiling.id))
            .where(TaxFiling.user_id == user_id)
        )
        if status:
            query = query.where(TaxFiling.status == status)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_filing_by_year_and_type(
        self,
        user_id: uuid.UUID,
        tax_year: int,
        tax_type: str,
    ) -> TaxFiling | None:
        """Get filing for specific year and type."""
        result = await self.db.execute(
            select(TaxFiling)
            .where(TaxFiling.user_id == user_id)
            .where(TaxFiling.tax_year == tax_year)
            .where(TaxFiling.tax_type == tax_type)
        )
        return result.scalar_one_or_none()

    async def get_total_taxes_paid(
        self,
        user_id: uuid.UUID,
        year: int | None = None,
    ) -> float:
        """Get total taxes paid by user."""
        query = (
            select(func.sum(TaxFiling.amount))
            .where(TaxFiling.user_id == user_id)
            .where(TaxFiling.status == "completed")
        )
        if year:
            query = query.where(TaxFiling.tax_year == year)

        result = await self.db.execute(query)
        return float(result.scalar() or 0)

    # Tax Obligation operations

    async def create_obligation(self, obligation: TaxObligation) -> TaxObligation:
        """Create a new tax obligation."""
        self.db.add(obligation)
        await self.db.flush()
        await self.db.refresh(obligation)
        return obligation

    async def get_obligations_by_user(
        self,
        user_id: uuid.UUID,
        is_paid: bool | None = None,
    ) -> list[TaxObligation]:
        """Get tax obligations for a user."""
        query = (
            select(TaxObligation)
            .where(TaxObligation.user_id == user_id)
            .order_by(TaxObligation.due_date.asc())
        )

        if is_paid is not None:
            query = query.where(TaxObligation.is_paid == is_paid)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_obligation_paid(
        self,
        obligation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Mark tax obligation as paid."""
        from sqlalchemy import update

        result = await self.db.execute(
            update(TaxObligation)
            .where(TaxObligation.id == obligation_id)
            .where(TaxObligation.user_id == user_id)
            .values(is_paid=True, paid_at=datetime.utcnow())
        )
        return result.rowcount > 0  # type: ignore
