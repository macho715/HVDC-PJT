import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional


class StatusCalculator:
    """
    Excel 수식 기반 Status_Current 계산 클래스
    
    Excel 수식:
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
    
    def __init__(self):
        # Site 컬럼들 (AO:AR 범위)
        self.site_cols = ['MIR', 'SHU', 'DAS', 'AGI']
        
        # Warehouse 컬럼들 (AF:AN 범위) - Pre Arrival 전용 컬럼 제외
        self.warehouse_cols = ['DSV Indoor', 'DSV MZP', 'AAA  Storage', 'Hauler Indoor', 'MOSB', 'DHL Warehouse']
        
        # Pre Arrival 전용 컬럼들 (AG:AH 범위)
        self.pre_arrival_cols = ['DSV Outdoor', 'DSV Al Markaz']
    
    def calculate_status_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        AS, AT 컬럼 계산
        AS = COUNT($AF:$AN)>0 → 1 if true else 0
        AT = COUNT($AO:$AR)>0 → 1 if true else 0
        """
        result_df = df.copy()
        
        # AS 컬럼 계산: Warehouse 범위에 값이 있는지 확인
        existing_warehouse_cols = [col for col in self.warehouse_cols if col in df.columns]
        if existing_warehouse_cols:
            warehouse_count = df[existing_warehouse_cols].notna().sum(axis=1)
        else:
            warehouse_count = pd.Series(0, index=df.index)
        result_df['Status_WAREHOUSE'] = (warehouse_count > 0).astype(int)
        
        # AT 컬럼 계산: Site 범위에 값이 있는지 확인
        existing_site_cols = [col for col in self.site_cols if col in df.columns]
        if existing_site_cols:
            site_count = df[existing_site_cols].notna().sum(axis=1)
        else:
            site_count = pd.Series(0, index=df.index)
        result_df['Status_SITE'] = (site_count > 0).astype(int)
        
        return result_df
    
    def calculate_status_current(self, df: pd.DataFrame) -> pd.Series:
        """
        Status_Current 계산
        Excel 수식: IF($AT=1, "site", IF($AS=1, "warehouse", "Pre Arrival"))
        """
        # AS, AT 컬럼이 없으면 먼저 계산
        if 'Status_WAREHOUSE' not in df.columns or 'Status_SITE' not in df.columns:
            df_with_flags = self.calculate_status_flags(df)
        else:
            df_with_flags = df
        
        def determine_status(row):
            if row['Status_SITE'] == 1:
                return "site"
            elif row['Status_WAREHOUSE'] == 1:
                return "warehouse"
            else:
                return "Pre Arrival"
        
        return df_with_flags.apply(determine_status, axis=1)
    
    def calculate_status_location(self, df: pd.DataFrame) -> pd.Series:
        """
        Status_Location 계산
        Excel 수식 정확 구현:
        =IF($AT=1, INDEX($AO$1:$AR$1, MATCH(MAX($AO:$AR), $AO:$AR, 0)),
           IF($AS=1, INDEX($AF$1:$AN$1, MATCH(MAX($AF:$AN), $AF:$AN, 0)),
              IF(COUNT($AG:$AH)=0, "Pre Arrival",
                 IF($AG=$AH, $AH$1, INDEX($AG$1:$AH$1, MATCH(MAX($AG:$AH), $AG:$AH, 0)))
              )
           )
        )
        """
        # AS, AT 컬럼이 없으면 먼저 계산
        if 'Status_WAREHOUSE' not in df.columns or 'Status_SITE' not in df.columns:
            df_with_flags = self.calculate_status_flags(df)
        else:
            df_with_flags = df
        
        def determine_location(row):
            if row['Status_SITE'] == 1:
                return self._find_site_location(row)
            elif row['Status_WAREHOUSE'] == 1:
                return self._find_warehouse_location(row)
            else:
                return self._find_pre_arrival_location(row)
        
        return df_with_flags.apply(determine_location, axis=1)
    
    def _find_site_location(self, row: pd.Series) -> str:
        """
        Excel 수식: INDEX($AO$1:$AR$1, MATCH(MAX($AO:$AR), $AO:$AR, 0))
        """
        max_date = None
        max_col = None
        
        for col in self.site_cols:
            if col in row.index:
                val = row[col]
                if pd.notna(val) and isinstance(val, datetime):
                    if max_date is None or val > max_date:
                        max_date = val
                        max_col = col
        
        return max_col if max_col else "SITE_NOT_FOUND"
    
    def _find_warehouse_location(self, row: pd.Series) -> str:
        """
        Excel 수식: INDEX($AF$1:$AN$1, MATCH(MAX($AF:$AN), $AF:$AN, 0))
        """
        max_date = None
        max_col = None
        
        for col in self.warehouse_cols:
            if col in row.index:
                val = row[col]
                if pd.notna(val) and isinstance(val, datetime):
                    if max_date is None or val > max_date:
                        max_date = val
                        max_col = col
        
        return max_col if max_col else "WAREHOUSE_NOT_FOUND"
    
    def _find_pre_arrival_location(self, row: pd.Series) -> str:
        """
        Excel 수식: IF($AG=$AH, $AH$1, INDEX($AG$1:$AH$1, MATCH(MAX($AG:$AH), $AG:$AH, 0)))
        두 개가 겹칠 경우 최종 장소는 DSV Al Markaz
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
        
        return "Pre Arrival"  # 기본 Pre Arrival 반환
    
    def calculate_complete_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        완전한 Status 계산 (AS, AT, Status_Current, Status_Location)
        """
        result_df = self.calculate_status_flags(df)
        result_df['Status_Current'] = self.calculate_status_current(result_df)
        result_df['Status_Location'] = self.calculate_status_location(result_df)
        
        return result_df 