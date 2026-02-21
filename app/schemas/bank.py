"""
Bank account schemas for request/response validation.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


BankProvider = Literal["mono", "okra"]
BankStatus = Literal["active", "inactive", "pending", "error"]


class BankAccountResponse(BaseModel):
    """Bank account response."""

    id: str
    provider: str
    bank_name: str | None
    account_number: str  # Masked
    status: str
    linked_at: datetime
    last_synced_at: datetime | None = None

    model_config = {"from_attributes": True}


class BankAccountsResponse(BaseModel):
    """Linked bank accounts response."""

    accounts: list[BankAccountResponse]


class LinkBankRequest(BaseModel):
    """Bank linking initiation request."""

    provider: BankProvider


class LinkBankResponse(BaseModel):
    """Bank linking initiation response."""

    widget_url: str
    session_id: str


class BankCallbackRequest(BaseModel):
    """Bank linking callback request."""

    provider: BankProvider
    code: str


class BankCallbackResponse(BaseModel):
    """Bank linking callback response."""

    account_id: str
    bank_name: str
    account_number: str  # Masked
    status: str
    linked_at: datetime


class BankSyncResponse(BaseModel):
    """Bank sync response."""

    account_id: str
    transactions_synced: int
    last_synced_at: datetime


class UnlinkBankResponse(BaseModel):
    """Bank unlink response."""

    message: str
    unlinked_at: datetime
