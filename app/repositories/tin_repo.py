"""
TIN repository for database operations.
"""
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tin import TINApplication


class TINRepository:
    """TIN application database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, application: TINApplication) -> TINApplication:
        """Create a new TIN application."""
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def get_by_id(
        self,
        application_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> TINApplication | None:
        """Get TIN application by ID."""
        query = select(TINApplication).where(TINApplication.id == application_id)
        if user_id:
            query = query.where(TINApplication.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_reference(
        self,
        reference_number: str,
    ) -> TINApplication | None:
        """Get TIN application by reference number."""
        result = await self.db.execute(
            select(TINApplication)
            .where(TINApplication.reference_number == reference_number)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> list[TINApplication]:
        """Get TIN applications for a user."""
        query = (
            select(TINApplication)
            .where(TINApplication.user_id == user_id)
            .order_by(TINApplication.applied_at.desc())
        )

        if status:
            query = query.where(TINApplication.status == status)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_latest_by_user(
        self,
        user_id: uuid.UUID,
    ) -> TINApplication | None:
        """Get the latest TIN application for a user."""
        result = await self.db.execute(
            select(TINApplication)
            .where(TINApplication.user_id == user_id)
            .order_by(TINApplication.applied_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        application_id: uuid.UUID,
        status: str,
        assigned_tin: str | None = None,
        rejection_reason: str | None = None,
    ) -> TINApplication | None:
        """Update TIN application status."""
        values = {
            "status": status,
            "processed_at": datetime.utcnow(),
        }
        if assigned_tin:
            values["assigned_tin"] = assigned_tin
        if rejection_reason:
            values["rejection_reason"] = rejection_reason

        await self.db.execute(
            update(TINApplication)
            .where(TINApplication.id == application_id)
            .values(**values)
        )
        return await self.get_by_id(application_id)

    async def update_documents(
        self,
        application_id: uuid.UUID,
        user_id: uuid.UUID,
        id_document_url: str | None = None,
        utility_bill_url: str | None = None,
    ) -> TINApplication | None:
        """Update TIN application documents."""
        values = {}
        if id_document_url:
            values["id_document_url"] = id_document_url
        if utility_bill_url:
            values["utility_bill_url"] = utility_bill_url

        if values:
            await self.db.execute(
                update(TINApplication)
                .where(TINApplication.id == application_id)
                .where(TINApplication.user_id == user_id)
                .values(**values)
            )
        return await self.get_by_id(application_id, user_id)
