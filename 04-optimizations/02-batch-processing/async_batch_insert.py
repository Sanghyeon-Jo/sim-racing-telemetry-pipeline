"""
대용량 배치 처리 최적화: Async/Batch Insert

문제: 수천 개의 세션 데이터 처리 시 API 병목 및 메모리 부족
해결: 
- 단일 레코드 처리 → 500개씩 배치 처리
- asyncio.gather()로 병렬 처리
- Rate Limiting으로 API 안정성 확보
"""

import asyncio
from typing import List, Dict, Any
from supabase import Client


async def async_batch_insert(
    supabase: Client,
    table_name: str,
    records: List[Dict[str, Any]],
    chunk_size: int = 500,
    max_concurrent: int = 5
) -> int:
    """
    비동기 배치 삽입 (병렬 처리)
    
    Args:
        supabase: Supabase 클라이언트
        table_name: 테이블 이름
        records: 삽입할 레코드 리스트
        chunk_size: 배치 크기 (기본값: 500)
        max_concurrent: 최대 동시 처리 수
        
    Returns:
        성공적으로 삽입된 레코드 수
    """
    total = len(records)
    chunks = [records[i:i + chunk_size] for i in range(0, total, chunk_size)]
    total_chunks = len(chunks)
    
    print(f"🚀 {table_name} 총 {total}개 데이터를 {total_chunks}개 배치로 병렬 처리 시작")
    
    semaphore = asyncio.Semaphore(max_concurrent)  # 동시 처리 수 제한
    
    async def insert_chunk(chunk: List[Dict[str, Any]], chunk_num: int):
        async with semaphore:  # Rate Limiting
            try:
                res = supabase.table(table_name).insert(chunk).execute()
                if res.data:
                    print(f"✅ {table_name} chunk {chunk_num}/{total_chunks} 성공 ({len(chunk)} rows)")
                    return len(chunk)
                else:
                    print(f"❌ {table_name} chunk {chunk_num}/{total_chunks} 실패: 응답 없음")
                    return 0
            except Exception as e:
                print(f"❌ {table_name} chunk {chunk_num}/{total_chunks} 예외: {repr(e)}")
                return 0
    
    # 모든 청크를 병렬로 처리
    results = await asyncio.gather(*[
        insert_chunk(chunk, i + 1) 
        for i, chunk in enumerate(chunks)
    ])
    
    total_inserted = sum(results)
    print(f"✅ {table_name} 총 {total_inserted}/{total}개 레코드 삽입 완료")
    return total_inserted


async def process_sessions_parallel(
    supabase: Client,
    sessions: List[Dict[str, Any]],
    process_func,
    max_concurrent: int = 10
) -> List[Any]:
    """
    여러 세션을 병렬로 처리
    
    Args:
        supabase: Supabase 클라이언트
        sessions: 세션 리스트
        process_func: 세션 처리 함수 (async)
        max_concurrent: 최대 동시 처리 수
        
    Returns:
        처리 결과 리스트
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(session):
        async with semaphore:
            return await process_func(supabase, session)
    
    results = await asyncio.gather(*[
        process_with_limit(session) 
        for session in sessions
    ])
    
    return results

