#!/usr/bin/env python3
"""
HVDC Project 중복 파일 검색 및 정리 도구
MACHO-GPT v3.4-mini │ Samsung C&T Logistics
"""

import os
import hashlib
from collections import defaultdict
from pathlib import Path
import json

def get_file_hash(filepath):
    """파일 해시값 계산"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"⚠️ 해시 계산 실패: {filepath} - {e}")
        return None

def get_file_info(filepath):
    """파일 정보 수집"""
    try:
        stat = os.stat(filepath)
        return {
            'path': filepath,
            'size': stat.st_size,
            'name': os.path.basename(filepath),
            'dir': os.path.dirname(filepath),
            'modified': stat.st_mtime
        }
    except Exception as e:
        print(f"⚠️ 파일 정보 수집 실패: {filepath} - {e}")
        return None

def find_duplicates(base_dir, target_dirs):
    """중복 파일 찾기"""
    file_hashes = defaultdict(list)
    name_groups = defaultdict(list)
    
    # 검색할 파일 확장자
    target_extensions = {'.py', '.json', '.md', '.txt', '.ttl', '.yml', '.yaml', '.bat', '.sh'}
    
    total_files = 0
    
    for target_dir in target_dirs:
        full_path = os.path.join(base_dir, target_dir)
        if not os.path.exists(full_path):
            print(f"❌ 디렉토리 없음: {full_path}")
            continue
            
        print(f"🔍 검색 중: {target_dir}")
        
        for root, dirs, files in os.walk(full_path):
            # __pycache__, .git, venv 등 제외
            dirs[:] = [d for d in dirs if not d.startswith(('.', '__pycache__', 'venv'))]
            
            for file in files:
                if any(file.endswith(ext) for ext in target_extensions):
                    filepath = os.path.join(root, file)
                    file_info = get_file_info(filepath)
                    
                    if file_info:
                        total_files += 1
                        
                        # 해시 기반 중복 검사
                        file_hash = get_file_hash(filepath)
                        if file_hash:
                            file_hashes[file_hash].append(file_info)
                        
                        # 파일명 기반 그룹핑
                        name_groups[file].append(file_info)
    
    print(f"📊 총 검색된 파일: {total_files:,}개")
    
    # 해시 기반 중복 파일
    hash_duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}
    
    # 파일명 기반 중복 파일 (크기가 다를 수 있음)
    name_duplicates = {k: v for k, v in name_groups.items() if len(v) > 1}
    
    return hash_duplicates, name_duplicates

def analyze_duplicates(hash_duplicates, name_duplicates):
    """중복 파일 분석 및 리포트"""
    print("\n" + "="*80)
    print("🔍 HVDC PROJECT 중복 파일 분석 결과")
    print("="*80)
    
    # 1. 완전 중복 파일 (해시 동일)
    if hash_duplicates:
        print(f"\n🎯 완전 중복 파일: {len(hash_duplicates)}개 그룹")
        total_waste = 0
        
        for i, (file_hash, files) in enumerate(hash_duplicates.items(), 1):
            print(f"\n📋 중복 그룹 {i}: {files[0]['name']}")
            print(f"   크기: {files[0]['size']:,} bytes")
            print(f"   중복 수: {len(files)}개")
            
            # 중복으로 인한 용량 낭비 계산
            waste = files[0]['size'] * (len(files) - 1)
            total_waste += waste
            print(f"   낭비 용량: {waste:,} bytes")
            
            for j, file_info in enumerate(files):
                marker = "🎯" if j == 0 else "🗑️"
                print(f"   {marker} {file_info['path']}")
        
        print(f"\n💾 총 낭비 용량: {total_waste:,} bytes ({total_waste/1024/1024:.2f} MB)")
    else:
        print("\n✅ 완전 중복 파일 없음")
    
    # 2. 파일명 중복 (내용 다를 수 있음)
    if name_duplicates:
        print(f"\n📝 파일명 중복: {len(name_duplicates)}개")
        
        for filename, files in name_duplicates.items():
            if len(files) > 1:
                sizes = [f['size'] for f in files]
                if len(set(sizes)) > 1:  # 크기가 다른 경우만 표시
                    print(f"\n📄 {filename} ({len(files)}개)")
                    for file_info in files:
                        print(f"   📁 {file_info['path']} ({file_info['size']:,} bytes)")
    
    return hash_duplicates

def suggest_cleanup(hash_duplicates):
    """정리 제안"""
    if not hash_duplicates:
        return []
    
    cleanup_suggestions = []
    
    for file_hash, files in hash_duplicates.items():
        # 우선순위: 더 깊은 경로의 파일을 삭제 대상으로 제안
        files_sorted = sorted(files, key=lambda x: (x['path'].count(os.sep), x['path']))
        keep_file = files_sorted[0]
        delete_files = files_sorted[1:]
        
        suggestion = {
            'keep': keep_file['path'],
            'delete': [f['path'] for f in delete_files],
            'reason': f"동일 파일 {len(files)}개 중 가장 상위 경로 유지"
        }
        cleanup_suggestions.append(suggestion)
    
    return cleanup_suggestions

def main():
    """메인 실행 함수"""
    base_dir = r"C:\HVDC PJT"
    target_dirs = ["hvdc_macho_gpt", "hvdc_ontology_system", "Mapping"]
    
    print("🚀 MACHO-GPT v3.4-mini 중복 파일 검색 시작")
    print(f"📂 기준 디렉토리: {base_dir}")
    print(f"🎯 검색 대상: {', '.join(target_dirs)}")
    
    # 중복 파일 검색
    hash_duplicates, name_duplicates = find_duplicates(base_dir, target_dirs)
    
    # 분석 결과 출력
    analyze_duplicates(hash_duplicates, name_duplicates)
    
    # 정리 제안
    cleanup_suggestions = suggest_cleanup(hash_duplicates)
    
    if cleanup_suggestions:
        print(f"\n🧹 정리 제안: {len(cleanup_suggestions)}개 그룹")
        
        # 정리 제안을 JSON으로 저장
        with open('duplicate_cleanup_suggestions.json', 'w', encoding='utf-8') as f:
            json.dump(cleanup_suggestions, f, ensure_ascii=False, indent=2)
        
        print("📋 정리 제안이 'duplicate_cleanup_suggestions.json'에 저장됨")
        
        # 사용자 확인 후 삭제 실행 여부
        print("\n❓ 중복 파일을 자동으로 삭제하시겠습니까? (y/N): ", end="")
        
        # 자동 실행하지 않고 제안만 표시
        print("N (안전을 위해 수동 확인 후 삭제 권장)")
    else:
        print("\n✅ 정리할 중복 파일이 없습니다.")

if __name__ == "__main__":
    main() 