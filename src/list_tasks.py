#!/usr/bin/env python3
"""
모든 작업 목록 조회 스크립트
"""

from shrimp_task_manager import ShrimpTaskManager


def main():
    print("📋 모든 작업 목록")
    print("=" * 60)

    # Task Manager 초기화
    task_manager = ShrimpTaskManager()

    # 모든 작업 가져오기
    tasks = task_manager.list_tasks()

    if not tasks:
        print("작업이 없습니다.")
        return

    # 각 작업 상세 정보 출력
    for i, task in enumerate(tasks, 1):
        print(f"🔹 작업 #{i}")
        print(f"ID: {task['id']}")
        print(f"제목: {task['title']}")
        print(f"설명: {task['description']}")
        print(
            f"상태: {task['status']} | 우선순위: {task['priority']} | 카테고리: {task['category']}"
        )
        print(
            f"담당자: {task['assignee']} | 신뢰도: {task['confidence']} | 모드: {task['mode']}"
        )
        print(f"태그: {', '.join(task['tags']) if task['tags'] else '없음'}")
        print(f"생성일: {task['created_at']}")
        if task["due_date"]:
            print(f"마감일: {task['due_date']}")
        print("-" * 60)

    print(f"\n총 {len(tasks)}개의 작업이 있습니다.")
    print("\n🎯 추천 명령어:")
    print("/task_manager get_analytics - 작업 분석")
    print("/macho_gpt switch_mode LATTICE - 창고 최적화 모드")
    print("/task_manager create_task - 새 작업 생성")


if __name__ == "__main__":
    main()
