#!/bin/bash
# HVDC MACHO-GPT v3.4-mini Linux/macOS 자동 설치 스크립트
# Samsung C&T Logistics | ADNOC·DSV Partnership

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 기본 변수
INSTALL_PATH="${HOME}/HVDC_PJT"
PYTHON_VERSION="3.8"
SKIP_PYTHON_CHECK=false
SKIP_DEPENDENCIES=false
VERBOSE=false

# 함수 정의
print_status() {
    local message="$1"
    local status="$2"
    local timestamp=$(date '+%H:%M:%S')
    
    case $status in
        "SUCCESS")
            echo -e "[${timestamp}] ${GREEN}✅${NC} $message"
            ;;
        "ERROR")
            echo -e "[${timestamp}] ${RED}❌${NC} $message"
            ;;
        "WARNING")
            echo -e "[${timestamp}] ${YELLOW}⚠️${NC} $message"
            ;;
        "INFO")
            echo -e "[${timestamp}] ${CYAN}ℹ️${NC} $message"
            ;;
        *)
            echo -e "[${timestamp}] $message"
            ;;
    esac
}

print_usage() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -p, --path PATH        설치 경로 지정 (기본값: ~/HVDC_PJT)"
    echo "  -v, --python-version   Python 버전 지정 (기본값: 3.8)"
    echo "  --skip-python-check    Python 설치 확인 건너뛰기"
    echo "  --skip-dependencies    의존성 설치 건너뛰기"
    echo "  --verbose              상세 출력"
    echo "  -h, --help             이 도움말 표시"
    echo ""
    echo "예제:"
    echo "  $0                                    # 기본 설치"
    echo "  $0 -p /opt/hvdc                       # 특정 경로에 설치"
    echo "  $0 --skip-python-check --verbose      # Python 확인 건너뛰고 상세 출력"
}

# 명령행 인수 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        -v|--python-version)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --skip-python-check)
            SKIP_PYTHON_CHECK=true
            shift
            ;;
        --skip-dependencies)
            SKIP_DEPENDENCIES=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            print_usage
            exit 1
            ;;
    esac
done

# 메인 설치 함수
install_hvdc_machogpt() {
    print_status "🚀 HVDC MACHO-GPT v3.4-mini 자동 설치 시작..." "INFO"
    print_status "설치 경로: $INSTALL_PATH" "INFO"
    
    # 1. Python 확인
    if [ "$SKIP_PYTHON_CHECK" = false ]; then
        print_status "Python 설치 확인 중..." "INFO"
        
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
            PYTHON_VERSION_ACTUAL=$(python3 --version 2>&1)
            print_status "Python3 발견: $PYTHON_VERSION_ACTUAL" "SUCCESS"
        elif command -v python &> /dev/null; then
            PYTHON_CMD="python"
            PYTHON_VERSION_ACTUAL=$(python --version 2>&1)
            print_status "Python 발견: $PYTHON_VERSION_ACTUAL" "SUCCESS"
        else
            print_status "Python이 설치되지 않았습니다." "ERROR"
            print_status "Python $PYTHON_VERSION 이상을 설치하세요." "ERROR"
            print_status "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv" "INFO"
            print_status "macOS: brew install python3" "INFO"
            exit 1
        fi
        
        # Python 버전 확인
        PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
        PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
            print_status "Python 3.8 이상이 필요합니다. 현재 버전: $PYTHON_MAJOR.$PYTHON_MINOR" "ERROR"
            exit 1
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    # 2. 프로젝트 폴더 생성
    print_status "프로젝트 폴더 생성 중..." "INFO"
    if [ ! -d "$INSTALL_PATH" ]; then
        mkdir -p "$INSTALL_PATH"
        print_status "프로젝트 폴더 생성됨: $INSTALL_PATH" "SUCCESS"
    else
        print_status "프로젝트 폴더가 이미 존재함: $INSTALL_PATH" "WARNING"
    fi
    
    cd "$INSTALL_PATH"
    
    # 3. 가상환경 생성
    print_status "Python 가상환경 생성 중..." "INFO"
    if [ -d "hvdc_env" ]; then
        print_status "기존 가상환경 발견, 제거 중..." "WARNING"
        rm -rf hvdc_env
    fi
    
    if $PYTHON_CMD -m venv hvdc_env; then
        print_status "가상환경 생성 완료" "SUCCESS"
    else
        print_status "가상환경 생성 실패" "ERROR"
        exit 1
    fi
    
    # 4. 가상환경 활성화
    print_status "가상환경 활성화 중..." "INFO"
    source hvdc_env/bin/activate
    
    if [ $? -eq 0 ]; then
        print_status "가상환경 활성화 완료" "SUCCESS"
    else
        print_status "가상환경 활성화 실패" "ERROR"
        exit 1
    fi
    
    # 5. pip 업그레이드
    print_status "pip 업그레이드 중..." "INFO"
    if python -m pip install --upgrade pip; then
        print_status "pip 업그레이드 완료" "SUCCESS"
    else
        print_status "pip 업그레이드 실패" "WARNING"
    fi
    
    # 6. 의존성 설치
    if [ "$SKIP_DEPENDENCIES" = false ]; then
        print_status "의존성 패키지 설치 중..." "INFO"
        
        # 기본 requirements.txt 설치
        if [ -f "requirements.txt" ]; then
            if pip install -r requirements.txt; then
                print_status "기본 의존성 설치 완료" "SUCCESS"
            else
                print_status "기본 의존성 설치 실패" "ERROR"
                exit 1
            fi
        else
            print_status "requirements.txt 파일이 없습니다. 기본 패키지를 설치합니다." "WARNING"
            if pip install pandas numpy pyyaml requests python-dotenv; then
                print_status "기본 패키지 설치 완료" "SUCCESS"
            else
                print_status "기본 패키지 설치 실패" "ERROR"
                exit 1
            fi
        fi
        
        # 추가 권장 패키지 설치
        print_status "추가 패키지 설치 중..." "INFO"
        if pip install openpyxl xlrd plotly dash; then
            print_status "추가 패키지 설치 완료" "SUCCESS"
        else
            print_status "추가 패키지 설치 실패" "WARNING"
        fi
    fi
    
    # 7. 설치 검증
    print_status "설치 검증 중..." "INFO"
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

print('🎉 설치 검증 완료!')
"
    
    if [ $? -eq 0 ]; then
        print_status "설치 검증 완료" "SUCCESS"
    else
        print_status "설치 검증 실패" "ERROR"
        exit 1
    fi
    
    # 8. 실행 스크립트 생성
    print_status "실행 스크립트 생성 중..." "INFO"
    cat > "$INSTALL_PATH/run_hvdc.sh" << EOF
#!/bin/bash
cd "$INSTALL_PATH"
source hvdc_env/bin/activate
cd hvdc_macho_gpt/src
python logi_meta_fixed.py "\$@"
EOF
    
    chmod +x "$INSTALL_PATH/run_hvdc.sh"
    print_status "실행 스크립트 생성됨: run_hvdc.sh" "SUCCESS"
    
    # 9. 완료 메시지
    print_status "🎉 HVDC MACHO-GPT v3.4-mini 설치 완료!" "SUCCESS"
    echo ""
    print_status "다음 단계:" "INFO"
    print_status "1. 데이터 파일을 hvdc_macho_gpt/data/ 폴더에 복사" "INFO"
    print_status "2. ./run_hvdc.sh 실행하여 시스템 시작" "INFO"
    print_status "3. INSTALLATION_GUIDE.md 참조하여 상세 설정" "INFO"
    echo ""
    print_status "빠른 시작:" "INFO"
    print_status "  cd $INSTALL_PATH" "INFO"
    print_status "  ./run_hvdc.sh --help" "INFO"
}

# 스크립트 실행
main() {
    # 루트 권한 확인
    if [ "$EUID" -eq 0 ]; then
        print_status "루트 권한으로 실행하지 마세요." "ERROR"
        exit 1
    fi
    
    # 설치 실행
    install_hvdc_machogpt
}

# 메인 함수 호출
main "$@" 