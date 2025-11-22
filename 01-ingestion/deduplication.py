"""
중복 제거 모듈

- 세션 레벨: SHA-256 해시 기반 중복 검사
- 샘플 레벨: session_id + elapsed_time 복합키 기반 중복 방지
"""

import hashlib
import pandas as pd
from typing import Optional


def generate_session_hash(df: pd.DataFrame) -> str:
    """
    세션 데이터의 SHA-256 해시 생성
    
    Args:
        df: 텔레메트리 DataFrame
        
    Returns:
        SHA-256 해시 문자열
    """
    # CSV 형식으로 변환 후 해시 생성
    data_str = df.to_csv(index=False)
    return hashlib.sha256(data_str.encode()).hexdigest()


def check_duplicate_by_hash(hash_value: str, existing_hashes: list) -> bool:
    """
    해시 기반 중복 검사
    
    Args:
        hash_value: 검사할 해시 값
        existing_hashes: 기존 해시 리스트
        
    Returns:
        중복 여부 (True: 중복, False: 신규)
    """
    return hash_value in existing_hashes


def check_duplicate_by_composite_key(
    session_id: str,
    elapsed_time: float,
    existing_keys: set
) -> bool:
    """
    복합키 기반 중복 검사 (session_id + elapsed_time)
    
    Args:
        session_id: 세션 ID
        elapsed_time: 경과 시간
        existing_keys: 기존 복합키 세트 (튜플의 세트)
        
    Returns:
        중복 여부 (True: 중복, False: 신규)
    """
    composite_key = (session_id, elapsed_time)
    return composite_key in existing_keys

