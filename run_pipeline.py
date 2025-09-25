#!/usr/bin/env python3
"""
HVDC DataChain Pipeline 실행 스크립트
올바른 데이터 디렉토리 경로로 파이프라인 실행
"""

import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.append('src')

from hvdc_datachain_pipeline import HVDCDataChainPipeline

def main():
    """메인 실행 함수"""
    try:
        # 현재 디렉토리의 data 폴더 사용
        data_dir = Path.cwd() / "data"
        
        print(f"데이터 디렉토리: {data_dir}")
        print(f"Excel 파일 목록:")
        for excel_file in data_dir.glob("*.xlsx"):
            print(f"  - {excel_file.name}")
        
        # 파이프라인 초기화 및 실행
        pipeline = HVDCDataChainPipeline(
            data_dir=str(data_dir),
            mode="PRIME"
        )
        
        result = pipeline.run_pipeline()
        
        # 결과 출력
        print("=" * 60)
        print("HVDC DataChain Pipeline 실행 결과")
        print("=" * 60)
        print(f"상태: {result['status']}")
        print(f"모드: {result.get('mode', 'N/A')}")
        print(f"신뢰도: {result.get('confidence', 0):.2f}%")
        print(f"타임스탬프: {result['timestamp']}")
        
        if result['status'] == 'SUCCESS':
            print("\n다음 행동:")
            for action in result.get('next_actions', []):
                print(f"  - {action}")
        elif result['status'] == 'WARNING':
            print(f"\n경고 메시지: {result.get('message', 'N/A')}")
        elif result['status'] == 'ERROR':
            print(f"\n오류: {result.get('error', 'N/A')}")
            
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"실행 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 