"""
Database Connection (PostgreSQL)
"""

from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Get PostgreSQL client connection
    
    Note: This uses Supabase client library for PostgreSQL connection.
    In production, this would connect to Cloud SQL or managed PostgreSQL.
    """
    # For production, use Cloud SQL connection string
    # DATABASE_URL format: postgresql://user:password@host:port/database
    return create_client(
        settings.DATABASE_URL,
        # In production, use service account key or connection pooling
    )

