"""
Referral endpoint and service tests.
"""
import uuid
from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.services.referral_service import ReferralService


@pytest_asyncio.fixture(scope="function")
async def referrer_user(db_session: AsyncSession) -> User:
    """Create a referrer user with a referral code."""
    user = User(
        id=uuid.uuid4(),
        name="Referrer User",
        email="referrer@example.com",
        password_hash=hash_password("ReferrerPass123"),
        is_verified=True,
        referral_code="REFER123",
        streak_days=0,
        last_active_date=date.today(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def referred_user(db_session: AsyncSession) -> User:
    """Create a user who will be referred (no referral code, no prior referral)."""
    user = User(
        id=uuid.uuid4(),
        name="New User",
        email="newuser@example.com",
        password_hash=hash_password("NewUserPass123"),
        is_verified=True,
        referral_code="NEWUSR01",
        streak_days=0,
        last_active_date=date.today(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def referred_auth_headers(referred_user: User) -> dict:
    """Auth headers for the referred user."""
    token = create_access_token(str(referred_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def referrer_auth_headers(referrer_user: User) -> dict:
    """Auth headers for the referrer user."""
    token = create_access_token(str(referrer_user.id))
    return {"Authorization": f"Bearer {token}"}


class TestGetReferralInfo:
    """Tests for GET /api/v1/referrals endpoint."""

    @pytest.mark.asyncio
    async def test_get_referral_info_success(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test getting referral info for an authenticated user."""
        response = await client.get(
            "/api/v1/referrals", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "referral_code" in data
        assert data["referral_code"] == test_user.referral_code
        assert "total_earnings" in data
        assert "monthly_limit" in data
        assert "referral_count" in data
        assert "pending_count" in data

    @pytest.mark.asyncio
    async def test_get_referral_info_default_stats(
        self, client: AsyncClient, auth_headers
    ):
        """Test that a new user has zero referral stats."""
        response = await client.get(
            "/api/v1/referrals", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["total_earnings"]) == 0
        assert data["referral_count"] == 0
        assert data["pending_count"] == 0

    @pytest.mark.asyncio
    async def test_get_referral_info_unauthenticated(
        self, client: AsyncClient
    ):
        """Test getting referral info without token returns 401."""
        response = await client.get("/api/v1/referrals")

        assert response.status_code == 401


class TestGetReferralHistory:
    """Tests for GET /api/v1/referrals/history endpoint."""

    @pytest.mark.asyncio
    async def test_get_history_empty(
        self, client: AsyncClient, auth_headers
    ):
        """Test that a new user has empty referral history."""
        response = await client.get(
            "/api/v1/referrals/history", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["referrals"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_history_unauthenticated(self, client: AsyncClient):
        """Test getting history without token returns 401."""
        response = await client.get("/api/v1/referrals/history")

        assert response.status_code == 401


class TestApplyReferralCode:
    """Tests for POST /api/v1/referrals/apply endpoint."""

    @pytest.mark.asyncio
    async def test_apply_referral_code_success(
        self,
        client: AsyncClient,
        referred_auth_headers,
        referrer_user,
    ):
        """Test applying a valid referral code."""
        response = await client.post(
            "/api/v1/referrals/apply",
            headers=referred_auth_headers,
            json={"referral_code": referrer_user.referral_code},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["applied"] is True
        assert data["referrer_name"] == referrer_user.name
        assert "message" in data

    @pytest.mark.asyncio
    async def test_apply_invalid_referral_code(
        self, client: AsyncClient, referred_auth_headers
    ):
        """Test applying a non-existent referral code returns 400."""
        response = await client.post(
            "/api/v1/referrals/apply",
            headers=referred_auth_headers,
            json={"referral_code": "DOESNTEXIST"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_apply_own_referral_code(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test applying your own referral code is rejected."""
        response = await client.post(
            "/api/v1/referrals/apply",
            headers=auth_headers,
            json={"referral_code": test_user.referral_code},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_apply_referral_code_twice(
        self,
        client: AsyncClient,
        referred_auth_headers,
        referrer_user,
    ):
        """Test applying a referral code twice is rejected."""
        # First application
        await client.post(
            "/api/v1/referrals/apply",
            headers=referred_auth_headers,
            json={"referral_code": referrer_user.referral_code},
        )

        # Second application - should fail
        response = await client.post(
            "/api/v1/referrals/apply",
            headers=referred_auth_headers,
            json={"referral_code": referrer_user.referral_code},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_apply_referral_code_unauthenticated(
        self, client: AsyncClient
    ):
        """Test applying referral code without auth returns 401."""
        response = await client.post(
            "/api/v1/referrals/apply",
            json={"referral_code": "TESTCODE"},
        )

        assert response.status_code == 401


class TestReferralServiceUnit:
    """Unit tests for ReferralService logic."""

    def test_mask_email_standard(self, db_session):
        """Test email masking with a standard email."""
        service = ReferralService(db_session)
        result = service._mask_email("testuser@example.com")

        assert result.startswith("t")
        assert result.endswith("@example.com")
        assert "*" in result
        # "testuser" -> "t******r"
        assert result == "t******r@example.com"

    def test_mask_email_short_local(self, db_session):
        """Test email masking with a 2-char local part."""
        service = ReferralService(db_session)
        result = service._mask_email("ab@example.com")

        assert result == "a*@example.com"

    def test_mask_email_single_char(self, db_session):
        """Test email masking with a single-char local part."""
        service = ReferralService(db_session)
        result = service._mask_email("x@example.com")

        assert result == "x*@example.com"

    def test_mask_email_no_at_sign(self, db_session):
        """Test email masking with no @ sign returns as-is."""
        service = ReferralService(db_session)
        result = service._mask_email("no-at-sign")

        assert result == "no-at-sign"

    @pytest.mark.asyncio
    async def test_complete_referral_no_referral(self, db_session):
        """Test completing a referral for a user with no referral returns False."""
        service = ReferralService(db_session)
        result = await service.complete_referral(uuid.uuid4())

        assert result is False

    @pytest.mark.asyncio
    async def test_get_referral_history_after_apply(
        self,
        client: AsyncClient,
        referrer_auth_headers,
        referred_auth_headers,
        referrer_user,
    ):
        """Test referral history shows up for the referrer after a code is applied."""
        # Apply the referral code as the referred user
        await client.post(
            "/api/v1/referrals/apply",
            headers=referred_auth_headers,
            json={"referral_code": referrer_user.referral_code},
        )

        # Check referrer's history
        response = await client.get(
            "/api/v1/referrals/history",
            headers=referrer_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["referrals"]) == 1
        assert data["referrals"][0]["status"] == "pending"
        assert float(data["referrals"][0]["reward"]) == 1000.00
