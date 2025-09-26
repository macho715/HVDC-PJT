#!/usr/bin/env python3
"""
MACHO-GPT Warehouse Inventory System v3.4-mini
실시간 창고 재고 모니터링 시스템

Command: /warehouse-inventory --real-time
Features:
- 실시간 재고 현황 추적
- 창고별 용량 활용도 분석
- 재고 회전율 계산
- 장기 보관 품목 식별
- 재고 최적화 제안
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime, timedelta
from collections import defaultdict
import json

class MACHOWarehouseInventory:
    """MACHO-GPT 창고 재고 관리 시스템"""
    
    def __init__(self):
        self.rdf_data = []
        self.inventory_data = {}
        self.capacity_data = {}
        self.alert_thresholds = {
            'high_volume': 500,     # 고용량 임계값 (건수)
            'low_turnover': 30,     # 낮은 회전율 임계값 (일)
            'capacity_limit': 80,   # 용량 한계 임계값 (%)
            'long_stay': 60         # 장기 보관 임계값 (일)
        }
        
        # 창고 용량 정보 (CBM 기준)
        self.warehouse_capacity = {
            'DSV Indoor': 5000,
            'DSV Outdoor': 8000,
            'DSV Al Markaz': 6000,
            'MOSB': 3000,
            'AAA Storage': 2000,
            'DHL Warehouse': 1500,
            'Hauler Indoor': 1000,
            'Shifting': 500
        }
        
        # 창고 속성 매핑
        self.warehouse_properties = {
            'hasDHLWarehouse': 'DHL Warehouse',
            'hasDSVIndoor': 'DSV Indoor',
            'hasDSVAlMarkaz': 'DSV Al Markaz',
            'hasDSVOutdoor': 'DSV Outdoor',
            'hasAAAStorage': 'AAA Storage',
            'hasHaulerIndoor': 'Hauler Indoor',
            'hasDSVMZP': 'DSV MZP',
            'hasMOSB': 'MOSB',
            'hasShifting': 'Shifting'
        }
    
    def load_rdf_data(self, rdf_file="rdf_output/HVDC WAREHOUSE_HITACHI(HE).ttl"):
        """RDF 데이터 로드"""
        print("[MACHO-GPT] 실시간 재고 데이터 로드 중...")
        
        if not Path(rdf_file).exists():
            print(f"[ERROR] RDF 파일을 찾을 수 없습니다: {rdf_file}")
            return False
            
        with open(rdf_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # TransportEvent 블록별로 분할
        event_blocks = re.split(r'(ex:TransportEvent_[^\s]+)', content)
        
        events_data = []
        
        for i in range(1, len(event_blocks), 2):
            if i + 1 < len(event_blocks):
                event_id = event_blocks[i].replace('ex:TransportEvent_', '')
                event_content = event_blocks[i + 1]
                
                event_data = {
                    'event': event_id,
                    'case': None,
                    'cbm': None,
                    'vendor': None,
                    'warehouse_timeline': []
                }
                
                # 기본 정보 추출
                cbm_match = re.search(r'ex:hasCubicMeter\s+"?([0-9.]+)"?\^\^xsd:decimal', event_content)
                if cbm_match:
                    event_data['cbm'] = float(cbm_match.group(1))
                
                vendor_match = re.search(r'ex:hasHVDCCode3\s+"([^"]+)"', event_content)
                if vendor_match:
                    event_data['vendor'] = vendor_match.group(1)
                
                case_match = re.search(r'ex:hasCase\s+"?([^"^\s]+)"?', event_content)
                if case_match:
                    event_data['case'] = case_match.group(1)
                
                # 창고별 날짜 정보 추출
                for prop, warehouse_name in self.warehouse_properties.items():
                    date_pattern = rf'ex:{prop}\s+"?([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})"?\^\^xsd:date'
                    date_match = re.search(date_pattern, event_content)
                    if date_match:
                        date_str = date_match.group(1)
                        event_data['warehouse_timeline'].append({
                            'warehouse': warehouse_name,
                            'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                            'date_str': date_str
                        })
                
                # 시간순 정렬
                event_data['warehouse_timeline'].sort(key=lambda x: x['date'])
                events_data.append(event_data)
        
        self.rdf_data = events_data
        print(f"[SUCCESS] 재고 데이터 로드 완료: {len(events_data)} 이벤트")
        return True
    
    def analyze_current_inventory(self):
        """현재 재고 분석"""
        print("\n=== 실시간 창고 재고 현황 ===")
        print("=" * 80)
        
        current_inventory = defaultdict(lambda: {
            'items': [],
            'total_cbm': 0,
            'total_count': 0,
            'avg_cbm': 0,
            'oldest_date': None,
            'newest_date': None
        })
        
        today = datetime.now().date()
        
        for event in self.rdf_data:
            if not event['warehouse_timeline']:
                continue
                
            # 마지막 창고 위치가 현재 재고 위치
            last_warehouse = event['warehouse_timeline'][-1]
            warehouse = last_warehouse['warehouse']
            storage_date = last_warehouse['date']
            
            # 현재부터 저장 기간 계산
            days_stored = (today - storage_date).days
            
            item_data = {
                'case': event['case'],
                'cbm': event['cbm'] or 0,
                'vendor': event['vendor'],
                'storage_date': storage_date,
                'days_stored': days_stored,
                'event': event['event']
            }
            
            current_inventory[warehouse]['items'].append(item_data)
            current_inventory[warehouse]['total_cbm'] += item_data['cbm']
            current_inventory[warehouse]['total_count'] += 1
            
            # 최신/최오래된 날짜 업데이트
            if (current_inventory[warehouse]['oldest_date'] is None or 
                storage_date < current_inventory[warehouse]['oldest_date']):
                current_inventory[warehouse]['oldest_date'] = storage_date
                
            if (current_inventory[warehouse]['newest_date'] is None or 
                storage_date > current_inventory[warehouse]['newest_date']):
                current_inventory[warehouse]['newest_date'] = storage_date
        
        # 평균 CBM 계산
        for warehouse, data in current_inventory.items():
            if data['total_count'] > 0:
                data['avg_cbm'] = data['total_cbm'] / data['total_count']
        
        self.inventory_data = dict(current_inventory)
        return self.inventory_data
    
    def calculate_capacity_utilization(self):
        """창고 용량 활용도 계산"""
        print("\n=== 창고 용량 활용도 분석 ===")
        print("-" * 80)
        
        utilization_data = {}
        
        print(f"{'창고명':<20} {'현재CBM':<10} {'용량CBM':<10} {'활용률':<8} {'여유공간':<10} {'상태':<10}")
        print("-" * 80)
        
        for warehouse, capacity in self.warehouse_capacity.items():
            current_cbm = self.inventory_data.get(warehouse, {}).get('total_cbm', 0)
            utilization_rate = (current_cbm / capacity) * 100 if capacity > 0 else 0
            remaining_space = capacity - current_cbm
            
            # 상태 결정
            if utilization_rate >= self.alert_thresholds['capacity_limit']:
                status = "HIGH"
            elif utilization_rate >= 60:
                status = "MEDIUM"
            else:
                status = "LOW"
            
            utilization_data[warehouse] = {
                'current_cbm': current_cbm,
                'capacity': capacity,
                'utilization_rate': utilization_rate,
                'remaining_space': remaining_space,
                'status': status
            }
            
            print(f"{warehouse:<20} {current_cbm:<10.2f} {capacity:<10.2f} {utilization_rate:<8.1f}% {remaining_space:<10.2f} {status:<10}")
        
        self.capacity_data = utilization_data
        return utilization_data
    
    def identify_long_stay_items(self):
        """장기 보관 품목 식별"""
        print(f"\n=== 장기 보관 품목 (>{self.alert_thresholds['long_stay']}일) ===")
        print("-" * 80)
        
        long_stay_items = []
        
        for warehouse, data in self.inventory_data.items():
            for item in data['items']:
                if item['days_stored'] > self.alert_thresholds['long_stay']:
                    long_stay_items.append({
                        'warehouse': warehouse,
                        'case': item['case'],
                        'cbm': item['cbm'],
                        'vendor': item['vendor'],
                        'days_stored': item['days_stored'],
                        'storage_date': item['storage_date']
                    })
        
        # 보관 기간 순으로 정렬
        long_stay_items.sort(key=lambda x: x['days_stored'], reverse=True)
        
        print(f"{'창고명':<20} {'Case':<15} {'CBM':<8} {'Vendor':<10} {'보관일수':<8} {'입고일':<12}")
        print("-" * 80)
        
        for item in long_stay_items[:20]:  # 상위 20개
            print(f"{item['warehouse']:<20} {item['case']:<15} {item['cbm']:<8.2f} {item['vendor']:<10} {item['days_stored']:<8} {item['storage_date']}")
        
        if not long_stay_items:
            print("장기 보관 품목이 없습니다.")
        
        return long_stay_items
    
    def calculate_turnover_rate(self):
        """재고 회전율 계산"""
        print("\n=== 창고별 재고 회전율 분석 ===")
        print("-" * 80)
        
        turnover_data = {}
        
        print(f"{'창고명':<20} {'평균보관일':<10} {'회전율':<8} {'최오래된품목':<12} {'최신품목':<12}")
        print("-" * 80)
        
        for warehouse, data in self.inventory_data.items():
            if data['total_count'] > 0:
                # 평균 보관 일수 계산
                avg_days = sum(item['days_stored'] for item in data['items']) / data['total_count']
                
                # 회전율 계산 (연간 기준)
                turnover_rate = 365 / avg_days if avg_days > 0 else 0
                
                oldest_days = max(item['days_stored'] for item in data['items'])
                newest_days = min(item['days_stored'] for item in data['items'])
                
                turnover_data[warehouse] = {
                    'avg_days': avg_days,
                    'turnover_rate': turnover_rate,
                    'oldest_days': oldest_days,
                    'newest_days': newest_days
                }
                
                print(f"{warehouse:<20} {avg_days:<10.1f} {turnover_rate:<8.2f} {oldest_days:<12} {newest_days:<12}")
        
        return turnover_data
    
    def generate_inventory_alerts(self):
        """재고 알림 생성"""
        print("\n=== 재고 관리 알림 ===")
        print("-" * 80)
        
        alerts = []
        
        # 1. 고용량 창고 알림
        for warehouse, data in self.inventory_data.items():
            if data['total_count'] > self.alert_thresholds['high_volume']:
                alerts.append({
                    'type': 'HIGH_VOLUME',
                    'warehouse': warehouse,
                    'message': f"고용량 재고: {data['total_count']}건 ({data['total_cbm']:.2f} CBM)",
                    'priority': 'HIGH'
                })
        
        # 2. 용량 초과 위험 알림
        for warehouse, data in self.capacity_data.items():
            if data['utilization_rate'] >= self.alert_thresholds['capacity_limit']:
                alerts.append({
                    'type': 'CAPACITY_RISK',
                    'warehouse': warehouse,
                    'message': f"용량 한계 근접: {data['utilization_rate']:.1f}% 사용",
                    'priority': 'CRITICAL'
                })
        
        # 3. 장기 보관 알림
        long_stay_count = 0
        for warehouse, data in self.inventory_data.items():
            long_stay_in_warehouse = sum(1 for item in data['items'] 
                                       if item['days_stored'] > self.alert_thresholds['long_stay'])
            if long_stay_in_warehouse > 0:
                long_stay_count += long_stay_in_warehouse
                alerts.append({
                    'type': 'LONG_STAY',
                    'warehouse': warehouse,
                    'message': f"장기 보관 품목: {long_stay_in_warehouse}건",
                    'priority': 'MEDIUM'
                })
        
        # 알림 출력
        if alerts:
            for alert in alerts:
                priority_symbol = {
                    'CRITICAL': '[!!!]',
                    'HIGH': '[!!]',
                    'MEDIUM': '[!]'
                }
                print(f"{priority_symbol[alert['priority']]} {alert['warehouse']}: {alert['message']}")
        else:
            print("현재 알림이 없습니다.")
        
        return alerts
    
    def generate_optimization_recommendations(self):
        """재고 최적화 제안"""
        print("\n=== 재고 최적화 제안 ===")
        print("-" * 80)
        
        recommendations = []
        
        # 1. 재고 재배치 제안
        high_util_warehouses = [w for w, d in self.capacity_data.items() 
                               if d['utilization_rate'] > 80]
        low_util_warehouses = [w for w, d in self.capacity_data.items() 
                              if d['utilization_rate'] < 40]
        
        if high_util_warehouses and low_util_warehouses:
            recommendations.append({
                'type': 'REBALANCE',
                'message': f"재고 재배치 제안: {', '.join(high_util_warehouses)} -> {', '.join(low_util_warehouses)}"
            })
        
        # 2. 장기 보관 품목 처리 제안
        long_stay_total = sum(len([item for item in data['items'] 
                                 if item['days_stored'] > self.alert_thresholds['long_stay']]) 
                            for data in self.inventory_data.values())
        
        if long_stay_total > 0:
            recommendations.append({
                'type': 'LONG_STAY_ACTION',
                'message': f"장기 보관 품목 {long_stay_total}건 처리 필요 (출고 또는 이동)"
            })
        
        # 3. 용량 확장 제안
        critical_warehouses = [w for w, d in self.capacity_data.items() 
                             if d['utilization_rate'] > 90]
        
        if critical_warehouses:
            recommendations.append({
                'type': 'CAPACITY_EXPANSION',
                'message': f"용량 확장 검토 필요: {', '.join(critical_warehouses)}"
            })
        
        # 제안 출력
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['message']}")
        
        if not recommendations:
            print("현재 최적화 제안이 없습니다. 시스템이 효율적으로 운영되고 있습니다.")
        
        return recommendations
    
    def generate_inventory_summary(self):
        """재고 요약 정보 생성"""
        print("\n=== 재고 현황 요약 ===")
        print("-" * 50)
        
        total_items = sum(data['total_count'] for data in self.inventory_data.values())
        total_cbm = sum(data['total_cbm'] for data in self.inventory_data.values())
        total_capacity = sum(self.warehouse_capacity.values())
        overall_utilization = (total_cbm / total_capacity) * 100
        
        active_warehouses = len([w for w, d in self.inventory_data.items() if d['total_count'] > 0])
        
        print(f"전체 재고 현황:")
        print(f"- 총 품목: {total_items:,}건")
        print(f"- 총 CBM: {total_cbm:,.2f}")
        print(f"- 전체 용량: {total_capacity:,.2f}")
        print(f"- 전체 활용률: {overall_utilization:.1f}%")
        print(f"- 활성 창고: {active_warehouses}개")
        
        # 가장 효율적/비효율적 창고
        if self.capacity_data:
            best_warehouse = max(self.capacity_data.items(), 
                               key=lambda x: x[1]['utilization_rate'] if x[1]['utilization_rate'] < 90 else 0)
            worst_warehouse = min(self.capacity_data.items(), 
                                key=lambda x: x[1]['utilization_rate'])
            
            print(f"- 최적 활용 창고: {best_warehouse[0]} ({best_warehouse[1]['utilization_rate']:.1f}%)")
            print(f"- 저활용 창고: {worst_warehouse[0]} ({worst_warehouse[1]['utilization_rate']:.1f}%)")
    
    def run_warehouse_inventory_analysis(self):
        """전체 창고 재고 분석 실행"""
        print("MACHO-GPT Warehouse Inventory System v3.4-mini")
        print("=" * 60)
        print("Command: /warehouse-inventory --real-time")
        print("=" * 60)
        
        # 1. 데이터 로드
        if not self.load_rdf_data():
            print("[ERROR] 데이터 로드 실패")
            return False
        
        # 2. 현재 재고 분석
        self.analyze_current_inventory()
        
        # 3. 용량 활용도 분석
        self.calculate_capacity_utilization()
        
        # 4. 회전율 분석
        turnover_data = self.calculate_turnover_rate()
        
        # 5. 장기 보관 품목 식별
        long_stay_items = self.identify_long_stay_items()
        
        # 6. 알림 생성
        alerts = self.generate_inventory_alerts()
        
        # 7. 최적화 제안
        recommendations = self.generate_optimization_recommendations()
        
        # 8. 요약 정보
        self.generate_inventory_summary()
        
        print(f"\n=== 분석 완료 ===")
        print(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"다음 업데이트: 1시간 후")
        
        return {
            'inventory_data': self.inventory_data,
            'capacity_data': self.capacity_data,
            'turnover_data': turnover_data,
            'long_stay_items': long_stay_items,
            'alerts': alerts,
            'recommendations': recommendations
        }

def main():
    """메인 실행 함수"""
    inventory_system = MACHOWarehouseInventory()
    results = inventory_system.run_warehouse_inventory_analysis()
    
    # 추천 명령어
    print(f"\n추천 명령어:")
    print("  /flow-optimization [물류 흐름 최적화 분석]")
    print("  /monthly-report [월별 재고 리포트 생성]")
    print("  /capacity-planning [창고 용량 계획 수립]")

if __name__ == "__main__":
    main() 