"""
Referral repository for database operations.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral


class ReferralRepository:
    """Referral database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, referral: Referral) -> Referral:
        """Create a new referral."""
        self.db.add(referral)
        await self.db.flush()
        await self.db.refresh(referral)
        return referral

    async def get_by_id(
        self,
        referral_id: uuid.UUID,
    ) -> Referral | None:
        """Get referral by ID."""
        result = await self.db.execute(
            select(Referral).where(Referral.id == referral_id)
        )
        return result.scalar_one_or_none()

    async def get_by_referrer(
        self,
        referrer_id: uuid.UUID,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Referral]:
        """Get referrals made by a user."""
        query = (
            select(Referral)
            .where(Referral.referrer_id == referrer_id)
            .order_by(Referral.created_at.desc())
        )

        if status:
            query = query.where(Referral.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_referrer(
        self,
        referrer_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        """Count referrals by referrer."""
        query = (
            select(func.count(Referral.id))
            .where(Referral.referrer_id == referrer_id)
        )
        if status:
            query = query.where(Referral.status == status)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_total_earnings(
        self,
        referrer_id: uuid.UUID,
    ) -> Decimal:
        """Get total referral earnings for a user."""
        result = await self.db.execute(
            select(func.sum(Referral.reward_amount))
            .where(Referral.referrer_id == referrer_id)
            .where(Referral.status == "completed")
            .where(Referral.reward_paid == True)  # noqa: E712
        )
        return Decimal(str(result.scalar() or 0))

    async def get_monthly_earnings(
        self,
        referrer_id: uuid.UUID,
        year: int,
        month: int,
    ) -> Decimal:
        """Get monthly referral earnings for a user."""
        result = await self.db.execute(
            select(func.sum(Referral.reward_amount))
            .where(Referral.referrer_id == referrer_id)
            .where(Referral.status == "completed")
            .where(func.extract("year", Referral.completed_at) == year)
            .where(func.extract("month", Referral.completed_at) == month)
        )
        return Decimal(str(result.scalar() or 0))

    async def get_by_referred(
        self,
        referred_id: uuid.UUID,
    ) -> Referral | None:
        """Get referral where user was referred."""
        result = await self.db.execute(
            select(Referral).where(Referral.referred_id == referred_id)
        )
        return result.scalar_one_or_none()

    async def complete_referral(
        self,
        referral_id: uuid.UUID,
    ) -> Referral | None:
        """Mark referral as completed."""
        await self.db.execute(
            update(Referral)
            .where(Referral.id == referral_id)
            .values(
                status="completed",
                completed_at=datetime.utcnow(),
            )
        )
        return await self.get_by_id(referral_id)

    async def mark_reward_paid(
        self,
        referral_id: uuid.UUID,
    ) -> bool:
        """Mark referral reward as paid."""
        result = await self.db.execute(
            update(Referral)
            .where(Referral.id == referral_id)
            .values(reward_paid=True)
        )
        return result.rowcount > 0  # type: ignore
