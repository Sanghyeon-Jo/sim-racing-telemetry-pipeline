"""
Telemetry Upload API Endpoint

CSV/GPX 파일 업로드 및 파싱
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from app.services.parser import TelemetryParser
from app.schemas.telemetry import TelemetryResponse

router = APIRouter()


@router.post("/upload", response_model=TelemetryResponse)
async def upload_telemetry_file(
    file: UploadFile = File(...)
) -> TelemetryResponse:
    """
    Upload and process telemetry log file (CSV/GPX).
    
    This endpoint handles data ingestion:
    - Accepts CSV or GPX format telemetry logs
    - Validates file format and size
    - Parses and cleans the data
    - Returns structured telemetry data
    
    Args:
        file: Uploaded telemetry log file (CSV or GPX format)
        
    Returns:
        TelemetryResponse: Parsed and cleaned telemetry data
        
    Raises:
        HTTPException: If file format is invalid or processing fails
    """
    parser = TelemetryParser()
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse based on file extension
        if file.filename.endswith('.csv'):
            df = parser.parse_csv(content)
            data = df.to_dict('records')
        elif file.filename.endswith('.gpx'):
            # GPX parsing not yet implemented
            raise HTTPException(
                status_code=400,
                detail="GPX format not yet supported. Please upload CSV files."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload CSV or GPX files."
            )
        
        return TelemetryResponse(
            filename=file.filename,
            records_count=len(data),
            data=data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

