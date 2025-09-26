# HVDC Logistics Dashboard 설치 및 실행 가이드

## 🚀 설치 방법

### 1. 가상환경 생성 (권장)
```bash
# Python 가상환경 생성
python -m venv hvdc_dashboard
source hvdc_dashboard/bin/activate  # Linux/Mac
# 또는
hvdc_dashboard\Scripts\activate     # Windows
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
python app.py
```

## 🌐 접속 방법

브라우저에서 다음 주소로 접속:
- **로컬**: http://localhost:8050
- **네트워크**: http://[서버IP]:8050

## 📊 대시보드 기능

### 메인 기능
- **Sankey 다이어그램**: 물류 흐름 시각화 (Import → Customs → Warehouse → Distribution → Export)
- **재고 수준 차트**: 창고별 누적 재고 현황
- **KPI 카드**: 주요 지표 (총 TEU, 일평균 TEU, 활성 창고 수)

### 필터링 기능
- **날짜 범위 선택**: 특정 기간 데이터 분석
- **창고 선택**: 전체 또는 개별 창고 데이터 보기
- **실시간 업데이트**: 필터 변경 시 즉시 그래프 업데이트

## 🛠️ 파일 구조

```
hvdc_dashboard/
├── app.py              # 메인 Dash 애플리케이션
├── data_loader.py      # 데이터 로드 및 생성 모듈
├── requirements.txt    # 의존성 패키지 목록
└── setup_and_run.md   # 설치 및 실행 가이드
```

## 📈 데이터 설명

### 생성되는 데이터
- **기간**: 2024년 1월 1일 ~ 12월 31일
- **창고**: Seoul_Hub, Busan_Port, Incheon_Gateway, Gwangju_Center
- **물류 단계**: Import → Customs → Warehouse → Distribution → Export
- **단위**: TEU (Twenty-foot Equivalent Unit)

### 데이터 특징
- 계절성 반영 (여름철 물동량 증가)
- 창고별 차별화된 패턴
- 재고 변동 시뮬레이션

## 🔧 커스터마이징

### 실제 데이터 연결
`data_loader.py`의 `load_io()` 함수를 수정하여 실제 데이터베이스나 파일에서 데이터를 로드할 수 있습니다.

### 추가 기능 구현
- 알림 시스템
- 데이터 내보내기
- 더 많은 차트 타입
- 사용자 인증

## 🐛 문제 해결

### 포트 충돌 시
```python
# app.py 마지막 줄 수정
app.run_server(host="0.0.0.0", port=8051, debug=True)  # 포트 번호 변경
```

### 메모리 부족 시
- 데이터 크기 축소
- 날짜 범위 제한
- 서버 메모리 증설

## 📝 주의사항

- 대시보드는 개발 모드로 실행됩니다
- 프로덕션 환경에서는 `debug=False` 설정 권장
- 실제 운영 시에는 적절한 인증 및 보안 조치 필요