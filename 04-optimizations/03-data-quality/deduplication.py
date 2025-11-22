"""
데이터 품질 및 무결성: 중복 제거

문제: 동일한 세션/샘플 데이터의 중복 저장
해결:
- 세션 레벨: SHA-256 해시 기반 중복 검사
- 샘플 레벨: session_id + elapsed_time 복합키로 중복 방지
"""

import hashlib
import pandas as pd
from typing import Set, Tuple, Optional


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


def check_session_duplicate(
    hash_value: str,
    existing_hashes: Set[str]
) -> bool:
    """
    세션 레벨 중복 검사 (SHA-256 해시 기반)
    
    Args:
        hash_value: 검사할 해시 값
        existing_hashes: 기존 해시 세트
        
    Returns:
        중복 여부 (True: 중복, False: 신규)
    """
    return hash_value in existing_hashes


def check_sample_duplicate(
    session_id: str,
    elapsed_time: float,
    existing_keys: Set[Tuple[str, float]]
) -> bool:
    """
    샘플 레벨 중복 검사 (session_id + elapsed_time 복합키)
    
    Args:
        session_id: 세션 ID
        elapsed_time: 경과 시간
        existing_keys: 기존 복합키 세트
        
    Returns:
        중복 여부 (True: 중복, False: 신규)
    """
    composite_key = (session_id, elapsed_time)
    return composite_key in existing_keys


def remove_duplicate_samples(
    df: pd.DataFrame,
    session_id_col: str = 'session_id',
    time_col: str = 'elapsed_time'
) -> pd.DataFrame:
    """
    DataFrame에서 중복 샘플 제거 (복합키 기반)
    
    Args:
        df: 입력 DataFrame
        session_id_col: 세션 ID 컬럼명
        time_col: 시간 컬럼명
        
    Returns:
        중복 제거된 DataFrame
    """
    if session_id_col not in df.columns or time_col not in df.columns:
        return df
    
    # 복합키 기반 중복 제거
    df = df.drop_duplicates(subset=[session_id_col, time_col], keep='first')
    
    return df

