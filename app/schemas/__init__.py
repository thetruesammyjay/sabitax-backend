"""
Pydantic schemas for SabiTax API.
"""
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SocialLoginRequest,
    TokenResponse,
    UserBasic,
)
from app.schemas.bank import (
    BankAccountResponse,
    BankAccountsResponse,
    BankCallbackRequest,
    BankCallbackResponse,
    BankSyncResponse,
    LinkBankRequest,
    LinkBankResponse,
    UnlinkBankResponse,
)
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ClearChatResponse,
)
from app.schemas.notification import (
    MarkReadResponse,
    NotificationResponse,
    NotificationSettingsRequest,
    NotificationSettingsResponse,
    NotificationsResponse,
)
from app.schemas.referral import (
    ApplyReferralRequest,
    ApplyReferralResponse,
    ReferralHistoryItem,
    ReferralHistoryResponse,
    ReferralInfoResponse,
)
from app.schemas.subscription import (
    CancelSubscriptionResponse,
    CurrentSubscriptionResponse,
    SubscriptionPlan,
    SubscriptionPlansResponse,
    UpgradeSubscriptionRequest,
    UpgradeSubscriptionResponse,
)
from app.schemas.tax import (
    TaxEstimateResponse,
    TaxFilingHistoryItem,
    TaxFilingHistoryResponse,
    TaxFilingRequest,
    TaxFilingResponse,
    TaxObligationItem,
    TaxObligationsResponse,
    TaxOptimizationResponse,
    TaxOptimizationSuggestion,
)
from app.schemas.tin import (
    TINApplicationRequest,
    TINApplicationResponse,
    TINApplicationStatusResponse,
    TINDocumentUploadResponse,
    TINStatusResponse,
)
from app.schemas.transaction import (
    ReceiptScanResponse,
    TransactionCreate,
    TransactionFilters,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from app.schemas.user import (
    UpdateStreakRequest,
    UserProfileResponse,
    UserResponse,
    UserStatsResponse,
    UserUpdate,
)
from app.schemas.wrapped import CategorySpending, WrappedResponse

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "SocialLoginRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "TokenResponse",
    "AuthResponse",
    "UserBasic",
    "MessageResponse",
    # User
    "UserUpdate",
    "UserResponse",
    "UserStatsResponse",
    "UserProfileResponse",
    "UpdateStreakRequest",
    # Transaction
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionListResponse",
    "TransactionFilters",
    "ReceiptScanResponse",
    # Tax
    "TaxObligationItem",
    "TaxObligationsResponse",
    "TaxEstimateResponse",
    "TaxFilingRequest",
    "TaxFilingResponse",
    "TaxFilingHistoryItem",
    "TaxFilingHistoryResponse",
    "TaxOptimizationSuggestion",
    "TaxOptimizationResponse",
    # TIN
    "TINStatusResponse",
    "TINApplicationRequest",
    "TINApplicationResponse",
    "TINApplicationStatusResponse",
    "TINDocumentUploadResponse",
    # Subscription
    "SubscriptionPlan",
    "SubscriptionPlansResponse",
    "CurrentSubscriptionResponse",
    "UpgradeSubscriptionRequest",
    "UpgradeSubscriptionResponse",
    "CancelSubscriptionResponse",
    # Referral
    "ReferralInfoResponse",
    "ReferralHistoryItem",
    "ReferralHistoryResponse",
    "ApplyReferralRequest",
    "ApplyReferralResponse",
    # Bank
    "BankAccountResponse",
    "BankAccountsResponse",
    "LinkBankRequest",
    "LinkBankResponse",
    "BankCallbackRequest",
    "BankCallbackResponse",
    "BankSyncResponse",
    "UnlinkBankResponse",
    # Chat
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ClearChatResponse",
    # Notification
    "NotificationResponse",
    "NotificationsResponse",
    "MarkReadResponse",
    "NotificationSettingsRequest",
    "NotificationSettingsResponse",
    # Wrapped
    "CategorySpending",
    "WrappedResponse",
]
