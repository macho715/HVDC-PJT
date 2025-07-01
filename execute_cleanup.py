#!/usr/bin/env python3
"""
HVDC Project 중복 파일 자동 삭제 실행 도구
MACHO-GPT v3.4-mini │ Samsung C&T Logistics
"""

import os
import json
import shutil
from pathlib import Path

def execute_cleanup(suggestions_file='duplicate_cleanup_suggestions.json', dry_run=False):
    """중복 파일 정리 실행"""
    
    if not os.path.exists(suggestions_file):
        print(f"❌ 제안 파일을 찾을 수 없습니다: {suggestions_file}")
        return
    
    # 제안 파일 로드
    with open(suggestions_file, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)
    
    print(f"🧹 MACHO-GPT v3.4-mini 중복 파일 정리 {'시뮬레이션' if dry_run else '실행'}")
    print(f"📋 총 정리 대상: {len(suggestions)}개 그룹")
    print("=" * 80)
    
    deleted_count = 0
    total_saved_bytes = 0
    errors = []
    
    for i, suggestion in enumerate(suggestions, 1):
        keep_file = suggestion['keep']
        delete_files = suggestion['delete']
        reason = suggestion['reason']
        
        print(f"\n📋 그룹 {i}: {reason}")
        print(f"   🎯 유지: {keep_file}")
        
        # 유지할 파일이 실제로 존재하는지 확인
        if not os.path.exists(keep_file):
            print(f"   ⚠️ 유지할 파일이 없음: {keep_file}")
            continue
        
        for delete_file in delete_files:
            if os.path.exists(delete_file):
                try:
                    file_size = os.path.getsize(delete_file)
                    
                    if dry_run:
                        print(f"   🗑️ 삭제 예정: {delete_file} ({file_size:,} bytes)")
                    else:
                        # 실제 삭제 실행
                        if os.path.isfile(delete_file):
                            os.remove(delete_file)
                        elif os.path.isdir(delete_file):
                            shutil.rmtree(delete_file)
                        
                        print(f"   ✅ 삭제 완료: {delete_file} ({file_size:,} bytes)")
                        deleted_count += 1
                        total_saved_bytes += file_size
                        
                except Exception as e:
                    error_msg = f"삭제 실패: {delete_file} - {e}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
            else:
                print(f"   ⚠️ 파일 없음: {delete_file}")
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("🎯 정리 작업 완료 요약")
    print("=" * 80)
    
    if dry_run:
        total_files_to_delete = sum(len(s['delete']) for s in suggestions)
        print(f"📊 삭제 예정 파일: {total_files_to_delete:,}개")
        print(f"💾 절약 예정 용량: {total_saved_bytes:,} bytes ({total_saved_bytes/1024/1024:.2f} MB)")
    else:
        print(f"📊 삭제된 파일: {deleted_count:,}개")
        print(f"💾 절약된 용량: {total_saved_bytes:,} bytes ({total_saved_bytes/1024/1024:.2f} MB)")
    
    if errors:
        print(f"\n⚠️ 오류 발생: {len(errors)}개")
        for error in errors[:5]:  # 최대 5개만 표시
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   ... 및 {len(errors) - 5}개 추가 오류")
    
    return deleted_count, total_saved_bytes, errors

def create_backup_list(suggestions_file='duplicate_cleanup_suggestions.json'):
    """삭제 예정 파일 목록을 백업용으로 저장"""
    
    with open(suggestions_file, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)
    
    backup_list = {
        'timestamp': '2025-01-01 00:00:00',
        'total_groups': len(suggestions),
        'files_to_delete': []
    }
    
    for suggestion in suggestions:
        keep_file = suggestion['keep']
        delete_files = suggestion['delete']
        
        for delete_file in delete_files:
            if os.path.exists(delete_file):
                backup_list['files_to_delete'].append({
                    'path': delete_file,
                    'size': os.path.getsize(delete_file),
                    'keep_alternative': keep_file
                })
    
    backup_filename = 'deleted_files_backup_list.json'
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(backup_list, f, ensure_ascii=False, indent=2)
    
    print(f"📋 백업 목록 저장: {backup_filename}")
    return backup_filename

def main():
    """메인 실행 함수"""
    
    print("🚀 MACHO-GPT v3.4-mini 중복 파일 정리 실행")
    print("=" * 60)
    
    # 1. 먼저 시뮬레이션 실행
    print("\n1️⃣ 시뮬레이션 실행 (실제 삭제 안함)")
    deleted_count, saved_bytes, errors = execute_cleanup(dry_run=True)
    
    # 2. 백업 목록 생성
    print("\n2️⃣ 백업 목록 생성")
    backup_file = create_backup_list()
    
    # 3. 실제 삭제 실행
    print("\n3️⃣ 실제 삭제 실행")
    print("⚠️ 주의: 이 작업은 되돌릴 수 없습니다!")
    
    # 자동 실행 (사용자 확인 없이)
    print("✅ 자동 실행 모드로 중복 파일 삭제를 진행합니다...")
    
    deleted_count, saved_bytes, errors = execute_cleanup(dry_run=False)
    
    print(f"\n🎯 최종 결과:")
    print(f"   📊 삭제된 파일: {deleted_count:,}개")
    print(f"   💾 절약된 용량: {saved_bytes:,} bytes ({saved_bytes/1024/1024:.2f} MB)")
    print(f"   ❌ 오류 수: {len(errors)}개")
    
    if errors:
        # 오류 로그 저장
        with open('cleanup_errors.log', 'w', encoding='utf-8') as f:
            for error in errors:
                f.write(f"{error}\n")
        print("📋 오류 상세 내용이 'cleanup_errors.log'에 저장됨")

if __name__ == "__main__":
    main() 