-- PostgreSQL 스키마 설계 (3NF 기반)
-- 텔레메트리 및 세션 데이터 저장을 위한 정규화된 스키마

-- 세션 메타데이터 테이블
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name VARCHAR(255),
    track_name VARCHAR(255),
    car_name VARCHAR(255),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash VARCHAR(64) UNIQUE,  -- SHA-256 해시 (중복 검사용)
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_hash (hash)
);

-- 텔레메트리 샘플 테이블
CREATE TABLE IF NOT EXISTS telemetry_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    elapsed_time DECIMAL(10, 3) NOT NULL,
    
    -- 제어 입력 (0.0~1.0 범위)
    throttle_position DECIMAL(3, 2) CHECK (throttle_position >= 0.0 AND throttle_position <= 1.0),
    brake_position DECIMAL(3, 2) CHECK (brake_position >= 0.0 AND brake_position <= 1.0),
    steering_angle DECIMAL(6, 3),
    clutch_position DECIMAL(3, 2) CHECK (clutch_position >= 0.0 AND clutch_position <= 1.0),
    
    -- 차량 상태
    speed_ms DECIMAL(6, 3),
    speed_kmh DECIMAL(6, 3),
    rpm INTEGER,
    gear INTEGER,
    engine_power DECIMAL(8, 2),
    engine_torque DECIMAL(8, 2),
    
    -- 위치 정보
    position_x DECIMAL(10, 3),
    position_y DECIMAL(10, 3),
    position_z DECIMAL(10, 3),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(11, 7),
    heading DECIMAL(6, 3),
    distance_lap DECIMAL(10, 3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    UNIQUE (session_id, elapsed_time),  -- 복합키로 중복 방지
    INDEX idx_telemetry_session_id (session_id),
    INDEX idx_telemetry_elapsed_time (elapsed_time)
);

-- ML 학습 데이터 테이블
CREATE TABLE IF NOT EXISTS ml_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subsession_id INTEGER NOT NULL,
    cust_id INTEGER NOT NULL,
    
    -- iRating 관련
    i_rating INTEGER,
    sof INTEGER,
    avg_opponent_ir INTEGER,
    max_opponent_ir INTEGER,
    min_opponent_ir INTEGER,
    ir_diff_from_avg INTEGER,
    
    -- Safety Rating 관련
    safety_rating DECIMAL(4, 2),
    avg_incidents_per_race DECIMAL(4, 2),
    dnf_rate DECIMAL(4, 3),
    
    -- 성과 지표
    recent_avg_finish_position DECIMAL(4, 2),
    win_rate DECIMAL(4, 3),
    top5_rate DECIMAL(4, 3),
    top10_rate DECIMAL(4, 3),
    ir_trend DECIMAL(6, 3),
    sr_trend DECIMAL(6, 3),
    
    -- 세션 정보
    track_id INTEGER,
    car_id INTEGER,
    series_id INTEGER,
    starting_position INTEGER,
    actual_finish_position INTEGER,
    actual_incidents INTEGER,
    total_participants INTEGER,
    actual_dnf BOOLEAN,
    
    -- 날씨 정보
    weather_temp DECIMAL(5, 2),
    track_temp DECIMAL(5, 2),
    relative_humidity DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    
    session_start_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (subsession_id, cust_id),  -- 복합키로 중복 방지
    INDEX idx_ml_training_subsession (subsession_id),
    INDEX idx_ml_training_cust (cust_id)
);

-- 파티셔닝 예시 (세션 생성 날짜 기준)
-- CREATE TABLE telemetry_samples_2025_01 PARTITION OF telemetry_samples
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

