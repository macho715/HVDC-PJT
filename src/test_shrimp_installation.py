"""
Shrimp Task Manager 설치 테스트 스크립트
HVDC 프로젝트용 MACHO-GPT 통합 시스템 검증
"""

import sys
import os
import sqlite3
from datetime import datetime


def test_imports():
    """모듈 import 테스트"""
    print("🔍 모듈 import 테스트...")

    try:
        from shrimp_task_manager import ShrimpTaskManager

        print("✅ ShrimpTaskManager import 성공")
    except ImportError as e:
        print(f"❌ ShrimpTaskManager import 실패: {e}")
        return False

    try:
        from macho_gpt import LogiMaster, ContainerStow, WeatherTie, mode_manager

        print("✅ MACHO-GPT 클래스들 import 성공")
    except ImportError as e:
        print(f"❌ MACHO-GPT 클래스들 import 실패: {e}")
        return False

    return True


def test_database():
    """데이터베이스 테스트"""
    print("\n🗄️ 데이터베이스 테스트...")

    try:
        from shrimp_task_manager import ShrimpTaskManager

        task_manager = ShrimpTaskManager()
        print("✅ TaskManager 초기화 성공")

        # 데이터베이스 파일 존재 확인
        if os.path.exists("hvdc_tasks.db"):
            print("✅ 데이터베이스 파일 생성 확인")
        else:
            print("❌ 데이터베이스 파일이 생성되지 않음")
            return False

        # 테이블 구조 확인
        conn = sqlite3.connect("hvdc_tasks.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ["tasks", "kpi_metrics", "project_settings"]
        for table in required_tables:
            if table in tables:
                print(f"✅ {table} 테이블 존재 확인")
            else:
                print(f"❌ {table} 테이블이 없음")
                return False

        conn.close()
        return True

    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")
        return False


def test_task_operations():
    """작업 관리 기능 테스트"""
    print("\n📝 작업 관리 기능 테스트...")

    try:
        from shrimp_task_manager import ShrimpTaskManager

        task_manager = ShrimpTaskManager()

        # 작업 생성 테스트
        test_task = task_manager.create_task(
            {
                "title": "설치 테스트 작업",
                "description": "Shrimp Task Manager 설치 검증용",
                "priority": "high",
                "category": "analysis",
                "assignee": "Test User",
                "tags": ["test", "installation", "verification"],
            }
        )

        print(f"✅ 작업 생성 성공: {test_task['title']}")

        # 작업 조회 테스트
        tasks = task_manager.list_tasks()
        if len(tasks) > 0:
            print(f"✅ 작업 조회 성공: {len(tasks)}개 작업")
        else:
            print("❌ 작업 조회 실패")
            return False

        # 작업 업데이트 테스트
        updated_task = task_manager.update_task(
            test_task["id"], {"status": "completed", "confidence": 0.95}
        )

        if updated_task and updated_task["status"] == "completed":
            print("✅ 작업 업데이트 성공")
        else:
            print("❌ 작업 업데이트 실패")
            return False

        # 분석 데이터 테스트
        analytics = task_manager.get_task_analytics()
        if analytics and "total_tasks" in analytics:
            print(f"✅ 분석 데이터 생성 성공: {analytics['total_tasks']}개 작업")
        else:
            print("❌ 분석 데이터 생성 실패")
            return False

        # 테스트 작업 삭제
        task_manager.delete_task(test_task["id"])
        print("✅ 테스트 작업 삭제 성공")

        return True

    except Exception as e:
        print(f"❌ 작업 관리 테스트 실패: {e}")
        return False


def test_macho_gpt_integration():
    """MACHO-GPT 통합 테스트"""
    print("\n🤖 MACHO-GPT 통합 테스트...")

    try:
        from macho_gpt import LogiMaster, ContainerStow, WeatherTie, mode_manager

        # 모드 매니저 테스트
        current_mode = mode_manager.get_current_mode()
        print(f"✅ 현재 모드: {current_mode}")

        # 모드 전환 테스트
        result = mode_manager.switch_mode("LATTICE")
        if result["status"] == "SUCCESS":
            print(
                f"✅ 모드 전환 성공: {result['previous_mode']} → {result['current_mode']}"
            )
        else:
            print(f"❌ 모드 전환 실패: {result.get('error', 'Unknown error')}")
            return False

        # LogiMaster 테스트
        logi_master = LogiMaster()
        kpi_result = logi_master.generate_kpi_dash()
        if kpi_result["status"] == "SUCCESS":
            print("✅ LogiMaster KPI 생성 성공")
        else:
            print(
                f"❌ LogiMaster KPI 생성 실패: {kpi_result.get('error', 'Unknown error')}"
            )
            return False

        # ContainerStow 테스트
        container_stow = ContainerStow()
        test_containers = [{"weight": 2000}, {"weight": 1500}]
        stow_result = container_stow.heat_stow_analysis(test_containers)
        if stow_result["status"] == "SUCCESS":
            print("✅ ContainerStow Heat-Stow 분석 성공")
        else:
            print(
                f"❌ ContainerStow 분석 실패: {stow_result.get('error', 'Unknown error')}"
            )
            return False

        # WeatherTie 테스트
        weather_tie = WeatherTie()
        weather_result = weather_tie.check_weather_conditions("AEJEA")
        if weather_result["status"] == "SUCCESS":
            print("✅ WeatherTie 날씨 확인 성공")
        else:
            print(
                f"❌ WeatherTie 날씨 확인 실패: {weather_result.get('error', 'Unknown error')}"
            )
            return False

        # 모드를 PRIME으로 복원
        mode_manager.switch_mode("PRIME")
        print("✅ 모드를 PRIME으로 복원")

        return True

    except Exception as e:
        print(f"❌ MACHO-GPT 통합 테스트 실패: {e}")
        return False


def test_task_manager_integration():
    """Task Manager와 MACHO-GPT 통합 테스트"""
    print("\n🔗 Task Manager 통합 테스트...")

    try:
        from shrimp_task_manager import ShrimpTaskManager

        task_manager = ShrimpTaskManager()

        # 통합 테스트용 작업 생성
        integration_task = task_manager.create_task(
            {
                "title": "MACHO-GPT 통합 테스트",
                "description": "Task Manager와 MACHO-GPT 통합 검증",
                "priority": "critical",
                "category": "logistics",
                "assignee": "MACHO-GPT",
                "tags": ["integration", "test", "macho-gpt"],
            }
        )

        # MACHO-GPT 통합 실행
        integration_result = task_manager.integrate_with_macho_gpt(
            integration_task["id"]
        )

        if "macho_integration" in integration_result:
            macho_data = integration_result["macho_integration"]
            print(f"✅ MACHO-GPT 통합 성공:")
            print(f"   - 권장 모드: {macho_data['mode']}")
            print(f"   - 신뢰도: {macho_data['confidence']}")
            print(f"   - 추천 명령어: {len(macho_data['recommended_commands'])}개")
        else:
            print(
                f"❌ MACHO-GPT 통합 실패: {integration_result.get('error', 'Unknown error')}"
            )
            return False

        # 테스트 작업 삭제
        task_manager.delete_task(integration_task["id"])
        print("✅ 통합 테스트 작업 삭제")

        return True

    except Exception as e:
        print(f"❌ Task Manager 통합 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🦐 Shrimp Task Manager 설치 테스트")
    print("=" * 50)
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        ("모듈 Import", test_imports),
        ("데이터베이스", test_database),
        ("작업 관리", test_task_operations),
        ("MACHO-GPT 통합", test_macho_gpt_integration),
        ("Task Manager 통합", test_task_manager_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과\n")
            else:
                print(f"❌ {test_name} 테스트 실패\n")
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}\n")

    print("=" * 50)
    print(f"테스트 완료: {passed}/{total} 통과")

    if passed == total:
        print("🎉 모든 테스트 통과! Shrimp Task Manager가 성공적으로 설치되었습니다.")
        print("\n📋 다음 단계:")
        print("1. Cursor IDE에서 MCP 서버 설정")
        print("2. '/task_manager list_tasks' 명령어로 작업 조회")
        print("3. '/macho_gpt switch_mode PRIME' 명령어로 모드 설정")
        print("4. SHRIMP_TASK_MANAGER_INSTALLATION_GUIDE.md 참조")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 설치 가이드를 확인하세요.")
        print("📖 SHRIMP_TASK_MANAGER_INSTALLATION_GUIDE.md 참조")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
