"""
TIN endpoints.
"""
import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.tin import (
    TINApplicationRequest,
    TINApplicationResponse,
    TINApplicationStatusResponse,
    TINStatusResponse,
)
from app.services.tin_service import TINService

router = APIRouter()


@router.get("", response_model=TINStatusResponse)
async def get_tin_status(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get user's TIN status.

    Returns whether user has a TIN and current application status.
    """
    service = TINService(db)
    return await service.get_status(current_user.id)


@router.post("/apply", response_model=TINApplicationResponse, status_code=201)
async def apply_for_tin(
    data: TINApplicationRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Apply for TIN.

    - **nin**: National Identification Number
    - **date_of_birth**: Date of birth
    - **id_document_url**: URL to ID document (optional)
    """
    service = TINService(db)
    return await service.apply(
        user_id=current_user.id,
        data=data,
    )


@router.get("/application/{application_id}", response_model=TINApplicationStatusResponse)
async def get_tin_application(
    application_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get TIN application status.
    """
    service = TINService(db)
    return await service.get_application_status(
        user_id=current_user.id,
        application_id=application_id,
    )
