from fastapi import APIRouter, HTTPException
from typing import List

from backend.models.requests import SingleLocationRequest, BatchLocationRequest
from backend.models.responses import SingleLocationResponse, BatchLocationResponse, LocationResult
from backend.services.geocoding_service import GeocodingService

router = APIRouter()
geocoding_service = GeocodingService()

@router.post("/geocode/single", response_model=SingleLocationResponse)
async def geocode_single_location(request: SingleLocationRequest):
    """Geocode a single location and return coordinates + all ABS classifications."""
    try:
        result = geocoding_service.process_single_location(request.location)
        return SingleLocationResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/geocode/batch", response_model=BatchLocationResponse)
async def geocode_batch_locations(request: BatchLocationRequest):
    """Geocode multiple locations and return coordinates + all ABS classifications."""
    try:
        results = geocoding_service.process_batch_locations(request.locations)
        
        successful_geocodes = sum(1 for result in results if result.geocode_success)
        failed_geocodes = len(results) - successful_geocodes
        
        return BatchLocationResponse(
            results=results,
            total_processed=len(results),
            successful_geocodes=successful_geocodes,
            failed_geocodes=failed_geocodes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")