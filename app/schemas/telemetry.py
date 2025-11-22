"""
Telemetry Data Schemas

This module defines Pydantic models for telemetry data validation
and API request/response structures.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class TelemetryRecord(BaseModel):
    """Schema for a single telemetry record."""
    
    timestamp: Optional[float] = Field(None, description="Timestamp in seconds")
    speed: Optional[float] = Field(None, description="Vehicle speed (km/h)")
    throttle: Optional[float] = Field(None, ge=0, le=100, description="Throttle percentage")
    brake: Optional[float] = Field(None, ge=0, le=100, description="Brake percentage")
    steering: Optional[float] = Field(None, ge=-1, le=1, description="Steering angle (-1 to 1)")
    lap: Optional[int] = Field(None, description="Current lap number")
    
    class Config:
        extra = "allow"  # Allow additional fields from CSV


class TelemetryResponse(BaseModel):
    """Response schema for telemetry data upload."""
    
    filename: str = Field(..., description="Name of the uploaded file")
    records_count: int = Field(..., ge=0, description="Number of records processed")
    data: List[Dict[str, Any]] = Field(..., description="Parsed telemetry data")
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "lap_data.csv",
                "records_count": 1500,
                "data": [
                    {
                        "timestamp": 0.0,
                        "speed": 120.5,
                        "throttle": 85.0,
                        "brake": 0.0,
                        "steering": 0.1,
                        "lap": 1
                    }
                ],
                "processed_at": "2024-01-01T12:00:00"
            }
        }

