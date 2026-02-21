"""
Tax endpoints.
"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.tax import (
    TaxEstimateResponse,
    TaxFilingHistoryResponse,
    TaxFilingRequest,
    TaxFilingResponse,
    TaxObligationsResponse,
    TaxOptimizationResponse,
)
from app.services.tax_service import TaxService

router = APIRouter()


@router.get("/obligations", response_model=TaxObligationsResponse)
async def get_tax_obligations(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get user's tax obligations.

    Returns all pending tax obligations with amounts and due dates.
    """
    service = TaxService(db)
    return await service.get_obligations(current_user.id)


@router.get("/estimate", response_model=TaxEstimateResponse)
async def get_tax_estimate(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get estimated tax liability.

    Calculates Nigerian Personal Income Tax based on recorded income.
    """
    service = TaxService(db)
    return await service.get_estimate(current_user.id)


@router.post("/file", response_model=TaxFilingResponse, status_code=201)
async def file_tax(
    data: TaxFilingRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    File tax returns.

    - **tax_type**: Type of tax (PIT, VAT, CIT, PAYE)
    - **year**: Tax year
    - **declaration**: Additional declaration data (optional)
    """
    service = TaxService(db)
    return await service.file_tax(
        user_id=current_user.id,
        data=data,
    )


@router.get("/filings", response_model=TaxFilingHistoryResponse)
async def get_tax_filings(
    current_user: CurrentUser,
    db: DbSession,
    tax_type: str | None = Query(None, description="Filter by tax type"),
    year: int | None = Query(None, description="Filter by year"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get filing history.

    Returns list of past tax filings with status.
    """
    service = TaxService(db)
    return await service.get_filings(
        user_id=current_user.id,
        tax_type=tax_type,
        year=year,
        limit=limit,
        offset=offset,
    )


@router.get("/optimization", response_model=TaxOptimizationResponse)
async def get_tax_optimization(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get tax optimization suggestions.

    Returns personalized suggestions for reducing tax liability.
    """
    service = TaxService(db)
    return await service.get_optimization(current_user.id)
