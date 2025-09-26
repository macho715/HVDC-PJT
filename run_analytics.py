#!/usr/bin/env python3
"""
Task Manager Analytics Runner
"""

from macho_gpt_integration import ShrimpTaskManager

def main():
    print("=== TASK ANALYTICS & KPI REPORT ===")
    
    # Initialize task manager
    tm = ShrimpTaskManager()
    
    # Get analytics
    analytics = tm.get_task_analytics()
    
    # Display all analytics fields
    for key, value in analytics.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 