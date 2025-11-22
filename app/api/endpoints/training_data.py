"""
Training Data Collection API Endpoint

정제된 세션 피처를 PostgreSQL 테이블에 업서트
"""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.supabase import get_supabase_client
from app.schemas.iracing import TrainingDataCreate

router = APIRouter()


@router.post("/collect/training-data")
async def collect_training_data(
    payload: TrainingDataCreate,
    supabase: Client = Depends(get_supabase_client),
):
    """
    Upsert feature-engineered training rows into PostgreSQL.
    
    중복 키: subsession_id, cust_id
    """
    try:
        upsert_payload = payload.model_dump(mode="json")
        response = (
            supabase.table("iracing_ml_training_data")
            .upsert(
                upsert_payload,
                on_conflict="subsession_id,cust_id",
                returning="representation",
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

