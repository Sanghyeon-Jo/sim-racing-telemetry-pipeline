"""
FastAPI Application Entry Point

Sim Racing Telemetry Pipeline API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import telemetry, collector
from app.core.config import settings

app = FastAPI(
    title="Sim Racing Telemetry Pipeline API",
    description="Data Ingestion, Parsing, Cleaning, and Serving API for Sim Racing Telemetry Logs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(telemetry.router, prefix="/api/v1", tags=["telemetry"])
app.include_router(collector.router, prefix="/api/v1", tags=["ingestion"])


@app.get("/")
async def root() -> dict:
    """
    Root endpoint for API health check.
    
    Returns:
        dict: API status and version information
    """
    return {
        "status": "healthy",
        "service": "Sim Racing Telemetry Pipeline API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "ok"}

