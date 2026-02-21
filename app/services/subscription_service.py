"""
Subscription service for plan management.
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.subscription import SUBSCRIPTION_PLANS, Subscription
from app.repositories.subscription_repo import SubscriptionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.subscription import (
    CancelSubscriptionResponse,
    CurrentSubscriptionResponse,
    SubscriptionPlan,
    SubscriptionPlansResponse,
    UpgradeSubscriptionRequest,
    UpgradeSubscriptionResponse,
)


class SubscriptionService:
    """Subscription business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_repo = SubscriptionRepository(db)
        self.user_repo = UserRepository(db)

    async def get_plans(self) -> SubscriptionPlansResponse:
        """
        Get available subscription plans.

        Returns:
            SubscriptionPlansResponse with all plans
        """
        plans = [
            SubscriptionPlan(
                id=str(plan["id"]),
                name=str(plan["name"]),
                price=Decimal(str(plan["price"])),
                currency=str(plan["currency"]),
                billing_period=str(plan["billing_period"]) if plan.get("billing_period") else None,
                features=list(plan["features"]),  # type: ignore[call-overload]
            )
            for plan in SUBSCRIPTION_PLANS.values()
        ]

        return SubscriptionPlansResponse(plans=plans)

    async def get_current(
        self,
        user_id: uuid.UUID,
    ) -> CurrentSubscriptionResponse:
        """
        Get user's current subscription.

        Args:
            user_id: User's ID

        Returns:
            CurrentSubscriptionResponse with current plan
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Get active subscription
        subscription = await self.subscription_repo.get_active_by_user(user_id)

        if subscription:
            plan = SUBSCRIPTION_PLANS.get(subscription.plan_id, SUBSCRIPTION_PLANS["free"])
            return CurrentSubscriptionResponse(
                plan_id=subscription.plan_id,
                plan_name=str(plan["name"]),
                status=subscription.status,
                started_at=subscription.started_at,
                expires_at=subscription.expires_at,
            )
        else:
            # Default to free plan
            return CurrentSubscriptionResponse(
                plan_id="free",
                plan_name="Free",
                status="active",
                started_at=user.created_at,
                expires_at=None,
            )

    async def upgrade(
        self,
        user_id: uuid.UUID,
        data: UpgradeSubscriptionRequest,
    ) -> UpgradeSubscriptionResponse:
        """
        Upgrade subscription.

        Args:
            user_id: User's ID
            data: Upgrade request

        Returns:
            UpgradeSubscriptionResponse with new subscription
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        if data.plan_id not in SUBSCRIPTION_PLANS:
            raise BadRequestError("Invalid subscription plan")

        plan = SUBSCRIPTION_PLANS[data.plan_id]

        if data.plan_id == "free":
            raise BadRequestError("Cannot upgrade to free plan. Use cancel instead.")

        # Check if already on this plan
        if user.subscription_plan == data.plan_id:
            raise BadRequestError(f"Already subscribed to {plan['name']}")

        # Calculate expiration
        now = datetime.now(timezone.utc)
        if plan.get("billing_period") == "yearly":
            expires_at = now + timedelta(days=365)
        elif plan.get("billing_period") == "monthly":
            expires_at = now + timedelta(days=30)
        else:
            expires_at = None

        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            plan_id=data.plan_id,
            status="active",
            payment_reference=data.payment_reference,
            amount_paid=Decimal(str(plan["price"])),
            started_at=now,
            expires_at=expires_at,
        )

        subscription = await self.subscription_repo.create(subscription)

        # Update user's plan
        await self.user_repo.update_subscription_plan(user_id, data.plan_id)

        return UpgradeSubscriptionResponse(
            plan_id=subscription.plan_id,
            plan_name=str(plan["name"]),
            status=subscription.status,
            payment_url=None,  # In production, integrate payment gateway
            expires_at=subscription.expires_at,
        )

    async def cancel(
        self,
        user_id: uuid.UUID,
    ) -> CancelSubscriptionResponse:
        """
        Cancel subscription.

        Args:
            user_id: User's ID

        Returns:
            CancelSubscriptionResponse with cancellation details
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        if user.subscription_plan == "free":
            raise BadRequestError("You are already on the free plan")

        # Get active subscription
        subscription = await self.subscription_repo.get_active_by_user(user_id)

        now = datetime.now(timezone.utc)

        if subscription:
            # Cancel the subscription
            await self.subscription_repo.cancel(subscription.id, user_id)
            access_until = subscription.expires_at

            # Update user's plan to free
            await self.user_repo.update_subscription_plan(user_id, "free")

            return CancelSubscriptionResponse(
                message="Subscription cancelled successfully",
                cancelled_at=now,
                access_until=access_until,
            )
        else:
            # Just reset to free
            await self.user_repo.update_subscription_plan(user_id, "free")

            return CancelSubscriptionResponse(
                message="Subscription cancelled",
                cancelled_at=now,
                access_until=None,
            )
