"""
Transaction schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


TransactionType = Literal["income", "expense"]


class TransactionBase(BaseModel):
    """Base transaction schema."""

    title: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: TransactionType
    category: str | None = Field(None, max_length=50)
    description: str | None = None


class TransactionCreate(TransactionBase):
    """Transaction creation request."""

    receipt_url: str | None = None
    transaction_date: datetime | None = None  # Defaults to now if not provided


class TransactionUpdate(BaseModel):
    """Transaction update request."""

    title: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    type: TransactionType | None = None
    category: str | None = None
    description: str | None = None
    receipt_url: str | None = None
    transaction_date: datetime | None = None


class TransactionResponse(BaseModel):
    """Transaction response."""

    id: str
    title: str
    amount: Decimal
    formatted_amount: str
    type: str
    category: str | None
    receipt_url: str | None
    description: str | None
    transaction_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    """Paginated transaction list response."""

    items: list[TransactionResponse]
    total: int
    total_income: Decimal
    total_expense: Decimal


class TransactionFilters(BaseModel):
    """Transaction query filters."""

    type: TransactionType | None = None
    category: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class ReceiptScanResponse(BaseModel):
    """Receipt OCR scan response."""

    suggested_title: str | None
    suggested_amount: Decimal | None
    suggested_category: str | None
    confidence: float | None = None
