"""
비정형 데이터 표준화: 헤더 자동 탐지

문제: MoTeC, iRacing, ACC 등 다양한 소스의 CSV 헤더 위치가 일정하지 않음
해결: Time 필드를 기반으로 헤더 위치 자동 탐지
"""

import csv
from typing import List, Optional, Tuple


def find_header_by_time_field(lines: List[str], max_lines: int = 100) -> Optional[int]:
    """
    Time 필드를 기반으로 헤더 행 찾기
    
    Args:
        lines: CSV 파일의 라인 리스트
        max_lines: 탐색할 최대 라인 수
        
    Returns:
        헤더 행 인덱스 (없으면 None)
    """
    time_variations = [
        'time', 'elapsed_time', 'timestamp', 'elapsed', 
        'sessiontime', 'session time', 'time(s)', 'time (s)'
    ]
    
    for i, line in enumerate(lines[:max_lines]):
        if not line.strip():
            continue
        
        # 쉼표로 분리
        parts = [p.strip().strip('"\'') for p in line.split(',')]
        cleaned_parts = [p.lower().split('(')[0].strip() for p in parts]  # 단위 제거
        
        # Time 필드가 있고, 충분한 컬럼 수가 있으면 헤더로 판단
        has_time = any(variation in cleaned_parts for variation in time_variations)
        if has_time and len(parts) > 3:
            return i
    
    return None


def find_header_by_field_count(lines: List[str], min_fields: int = 10) -> Optional[int]:
    """
    필드 개수를 기반으로 헤더 행 찾기 (대안 방법)
    
    많은 필드를 가진 첫 번째 비숫자 행을 헤더로 판단
    """
    for i, line in enumerate(lines[:100]):
        if not line.strip():
            continue
        
        parts = [p.strip().strip('"\'') for p in line.split(',')]
        first_field = parts[0] if parts else ""
        
        # 숫자로 시작하면 데이터 행
        try:
            float(first_field)
            continue
        except ValueError:
            # 비숫자이고 충분한 필드가 있으면 헤더로 판단
            if len(parts) >= min_fields:
                return i
    
    return None


def detect_header_and_unit(lines: List[str], sep: str = ',') -> Tuple[Optional[int], Optional[int]]:
    """
    헤더 및 단위 행 인덱스 찾기
    
    Returns:
        (header_idx, unit_idx or None)
    """
    # 먼저 Time 필드 기반으로 찾기
    header_idx = find_header_by_time_field(lines)
    
    if header_idx is None:
        # 대안: 필드 개수 기반
        header_idx = find_header_by_field_count(lines)
    
    if header_idx is None:
        return None, None
    
    # 단위 행 체크 (헤더 다음 줄)
    unit_idx = None
    if header_idx + 1 < len(lines):
        next_line = lines[header_idx + 1].strip()
        if next_line:
            next_parts = [p.strip().strip('"\'') for p in next_line.split(sep)]
            # 단위 행인지 체크 (모두 짧은 텍스트이고 숫자가 아님)
            is_unit_row = all(
                len(p) < 10 and not p.replace('.', '').replace('-', '').isdigit()
                for p in next_parts
            )
            if is_unit_row and len(next_parts) == len(lines[header_idx].split(sep)):
                unit_idx = header_idx + 1
    
    return header_idx, unit_idx

