"""
Tax schemas for request/response validation.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


TaxType = Literal["PIT", "VAT", "CIT", "PAYE"]
FilingStatus = Literal["draft", "submitted", "processing", "completed", "rejected"]


class TaxObligationItem(BaseModel):
    """Single tax obligation item."""

    type: str
    name: str
    amount: Decimal
    due_date: date | None
    status: str
    based_on: str | None


class TaxObligationsResponse(BaseModel):
    """Tax obligations response."""

    obligations: list[TaxObligationItem]
    total_due: Decimal


class TaxEstimateResponse(BaseModel):
    """Tax estimate calculation response."""

    total_income: Decimal
    taxable_income: Decimal
    estimated_tax: Decimal
    tax_rate: Decimal  # Effective tax rate percentage
    potential_savings: Decimal
    next_due_date: date | None
    cra: Decimal  # Consolidated Relief Allowance


class TaxFilingRequest(BaseModel):
    """Tax filing submission request."""

    tax_type: TaxType
    year: int = Field(..., ge=2000, le=2100)
    declaration: dict | None = None


class TaxFilingResponse(BaseModel):
    """Tax filing submission response."""

    filing_id: str
    status: str
    reference_number: str | None
    filed_at: datetime

    model_config = {"from_attributes": True}


class TaxFilingHistoryItem(BaseModel):
    """Tax filing history item."""

    id: str
    tax_type: str
    tax_year: int
    amount: Decimal
    status: str
    reference_number: str | None
    filed_at: datetime

    model_config = {"from_attributes": True}


class TaxFilingHistoryResponse(BaseModel):
    """Tax filing history response."""

    filings: list[TaxFilingHistoryItem]
    total: int


class TaxOptimizationSuggestion(BaseModel):
    """Tax optimization suggestion."""

    type: str
    title: str
    description: str
    estimated_savings: Decimal


class TaxOptimizationResponse(BaseModel):
    """Tax optimization suggestions response."""

    potential_savings: Decimal
    suggestions: list[TaxOptimizationSuggestion]
