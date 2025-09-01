from fastapi import APIRouter

from backend.models.responses import HealthResponse
from backend.services.geocoding_service import GeocodingService

router = APIRouter()
geocoding_service = GeocodingService()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify system status."""
    health_status = geocoding_service.check_system_health()
    
    return HealthResponse(
        status=health_status['status'],
        version="1.0.0",
        asgs_files_available=health_status['asgs_files_available'],
        nominatim_accessible=health_status['nominatim_accessible']
    )