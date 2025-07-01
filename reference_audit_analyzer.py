#!/usr/bin/env python3
"""
HVDC Project 참조 관계 상세 분석 도구
MACHO-GPT v3.4-mini │ Samsung C&T Logistics
Reference Audit & Safe Cleanup Strategy
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

class ReferenceAuditor:
    def __init__(self, project_root="."):
        self.project_root = os.path.abspath(project_root)
        self.backup_patterns = [
            'backup', 'bak', 'old', 'archive', 'temp', 'tmp',
            'v2.6_20250626', 'v2.8.1_1751267433', 'Clean_Project_Backup'
        ]
        self.active_directories = []
        self.backup_directories = []
        self.reference_map = defaultdict(list)
        
    def is_backup_path(self, filepath):
        """경로가 백업 디렉토리인지 판단"""
        path_lower = filepath.lower()
        return any(pattern.lower() in path_lower for pattern in self.backup_patterns)
    
    def classify_directories(self):
        """디렉토리를 활성/백업으로 분류"""
        for root, dirs, files in os.walk(self.project_root):
            # 제외할 디렉토리
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]
            
            if self.is_backup_path(root):
                self.backup_directories.append(root)
            else:
                self.active_directories.append(root)
    
    def analyze_file_references(self, target_file, suggestions_data):
        """특정 파일의 참조 관계 분석"""
        filename = os.path.basename(target_file)
        basename = os.path.splitext(filename)[0]
        
        # 검색 패턴 정의
        search_patterns = [
            filename,  # 전체 파일명
            basename,  # 확장자 없는 이름
            f"from {basename} import",  # Python import
            f"import {basename}",  # Python import
            f'"{filename}"',  # 문자열 참조
            f"'{filename}'",  # 문자열 참조
            f"{basename}.",  # 모듈 접근
            f"/{filename}",  # 경로 참조
            f"\\{filename}",  # Windows 경로 참조
        ]
        
        references = {
            'active_references': [],
            'backup_references': [],
            'self_references': [],
            'import_references': [],
            'string_references': [],
            'path_references': []
        }
        
        # 프로젝트 내 모든 파일 검색
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.md', '.json', '.txt', '.bat', '.sh', '.yml', '.yaml')):
                    file_path = os.path.join(root, file)
                    
                    # 자기 자신은 제외
                    if os.path.abspath(file_path) == os.path.abspath(target_file):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        found_patterns = []
                        for pattern in search_patterns:
                            if pattern in content:
                                found_patterns.append(pattern)
                        
                        if found_patterns:
                            ref_info = {
                                'file': file_path,
                                'patterns': found_patterns,
                                'is_backup': self.is_backup_path(file_path),
                                'line_count': self._count_pattern_occurrences(content, found_patterns)
                            }
                            
                            # 참조 유형별 분류
                            if self.is_backup_path(file_path):
                                references['backup_references'].append(ref_info)
                            else:
                                references['active_references'].append(ref_info)
                            
                            # 참조 패턴별 분류
                            for pattern in found_patterns:
                                if 'import' in pattern:
                                    references['import_references'].append(ref_info)
                                elif pattern.startswith('"') or pattern.startswith("'"):
                                    references['string_references'].append(ref_info)
                                elif '/' in pattern or '\\' in pattern:
                                    references['path_references'].append(ref_info)
                    
                    except Exception as e:
                        continue
        
        return references
    
    def _count_pattern_occurrences(self, content, patterns):
        """패턴 발생 횟수 계산"""
        total_count = 0
        for pattern in patterns:
            total_count += content.count(pattern)
        return total_count
    
    def analyze_all_duplicates(self, suggestions_file='duplicate_cleanup_suggestions.json'):
        """모든 중복 파일의 참조 관계 분석"""
        
        if not os.path.exists(suggestions_file):
            print(f"❌ 제안 파일을 찾을 수 없습니다: {suggestions_file}")
            return None
        
        with open(suggestions_file, 'r', encoding='utf-8') as f:
            suggestions = json.load(f)
        
        print("🔍 MACHO-GPT v3.4-mini 참조 관계 상세 분석")
        print("=" * 80)
        
        # 디렉토리 분류
        self.classify_directories()
        
        print(f"📁 활성 디렉토리: {len(self.active_directories)}개")
        print(f"📦 백업 디렉토리: {len(self.backup_directories)}개")
        
        analysis_results = {
            'safe_to_delete': [],
            'risky_to_delete': [],
            'backup_only_references': [],
            'active_references': [],
            'summary': {}
        }
        
        for i, suggestion in enumerate(suggestions, 1):
            keep_file = suggestion['keep']
            delete_files = suggestion['delete']
            
            print(f"\n🔍 그룹 {i}: {os.path.basename(keep_file)}")
            
            group_analysis = {
                'group_id': i,
                'keep_file': keep_file,
                'delete_files': [],
                'safety_level': 'SAFE',  # SAFE, RISKY, DANGEROUS
                'reasons': []
            }
            
            for delete_file in delete_files:
                if not os.path.exists(delete_file):
                    print(f"   ℹ️ 파일 없음: {os.path.basename(delete_file)}")
                    continue
                
                # 참조 분석
                refs = self.analyze_file_references(delete_file, suggestions)
                
                file_analysis = {
                    'file': delete_file,
                    'active_refs': len(refs['active_references']),
                    'backup_refs': len(refs['backup_references']),
                    'import_refs': len(refs['import_references']),
                    'total_refs': len(refs['active_references']) + len(refs['backup_references']),
                    'is_backup_file': self.is_backup_path(delete_file),
                    'safety_assessment': 'SAFE'
                }
                
                # 안전성 평가
                if refs['active_references']:
                    # 활성 참조가 있는 경우
                    active_non_backup = [r for r in refs['active_references'] if not self.is_backup_path(r['file'])]
                    if active_non_backup:
                        file_analysis['safety_assessment'] = 'DANGEROUS'
                        group_analysis['safety_level'] = 'DANGEROUS'
                        group_analysis['reasons'].append(f"{os.path.basename(delete_file)}: 활성 파일에서 {len(active_non_backup)}회 참조")
                        print(f"   ❌ 위험: {os.path.basename(delete_file)} - 활성 참조 {len(active_non_backup)}개")
                    else:
                        file_analysis['safety_assessment'] = 'RISKY'
                        if group_analysis['safety_level'] == 'SAFE':
                            group_analysis['safety_level'] = 'RISKY'
                        group_analysis['reasons'].append(f"{os.path.basename(delete_file)}: 백업 내 참조만 존재")
                        print(f"   ⚠️ 주의: {os.path.basename(delete_file)} - 백업 내 참조만 {len(refs['active_references'])}개")
                else:
                    # 백업 참조만 있거나 참조 없음
                    if refs['backup_references']:
                        print(f"   ✅ 안전: {os.path.basename(delete_file)} - 백업 참조만 {len(refs['backup_references'])}개")
                    else:
                        print(f"   ✅ 안전: {os.path.basename(delete_file)} - 참조 없음")
                
                # 상세 참조 정보 출력
                if refs['active_references']:
                    print(f"      📋 활성 참조 상세:")
                    for ref in refs['active_references'][:3]:  # 처음 3개만
                        rel_path = os.path.relpath(ref['file'], self.project_root)
                        print(f"         • {rel_path} ({ref['line_count']}회)")
                
                group_analysis['delete_files'].append(file_analysis)
            
            # 그룹별 분류
            if group_analysis['safety_level'] == 'SAFE':
                analysis_results['safe_to_delete'].append(group_analysis)
            elif group_analysis['safety_level'] == 'RISKY':
                analysis_results['risky_to_delete'].append(group_analysis)
            else:
                analysis_results['active_references'].append(group_analysis)
            
            print(f"   🎯 그룹 안전도: {group_analysis['safety_level']}")
        
        # 결과 요약
        analysis_results['summary'] = {
            'total_groups': len(suggestions),
            'safe_groups': len(analysis_results['safe_to_delete']),
            'risky_groups': len(analysis_results['risky_to_delete']),
            'dangerous_groups': len(analysis_results['active_references']),
            'backup_directories': len(self.backup_directories),
            'active_directories': len(self.active_directories)
        }
        
        return analysis_results
    
    def generate_safe_cleanup_plan(self, analysis_results):
        """안전한 정리 계획 생성"""
        
        print("\n" + "=" * 80)
        print("📊 참조 분석 결과 요약")
        print("=" * 80)
        
        summary = analysis_results['summary']
        print(f"✅ 안전한 그룹: {summary['safe_groups']}개")
        print(f"⚠️ 주의 그룹: {summary['risky_groups']}개")
        print(f"❌ 위험한 그룹: {summary['dangerous_groups']}개")
        
        # 안전한 삭제 제안 생성
        if analysis_results['safe_to_delete']:
            safe_suggestions = []
            for group in analysis_results['safe_to_delete']:
                # 원본 형식으로 변환
                safe_suggestions.append({
                    'keep': group['keep_file'],
                    'delete': [f['file'] for f in group['delete_files']],
                    'reason': f"안전: 활성 참조 없음"
                })
            
            # 안전한 제안 저장
            with open('safe_cleanup_plan.json', 'w', encoding='utf-8') as f:
                json.dump(safe_suggestions, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ 안전한 삭제 계획 저장: safe_cleanup_plan.json")
            print(f"   📊 안전한 삭제 대상: {len(safe_suggestions)}개 그룹")
        
        # 상세 분석 보고서 저장
        with open('reference_audit_report.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 상세 분석 보고서: reference_audit_report.json")
        
        # 권장사항 출력
        print(f"\n🎯 권장사항:")
        if summary['safe_groups'] > 0:
            print(f"   ✅ {summary['safe_groups']}개 그룹은 안전하게 삭제 가능")
            print(f"   ✅ python execute_cleanup.py --suggestions-file safe_cleanup_plan.json")
        
        if summary['risky_groups'] > 0:
            print(f"   ⚠️ {summary['risky_groups']}개 그룹은 백업 검증 후 삭제")
            print(f"   ⚠️ 백업 폴더가 실제 사용되지 않는지 확인 필요")
        
        if summary['dangerous_groups'] > 0:
            print(f"   ❌ {summary['dangerous_groups']}개 그룹은 삭제 금지")
            print(f"   ❌ 활성 참조가 있어 삭제 시 시스템 오류 발생 가능")
        
        return analysis_results

def main():
    """메인 실행 함수"""
    
    print("🚀 MACHO-GPT v3.4-mini 참조 관계 상세 분석 시작")
    print("=" * 60)
    
    auditor = ReferenceAuditor()
    
    # 전체 중복 파일 분석
    analysis_results = auditor.analyze_all_duplicates()
    
    if analysis_results:
        # 안전한 정리 계획 생성
        auditor.generate_safe_cleanup_plan(analysis_results)
        
        print(f"\n📋 분석 완료. 결과를 확인한 후 안전한 파일만 삭제하세요.")
    else:
        print("❌ 분석 실패. 중복 파일 제안을 먼저 생성하세요.")

if __name__ == "__main__":
    main() 