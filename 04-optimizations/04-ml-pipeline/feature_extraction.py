"""
ML 학습 파이프라인: 피처 엔지니어링

목표: 모델 학습을 위한 자동화된 피처 엔지니어링
"""

from typing import Dict, List, Any
import pandas as pd


def extract_recent_trends(
    user_id: str,
    recent_sessions: List[Dict[str, Any]],
    window_size: int = 5
) -> Dict[str, float]:
    """
    최근 트렌드 추출 (과거 5게임 기록 기반)
    
    Args:
        user_id: 사용자 ID
        recent_sessions: 최근 세션 리스트
        window_size: 분석할 세션 수
        
    Returns:
        트렌드 피처 딕셔너리
    """
    if len(recent_sessions) < window_size:
        window_size = len(recent_sessions)
    
    recent = recent_sessions[-window_size:]
    
    # 평균 완주 순위
    avg_finish_position = sum(s.get('finish_position', 0) for s in recent) / len(recent)
    
    # 사고율
    total_incidents = sum(s.get('incidents', 0) for s in recent)
    avg_incidents_per_race = total_incidents / len(recent)
    
    # DNF율
    dnf_count = sum(1 for s in recent if s.get('dnf', False))
    dnf_rate = dnf_count / len(recent)
    
    # 승률
    win_count = sum(1 for s in recent if s.get('finish_position', 999) == 1)
    win_rate = win_count / len(recent)
    
    # Top 5, Top 10율
    top5_count = sum(1 for s in recent if s.get('finish_position', 999) <= 5)
    top10_count = sum(1 for s in recent if s.get('finish_position', 999) <= 10)
    top5_rate = top5_count / len(recent)
    top10_rate = top10_count / len(recent)
    
    return {
        'recent_avg_finish_position': avg_finish_position,
        'avg_incidents_per_race': avg_incidents_per_race,
        'dnf_rate': dnf_rate,
        'win_rate': win_rate,
        'top5_rate': top5_rate,
        'top10_rate': top10_rate
    }


def calculate_opponent_stats(
    participants: List[Dict[str, Any]],
    user_id: str
) -> Dict[str, float]:
    """
    상대방 iRating 통계 계산
    
    Args:
        participants: 참가자 리스트
        user_id: 사용자 ID
        
    Returns:
        상대방 통계 딕셔너리
    """
    opponent_ratings = [
        p.get('i_rating', 0) 
        for p in participants 
        if p.get('user_id') != user_id
    ]
    
    if not opponent_ratings:
        return {
            'avg_opponent_ir': None,
            'max_opponent_ir': None,
            'min_opponent_ir': None
        }
    
    return {
        'avg_opponent_ir': sum(opponent_ratings) / len(opponent_ratings),
        'max_opponent_ir': max(opponent_ratings),
        'min_opponent_ir': min(opponent_ratings)
    }


def calculate_track_difficulty(
    track_id: int,
    historical_data: List[Dict[str, Any]]
) -> float:
    """
    트랙 난이도 계산 (과거 데이터 기반)
    
    Args:
        track_id: 트랙 ID
        historical_data: 과거 세션 데이터
        
    Returns:
        트랙 난이도 점수
    """
    track_sessions = [s for s in historical_data if s.get('track_id') == track_id]
    
    if not track_sessions:
        return 0.5  # 기본값
    
    # 평균 사고율을 난이도로 사용
    avg_incidents = sum(s.get('incidents', 0) for s in track_sessions) / len(track_sessions)
    difficulty = min(1.0, avg_incidents / 10.0)  # 0.0~1.0 범위로 정규화
    
    return difficulty


def generate_training_features(
    session_data: Dict[str, Any],
    user_history: List[Dict[str, Any]],
    participants: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    ML 학습용 피처 생성
    
    Args:
        session_data: 현재 세션 데이터
        user_history: 사용자 과거 기록
        participants: 참가자 리스트
        
    Returns:
        피처 딕셔너리
    """
    features = {}
    
    # 기본 세션 정보
    features.update({
        'subsession_id': session_data.get('subsession_id'),
        'cust_id': session_data.get('cust_id'),
        'track_id': session_data.get('track_id'),
        'car_id': session_data.get('car_id'),
        'series_id': session_data.get('series_id'),
    })
    
    # 최근 트렌드
    recent_trends = extract_recent_trends(
        session_data.get('cust_id'),
        user_history
    )
    features.update(recent_trends)
    
    # 상대방 통계
    opponent_stats = calculate_opponent_stats(
        participants,
        session_data.get('cust_id')
    )
    features.update(opponent_stats)
    
    # iRating 차이
    user_ir = session_data.get('i_rating', 0)
    avg_opponent_ir = opponent_stats.get('avg_opponent_ir', 0)
    if avg_opponent_ir:
        features['ir_diff_from_avg'] = user_ir - avg_opponent_ir
    
    return features

