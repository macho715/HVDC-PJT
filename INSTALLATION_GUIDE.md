# HVDC MACHO-GPT v3.4-mini 설치 가이드북
## Samsung C&T Logistics | ADNOC·DSV Partnership

### 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 전 준비사항](#설치-전-준비사항)
3. [환경 설정](#환경-설정)
4. [의존성 설치](#의존성-설치)
5. [데이터 준비](#데이터-준비)
6. [실행 및 테스트](#실행-및-테스트)
7. [문제 해결](#문제-해결)
8. [자동화 스크립트](#자동화-스크립트)

---

## 🖥️ 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 이상 (3.9+ 권장)
- **RAM**: 4GB 이상 (8GB 권장)
- **저장공간**: 2GB 이상
- **네트워크**: 인터넷 연결 (패키지 다운로드용)

### 권장 사양
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.9 또는 3.10
- **RAM**: 8GB 이상
- **저장공간**: 5GB 이상
- **CPU**: 4코어 이상

---

## 📦 설치 전 준비사항

### 1. Python 설치 확인
```bash
# Python 버전 확인
python --version
# 또는
python3 --version

# pip 설치 확인
pip --version
```

### 2. Git 설치 (선택사항)
```bash
# Windows
winget install Git.Git

# macOS
brew install git

# Ubuntu
sudo apt update && sudo apt install git
```

---

## ⚙️ 환경 설정

### Windows 환경
```powershell
# 1. 프로젝트 폴더 생성
mkdir "C:\HVDC_PJT"
cd "C:\HVDC_PJT"

# 2. 가상환경 생성
python -m venv hvdc_env

# 3. 가상환경 활성화
.\hvdc_env\Scripts\Activate.ps1

# 4. PowerShell 인코딩 설정 (이모지 지원)
chcp 65001
```

### macOS/Linux 환경
```bash
# 1. 프로젝트 폴더 생성
mkdir ~/HVDC_PJT
cd ~/HVDC_PJT

# 2. 가상환경 생성
python3 -m venv hvdc_env

# 3. 가상환경 활성화
source hvdc_env/bin/activate
```

---

## 📚 의존성 설치

### 1. 기본 의존성 설치
```bash
# requirements.txt 설치
pip install -r requirements.txt

# 추가 권장 패키지
pip install openpyxl xlrd plotly dash
```

### 2. 설치 확인
```bash
# 설치된 패키지 확인
pip list

# Python에서 import 테스트
python -c "import pandas, numpy, yaml, requests; print('✅ 모든 패키지 설치 완료')"
```

---

## 📁 데이터 준비

### 1. 폴더 구조 생성
```
HVDC_PJT/
├── hvdc_macho_gpt/
│   ├── data/                    # Excel 데이터 파일들
│   ├── src/                     # 소스 코드
│   ├── reports/                 # 생성된 리포트
│   ├── configs/                 # 설정 파일
│   ├── templates/               # 템플릿 파일
│   └── tests/                   # 테스트 파일
├── requirements.txt
└── README.md
```

### 2. 데이터 파일 복사
```bash
# 데이터 파일들을 data/ 폴더에 복사
cp "HVDC WAREHOUSE_*.xlsx" hvdc_macho_gpt/data/
```

---

## 🚀 실행 및 테스트

### 1. 메인 시스템 실행
```bash
# 가상환경 활성화 후
cd hvdc_macho_gpt/src

# 메인 시스템 실행
python logi_meta_fixed.py

# 또는 특정 명령어 실행
python logi_meta_fixed.py --command warehouse-status
```

### 2. 창고 관리 시스템 실행
```bash
# 창고 확장 모듈 실행
python warehouse_enhanced.py

# 특정 창고 분석
python warehouse_enhanced.py --warehouse "DSV Al Markaz"
```

### 3. 설치 검증
```bash
# 설치 검증 스크립트 실행
python -c "
import sys
import pandas as pd
import numpy as np
import yaml
import requests
from pathlib import Path

print('🔍 HVDC MACHO-GPT 설치 검증 중...')

# 필수 패키지 확인
packages = ['pandas', 'numpy', 'yaml', 'requests']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} - 설치됨')
    except ImportError:
        print(f'❌ {pkg} - 설치 필요')

# 데이터 파일 확인
data_files = [
    'data/HVDC WAREHOUSE_INVOICE.xlsx',
    'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
    'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
]

for file in data_files:
    if Path(file).exists():
        print(f'✅ {file} - 존재함')
    else:
        print(f'❌ {file} - 없음')

print('🎉 설치 검증 완료!')
"
```

---

## 🔧 문제 해결

### 1. 일반적인 오류

#### Python 버전 오류
```bash
# Python 3.8+ 설치 확인
python --version

# 가상환경 재생성
rm -rf hvdc_env
python -m venv hvdc_env
```

#### 패키지 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 클리어 후 재설치
pip cache purge
pip install -r requirements.txt --force-reinstall
```

#### 인코딩 오류 (Windows)
```powershell
# PowerShell UTF-8 설정
chcp 65001

# 또는 환경변수 설정
$env:PYTHONIOENCODING="utf-8"
```

### 2. 특정 오류 해결

#### YAML 파싱 오류
```bash
# expected_stock.yml 파일 수정
# 주석 처리된 YAML 구문 확인
```

#### Excel 파일 읽기 오류
```bash
# openpyxl 설치
pip install openpyxl

# 파일 경로 확인
ls -la data/*.xlsx
```

#### 메모리 부족 오류
```bash
# 가상환경 메모리 제한 설정
export PYTHONMALLOC=malloc
```

---

## 🤖 자동화 스크립트

### Windows 자동 설치 스크립트
```powershell
# install_hvdc.ps1
Write-Host "🚀 HVDC MACHO-GPT 자동 설치 시작..." -ForegroundColor Green

# Python 확인
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python이 설치되지 않았습니다." -ForegroundColor Red
    exit 1
}

# 프로젝트 폴더 생성
$projectPath = "C:\HVDC_PJT"
if (!(Test-Path $projectPath)) {
    New-Item -ItemType Directory -Path $projectPath
}

Set-Location $projectPath

# 가상환경 생성
python -m venv hvdc_env
.\hvdc_env\Scripts\Activate.ps1

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
pip install openpyxl xlrd plotly dash

Write-Host "✅ 설치 완료!" -ForegroundColor Green
```

### Linux/macOS 자동 설치 스크립트
```bash
#!/bin/bash
# install_hvdc.sh

echo "🚀 HVDC MACHO-GPT 자동 설치 시작..."

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다."
    exit 1
fi

# 프로젝트 폴더 생성
PROJECT_PATH="$HOME/HVDC_PJT"
mkdir -p $PROJECT_PATH
cd $PROJECT_PATH

# 가상환경 생성
python3 -m venv hvdc_env
source hvdc_env/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
pip install openpyxl xlrd plotly dash

echo "✅ 설치 완료!"
```

### 실행 스크립트
```bash
# run_hvdc.sh (Linux/macOS)
#!/bin/bash
cd ~/HVDC_PJT
source hvdc_env/bin/activate
cd hvdc_macho_gpt/src
python logi_meta_fixed.py "$@"
```

```batch
:: run_hvdc.bat (Windows)
@echo off
cd /d C:\HVDC_PJT
call hvdc_env\Scripts\activate.bat
cd hvdc_macho_gpt\src
python logi_meta_fixed.py %*
```

---

## 📊 사용 예제

### 1. 기본 시스템 상태 확인
```bash
python logi_meta_fixed.py --status
```

### 2. 창고 상태 조회
```bash
python logi_meta_fixed.py --command warehouse-status
```

### 3. 월별 창고 리포트 생성
```bash
python logi_meta_fixed.py --command warehouse-monthly --month 2025-06
```

### 4. 대시보드 생성
```bash
python logi_meta_fixed.py --command warehouse-dashboard
```

---

## 🔧 추천 명령어

🔧 **추천 명령어:**
/cmd_install_dependencies [의존성 패키지 설치 - 초기 설정]
/cmd_verify_installation [설치 상태 검증 - 시스템 확인]  
/cmd_run_warehouse_analysis [창고 분석 실행 - 데이터 처리]

---

## 📞 지원 및 문의

### 기술 지원
- **이메일**: hvdc-support@samsungct.com
- **문서**: `/docs` 폴더 참조
- **로그**: `logs/` 폴더 확인

### 버그 리포트
1. 오류 메시지 스크린샷
2. 시스템 정보 (`python --version`, `pip list`)
3. 실행 명령어 및 입력 데이터

---

**© 2025 Samsung C&T Logistics | ADNOC·DSV Partnership**
**MACHO-GPT v3.4-mini | Enhanced Cursor IDE Integration** 