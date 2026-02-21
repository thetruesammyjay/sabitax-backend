"""
Tax service for tax calculations, obligations, and filing.
"""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.utils import (
    calculate_nigerian_pit,
    generate_filing_reference,
    get_next_tax_due_date,
    get_tax_year,
)
from app.models.tax import TaxFiling
from app.repositories.tax_repo import TaxRepository
from app.repositories.transaction_repo import TransactionRepository
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


class TaxService:
    """Tax business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tax_repo = TaxRepository(db)
        self.transaction_repo = TransactionRepository(db)

    async def get_obligations(
        self,
        user_id: uuid.UUID,
    ) -> TaxObligationsResponse:
        """
        Get user's tax obligations.

        Args:
            user_id: User's ID

        Returns:
            TaxObligationsResponse with obligations and total
        """
        # Get current year totals
        current_year = date.today().year
        totals = await self.transaction_repo.get_totals_by_user(user_id, year=current_year)
        total_income = totals.get("income", Decimal("0"))

        # Calculate PIT
        tax_result = calculate_nigerian_pit(total_income)
        pit_amount = tax_result["tax_amount"]

        obligations = []

        # Personal Income Tax
        obligations.append(
            TaxObligationItem(
                type="PIT",
                name="Personal Income Tax",
                amount=pit_amount,
                due_date=get_next_tax_due_date(),
                status="pending" if pit_amount > 0 else "none",
                based_on=f"₦{total_income:,.0f} annual income" if total_income > 0 else "No recorded income",
            )
        )

        # VAT (only if business transactions)
        # For individuals, VAT typically doesn't apply
        obligations.append(
            TaxObligationItem(
                type="VAT",
                name="Value Added Tax",
                amount=Decimal("0"),
                due_date=None,
                status="none",
                based_on="No taxable business transactions",
            )
        )

        total_due = sum((o.amount for o in obligations if o.status == "pending"), Decimal("0"))

        return TaxObligationsResponse(
            obligations=obligations,
            total_due=total_due,
        )

    async def get_estimate(
        self,
        user_id: uuid.UUID,
    ) -> TaxEstimateResponse:
        """
        Get estimated tax liability.

        Args:
            user_id: User's ID

        Returns:
            TaxEstimateResponse with tax calculation
        """
        current_year = date.today().year
        totals = await self.transaction_repo.get_totals_by_user(user_id, year=current_year)
        total_income = totals.get("income", Decimal("0"))

        # Calculate tax
        tax_result = calculate_nigerian_pit(total_income)

        # Calculate potential savings (estimate)
        # Suggest possible reliefs that could reduce tax
        potential_savings = Decimal("0")
        if total_income > Decimal("1000000"):
            # Estimate 5% potential savings through optimization
            potential_savings = (tax_result["tax_amount"] * Decimal("0.05")).quantize(
                Decimal("0.01")
            )

        return TaxEstimateResponse(
            total_income=total_income,
            taxable_income=tax_result["taxable_income"],
            estimated_tax=tax_result["tax_amount"],
            tax_rate=tax_result["effective_rate"],
            potential_savings=potential_savings,
            next_due_date=get_next_tax_due_date(),
            cra=tax_result["cra"],
        )

    async def file_tax(
        self,
        user_id: uuid.UUID,
        data: TaxFilingRequest,
    ) -> TaxFilingResponse:
        """
        Submit tax filing.

        Args:
            user_id: User's ID
            data: Filing request data

        Returns:
            TaxFilingResponse with filing details
        """
        # Check for duplicate filing
        existing = await self.tax_repo.get_filing_by_year_and_type(
            user_id, data.year, data.tax_type
        )
        if existing and existing.status in ["submitted", "processing", "completed"]:
            raise BadRequestError(
                f"{data.tax_type} for {data.year} has already been filed"
            )

        # Get income for the year
        totals = await self.transaction_repo.get_totals_by_user(user_id, year=data.year)
        total_income = totals.get("income", Decimal("0"))

        # Calculate tax amount
        tax_result = calculate_nigerian_pit(total_income)

        # Create filing
        filing = TaxFiling(
            user_id=user_id,
            tax_type=data.tax_type,
            tax_year=data.year,
            amount=tax_result["tax_amount"],
            status="submitted",
            reference_number=generate_filing_reference(),
            declaration_data=data.declaration,
            filed_at=datetime.now(timezone.utc),
        )

        filing = await self.tax_repo.create_filing(filing)

        return TaxFilingResponse(
            filing_id=str(filing.id),
            status=filing.status,
            reference_number=filing.reference_number,
            filed_at=filing.filed_at,
        )

    async def get_filings(
        self,
        user_id: uuid.UUID,
        tax_type: str | None = None,
        year: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> TaxFilingHistoryResponse:
        """
        Get tax filing history.

        Args:
            user_id: User's ID
            tax_type: Filter by type
            year: Filter by year
            limit: Max results
            offset: Skip results

        Returns:
            TaxFilingHistoryResponse with filing history
        """
        filings = await self.tax_repo.get_filings_by_user(
            user_id=user_id,
            tax_type=tax_type,
            year=year,
            limit=limit,
            offset=offset,
        )

        total = await self.tax_repo.count_filings_by_user(user_id)

        return TaxFilingHistoryResponse(
            filings=[
                TaxFilingHistoryItem(
                    id=str(f.id),
                    tax_type=f.tax_type,
                    tax_year=f.tax_year,
                    amount=f.amount,
                    status=f.status,
                    reference_number=f.reference_number,
                    filed_at=f.filed_at,
                )
                for f in filings
            ],
            total=total,
        )

    async def get_optimization(
        self,
        user_id: uuid.UUID,
    ) -> TaxOptimizationResponse:
        """
        Get tax optimization suggestions.

        Args:
            user_id: User's ID

        Returns:
            TaxOptimizationResponse with suggestions
        """
        current_year = date.today().year
        totals = await self.transaction_repo.get_totals_by_user(user_id, year=current_year)
        total_income = totals.get("income", Decimal("0"))

        suggestions = []
        potential_savings = Decimal("0")

        if total_income > Decimal("500000"):
            # Rent relief suggestion
            rent_savings = Decimal("15000")
            suggestions.append(
                TaxOptimizationSuggestion(
                    type="relief",
                    title="Rent Relief",
                    description="Claim rent payments as tax relief. Keep receipts of rent payments.",
                    estimated_savings=rent_savings,
                )
            )
            potential_savings += rent_savings

        if total_income > Decimal("1000000"):
            # Pension contribution suggestion
            pension_savings = (total_income * Decimal("0.08") * Decimal("0.20")).quantize(
                Decimal("0.01")
            )
            suggestions.append(
                TaxOptimizationSuggestion(
                    type="pension",
                    title="Pension Contribution",
                    description="Contribute to a pension scheme. Up to 20% of basic salary is tax-free.",
                    estimated_savings=pension_savings,
                )
            )
            potential_savings += pension_savings

        if total_income > Decimal("2000000"):
            # Life insurance suggestion
            insurance_savings = Decimal("10000")
            suggestions.append(
                TaxOptimizationSuggestion(
                    type="insurance",
                    title="Life Insurance Premium",
                    description="Life insurance premiums qualify for tax relief under PITA.",
                    estimated_savings=insurance_savings,
                )
            )
            potential_savings += insurance_savings

        # NHF contribution
        if total_income > Decimal("0"):
            suggestions.append(
                TaxOptimizationSuggestion(
                    type="nhf",
                    title="NHF Contribution",
                    description="National Housing Fund contributions (2.5% of basic salary) are tax-deductible.",
                    estimated_savings=Decimal("5000"),
                )
            )
            potential_savings += Decimal("5000")

        return TaxOptimizationResponse(
            potential_savings=potential_savings,
            suggestions=suggestions,
        )
