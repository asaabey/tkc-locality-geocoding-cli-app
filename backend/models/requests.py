from typing import List
from pydantic import BaseModel, Field

class SingleLocationRequest(BaseModel):
    location: str = Field(..., description="Location name to geocode", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Alice Springs Hospital, NT"
            }
        }

class BatchLocationRequest(BaseModel):
    locations: List[str] = Field(..., description="List of location names to geocode", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "locations": [
                    "Alice Springs Hospital, NT",
                    "Darwin Hospital, NT",
                    "Katherine Hospital, NT"
                ]
            }
        }