# logi_meta_fixed.py 최종 설치 가이드북

## 📦 목적
- **MACHO-GPT v3.4-mini Command Metadata System + WAREHOUSE Extension**
- HVDC 프로젝트의 메타데이터 관리, 창고/현장/월별 재고 분석, KPI 트리거, 명령어 자동화 지원

---

## 1. 시스템 요구사항
- **Python**: 3.8 이상 (3.9~3.12 권장)
- **운영체제**: Windows 10/11, macOS, Ubuntu 18.04+
- **메모리**: 4GB 이상
- **저장공간**: 500MB 이상

---

## 2. 준비 파일
- `logi_meta_fixed.py` (메타데이터 시스템)
- `warehouse_enhanced.py` (창고 확장 모듈)
- `requirements_meta.txt` (의존성 목록)
- `test_meta_installation.py` (설치 확인 스크립트)

---

## 3. 설치 절차

### 3.1. 가상환경 생성 (권장)
```bash
python -m venv logi_meta_env
# Windows
logi_meta_env\Scripts\activate
# macOS/Linux
source logi_meta_env/bin/activate
```

### 3.2. 의존성 설치
```bash
pip install -r requirements_meta.txt
```

### 3.3. 파일 복사
- 위 4개 파일을 같은 폴더에 복사 (예: `C:\HVDC_META`)

### 3.4. 설치 확인
```bash
python test_meta_installation.py
```
- 모든 항목이 ✅로 나오면 성공

---

## 4. 주요 명령어 예시

### 4.1. 시스템 상태 확인
```bash
python logi_meta_fixed.py --status
```

### 4.2. 명령어 목록 확인
```bash
python logi_meta_fixed.py --list all
python logi_meta_fixed.py --list warehouse
```

### 4.3. 창고 상태/월별 분석/대시보드
```bash
python logi_meta_fixed.py "logi_master warehouse-status"
python logi_meta_fixed.py "logi_master warehouse-monthly" --year 2024 --month 6
python logi_meta_fixed.py "logi_master warehouse-dashboard"
```

### 4.4. 메타데이터 내보내기
```bash
python logi_meta_fixed.py --export json
python logi_meta_fixed.py --warehouse-export yaml
```

---

## 5. 윈도우/한글 환경 특이점
- **이모지(✅ 등) 출력 오류**: PowerShell에서 `chcp 65001` 실행 후 재시도, 또는 print문에서 이모지 제거
- **경로 문제**: 파일명/경로에 한글, 공백이 있으면 오류 발생 가능 → 영문/공백 없는 경로 권장
- **가상환경 권장**: 시스템 Python(Anaconda 등)보다 venv 사용 시 충돌 적음

---

## 6. 문제해결/FAQ

### Q1. ImportError: No module named 'warehouse_enhanced'
- warehouse_enhanced.py가 같은 폴더에 있는지 확인
- PYTHONPATH에 현재 폴더 추가: `set PYTHONPATH=%CD%` (Windows), `export PYTHONPATH=$(pwd)` (Linux)

### Q2. ModuleNotFoundError: No module named 'plotly'
- `pip install plotly` 또는 `pip install -r requirements_meta.txt` 재실행

### Q3. UnicodeEncodeError: 'cp949' codec can't encode character
- PowerShell에서 `chcp 65001` 실행 후 재시도
- 또는 print문에서 이모지(✅ 등) 제거

### Q4. AttributeError: 'NoneType' object has no attribute ...
- warehouse_enhanced.py가 정상적으로 로드되지 않은 경우
- 파일 경로, 이름, PYTHONPATH 확인

### Q5. 시스템 명령어 실행 실패
- test_meta_installation.py로 설치 상태 점검
- 누락된 파일/패키지 확인 후 재설치

---

## 7. 설치 체크리스트
- [ ] Python 3.8+ 설치
- [ ] 가상환경 생성 및 활성화
- [ ] requirements_meta.txt로 패키지 설치
- [ ] logi_meta_fixed.py, warehouse_enhanced.py 복사
- [ ] test_meta_installation.py로 설치 확인
- [ ] 시스템 상태/명령어 실행 성공

---

## 8. 자동화/고급

### 8.1. Windows 자동 실행 배치
```batch
@echo off
cd /d "%~dp0"
call logi_meta_env\Scripts\activate
python logi_meta_fixed.py --status
python logi_meta_fixed.py "logi_master warehouse-status"
pause
```

### 8.2. Linux/macOS 자동 실행 스크립트
```bash
#!/bin/bash
cd "$(dirname "$0")"
source logi_meta_env/bin/activate
python logi_meta_fixed.py --status
python logi_meta_fixed.py "logi_master warehouse-status"
```

---

## 9. 참고/백업
- requirements_meta.txt: 의존성 목록
- test_meta_installation.py: 설치 확인 자동화
- logi_meta_fixed.py, warehouse_enhanced.py: 핵심 모듈

---

## 10. 문의/지원
- 시스템 로그: `python logi_meta_fixed.py --status > logi_meta.log 2>&1`
- 패키지 목록: `pip freeze > installed_packages_meta.txt`
- 백업: `cp logi_meta_fixed.py logi_meta_fixed.py.bak`

---

**🎉 설치가 완료되었습니다! MACHO-GPT v3.4-mini 메타데이터 시스템을 사용할 수 있습니다.**

🔧 **추천 명령어:**
/logi_master warehouse-status [창고 상태 확인 - 시스템 검증]
/logi_master warehouse-monthly [월별 창고 분석 - 트렌드 파악]
/logi_master warehouse-dashboard [창고 대시보드 생성 - 시각화]

# expected_stock.yml 수정 필요
"2025-06-24": {}
"2025-06-25": {}
"2025-07-01": {}

tolerance:
  default: 2
  "DSV Al Markaz": 2
  "DSV Indoor": 2
  "DSV Outdoor": 2 