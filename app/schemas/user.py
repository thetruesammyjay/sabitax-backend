"""
User schemas for request/response validation.
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    name: str | None = None
    email: EmailStr | None = None


class UserCreate(BaseModel):
    """User creation schema (internal use)."""

    name: str
    email: EmailStr
    password_hash: str


class UserUpdate(BaseModel):
    """User update request."""

    name: str | None = Field(None, min_length=2, max_length=255)


class UserResponse(BaseModel):
    """User profile response."""

    id: str
    name: str | None
    email: str
    avatar_initials: str
    is_verified: bool
    tin: str | None = None  # Masked TIN
    tin_verified: bool = False
    streak_days: int = 0
    subscription_plan: str = "free"
    compliance_score: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class UserStatsResponse(BaseModel):
    """User dashboard statistics response."""

    compliance_score: int
    streak_days: int
    total_income: Decimal
    total_expenses: Decimal
    estimated_tax: Decimal
    income_documented_percent: int
    tax_due_date: date | None


class UserProfileResponse(BaseModel):
    """Complete user profile with stats."""

    user: UserResponse
    stats: UserStatsResponse


class UpdateStreakRequest(BaseModel):
    """Request to update user streak (internal use)."""

    streak_days: int
    last_active_date: date
