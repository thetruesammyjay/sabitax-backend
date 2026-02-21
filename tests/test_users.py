"""
User endpoint and service tests.
"""
import pytest
from httpx import AsyncClient


class TestGetProfile:
    """Tests for GET /api/v1/users/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_profile_success(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test getting user profile with valid auth."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["is_verified"] is True
        assert "id" in data
        assert "avatar_initials" in data
        assert "compliance_score" in data
        assert "streak_days" in data
        assert "subscription_plan" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_profile_unauthenticated(self, client: AsyncClient):
        """Test getting profile without token returns 401."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_profile_invalid_token(self, client: AsyncClient):
        """Test getting profile with invalid token returns 401."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer fake-invalid-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_profile_avatar_initials(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test that avatar initials are derived from user name."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Test User -> "TU"
        assert data["avatar_initials"] == "TU"

    @pytest.mark.asyncio
    async def test_get_profile_subscription_defaults(
        self, client: AsyncClient, auth_headers
    ):
        """Test that default subscription plan is free."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["subscription_plan"] == "free"


class TestUpdateProfile:
    """Tests for PATCH /api/v1/users/me endpoint."""

    @pytest.mark.asyncio
    async def test_update_name_success(
        self, client: AsyncClient, auth_headers
    ):
        """Test updating user name."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_name_persists(
        self, client: AsyncClient, auth_headers
    ):
        """Test that name update persists across requests."""
        # Update name
        await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"name": "Persistent Name"},
        )

        # Fetch again
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["name"] == "Persistent Name"

    @pytest.mark.asyncio
    async def test_update_name_too_short(
        self, client: AsyncClient, auth_headers
    ):
        """Test that name with < 2 characters is rejected."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"name": "A"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_unauthenticated(self, client: AsyncClient):
        """Test updating profile without token returns 401."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"name": "Hacker"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_empty_body(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test updating with empty body returns current profile unchanged."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_user.name


class TestGetStats:
    """Tests for GET /api/v1/users/me/stats endpoint."""

    @pytest.mark.asyncio
    async def test_get_stats_success(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting user dashboard stats."""
        response = await client.get(
            "/api/v1/users/me/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "compliance_score" in data
        assert "streak_days" in data
        assert "total_income" in data
        assert "total_expenses" in data
        assert "estimated_tax" in data
        assert "income_documented_percent" in data
        assert "tax_due_date" in data

    @pytest.mark.asyncio
    async def test_get_stats_default_values(
        self, client: AsyncClient, auth_headers
    ):
        """Test that stats are zeroed out for a new user with no transactions."""
        response = await client.get(
            "/api/v1/users/me/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # New user has no income/expenses
        assert float(data["total_income"]) == 0
        assert float(data["total_expenses"]) == 0
        assert float(data["estimated_tax"]) == 0

    @pytest.mark.asyncio
    async def test_get_stats_unauthenticated(self, client: AsyncClient):
        """Test getting stats without token returns 401."""
        response = await client.get("/api/v1/users/me/stats")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_stats_streak_days(
        self, client: AsyncClient, auth_headers
    ):
        """Test that streak days match the test user's streak."""
        response = await client.get(
            "/api/v1/users/me/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["streak_days"] == 1  # Matches test_user fixture
