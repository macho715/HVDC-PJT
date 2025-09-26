#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8 인코딩 변환 스크립트
HVDC 프로젝트의 설정 파일들을 UTF-8로 변환하여 pytest 인코딩 오류 해결
"""

import os
import chardet
from pathlib import Path
import logging
from typing import List, Tuple

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('utf8_conversion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def detect_encoding(file_path: Path) -> Tuple[str, float]:
    """파일의 인코딩을 감지합니다."""
    try:
        with open(file_path, 'rb') as f:
            raw = f.read()
            if not raw:
                return 'utf-8', 1.0
            
            detected = chardet.detect(raw)
            encoding = detected['encoding']
            confidence = detected['confidence']
            
            if encoding is None:
                return 'utf-8', 0.0
                
            return encoding.lower(), confidence
    except Exception as e:
        logger.error(f"인코딩 감지 실패 {file_path}: {e}")
        return 'utf-8', 0.0

def convert_file_to_utf8(file_path: Path, backup: bool = True) -> bool:
    """파일을 UTF-8로 변환합니다."""
    try:
        # 인코딩 감지
        current_encoding, confidence = detect_encoding(file_path)
        
        if current_encoding == 'utf-8':
            logger.info(f"SKIP: {file_path} (이미 UTF-8)")
            return True
            
        logger.info(f"감지: {file_path} ({current_encoding}, 신뢰도: {confidence:.2f})")
        
        # 백업 생성
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            if not backup_path.exists():
                with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                logger.info(f"백업 생성: {backup_path}")
        
        # 파일 읽기
        try:
            with open(file_path, 'r', encoding=current_encoding, errors='ignore') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 다른 인코딩 시도
            for fallback_encoding in ['cp949', 'euc-kr', 'latin-1', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding, errors='ignore') as f:
                        content = f.read()
                    logger.info(f"대체 인코딩 사용: {fallback_encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                logger.error(f"모든 인코딩 시도 실패: {file_path}")
                return False
        
        # UTF-8로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"✅ 변환 완료: {file_path} ({current_encoding} → UTF-8)")
        return True
        
    except Exception as e:
        logger.error(f"변환 실패 {file_path}: {e}")
        return False

def find_config_files(root_dir: Path) -> List[Path]:
    """설정 파일들을 찾습니다."""
    config_files = []
    extensions = ['.ini', '.cfg', '.toml', '.md']
    
    for ext in extensions:
        config_files.extend(root_dir.rglob(f'*{ext}'))
    
    # node_modules 제외
    config_files = [f for f in config_files if 'node_modules' not in str(f)]
    
    return sorted(config_files)

def main():
    """메인 함수"""
    root_dir = Path('.')
    logger.info(f"작업 디렉토리: {root_dir.absolute()}")
    
    # 설정 파일 찾기
    config_files = find_config_files(root_dir)
    logger.info(f"발견된 설정 파일 수: {len(config_files)}")
    
    # 주요 파일 우선 처리
    priority_files = [
        'pytest.ini',
        'setup.cfg', 
        'tox.ini',
        'pyproject.toml',
        'requirements.txt',
        'README.md'
    ]
    
    priority_paths = []
    other_paths = []
    
    for file_path in config_files:
        if file_path.name in priority_files:
            priority_paths.append(file_path)
        else:
            other_paths.append(file_path)
    
    # 우선순위 파일 먼저 처리
    logger.info("=== 우선순위 파일 처리 ===")
    success_count = 0
    for file_path in priority_paths:
        if convert_file_to_utf8(file_path):
            success_count += 1
    
    logger.info(f"우선순위 파일 변환 완료: {success_count}/{len(priority_paths)}")
    
    # 나머지 파일 처리
    logger.info("=== 나머지 파일 처리 ===")
    success_count = 0
    for file_path in other_paths[:50]:  # 처음 50개만 처리
        if convert_file_to_utf8(file_path):
            success_count += 1
    
    logger.info(f"나머지 파일 변환 완료: {success_count}/{min(50, len(other_paths))}")
    
    logger.info("=== 변환 작업 완료 ===")
    logger.info("이제 pytest를 다시 실행해보세요:")
    logger.info("pytest -q --tb=short --disable-warnings")

if __name__ == "__main__":
    main() 