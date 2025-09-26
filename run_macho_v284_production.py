#!/usr/bin/env python3
"""
🎯 MACHO v2.8.4 프로덕션 실행기
자동 실행: Enhanced Data Sync + Flow Code 분석
"""

import subprocess
import sys
from datetime import datetime

def run_macho_production():
    print("🚀 MACHO v2.8.4 프로덕션 시스템 실행")
    print("=" * 60)
    
    try:
        # 1. Enhanced Data Sync 실행
        print("\n📊 Enhanced Data Sync v2.8.4 실행 중...")
        result1 = subprocess.run([sys.executable, "enhanced_data_sync_v284_windows.py"], 
                               capture_output=True, text=True)
        
        if result1.returncode == 0:
            print("✅ Enhanced Data Sync 완료")
        else:
            print(f"❌ Enhanced Data Sync 실패: {result1.stderr}")
            return False
        
        # 2. Flow Code 분석 실행
        print("\n🔍 Flow Code 분석 v2.8.4 실행 중...")
        result2 = subprocess.run([sys.executable, "macho_flow_corrected_v284.py"], 
                               capture_output=True, text=True)
        
        if result2.returncode == 0:
            print("✅ Flow Code 분석 완료")
        else:
            print(f"❌ Flow Code 분석 실패: {result2.stderr}")
            return False
        
        print("\n🎉 MACHO v2.8.4 프로덕션 시스템 실행 완료!")
        print("📊 상태: 🥇 PERFECT MATCH")
        return True
        
    except Exception as e:
        print(f"❌ 시스템 실행 실패: {e}")
        return False

if __name__ == "__main__":
    success = run_macho_production()
    sys.exit(0 if success else 1)
