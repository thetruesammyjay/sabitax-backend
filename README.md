---
title: SabiTax Backend
emoji: 💰
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
---

# SabiTax Backend API

Nigerian Tax Management Platform - FastAPI Backend

## Features

- 🔐 **Authentication**: Email/password with JWT, Google/Apple OAuth
- 📊 **Transactions**: Track income and expenses with categories
- 💰 **Tax Calculations**: Nigerian PIT, VAT, PAYE with FIRS brackets
- 📋 **Tax Filing**: Submit and track tax returns
- 🆔 **TIN Management**: Apply for Tax Identification Number
- 💳 **Bank Integration**: Link accounts via Mono/Okra
- 🤖 **AI Tax Assistant**: OpenAI-powered tax guidance
- 👥 **Referrals**: Earn ₦1,000 per referral
- 📱 **Notifications**: Tax reminders and updates

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async with asyncpg)
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT with python-jose
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest-asyncio

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL (or NeonDB)
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/thetruesammyjay/sabitax-backend.git
cd sabitax-backend

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your settings

# Run database migrations
uv run alembic upgrade head

# Start the server
uv run uvicorn main:app --reload
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Secret key for JWT tokens |
| `OPENAI_API_KEY` | OpenAI API key for AI chat |
| `MONO_SECRET_KEY` | Mono API key (optional) |
| `OKRA_SECRET_KEY` | Okra API key (optional) |

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register` | Create account |
| `POST /api/v1/auth/login` | Login |
| `GET /api/v1/users/me` | Get profile |
| `GET /api/v1/transactions` | List transactions |
| `GET /api/v1/tax/estimate` | Get tax estimate |
| `POST /api/v1/tax/file` | File tax return |
| `POST /api/v1/chat` | AI tax assistant |
| `GET /api/v1/health` | Health check |

## Nigerian Tax Features

### Personal Income Tax (PIT)
- Calculates tax using FIRS progressive brackets (7%-24%)
- Applies Consolidated Relief Allowance (CRA) automatically
- Tracks filing deadlines (March 31st annually)

### Tax Brackets

| Income Range | Rate |
|-------------|------|
| First ₦300,000 | 7% |
| Next ₦300,000 | 11% |
| Next ₦500,000 | 15% |
| Next ₦500,000 | 19% |
| Next ₦1,600,000 | 21% |
| Above ₦3,200,000 | 24% |

## Testing

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio aiosqlite

# Run tests
uv run pytest -v
```

## Deployment

### HuggingFace Spaces

1. Create a new Space with Docker SDK
2. Add environment variables in Settings
3. Push the repository

### Docker

```bash
docker build -t sabitax-backend .
docker run -p 7860:7860 --env-file .env sabitax-backend
```

## Project Structure

```
sabitax-backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Security, utils, exceptions
│   ├── models/          # SQLAlchemy models
│   ├── repositories/    # Database access layer
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── config.py        # Settings
│   └── database.py      # DB connection
├── alembic/             # Database migrations
├── tests/               # Test files
├── main.py              # FastAPI app
├── Dockerfile
└── pyproject.toml
```

## License

MIT License

## Author

[@thetruesammyjay](https://github.com/thetruesammyjay)
