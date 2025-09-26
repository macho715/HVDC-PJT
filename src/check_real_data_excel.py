"""
실제 데이터 기반 엑셀 파일 구조 확인 및 요약
"""

import pandas as pd
import os
from datetime import datetime


def check_real_data_excel():
    """실제 데이터 기반 엑셀 파일 확인"""

    # 최신 실제 데이터 파일 찾기
    output_dir = "../output"

    # 모든 엑셀 파일 확인
    all_files = [f for f in os.listdir(output_dir) if f.endswith(".xlsx")]

    print("📊 Output 디렉토리 엑셀 파일 목록:")
    for file in sorted(all_files):
        file_path = os.path.join(output_dir, file)
        file_size = os.path.getsize(file_path) / 1024  # KB
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(
            f"   📄 {file} ({file_size:.1f}KB, {file_time.strftime('%Y-%m-%d %H:%M:%S')})"
        )

    # 실제 데이터 파일 찾기
    real_data_files = [f for f in all_files if "Real_Data" in f or "real" in f.lower()]

    if not real_data_files:
        print("\n❌ 실제 데이터 파일을 찾을 수 없습니다.")
        print("📋 최신 파일을 확인합니다...")

        # 최신 파일 선택
        if all_files:
            latest_file = max(
                all_files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x))
            )
            print(f"📄 최신 파일: {latest_file}")
            check_excel_structure(os.path.join(output_dir, latest_file))
        return

    # 최신 실제 데이터 파일 선택
    latest_real_file = max(
        real_data_files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x))
    )
    real_file_path = os.path.join(output_dir, latest_real_file)

    print(f"\n📊 실제 데이터 파일 분석: {latest_real_file}")
    check_excel_structure(real_file_path)


def check_excel_structure(excel_path):
    """엑셀 파일 구조 확인"""

    print(f"📊 엑셀 파일 분석: {excel_path}")
    print("=" * 60)

    try:
        # 엑셀 파일 읽기
        xl_file = pd.ExcelFile(excel_path)

        print(f"📋 총 시트 수: {len(xl_file.sheet_names)}")
        print(f"📋 시트 목록: {xl_file.sheet_names}")
        print()

        # 각 시트별 분석
        for sheet_name in xl_file.sheet_names:
            print(f"📊 시트: {sheet_name}")
            print("-" * 40)

            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"   📏 크기: {df.shape[0]} 행 × {df.shape[1]} 열")
                print(f"   📋 컬럼: {list(df.columns)[:10]}...")  # 처음 10개만

                # 처음 2행만 출력
                if not df.empty:
                    print("   📄 데이터 샘플:")
                    display_df = df.head(2)
                    for idx, row in display_df.iterrows():
                        row_dict = dict(row)
                        # 너무 긴 값 축약
                        for k, v in row_dict.items():
                            if isinstance(v, str) and len(v) > 50:
                                row_dict[k] = v[:50] + "..."
                        print(f"      Row {idx}: {row_dict}")
                    print()
            except Exception as e:
                print(f"   ❌ 읽기 오류: {str(e)}")
                print()

        print("=" * 60)
        print("✅ 엑셀 파일 분석 완료")

    except Exception as e:
        print(f"❌ 파일 분석 오류: {str(e)}")


if __name__ == "__main__":
    check_real_data_excel()
