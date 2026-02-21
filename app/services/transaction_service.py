"""
Transaction service for income and expense management.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.utils import format_naira
from app.models.transaction import Transaction
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)


class TransactionService:
    """Transaction business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.transaction_repo = TransactionRepository(db)

    async def create(
        self,
        user_id: uuid.UUID,
        data: TransactionCreate,
    ) -> TransactionResponse:
        """
        Create a new transaction.

        Args:
            user_id: User's ID
            data: Transaction data

        Returns:
            Created TransactionResponse
        """
        transaction = Transaction(
            user_id=user_id,
            title=data.title,
            amount=data.amount,
            type=data.type,
            category=data.category,
            description=data.description,
            receipt_url=data.receipt_url,
            transaction_date=data.transaction_date or datetime.now(timezone.utc),
        )

        transaction = await self.transaction_repo.create(transaction)

        return self._to_response(transaction)

    async def get_by_id(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TransactionResponse:
        """
        Get transaction by ID.

        Args:
            transaction_id: Transaction ID
            user_id: User's ID

        Returns:
            TransactionResponse

        Raises:
            NotFoundError: If not found
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id, user_id)

        if not transaction:
            raise NotFoundError("Transaction not found", resource="transaction")

        return self._to_response(transaction)

    async def list_transactions(
        self,
        user_id: uuid.UUID,
        type: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> TransactionListResponse:
        """
        List user transactions with filters.

        Args:
            user_id: User's ID
            type: Filter by type (income/expense)
            category: Filter by category
            start_date: Filter from date
            end_date: Filter to date
            limit: Max results
            offset: Skip results

        Returns:
            TransactionListResponse with items and totals
        """
        transactions = await self.transaction_repo.get_by_user(
            user_id=user_id,
            type=type,
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        total = await self.transaction_repo.count_by_user(
            user_id=user_id,
            type=type,
            category=category,
            start_date=start_date,
            end_date=end_date,
        )

        totals = await self.transaction_repo.get_totals_by_user(user_id)

        return TransactionListResponse(
            items=[self._to_response(t) for t in transactions],
            total=total,
            total_income=totals.get("income", Decimal("0")),
            total_expense=totals.get("expense", Decimal("0")),
        )

    async def update(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
        data: TransactionUpdate,
    ) -> TransactionResponse:
        """
        Update a transaction.

        Args:
            transaction_id: Transaction ID
            user_id: User's ID
            data: Update data

        Returns:
            Updated TransactionResponse

        Raises:
            NotFoundError: If not found
        """
        # Check if exists
        existing = await self.transaction_repo.get_by_id(transaction_id, user_id)
        if not existing:
            raise NotFoundError("Transaction not found", resource="transaction")

        # Build update dict
        updates: dict[str, Any] = {}
        if data.title is not None:
            updates["title"] = data.title
        if data.amount is not None:
            updates["amount"] = data.amount
        if data.type is not None:
            updates["type"] = data.type
        if data.category is not None:
            updates["category"] = data.category
        if data.description is not None:
            updates["description"] = data.description
        if data.receipt_url is not None:
            updates["receipt_url"] = data.receipt_url
        if data.transaction_date is not None:
            updates["transaction_date"] = data.transaction_date

        if updates:
            transaction = await self.transaction_repo.update(
                transaction_id, user_id, **updates
            )
            if transaction is None:
                transaction = existing
        else:
            transaction = existing

        return self._to_response(transaction)

    async def delete(
        self,
        transaction_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id: Transaction ID
            user_id: User's ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If not found
        """
        deleted = await self.transaction_repo.delete(transaction_id, user_id)

        if not deleted:
            raise NotFoundError("Transaction not found", resource="transaction")

        return True

    async def scan_receipt(
        self,
        file_content: bytes,
        filename: str,
    ) -> dict:
        """
        Scan receipt using OCR.

        This is a placeholder - integrate actual OCR service.

        Args:
            file_content: File bytes
            filename: Original filename

        Returns:
            Suggested transaction data
        """
        # Placeholder - integrate OCR (e.g., Google Vision, Tesseract)
        # For now, return empty suggestions
        return {
            "suggested_title": None,
            "suggested_amount": None,
            "suggested_category": None,
            "confidence": None,
        }

    def _to_response(self, transaction: Transaction) -> TransactionResponse:
        """Convert Transaction model to response schema."""
        # Format amount with sign
        if transaction.type == "income":
            formatted = format_naira(transaction.amount, show_sign=True)
        else:
            formatted = format_naira(-transaction.amount, show_sign=True)

        return TransactionResponse(
            id=str(transaction.id),
            title=transaction.title,
            amount=transaction.amount,
            formatted_amount=formatted,
            type=transaction.type,
            category=transaction.category,
            receipt_url=transaction.receipt_url,
            description=transaction.description,
            transaction_date=transaction.transaction_date,
            created_at=transaction.created_at,
        )
