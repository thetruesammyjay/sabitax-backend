"""
Bank account repository for database operations.
"""
import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank_account import BankAccount


class BankRepository:
    """Bank account database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, bank_account: BankAccount) -> BankAccount:
        """Create a new bank account link."""
        self.db.add(bank_account)
        await self.db.flush()
        await self.db.refresh(bank_account)
        return bank_account

    async def get_by_id(
        self,
        account_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> BankAccount | None:
        """Get bank account by ID."""
        query = select(BankAccount).where(BankAccount.id == account_id)
        if user_id:
            query = query.where(BankAccount.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> list[BankAccount]:
        """Get bank accounts for a user."""
        query = (
            select(BankAccount)
            .where(BankAccount.user_id == user_id)
            .order_by(BankAccount.linked_at.desc())
        )

        if status:
            query = query.where(BankAccount.status == status)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_provider_account_id(
        self,
        provider: str,
        provider_account_id: str,
    ) -> BankAccount | None:
        """Get bank account by provider and provider account ID."""
        result = await self.db.execute(
            select(BankAccount)
            .where(BankAccount.provider == provider)
            .where(BankAccount.provider_account_id == provider_account_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        account_id: uuid.UUID,
        user_id: uuid.UUID,
        **kwargs,
    ) -> BankAccount | None:
        """Update bank account."""
        await self.db.execute(
            update(BankAccount)
            .where(BankAccount.id == account_id)
            .where(BankAccount.user_id == user_id)
            .values(**kwargs)
        )
        return await self.get_by_id(account_id, user_id)

    async def update_sync_time(
        self,
        account_id: uuid.UUID,
    ) -> bool:
        """Update last synced timestamp."""
        result = await self.db.execute(
            update(BankAccount)
            .where(BankAccount.id == account_id)
            .values(last_synced_at=datetime.utcnow())
        )
        return result.rowcount > 0  # type: ignore

    async def delete(
        self,
        account_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete (unlink) bank account."""
        result = await self.db.execute(
            delete(BankAccount)
            .where(BankAccount.id == account_id)
            .where(BankAccount.user_id == user_id)
        )
        return result.rowcount > 0  # type: ignore
