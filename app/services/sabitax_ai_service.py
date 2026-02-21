"""
Service for proxying requests to SabiTax AI endpoints (Hugging Face Space).
"""
import httpx
from fastapi import UploadFile

from app.config import get_settings
from app.core.exceptions import ExternalServiceError


class SabiTaxAIService:
    """Service to interact with the SabiTax AI model on Hugging Face."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.nexusbert_api_url.rstrip("/")
        self.headers = {}
        if self.settings.nexusbert_api_key:
            self.headers["X-API-Key"] = self.settings.nexusbert_api_key

    async def _handle_response(self, response: httpx.Response, endpoint: str) -> dict:
        """Centralized response handling for SabiTax AI API."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            try:
                error_data = response.json()
                raise ExternalServiceError(
                    message=f"Validation error from SabiTax AI {endpoint}: {error_data}"
                )
            except Exception:
                raise ExternalServiceError(
                    message=f"Validation error from SabiTax AI {endpoint}"
                )
        else:
            raise ExternalServiceError(
                message=f"Failed to communicate with SabiTax AI {endpoint} (Status {response.status_code})"
            )

    async def ingest_document(self, file: UploadFile, force: bool = False) -> dict:
        """
        Ingest a new document into the SabiTax AI vector database.
        Proxy to POST /ingest
        """
        api_url = f"{self.base_url}/ingest"
        params = {"force": str(force).lower()}

        try:
            # We need to read the file entirely into memory to forward it
            file_content = await file.read()
            files = {"file": (file.filename, file_content, file.content_type)}

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    api_url,
                    headers=self.headers,
                    params=params,
                    files=files,
                )
                return await self._handle_response(response, "/ingest")
        except Exception as e:
            if isinstance(e, ExternalServiceError):
                raise
            raise ExternalServiceError(message=f"Error connecting to SabiTax AI: {str(e)}")

    async def get_stats(self) -> dict:
        """
        Get statistics about the SabiTax AI vector database.
        Proxy to GET /stats
        """
        api_url = f"{self.base_url}/stats"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    api_url,
                    headers=self.headers,
                )
                return await self._handle_response(response, "/stats")
        except Exception as e:
            if isinstance(e, ExternalServiceError):
                raise
            raise ExternalServiceError(message=f"Error connecting to SabiTax AI: {str(e)}")

    async def create_yearly_wrap(self, year: int) -> dict:
        """
        Generate a yearly financial wrap video.
        Proxy to POST /yearly-wrap
        """
        api_url = f"{self.base_url}/yearly-wrap"
        data = {"year": year}

        try:
            # The API expects application/x-www-form-urlencoded
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    api_url,
                    headers=self.headers,
                    data=data,
                )
                return await self._handle_response(response, "/yearly-wrap")
        except Exception as e:
            if isinstance(e, ExternalServiceError):
                raise
            raise ExternalServiceError(message=f"Error connecting to SabiTax AI: {str(e)}")

    async def check_health(self) -> dict:
        """
        Check the status of SabiTax AI services.
        Proxy to GET /health (Does not require API key)
        """
        api_url = f"{self.base_url}/health"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(api_url)
                return await self._handle_response(response, "/health")
        except Exception as e:
            if isinstance(e, ExternalServiceError):
                raise
            raise ExternalServiceError(message=f"Error connecting to SabiTax AI: {str(e)}")
