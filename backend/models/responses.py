from typing import List, Optional
from pydantic import BaseModel

class LocationResult(BaseModel):
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    sa1_code: Optional[str] = None
    sa1_name: Optional[str] = None
    sa2_code: Optional[str] = None
    sa2_name: Optional[str] = None
    sa3_code: Optional[str] = None
    sa3_name: Optional[str] = None
    sa4_code: Optional[str] = None
    sa4_name: Optional[str] = None
    gccsa_code: Optional[str] = None
    gccsa_name: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    iare_code: Optional[str] = None
    iare_name: Optional[str] = None
    ireg_code: Optional[str] = None
    ireg_name: Optional[str] = None
    geocode_success: bool = False
    error_message: Optional[str] = None

class SingleLocationResponse(BaseModel):
    result: LocationResult

class BatchLocationResponse(BaseModel):
    results: List[LocationResult]
    total_processed: int
    successful_geocodes: int
    failed_geocodes: int

class HealthResponse(BaseModel):
    status: str
    version: str
    asgs_files_available: bool
    nominatim_accessible: bool