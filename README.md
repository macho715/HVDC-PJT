# HVDC MACHO-GPT v3.4-mini
## Samsung C&T Logistics | ADNOC·DSV Partnership

### 📋 프로젝트 개요

HVDC MACHO-GPT v3.4-mini는 삼성물산 C&T 물류부문과 ADNOC·DSV 파트너십을 위한 고급 물류 AI 시스템입니다. 창고 관리, 재고 분석, KPI 모니터링, 그리고 실시간 대시보드 기능을 제공합니다.

### 🚀 주요 기능

- **창고 관리 시스템**: DSV Al Markaz, DSV Indoor, DSV Outdoor 창고별 재고 관리
- **실시간 KPI 모니터링**: 재고 현황, 입출고 분석, 예측 모델링
- **Excel 데이터 처리**: HVDC 창고 데이터 자동 분석 및 리포트 생성
- **대시보드 시각화**: 인터랙티브 웹 기반 대시보드
- **자동화 워크플로우**: 일일/월간 리포트 자동 생성

### 📁 프로젝트 구조

```
hvdc_macho_gpt/
├── src/                          # 소스 코드
│   ├── logi_meta_fixed.py       # 메인 시스템 (메타데이터 관리)
│   ├── warehouse_enhanced.py    # 창고 확장 모듈
│   ├── core/                    # 핵심 모듈
│   ├── integrations/            # 외부 시스템 연동
│   ├── workflows/               # 워크플로우
│   └── utils/                   # 유틸리티
├── data/                        # Excel 데이터 파일
│   ├── HVDC WAREHOUSE_INVOICE.xlsx
│   ├── HVDC WAREHOUSE_HITACHI(HE).xlsx
│   ├── HVDC WAREHOUSE_SIMENSE(SIM).xlsx
│   └── HVDC WAREHOUSE_HITACHI(HE_LOCAL).xlsx
├── reports/                     # 생성된 리포트
├── configs/                     # 설정 파일
├── templates/                   # 템플릿
├── tests/                       # 테스트 파일
├── requirements.txt             # Python 의존성
├── INSTALLATION_GUIDE.md        # 설치 가이드
├── install_hvdc.ps1            # Windows 자동 설치
├── install_hvdc.sh             # Linux/macOS 자동 설치
├── run_hvdc.bat                # Windows 실행 스크립트
├── run_hvdc.sh                 # Linux/macOS 실행 스크립트
└── check_installation.py       # 설치 검증 스크립트
```

### 🛠️ 빠른 시작

#### 1. 자동 설치 (권장)

**Windows:**
```powershell
# PowerShell에서 실행
.\install_hvdc.ps1
```

**Linux/macOS:**
```bash
# 터미널에서 실행
chmod +x install_hvdc.sh
./install_hvdc.sh
```

#### 2. 수동 설치

```bash
# 1. Python 가상환경 생성
python -m venv hvdc_env

# 2. 가상환경 활성화
# Windows:
.\hvdc_env\Scripts\Activate.ps1
# Linux/macOS:
source hvdc_env/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
pip install openpyxl xlrd plotly dash

# 4. 설치 검증
python check_installation.py
```

#### 3. 시스템 실행

**Windows:**
```cmd
run_hvdc.bat
```

**Linux/macOS:**
```bash
./run_hvdc.sh
```

### 📊 사용 예제

#### 기본 시스템 상태 확인
```bash
python src/logi_meta_fixed.py --status
```

#### 창고 상태 조회
```bash
python src/logi_meta_fixed.py --command warehouse-status
```

#### 월별 창고 리포트 생성
```bash
python src/logi_meta_fixed.py --command warehouse-monthly --month 2025-06
```

#### 대시보드 생성
```bash
python src/logi_meta_fixed.py --command warehouse-dashboard
```

### 🔧 시스템 요구사항

- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 이상 (3.9+ 권장)
- **RAM**: 4GB 이상 (8GB 권장)
- **저장공간**: 2GB 이상

### 📚 주요 모듈

#### LogiMetaSystemWarehouse
메인 메타데이터 관리 시스템으로 다음 기능을 제공합니다:
- 명령어 레지스트리 관리
- 시스템 상태 모니터링
- KPI 트리거 설정
- 도구 통합 상태 관리

#### HVDCWarehouseCommand
창고 확장 모듈로 다음 기능을 제공합니다:
- 창고별 재고 현황 분석
- 월별 입출고 리포트
- 현장별 공급망 분석
- 3D 창고 레이아웃 시각화

### 🔧 문제 해결

#### 일반적인 오류

1. **Python 버전 오류**
   ```bash
   python --version  # 3.8+ 확인
   ```

2. **패키지 설치 오류**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **인코딩 오류 (Windows)**
   ```powershell
   chcp 65001  # UTF-8 설정
   ```

#### 설치 검증
```bash
python check_installation.py
```

### 📞 지원 및 문의

- **기술 지원**: hvdc-support@samsungct.com
- **문서**: `INSTALLATION_GUIDE.md` 참조
- **버그 리포트**: GitHub Issues 또는 이메일

### 🔧 추천 명령어

🔧 **추천 명령어:**
/cmd_install_dependencies [의존성 패키지 설치 - 초기 설정]
/cmd_verify_installation [설치 상태 검증 - 시스템 확인]  
/cmd_run_warehouse_analysis [창고 분석 실행 - 데이터 처리]

---

**© 2025 Samsung C&T Logistics | ADNOC·DSV Partnership**
**MACHO-GPT v3.4-mini | Enhanced Cursor IDE Integration** 