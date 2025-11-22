# 대용량 가상 차량 데이터 ETL 파이프라인 구축

> Sim Racing Telemetry Data Pipeline - End-to-End ETL Pipeline

**기간**: 2025.07 ~ 2025.11  
**수행**: 개인 프로젝트  
**기술**: Python(Asyncio), FastAPI, PostgreSQL, GCP(Cloud Run)

---

## 📋 프로젝트 개요

iRacing/MoTeC/ACC에서 추출된 텔레메트리 로그를 **수집**, **정제**, **저장**, **서빙**하는 End-to-End 데이터 파이프라인입니다.

### 목적
- End-to-End 파이프라인 구축 및 서비스 안정성 확보
- 대용량 ETL 안정성 확보 (Async/Batch) 및 DB 스키마 최적화

### 기여
- 대용량 ETL 안정성 확보 (Async/Batch)
- DB 스키마 최적화 (3NF 기반 설계)
- 비정형 데이터 자동 표준화 (파싱 성공률 95% 이상)
- 데이터 품질 및 무결성 보장 (중복 레코드 0건)

---

## ⚙️ End-to-End 파이프라인

### Stage 1: Ingestion (데이터 수집 및 표준화)
- **Pandas 기반 대용량 CSV 파싱 및 헤더 자동 탐지**
- FastAPI (Async Worker)
- 필드 정규화 (Snake_case)
- 단위 변환 (mph → kph)
- 중복 제거 & 타입 캐스팅

**구현**: `01-ingestion/`

### Stage 2: Storage (고성능 저장소 구축)
- **Bulk Insert 및 3NF 기반 스키마 설계로 대용량 데이터 적재 최적화**
- PostgreSQL
- 관계형 스키마 (3NF)
- Telemetry & Session Tables
- 파티셔닝 & 인덱싱
- 데이터 무결성 (Foreign Keys)

**구현**: `02-storage/`

### Stage 3: Serving (데이터 활용 및 성과)
- **ML Feature 추출 및 대시보드 연동으로 수기 분석 시간 획기적 단축 달성**
- Application Service
- Real-time Dashboard (Next.js)
- ML Training Data Export
- Driving Analysis Report

**구현**: `03-serving/`

---

## 🎯 난제 해결 및 최적화 전략

### 1. 비정형 데이터 표준화
**문제**: MoTeC, iRacing 등 다양한 소스의 CSV 헤더 위치 및 단위 불일치  
**해결**:
- **Auto-Parsing**: Pandas로 'Time' 필드 탐지하여 헤더 위치 자동 인식
- **Field Mapping**: 필드 매핑 정규화 및 단위 자동 변환 로직 구현

**결과**: 파싱 성공률 **95% 이상** 달성, 수동 전처리 작업 **100% 제거**

**구현**: `04-optimizations/01-data-standardization/`

### 2. 대용량 배치 처리 최적화
**문제**: 수천 개 세션 데이터 처리 시 API 병목 및 메모리 부족  
**해결**:
- **Bulk Processing**: 단일 레코드 처리 → 500개씩 배치 삽입으로 전환
- **Async IO**: `asyncio.gather()`로 세션별 피처 추출 병렬 처리
- **Rate Limiting**: IP 기반 요청 제한으로 API 안정성 확보

**결과**: 500개 세션 처리 시간 **30분 이내** 달성 (세션당 약 3.6초)

**구현**: `04-optimizations/02-batch-processing/`

### 3. 데이터 품질 및 무결성
**문제**: 센서 값 범위 초과 및 중복 데이터 유입  
**해결**:
- **Validation**: `clamp` 함수로 센서 값 범위 강제 (0.0~1.0, DECIMAL 정밀도)
- **Deduplication**:
  - 세션 레벨: SHA-256 해시 값 비교로 중복 파일 업로드 방지
  - 샘플 레벨: `session_id + elapsed_time` 복합키로 중복 레코드 방지

**결과**: 데이터 일관성 **100%**, 중복 레코드 **0건**

**구현**: `04-optimizations/03-data-quality/`

### 4. ML 학습 파이프라인
**목표**: 모델 학습을 위한 자동화된 피처 엔지니어링  
**파이프라인**:
1. **Extraction**: 과거 5게임 기록 기반 "최근 트렌드" 추출 (랭크, 사고율)
2. **Calculation**: "상대방 iRating" 및 트랙 난이도 자동 계산
3. **Generation**: 처리된 데이터를 학습 데이터 테이블(`ml_training_data`)에 자동 로드

**가치**: "Clean Data" 환경 제공으로 개발자는 모델링에만 집중 가능

**구현**: `04-optimizations/04-ml-pipeline/`

---

## 🚀 빠른 시작

### 요구사항
- Python 3.11+
- PostgreSQL (또는 Supabase)
- FastAPI, Pandas, NumPy

### 설치 및 실행

```bash
# 저장소 클론
git clone <repository-url>
cd simracing-telemetry-pipline

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 Supabase 연결 정보 입력

# API 서버 실행
uvicorn app.main:app --reload
```

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📡 API 엔드포인트

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `POST` | `/api/v1/upload` | CSV/GPX 파일 업로드 → 파싱된 telemetry JSON 반환 |
| `POST` | `/api/v1/collect/training-data` | 정제된 세션 피처를 Supabase 테이블에 업서트 (중복 키: `subsession_id,cust_id`) |
| `GET` | `/health` | 서비스 헬스 체크 |

---

## 📁 폴더 구조

```
simracing-telemetry-pipline/
├── 01-ingestion/              # Stage 1: 데이터 수집 및 표준화
│   ├── parser.py              # Pandas 기반 CSV 파서 (헤더 자동 탐지)
│   ├── normalization.py       # 필드 정규화 (snake_case, 단위 변환)
│   └── deduplication.py      # 중복 제거 로직
│
├── 02-storage/                # Stage 2: 고성능 저장소 구축
│   ├── schema.sql             # PostgreSQL 스키마 (3NF 설계)
│   ├── batch_insert.py        # Bulk Insert 최적화 코드
│   └── indexing_strategy.sql  # 인덱싱 전략
│
├── 03-serving/                # Stage 3: 데이터 활용 및 서빙
│   └── api/
│       ├── main.py            # FastAPI 앱 엔트리포인트
│       └── endpoints/
│           ├── upload.py      # 파일 업로드 API
│           └── training_data.py  # ML 학습 데이터 API
│
├── 04-optimizations/           # 최적화 전략 구현
│   ├── 01-data-standardization/  # 비정형 데이터 표준화
│   ├── 02-batch-processing/      # 대용량 배치 처리 최적화
│   ├── 03-data-quality/          # 데이터 품질 및 무결성
│   └── 04-ml-pipeline/           # ML 학습 파이프라인
│
├── data/                       # 샘플 데이터
│   └── sample_session.csv
│
├── docs/                       # 문서
│   ├── architecture.md         # 아키텍처 다이어그램 설명
│   └── optimization_strategies.md  # 최적화 전략 상세 설명
│
└── README.md                   # 이 파일
```

---

## 🛠️ 기술 스택

- **FastAPI + Uvicorn**: 비동기 API 서버
- **Pandas / NumPy**: 벡터화 파싱 및 단위 변환
- **Pydantic**: 요청/응답 스키마 검증
- **PostgreSQL (Supabase)**: 저장 및 중복 방지 업서트
- **Asyncio**: 비동기 배치 처리
- **GCP Cloud Run**: 서버리스 배포

---

## 📊 성과 지표

- **파싱 성공률**: 95% 이상
- **처리 성능**: 500개 세션 30분 이내 (세션당 약 3.6초)
- **데이터 일관성**: 100% (중복 레코드 0건)
- **수동 전처리 제거**: 100%

---

## 📌 향후 확장 아이디어

- Supabase를 대신해 Kafka → Snowflake 파이프라인으로 확장
- `POST /api/v1/upload` 단계에서 바로 배치 저장을 수행하여 실시간 피처 뷰 생성
- ML 추론 엔드포인트(예: 랭킹 예측) 추가

---

**Note**: 이 저장소는 데이터 엔지니어 포트폴리오 제출용으로 정리된 스냅샷입니다. 코드와 샘플은 핵심 파이프라인을 설명하기 위한 용도로만 사용됩니다.

