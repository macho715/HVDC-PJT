# HVDC MACHO GPT v3.4-mini

Samsung C&T Logistics | ADNOC-DSV Partnership

## 📋 프로젝트 개요

HVDC MACHO-GPT v3.4-mini는 삼성물산 C&T 물류부문과 ADNOC-DSV 파트너십을 위한 고급 물류 AI 시스템입니다. 창고 관리, 재고 분석, KPI 모니터링, 그리고 실시간 대시보드 기능을 제공합니다.

## 🚀 주요 기능

• **창고 관리 시스템**: DSV AI Markaz, DSV Indoor, DSV Outdoor 창고별 재고 관리
• **실시간 KPI 모니터링**: 재고 현황, 입출고 분석, 예측 모델링
• **Excel 데이터 처리**: HVDC 창고 데이터 자동 분석 및 리포트 생성
• **대시보드 시각화**: 인터랙티브 웹 기반 대시보드
• **자동화 워크플로우**: 일일/월간 리포트 자동 생성

## 📁 프로젝트 구조

```
hvdc_macho_gpt/
├── src/
│   ├── logi_meta_fixed.py          # 메인 시스템 (메타데이터 관리)
│   ├── warehouse_enhanced.py       # 창고 핵심 모듈
│   ├── core/                       # 핵심 모듈
│   ├── integrations/               # 외부 시스템 연동
│   ├── workflows/                  # 워크플로우
│   └── utils/                      # 유틸리티
├── data/                           # Excel 데이터 파일
│   ├── HVDC WAREHOUSE_INVOICE.xlsx
│   ├── HVDC WAREHOUSE_HITACHI(HE).xlsx
│   └── HVDC WAREHOUSE_SIMENSE(SIM).xlsx
├── reports/                        # 생성된 리포트
├── configs/                        # 설정 파일
└── HVDC STATUS/                    # 상태 모니터링
    ├── analyze_data.py
    ├── scripts/
    └── deploy-MintLight/
```

## 🛠️ 설치 및 실행

### 1. 환경 설정
```bash
# Python 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 필수 패키지 설치
pip install -r requirements.txt
```

### 2. 원클릭 설치 (권장)
```bash
# HVDC 온톨로지 시스템 자동 설치
cd hvdc_macho_gpt/hvdc_ontology_system
python oneclick_installer.py
```

### 3. 수동 설정
```bash
# 메인 시스템 실행
python src/logi_meta_fixed.py

# 창고 시스템 실행
python src/warehouse_enhanced.py

# 데이터 분석 실행
python "HVDC STATUS/analyze_data.py"
```

## 💻 CLI 명령어

```bash
# 창고 현황 조회
python hvdc_cli.py warehouse_status

# 위험 아이템 체크
python hvdc_cli.py risk_check

# 벤더별 추적
python hvdc_cli.py track_items --vendor Hitachi

# 실행 예시
python run_example.py
```

## 📊 데이터 구조

### 지원 데이터 형식
- **Excel 파일**: .xlsx, .xls
- **CSV 파일**: UTF-8 인코딩
- **SQLite DB**: 온톨로지 데이터 저장

### 주요 데이터 테이블
- **창고 정보**: 위치, 용량, 사용률
- **재고 아이템**: 품목, 수량, 벤더 정보
- **입출고 기록**: 날짜, 수량, 담당자
- **KPI 메트릭**: 효율성, 정확도, 처리량

## 🔧 고급 기능

### 1. 온톨로지 시스템
```bash
# 온톨로지 매핑 실행
python tools/ontology_mapper.py

# YAML 검증
python tools/validate_yaml_ontology.py
```

### 2. 대시보드 시스템
```bash
# BI 대시보드 실행
python bi_dashboard.py

# PowerBI 데이터 생성
python generate_powerbi_data.py
```

### 3. 자동화 파이프라인
```bash
# 자동 파이프라인 실행
python scripts/auto_pipeline.py

# 스케줄링 설정
python scripts/automation/pipeline.py
```

## 📈 성능 모니터링

### KPI 지표
- **재고 정확도**: 99.5% 목표
- **처리 속도**: 실시간 데이터 업데이트
- **시스템 가용성**: 99.9% 업타임
- **데이터 품질**: 자동 검증 및 정제

### 알람 시스템
- 재고 부족 알람
- 시스템 오류 알람
- 성능 저하 알람
- 데이터 품질 알람

## 🔐 보안 및 백업

### 데이터 보안
- 접근 권한 관리
- 데이터 암호화
- 로그 모니터링
- 정기 보안 점검

### 백업 정책
- 일일 자동 백업
- 주간 전체 백업
- 월간 아카이브
- 재해 복구 계획

## 📞 지원 및 문의

### 기술 지원
- **개발팀**: HVDC MACHO GPT Team
- **이메일**: hvdc-support@samsung.com
- **문서**: [내부 위키](http://wiki.samsung.com/hvdc)

### 업데이트 이력
- **v3.4-mini**: 온톨로지 시스템 완전 자동화
- **v3.3**: PowerBI 대시보드 통합
- **v3.2**: CLI 명령어 시스템 추가
- **v3.1**: 실시간 모니터링 기능
- **v3.0**: 초기 릴리스

## 📝 라이선스

Samsung C&T Logistics 내부 프로젝트
© 2025 Samsung C&T Corporation. All rights reserved.

---

**🎯 Status**: Production Ready | **📅 Last Update**: 2025-01-28 | **🔧 Version**: v3.4-mini 