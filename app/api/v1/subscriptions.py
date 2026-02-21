"""
Subscription endpoints.
"""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.subscription import (
    CancelSubscriptionResponse,
    CurrentSubscriptionResponse,
    SubscriptionPlansResponse,
    UpgradeSubscriptionRequest,
    UpgradeSubscriptionResponse,
)
from app.services.subscription_service import SubscriptionService

router = APIRouter()


@router.get("/plans", response_model=SubscriptionPlansResponse)
async def get_subscription_plans(
    db: DbSession,
):
    """
    Get available subscription plans.

    Returns all available plans with features and pricing.
    """
    service = SubscriptionService(db)
    return await service.get_plans()


@router.get("/current", response_model=CurrentSubscriptionResponse)
async def get_current_subscription(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get user's current subscription.

    Returns current plan, status, and expiration date.
    """
    service = SubscriptionService(db)
    return await service.get_current(current_user.id)


@router.post("/upgrade", response_model=UpgradeSubscriptionResponse)
async def upgrade_subscription(
    data: UpgradeSubscriptionRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Upgrade subscription.

    - **plan_id**: Target plan ('plus')
    - **payment_method**: Payment method ('card')
    - **payment_reference**: Payment reference (optional)
    """
    service = SubscriptionService(db)
    return await service.upgrade(
        user_id=current_user.id,
        data=data,
    )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Cancel subscription.

    Downgrades to free plan. Access continues until current period ends.
    """
    service = SubscriptionService(db)
    return await service.cancel(current_user.id)
