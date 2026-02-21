"""
Referral schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ReferralInfoResponse(BaseModel):
    """User's referral info response."""

    referral_code: str
    total_earnings: Decimal
    monthly_limit: Decimal
    referral_count: int
    pending_count: int


class ReferralHistoryItem(BaseModel):
    """Referral history item."""

    id: str
    referred_user: str  # Email or masked identifier
    status: str
    reward: Decimal
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ReferralHistoryResponse(BaseModel):
    """Referral history response."""

    referrals: list[ReferralHistoryItem]
    total: int


class ApplyReferralRequest(BaseModel):
    """Apply referral code request."""

    referral_code: str = Field(..., min_length=5, max_length=20)


class ApplyReferralResponse(BaseModel):
    """Apply referral code response."""

    message: str
    referrer_name: str | None = None
    applied: bool
