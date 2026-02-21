"""
SabiTax Advanced AI endpoints.
"""
from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import CurrentUser
from app.services.sabitax_ai_service import SabiTaxAIService

router = APIRouter()


@router.post("/ingest")
async def ingest_document(
    current_user: CurrentUser,
    file: UploadFile = File(...),
    force: bool = False,
):
    """
    Ingest a new tax document into the AI's vector database.
    Requires authentication.
    """
    service = SabiTaxAIService()
    return await service.ingest_document(file=file, force=force)


@router.get("/stats")
async def get_stats(current_user: CurrentUser):
    """
    Get the current status and size of the AI's vector database.
    Requires authentication.
    """
    service = SabiTaxAIService()
    return await service.get_stats()


@router.post("/yearly-wrap")
async def create_yearly_wrap(
    current_user: CurrentUser,
    year: int = Form(...),
):
    """
    Generate a personalized yearly financial wrap video using AI.
    Requires authentication.
    """
    service = SabiTaxAIService()
    return await service.create_yearly_wrap(year=year)


@router.get("/health")
async def check_sabitax_ai_health():
    """
    Check the connection health to the AI, Gemini API, and Pinecone DB.
    Does NOT require authentication.
    """
    service = SabiTaxAIService()
    return await service.check_health()
