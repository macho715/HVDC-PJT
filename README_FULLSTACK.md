# 🚀 HVDC Project Full Stack System

삼성물산 HVDC 프로젝트를 위한 완전한 Full Stack 물류 시스템입니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   React App     │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ant Design    │    │   Redis Cache   │    │   Celery        │
│   UI Components │    │   Port: 6379    │    │   Background    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 주요 기능

### 🔌 백엔드 API (FastAPI)
- **창고 관리**: 창고 데이터 CRUD, 용량 모니터링
- **컨테이너 관리**: 적재 최적화, 압력 한계 검증 (4t/m²)
- **송장 처리**: OCR 기반 HS코드 추출, FANR/MOIAT 규정 준수
- **KPI 모니터링**: 실시간 성과 지표 추적
- **모드 전환**: PRIME/ORACLE/LATTICE/RHYTHM/COST-GUARD/ZERO

### 🌐 프론트엔드 (React + Ant Design)
- **대시보드**: 실시간 KPI 및 시스템 상태 모니터링
- **창고 관리**: 창고 정보 CRUD, 구역별 관리
- **컨테이너 관리**: 적재 상태, 압력 모니터링
- **송장 관리**: OCR 결과, HS코드 검증
- **시스템 제어**: 모드 전환, 상태 모니터링

### 🗄️ 데이터베이스
- **PostgreSQL**: 메인 데이터 저장소
- **Redis**: 캐싱 및 세션 관리
- **Celery**: 백그라운드 작업 처리

## 🚀 빠른 시작

### 1. 시스템 요구사항
- Python 3.8+
- Node.js 18+
- Docker & Docker Compose (선택사항)

### 2. 로컬 개발 환경 설정

#### 백엔드 설정
```bash
cd HVDC_PJT/src/backend
pip install -r requirements.txt
python app.py
```

#### 프론트엔드 설정
```bash
cd HVDC_PJT/src/frontend
npm install
npm start
```

### 3. 통합 실행 (권장)
```bash
cd HVDC_PJT
python run_fullstack.py
```

### 4. Docker 실행
```bash
cd HVDC_PJT
docker-compose up --build
```

## 📱 접속 정보

| 서비스 | URL | 설명 |
|--------|-----|------|
| **웹 애플리케이션** | http://localhost:3000 | 메인 사용자 인터페이스 |
| **API 서버** | http://localhost:8000 | 백엔드 API 엔드포인트 |
| **API 문서** | http://localhost:8000/docs | Swagger UI API 문서 |
| **시스템 상태** | http://localhost:8000/health | 헬스 체크 |

## 🔧 API 엔드포인트

### 시스템 관리
- `GET /` - 시스템 정보
- `GET /health` - 헬스 체크
- `GET /api/v1/system/status` - 시스템 상태
- `POST /api/v1/system/switch-mode` - 모드 전환

### 창고 관리
- `GET /api/v1/warehouses` - 창고 목록
- `POST /api/v1/warehouses` - 창고 생성
- `PUT /api/v1/warehouses/{id}` - 창고 수정
- `DELETE /api/v1/warehouses/{id}` - 창고 삭제

### 컨테이너 관리
- `GET /api/v1/containers` - 컨테이너 목록
- `POST /api/v1/containers` - 컨테이너 생성
- `PUT /api/v1/containers/{id}` - 컨테이너 수정
- `DELETE /api/v1/containers/{id}` - 컨테이너 삭제

### 송장 관리
- `GET /api/v1/invoices` - 송장 목록
- `POST /api/v1/invoices` - 송장 생성
- `PUT /api/v1/invoices/{id}` - 송장 수정
- `DELETE /api/v1/invoices/{id}` - 송장 삭제

### KPI 관리
- `GET /api/v1/kpis` - KPI 목록
- `POST /api/v1/kpis` - KPI 생성
- `PUT /api/v1/kpis/{id}` - KPI 수정
- `DELETE /api/v1/kpis/{id}` - KPI 삭제

## 🧪 테스트 실행

### 백엔드 테스트
```bash
cd HVDC_PJT
pytest tests/test_backend_api.py -v
```

### 프론트엔드 테스트
```bash
cd HVDC_PJT/src/frontend
npm test
```

## 🏛️ 시스템 모드

| 모드 | 설명 | 주요 기능 |
|------|------|-----------|
| **PRIME** | 기본 운영 모드 | 모든 기능 활성화 |
| **ORACLE** | 데이터 분석 모드 | AI 기반 의사결정 지원 |
| **LATTICE** | 창고 최적화 모드 | 적재 및 공간 효율성 극대화 |
| **RHYTHM** | 실시간 모니터링 모드 | KPI 및 알림 집중 |
| **COST-GUARD** | 비용 관리 모드 | 예산 및 비용 최적화 |
| **ZERO** | 안전 모드 | 최소 기능만 활성화 |

## 🔒 보안 및 규정 준수

- **FANR/MOIAT 규정**: UAE 물류 규정 준수
- **OCR 신뢰도**: ≥0.90 임계값 적용
- **압력 한계**: 4t/m² 안전 한계 준수
- **데이터 검증**: Pydantic 모델 기반 입력 검증

## 📊 성능 지표

- **응답 시간**: <3초 (95% 요청)
- **시스템 신뢰도**: ≥0.95
- **가용성**: 99.9%
- **동시 사용자**: 100+ 지원

## 🛠️ 개발 도구

### 백엔드
- **FastAPI**: 고성능 Python 웹 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **Celery**: 비동기 작업 처리

### 프론트엔드
- **React 18**: 최신 React 기능 활용
- **Ant Design**: 엔터프라이즈급 UI 컴포넌트
- **Recharts**: 데이터 시각화
- **Axios**: HTTP 클라이언트

## 📁 프로젝트 구조

```
HVDC_PJT/
├── src/
│   ├── backend/           # FastAPI 백엔드
│   │   ├── app.py        # 메인 애플리케이션
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/          # React 프론트엔드
│       ├── src/
│       │   ├── components/    # 재사용 컴포넌트
│       │   ├── pages/         # 페이지 컴포넌트
│       │   ├── contexts/      # React Context
│       │   └── App.js         # 메인 앱
│       ├── package.json
│       └── Dockerfile
├── tests/                 # 테스트 파일
├── docker-compose.yml     # Docker 설정
├── run_fullstack.py       # 통합 실행 스크립트
└── README_FULLSTACK.md    # 이 파일
```

## 🚨 문제 해결

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 포트 사용 중인 프로세스 확인
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   ```

2. **의존성 설치 실패**
   ```bash
   # Python 가상환경 사용
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Docker 실행 오류**
   ```bash
   # Docker 서비스 상태 확인
   docker --version
   docker-compose --version
   ```

## 📞 지원 및 문의

- **프로젝트 관리자**: HVDC Project Team
- **기술 지원**: 삼성물산 IT팀
- **문서 버전**: v3.4.0

## 📝 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 3.4.0 | 2025-01-03 | Full Stack 시스템 초기 구현 |
| 3.3.0 | 2024-12-20 | 백엔드 API 기본 구조 |
| 3.2.0 | 2024-12-15 | 프론트엔드 React 앱 |
| 3.1.0 | 2024-12-10 | 시스템 아키텍처 설계 |

---

**🎉 HVDC Full Stack 시스템이 성공적으로 구현되었습니다!**

시스템을 시작하려면 `python run_fullstack.py` 명령을 실행하세요.












