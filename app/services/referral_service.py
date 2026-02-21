"""
Referral service for referral tracking and rewards.
"""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.utils import generate_referral_code
from app.models.referral import MONTHLY_REFERRAL_LIMIT, REFERRAL_REWARD_AMOUNT, Referral
from app.repositories.referral_repo import ReferralRepository
from app.repositories.user_repo import UserRepository
from app.schemas.referral import (
    ApplyReferralRequest,
    ApplyReferralResponse,
    ReferralHistoryItem,
    ReferralHistoryResponse,
    ReferralInfoResponse,
)


class ReferralService:
    """Referral business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.referral_repo = ReferralRepository(db)
        self.user_repo = UserRepository(db)

    async def get_info(
        self,
        user_id: uuid.UUID,
    ) -> ReferralInfoResponse:
        """
        Get user's referral info.

        Args:
            user_id: User's ID

        Returns:
            ReferralInfoResponse with referral stats
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Ensure user has a referral code
        if not user.referral_code:
            referral_code = generate_referral_code(user.name or "User")
            await self.user_repo.set_referral_code(user_id, referral_code)
            user.referral_code = referral_code

        # Get referral stats
        total_earnings = await self.referral_repo.get_total_earnings(user_id)
        completed_count = await self.referral_repo.count_by_referrer(user_id, status="completed")
        pending_count = await self.referral_repo.count_by_referrer(user_id, status="pending")

        return ReferralInfoResponse(
            referral_code=user.referral_code,
            total_earnings=total_earnings,
            monthly_limit=MONTHLY_REFERRAL_LIMIT,
            referral_count=completed_count,
            pending_count=pending_count,
        )

    async def get_history(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> ReferralHistoryResponse:
        """
        Get referral history.

        Args:
            user_id: User's ID
            limit: Max results
            offset: Skip results

        Returns:
            ReferralHistoryResponse with referral list
        """
        referrals = await self.referral_repo.get_by_referrer(
            user_id, limit=limit, offset=offset
        )

        total = await self.referral_repo.count_by_referrer(user_id)

        items = []
        for referral in referrals:
            # Get referred user email (masked)
            referred_user = await self.user_repo.get_by_id(referral.referred_id)
            if referred_user:
                masked_email = self._mask_email(referred_user.email)
            else:
                masked_email = "Unknown"

            items.append(
                ReferralHistoryItem(
                    id=str(referral.id),
                    referred_user=masked_email,
                    status=referral.status,
                    reward=referral.reward_amount,
                    created_at=referral.created_at,
                    completed_at=referral.completed_at,
                )
            )

        return ReferralHistoryResponse(
            referrals=items,
            total=total,
        )

    async def apply_referral_code(
        self,
        user_id: uuid.UUID,
        referral_code: str,
    ) -> ApplyReferralResponse:
        """
        Apply referral code for a user.

        Args:
            user_id: User's ID (the one applying the code)
            referral_code: Referral code to apply

        Returns:
            ApplyReferralResponse with result
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Check if user was already referred
        existing_referral = await self.referral_repo.get_by_referred(user_id)
        if existing_referral:
            raise BadRequestError("You have already used a referral code")

        # Find referrer
        referrer = await self.user_repo.get_by_referral_code(referral_code.upper())

        if not referrer:
            raise BadRequestError("Invalid referral code")

        if referrer.id == user_id:
            raise BadRequestError("You cannot use your own referral code")

        # Check monthly limit for referrer
        today = date.today()
        monthly_earnings = await self.referral_repo.get_monthly_earnings(
            referrer.id, today.year, today.month
        )

        if monthly_earnings >= MONTHLY_REFERRAL_LIMIT:
            # Still allow referral but don't reward
            pass

        # Create referral
        referral = Referral(
            referrer_id=referrer.id,
            referred_id=user_id,
            status="pending",
            reward_amount=REFERRAL_REWARD_AMOUNT,
        )

        await self.referral_repo.create(referral)

        # Update user's referred_by
        await self.user_repo.set_referred_by(user_id, referrer.id)

        return ApplyReferralResponse(
            message="Referral code applied successfully!",
            referrer_name=referrer.name,
            applied=True,
        )

    async def complete_referral(
        self,
        referred_id: uuid.UUID,
    ) -> bool:
        """
        Complete a referral (e.g., after first transaction).

        Args:
            referred_id: ID of the referred user

        Returns:
            True if completed
        """
        referral = await self.referral_repo.get_by_referred(referred_id)

        if not referral:
            return False

        if referral.status == "completed":
            return True

        # Complete the referral
        await self.referral_repo.complete_referral(referral.id)

        # Check monthly limit before paying
        today = date.today()
        monthly_earnings = await self.referral_repo.get_monthly_earnings(
            referral.referrer_id, today.year, today.month
        )

        if monthly_earnings < MONTHLY_REFERRAL_LIMIT:
            # Mark reward as paid (in production, trigger actual payment)
            await self.referral_repo.mark_reward_paid(referral.id)

        return True

    def _mask_email(self, email: str) -> str:
        """Mask email for privacy."""
        if "@" not in email:
            return email

        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "*"
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"
