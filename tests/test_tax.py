"""
Tax calculation and endpoint tests.
"""
from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.core.utils import (
    calculate_nigerian_pit,
    calculate_vat,
    calculate_cra,
    format_naira,
)


class TestTaxCalculations:
    """Tests for Nigerian tax calculation utilities."""

    def test_calculate_pit_first_bracket(self):
        """Test PIT calculation for first bracket (<=₦300,000)."""
        result = calculate_nigerian_pit(Decimal("300000"))

        assert result["gross_income"] == Decimal("300000")
        # CRA = max(200000, 3000) + 60000 = 260000
        # Taxable = 300000 - 260000 = 40000
        # Tax = 40000 * 7% = 2800
        assert result["tax_amount"] == Decimal("2800.00")

    def test_calculate_pit_second_bracket(self):
        """Test PIT calculation for second bracket (₦300,001 - ₦600,000)."""
        result = calculate_nigerian_pit(Decimal("600000"))

        # CRA = max(200000, 6000) + 120000 = 320000
        # Taxable = 600000 - 320000 = 280000
        # Tax = 280000 * 7% = 19600
        assert result["tax_amount"] == Decimal("19600.00")

    def test_calculate_pit_high_income(self):
        """Test PIT calculation for high income (>₦3.2M)."""
        result = calculate_nigerian_pit(Decimal("10000000"))

        # Should use all brackets with top bracket at 24%
        assert result["tax_amount"] > Decimal("0")
        assert 0 < result["effective_rate"] <= Decimal("24")

    def test_calculate_pit_with_cra(self):
        """Test that CRA is calculated correctly."""
        result = calculate_nigerian_pit(Decimal("5000000"))

        # CRA = ₦200,000 + 20% of gross income
        expected_cra = Decimal("200000") + (Decimal("5000000") * Decimal("0.20"))
        assert result["cra"] == expected_cra

    def test_calculate_pit_zero_income(self):
        """Test PIT calculation for zero income."""
        result = calculate_nigerian_pit(Decimal("0"))

        assert result["tax_amount"] == Decimal("0")
        assert result["effective_rate"] == Decimal("0")

    def test_calculate_vat(self):
        """Test VAT calculation at 7.5%."""
        result = calculate_vat(Decimal("100000"))

        assert result == Decimal("7500.00")

    def test_calculate_cra(self):
        """Test Consolidated Relief Allowance calculation."""
        result = calculate_cra(Decimal("2000000"))

        # CRA = max(₦200,000, 1% of gross) + 20% of gross
        # = max(200000, 20000) + 400000 = 200000 + 400000 = 600000
        assert result == Decimal("600000.00")


class TestTaxEndpoints:
    """Tests for tax API endpoints."""

    @pytest.mark.asyncio
    async def test_get_tax_estimate(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting tax estimate."""
        response = await client.get(
            "/api/v1/tax/estimate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "estimated_tax" in data
        assert "tax_rate" in data
        assert "cra" in data

    @pytest.mark.asyncio
    async def test_get_tax_obligations(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting tax obligations."""
        response = await client.get(
            "/api/v1/tax/obligations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "obligations" in data
        assert "total_due" in data

    @pytest.mark.asyncio
    async def test_get_tax_optimization(
        self, client: AsyncClient, auth_headers
    ):
        """Test getting tax optimization suggestions."""
        response = await client.get(
            "/api/v1/tax/optimization",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert "potential_savings" in data


class TestFormatNaira:
    """Tests for Naira formatting utility."""

    def test_format_naira_basic(self):
        """Test basic Naira formatting."""
        result = format_naira(Decimal("1234567"))

        assert "₦" in result
        assert "1,234,567" in result

    def test_format_naira_negative(self):
        """Test Naira formatting with negative amount."""
        result = format_naira(Decimal("-5000"), show_sign=True)

        assert "-₦" in result or "₦-" in result

    def test_format_naira_zero(self):
        """Test Naira formatting with zero."""
        result = format_naira(Decimal("0"))

        assert "₦0" in result
