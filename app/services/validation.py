"""
데이터 품질 및 무결성: 값 범위 검증

문제: 센서 값이 범위를 벗어나는 경우 발생
해결: clamp 함수로 값 범위 강제 (0.0~1.0, DECIMAL 범위 등)
"""

import pandas as pd
from typing import Optional, Union


def clamp_01(value: Union[float, int, None]) -> Optional[float]:
    """
    0.0~1.0 범위로 클리핑 (throttle, brake, clutch 등)
    
    Args:
        value: 입력 값
        
    Returns:
        클리핑된 값 (None이면 None 반환)
    """
    if value is None or pd.isna(value):
        return None
    if value > 1.0:
        return 1.0
    if value < 0.0:
        return 0.0
    return float(value)


def clamp_decimal53(value: Union[float, int, None]) -> Optional[float]:
    """
    DECIMAL(5,3) 범위로 클리핑 (±99.999)
    
    Args:
        value: 입력 값
        
    Returns:
        클리핑된 값
    """
    if value is None or pd.isna(value):
        return None
    if value > 99.999:
        return 99.999
    if value < -99.999:
        return -99.999
    return float(value)


def clamp_decimal63(value: Union[float, int, None]) -> Optional[float]:
    """
    DECIMAL(6,3) 범위로 클리핑 (±999.999)
    
    Args:
        value: 입력 값
        
    Returns:
        클리핑된 값
    """
    if value is None or pd.isna(value):
        return None
    if value > 999.999:
        return 999.999
    if value < -999.999:
        return -999.999
    return float(value)


def validate_sensor_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame의 센서 값들을 검증 및 클리핑
    
    Args:
        df: 입력 DataFrame
        
    Returns:
        검증된 DataFrame
    """
    # 0.0~1.0 범위 컬럼들
    clamp_01_columns = ['throttle', 'brake', 'clutch', 'throttle_position', 
                       'brake_position', 'clutch_position']
    
    for col in clamp_01_columns:
        if col in df.columns:
            df[col] = df[col].apply(clamp_01)
    
    # DECIMAL(6,3) 범위 컬럼들 (타이어 압력 등)
    clamp_63_columns = ['tire_pressure_fl', 'tire_pressure_fr', 
                       'tire_pressure_rl', 'tire_pressure_rr']
    
    for col in clamp_63_columns:
        if col in df.columns:
            df[col] = df[col].apply(clamp_decimal63)
    
    return df

