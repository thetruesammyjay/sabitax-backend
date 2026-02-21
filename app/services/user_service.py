"""
User service for profile and stats management.
"""
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.utils import (
    calculate_compliance_score,
    calculate_nigerian_pit,
    get_next_tax_due_date,
    mask_tin,
)
from app.repositories.tax_repo import TaxRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse, UserStatsResponse


class UserService:
    """User business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.tax_repo = TaxRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> UserResponse:
        """
        Get user profile with compliance score.

        Args:
            user_id: User's ID

        Returns:
            UserResponse with profile data

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Calculate compliance score
        stats = await self.get_stats(user_id)

        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            avatar_initials=user.avatar_initials,
            is_verified=user.is_verified,
            tin=mask_tin(user.tin) if user.tin else None,
            tin_verified=user.tin_verified,
            streak_days=user.streak_days,
            subscription_plan=user.subscription_plan,
            compliance_score=stats.compliance_score,
            created_at=user.created_at,
        )

    async def update_profile(
        self,
        user_id: uuid.UUID,
        name: str | None = None,
    ) -> UserResponse:
        """
        Update user profile.

        Args:
            user_id: User's ID
            name: New name (optional)

        Returns:
            Updated UserResponse
        """
        updates = {}
        if name is not None:
            updates["name"] = name

        if updates:
            await self.user_repo.update(user_id, **updates)

        return await self.get_profile(user_id)

    async def get_stats(self, user_id: uuid.UUID) -> UserStatsResponse:
        """
        Get user dashboard statistics.

        Args:
            user_id: User's ID

        Returns:
            UserStatsResponse with all stats
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise NotFoundError("User not found", resource="user")

        # Get current year
        current_year = date.today().year

        # Get transaction totals
        totals = await self.transaction_repo.get_totals_by_user(user_id, year=current_year)
        total_income = totals.get("income", Decimal("0"))
        total_expenses = totals.get("expense", Decimal("0"))

        # Calculate estimated tax
        tax_result = calculate_nigerian_pit(total_income)
        estimated_tax = tax_result["tax_amount"]

        # Calculate income documentation percentage
        # (For now, assume all logged income is documented)
        income_documented_percent = 100 if total_income > 0 else 0

        # Calculate compliance score
        filings_count = await self.tax_repo.count_filings_by_user(user_id)
        completed_filings = await self.tax_repo.count_filings_by_user(
            user_id, status="completed"
        )

        compliance_score = calculate_compliance_score(
            documented_income=float(total_income),
            estimated_income=float(total_income),
            has_tin=user.tin_verified,
            filings_on_time=completed_filings,
            total_filings=filings_count,
        )

        return UserStatsResponse(
            compliance_score=compliance_score,
            streak_days=user.streak_days,
            total_income=total_income,
            total_expenses=total_expenses,
            estimated_tax=estimated_tax,
            income_documented_percent=income_documented_percent,
            tax_due_date=get_next_tax_due_date(),
        )
