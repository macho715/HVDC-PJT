import pytest
import pandas as pd
import numpy as np
from datetime import datetime


class TestExcelStatusLogic:
    """
    Excel 수식 기반 Status_Current 결정 로직 테스트
    
    Excel 수식:
    =IF($AT=1, "site", IF($AS=1, "warehouse", "Pre Arrival"))
    
    복합 수식:
    =IF($AT=1,
       INDEX($AO$1:$AR$1, MATCH(MAX($AO:$AR), $AO:$AR, 0)),
       IF($AS=1,
          INDEX($AF$1:$AN$1, MATCH(MAX($AF:$AN), $AF:$AN, 0)),
          IF($AG=$AH,
             $AH$1,
             INDEX($AG$1:$AH$1, MATCH(MAX($AG:$AH), $AG:$AH, 0))
          )
       )
    )
    """
    
    def test_status_determination_site_case(self):
        """AT=1이면 'site' 상태로 결정되어야 함"""
        # Given: AT=1, AS=0인 샘플 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [0],  # AS 컬럼 (COUNT($AF:$AN)>0의 결과)
            'Status_SITE': [1],       # AT 컬럼 (COUNT($AO:$AR)>0의 결과)
            'Status_Current': ['']    # 계산될 컬럼
        })
        
        # When: Status 결정 로직 적용
        result = self._determine_status(test_data.iloc[0])
        
        # Then: 'site' 결정
        assert result == 'site', f"Expected 'site' but got '{result}'"
        
    def test_status_determination_warehouse_case(self):
        """AT=0, AS=1이면 'warehouse' 상태로 결정되어야 함"""
        # Given: AT=0, AS=1인 샘플 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [1],  # AS 컬럼
            'Status_SITE': [0],       # AT 컬럼
            'Status_Current': ['']
        })
        
        # When: Status 결정 로직 적용
        result = self._determine_status(test_data.iloc[0])
        
        # Then: 'warehouse' 결정
        assert result == 'warehouse', f"Expected 'warehouse' but got '{result}'"
        
    def test_status_determination_pre_arrival_case(self):
        """AT=0, AS=0이면 'Pre Arrival' 상태로 결정되어야 함"""
        # Given: AT=0, AS=0인 샘플 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [0],  # AS 컬럼
            'Status_SITE': [0],       # AT 컬럼
            'Status_Current': ['']
        })
        
        # When: Status 결정 로직 적용
        result = self._determine_status(test_data.iloc[0])
        
        # Then: 'Pre Arrival' 결정
        assert result == 'Pre Arrival', f"Expected 'Pre Arrival' but got '{result}'"
        
    def test_status_location_site_max_finder(self):
        """Site 상태에서 최대값 위치의 헤더를 반환해야 함"""
        # Given: Site 상태이고 AO:AR 범위에 값이 있는 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [0],
            'Status_SITE': [1],
            'MIR': [datetime(2024, 3, 15)],  # AO 컬럼
            'SHU': [np.nan],                 # AP 컬럼
            'DAS': [datetime(2024, 5, 10)],  # AQ 컬럼
            'AGI': [np.nan]                  # AR 컬럼
        })
        
        # When: Site 위치 결정 로직 적용
        result = self._find_site_location(test_data.iloc[0])
        
        # Then: 최신 날짜(DAS)가 반환되어야 함
        assert result == 'DAS', f"Expected 'DAS' but got '{result}'"
        
    def test_status_location_warehouse_max_finder(self):
        """Warehouse 상태에서 최대값 위치의 헤더를 반환해야 함"""
        # Given: Warehouse 상태이고 AF:AN 범위에 값이 있는 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [1],
            'Status_SITE': [0],
            'DSV Indoor': [datetime(2024, 2, 1)],    # AF 컬럼
            'DSV Outdoor': [datetime(2024, 4, 15)],  # AG 컬럼
            'DSV Al Markaz': [np.nan],               # AH 컬럼
            'DSV MZP': [np.nan],                     # AI 컬럼
            'AAA  Storage': [np.nan],                # AJ 컬럼
            'Hauler Indoor': [np.nan],               # AK 컬럼
            'MOSB': [np.nan],                        # AL 컬럼
            'DHL Warehouse': [np.nan]                # AM 컬럼
        })
        
        # When: Warehouse 위치 결정 로직 적용
        result = self._find_warehouse_location(test_data.iloc[0])
        
        # Then: 최신 날짜(DSV Outdoor)가 반환되어야 함
        assert result == 'DSV Outdoor', f"Expected 'DSV Outdoor' but got '{result}'"
        
    def test_status_location_pre_arrival_equal_values(self):
        """Pre Arrival 상태에서 AG=AH 동일값이면 AH 헤더 반환"""
        # Given: Pre Arrival 상태이고 AG=AH인 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [0],
            'Status_SITE': [0],
            'DSV Outdoor': [datetime(2024, 3, 15)],   # AG 컬럼
            'DSV Al Markaz': [datetime(2024, 3, 15)]  # AH 컬럼
        })
        
        # When: Pre Arrival 위치 결정 로직 적용
        result = self._find_pre_arrival_location(test_data.iloc[0])
        
        # Then: AH 헤더(DSV Al Markaz) 반환
        assert result == 'DSV Al Markaz', f"Expected 'DSV Al Markaz' but got '{result}'"
        
    def test_status_location_pre_arrival_different_values(self):
        """Pre Arrival 상태에서 AG≠AH이면 최대값 위치 헤더 반환"""
        # Given: Pre Arrival 상태이고 AG≠AH인 데이터
        test_data = pd.DataFrame({
            'Status_WAREHOUSE': [0],
            'Status_SITE': [0],
            'DSV Outdoor': [datetime(2024, 3, 15)],   # AG 컬럼
            'DSV Al Markaz': [datetime(2024, 5, 20)]  # AH 컬럼
        })
        
        # When: Pre Arrival 위치 결정 로직 적용
        result = self._find_pre_arrival_location(test_data.iloc[0])
        
        # Then: 최대값 위치 헤더(DSV Al Markaz) 반환
        assert result == 'DSV Al Markaz', f"Expected 'DSV Al Markaz' but got '{result}'"
        
    def _determine_status(self, row: pd.Series) -> str:
        """
        Excel 수식: IF($AT=1, "site", IF($AS=1, "warehouse", "Pre Arrival"))
        """
        if row['Status_SITE'] == 1:
            return "site"
        elif row['Status_WAREHOUSE'] == 1:
            return "warehouse"
        else:
            return "Pre Arrival"
        
    def _find_site_location(self, row: pd.Series) -> str:
        """
        Excel 수식: INDEX($AO$1:$AR$1, MATCH(MAX($AO:$AR), $AO:$AR, 0))
        """
        # Site 컬럼들 (AO:AR 범위)
        site_cols = ['MIR', 'SHU', 'DAS', 'AGI']
        
        # 각 컬럼의 값 가져오기
        max_date = None
        max_col = None
        
        for col in site_cols:
            if col in row.index:
                val = row[col]
                if pd.notna(val) and isinstance(val, datetime):
                    if max_date is None or val > max_date:
                        max_date = val
                        max_col = col
        
        return max_col if max_col else "NOT_FOUND"
        
    def _find_warehouse_location(self, row: pd.Series) -> str:
        """
        Excel 수식: INDEX($AF$1:$AN$1, MATCH(MAX($AF:$AN), $AF:$AN, 0))
        """
        # Warehouse 컬럼들 (AF:AN 범위)
        warehouse_cols = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP', 
                         'AAA  Storage', 'Hauler Indoor', 'MOSB', 'DHL Warehouse']
        
        # 각 컬럼의 값 가져오기
        max_date = None
        max_col = None
        
        for col in warehouse_cols:
            if col in row.index:
                val = row[col]
                if pd.notna(val) and isinstance(val, datetime):
                    if max_date is None or val > max_date:
                        max_date = val
                        max_col = col
        
        return max_col if max_col else "NOT_FOUND"
        
    def _find_pre_arrival_location(self, row: pd.Series) -> str:
        """
        Excel 수식: IF($AG=$AH, $AH$1, INDEX($AG$1:$AH$1, MATCH(MAX($AG:$AH), $AG:$AH, 0)))
        """
        # Pre Arrival 상태에서 AG:AH 범위 (DSV Outdoor, DSV Al Markaz)
        dsv_outdoor = row.get('DSV Outdoor')
        dsv_al_markaz = row.get('DSV Al Markaz')
        
        # 두 값이 모두 존재하는 경우
        if pd.notna(dsv_outdoor) and pd.notna(dsv_al_markaz):
            # 동일한 값인 경우 DSV Al Markaz 우선 선택
            if dsv_outdoor == dsv_al_markaz:
                return 'DSV Al Markaz'
            # 다른 값인 경우 최대값(최신 날짜) 선택
            elif isinstance(dsv_outdoor, datetime) and isinstance(dsv_al_markaz, datetime):
                if dsv_al_markaz > dsv_outdoor:
                    return 'DSV Al Markaz'
                else:
                    return 'DSV Outdoor'
        
        # 하나만 존재하는 경우
        elif pd.notna(dsv_al_markaz):
            return 'DSV Al Markaz'
        elif pd.notna(dsv_outdoor):
            return 'DSV Outdoor'
        
        return "NOT_FOUND" 