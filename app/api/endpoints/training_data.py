"""
Training Data Collection API Endpoint

ML 학습용 데이터를 PostgreSQL에 저장하는 API입니다.

핵심 기능:
- Upsert: 중복 키(subsession_id, cust_id)가 있으면 업데이트, 없으면 삽입
- 데이터 검증: Pydantic 스키마로 자동 검증
- 에러 처리: 명확한 에러 메시지 반환

설계 배경:
- Upsert 사용: 중복 데이터 방지 및 자동 업데이트를 위해 ON CONFLICT 처리
- 복합키: subsession_id + cust_id로 세션별 사용자 데이터 관리
"""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client  # 실제로는 PostgreSQL 클라이언트

from app.core.database import get_db_client
from app.schemas.iracing import TrainingDataCreate

router = APIRouter()


@router.post("/collect/training-data")
async def collect_training_data(
    payload: TrainingDataCreate,
    db_client: Client = Depends(get_db_client),
):
    """
    ML 학습용 피처 데이터를 PostgreSQL에 Upsert
    
    Args:
        payload: 학습 데이터 (Pydantic 스키마로 자동 검증)
        db_client: PostgreSQL 데이터베이스 클라이언트 (의존성 주입)
        
    Returns:
        저장된 데이터
        
    설명:
        - Upsert: ON CONFLICT 처리로 중복 방지 및 자동 업데이트
        - 복합키: subsession_id + cust_id로 세션별 사용자 데이터 관리
        - Pydantic 검증: 요청 데이터 자동 검증 및 타입 변환
    """
    try:
        # Pydantic 모델을 딕셔너리로 변환
        upsert_payload = payload.model_dump(mode="json")
        
        # PostgreSQL Upsert 실행
        # ON CONFLICT (subsession_id, cust_id) DO UPDATE
        response = (
            db_client.table("iracing_ml_training_data")
            .upsert(
                upsert_payload,
                on_conflict="subsession_id,cust_id",  # 복합키로 중복 검사
                returning="representation",  # 업데이트된 데이터 반환
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Database upsert returned no data.",
            )

        return {"data": response.data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
