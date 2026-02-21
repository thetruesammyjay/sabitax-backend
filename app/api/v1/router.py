"""
Main API v1 router combining all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    banks,
    chat,
    notifications,
    referrals,
    subscriptions,
    tax,
    tin,
    transactions,
    users,
    sabitax_ai,
)

router = APIRouter()


# Health check
@router.get("/health")
async def health_check():
    """
    API health check endpoint.

    Returns service status.
    """
    return {
        "status": "healthy",
        "service": "SabiTax API",
        "version": "1.0.0",
    }


# Include all routers
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"],
)

router.include_router(
    tax.router,
    prefix="/tax",
    tags=["Tax"],
)

router.include_router(
    tin.router,
    prefix="/tin",
    tags=["TIN"],
)

router.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["Subscriptions"],
)

router.include_router(
    referrals.router,
    prefix="/referrals",
    tags=["Referrals"],
)

router.include_router(
    banks.router,
    prefix="/banks",
    tags=["Bank Accounts"],
)

router.include_router(
    chat.router,
    prefix="/chat",
    tags=["AI Chat"],
)

router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)

router.include_router(
    sabitax_ai.router,
    prefix="/sabitax-ai",
    tags=["SabiTax Advanced AI"],
)
