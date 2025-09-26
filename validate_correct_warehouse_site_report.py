#!/usr/bin/env python3
"""
MACHO 시스템 올바른 창고/현장 시트 구조 검증 - TDD Refactor Phase
생성된 리포트가 MACHO 시스템의 올바른 구조를 가지고 있는지 검증
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validate_correct_warehouse_site_report.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CorrectWarehouseSiteReportValidator:
    """MACHO 시스템 올바른 창고/현장 시트 구조 검증기"""
    
    def __init__(self, excel_path):
        self.excel_path = excel_path
        logger.info(f"🔍 MACHO 시스템 올바른 창고/현장 시트 구조 검증 시작: {excel_path}")
        
        # 정확한 창고 컬럼 (MACHO 시스템 기준)
        self.correct_warehouse_columns = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 
            'DSV MZP', 'Hauler Indoor', 'MOSB', 'AAA  Storage'
        ]
        
        # 정확한 현장 컬럼 (MACHO 시스템 기준)
        self.correct_site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 검증 결과 저장
        self.validation_results = []
        
    def validate_file_structure(self):
        """파일 구조 검증"""
        try:
            # Excel 파일 로드
            excel_file = pd.ExcelFile(self.excel_path)
            sheet_names = excel_file.sheet_names
            
            # 예상 시트명
            expected_sheets = [
                '전체_트랜잭션_데이터',
                '창고별_월별_입출고',
                '현장별_월별_입고재고',
                '분석_요약'
            ]
            
            # 시트 존재 여부 확인
            for expected_sheet in expected_sheets:
                if expected_sheet in sheet_names:
                    self.validation_results.append({
                        'Category': 'File Structure',
                        'Test': f"시트 '{expected_sheet}' 존재",
                        'Result': 'PASS',
                        'Details': f"시트가 존재합니다"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'File Structure',
                        'Test': f"시트 '{expected_sheet}' 존재",
                        'Result': 'FAIL',
                        'Details': f"시트가 존재하지 않습니다"
                    })
            
            logger.info(f"✅ 파일 구조 검증 완료: {len(sheet_names)}개 시트")
            return excel_file
            
        except Exception as e:
            logger.error(f"❌ 파일 구조 검증 실패: {e}")
            self.validation_results.append({
                'Category': 'File Structure',
                'Test': '파일 로드',
                'Result': 'FAIL',
                'Details': f"파일 로드 실패: {e}"
            })
            return None
    
    def validate_warehouse_multi_level_headers(self, excel_file):
        """창고 시트 Multi-level 헤더 검증"""
        try:
            # 창고 시트 로드
            warehouse_df = pd.read_excel(excel_file, sheet_name='창고별_월별_입출고', header=[0, 1])
            
            # Multi-level 헤더 확인
            if isinstance(warehouse_df.columns, pd.MultiIndex):
                self.validation_results.append({
                    'Category': 'Warehouse Sheet',
                    'Test': 'Multi-level 헤더 구조',
                    'Result': 'PASS',
                    'Details': f"Multi-level 헤더 구조가 올바릅니다"
                })
                
                # 헤더 레벨 확인
                level_0_values = warehouse_df.columns.get_level_values(0).unique().tolist()
                level_1_values = warehouse_df.columns.get_level_values(1).unique().tolist()
                
                # 입고/출고 구분 확인
                if '입고' in level_0_values and '출고' in level_0_values:
                    self.validation_results.append({
                        'Category': 'Warehouse Sheet',
                        'Test': '입고/출고 헤더 구분',
                        'Result': 'PASS',
                        'Details': f"입고/출고 헤더가 올바릅니다: {level_0_values}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Warehouse Sheet',
                        'Test': '입고/출고 헤더 구분',
                        'Result': 'FAIL',
                        'Details': f"입고/출고 헤더가 잘못되었습니다: {level_0_values}"
                    })
                
                # 창고명 확인
                correct_warehouse_count = 0
                for warehouse in self.correct_warehouse_columns:
                    if warehouse in level_1_values:
                        correct_warehouse_count += 1
                
                if correct_warehouse_count == len(self.correct_warehouse_columns):
                    self.validation_results.append({
                        'Category': 'Warehouse Sheet',
                        'Test': '창고명 헤더 확인',
                        'Result': 'PASS',
                        'Details': f"모든 창고명이 올바릅니다: {correct_warehouse_count}/{len(self.correct_warehouse_columns)}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Warehouse Sheet',
                        'Test': '창고명 헤더 확인',
                        'Result': 'FAIL',
                        'Details': f"창고명이 부족합니다: {correct_warehouse_count}/{len(self.correct_warehouse_columns)}"
                    })
                
                # 예상 컬럼 수 확인 (7개 창고 × 2 = 14개)
                expected_columns = len(self.correct_warehouse_columns) * 2
                actual_columns = len(warehouse_df.columns)
                
                if actual_columns == expected_columns:
                    self.validation_results.append({
                        'Category': 'Warehouse Sheet',
                        'Test': '컬럼 수 확인',
                        'Result': 'PASS',
                        'Details': f"컬럼 수가 올바릅니다: {actual_columns}/{expected_columns}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Warehouse Sheet',
                        'Test': '컬럼 수 확인',
                        'Result': 'FAIL',
                        'Details': f"컬럼 수가 잘못되었습니다: {actual_columns}/{expected_columns}"
                    })
                
                logger.info(f"✅ 창고 시트 Multi-level 헤더 검증 완료")
                
            else:
                self.validation_results.append({
                    'Category': 'Warehouse Sheet',
                    'Test': 'Multi-level 헤더 구조',
                    'Result': 'FAIL',
                    'Details': f"Multi-level 헤더가 아닙니다"
                })
                
        except Exception as e:
            logger.error(f"❌ 창고 시트 검증 실패: {e}")
            self.validation_results.append({
                'Category': 'Warehouse Sheet',
                'Test': '창고 시트 검증',
                'Result': 'FAIL',
                'Details': f"창고 시트 검증 실패: {e}"
            })
    
    def validate_site_multi_level_headers(self, excel_file):
        """현장 시트 Multi-level 헤더 검증"""
        try:
            # 현장 시트 로드
            site_df = pd.read_excel(excel_file, sheet_name='현장별_월별_입고재고', header=[0, 1])
            
            # Multi-level 헤더 확인
            if isinstance(site_df.columns, pd.MultiIndex):
                self.validation_results.append({
                    'Category': 'Site Sheet',
                    'Test': 'Multi-level 헤더 구조',
                    'Result': 'PASS',
                    'Details': f"Multi-level 헤더 구조가 올바릅니다"
                })
                
                # 헤더 레벨 확인
                level_0_values = site_df.columns.get_level_values(0).unique().tolist()
                level_1_values = site_df.columns.get_level_values(1).unique().tolist()
                
                # 입고/재고 구분 확인 (출고 없음)
                if '입고' in level_0_values and '재고' in level_0_values and '출고' not in level_0_values:
                    self.validation_results.append({
                        'Category': 'Site Sheet',
                        'Test': '입고/재고 헤더 구분',
                        'Result': 'PASS',
                        'Details': f"입고/재고 헤더가 올바릅니다: {level_0_values}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Site Sheet',
                        'Test': '입고/재고 헤더 구분',
                        'Result': 'FAIL',
                        'Details': f"입고/재고 헤더가 잘못되었습니다: {level_0_values}"
                    })
                
                # 현장명 확인
                correct_site_count = 0
                for site in self.correct_site_columns:
                    if site in level_1_values:
                        correct_site_count += 1
                
                if correct_site_count == len(self.correct_site_columns):
                    self.validation_results.append({
                        'Category': 'Site Sheet',
                        'Test': '현장명 헤더 확인',
                        'Result': 'PASS',
                        'Details': f"모든 현장명이 올바릅니다: {correct_site_count}/{len(self.correct_site_columns)}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Site Sheet',
                        'Test': '현장명 헤더 확인',
                        'Result': 'FAIL',
                        'Details': f"현장명이 부족합니다: {correct_site_count}/{len(self.correct_site_columns)}"
                    })
                
                # 예상 컬럼 수 확인 (4개 현장 × 2 = 8개)
                expected_columns = len(self.correct_site_columns) * 2
                actual_columns = len(site_df.columns)
                
                if actual_columns == expected_columns:
                    self.validation_results.append({
                        'Category': 'Site Sheet',
                        'Test': '컬럼 수 확인',
                        'Result': 'PASS',
                        'Details': f"컬럼 수가 올바릅니다: {actual_columns}/{expected_columns}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Site Sheet',
                        'Test': '컬럼 수 확인',
                        'Result': 'FAIL',
                        'Details': f"컬럼 수가 잘못되었습니다: {actual_columns}/{expected_columns}"
                    })
                
                logger.info(f"✅ 현장 시트 Multi-level 헤더 검증 완료")
                
            else:
                self.validation_results.append({
                    'Category': 'Site Sheet',
                    'Test': 'Multi-level 헤더 구조',
                    'Result': 'FAIL',
                    'Details': f"Multi-level 헤더가 아닙니다"
                })
                
        except Exception as e:
            logger.error(f"❌ 현장 시트 검증 실패: {e}")
            self.validation_results.append({
                'Category': 'Site Sheet',
                'Test': '현장 시트 검증',
                'Result': 'FAIL',
                'Details': f"현장 시트 검증 실패: {e}"
            })
    
    def validate_transaction_data(self, excel_file):
        """트랜잭션 데이터 검증"""
        try:
            # 트랜잭션 데이터 로드
            transaction_df = pd.read_excel(excel_file, sheet_name='전체_트랜잭션_데이터')
            
            # 데이터 건수 확인
            expected_min_count = 7700  # 최소 예상 건수
            actual_count = len(transaction_df)
            
            if actual_count >= expected_min_count:
                self.validation_results.append({
                    'Category': 'Transaction Data',
                    'Test': '데이터 건수 확인',
                    'Result': 'PASS',
                    'Details': f"데이터 건수가 충분합니다: {actual_count:,}건 >= {expected_min_count:,}건"
                })
            else:
                self.validation_results.append({
                    'Category': 'Transaction Data',
                    'Test': '데이터 건수 확인',
                    'Result': 'FAIL',
                    'Details': f"데이터 건수가 부족합니다: {actual_count:,}건 < {expected_min_count:,}건"
                })
            
            # Flow Code 컬럼 확인
            if 'FLOW_CODE' in transaction_df.columns:
                flow_codes = transaction_df['FLOW_CODE'].unique()
                expected_codes = [1, 2, 3]  # Pre Arrival 제외
                
                if all(code in flow_codes for code in expected_codes):
                    self.validation_results.append({
                        'Category': 'Transaction Data',
                        'Test': 'Flow Code 존재',
                        'Result': 'PASS',
                        'Details': f"Flow Code가 올바릅니다: {sorted(flow_codes)}"
                    })
                else:
                    self.validation_results.append({
                        'Category': 'Transaction Data',
                        'Test': 'Flow Code 존재',
                        'Result': 'FAIL',
                        'Details': f"Flow Code가 부족합니다: {sorted(flow_codes)}"
                    })
            else:
                self.validation_results.append({
                    'Category': 'Transaction Data',
                    'Test': 'Flow Code 컬럼',
                    'Result': 'FAIL',
                    'Details': f"FLOW_CODE 컬럼이 없습니다"
                })
            
            logger.info(f"✅ 트랜잭션 데이터 검증 완료: {actual_count:,}건")
            
        except Exception as e:
            logger.error(f"❌ 트랜잭션 데이터 검증 실패: {e}")
            self.validation_results.append({
                'Category': 'Transaction Data',
                'Test': '트랜잭션 데이터 검증',
                'Result': 'FAIL',
                'Details': f"트랜잭션 데이터 검증 실패: {e}"
            })
    
    def validate_monthly_data_structure(self, excel_file):
        """월별 데이터 구조 검증"""
        try:
            # 창고 월별 데이터 검증
            warehouse_df = pd.read_excel(excel_file, sheet_name='창고별_월별_입출고', header=[0, 1])
            
            # 12개월 데이터 확인
            expected_months = 12
            actual_months = len(warehouse_df)
            
            if actual_months == expected_months:
                self.validation_results.append({
                    'Category': 'Monthly Data',
                    'Test': '창고 월별 데이터 행 수',
                    'Result': 'PASS',
                    'Details': f"12개월 데이터가 올바릅니다: {actual_months}개월"
                })
            else:
                self.validation_results.append({
                    'Category': 'Monthly Data',
                    'Test': '창고 월별 데이터 행 수',
                    'Result': 'FAIL',
                    'Details': f"12개월 데이터가 아닙니다: {actual_months}개월"
                })
            
            # 현장 월별 데이터 검증
            site_df = pd.read_excel(excel_file, sheet_name='현장별_월별_입고재고', header=[0, 1])
            
            actual_site_months = len(site_df)
            if actual_site_months == expected_months:
                self.validation_results.append({
                    'Category': 'Monthly Data',
                    'Test': '현장 월별 데이터 행 수',
                    'Result': 'PASS',
                    'Details': f"12개월 데이터가 올바릅니다: {actual_site_months}개월"
                })
            else:
                self.validation_results.append({
                    'Category': 'Monthly Data',
                    'Test': '현장 월별 데이터 행 수',
                    'Result': 'FAIL',
                    'Details': f"12개월 데이터가 아닙니다: {actual_site_months}개월"
                })
            
            logger.info(f"✅ 월별 데이터 구조 검증 완료")
            
        except Exception as e:
            logger.error(f"❌ 월별 데이터 구조 검증 실패: {e}")
            self.validation_results.append({
                'Category': 'Monthly Data',
                'Test': '월별 데이터 구조 검증',
                'Result': 'FAIL',
                'Details': f"월별 데이터 구조 검증 실패: {e}"
            })
    
    def run_full_validation(self):
        """전체 검증 실행"""
        try:
            # 1. 파일 구조 검증
            excel_file = self.validate_file_structure()
            if excel_file is None:
                return False
            
            # 2. 창고 시트 검증
            self.validate_warehouse_multi_level_headers(excel_file)
            
            # 3. 현장 시트 검증
            self.validate_site_multi_level_headers(excel_file)
            
            # 4. 트랜잭션 데이터 검증
            self.validate_transaction_data(excel_file)
            
            # 5. 월별 데이터 구조 검증
            self.validate_monthly_data_structure(excel_file)
            
            # 6. 결과 요약
            self.generate_validation_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 전체 검증 실행 실패: {e}")
            return False
    
    def generate_validation_report(self):
        """검증 결과 리포트 생성"""
        # 검증 결과 분석
        total_tests = len(self.validation_results)
        pass_tests = len([r for r in self.validation_results if r['Result'] == 'PASS'])
        fail_tests = len([r for r in self.validation_results if r['Result'] == 'FAIL'])
        
        success_rate = (pass_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 콘솔 출력
        print(f"\n{'='*80}")
        print("🎯 MACHO 시스템 올바른 창고/현장 시트 구조 검증 결과")
        print(f"{'='*80}")
        print(f"📊 검증 파일: {self.excel_path}")
        print(f"📊 총 테스트: {total_tests}개")
        print(f"📊 성공: {pass_tests}개 ({success_rate:.1f}%)")
        print(f"📊 실패: {fail_tests}개 ({100-success_rate:.1f}%)")
        
        # 카테고리별 결과
        categories = {}
        for result in self.validation_results:
            category = result['Category']
            if category not in categories:
                categories[category] = {'PASS': 0, 'FAIL': 0}
            categories[category][result['Result']] += 1
        
        print(f"\n📋 카테고리별 검증 결과:")
        for category, counts in categories.items():
            total_cat = counts['PASS'] + counts['FAIL']
            pass_rate = (counts['PASS'] / total_cat) * 100 if total_cat > 0 else 0
            print(f"  {category}: {counts['PASS']}/{total_cat} ({pass_rate:.1f}%)")
        
        # 실패한 테스트 세부사항
        if fail_tests > 0:
            print(f"\n❌ 실패한 테스트:")
            for result in self.validation_results:
                if result['Result'] == 'FAIL':
                    print(f"  - {result['Category']}: {result['Test']}")
                    print(f"    상세: {result['Details']}")
        
        # 성공한 주요 테스트
        print(f"\n✅ 성공한 주요 테스트:")
        key_tests = [
            'Multi-level 헤더 구조',
            '입고/출고 헤더 구분',
            '입고/재고 헤더 구분',
            '데이터 건수 확인'
        ]
        for result in self.validation_results:
            if result['Result'] == 'PASS' and any(key in result['Test'] for key in key_tests):
                print(f"  ✓ {result['Category']}: {result['Test']}")
        
        print(f"{'='*80}")
        
        # Excel 검증 리포트 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"MACHO_VALIDATION_REPORT_{timestamp}.xlsx"
        
        validation_df = pd.DataFrame(self.validation_results)
        validation_df.to_excel(report_filename, index=False)
        
        print(f"📋 검증 리포트 저장: {report_filename}")
        
        # 최종 결과 반환
        if success_rate >= 95:
            print(f"\n🎉 검증 성공! MACHO 시스템 구조가 올바릅니다.")
            return True
        else:
            print(f"\n⚠️ 검증 실패! 구조 수정이 필요합니다.")
            return False

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python validate_correct_warehouse_site_report.py <Excel_파일_경로>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    # 검증 실행
    validator = CorrectWarehouseSiteReportValidator(excel_path)
    success = validator.run_full_validation()
    
    if success:
        print(f"\n🎯 **추천 명령어:**")
        print(f"/logi_master monthly_analysis [월별 물류 분석 - Multi-level 헤더 기반]")
        print(f"/switch_mode LATTICE [LATTICE 모드 - 창고 최적화 분석]")
        print(f"/visualize_data warehouse_heatmap [창고별 입출고 히트맵 시각화]")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 