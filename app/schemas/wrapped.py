"""
Wrapped (Year Summary) schemas for request/response validation.
"""
from decimal import Decimal

from pydantic import BaseModel


class CategorySpending(BaseModel):
    """Category spending summary."""

    category: str
    amount: Decimal
    percentage: float | None = None


class WrappedResponse(BaseModel):
    """Annual wrapped summary response."""

    year: int
    total_income: Decimal
    total_expenses: Decimal
    taxes_paid: Decimal
    top_categories: list[CategorySpending]
    spending_style: str
    compliance_rating: str
    income_growth: float | None = None  # Percentage compared to previous year
    savings_rate: float | None = None  # Percentage saved
