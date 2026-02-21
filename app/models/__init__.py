"""
SQLAlchemy models for SabiTax database.
"""
from app.models.bank_account import BankAccount
from app.models.base import BaseModel
from app.models.chat import ChatMessage, TAX_ASSISTANT_SYSTEM_PROMPT
from app.models.notification import Notification
from app.models.referral import (
    MONTHLY_REFERRAL_LIMIT,
    REFERRAL_REWARD_AMOUNT,
    Referral,
)
from app.models.subscription import SUBSCRIPTION_PLANS, Subscription
from app.models.tax import TaxFiling, TaxObligation
from app.models.tin import TINApplication
from app.models.transaction import EXPENSE_CATEGORIES, INCOME_CATEGORIES, Transaction
from app.models.user import User

__all__ = [
    # Base
    "BaseModel",
    # Models
    "User",
    "Transaction",
    "TaxFiling",
    "TaxObligation",
    "TINApplication",
    "Subscription",
    "Referral",
    "BankAccount",
    "ChatMessage",
    "Notification",
    # Constants
    "INCOME_CATEGORIES",
    "EXPENSE_CATEGORIES",
    "SUBSCRIPTION_PLANS",
    "REFERRAL_REWARD_AMOUNT",
    "MONTHLY_REFERRAL_LIMIT",
    "TAX_ASSISTANT_SYSTEM_PROMPT",
]
