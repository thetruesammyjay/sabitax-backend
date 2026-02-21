"""
Subscription schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


PlanId = Literal["free", "plus"]
SubscriptionStatus = Literal["active", "cancelled", "expired", "trial"]


class SubscriptionPlan(BaseModel):
    """Subscription plan details."""

    id: str
    name: str
    price: Decimal
    currency: str = "NGN"
    billing_period: str | None = None
    features: list[str]


class SubscriptionPlansResponse(BaseModel):
    """Available subscription plans response."""

    plans: list[SubscriptionPlan]


class CurrentSubscriptionResponse(BaseModel):
    """User's current subscription response."""

    plan_id: str
    plan_name: str
    status: str
    started_at: datetime | None = None
    expires_at: datetime | None = None


class UpgradeSubscriptionRequest(BaseModel):
    """Subscription upgrade request."""

    plan_id: PlanId
    payment_method: str = "card"
    payment_reference: str | None = None


class UpgradeSubscriptionResponse(BaseModel):
    """Subscription upgrade response."""

    plan_id: str
    plan_name: str
    status: str
    payment_url: str | None = None
    expires_at: datetime | None = None


class CancelSubscriptionResponse(BaseModel):
    """Subscription cancellation response."""

    message: str
    cancelled_at: datetime
    access_until: datetime | None = None
