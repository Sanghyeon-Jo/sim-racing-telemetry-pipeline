"""
Telemetry Data Parser Service

Pandas 기반 CSV 파싱 및 헤더 자동 탐지
- Time 필드 기반 헤더 위치 자동 탐지
- 단위 변환 (mph → kph, m/s → km/h)
- 필드 정규화 (snake_case)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import io
import csv
from io import StringIO


def deduplicate_columns(columns: List[str]) -> List[str]:
    """컬럼명 중복 제거 및 정규화"""
    seen, out = {}, []
    for c in columns:
        k = c.strip().lower()
        if k in seen:
            seen[k] += 1
            k = f"{k}_{seen[k]}"
        else:
            seen[k] = 0
        out.append(k)
    return out


def _guess_sep(lines: List[str]) -> str:
    """CSV 구분자 자동 탐지"""
    sample = "\n".join(lines[:30])
    try:
        return csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"]).delimiter
    except Exception:
        return ","


def _is_header(tokens: List[str]) -> bool:
    """헤더 행인지 판단 (Time 필드 포함 여부)"""
    toks = [t.strip().lower() for t in tokens]
    return ("time" in toks) and (len(toks) >= 5)


_UNIT_TOKENS = {
    "s", "sec", "second", "seconds", "ms", "millisecond", "milliseconds",
    "km/h", "kph", "kmh", "m/s", "mps", "mph", "mi/h",
    "deg", "deg/s", "%", "no", "1/min", "c", "°c", "mm", "bar", "psi", "g", "m", "n", "kn", "pa", "-", ""
}


def _is_units(tokens: List[str]) -> bool:
    """단위 행인지 판단"""
    toks = [t.strip().lower() for t in tokens]
    if not toks:
        return False
    match = sum(1 for t in toks if t in _UNIT_TOKENS or (t.endswith("/s") and t[:-2] in _UNIT_TOKENS))
    return (match / len(toks)) >= 0.4


def _find_header_unit_idx(lines: List[str], sep: str) -> Tuple[Optional[int], Optional[int]]:
    """
    헤더 및 단위 행 인덱스 찾기
    
    Returns:
        (header_idx, unit_idx or None)
    """
    start, end = 0, min(len(lines) - 1, 80)
    for i in range(start, end):
        toks = lines[i].rstrip("\n").split(sep)
        if _is_header(toks):
            # 바로 다음 줄이 유닛이면 unit_idx=i+1
            if i + 1 < len(lines):
                toks2 = lines[i + 1].rstrip("\n").split(sep)
                if _is_units(toks2):
                    return i, i + 1
            return i, None
    return None, None


def _normalize_unit(u: str) -> Optional[str]:
    """단위 정규화"""
    if not u:
        return None
    u = u.strip().lower()
    if u in {"km/h", "kph", "kmh"}:
        return "km/h"
    if u in {"m/s", "mps"}:
        return "m/s"
    if u in {"mph", "mi/h"}:
        return "mph"
    if u in {"s", "sec", "second", "seconds"}:
        return "s"
    if u in {"ms", "millisecond", "milliseconds"}:
        return "ms"
    return u


class TelemetryParser:
    """
    텔레메트리 로그 파일 파서
    
    주요 기능:
    - 헤더 자동 탐지 (Time 필드 기반)
    - 단위 변환 (mph → kph, m/s → km/h)
    - 필드 정규화 (snake_case)
    """
    
    def __init__(self):
        """Initialize the parser with default settings."""
        self.chunk_size = 10000
    
    def parse_csv(
        self, 
        content: bytes, 
        encoding: str = 'utf-8'
    ) -> pd.DataFrame:
        """
        CSV 텔레메트리 로그 파일 파싱
        
        Args:
            content: Raw file content as bytes
            encoding: File encoding (default: utf-8)
            
        Returns:
            pd.DataFrame: Parsed and cleaned telemetry data
            
        Raises:
            ValueError: If CSV format is invalid
        """
        try:
            # 텍스트로 변환
            text = content.decode(encoding, errors="ignore")
            lines = text.splitlines()
            
            if not lines:
                raise ValueError("CSV 파일이 비어있습니다")
            
            # 1) 구분자/헤더/유닛 탐지
            sep = _guess_sep(lines)
            header_idx, unit_idx = _find_header_unit_idx(lines, sep)
            
            if header_idx is None:
                raise ValueError("헤더 행(Time, Speed 등)을 찾지 못했습니다. CSV 포맷을 확인하세요.")
            
            header_line = lines[header_idx].strip()
            unit_line = lines[unit_idx].strip() if unit_idx is not None else ""
            
            header_cols_raw = [c.strip().lower() for c in header_line.split(sep)]
            header_cols_norm = deduplicate_columns(header_cols_raw)
            
            unit_vals_raw = [u.strip().lower() for u in unit_line.split(sep)] if unit_line else []
            unit_map_raw = dict(zip(header_cols_norm, unit_vals_raw))
            unit_map = {k: _normalize_unit(v) for k, v in unit_map_raw.items()}
            
            # 2) 실제 데이터 로드 (헤더부터 읽고, 단위 행은 skip)
            start_from_header = "\n".join(lines[header_idx:])
            skiprows_rel = [1] if unit_idx == header_idx + 1 else None
            
            read_csv_kwargs = dict(sep=sep, header=0, on_bad_lines="skip", skiprows=skiprows_rel)
            
            try:
                df = pd.read_csv(StringIO(start_from_header), engine="c", low_memory=False, **read_csv_kwargs)
            except Exception:
                df = pd.read_csv(StringIO(start_from_header), engine="python", **read_csv_kwargs)
            
            # 컬럼 정규화
            df.columns = deduplicate_columns([c.strip().lower() for c in df.columns])
            
            # 3) 시간 컬럼 자동 탐지/리네임(+ms→s)
            time_col = next((c for c in df.columns if c.startswith("time")), None)
            if time_col is None and "timestamp" in df.columns:
                time_col = "timestamp"
            if time_col is None:
                # 유닛으로 추정
                cand = [c for c, u in unit_map.items() if c in df.columns and u in ("s", "ms")]
                time_col = cand[0] if cand else None
            if time_col is None:
                raise ValueError("'time' 열이 없음 (time/time(s)/timestamp를 찾지 못함)")
            
            if time_col != "time":
                df.rename(columns={time_col: "time"}, inplace=True)
            
            time_unit = (unit_map.get(time_col) or "").lower()
            if time_unit in ("ms",):
                df["time"] = pd.to_numeric(df["time"], errors="coerce") / 1000.0
            
            # 4) 단위 기반 수치 변환 (숫자만 추출 → 숫자화 → 유닛 변환)
            for col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(r"[^0-9\.\-eE+]", "", regex=True)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")
                u = unit_map.get(col)
                if u == "m/s":
                    df[col] = df[col] * 3.6  # m/s → km/h
                elif u == "mph":
                    df[col] = df[col] * 1.60934  # mph → km/h
            
            # 5) 결측/보조열 정리
            df = df.dropna(subset=["time"])  # time 없는 행 제거
            df = df.dropna()  # 나머지 결측 제거
            
            # 6) 데이터 타입 최적화
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame 정제
        
        - 중복 행 제거
        - 결측값 처리
        - 데이터 타입 최적화
        """
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values in numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Optimize data types to reduce memory usage
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df

