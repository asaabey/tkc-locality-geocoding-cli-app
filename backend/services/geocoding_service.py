import logging
from typing import List, Dict, Any
import pandas as pd
from shapely.geometry import Point

from src.geocode import geocode_name
from src.classify import classify_points
from backend.models.responses import LocationResult

logger = logging.getLogger(__name__)

class GeocodingService:
    """Service layer for geocoding and classification operations."""
    
    def __init__(self):
        self.logger = logger
    
    def process_single_location(self, location: str) -> LocationResult:
        """Process a single location and return all classifications."""
        try:
            # Geocode the location
            geocode_result = geocode_name(location)
            
            if geocode_result['lat'] is None or geocode_result['lon'] is None:
                return LocationResult(
                    location=location,
                    geocode_success=False,
                    error_message="Geocoding failed - location not found"
                )
            
            # Create DataFrame for classification
            df = pd.DataFrame([{
                'location': location,
                'Latitude': geocode_result['lat'],
                'Longitude': geocode_result['lon']
            }])
            
            # Classify the point
            classified_df = classify_points(df)
            
            if classified_df.empty:
                return LocationResult(
                    location=location,
                    latitude=geocode_result['lat'],
                    longitude=geocode_result['lon'],
                    geocode_success=True,
                    error_message="Classification failed - no ASGS data available"
                )
            
            # Extract the result
            row = classified_df.iloc[0]
            
            return LocationResult(
                location=location,
                latitude=row.get('Latitude'),
                longitude=row.get('Longitude'),
                sa1_code=row.get('SA1_CODE'),
                sa1_name=row.get('SA1_NAME'),
                sa2_code=row.get('SA2_CODE'),
                sa2_name=row.get('SA2_NAME'),
                sa3_code=row.get('SA3_CODE'),
                sa3_name=row.get('SA3_NAME'),
                sa4_code=row.get('SA4_CODE'),
                sa4_name=row.get('SA4_NAME'),
                gccsa_code=row.get('GCCSA_CODE'),
                gccsa_name=row.get('GCCSA_NAME'),
                state_code=row.get('STE_CODE'),
                state_name=row.get('STE_NAME'),
                iare_code=row.get('IARE_CODE'),
                iare_name=row.get('IARE_NAME'),
                geocode_success=True
            )
            
        except Exception as e:
            logger.error(f"Error processing location '{location}': {str(e)}")
            return LocationResult(
                location=location,
                geocode_success=False,
                error_message=f"Processing error: {str(e)}"
            )
    
    def process_batch_locations(self, locations: List[str]) -> List[LocationResult]:
        """Process multiple locations and return all classifications."""
        results = []
        
        for location in locations:
            result = self.process_single_location(location)
            results.append(result)
            
        return results
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check if system components are available."""
        try:
            # Test geocoding
            test_result = geocode_name("Alice Springs, NT")
            nominatim_accessible = test_result.get('lat') is not None
            
            # Test ASGS files (this will be checked in classify module)
            test_df = pd.DataFrame([{'location': 'test', 'Latitude': -23.0, 'Longitude': 133.0}])
            try:
                classified_df = classify_points(test_df)
                asgs_files_available = not classified_df.empty
            except Exception:
                asgs_files_available = False
            
            return {
                'status': 'healthy' if nominatim_accessible and asgs_files_available else 'degraded',
                'nominatim_accessible': nominatim_accessible,
                'asgs_files_available': asgs_files_available
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'nominatim_accessible': False,
                'asgs_files_available': False,
                'error': str(e)
            }