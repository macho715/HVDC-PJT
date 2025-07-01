#!/usr/bin/env python3
"""
HVDC Project 중복 파일 삭제 예정 목록 표시
MACHO-GPT v3.4-mini │ Samsung C&T Logistics
"""

import os
import json
from pathlib import Path

def show_cleanup_list(suggestions_file='duplicate_cleanup_suggestions.json'):
    """삭제 예정 파일 목록 표시"""
    
    if not os.path.exists(suggestions_file):
        print(f"❌ 제안 파일을 찾을 수 없습니다: {suggestions_file}")
        return
    
    # 제안 파일 로드
    with open(suggestions_file, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)
    
    print("🧹 MACHO-GPT v3.4-mini 중복 파일 삭제 예정 목록")
    print("=" * 80)
    print(f"📋 총 중복 그룹: {len(suggestions)}개")
    
    total_files_to_delete = 0
    total_bytes_to_save = 0
    existing_files = []
    missing_files = []
    
    for i, suggestion in enumerate(suggestions, 1):
        keep_file = suggestion['keep']
        delete_files = suggestion['delete']
        reason = suggestion['reason']
        
        print(f"\n📋 그룹 {i}: {os.path.basename(keep_file)}")
        print(f"   📝 이유: {reason}")
        print(f"   🎯 유지할 파일: {keep_file}")
        
        # 유지할 파일 존재 여부 확인
        if os.path.exists(keep_file):
            keep_size = os.path.getsize(keep_file)
            print(f"      ✅ 존재 ({keep_size:,} bytes)")
        else:
            print(f"      ❌ 파일 없음")
        
        print(f"   🗑️ 삭제 예정 파일 ({len(delete_files)}개):")
        
        for j, delete_file in enumerate(delete_files, 1):
            if os.path.exists(delete_file):
                file_size = os.path.getsize(delete_file)
                total_files_to_delete += 1
                total_bytes_to_save += file_size
                existing_files.append({
                    'path': delete_file,
                    'size': file_size,
                    'group': i
                })
                print(f"      {j}. ✅ {delete_file} ({file_size:,} bytes)")
            else:
                missing_files.append(delete_file)
                print(f"      {j}. ❌ {delete_file} (파일 없음)")
    
    # 요약 정보
    print("\n" + "=" * 80)
    print("📊 삭제 예정 파일 요약")
    print("=" * 80)
    print(f"✅ 실제 존재하는 삭제 대상: {total_files_to_delete:,}개")
    print(f"❌ 이미 없는 파일: {len(missing_files):,}개")
    print(f"💾 절약 예정 용량: {total_bytes_to_save:,} bytes ({total_bytes_to_save/1024/1024:.2f} MB)")
    
    # 상위 10개 큰 파일들
    if existing_files:
        print(f"\n🔝 용량이 큰 삭제 예정 파일 TOP 10:")
        sorted_files = sorted(existing_files, key=lambda x: x['size'], reverse=True)
        for i, file_info in enumerate(sorted_files[:10], 1):
            size_mb = file_info['size'] / 1024 / 1024
            filename = os.path.basename(file_info['path'])
            print(f"   {i:2d}. {filename} ({size_mb:.2f} MB)")
            print(f"       📁 {file_info['path']}")
    
    # 디렉토리별 분류
    print(f"\n📁 디렉토리별 삭제 파일 수:")
    dir_counts = {}
    for file_info in existing_files:
        dir_path = os.path.dirname(file_info['path'])
        if dir_path not in dir_counts:
            dir_counts[dir_path] = {'count': 0, 'size': 0}
        dir_counts[dir_path]['count'] += 1
        dir_counts[dir_path]['size'] += file_info['size']
    
    # 파일 수가 많은 순으로 정렬
    sorted_dirs = sorted(dir_counts.items(), key=lambda x: x[1]['count'], reverse=True)
    for dir_path, info in sorted_dirs[:15]:  # 상위 15개 디렉토리
        count = info['count']
        size_mb = info['size'] / 1024 / 1024
        print(f"   📂 {dir_path}")
        print(f"      🗑️ {count}개 파일, {size_mb:.2f} MB")
    
    return total_files_to_delete, total_bytes_to_save

def main():
    """메인 실행 함수"""
    
    print("🚀 MACHO-GPT v3.4-mini 삭제 예정 파일 목록 조회")
    print("=" * 60)
    
    total_files, total_bytes = show_cleanup_list()
    
    print(f"\n🎯 최종 요약:")
    print(f"   📊 삭제 예정 파일: {total_files:,}개")
    print(f"   💾 절약 예정 용량: {total_bytes:,} bytes ({total_bytes/1024/1024:.2f} MB)")
    
    if total_files > 0:
        print(f"\n❓ 이 파일들을 삭제하시겠습니까?")
        print(f"   ✅ 삭제하려면: python execute_cleanup.py")
        print(f"   ❌ 취소하려면: 아무것도 하지 마세요")

if __name__ == "__main__":
    main() 