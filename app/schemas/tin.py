"""
TIN schemas for request/response validation.
"""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


TINStatus = Literal["processing", "approved", "rejected", "pending_documents"]


class TINStatusResponse(BaseModel):
    """User's TIN status response."""

    has_tin: bool
    tin: str | None = None  # Masked TIN
    status: str  # verified, pending, none
    applied_at: datetime | None = None


class TINApplicationRequest(BaseModel):
    """TIN application request."""

    nin: str = Field(..., min_length=11, max_length=20)
    date_of_birth: date
    id_document_url: str | None = None


class TINApplicationResponse(BaseModel):
    """TIN application submission response."""

    application_id: str
    reference_number: str
    status: str
    estimated_completion: str = "3-5 business days"


class TINApplicationStatusResponse(BaseModel):
    """TIN application status response."""

    id: str
    reference_number: str | None
    status: str
    applied_at: datetime
    processed_at: datetime | None
    assigned_tin: str | None = None
    rejection_reason: str | None = None

    model_config = {"from_attributes": True}


class TINDocumentUploadResponse(BaseModel):
    """TIN document upload response."""

    document_url: str
    document_type: str
    uploaded_at: datetime
