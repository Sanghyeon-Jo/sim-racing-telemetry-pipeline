"""
비정형 데이터 표준화: 단위 변환

문제: mph, kph, m/s 등 다양한 단위 혼재
해결: 단위 자동 인식 및 통일된 단위(km/h)로 변환
"""

import pandas as pd
from typing import Dict, Optional


def normalize_unit(unit: str) -> Optional[str]:
    """단위 정규화"""
    if not unit:
        return None
    u = unit.strip().lower()
    
    # 속도 단위
    if u in {"km/h", "kph", "kmh"}:
        return "km/h"
    if u in {"m/s", "mps"}:
        return "m/s"
    if u in {"mph", "mi/h"}:
        return "mph"
    
    # 시간 단위
    if u in {"s", "sec", "second", "seconds"}:
        return "s"
    if u in {"ms", "millisecond", "milliseconds"}:
        return "ms"
    
    return u


def convert_speed_to_kmh(df: pd.DataFrame, col: str, from_unit: str) -> pd.DataFrame:
    """
    속도 단위를 km/h로 변환
    
    Args:
        df: DataFrame
        col: 변환할 컬럼명
        from_unit: 원본 단위 (m/s, mph 등)
        
    Returns:
        변환된 DataFrame
    """
    if col not in df.columns:
        return df
    
    from_unit = normalize_unit(from_unit)
    
    if from_unit == "m/s":
        df[col] = df[col] * 3.6  # m/s → km/h
    elif from_unit == "mph":
        df[col] = df[col] * 1.60934  # mph → km/h
    # km/h는 그대로
    
    return df


def convert_time_to_seconds(df: pd.DataFrame, col: str, from_unit: str) -> pd.DataFrame:
    """
    시간 단위를 초(seconds)로 변환
    
    Args:
        df: DataFrame
        col: 변환할 컬럼명
        from_unit: 원본 단위 (ms 등)
        
    Returns:
        변환된 DataFrame
    """
    if col not in df.columns:
        return df
    
    from_unit = normalize_unit(from_unit)
    
    if from_unit == "ms":
        df[col] = df[col] / 1000.0  # ms → s
    
    return df


def apply_unit_conversions(df: pd.DataFrame, unit_map: Dict[str, str]) -> pd.DataFrame:
    """
    단위 맵을 기반으로 모든 컬럼에 단위 변환 적용
    
    Args:
        df: DataFrame
        unit_map: 컬럼명 -> 단위 매핑 딕셔너리
        
    Returns:
        변환된 DataFrame
    """
    for col, unit in unit_map.items():
        if col not in df.columns:
            continue
        
        unit = normalize_unit(unit)
        
        # 속도 관련 컬럼 (speed, velocity 등)
        if any(keyword in col.lower() for keyword in ['speed', 'velocity', 'vel']):
            df = convert_speed_to_kmh(df, col, unit)
        
        # 시간 관련 컬럼
        elif 'time' in col.lower():
            df = convert_time_to_seconds(df, col, unit)
    
    return df

