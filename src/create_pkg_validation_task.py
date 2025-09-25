"""
PKG 수량 검증 태스크 생성 스크립트
HVDC 프로젝트 TDD 개발을 위한 Shrimp Task Manager 활용
"""

from shrimp_task_manager import ShrimpTaskManager
import json

def create_pkg_validation_task():
    """PKG 수량 검증 태스크 생성"""
    
    # Shrimp Task Manager 초기화
    task_manager = ShrimpTaskManager()
    
    # PKG 수량 검증 태스크 데이터
    pkg_task_data = {
        'title': 'PKG 수량 검증 시스템',
        'description': '''
HVDC 프로젝트 PKG 수량 검증 시스템 TDD 개발

목표:
- 송장, 창고 입출고, 현장 데이터의 PKG 수량 일치 여부 자동 검증
- 불일치 시 상세 리포트 및 알림 생성
- 신뢰도 ≥0.95 보장

TDD 개발 단계:
1. PKG 수량 집계 테스트 (송장 vs 창고)
2. 불일치 탐지 테스트
3. 리포트 생성 테스트
4. 알림 시스템 테스트
5. 성능 최적화 테스트

기술 스택:
- Python, pandas, SQLite
- MACHO-GPT 통합
- Shrimp Task Manager 연동
        ''',
        'priority': 'critical',
        'category': 'warehouse',
        'assignee': 'MACHO-GPT',
        'tags': ['PKG', '수량검증', 'TDD', '자동화', 'HVDC'],
        'dependencies': [],
        'kpi_metrics': {
            'target_accuracy': 0.95,
            'processing_time_limit': 30,  # seconds
            'data_volume_threshold': 10000,  # records
            'compliance_score': 0.98
        }
    }
    
    # 태스크 생성
    task = task_manager.create_task(pkg_task_data)
    
    print("🦐 PKG 수량 검증 태스크 생성 완료!")
    print("=" * 60)
    print(f"📋 태스크 ID: {task['id']}")
    print(f"📝 제목: {task['title']}")
    print(f"🏷️  카테고리: {task['category']}")
    print(f"⚡ 우선순위: {task['priority']}")
    print(f"👤 담당자: {task['assignee']}")
    print(f"🏷️  태그: {', '.join(task['tags'])}")
    print(f"📊 상태: {task['status']}")
    print(f"🎯 신뢰도: {task['confidence']}")
    print(f"🔧 모드: {task['mode']}")
    
    # MACHO-GPT 통합
    print("\n🔗 MACHO-GPT 통합 중...")
    integration = task_manager.integrate_with_macho_gpt(task['id'])
    
    print(f"✅ 통합 완료!")
    print(f"🎯 추천 모드: {integration['macho_integration']['mode']}")
    print(f"📈 신뢰도: {integration['macho_integration']['confidence']}")
    print(f"💡 추천 명령어:")
    for cmd in integration['macho_integration']['recommended_commands']:
        print(f"   - {cmd}")
    
    # 다음 단계 안내
    print("\n📋 다음 TDD 단계:")
    print("1. tests/test_pkg_validation.py 작성")
    print("2. pytest로 실패 테스트 확인 (Red)")
    print("3. src/pkg_validation.py 최소 구현")
    print("4. 테스트 통과 확인 (Green)")
    print("5. 리팩터링 및 구조 개선")
    
    print("\n🔧 추천 명령어:")
    print("/test-scenario unit-tests - 전체 테스트 상태 확인")
    print("/automate test-pipeline - 테스트 자동화 실행")
    print(f"/task_manager get_task {task['id']} - 태스크 상세 조회")
    print(f"/task_manager update_task {task['id']} - 태스크 상태 업데이트")
    
    return task

if __name__ == "__main__":
    create_pkg_validation_task() 