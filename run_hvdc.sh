#!/bin/bash
# HVDC MACHO-GPT v3.4-mini Linux/macOS 실행 스크립트
# Samsung C&T Logistics | ADNOC·DSV Partnership

echo "🚀 HVDC MACHO-GPT v3.4-mini 시작 중..."

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 가상환경 활성화됨"
else
    echo "⚠️ 가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다."
fi

# src 디렉토리로 이동
if [ -d "src" ]; then
    cd src
else
    echo "❌ src 디렉토리를 찾을 수 없습니다."
    exit 1
fi

# 메인 시스템 실행
if [ -f "logi_meta_fixed.py" ]; then
    echo "📊 MACHO-GPT 시스템 실행 중..."
    python logi_meta_fixed.py "$@"
else
    echo "❌ logi_meta_fixed.py 파일을 찾을 수 없습니다."
    exit 1
fi

echo "🏁 시스템 종료" 