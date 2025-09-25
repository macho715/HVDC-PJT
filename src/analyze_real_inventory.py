"""
/logi_master analyze_inventory - 전체 재고 실제 검증 스크립트
HVDC 프로젝트 실제 데이터 기반 50개 샘플 재고 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from warehouse_io_calculator import WarehouseIOCalculator
from status_calculator import StatusCalculator
import logging
import os
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealInventoryAnalyzer:
    """실제 재고 분석 클래스"""
    
    def __init__(self):
        self.calculator = WarehouseIOCalculator()
        self.status_calculator = StatusCalculator()
        self.data_path = Path("data")
        
    def load_real_hvdc_data(self):
        """실제 HVDC 데이터 로드"""
        logger.info("📊 실제 HVDC 데이터 로드 중...")
        
        # 데이터 파일들 확인
        data_files = list(self.data_path.glob("*.xlsx"))
        logger.info(f"발견된 데이터 파일: {[f.name for f in data_files]}")
        
        # HITACHI 데이터 로드 시도
        hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        if hitachi_file.exists():
            try:
                df = pd.read_excel(hitachi_file)
                logger.info(f"✅ HITACHI 데이터 로드 성공: {len(df)}건")
                return df
            except Exception as e:
                logger.error(f"❌ HITACHI 데이터 로드 실패: {e}")
        
        # SIMENSE 데이터 로드 시도
        simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        if simense_file.exists():
            try:
                df = pd.read_excel(simense_file)
                logger.info(f"✅ SIMENSE 데이터 로드 성공: {len(df)}건")
                return df
            except Exception as e:
                logger.error(f"❌ SIMENSE 데이터 로드 실패: {e}")
        
        # 실제 데이터가 없으면 테스트 데이터 생성
        logger.warning("⚠️ 실제 데이터 파일을 찾을 수 없어 테스트 데이터를 생성합니다.")
        return self.create_realistic_test_data()
    
    def create_realistic_test_data(self):
        """현실적인 테스트 데이터 생성 (실제 HVDC 데이터 구조 기반)"""
        logger.info("🔧 현실적인 테스트 데이터 생성...")
        
        # 실제 HVDC 프로젝트 구조 기반 데이터
        np.random.seed(42)  # 재현 가능한 결과
        
        # 50개 샘플 생성
        n_samples = 50
        
        # 실제 HVDC 코드 패턴
        hvdc_codes = [
            "HVDC-HE-001", "HVDC-HE-002", "HVDC-HE-003", "HVDC-HE-004", "HVDC-HE-005",
            "HVDC-HE-006", "HVDC-HE-007", "HVDC-HE-008", "HVDC-HE-009", "HVDC-HE-010",
            "HVDC-SIM-001", "HVDC-SIM-002", "HVDC-SIM-003", "HVDC-SIM-004", "HVDC-SIM-005",
            "HVDC-SIM-006", "HVDC-SIM-007", "HVDC-SIM-008", "HVDC-SIM-009", "HVDC-SIM-010",
            "HVDC-SCT-001", "HVDC-SCT-002", "HVDC-SCT-003", "HVDC-SCT-004", "HVDC-SCT-005",
            "HVDC-SCT-006", "HVDC-SCT-007", "HVDC-SCT-008", "HVDC-SCT-009", "HVDC-SCT-010",
            "HVDC-HE-011", "HVDC-HE-012", "HVDC-HE-013", "HVDC-HE-014", "HVDC-HE-015",
            "HVDC-HE-016", "HVDC-HE-017", "HVDC-HE-018", "HVDC-HE-019", "HVDC-HE-020",
            "HVDC-SIM-011", "HVDC-SIM-012", "HVDC-SIM-013", "HVDC-SIM-014", "HVDC-SIM-015",
            "HVDC-SIM-016", "HVDC-SIM-017", "HVDC-SIM-018", "HVDC-SIM-019", "HVDC-SIM-020",
            "HVDC-SCT-011", "HVDC-SCT-012", "HVDC-SCT-013", "HVDC-SCT-014", "HVDC-SCT-015"
        ]
        
        # 실제 날짜 범위 (2024년 1월 ~ 2024년 12월)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # 창고별 입고 날짜 생성
        warehouse_dates = {}
        warehouse_cols = self.calculator.warehouse_columns
        
        for warehouse in warehouse_cols:
            # 각 창고별로 30-70% 확률로 입고
            warehouse_dates[warehouse] = []
            for i in range(n_samples):
                if np.random.random() < 0.5:  # 50% 확률로 입고
                    date = start_date + timedelta(days=np.random.randint(0, 365))
                    warehouse_dates[warehouse].append(date)
                else:
                    warehouse_dates[warehouse].append(None)
        
        # 현장별 입고 날짜 생성 (창고 입고 후)
        site_dates = {}
        site_cols = self.calculator.site_columns
        
        for site in site_cols:
            site_dates[site] = []
            for i in range(n_samples):
                # 창고 입고가 있는 경우에만 현장 입고 가능
                has_warehouse = any(warehouse_dates[wh][i] is not None for wh in warehouse_cols)
                if has_warehouse and np.random.random() < 0.7:  # 70% 확률로 현장 입고
                    # 창고 입고 후 1-30일 후 현장 입고
                    warehouse_date = None
                    for wh in warehouse_cols:
                        if warehouse_dates[wh][i] is not None:
                            warehouse_date = warehouse_dates[wh][i]
                            break
                    
                    if warehouse_date:
                        site_date = warehouse_date + timedelta(days=np.random.randint(1, 31))
                        site_dates[site].append(site_date)
                    else:
                        site_dates[site].append(None)
                else:
                    site_dates[site].append(None)
        
        # PKG 수량 (실제 수량 분포)
        pkg_quantities = np.random.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20], 
                                        size=n_samples, p=[0.3, 0.25, 0.2, 0.1, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01])
        
        # 데이터프레임 생성
        data = {
            'Item': hvdc_codes[:n_samples],
            'Pkg': pkg_quantities
        }
        
        # 창고 컬럼 추가
        for warehouse in warehouse_cols:
            data[warehouse] = warehouse_dates[warehouse]
        
        # 현장 컬럼 추가
        for site in site_cols:
            data[site] = site_dates[site]
        
        df = pd.DataFrame(data)
        logger.info(f"✅ 현실적인 테스트 데이터 생성 완료: {len(df)}건")
        
        return df
    
    def analyze_inventory_samples(self, df, sample_size=50):
        """50개 샘플 재고 분석"""
        logger.info(f"🔍 {sample_size}개 샘플 재고 분석 시작...")
        
        # 실제 데이터 컬럼 확인
        logger.info(f"실제 데이터 컬럼: {list(df.columns)}")
        
        # 샘플 데이터 선택 (처음 50개 또는 전체)
        sample_df = df.head(sample_size).copy()
        
        # 1. Status 계산
        status_df = self.status_calculator.calculate_complete_status(sample_df)
        
        # 2. Final Location 계산
        final_df = self.calculator.calculate_final_location(status_df)
        
        # 3. 각 샘플별 상세 분석
        sample_analysis = []
        
        for idx, row in final_df.iterrows():
            # 기본 정보 (실제 컬럼명에 맞게 조정)
            item_column = 'Item' if 'Item' in row.index else df.columns[0]  # 첫 번째 컬럼을 Item으로 사용
            
            item_info = {
                'Item': str(row[item_column]) if pd.notna(row[item_column]) else f"Item_{idx}",
                'Pkg': row.get('Pkg', 1) if 'Pkg' in row.index else 1,
                'Status_Current': row['Status_Current'],
                'Status_Location': row['Status_Location'],
                'Final_Location': row['Final_Location']
            }
            
            # 창고 입고 정보
            warehouse_info = {}
            for warehouse in self.calculator.warehouse_columns:
                if warehouse in row.index and pd.notna(row[warehouse]):
                    safe_date = pd.to_datetime(row[warehouse], errors='coerce')
                    warehouse_info[warehouse] = {
                        'date': safe_date if not pd.isna(safe_date) else None,
                        'month': safe_date.strftime('%Y-%m') if not pd.isna(safe_date) else None
                    }
            
            # 현장 입고 정보
            site_info = {}
            for site in self.calculator.site_columns:
                if site in row.index and pd.notna(row[site]):
                    safe_date = pd.to_datetime(row[site], errors='coerce')
                    site_info[site] = {
                        'date': safe_date if not pd.isna(safe_date) else None,
                        'month': safe_date.strftime('%Y-%m') if not pd.isna(safe_date) else None
                    }
            
            # 재고 상태 판정
            inventory_status = self.determine_inventory_status(row, warehouse_info, site_info)
            
            sample_analysis.append({
                'item_info': item_info,
                'warehouse_info': warehouse_info,
                'site_info': site_info,
                'inventory_status': inventory_status
            })
        
        return sample_analysis
    
    def determine_inventory_status(self, row, warehouse_info, site_info):
        """재고 상태 판정"""
        status = row['Status_Current']
        location = row['Status_Location']
        
        if status == 'warehouse':
            warehouse_name = location
            warehouse_date = warehouse_info.get(warehouse_name, {}).get('date')
            days = (datetime.now() - warehouse_date).days if warehouse_date is not None and not pd.isna(warehouse_date) else None
            return {
                'type': 'warehouse_inventory',
                'location': warehouse_name,
                'arrival_date': warehouse_date if warehouse_date is not None and not pd.isna(warehouse_date) else 'N/A',
                'days_in_warehouse': days if days is not None else 'N/A',
                'description': f"{warehouse_name} 창고 재고"
            }
        elif status == 'site':
            site_name = location
            site_date = site_info.get(site_name, {}).get('date')
            days = (datetime.now() - site_date).days if site_date is not None and not pd.isna(site_date) else None
            return {
                'type': 'site_inventory',
                'location': site_name,
                'arrival_date': site_date if site_date is not None and not pd.isna(site_date) else 'N/A',
                'days_at_site': days if days is not None else 'N/A',
                'description': f"{site_name} 현장 재고"
            }
        else:
            return {
                'type': 'pre_arrival',
                'location': 'Pre Arrival',
                'description': '입항 전 상태'
            }
    
    def calculate_inventory_statistics(self, sample_analysis):
        """재고 통계 계산"""
        logger.info("📊 재고 통계 계산...")
        
        # 상태별 분포
        status_counts = {}
        location_counts = {}
        warehouse_inventory = []
        site_inventory = []
        
        for sample in sample_analysis:
            item_info = sample['item_info']
            inventory_status = sample['inventory_status']
            
            # 상태별 카운트
            status = item_info['Status_Current']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # 위치별 카운트
            location = item_info['Status_Location']
            location_counts[location] = location_counts.get(location, 0) + 1
            
            # 창고/현장 재고 상세
            if inventory_status['type'] == 'warehouse_inventory':
                warehouse_inventory.append({
                    'item': item_info['Item'],
                    'location': inventory_status['location'],
                    'pkg': item_info['Pkg'],
                    'days': inventory_status['days_in_warehouse']
                })
            elif inventory_status['type'] == 'site_inventory':
                site_inventory.append({
                    'item': item_info['Item'],
                    'location': inventory_status['location'],
                    'pkg': item_info['Pkg'],
                    'days': inventory_status['days_at_site']
                })
        
        # 통계 계산
        total_pkg = sum(sample['item_info']['Pkg'] for sample in sample_analysis)
        avg_pkg = total_pkg / len(sample_analysis)
        
        # 창고별 재고 통계
        warehouse_stats = {}
        for inv in warehouse_inventory:
            location = inv['location']
            if location not in warehouse_stats:
                warehouse_stats[location] = {'count': 0, 'total_pkg': 0, 'avg_days': 0, 'items': []}
            
            warehouse_stats[location]['count'] += 1
            warehouse_stats[location]['total_pkg'] += inv['pkg']
            warehouse_stats[location]['items'].append(inv['item'])
        
        # 평균 재고일수 계산
        for location in warehouse_stats:
            days_list = [inv['days'] for inv in warehouse_inventory if inv['location'] == location and inv['days'] is not None]
            if days_list:
                warehouse_stats[location]['avg_days'] = sum(days_list) / len(days_list)
        
        return {
            'total_samples': len(sample_analysis),
            'total_pkg': total_pkg,
            'avg_pkg': avg_pkg,
            'status_distribution': status_counts,
            'location_distribution': location_counts,
            'warehouse_inventory': warehouse_inventory,
            'site_inventory': site_inventory,
            'warehouse_stats': warehouse_stats
        }
    
    def print_inventory_report(self, sample_analysis, statistics):
        """재고 분석 리포트 출력"""
        print("\n" + "="*100)
        print("🏭 /logi_master analyze_inventory - 전체 재고 실제 검증 리포트")
        print("="*100)
        
        # 1. 전체 통계
        print(f"\n📊 전체 통계:")
        print(f"   총 샘플: {statistics['total_samples']}건")
        print(f"   총 PKG: {statistics['total_pkg']}개")
        print(f"   평균 PKG: {statistics['avg_pkg']:.2f}개")
        
        # 2. 상태별 분포
        print(f"\n📈 상태별 분포:")
        for status, count in statistics['status_distribution'].items():
            percentage = (count / statistics['total_samples']) * 100
            print(f"   {status}: {count}건 ({percentage:.1f}%)")
        
        # 3. 위치별 분포
        print(f"\n📍 위치별 분포:")
        for location, count in statistics['location_distribution'].items():
            percentage = (count / statistics['total_samples']) * 100
            print(f"   {location}: {count}건 ({percentage:.1f}%)")
        
        # 4. 창고별 재고 상세
        print(f"\n🏢 창고별 재고 상세:")
        for location, stats in statistics['warehouse_stats'].items():
            print(f"   {location}:")
            print(f"     - 재고 건수: {stats['count']}건")
            print(f"     - 총 PKG: {stats['total_pkg']}개")
            print(f"     - 평균 재고일수: {stats['avg_days']:.1f}일")
            print(f"     - 재고 항목: {', '.join(stats['items'][:5])}{'...' if len(stats['items']) > 5 else ''}")
        
        # 5. 50개 샘플 상세 (처음 10개만 표시)
        print(f"\n📋 샘플 상세 (처음 10개):")
        print("-" * 100)
        print(f"{'Item':<15} {'Pkg':<5} {'Status':<12} {'Location':<15} {'Type':<15} {'Days':<8} {'Description'}")
        print("-" * 100)
        
        for i, sample in enumerate(sample_analysis[:10]):
            item_info = sample['item_info']
            inventory_status = sample['inventory_status']
            
            days = inventory_status.get('days_in_warehouse') or inventory_status.get('days_at_site') or 'N/A'
            if isinstance(days, (int, float)):
                days = f"{days:.0f}일"
            
            print(f"{item_info['Item']:<15} {item_info['Pkg']:<5} {item_info['Status_Current']:<12} "
                  f"{item_info['Status_Location']:<15} {inventory_status['type']:<15} {days:<8} "
                  f"{inventory_status['description']}")
        
        if len(sample_analysis) > 10:
            print(f"... (총 {len(sample_analysis)}개 샘플 중 10개 표시)")
        
        # 6. 재고 품질 지표
        print(f"\n🎯 재고 품질 지표:")
        
        # 창고 재고율
        warehouse_count = statistics['status_distribution'].get('warehouse', 0)
        warehouse_rate = (warehouse_count / statistics['total_samples']) * 100
        print(f"   창고 재고율: {warehouse_rate:.1f}% ({warehouse_count}/{statistics['total_samples']})")
        
        # 현장 재고율
        site_count = statistics['status_distribution'].get('site', 0)
        site_rate = (site_count / statistics['total_samples']) * 100
        print(f"   현장 재고율: {site_rate:.1f}% ({site_count}/{statistics['total_samples']})")
        
        # Pre Arrival 비율
        pre_arrival_count = statistics['status_distribution'].get('Pre Arrival', 0)
        pre_arrival_rate = (pre_arrival_count / statistics['total_samples']) * 100
        print(f"   Pre Arrival 비율: {pre_arrival_rate:.1f}% ({pre_arrival_count}/{statistics['total_samples']})")
        
        # 평균 재고일수
        all_days = []
        for inv in statistics['warehouse_inventory'] + statistics['site_inventory']:
            if inv['days'] is not None:
                all_days.append(inv['days'])
        
        if all_days:
            avg_days = sum(all_days) / len(all_days)
            print(f"   평균 재고일수: {avg_days:.1f}일")
        
        print("="*100)
    
    def export_samples_to_excel(self, sample_analysis, filename="real_inventory_sample_50.xlsx"):
        """샘플 분석 결과를 엑셀로 저장"""
        rows = []
        for sample in sample_analysis:
            item_info = sample['item_info']
            inv = sample['inventory_status']
            rows.append({
                'Item': item_info['Item'],
                'Pkg': item_info['Pkg'],
                'Status': item_info['Status_Current'],
                'Location': item_info['Status_Location'],
                'Type': inv['type'],
                'Days': inv.get('days_in_warehouse') or inv.get('days_at_site') or 'N/A',
                'Description': inv['description']
            })
        df = pd.DataFrame(rows)
        df.to_excel(filename, index=False)
        logger.info(f"✅ 샘플 50건 엑셀 저장 완료: {filename}")

    def export_complete_original_data(self, df, filename="HVDC_complete_data_original.xlsx"):
        """원본 데이터 전체를 엑셀로 저장"""
        logger.info(f"📊 원본 데이터 전체 저장 중: {len(df)}건")
        
        # 원본 데이터 그대로 저장 (모든 컬럼 포함)
        df.to_excel(filename, index=False)
        logger.info(f"✅ 원본 데이터 전체 저장 완료: {filename}")
        
        # 데이터 요약 정보도 함께 저장
        summary_data = {
            '항목': ['총 레코드 수', '총 컬럼 수', '데이터 크기', '저장 시간'],
            '값': [
                len(df),
                len(df.columns),
                f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # 요약 정보를 별도 시트로 저장
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
            summary_df.to_excel(writer, sheet_name='Data_Summary', index=False)
        
        logger.info(f"✅ 데이터 요약 정보 추가 저장 완료")

    def run_comprehensive_analysis(self):
        """종합 재고 분석 실행"""
        logger.info("🚀 /logi_master analyze_inventory 실행...")
        
        # 1. 실제 데이터 로드
        df = self.load_real_hvdc_data()
        
        # 2. 원본 데이터 전체 저장
        self.export_complete_original_data(df)
        
        # 3. 50개 샘플 분석
        sample_analysis = self.analyze_inventory_samples(df, 50)
        
        # 4. 통계 계산
        statistics = self.calculate_inventory_statistics(sample_analysis)
        
        # 5. 리포트 출력
        self.print_inventory_report(sample_analysis, statistics)
        
        # 6. 샘플 엑셀로 저장
        self.export_samples_to_excel(sample_analysis)
        
        return {
            'sample_analysis': sample_analysis,
            'statistics': statistics,
            'raw_data': df
        }

def main():
    """메인 실행 함수"""
    analyzer = RealInventoryAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    return results

if __name__ == "__main__":
    main() 