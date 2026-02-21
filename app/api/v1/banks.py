"""
Bank account endpoints.
"""
import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.bank import (
    BankAccountsResponse,
    BankCallbackRequest,
    BankCallbackResponse,
    BankSyncResponse,
    LinkBankRequest,
    LinkBankResponse,
    UnlinkBankResponse,
)
from app.services.bank_service import BankService

router = APIRouter()


@router.get("", response_model=BankAccountsResponse)
async def get_linked_banks(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get linked bank accounts.

    Returns all active linked bank accounts.
    """
    service = BankService(db)
    return await service.get_linked_accounts(current_user.id)


@router.post("/link", response_model=LinkBankResponse)
async def initiate_bank_link(
    data: LinkBankRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Initiate bank linking.

    - **provider**: Bank provider ('mono' or 'okra')

    Returns widget URL to complete linking.
    """
    service = BankService(db)
    return await service.initiate_link(
        user_id=current_user.id,
        provider=data.provider,
    )


@router.post("/callback", response_model=BankCallbackResponse)
async def bank_link_callback(
    data: BankCallbackRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Handle bank linking callback.

    Called after user completes bank linking in widget.
    """
    service = BankService(db)
    return await service.handle_callback(
        user_id=current_user.id,
        provider=data.provider,
        code=data.code,
    )


@router.delete("/{bank_id}", response_model=UnlinkBankResponse)
async def unlink_bank(
    bank_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Unlink a bank account.
    """
    service = BankService(db)
    return await service.unlink_account(
        user_id=current_user.id,
        account_id=bank_id,
    )


@router.post("/{bank_id}/sync", response_model=BankSyncResponse)
async def sync_bank_transactions(
    bank_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Force sync bank transactions.

    Fetches latest transactions from the bank.
    """
    service = BankService(db)
    return await service.sync_transactions(
        user_id=current_user.id,
        account_id=bank_id,
    )
