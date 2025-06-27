@echo off
REM HVDC MACHO-GPT v3.4-mini Windows 실행 스크립트
REM Samsung C&T Logistics | ADNOC·DSV Partnership

echo 🚀 HVDC MACHO-GPT v3.4-mini 시작 중...

REM 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

REM 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 가상환경 활성화됨
) else (
    echo ⚠️ 가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.
)

REM src 디렉토리로 이동
if exist "src" (
    cd src
) else (
    echo ❌ src 디렉토리를 찾을 수 없습니다.
    pause
    exit /b 1
)

REM 메인 시스템 실행
if exist "logi_meta_fixed.py" (
    echo 📊 MACHO-GPT 시스템 실행 중...
    python logi_meta_fixed.py %*
) else (
    echo ❌ logi_meta_fixed.py 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo 🏁 시스템 종료
pause 