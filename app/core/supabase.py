"""
PostgreSQL Database Connection (Legacy)

⚠️ 이 파일은 하위 호환성을 위해 유지됩니다.
새로운 코드는 app.core.database.get_db_client()를 사용하세요.

실제로는 PostgreSQL 데이터베이스에 연결하며,
Supabase는 PostgreSQL 기반 SaaS입니다.
"""

from app.core.database import get_db_client, get_supabase_client

__all__ = ["get_db_client", "get_supabase_client"]
