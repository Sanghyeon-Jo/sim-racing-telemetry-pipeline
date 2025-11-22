"""
배치 삽입 모듈

500개씩 배치 처리로 대용량 데이터 적재 최적화
"""

from typing import List, Dict, Any
from supabase import Client


def chunked_insert(
    supabase: Client,
    table_name: str,
    records: List[Dict[str, Any]],
    chunk_size: int = 500
) -> int:
    """
    배치 단위로 데이터 삽입
    
    Args:
        supabase: Supabase 클라이언트
        table_name: 테이블 이름
        records: 삽입할 레코드 리스트
        chunk_size: 배치 크기 (기본값: 500)
        
    Returns:
        성공적으로 삽입된 레코드 수
    """
    total = len(records)
    print(f"🚚 {table_name} 총 {total}개 데이터를 {chunk_size}개씩 나눠 insert 시작")
    
    inserted_count = 0
    
    for i in range(0, total, chunk_size):
        chunk = records[i:i + chunk_size]
        batch_num = i // chunk_size + 1
        total_batches = (total + chunk_size - 1) // chunk_size
        
        try:
            res = supabase.table(table_name).insert(chunk).execute()
            if not res.data:
                print(f"❌ {table_name} insert 실패 (chunk {batch_num}/{total_batches}): 응답 없음")
            else:
                inserted_count += len(chunk)
                print(f"✅ {table_name} insert 성공 (chunk {batch_num}/{total_batches}, {len(chunk)} rows)")
        except Exception as e:
            print(f"❌ {table_name} insert 예외 발생 (chunk {batch_num}/{total_batches}): {repr(e)}")
            # 에러 발생 시에도 다음 배치 계속 처리
    
    print(f"✅ {table_name} 총 {inserted_count}/{total}개 레코드 삽입 완료")
    return inserted_count


async def async_chunked_insert(
    supabase: Client,
    table_name: str,
    records: List[Dict[str, Any]],
    chunk_size: int = 500
) -> int:
    """
    비동기 배치 단위로 데이터 삽입
    
    asyncio.gather()를 활용한 병렬 처리 가능
    """
    import asyncio
    
    total = len(records)
    chunks = [records[i:i + chunk_size] for i in range(0, total, chunk_size)]
    
    async def insert_chunk(chunk: List[Dict[str, Any]], chunk_num: int):
        try:
            res = supabase.table(table_name).insert(chunk).execute()
            if res.data:
                print(f"✅ {table_name} chunk {chunk_num} 성공 ({len(chunk)} rows)")
                return len(chunk)
            else:
                print(f"❌ {table_name} chunk {chunk_num} 실패: 응답 없음")
                return 0
        except Exception as e:
            print(f"❌ {table_name} chunk {chunk_num} 예외: {repr(e)}")
            return 0
    
    # 모든 청크를 병렬로 처리
    results = await asyncio.gather(*[insert_chunk(chunk, i+1) for i, chunk in enumerate(chunks)])
    
    total_inserted = sum(results)
    print(f"✅ {table_name} 총 {total_inserted}/{total}개 레코드 삽입 완료")
    return total_inserted

