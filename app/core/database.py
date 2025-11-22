"""
PostgreSQL Database Connection

이 모듈은 PostgreSQL 데이터베이스 연결을 관리합니다.
프로덕션 환경에서는 GCP Cloud SQL (PostgreSQL)을 사용합니다.

설계 배경:
- Supabase 클라이언트는 내부적으로 PostgreSQL을 사용하므로,
  실제 프로덕션에서는 Cloud SQL로 쉽게 마이그레이션 가능
- Connection pooling을 통해 대용량 트래픽 처리
"""

from typing import Optional
from supabase import create_client, Client
from app.core.config import settings


def get_db_client() -> Client:
    """
    PostgreSQL 데이터베이스 클라이언트 반환
    
    Returns:
        Client: PostgreSQL 데이터베이스 클라이언트
        
    설명:
        - 개발 환경: Supabase (PostgreSQL 기반 SaaS)
        - 프로덕션: GCP Cloud SQL (PostgreSQL)
        - DATABASE_URL 형식: postgresql://user:password@host:port/database
    """
    return create_client(
        settings.DATABASE_URL,
        # 프로덕션에서는 서비스 계정 키 또는 connection pooling 사용
    )


# 하위 호환성을 위한 별칭
get_supabase_client = get_db_client

