# SabiTax Backend - API Endpoints

> Base URL: `https://your-space.hf.space/api/v1`

---

## Authentication

### `POST /auth/register`
Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "is_verified": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### `POST /auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

### `POST /auth/social`
Social login (Google/Apple).

**Request Body:**
```json
{
  "provider": "google",
  "token": "social-auth-token"
}
```

**Response:** Same as login response.

---

### `POST /auth/forgot-password`
Request password reset.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password reset email sent"
}
```

---

### `POST /auth/reset-password`
Reset password with token.

**Request Body:**
```json
{
  "token": "reset-token",
  "new_password": "newSecurePassword"
}
```

---

## Users

### `GET /users/me`
Get current authenticated user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "avatar_initials": "JD",
  "is_verified": true,
  "tin": "221***90",
  "streak_days": 2,
  "subscription_plan": "free",
  "compliance_score": 85,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### `PATCH /users/me`
Update current user profile.

**Request Body:**
```json
{
  "name": "John Updated"
}
```

---

### `GET /users/me/stats`
Get user dashboard statistics.

**Response:**
```json
{
  "compliance_score": 85,
  "streak_days": 2,
  "total_income": 970000,
  "estimated_tax": 97000,
  "income_documented_percent": 85,
  "tax_due_date": "2025-01-31"
}
```

---

## Transactions

### `GET /transactions`
Get list of user transactions.

**Query Parameters:**
- `type`: `income` | `expense` (optional)
- `category`: string (optional)
- `limit`: number (default: 50)
- `offset`: number (default: 0)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Salary Jan",
      "amount": 850000,
      "formatted_amount": "+₦850,000",
      "type": "income",
      "category": "Salary",
      "date": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 100,
  "total_income": 970000,
  "total_expense": 53900
}
```

---

### `POST /transactions`
Create a new transaction.

**Request Body:**
```json
{
  "title": "Freelance Project",
  "amount": 120000,
  "type": "income",
  "category": "Freelance",
  "receipt_url": null
}
```

**Response:** `201 Created`

---

### `GET /transactions/{id}`
Get transaction details.

---

### `PATCH /transactions/{id}`
Update a transaction.

---

### `DELETE /transactions/{id}`
Delete a transaction.

---

### `POST /transactions/scan-receipt`
Upload and scan receipt (OCR).

**Request:** `multipart/form-data`
- `file`: image file

**Response:**
```json
{
  "suggested_title": "Shoprite Lekki",
  "suggested_amount": 45000,
  "suggested_category": "Groceries"
}
```

---

## Tax

### `GET /tax/obligations`
Get user's tax obligations.

**Response:**
```json
{
  "obligations": [
    {
      "type": "PIT",
      "name": "Personal Income Tax",
      "amount": 45000,
      "due_date": "2025-01-31",
      "status": "pending",
      "based_on": "₦850k monthly income"
    },
    {
      "type": "VAT",
      "name": "Value Added Tax",
      "amount": 0,
      "due_date": null,
      "status": "none",
      "based_on": "No taxable business transactions"
    }
  ],
  "total_due": 45000
}
```

---

### `GET /tax/estimate`
Get estimated tax liability.

**Response:**
```json
{
  "total_income": 970000,
  "taxable_income": 870000,
  "estimated_tax": 97000,
  "tax_rate": 10,
  "potential_savings": 20000,
  "next_due_date": "2025-01-31"
}
```

---

### `POST /tax/file`
File tax returns.

**Request Body:**
```json
{
  "tax_type": "PIT",
  "year": 2024,
  "declaration": {
    "total_income": 970000,
    "deductions": []
  }
}
```

**Response:**
```json
{
  "filing_id": "uuid",
  "status": "submitted",
  "reference_number": "FIRS-2025-XXXXX"
}
```

---

### `GET /tax/filings`
Get filing history.

---

### `GET /tax/optimization`
Get tax optimization suggestions.

**Response:**
```json
{
  "potential_savings": 20000,
  "suggestions": [
    {
      "type": "relief",
      "title": "Rent Relief",
      "description": "Claim rent payments as relief",
      "estimated_savings": 15000
    }
  ]
}
```

---

## TIN (Tax Identification Number)

### `GET /tin`
Get user's TIN status.

**Response:**
```json
{
  "has_tin": true,
  "tin": "221***90",
  "status": "verified",
  "applied_at": null
}
```

---

### `POST /tin/apply`
Apply for TIN.

**Request Body:**
```json
{
  "nin": "12345678901",
  "date_of_birth": "1990-05-15",
  "id_document_url": "https://..."
}
```

**Response:**
```json
{
  "application_id": "uuid",
  "status": "processing",
  "estimated_completion": "3-5 business days"
}
```

---

### `GET /tin/application/{id}`
Get TIN application status.

---

### `POST /tin/upload-id`
Upload ID document for TIN application.

**Request:** `multipart/form-data`

---

## Subscriptions

### `GET /subscriptions/plans`
Get available subscription plans.

**Response:**
```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price": 0,
      "currency": "NGN",
      "features": ["Track Expenses", "Basic Reports"]
    },
    {
      "id": "plus",
      "name": "SabiTax Plus",
      "price": 5000,
      "currency": "NGN",
      "billing_period": "yearly",
      "features": ["Auto-Filing (PIT & VAT)", "Audit Defense", "Priority Support"]
    }
  ]
}
```

---

### `GET /subscriptions/current`
Get user's current subscription.

**Response:**
```json
{
  "plan_id": "free",
  "plan_name": "Free",
  "status": "active",
  "expires_at": null
}
```

---

### `POST /subscriptions/upgrade`
Upgrade subscription.

**Request Body:**
```json
{
  "plan_id": "plus",
  "payment_method": "card"
}
```

---

### `POST /subscriptions/cancel`
Cancel subscription.

---

## Referrals

### `GET /referrals`
Get user's referral info.

**Response:**
```json
{
  "referral_code": "SABI-JOE",
  "total_earnings": 5000,
  "monthly_limit": 50000,
  "referral_count": 5,
  "pending_count": 2
}
```

---

### `GET /referrals/history`
Get referral history.

**Response:**
```json
{
  "referrals": [
    {
      "id": "uuid",
      "referred_user": "jane@example.com",
      "status": "completed",
      "reward": 1000,
      "completed_at": "2025-01-10T00:00:00Z"
    }
  ]
}
```

---

### `POST /referrals/apply`
Apply referral code during signup.

**Request Body:**
```json
{
  "referral_code": "SABI-JOE"
}
```

---

## Bank Accounts

### `GET /banks`
Get linked bank accounts.

**Response:**
```json
{
  "accounts": [
    {
      "id": "uuid",
      "provider": "mono",
      "bank_name": "GTBank",
      "account_number": "***4567",
      "status": "active",
      "linked_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### `POST /banks/link`
Initiate bank linking.

**Request Body:**
```json
{
  "provider": "mono"
}
```

**Response:**
```json
{
  "widget_url": "https://connect.mono.co/...",
  "session_id": "xxx"
}
```

---

### `POST /banks/callback`
Handle bank linking callback.

**Request Body:**
```json
{
  "provider": "mono",
  "code": "code_from_widget"
}
```

---

### `DELETE /banks/{id}`
Unlink a bank account.

---

### `POST /banks/{id}/sync`
Force sync bank transactions.

---

## AI Chat (Tax Assistant)

### `POST /chat`
Send message to AI Tax Assistant.

**Request Body:**
```json
{
  "message": "What is the deadline for filing PAYE?"
}
```

**Response:**
```json
{
  "id": "uuid",
  "role": "assistant",
  "content": "Great question! PAYE returns are due by the 10th of the following month. The annual return is due Jan 31st! 📅",
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

### `GET /chat/history`
Get chat history.

**Query Parameters:**
- `limit`: number (default: 50)
- `before`: message_id (for pagination)

**Response:**
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What is the deadline for filing PAYE?",
      "created_at": "2025-01-15T09:59:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Great question! PAYE returns are due...",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

### `DELETE /chat/history`
Clear chat history.

---

## Notifications

### `GET /notifications`
Get user notifications.

**Response:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "tax_reminder",
      "title": "Tax Due Soon",
      "message": "Your PIT is due in 5 days",
      "read": false,
      "created_at": "2025-01-26T00:00:00Z"
    }
  ],
  "unread_count": 3
}
```

---

### `PATCH /notifications/{id}/read`
Mark notification as read.

---

### `POST /notifications/settings`
Update notification settings.

---

## Wrapped (Year Summary)

### `GET /wrapped/{year}`
Get yearly tax/spending summary.

**Response:**
```json
{
  "year": 2025,
  "total_income": 10200000,
  "total_expenses": 2500000,
  "taxes_paid": 1020000,
  "top_categories": [
    {"category": "Food", "amount": 800000},
    {"category": "Transport", "amount": 500000}
  ],
  "spending_style": "Balanced Spender",
  "compliance_rating": "Excellent"
}
```

---

## SabiTax Advanced AI (Document Proxy)

### `POST /sabitax-ai/ingest`
Upload a new tax document for the AI to learn.

**Request:** `multipart/form-data`
- `file`: PDF or Text file
- `force`: boolean (optional)

**Response:**
```json
{
  "message": "File processed successfully",
  "filename": "tax_law_2025.pdf",
  "chunks_added": 45
}
```

---

### `GET /sabitax-ai/stats`
Get current vector database status.

**Response:**
```json
{
  "total_vectors": 1500,
  "dimension": 768,
  "index_name": "sabitax-index"
}
```

---

### `POST /sabitax-ai/yearly-wrap`
Generate a yearly financial wrap video using AI.

**Request:** `application/x-www-form-urlencoded`
- `year`: 2024

**Response:**
```json
{
  "status": "success",
  "video_url": "https://...",
  "analysis": {},
  "video_script": {}
}
```

---

### `GET /sabitax-ai/health`
Check connection to SabiTax AI services.

**Response:**
```json
{
  "status": "online",
  "gemini_connected": true,
  "pinecone_connected": true,
  "vectors_indexed": 1500
}
```

---

## Health Check

### `GET /health`
API health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```
