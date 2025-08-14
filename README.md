# RAG 기반 인재 추론 시스템

## 📋 프로젝트 개요

인재의 경력 정보(회사, 직무, 재직 기간)를 기반으로 LLM을 활용하여 경험 태그와 역량을 추론하는 RAG(Retrieval-Augmented Generation) 시스템.

### 🎯 핵심 기능
- **인재 프로필 분석**: JSON 형태의 인재 데이터를 입력받아 경험 태그 추론
- **회사 정보/지표 검색**: 재직기간 동안의 회사 정보 및 지표 조회
- **벡터 검색**: pgvector를 활용한 회사 정보 및 뉴스 데이터 유사도 검색
- **LLM 기반 추론**: OpenAI GPT 모델을 사용한 컨텍스트 기반 경험 추론
- **Redis 캐싱**: SHA256 기반 캐시 키를 사용한 추론 결과 캐싱
- **RESTful API**: FastAPI 기반 비동기 API 서버

## 🛠 기술 스택

### 백엔드 프레임워크
- **FastAPI**: 비동기 웹 프레임워크
- **Python 3.13+**: 최신 Python 버전
- **SQLAlchemy**: ORM 및 데이터베이스 추상화
- **Alembic**: 데이터베이스 마이그레이션

### 데이터베이스 및 캐싱
- **PostgreSQL + pgvector**: 벡터 유사도 검색 지원
- **Redis**: 추론 결과 캐싱
- **OpenAI Embeddings**: 텍스트 벡터화

### 아키텍처 패턴
- **DIP**
- **Domain-Driven Design**: 도메인 중심 설계
- **Dependency Injection**: 의존성 주입 컨테이너 사용

### 개발 도구
- **Poetry**: 패키지 관리
- **Docker Compose**: 컨테이너 오케스트레이션
- **pytest**: 테스트 프레임워크
- **Black, Ruff, isort**: 코드 포맷팅 및 린팅

## 🚀 설치 및 실행 방법

### 1. 사전 요구사항
```bash
# Python 3.13+ 설치
# Poetry 설치
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 프로젝트 설정
```bash
# 프로젝트 클론
git clone <repository-url>
cd AI-technical-assignment

# 의존성 설치
poetry install

# 가상환경 활성화
poetry shell (plugin 필요)
```

### 3. 환경 변수 설정
```bash
# .env 파일 생성
cp ./.env-example .env
cp .env-migrations-example .env-migrations

# 환경 변수 수정
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 서비스 실행
```bash
# Docker Compose로 pg 컨테이너 실행
docker-compose up -d postgres

# 데이터베이스 마이그레이션
alembic upgrade head

# 셈플 데이터
python -m tools.init_data

# 개발 서버 실행
docker-compose up -d
```

## 📡 API 사용법

### 메인 API 엔드포인트

#### 인재 경험 추론 API
```bash
POST /api/v1/inferences/talent-profile-analyses
Content-Type: multipart/form-data

```
#### 회사 정보 저장 API
```bash
POST /api/v1/enrichments/data-sources
```

#### 헬스 체크
```bash
GET /health
```

### 입력 파일 형식
```json
{
  "firstName": "홍길동",
  "lastName": "",
  "headline": "Software Engineer",
  "summary": "경험 많은 소프트웨어 엔지니어",
  "positions": [
    {
      "companyName": "토스",
      "title": "Senior Software Engineer",
      "description": "결제 시스템 개발",
      "startEndDate": {
        "start": {"year": 2020, "month": 3},
        "end": {"year": 2023, "month": 6}
      }
    }
  ],
  "educations": [
    {
      "schoolName": "서울대학교",
      "degree": "학사",
      "fieldOfStudy": "컴퓨터공학"
    }
  ]
}
```

### 응답 데이터 형식
```json
{
  "experience_tags": [
    "성장기스타트업 경험",
    "리더십",
    "핀테크 도메인 경험"
  ],
  "competency_tags": [
    "백엔드 개발",
    "결제 시스템",
    "대규모 서비스"
  ],
  "inferences": [
    {"tag": "성장기스타트업경험", "inference": "},
    {"tag": "성장기스타트업경험", "inference": "},
    {"tag": "성장기스타트업경험", "inference": "},
  ]
}
```

## 🏗 프로젝트 구조

```
src/
├── config/                    # 설정 파일
│   └── config.py              # 환경 변수 및 설정 관리
├── containers.py              # DI 컨테이너 설정
├── server.py                  # FastAPI 애플리케이션 진입점
├── shared/                    # 공통 모듈
│   ├── cache/                 # 캐싱 관련
│   │   ├── cache_port.py      # 캐시 포트 (인터페이스)
│   │   └── redis_cache_adapter.py  # Redis 캐시 구현체
│   └── exceptions.py          # 공통 예외 처리
├── enrichment/                # 데이터 도메인
│   ├── domain/                # 도메인 계층
│   │   ├── aggregates/        # 애그리게이트
│   │   ├── entities/          # 엔티티
│   │   ├── repositories/      # 리포지토리 포트
│   │   └── vos/               # 값 객체
│   ├── application/           # 애플리케이션 계층
│   │   ├── services/          # 애플리케이션 서비스
│   │   └── ports/             # 외부 의존성 포트
│   ├── infrastructure/        # 인프라스트럭처 계층
│   │   ├── repositories/      # 리포지토리 구현체
│   │   ├── readers/           # 데이터 리더
│   │   ├── orm/               # ORM 모델
│   │   └── embeddings/        # 임베딩(openai) 클라이언트 
│   └── controllers/           # 컨트롤러 계층
└── inference/                 # 추론 도메인
    ├── domain/                # 도메인 계층
    │   ├── aggregates/        # 애그리게이트
    │   ├── entities/          # 회사, 뉴스 엔티티
    │   ├── services/          # 도메인 서비스
    │   └── vos/               # 값 객체
    ├── application/           # 애플리케이션 계층
    │   ├── services/          # TalentInference 서비스
    │   └── templates/         # 프롬프트 템플릿
    ├── infrastructure/        # 인프라스트럭처 계층
    │   └── adapters/          # 외부 서비스 어댑터
    └── controllers/           # API 컨트롤러
```
## 🔄 시스템 플로우

### 1. 전체 추론 프로세스
```mermaid
flowchart TD
    A[JSON 파일 업로드] --> B[TalentProfile 파싱]
    B --> C[캐시 키 생성 SHA256]
    C --> D{캐시 히트?}
    D -->|Yes| E[캐시된 결과 반환]
    D -->|No| F[회사 정보 검색]
    F --> G[뉴스 데이터 벡터 검색]
    G --> H[도메인 서비스로 컨텍스트 집계]
    H --> I[LLM 프롬프트 생성]
    I --> J[OpenAI GPT 추론]
    J --> K[결과 파싱 및 검증]
    K --> L[Redis 캐싱]
    L --> M[JSON 응답 반환]
```

### 2. 벡터 검색 프로세스
```mermaid
flowchart TD
    A[검색 쿼리] --> B[OpenAI Embeddings]
    B --> C[벡터 생성]
    C --> D[pgvector 유사도 검색]
    D --> E[상위 N개 결과 반환]
    E --> F[컨텍스트 집계]
```

## 🧪 테스트

### 테스트 실행
```bash
# 모든 테스트 실행
pytest tests
```
