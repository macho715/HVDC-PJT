import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def analyze_excel_structure(file_path):
    """Excel 파일의 구조(시트, 컬럼, 샘플 데이터)를 분석하고 출력합니다."""
    
    print(f"📄 파일 분석 시작: {os.path.basename(file_path)}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return

    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        print(f"📊 총 {len(sheet_names)}개의 시트 발견:")
        for sheet_name in sheet_names:
            print(f"  - {sheet_name}")
            
        print("\n" + "=" * 60)
        
        for sheet_name in sheet_names:
            print(f"\n📋 시트명: '{sheet_name}'")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"  - 데이터 행/열: {df.shape}")
            print(f"  - 컬럼 목록: {df.columns.tolist()}")
            print("  - 상위 5개 데이터 샘플:")
            print(df.head().to_string())
            
    except Exception as e:
        print(f"❌ 파일 분석 중 오류 발생: {e}")

def perform_eda(file_path):
    """메인 트랜잭션 시트에 대한 탐색적 데이터 분석(EDA)을 수행합니다."""
    
    print("\n" + "=" * 60)
    print("📊 메인 트랜잭션 탐색적 데이터 분석(EDA) 시작")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return
        
    try:
        df = pd.read_excel(file_path, sheet_name='메인_트랜잭션_SQM_STACK')
        
        # 1. 숫자형 데이터 요약 통계
        print("\n1️⃣  주요 숫자 컬럼 요약 통계:")
        numeric_cols = ['CBM', 'SQM', 'N.W(kgs)', 'G.W(kgs)']
        # 존재하는 컬럼만 선택
        existing_numeric_cols = [col for col in numeric_cols if col in df.columns]
        if existing_numeric_cols:
            print(df[existing_numeric_cols].describe().to_string())
        else:
            print("  - 요약할 숫자 컬럼이 없습니다.")

        # 2. 범주형 데이터 분석
        print("\n2️⃣  주요 범주형 컬럼 분포:")
        
        # Site별 분포
        if 'Site' in df.columns:
            print("\n  - 현장(Site)별 데이터 건수:")
            print(df['Site'].value_counts().to_string())
        
        # VENDOR별 분포
        if 'VENDOR' in df.columns:
            print("\n  - 공급사(VENDOR)별 데이터 건수:")
            print(df['VENDOR'].value_counts().to_string())
            
        # FLOW_PATTERN별 분포
        if 'FLOW_PATTERN' in df.columns:
            print("\n  - 물류 흐름(FLOW_PATTERN)별 데이터 건수:")
            print(df['FLOW_PATTERN'].value_counts().to_string())

    except Exception as e:
        print(f"❌ EDA 수행 중 오류 발생: {e}")

def visualize_data(file_path, output_dir):
    """주요 데이터를 시각화하고 이미지 파일로 저장합니다."""
    
    print("\n" + "=" * 60)
    print("🎨 데이터 시각화 시작")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return

    try:
        # 시각화 스타일 설정
        sns.set(style="whitegrid", font="Malgun Gothic")
        plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지

        # 1. 현장별 요약 통계 시각화 (막대그래프)
        df_site_summary = pd.read_excel(file_path, sheet_name='현장별_요약통계')
        
        plt.figure(figsize=(12, 7))
        sns.barplot(x='현장', y='총 처리량', data=df_site_summary.sort_values('총 처리량', ascending=False), palette='viridis')
        plt.title('현장별 총 처리량', fontsize=16)
        plt.xlabel('현장', fontsize=12)
        plt.ylabel('총 처리량', fontsize=12)
        
        chart_path1 = os.path.join(output_dir, '현장별_총_처리량_막대그래프.png')
        plt.savefig(chart_path1)
        plt.close()
        print(f"  - ✅ 현장별 총 처리량 막대그래프 저장 완료: {os.path.basename(chart_path1)}")

        # 2. 월별 입고 추이 시각화 (선 그래프)
        df_site_monthly = pd.read_excel(file_path, sheet_name='현장별_월별_입출고')
        df_site_monthly['총 입고'] = df_site_monthly[['DAS 입고', 'AGI 입고', 'SHU 입고', 'MIR 입고']].sum(axis=1)
        
        plt.figure(figsize=(16, 8))
        plt.plot(df_site_monthly['구분'], df_site_monthly['총 입고'], marker='o', linestyle='-', color='dodgerblue')
        plt.title('전체 현장 월별 총 입고량 추이', fontsize=16)
        plt.xlabel('월', fontsize=12)
        plt.ylabel('총 입고량', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        
        chart_path2 = os.path.join(output_dir, '월별_총_입고량_추이_선그래프.png')
        plt.savefig(chart_path2)
        plt.close()
        print(f"  - ✅ 월별 총 입고량 추이 선그래프 저장 완료: {os.path.basename(chart_path2)}")

    except Exception as e:
        print(f"❌ 시각화 중 오류 발생: {e}")

def generate_report(file_path, report_dir):
    """분석 결과를 종합하여 마크다운 리포트를 생성합니다."""
    
    print("\n" + "=" * 60)
    print("📝 분석 결과 요약 리포트 생성 시작")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return

    try:
        xls = pd.ExcelFile(file_path)
        
        # 데이터 다시 읽기
        df_main = pd.read_excel(xls, sheet_name='메인_트랜잭션_SQM_STACK')
        df_site_summary = pd.read_excel(xls, sheet_name='현장별_요약통계')

        # 리포트 내용 구성
        report_content = f"""
# MACHO 통합 데이터 분석 리포트

**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**분석 대상 파일**: `{os.path.basename(file_path)}`

---

## 1. 개요
이 리포트는 MACHO 시스템에서 통합된 물류 데이터를 분석하여 주요 현황과 패턴을 파악하는 것을 목적으로 합니다. 데이터 구조 분석, 탐색적 데이터 분석(EDA), 시각화를 통해 핵심 인사이트를 도출합니다.

---

## 2. 데이터 구조 요약
- **총 {len(xls.sheet_names)}개 시트**가 발견되었습니다.
- **주요 시트**:
    - `메인_트랜잭션_SQM_STACK`: 총 **{df_main.shape[0]}** 건의 상세 트랜잭션 데이터
    - `현장별_요약통계`: **{df_site_summary.shape[0]}개 현장**에 대한 요약 통계

---

## 3. 탐색적 데이터 분석(EDA) 결과

### 주요 숫자 데이터 요약 (SQM 기준)
```
{df_main['SQM'].describe().to_string()}
```

### 주요 범주형 데이터 분포
- **현장(Site)별 데이터 건수**:
```
{df_main['Site'].value_counts().to_string()}
```
- **공급사(VENDOR)별 데이터 건수**:
```
{df_main['VENDOR'].value_counts().to_string()}
```
- **물류 흐름(FLOW_PATTERN)별 데이터 건수**:
```
{df_main['FLOW_PATTERN'].value_counts().to_string()}
```

---

## 4. 시각화 분석

### 현장별 총 처리량
![현장별 총 처리량](현장별_총_처리량_막대그래프.png)
*`SHU`와 `MIR` 현장이 가장 많은 물동량을 처리하고 있으며, `DAS`와 `AGI`가 그 뒤를 잇고 있습니다.*

### 전체 현장 월별 총 입고량 추이
![월별 총 입고량 추이](월별_총_입고량_추이_선그래프.png)
*월별 입고량은 변동성이 있으며, 특정 월에 급증하는 패턴을 보입니다. 이는 프로젝트 일정이나 계절적 요인과 관련이 있을 수 있습니다.*

---

## 5. 결론 및 제언
- **주요 공급사**: `HITACHI`가 핵심 공급사입니다.
- **주요 현장**: `SHU`, `MIR` 현장의 물동량 관리가 중요합니다. (`DAS`와 `Das`는 데이터 정제 후 재분석 필요)
- **주요 물류 흐름**: '항구 → 창고1 → 현장'이 가장 일반적인 패턴으로, 창고 운영 효율성이 전체 물류에 큰 영향을 미칩니다.
- **향후 분석 제안**:
    - `DAS`/`Das`와 같이 대소문자가 다른 데이터를 통일하여 분석 정확도 향상
    - 특정 월에 입고량이 급증하는 원인 심층 분석
    - 화물 크기(`SQM`)와 물류 흐름 간의 상관관계 분석
"""
        report_path = os.path.join(report_dir, 'MACHO_분석_리포트.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f"  - ✅ 분석 리포트 저장 완료: {os.path.basename(report_path)}")

    except Exception as e:
        print(f"❌ 리포트 생성 중 오류 발생: {e}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    target_dir = os.path.join(base_dir, '02_통합결과')
    report_dir = os.path.join(base_dir, '04_작업리포트') # 리포트 저장 경로 추가

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        
    files = [f for f in os.listdir(target_dir) if f.endswith('.xlsx') and 'MACHO_완전통합' in f and not f.startswith('~$')]
    
    if not files:
        print("분석할 통합 파일을 찾을 수 없습니다.")
    else:
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(target_dir, f)))
        file_to_analyze = os.path.join(target_dir, latest_file)
        
        analyze_excel_structure(file_to_analyze)
        perform_eda(file_to_analyze)
        visualize_data(file_to_analyze, report_dir)
        generate_report(file_to_analyze, report_dir) # 리포트 생성 함수 호출 