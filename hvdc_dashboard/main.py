# -*- coding: utf-8 -*-
# HVDC 대시보드 메인 실행 파일

import sys
import os
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hvdc_dashboard.taipy_app import app
from hvdc_dashboard.config import UI_CONFIG, LOG_CONFIG

def setup_logging():
    """로깅 설정"""
    # 로그 디렉토리 생성
    log_dir = Path(LOG_CONFIG['file']).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 로깅 설정
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """메인 실행 함수"""
    print("🚀 HVDC 프로젝트 물류 KPI 대시보드 시작...")
    
    # 로깅 설정
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 환경 정보 출력
        logger.info(f"프로젝트 루트: {project_root}")
        logger.info(f"Python 버전: {sys.version}")
        logger.info(f"작업 디렉토리: {os.getcwd()}")
        
        # Taipy 앱 실행
        logger.info("Taipy 앱 시작...")
        app.run(
            title=UI_CONFIG['title'],
            dark_mode=UI_CONFIG['dark_mode'],
            port=UI_CONFIG['port'],
            debug=UI_CONFIG['debug'],
            show_upload=UI_CONFIG['show_upload']
        )
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"앱 실행 중 오류 발생: {e}")
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 