"""
Referral endpoints.
"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.referral import (
    ApplyReferralRequest,
    ApplyReferralResponse,
    ReferralHistoryResponse,
    ReferralInfoResponse,
)
from app.services.referral_service import ReferralService

router = APIRouter()


@router.get("", response_model=ReferralInfoResponse)
async def get_referral_info(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get user's referral info.

    Returns referral code, total earnings, and referral count.
    """
    service = ReferralService(db)
    return await service.get_info(current_user.id)


@router.get("/history", response_model=ReferralHistoryResponse)
async def get_referral_history(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get referral history.

    Returns list of referrals with status and rewards.
    """
    service = ReferralService(db)
    return await service.get_history(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.post("/apply", response_model=ApplyReferralResponse)
async def apply_referral_code(
    data: ApplyReferralRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Apply referral code.

    Links current user to the referrer.
    """
    service = ReferralService(db)
    return await service.apply_referral_code(
        user_id=current_user.id,
        referral_code=data.referral_code,
    )
