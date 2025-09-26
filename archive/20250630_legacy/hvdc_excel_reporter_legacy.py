"""
📋 HVDC 입고 로직 구현 및 집계 시스템 종합 보고서 (Legacy Version)
Samsung C&T · ADNOC · DSV Partnership

===== 레거시 버전 (v2.8.1-legacy) =====
❌ 검증 결과: 월별 누적·재고 정합률 85.24% (최대 14% 오차)
❌ KPI 일부 실패: Site Inventory Days 46일 (30일 초과)

Legacy 구조:
- 단순 입고-출고 차이 계산 (cumsum 미적용)
- 직송만 포함 (WH→Site 출고 제외)
- 5% 소비 로직 적용
- 창고_월별_입출고 15열 (누계 없음)

입고 로직 3단계: calculate_warehouse_inbound() → create_monthly_inbound_pivot() → calculate_final_location()
Multi-Level Header: 창고 15열, 현장 9열
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 레거시 버전 정보
LEGACY_VERSION = "v2.8.1-legacy"
LEGACY_DATE = "2025-06-30"
LEGACY_VERIFICATION_RATE = 85.24  # 검증 정합률 (%)

# KPI 임계값 (레거시 버전)
KPI_THRESHOLDS = {
    'pkg_accuracy': 0.99,      # 99% 이상 (달성 실패: 94.76%)
    'site_inventory_days': 30,  # 30일 이하 (달성 실패: 46일)
    'backlog_tolerance': 0      # 0건 유지
}

class WarehouseIOCalculatorLegacy:
    """창고 입출고 계산기 - 레거시 버전 (단순 입고-출고)"""
    
    def __init__(self):
        """초기화"""
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 실제 데이터 경로 설정
        self.data_path = Path("../data")
        self.hitachi_file = self.data_path / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        self.simense_file = self.data_path / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        
        # 창고 컬럼 표준화
        self.warehouse_columns = [
            'AAA Storage', 'DSV Al Markaz', 'DSV Indoor', 'DSV MZP',
            'DSV Outdoor', 'Hauler Indoor', 'MOSB'
        ]
        
        # 현장 컬럼 표준화
        self.site_columns = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 창고 우선순위
        self.warehouse_priority = ['DSV Al Markaz', 'DSV Indoor', 'DSV Outdoor', 'DSV MZP', 'AAA Storage', 'Hauler Indoor', 'MOSB']
        
        # Flow Code 매핑
        self.flow_codes = {
            0: 'Pre Arrival',
            1: 'Port → WH (1개)',
            2: 'Port → WH (2개)',
            3: 'Port → WH (3개)',
            4: 'Port → WH (4개+)'
        }
        
        # 데이터 저장 변수
        self.combined_data = None
        self.total_records = 0
        
        logger.info("🏗️ HVDC 입고 로직 구현 및 집계 시스템 초기화 완료 (레거시 버전)")
    
    def calculate_warehouse_inventory_legacy(self, df: pd.DataFrame) -> Dict:
        """레거시 버전: 단순 입고-출고 차이 계산 (cumsum 미적용)"""
        logger.info("🔄 calculate_warehouse_inventory_legacy() - 단순 입고-출고 차이")
        
        # 입고 및 출고 계산
        inbound_result = self.calculate_warehouse_inbound(df)
        outbound_result = self.calculate_warehouse_outbound(df)
        
        # 월별 재고 계산 (단순 차이)
        inventory_by_month = {}
        all_months = set()
        
        # 모든 월 수집
        all_months.update(inbound_result['by_month'].keys())
        all_months.update(outbound_result['by_month'].keys())
        
        # 단순 월별 차이 계산 (cumsum 없음)
        for month in sorted(all_months):
            inbound_count = inbound_result['by_month'].get(month, 0)
            outbound_count = outbound_result['by_month'].get(month, 0)
            inventory_by_month[month] = inbound_count - outbound_count  # 단순 차이
        
        # 창고별 재고 계산
        inventory_by_warehouse = {}
        for warehouse in self.warehouse_columns:
            inbound_count = inbound_result['by_warehouse'].get(warehouse, 0)
            outbound_count = outbound_result['by_warehouse'].get(warehouse, 0)
            inventory_by_warehouse[warehouse] = inbound_count - outbound_count
        
        return {
            'inventory_by_month': inventory_by_month,
            'inventory_by_warehouse': inventory_by_warehouse,
            'total_inventory': sum(inventory_by_warehouse.values())
        }

def main():
    """메인 실행 함수 (레거시 버전)"""
    print("📋 HVDC 입고 로직 구현 및 집계 시스템 종합 보고서 (Legacy)")
    print("입고 로직 3단계 프로세스 + Multi-Level Header 구조")
    print("Samsung C&T · ADNOC · DSV Partnership")
    print("=" * 60)
    
    # 레거시 버전 정보 출력
    print(f"🔧 레거시 버전: {LEGACY_VERSION}")
    print(f"📅 레거시 날짜: {LEGACY_DATE}")
    print(f"❌ 검증 정합률: {LEGACY_VERIFICATION_RATE}% (최대 14% 오차)")
    print("=" * 60)
    
    print("\n❌ 레거시 버전 한계점:")
    print("   - 월별 누적 재고 미적용 (단순 입고-출고 차이)")
    print("   - 직송만 포함 (WH→Site 출고 제외)")
    print("   - 5% 소비 로직 적용 (예측치 왜곡)")
    print("   - 창고_월별_입출고 15열 (누계 없음)")
    print("\n✅ 패치 버전 사용을 권장합니다.")


if __name__ == "__main__":
    main() 