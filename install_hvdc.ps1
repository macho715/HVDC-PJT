# HVDC MACHO-GPT v3.4-mini Windows 자동 설치 스크립트
# Samsung C&T Logistics | ADNOC·DSV Partnership

param(
    [string]$InstallPath = "C:\HVDC_PJT",
    [switch]$SkipPythonCheck,
    [switch]$SkipDependencies,
    [switch]$Verbose
)

# 색상 함수 정의
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    switch ($Status) {
        "SUCCESS" { Write-ColorOutput "[$timestamp] ✅ $Message" "Green" }
        "ERROR" { Write-ColorOutput "[$timestamp] ❌ $Message" "Red" }
        "WARNING" { Write-ColorOutput "[$timestamp] ⚠️ $Message" "Yellow" }
        "INFO" { Write-ColorOutput "[$timestamp] ℹ️ $Message" "Cyan" }
        default { Write-ColorOutput "[$timestamp] $Message" "White" }
    }
}

# 메인 설치 함수
function Install-HVDCMachoGPT {
    Write-Status "🚀 HVDC MACHO-GPT v3.4-mini 자동 설치 시작..." "INFO"
    Write-Status "설치 경로: $InstallPath" "INFO"
    
    # 1. Python 확인
    if (-not $SkipPythonCheck) {
        Write-Status "Python 설치 확인 중..." "INFO"
        try {
            $pythonVersion = python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Status "Python 발견: $pythonVersion" "SUCCESS"
            } else {
                throw "Python이 설치되지 않았습니다."
            }
        } catch {
            Write-Status "Python 설치가 필요합니다. https://python.org 에서 다운로드하세요." "ERROR"
            return $false
        }
    }
    
    # 2. 프로젝트 폴더 생성
    Write-Status "프로젝트 폴더 생성 중..." "INFO"
    try {
        if (!(Test-Path $InstallPath)) {
            New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
            Write-Status "프로젝트 폴더 생성됨: $InstallPath" "SUCCESS"
        } else {
            Write-Status "프로젝트 폴더가 이미 존재함: $InstallPath" "WARNING"
        }
        
        Set-Location $InstallPath
    } catch {
        Write-Status "폴더 생성 실패: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # 3. 가상환경 생성
    Write-Status "Python 가상환경 생성 중..." "INFO"
    try {
        if (Test-Path "hvdc_env") {
            Write-Status "기존 가상환경 발견, 제거 중..." "WARNING"
            Remove-Item "hvdc_env" -Recurse -Force
        }
        
        python -m venv hvdc_env
        if ($LASTEXITCODE -eq 0) {
            Write-Status "가상환경 생성 완료" "SUCCESS"
        } else {
            throw "가상환경 생성 실패"
        }
    } catch {
        Write-Status "가상환경 생성 실패: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # 4. 가상환경 활성화
    Write-Status "가상환경 활성화 중..." "INFO"
    try {
        & "$InstallPath\hvdc_env\Scripts\Activate.ps1"
        if ($LASTEXITCODE -eq 0) {
            Write-Status "가상환경 활성화 완료" "SUCCESS"
        } else {
            throw "가상환경 활성화 실패"
        }
    } catch {
        Write-Status "가상환경 활성화 실패: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # 5. pip 업그레이드
    Write-Status "pip 업그레이드 중..." "INFO"
    try {
        python -m pip install --upgrade pip
        Write-Status "pip 업그레이드 완료" "SUCCESS"
    } catch {
        Write-Status "pip 업그레이드 실패: $($_.Exception.Message)" "WARNING"
    }
    
    # 6. 의존성 설치
    if (-not $SkipDependencies) {
        Write-Status "의존성 패키지 설치 중..." "INFO"
        try {
            # 기본 requirements.txt 설치
            if (Test-Path "requirements.txt") {
                pip install -r requirements.txt
                Write-Status "기본 의존성 설치 완료" "SUCCESS"
            } else {
                Write-Status "requirements.txt 파일이 없습니다. 기본 패키지를 설치합니다." "WARNING"
                pip install pandas numpy pyyaml requests python-dotenv
            }
            
            # 추가 권장 패키지 설치
            Write-Status "추가 패키지 설치 중..." "INFO"
            pip install openpyxl xlrd plotly dash
            Write-Status "추가 패키지 설치 완료" "SUCCESS"
            
        } catch {
            Write-Status "의존성 설치 실패: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }
    
    # 7. 설치 검증
    Write-Status "설치 검증 중..." "INFO"
    try {
        $verificationScript = @"
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

print('🎉 설치 검증 완료!')
"@
        
        python -c $verificationScript
        Write-Status "설치 검증 완료" "SUCCESS"
        
    } catch {
        Write-Status "설치 검증 실패: $($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # 8. 실행 스크립트 생성
    Write-Status "실행 스크립트 생성 중..." "INFO"
    try {
        $runScript = @"
@echo off
cd /d $InstallPath
call hvdc_env\Scripts\activate.bat
cd hvdc_macho_gpt\src
python logi_meta_fixed.py %*
"@
        
        $runScript | Out-File -FilePath "$InstallPath\run_hvdc.bat" -Encoding UTF8
        Write-Status "실행 스크립트 생성됨: run_hvdc.bat" "SUCCESS"
        
    } catch {
        Write-Status "실행 스크립트 생성 실패: $($_.Exception.Message)" "WARNING"
    }
    
    # 9. 완료 메시지
    Write-Status "🎉 HVDC MACHO-GPT v3.4-mini 설치 완료!" "SUCCESS"
    Write-Status "다음 단계:" "INFO"
    Write-Status "1. 데이터 파일을 hvdc_macho_gpt/data/ 폴더에 복사" "INFO"
    Write-Status "2. run_hvdc.bat 실행하여 시스템 시작" "INFO"
    Write-Status "3. INSTALLATION_GUIDE.md 참조하여 상세 설정" "INFO"
    
    return $true
}

# 스크립트 실행
try {
    $success = Install-HVDCMachoGPT
    if ($success) {
        exit 0
    } else {
        exit 1
    }
} catch {
    Write-Status "설치 중 예상치 못한 오류 발생: $($_.Exception.Message)" "ERROR"
    exit 1
} 