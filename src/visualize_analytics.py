#!/usr/bin/env python3
"""
작업 분석 데이터 시각화 스크립트
"""

from shrimp_task_manager import ShrimpTaskManager

def main():
    print("📊 작업 분석 리포트")
    print("=" * 50)
    
    # Task Manager 초기화
    task_manager = ShrimpTaskManager()
    
    # 분석 데이터 가져오기
    analytics = task_manager.get_task_analytics()
    
    # 기본 통계 출력
    print(f"총 작업 수: {analytics['total_tasks']}")
    print(f"완료된 작업: {analytics['completed_tasks']}")
    print(f"완료율: {analytics['completion_rate']}%")
    print()
    
    # 상태별 분포
    print("📈 상태별 분포:")
    for status, count in analytics['status_distribution'].items():
        percentage = (count / analytics['total_tasks'] * 100) if analytics['total_tasks'] > 0 else 0
        print(f"  {status}: {count}개 ({percentage:.1f}%)")
    print()
    
    # 카테고리별 분포
    print("🏷️ 카테고리별 분포:")
    for category, count in analytics['category_distribution'].items():
        percentage = (count / analytics['total_tasks'] * 100) if analytics['total_tasks'] > 0 else 0
        print(f"  {category}: {count}개 ({percentage:.1f}%)")
    print()
    
    # 우선순위별 분포
    print("⚡ 우선순위별 분포:")
    for priority, count in analytics['priority_distribution'].items():
        percentage = (count / analytics['total_tasks'] * 100) if analytics['total_tasks'] > 0 else 0
        print(f"  {priority}: {count}개 ({percentage:.1f}%)")
    print()
    
    # 최근 작업 목록
    print("🕒 최근 작업 목록:")
    tasks = task_manager.list_tasks()
    for i, task in enumerate(tasks[:5], 1):  # 최근 5개만 표시
        print(f"  {i}. {task['title']} ({task['status']}) - {task['category']}")
    print()
    
    print("=" * 50)
    print("🎯 추천 명령어:")
    print("/task_manager list_tasks - 모든 작업 조회")
    print("/macho_gpt switch_mode LATTICE - 창고 최적화 모드")
    print("/task_manager create_task - 새 작업 생성")

if __name__ == "__main__":
    main() 