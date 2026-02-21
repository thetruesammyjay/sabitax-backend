"""
TIN service for Tax Identification Number applications.
"""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.utils import generate_tin_reference, mask_tin
from app.models.tin import TINApplication
from app.repositories.tin_repo import TINRepository
from app.repositories.user_repo import UserRepository
from app.schemas.tin import (
    TINApplicationRequest,
    TINApplicationResponse,
    TINApplicationStatusResponse,
    TINStatusResponse,
)


class TINService:
    """TIN application business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tin_repo = TINRepository(db)
        self.user_repo = UserRepository(db)

    async def get_status(
        self,
        user_id: uuid.UUID,
    ) -> TINStatusResponse:
        """
        Get user's TIN status.

        Args:
            user_id: User's ID

        Returns:
            TINStatusResponse with TIN info
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Check for pending application
        latest_application = await self.tin_repo.get_latest_by_user(user_id)

        if user.tin and user.tin_verified:
            return TINStatusResponse(
                has_tin=True,
                tin=mask_tin(user.tin),
                status="verified",
                applied_at=latest_application.applied_at if latest_application else None,
            )
        elif latest_application:
            return TINStatusResponse(
                has_tin=False,
                tin=None,
                status=latest_application.status,
                applied_at=latest_application.applied_at,
            )
        else:
            return TINStatusResponse(
                has_tin=False,
                tin=None,
                status="none",
                applied_at=None,
            )

    async def apply(
        self,
        user_id: uuid.UUID,
        data: TINApplicationRequest,
    ) -> TINApplicationResponse:
        """
        Apply for TIN.

        Args:
            user_id: User's ID
            data: Application data

        Returns:
            TINApplicationResponse with application details
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Check if already has TIN
        if user.tin and user.tin_verified:
            raise BadRequestError("You already have a verified TIN")

        # Check for pending application
        latest = await self.tin_repo.get_latest_by_user(user_id)
        if latest and latest.status == "processing":
            raise BadRequestError(
                "You have a pending TIN application. Please wait for it to be processed."
            )

        # Create application
        application = TINApplication(
            user_id=user_id,
            nin=data.nin,
            date_of_birth=data.date_of_birth,
            id_document_url=data.id_document_url,
            reference_number=generate_tin_reference(),
            status="processing",
            applied_at=datetime.now(timezone.utc),
        )

        application = await self.tin_repo.create(application)

        return TINApplicationResponse(
            application_id=str(application.id),
            reference_number=application.reference_number or "",
            status=application.status,
            estimated_completion="3-5 business days",
        )

    async def get_application_status(
        self,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
    ) -> TINApplicationStatusResponse:
        """
        Get TIN application status.

        Args:
            user_id: User's ID
            application_id: Application ID

        Returns:
            TINApplicationStatusResponse with status details
        """
        application = await self.tin_repo.get_by_id(application_id, user_id)

        if not application:
            raise NotFoundError("TIN application not found", resource="tin_application")

        return TINApplicationStatusResponse(
            id=str(application.id),
            reference_number=application.reference_number,
            status=application.status,
            applied_at=application.applied_at,
            processed_at=application.processed_at,
            assigned_tin=mask_tin(application.assigned_tin) if application.assigned_tin else None,
            rejection_reason=application.rejection_reason,
        )

    async def upload_document(
        self,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
        document_type: str,
        document_url: str,
    ) -> dict:
        """
        Upload document for TIN application.

        Args:
            user_id: User's ID
            application_id: Application ID
            document_type: Type of document (id, utility_bill)
            document_url: URL of uploaded document

        Returns:
            Upload confirmation
        """
        application = await self.tin_repo.get_by_id(application_id, user_id)

        if not application:
            raise NotFoundError("TIN application not found", resource="tin_application")

        if application.status not in ["processing", "pending_documents"]:
            raise BadRequestError("Cannot upload documents for this application")

        # Update document URL
        if document_type == "id":
            await self.tin_repo.update_documents(
                application_id, user_id, id_document_url=document_url
            )
        elif document_type == "utility_bill":
            await self.tin_repo.update_documents(
                application_id, user_id, utility_bill_url=document_url
            )

        return {
            "document_url": document_url,
            "document_type": document_type,
            "uploaded_at": datetime.now(timezone.utc),
        }

    async def process_application(
        self,
        application_id: uuid.UUID,
        status: str,
        assigned_tin: str | None = None,
        rejection_reason: str | None = None,
    ) -> TINApplicationStatusResponse:
        """
        Process TIN application (admin/system use).

        Args:
            application_id: Application ID
            status: New status
            assigned_tin: Assigned TIN if approved
            rejection_reason: Reason if rejected

        Returns:
            Updated application status
        """
        application = await self.tin_repo.update_status(
            application_id,
            status=status,
            assigned_tin=assigned_tin,
            rejection_reason=rejection_reason,
        )

        if not application:
            raise NotFoundError("TIN application not found", resource="tin_application")

        # If approved, update user's TIN
        if status == "approved" and assigned_tin:
            await self.user_repo.set_tin(
                application.user_id,
                tin=assigned_tin,
                verified=True,
            )

        return TINApplicationStatusResponse(
            id=str(application.id),
            reference_number=application.reference_number,
            status=application.status,
            applied_at=application.applied_at,
            processed_at=application.processed_at,
            assigned_tin=mask_tin(application.assigned_tin) if application.assigned_tin else None,
            rejection_reason=application.rejection_reason,
        )
