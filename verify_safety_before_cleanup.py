#!/usr/bin/env python3
"""
HVDC Project 중복 파일 삭제 전 안전성 검증
MACHO-GPT v3.4-mini │ Samsung C&T Logistics
"""

import os
import json
import hashlib
import ast
import re
from pathlib import Path
from collections import defaultdict

def calculate_file_hash(filepath):
    """파일의 MD5 해시 계산"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"❌ 해시 계산 실패: {filepath} - {e}")
        return None

def analyze_python_imports(filepath):
    """Python 파일의 import 구문 분석"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    except Exception as e:
        return []

def check_file_references(filepath, project_root):
    """프로젝트 내에서 파일이 참조되는지 확인"""
    filename = os.path.basename(filepath)
    basename = os.path.splitext(filename)[0]
    
    references = []
    search_patterns = [
        filename,  # 전체 파일명
        basename,  # 확장자 없는 이름
        f"from {basename} import",  # Python import
        f"import {basename}",  # Python import
        f'"{filename}"',  # 문자열 참조
        f"'{filename}'",  # 문자열 참조
    ]
    
    # 프로젝트 내 모든 Python 파일 검색
    for root, dirs, files in os.walk(project_root):
        # 백업 폴더는 제외
        dirs[:] = [d for d in dirs if not any(x in d.lower() for x in ['backup', 'venv', '__pycache__', '.git'])]
        
        for file in files:
            if file.endswith(('.py', '.md', '.json', '.txt', '.bat', '.sh')):
                file_path = os.path.join(root, file)
                if file_path == filepath:  # 자기 자신은 제외
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in search_patterns:
                        if pattern in content:
                            references.append({
                                'file': file_path,
                                'pattern': pattern,
                                'type': 'reference'
                            })
                            break
                except Exception:
                    continue
    
    return references

def verify_duplicate_safety(suggestions_file='duplicate_cleanup_suggestions.json'):
    """중복 파일 삭제 안전성 검증"""
    
    if not os.path.exists(suggestions_file):
        print(f"❌ 제안 파일을 찾을 수 없습니다: {suggestions_file}")
        return False
    
    with open(suggestions_file, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)
    
    print("🔍 MACHO-GPT v3.4-mini 중복 파일 삭제 안전성 검증")
    print("=" * 80)
    
    project_root = os.getcwd()
    safety_issues = []
    verified_safe = []
    hash_verification_failed = []
    
    for i, suggestion in enumerate(suggestions, 1):
        keep_file = suggestion['keep']
        delete_files = suggestion['delete']
        
        print(f"\n🔍 그룹 {i}: {os.path.basename(keep_file)}")
        
        # 1. 유지할 파일이 존재하는지 확인
        if not os.path.exists(keep_file):
            safety_issues.append({
                'group': i,
                'issue': 'keep_file_missing',
                'details': f"유지할 파일이 없음: {keep_file}"
            })
            print(f"   ❌ 위험: 유지할 파일이 존재하지 않음")
            continue
        
        keep_hash = calculate_file_hash(keep_file)
        if not keep_hash:
            hash_verification_failed.append({
                'group': i,
                'file': keep_file,
                'reason': 'hash_calculation_failed'
            })
            continue
        
        group_safe = True
        
        # 2. 삭제할 파일들이 정말 동일한지 검증
        for delete_file in delete_files:
            if not os.path.exists(delete_file):
                print(f"   ℹ️ 삭제 대상 파일이 이미 없음: {os.path.basename(delete_file)}")
                continue
            
            delete_hash = calculate_file_hash(delete_file)
            if not delete_hash:
                hash_verification_failed.append({
                    'group': i,
                    'file': delete_file,
                    'reason': 'hash_calculation_failed'
                })
                continue
            
            # 해시 비교
            if keep_hash != delete_hash:
                safety_issues.append({
                    'group': i,
                    'issue': 'hash_mismatch',
                    'details': f"파일 내용이 다름: {delete_file}",
                    'keep_file': keep_file,
                    'delete_file': delete_file
                })
                print(f"   ❌ 위험: 파일 내용이 다름 - {os.path.basename(delete_file)}")
                group_safe = False
            else:
                print(f"   ✅ 해시 일치: {os.path.basename(delete_file)}")
        
        # 3. 삭제할 파일들이 다른 곳에서 참조되는지 확인
        for delete_file in delete_files:
            if not os.path.exists(delete_file):
                continue
            
            references = check_file_references(delete_file, project_root)
            if references:
                safety_issues.append({
                    'group': i,
                    'issue': 'file_referenced',
                    'details': f"다른 파일에서 참조됨: {delete_file}",
                    'references': references[:3]  # 처음 3개만 저장
                })
                print(f"   ⚠️ 주의: {os.path.basename(delete_file)}이(가) {len(references)}곳에서 참조됨")
                group_safe = False
        
        # 4. Python 파일의 경우 import 구조 분석
        if keep_file.endswith('.py'):
            keep_imports = analyze_python_imports(keep_file)
            for delete_file in delete_files:
                if delete_file.endswith('.py') and os.path.exists(delete_file):
                    delete_imports = analyze_python_imports(delete_file)
                    if keep_imports != delete_imports:
                        safety_issues.append({
                            'group': i,
                            'issue': 'import_mismatch',
                            'details': f"Import 구조가 다름: {delete_file}",
                            'keep_imports': keep_imports,
                            'delete_imports': delete_imports
                        })
                        print(f"   ⚠️ 주의: Import 구조가 다를 수 있음 - {os.path.basename(delete_file)}")
        
        if group_safe:
            verified_safe.append(i)
            print(f"   ✅ 안전: 이 그룹은 삭제해도 안전함")
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 안전성 검증 결과")
    print("=" * 80)
    print(f"✅ 안전한 그룹: {len(verified_safe)}개")
    print(f"⚠️ 위험한 그룹: {len(safety_issues)}개")
    print(f"❌ 해시 검증 실패: {len(hash_verification_failed)}개")
    
    if safety_issues:
        print(f"\n⚠️ 발견된 안전성 문제:")
        issue_counts = defaultdict(int)
        for issue in safety_issues:
            issue_counts[issue['issue']] += 1
        
        for issue_type, count in issue_counts.items():
            issue_names = {
                'keep_file_missing': '유지할 파일 없음',
                'hash_mismatch': '파일 내용 불일치',
                'file_referenced': '다른 곳에서 참조됨',
                'import_mismatch': 'Import 구조 다름'
            }
            print(f"   • {issue_names.get(issue_type, issue_type)}: {count}건")
    
    if hash_verification_failed:
        print(f"\n❌ 해시 검증 실패한 파일들:")
        for failed in hash_verification_failed[:10]:  # 처음 10개만 표시
            print(f"   • 그룹 {failed['group']}: {os.path.basename(failed['file'])}")
    
    # 상세 문제 보고서 생성
    if safety_issues or hash_verification_failed:
        report_file = 'safety_verification_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'safety_issues': safety_issues,
                'hash_verification_failed': hash_verification_failed,
                'verified_safe_groups': verified_safe,
                'total_groups': len(suggestions)
            }, f, indent=2, ensure_ascii=False)
        print(f"\n📄 상세 보고서 저장됨: {report_file}")
    
    # 최종 권장사항
    print(f"\n🎯 최종 권장사항:")
    if len(safety_issues) == 0 and len(hash_verification_failed) == 0:
        print("   ✅ 모든 파일이 안전하게 삭제 가능합니다.")
        print("   ✅ python execute_cleanup.py 실행 가능")
        return True
    elif len(safety_issues) <= 5:
        print("   ⚠️ 일부 위험 요소가 있지만 대부분 안전합니다.")
        print("   ⚠️ 문제가 있는 그룹을 제외하고 삭제 권장")
        return False
    else:
        print("   ❌ 많은 안전성 문제가 발견되었습니다.")
        print("   ❌ 수동 검토 후 개별 삭제 권장")
        return False

def create_safe_cleanup_suggestions():
    """안전한 파일들만 포함한 정리 제안 생성"""
    
    # 원본 제안 로드
    with open('duplicate_cleanup_suggestions.json', 'r', encoding='utf-8') as f:
        original_suggestions = json.load(f)
    
    # 안전성 검증 결과 로드
    if os.path.exists('safety_verification_report.json'):
        with open('safety_verification_report.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        safe_groups = set(report['verified_safe_groups'])
        problematic_groups = set()
        
        for issue in report['safety_issues']:
            problematic_groups.add(issue['group'])
        
        # 안전한 그룹만 필터링
        safe_suggestions = []
        for i, suggestion in enumerate(original_suggestions, 1):
            if i in safe_groups and i not in problematic_groups:
                safe_suggestions.append(suggestion)
        
        # 안전한 제안만 저장
        safe_file = 'safe_cleanup_suggestions.json'
        with open(safe_file, 'w', encoding='utf-8') as f:
            json.dump(safe_suggestions, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 안전한 삭제 제안 파일 생성: {safe_file}")
        print(f"   📊 원본: {len(original_suggestions)}개 → 안전: {len(safe_suggestions)}개")
        
        return safe_file
    
    return None

def main():
    """메인 실행 함수"""
    
    print("🚀 MACHO-GPT v3.4-mini 중복 파일 삭제 안전성 검증 시작")
    print("=" * 60)
    
    # 안전성 검증 실행
    is_safe = verify_duplicate_safety()
    
    # 안전한 제안 파일 생성
    if not is_safe:
        safe_file = create_safe_cleanup_suggestions()
        if safe_file:
            print(f"\n🔧 안전한 파일만 삭제하려면:")
            print(f"   python execute_cleanup.py --suggestions-file {safe_file}")
    
    print(f"\n📋 검증 완료. 결과를 검토한 후 삭제를 진행하세요.")

if __name__ == "__main__":
    main() 