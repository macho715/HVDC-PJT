#!/usr/bin/env python3
"""
Extract test issues from quality consistency test report
"""

def extract_test_issues():
    try:
        with open('output/validation_reports/quality_consistency_test_report.txt', 'r', encoding='latin-1') as f:
            content = f.read()
        
        lines = content.split('\n')
        issues = []
        
        for line in lines:
            if any(keyword in line.upper() for keyword in ['FAIL', 'WARNING', 'ERROR', 'SKIPPED']):
                issues.append(line.strip())
        
        print("=== TEST ISSUES SUMMARY ===")
        print(f"Total issues found: {len(issues)}")
        print()
        
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
        else:
            print("✅ No issues found - All tests passed!")
            
    except Exception as e:
        print(f"Error reading test report: {e}")

if __name__ == "__main__":
    extract_test_issues() 