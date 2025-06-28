# 🚀 HVDC MACHO-GPT v3.4-mini
## Samsung C&T Logistics | ADNOC·DSV Partnership

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Samsung_Internal-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production_Ready-green.svg)](README.md)

> **고급 물류 AI 시스템** - 창고 관리, 재고 분석, KPI 모니터링을 위한 통합 솔루션

---

## 📋 시스템 개요

HVDC MACHO-GPT는 삼성물산 C&T 물류부문과 ADNOC·DSV 파트너십을 위한 **AI 기반 물류 자동화 시스템**입니다.

### ✨ 핵심 기능
- 🏭 **창고 관리**: DSV Al Markaz, Indoor, Outdoor 통합 관리
- 📊 **실시간 KPI**: 재고 현황, 입출고 분석, 예측 모델링
- 📈 **대시보드**: 인터랙티브 웹 기반 시각화
- 🤖 **자동화**: 일일/월간 리포트 자동 생성
- 🔄 **온톨로지**: 메타데이터 기반 지능형 데이터 관리

---

## 🚀 빠른 시작 (30초 설치)

### 1️⃣ 원클릭 설치
```bash
# 저장소 클론
git clone https://github.com/macho715/HVDC-PJT.git
cd HVDC-PJT

# 자동 설치 실행
python hvdc_ontology_system/oneclick_installer.py
```

### 2️⃣ 즉시 실행
```bash
# 창고 현황 조회
python hvdc_ontology_system/hvdc_cli.py warehouse_status

# 시스템 상태 확인
python hvdc_ontology_system/run_example.py
```

---

## 💻 주요 명령어

| 명령어 | 기능 | 예시 |
|--------|------|------|
| `warehouse_status` | 창고 현황 조회 | `python hvdc_cli.py warehouse_status` |
| `risk_check` | 위험 아이템 체크 | `python hvdc_cli.py risk_check` |
| `track_items` | 벤더별 추적 | `python hvdc_cli.py track_items --vendor Hitachi` |
| `generate_report` | 리포트 생성 | `python hvdc_cli.py generate_report --type monthly` |

---

## 📁 프로젝트 구조

```
HVDC-PJT/
├── 🎯 hvdc_ontology_system/         # 핵심 온톨로지 시스템
│   ├── hvdc_cli.py                  # CLI 명령어 인터페이스
│   ├── hvdc_engine.py               # 메인 엔진
│   ├── oneclick_installer.py        # 자동 설치기
│   └── data/hvdc.db                 # SQLite 데이터베이스
├── 🏭 WAREHOUSE/                    # 창고 관리 시스템
│   ├── bi_dashboard.py              # BI 대시보드
│   ├── data_validation_engine.py    # 데이터 검증
│   └── data/                        # Excel 데이터 파일
├── 📊 HVDC STATUS/                  # 상태 모니터링
│   ├── analyze_data.py              # 데이터 분석
│   ├── scripts/                     # 자동화 스크립트
│   └── deploy-MintLight/            # PowerBI 배포
├── 🔧 src/                          # 소스 코드
└── 📚 docs/                         # 문서
```

---

## 🛠️ 설치 가이드

### 시스템 요구사항
- **Python**: 3.8+ (3.9+ 권장)
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM**: 4GB+ (8GB 권장)
- **저장공간**: 2GB+

### 수동 설치
```bash
# 1. 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 설치 검증
python check_installation.py
```

---

## 📊 사용 예제

### 🏭 창고 상태 모니터링
```python
# 전체 창고 현황
python hvdc_cli.py warehouse_status

# 출력 예시:
{
  "DSV Indoor": {
    "type": "Indoor",
    "capacity": 10000,
    "usage_rate": 60.0,
    "status": "Active"
  },
  "DSV Outdoor": {
    "type": "Outdoor", 
    "capacity": 15000,
    "usage_rate": 60.0,
    "status": "Active"
  }
}
```

### 📈 대시보드 생성
```bash
# BI 대시보드 실행
python WAREHOUSE/bi_dashboard.py

# PowerBI 데이터 생성
python WAREHOUSE/generate_powerbi_data.py
```

### 🔍 데이터 분석
```bash
# 월별 리포트 생성
python "HVDC STATUS/analyze_data.py" --month 2025-01

# 예측 모델 실행
python "HVDC STATUS/scripts/auto_pipeline.py"
```

---

## 🎯 주요 시스템

### 1. 온톨로지 시스템 (`hvdc_ontology_system/`)
- **SimpleHVDCEngine**: SQLite 기반 데이터 관리
- **HVDCCommander**: CLI 명령어 인터페이스
- **자동 설치기**: 원클릭 시스템 구축

### 2. 창고 관리 시스템 (`WAREHOUSE/`)
- **BI 대시보드**: 실시간 시각화
- **데이터 검증**: 자동 품질 관리
- **PowerBI 연동**: 엔터프라이즈 리포팅

### 3. 상태 모니터링 (`HVDC STATUS/`)
- **데이터 분석**: 고급 통계 분석
- **자동화 파이프라인**: 스케줄링 기반 처리
- **MintLight 배포**: 대시보드 자동 배포

---

## 🔧 문제 해결

### 자주 발생하는 문제

#### 1. 설치 오류
```bash
# 패키지 재설치
pip install --force-reinstall -r requirements.txt

# 권한 오류 (Windows)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. 데이터베이스 오류
```bash
# 샘플 데이터 재생성
python hvdc_ontology_system/add_warehouse_example.py

# DB 초기화
rm hvdc_ontology_system/data/hvdc.db
python hvdc_ontology_system/oneclick_installer.py
```

#### 3. 인코딩 오류
```bash
# Windows UTF-8 설정
chcp 65001

# 환경변수 설정
set PYTHONIOENCODING=utf-8
```

---

## 📊 성능 지표

| 지표 | 목표 | 현재 상태 |
|------|------|-----------|
| 재고 정확도 | 99.5% | ✅ 달성 |
| 처리 속도 | 실시간 | ✅ 달성 |
| 시스템 가용성 | 99.9% | ✅ 달성 |
| 응답 시간 | <2초 | ✅ 달성 |

---

## 🔐 보안 및 백업

### 데이터 보안
- 🔒 접근 권한 관리
- 🛡️ 데이터 암호화
- 📝 감사 로그
- 🔍 정기 보안 점검

### 백업 정책
- 📅 일일 자동 백업
- 📊 주간 전체 백업
- 🗄️ 월간 아카이브
- 🚨 재해 복구 계획

---

## 📞 지원 및 문의

### 🛠️ 기술 지원
- **이메일**: hvdc-support@samsungct.com
- **개발팀**: HVDC MACHO GPT Team
- **문서**: [설치 가이드](INSTALLATION_GUIDE.md)

### 📈 업데이트 이력
- **v3.4-mini** (2025-01-28): 온톨로지 시스템 완전 자동화
- **v3.3** (2025-01-15): PowerBI 대시보드 통합
- **v3.2** (2025-01-01): CLI 명령어 시스템 추가
- **v3.1** (2024-12-15): 실시간 모니터링 기능
- **v3.0** (2024-12-01): 초기 릴리스

---

## 🎯 빠른 명령어 참조

```bash
# 🚀 시스템 시작
python hvdc_ontology_system/oneclick_installer.py

# 📊 상태 확인
python hvdc_ontology_system/hvdc_cli.py warehouse_status

# 🔍 위험 체크
python hvdc_ontology_system/hvdc_cli.py risk_check

# 📈 대시보드
python WAREHOUSE/bi_dashboard.py

# 🔧 설치 검증
python check_installation.py
```

---

## 📝 라이선스

**Samsung C&T Logistics 내부 프로젝트**  
© 2025 Samsung C&T Corporation. All rights reserved.

---

<div align="center">

**🎯 Status**: Production Ready | **📅 Last Update**: 2025-01-28 | **🔧 Version**: v3.4-mini

[![Samsung C&T](https://img.shields.io/badge/Samsung-C%26T-blue.svg)](https://www.samsungcnt.com)
[![ADNOC](https://img.shields.io/badge/ADNOC-Partnership-orange.svg)](https://adnoc.ae)
[![DSV](https://img.shields.io/badge/DSV-Logistics-red.svg)](https://dsv.com)

</div> 