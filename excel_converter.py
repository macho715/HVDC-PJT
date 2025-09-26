#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACHO-GPT v3.4-mini - Excel File Converter for ChatGPT
HVDC Project - Samsung C&T Logistics
ADNOC·DSV Partnership

Excel 파일을 ChatGPT가 읽을 수 있는 형태로 변환하는 도구
"""

import pandas as pd
import json
import csv
import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

class ExcelConverter:
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        self.output_formats = ['json', 'csv', 'txt', 'md']
        
    def convert_excel_to_json(self, file_path, output_path=None):
        """Excel 파일을 JSON으로 변환 (모든 날짜/시간 타입 문자열 변환 포함)"""
        import datetime
        try:
            # Excel 파일 읽기
            excel_file = pd.ExcelFile(file_path)
            result = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # 날짜/시간 컬럼을 문자열로 변환 (pandas, python datetime 모두)
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = df[col].astype(str)
                # 모든 셀에서 datetime, date 타입을 문자열로 변환
                df = df.applymap(lambda x: x.isoformat() if isinstance(x, (datetime.datetime, datetime.date)) else x)
                
                # NaN 값을 None으로 변환
                df = df.where(pd.notnull(df), None)
                
                # DataFrame을 딕셔너리로 변환
                sheet_data = {
                    'columns': df.columns.tolist(),
                    'data': df.values.tolist(),
                    'shape': df.shape,
                    'dtypes': df.dtypes.astype(str).to_dict()
                }
                
                result[sheet_name] = sheet_data
            
            if output_path is None:
                output_path = file_path.replace('.xlsx', '.json').replace('.xls', '.json')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return output_path
            
        except Exception as e:
            print(f"JSON 변환 오류: {e}")
            return None
    
    def convert_excel_to_csv(self, file_path, output_path=None):
        """Excel 파일을 CSV로 변환"""
        try:
            excel_file = pd.ExcelFile(file_path)
            
            if len(excel_file.sheet_names) == 1:
                # 단일 시트인 경우
                df = pd.read_excel(file_path)
                if output_path is None:
                    output_path = file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
                
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                return output_path
            else:
                # 다중 시트인 경우
                base_name = Path(file_path).stem
                output_files = []
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheet_output = f"{base_name}_{sheet_name}.csv"
                    df.to_csv(sheet_output, index=False, encoding='utf-8-sig')
                    output_files.append(sheet_output)
                
                return output_files
                
        except Exception as e:
            print(f"CSV 변환 오류: {e}")
            return None
    
    def convert_excel_to_txt(self, file_path, output_path=None):
        """Excel 파일을 텍스트로 변환"""
        try:
            excel_file = pd.ExcelFile(file_path)
            result = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                result.append(f"=== 시트: {sheet_name} ===")
                result.append(f"크기: {df.shape[0]}행 x {df.shape[1]}열")
                result.append("")
                
                # 헤더
                result.append(" | ".join(str(col) for col in df.columns))
                result.append("-" * (len(" | ".join(str(col) for col in df.columns))))
                
                # 데이터
                for _, row in df.iterrows():
                    result.append(" | ".join(str(val) if pd.notna(val) else "" for val in row))
                
                result.append("")
                result.append("=" * 50)
                result.append("")
            
            if output_path is None:
                output_path = file_path.replace('.xlsx', '.txt').replace('.xls', '.txt')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
            
            return output_path
            
        except Exception as e:
            print(f"TXT 변환 오류: {e}")
            return None
    
    def convert_excel_to_markdown(self, file_path, output_path=None):
        """Excel 파일을 Markdown 테이블로 변환"""
        try:
            excel_file = pd.ExcelFile(file_path)
            result = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                result.append(f"# {sheet_name}")
                result.append(f"")
                result.append(f"**크기:** {df.shape[0]}행 x {df.shape[1]}열")
                result.append(f"")
                
                # Markdown 테이블 생성
                if not df.empty:
                    # 헤더
                    result.append("| " + " | ".join(str(col) for col in df.columns) + " |")
                    result.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
                    
                    # 데이터
                    for _, row in df.iterrows():
                        result.append("| " + " | ".join(str(val) if pd.notna(val) else "" for val in row) + " |")
                
                result.append("")
                result.append("---")
                result.append("")
            
            if output_path is None:
                output_path = file_path.replace('.xlsx', '.md').replace('.xls', '.md')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
            
            return output_path
            
        except Exception as e:
            print(f"Markdown 변환 오류: {e}")
            return None
    
    def convert_excel_to_summary(self, file_path, output_path=None):
        """Excel 파일을 요약 정보로 변환"""
        try:
            excel_file = pd.ExcelFile(file_path)
            result = []
            
            result.append(f"# Excel 파일 분석 요약")
            result.append(f"**파일명:** {Path(file_path).name}")
            result.append(f"**변환 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            result.append(f"**총 시트 수:** {len(excel_file.sheet_names)}")
            result.append(f"")
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                result.append(f"## 시트: {sheet_name}")
                result.append(f"- **크기:** {df.shape[0]}행 x {df.shape[1]}열")
                result.append(f"- **컬럼:** {', '.join(str(col) for col in df.columns)}")
                
                # 데이터 타입 정보
                dtypes_info = df.dtypes.value_counts()
                result.append(f"- **데이터 타입:**")
                for dtype, count in dtypes_info.items():
                    result.append(f"  - {dtype}: {count}개 컬럼")
                
                # 샘플 데이터 (처음 5행)
                if not df.empty:
                    result.append(f"- **샘플 데이터 (처음 5행):**")
                    result.append(f"```")
                    result.append(df.head().to_string())
                    result.append(f"```")
                
                result.append(f"")
            
            if output_path is None:
                output_path = file_path.replace('.xlsx', '_summary.md').replace('.xls', '_summary.md')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
            
            return output_path
            
        except Exception as e:
            print(f"요약 변환 오류: {e}")
            return None
    
    def convert_all_formats(self, file_path, output_dir=None):
        """모든 형식으로 변환"""
        if output_dir is None:
            output_dir = Path(file_path).parent
        
        results = {}
        
        # JSON 변환
        json_path = self.convert_excel_to_json(file_path, 
                                             os.path.join(output_dir, f"{Path(file_path).stem}.json"))
        if json_path:
            results['json'] = json_path
        
        # CSV 변환
        csv_result = self.convert_excel_to_csv(file_path)
        if csv_result:
            if isinstance(csv_result, list):
                results['csv'] = csv_result
            else:
                results['csv'] = [csv_result]
        
        # TXT 변환
        txt_path = self.convert_excel_to_txt(file_path, 
                                           os.path.join(output_dir, f"{Path(file_path).stem}.txt"))
        if txt_path:
            results['txt'] = txt_path
        
        # Markdown 변환
        md_path = self.convert_excel_to_markdown(file_path, 
                                               os.path.join(output_dir, f"{Path(file_path).stem}.md"))
        if md_path:
            results['markdown'] = md_path
        
        # 요약 변환
        summary_path = self.convert_excel_to_summary(file_path, 
                                                   os.path.join(output_dir, f"{Path(file_path).stem}_summary.md"))
        if summary_path:
            results['summary'] = summary_path
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Excel 파일을 ChatGPT가 읽을 수 있는 형태로 변환')
    parser.add_argument('file_path', nargs='?', help='변환할 Excel 파일 경로')
    parser.add_argument('-o', '--output', help='출력 디렉토리')
    parser.add_argument('-f', '--format', choices=['json', 'csv', 'txt', 'md', 'summary', 'all'], 
                       default='all', help='출력 형식')
    parser.add_argument('--list-formats', action='store_true', help='지원되는 형식 목록 출력')
    
    args = parser.parse_args()
    
    converter = ExcelConverter()
    
    if args.list_formats:
        print("지원되는 입력 형식:", converter.supported_formats)
        print("지원되는 출력 형식:", converter.output_formats)
        return
    
    if not hasattr(args, 'file_path') or args.file_path is None:
        print("사용법: python excel_converter.py [파일경로] [옵션]")
        print("도움말: python excel_converter.py -h")
        return
    
    if not os.path.exists(args.file_path):
        print(f"오류: 파일을 찾을 수 없습니다 - {args.file_path}")
        return
    
    file_ext = Path(args.file_path).suffix.lower()
    if file_ext not in converter.supported_formats:
        print(f"오류: 지원되지 않는 파일 형식입니다 - {file_ext}")
        print(f"지원되는 형식: {converter.supported_formats}")
        return
    
    print(f"=== MACHO-GPT Excel Converter ===")
    print(f"파일: {args.file_path}")
    print(f"형식: {args.format}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 40)
    
    try:
        if args.format == 'all':
            results = converter.convert_all_formats(args.file_path, args.output)
            print(f"\n변환 완료!")
            for format_type, paths in results.items():
                if isinstance(paths, list):
                    print(f"- {format_type.upper()}: {len(paths)}개 파일")
                    for path in paths:
                        print(f"  - {path}")
                else:
                    print(f"- {format_type.upper()}: {paths}")
        else:
            if args.format == 'json':
                result = converter.convert_excel_to_json(args.file_path, args.output)
            elif args.format == 'csv':
                result = converter.convert_excel_to_csv(args.file_path, args.output)
            elif args.format == 'txt':
                result = converter.convert_excel_to_txt(args.file_path, args.output)
            elif args.format == 'md':
                result = converter.convert_excel_to_markdown(args.file_path, args.output)
            elif args.format == 'summary':
                result = converter.convert_excel_to_summary(args.file_path, args.output)
            
            if result:
                print(f"\n변환 완료: {result}")
            else:
                print(f"\n변환 실패")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main() 