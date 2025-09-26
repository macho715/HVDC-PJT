# 🚢 HVDC 프로젝트 물류 KPI 대시보드

삼성C&T HVDC 프로젝트의 물류 데이터를 분석하고 시각화하는 실무형 대시보드입니다.

## 📋 프로젝트 구조

```
hvdc_dashboard/
├── config.py              # 환경 설정 및 경로 관리
├── data_loader.py         # 데이터 로딩 및 검증
├── business_logic.py      # KPI 계산 및 비즈니스 로직
├── taipy_app.py          # Taipy GUI 애플리케이션
├── main.py               # 메인 실행 파일
├── tests/
│   └── test_loader.py    # 테스트 코드
├── data/                 # 데이터 파일 디렉토리
└── logs/                 # 로그 파일 디렉토리
```

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install taipy pandas numpy
```

### 2. 실행

```bash
cd hvdc_dashboard
python main.py
```

### 3. 테스트 실행

```bash
python tests/test_loader.py
```

## 📊 주요 기능

### KPI 대시보드
- **TEU 합계**: 컨테이너 용량 총합
- **OOG 건수**: Out of Gauge 화물 건수
- **관세/VAT**: 총 관세 및 부가세
- **DEM/DET**: 입출고 지연 일수
- **창고 점유율**: 창고 사용률

### 필터링 기능
- 연도별 필터
- 월별 필터
- 카테고리별 필터
- 창고별 필터

### 시각화
- 월별 TEU 추이 (막대 그래프)
- 카테고리별 TEU 분포 (파이 차트)
- 창고별 TEU 분포 (막대 그래프)
- KPI 상세 테이블
- 원본 데이터 테이블

### 알림 시스템
- DEM/DET 초과 경고
- 창고 점유율 초과 경고
- OOG 비율 높음 경고

## ⚙️ 설정

### 환경 변수
- `HVDC_DATA_PATH`: 데이터 파일 경로
- `HVDC_SHEET_NAME`: Excel 시트 이름 (기본값: "LSR")

### 설정 파일 (config.py)
- KPI 임계값 설정
- TEU 가중치 설정
- OOG 키워드 설정
- HS Code 매핑

## 🔧 개발 가이드

### 새로운 KPI 추가
1. `business_logic.py`의 `calculate_kpis()` 함수에 KPI 계산 로직 추가
2. `taipy_app.py`의 UI에 KPI 표시 섹션 추가

### 새로운 필터 추가
1. `business_logic.py`의 `apply_filters()` 함수에 필터 로직 추가
2. `taipy_app.py`의 UI에 필터 컨트롤 추가

### 새로운 시각화 추가
1. `business_logic.py`의 `get_visualization_data()` 함수에 데이터 생성 로직 추가
2. `taipy_app.py`의 UI에 차트 섹션 추가

## 📝 로그

로그 파일은 `logs/hvdc_dashboard.log`에 저장됩니다.

## 🧪 테스트

```bash
# 전체 테스트 실행
python tests/test_loader.py

# 개별 테스트 실행
python -c "from tests.test_loader import test_sample_data_creation; test_sample_data_creation()"
```

## 🔍 문제 해결

### 데이터 로딩 실패
1. 데이터 파일 경로 확인
2. 파일 형식 확인 (Excel/CSV)
3. 필수 컬럼 존재 여부 확인

### Taipy 실행 오류
1. 의존성 설치 확인
2. Python 버전 확인 (3.8+ 권장)
3. 포트 충돌 확인

## 📞 지원

문제가 발생하면 로그 파일을 확인하고 개발팀에 문의하세요.

---

**개발**: 삼성C&T HVDC 프로젝트팀  
**버전**: 1.0.0  
**최종 업데이트**: 2024-07-30 