# SabiTax Backend - File Structure

> **Stack**: Python FastAPI | PostgreSQL (NeonDB) | Hosted on HuggingFace  
> **Init**: `uv init sabitax-backend`

---

## Project Structure

```
sabitax-backend/
├── pyproject.toml              # UV/Python project config
├── .env                        # Environment variables
├── .env.example                # Example env vars template
├── main.py                     # FastAPI app entrypoint
├── README.md                   # Project documentation
│
├── app/
│   ├── __init__.py
│   ├── config.py               # Settings/environment config
│   ├── database.py             # Database connection & session
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── transaction.py      # Transaction model
│   │   ├── tax.py              # Tax obligations model
│   │   ├── tin.py              # TIN applications model
│   │   ├── subscription.py     # Subscription/Plan model
│   │   ├── referral.py         # Referral model
│   │   ├── bank_account.py     # Linked bank accounts model
│   │   └── chat.py             # Chat messages model
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user.py             # User schemas
│   │   ├── auth.py             # Auth request/response schemas
│   │   ├── transaction.py      # Transaction schemas
│   │   ├── tax.py              # Tax schemas
│   │   ├── tin.py              # TIN schemas
│   │   ├── subscription.py     # Subscription schemas
│   │   ├── referral.py         # Referral schemas
│   │   ├── bank.py             # Bank linking schemas
│   │   └── chat.py             # Chat schemas
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── user_service.py     # User management
│   │   ├── transaction_service.py  # Transaction logic
│   │   ├── tax_service.py      # Tax calculation & filing
│   │   ├── tin_service.py      # TIN application logic
│   │   ├── subscription_service.py # Subscription management
│   │   ├── referral_service.py # Referral tracking
│   │   ├── bank_service.py     # Bank linking (Mono/Okra)
│   │   └── chat_service.py     # AI Tax Assistant logic
│   │
│   ├── repositories/           # Database access layer
│   │   ├── __init__.py
│   │   ├── user_repo.py
│   │   ├── transaction_repo.py
│   │   ├── tax_repo.py
│   │   ├── tin_repo.py
│   │   ├── subscription_repo.py
│   │   ├── referral_repo.py
│   │   ├── bank_repo.py
│   │   └── chat_repo.py
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (auth, db session)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main API router
│   │       ├── auth.py         # Auth endpoints
│   │       ├── users.py        # User endpoints
│   │       ├── transactions.py # Transaction endpoints
│   │       ├── tax.py          # Tax endpoints
│   │       ├── tin.py          # TIN endpoints
│   │       ├── subscriptions.py    # Subscription endpoints
│   │       ├── referrals.py    # Referral endpoints
│   │       ├── banks.py        # Bank linking endpoints
│   │       └── chat.py         # AI Chat endpoints
│   │
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, password hashing
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── utils.py            # Helper functions
│   │
│   └── migrations/             # Alembic migrations
│       ├── env.py
│       ├── versions/
│       └── alembic.ini
│
└── tests/                      # Unit & integration tests
    ├── __init__.py
    ├── conftest.py             # Test fixtures
    ├── test_auth.py
    ├── test_users.py
    ├── test_transactions.py
    ├── test_tax.py
    └── test_referrals.py
```

---

## Dependencies (pyproject.toml)

```toml
[project]
name = "sabitax-backend"
version = "0.1.0"
description = "SabiTax Backend API"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "psycopg2-binary>=2.9.9",
    "alembic>=1.13.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
    "httpx>=0.26.0",
    "openai>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
]
```

### UV Commands

```bash
# Initialize project
uv init sabitax-backend

# Add dependencies
uv add fastapi "uvicorn[standard]" sqlalchemy asyncpg psycopg2-binary
uv add alembic pydantic pydantic-settings
uv add "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
uv add httpx openai

# Dev dependencies
uv add --dev pytest pytest-asyncio

# Run server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 7860
```

---

## Environment Variables (.env.example)

```env
# App
APP_NAME=SabiTax
DEBUG=true
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-here

# Database (NeonDB PostgreSQL)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# JWT Auth
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI (OpenAI for Tax Assistant)
OPENAI_API_KEY=sk-xxx

# Bank Integration (Optional)
MONO_SECRET_KEY=
OKRA_SECRET_KEY=
```

---

## HuggingFace Deployment

For HuggingFace Spaces deployment, create:

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY . .

# Install dependencies
RUN uv sync

# Expose port (HuggingFace uses 7860)
EXPOSE 7860

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### README.md (HuggingFace)

```yaml
---
title: SabiTax API
emoji: 💰
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
---
```
