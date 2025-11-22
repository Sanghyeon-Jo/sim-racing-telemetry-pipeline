"""
필드 정규화 및 단위 변환 모듈

- 필드명 snake_case 변환
- 단위 변환 (mph → kph, m/s → km/h)
"""

import re
import pandas as pd
from typing import Dict, Optional


def to_snake_case(name: str) -> str:
    """필드명을 snake_case로 변환"""
    # 대문자를 소문자로, 공백/특수문자를 언더스코어로
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower().replace(' ', '_').replace('-', '_')


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame의 모든 컬럼명을 snake_case로 변환"""
    df.columns = [to_snake_case(col) for col in df.columns]
    return df


def convert_units(df: pd.DataFrame, unit_map: Dict[str, str]) -> pd.DataFrame:
    """
    단위 변환 수행
    
    Args:
        df: 입력 DataFrame
        unit_map: 컬럼명 -> 단위 매핑 딕셔너리
        
    Returns:
        변환된 DataFrame
    """
    for col, unit in unit_map.items():
        if col not in df.columns:
            continue
            
        unit = unit.lower().strip()
        
        # m/s → km/h
        if unit in {"m/s", "mps"}:
            df[col] = df[col] * 3.6
            
        # mph → km/h
        elif unit in {"mph", "mi/h"}:
            df[col] = df[col] * 1.60934
            
        # ms → s
        elif unit in {"ms", "millisecond", "milliseconds"}:
            df[col] = df[col] / 1000.0
    
    return df

