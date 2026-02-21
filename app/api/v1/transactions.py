"""
Transaction endpoints.
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import MessageResponse
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    current_user: CurrentUser,
    db: DbSession,
    type: str | None = Query(None, description="Filter by type: income or expense"),
    category: str | None = Query(None, description="Filter by category"),
    start_date: datetime | None = Query(None, description="Filter from date"),
    end_date: datetime | None = Query(None, description="Filter to date"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
):
    """
    Get list of user transactions.

    Supports filtering by type, category, and date range.
    """
    service = TransactionService(db)
    return await service.list_transactions(
        user_id=current_user.id,
        type=type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    data: TransactionCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Create a new transaction.

    - **title**: Transaction title
    - **amount**: Amount (positive)
    - **type**: 'income' or 'expense'
    - **category**: Category name (optional)
    - **description**: Description (optional)
    - **receipt_url**: Receipt image URL (optional)
    """
    service = TransactionService(db)
    return await service.create(
        user_id=current_user.id,
        data=data,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get transaction details.
    """
    service = TransactionService(db)
    return await service.get_by_id(
        transaction_id=transaction_id,
        user_id=current_user.id,
    )


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    data: TransactionUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Update a transaction.
    """
    service = TransactionService(db)
    return await service.update(
        transaction_id=transaction_id,
        user_id=current_user.id,
        data=data,
    )


@router.delete("/{transaction_id}", response_model=MessageResponse)
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Delete a transaction.
    """
    service = TransactionService(db)
    await service.delete(
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
    return MessageResponse(message="Transaction deleted successfully")
