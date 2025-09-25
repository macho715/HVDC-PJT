import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_io():
    """
    HVDC 물류 데이터를 생성하는 함수
    실제 환경에서는 데이터베이스나 파일에서 로드
    """
    # 날짜 범위 설정
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 창고 목록
    warehouses = ['Seoul_Hub', 'Busan_Port', 'Incheon_Gateway', 'Gwangju_Center']
    
    # 물류 단계
    stages = ['Import', 'Customs', 'Warehouse', 'Distribution', 'Export']
    
    # 데이터 생성
    np.random.seed(42)  # 재현 가능한 결과를 위해
    
    data = []
    
    for date in date_range:
        # 각 창고별로 데이터 생성
        for warehouse in warehouses:
            # 계절성 반영 (여름철 물동량 증가)
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
            
            # 각 단계별 물류 흐름
            for i in range(len(stages) - 1):
                stage_from = stages[i]
                stage_to = stages[i + 1]
                
                # TEU (Twenty-foot Equivalent Unit) 계산
                base_teu = np.random.normal(100, 30) * seasonal_factor
                teu = max(0, base_teu)  # 음수 방지
                
                # 재고 변동 (입고 - 출고)
                if stage_from == 'Import':
                    net = teu  # 입고
                elif stage_to == 'Export':
                    net = -teu  # 출고
                else:
                    net = np.random.normal(0, 20)  # 중간 단계 변동
                
                data.append({
                    'date': date,
                    'warehouse': warehouse,
                    'stage_from': stage_from,
                    'stage_to': stage_to,
                    'teu': teu,
                    'net': net
                })
    
    # DataFrame 생성
    df = pd.DataFrame(data)
    
    # 추가 처리
    df['date'] = pd.to_datetime(df['date'])
    df['teu'] = df['teu'].round(1)
    df['net'] = df['net'].round(1)
    
    return df

if __name__ == "__main__":
    # 테스트용
    df = load_io()
    print("Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Date range: {df.date.min()} to {df.date.max()}")
    print(f"Warehouses: {df.warehouse.unique()}")
    print(f"Stages: {df.stage_from.unique()}")
    print("\nSample data:")
    print(df.head())