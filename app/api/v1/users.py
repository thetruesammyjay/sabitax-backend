"""
User endpoints.
"""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.user import UserResponse, UserStatsResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get current authenticated user profile.

    Returns user profile with compliance score.
    """
    service = UserService(db)
    return await service.get_profile(current_user.id)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Update current user profile.

    - **name**: New display name (optional)
    """
    service = UserService(db)
    return await service.update_profile(
        user_id=current_user.id,
        name=data.name,
    )


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get user dashboard statistics.

    Returns:
    - Compliance score
    - Streak days
    - Total income/expenses
    - Estimated tax
    - Next tax due date
    """
    service = UserService(db)
    return await service.get_stats(current_user.id)
