#!/usr/bin/env python3
"""
HVDC 입고/출고 분석 시스템
Inbound/Outbound Analysis System for HVDC Warehouse Operations

Features:
- 창고별 입고/출고 현황 분석
- 날짜별 입출고 패턴 분석  
- 재고 상태 추적
- 물류 흐름 최적화 인사이트
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class HVDCInboundOutboundAnalyzer:
    """HVDC 입고/출고 분석기"""
    
    def __init__(self):
        self.rdf_data = []
        self.warehouse_movements = {}
        self.inbound_data = {}
        self.outbound_data = {}
        
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
        
        # 현장 속성 매핑
        self.site_properties = {
            'hasDAS': 'DAS',
            'hasAGI': 'AGI', 
            'hasSHU': 'SHU',
            'hasMIR': 'MIR'
        }
    
    def load_rdf_data(self, rdf_file="rdf_output/HVDC WAREHOUSE_HITACHI(HE).ttl"):
        """RDF 파일에서 데이터 로드"""
        print(f"📊 입고/출고 데이터 로드: {rdf_file}")
        
        if not Path(rdf_file).exists():
            print(f"❌ 파일을 찾을 수 없습니다: {rdf_file}")
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
                
                # 이벤트 데이터 추출
                event_data = {
                    'event': event_id,
                    'case': None,
                    'cbm': None,
                    'vendor': None,
                    'warehouse_timeline': [],  # 창고별 날짜 정보
                    'site_timeline': []        # 현장별 날짜 정보
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
                
                # 현장별 날짜 정보 추출
                for prop, site_name in self.site_properties.items():
                    date_pattern = rf'ex:{prop}\s+"?([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})"?\^\^xsd:date'
                    date_match = re.search(date_pattern, event_content)
                    if date_match:
                        date_str = date_match.group(1)
                        event_data['site_timeline'].append({
                            'site': site_name,
                            'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                            'date_str': date_str
                        })
                
                # 시간순 정렬
                event_data['warehouse_timeline'].sort(key=lambda x: x['date'])
                event_data['site_timeline'].sort(key=lambda x: x['date'])
                
                events_data.append(event_data)
        
        self.rdf_data = events_data
        print(f"✅ 데이터 로드 완료: {len(events_data)} 이벤트")
        return True
    
    def analyze_warehouse_movements(self):
        """창고별 입고/출고 분석"""
        print("\n📊 창고별 입고/출고 분석")
        print("=" * 80)
        
        # 창고별 입고/출고 데이터 집계
        warehouse_stats = defaultdict(lambda: {
            'inbound': [],     # 입고 (다른 창고에서 들어옴)
            'outbound': [],    # 출고 (다른 창고로 나감)
            'inventory': [],   # 재고 (현재 보관 중)
            'total_cbm': 0,
            'total_cases': 0
        })
        
        for event in self.rdf_data:
            if not event['warehouse_timeline']:
                continue
                
            warehouses = event['warehouse_timeline']
            cbm = event['cbm'] or 0
            case = event['case']
            
            for i, wh_info in enumerate(warehouses):
                warehouse = wh_info['warehouse']
                
                # 입고 분석 (이전 창고에서 온 경우)
                if i > 0:
                    prev_warehouse = warehouses[i-1]['warehouse']
                    warehouse_stats[warehouse]['inbound'].append({
                        'from': prev_warehouse,
                        'date': wh_info['date'],
                        'case': case,
                        'cbm': cbm,
                        'event': event['event']
                    })
                
                # 출고 분석 (다음 창고로 가는 경우)
                if i < len(warehouses) - 1:
                    next_warehouse = warehouses[i+1]['warehouse']
                    warehouse_stats[warehouse]['outbound'].append({
                        'to': next_warehouse,
                        'date': wh_info['date'],
                        'case': case,
                        'cbm': cbm,
                        'event': event['event']
                    })
                
                # 최종 창고인 경우 재고로 분류
                if i == len(warehouses) - 1:
                    # 현장으로 이동하지 않은 경우만 재고로 간주
                    if not event['site_timeline']:
                        warehouse_stats[warehouse]['inventory'].append({
                            'case': case,
                            'cbm': cbm,
                            'date': wh_info['date'],
                            'event': event['event']
                        })
                
                warehouse_stats[warehouse]['total_cbm'] += cbm
                warehouse_stats[warehouse]['total_cases'] += 1
        
        self.warehouse_movements = dict(warehouse_stats)
        return self.warehouse_movements
    
    def print_inbound_outbound_summary(self):
        """입고/출고 요약 출력"""
        if not self.warehouse_movements:
            self.analyze_warehouse_movements()
        
        print(f"\n📋 창고별 입고/출고 요약")
        print("-" * 100)
        print(f"{'창고명':<20} {'입고 건수':<10} {'입고 CBM':<12} {'출고 건수':<10} {'출고 CBM':<12} {'재고 건수':<10} {'재고 CBM':<12}")
        print("-" * 100)
        
        total_inbound = 0
        total_outbound = 0
        total_inventory = 0
        
        # 입고/출고 건수 기준 정렬
        sorted_warehouses = sorted(
            self.warehouse_movements.items(),
            key=lambda x: len(x[1]['inbound']) + len(x[1]['outbound']),
            reverse=True
        )
        
        for warehouse, stats in sorted_warehouses:
            inbound_count = len(stats['inbound'])
            inbound_cbm = sum(item['cbm'] for item in stats['inbound'])
            
            outbound_count = len(stats['outbound'])
            outbound_cbm = sum(item['cbm'] for item in stats['outbound'])
            
            inventory_count = len(stats['inventory'])
            inventory_cbm = sum(item['cbm'] for item in stats['inventory'])
            
            print(f"{warehouse:<20} {inbound_count:<10} {inbound_cbm:<12.2f} {outbound_count:<10} {outbound_cbm:<12.2f} {inventory_count:<10} {inventory_cbm:<12.2f}")
            
            total_inbound += inbound_count
            total_outbound += outbound_count
            total_inventory += inventory_count
        
        print("-" * 100)
        print(f"{'총계':<20} {total_inbound:<10} {'':<12} {total_outbound:<10} {'':<12} {total_inventory:<10} {'':<12}")
    
    def analyze_monthly_patterns(self):
        """월별 입고/출고 패턴 분석"""
        print(f"\n📅 월별 입고/출고 패턴 분석")
        print("-" * 80)
        
        monthly_data = defaultdict(lambda: {'inbound': 0, 'outbound': 0, 'cbm_inbound': 0, 'cbm_outbound': 0})
        
        for warehouse, stats in self.warehouse_movements.items():
            # 입고 데이터
            for item in stats['inbound']:
                month_key = item['date'].strftime('%Y-%m')
                monthly_data[month_key]['inbound'] += 1
                monthly_data[month_key]['cbm_inbound'] += item['cbm']
            
            # 출고 데이터
            for item in stats['outbound']:
                month_key = item['date'].strftime('%Y-%m')
                monthly_data[month_key]['outbound'] += 1
                monthly_data[month_key]['cbm_outbound'] += item['cbm']
        
        print(f"{'월':<10} {'입고 건수':<10} {'입고 CBM':<12} {'출고 건수':<10} {'출고 CBM':<12} {'순증감':<10}")
        print("-" * 80)
        
        sorted_months = sorted(monthly_data.keys())
        for month in sorted_months:
            data = monthly_data[month]
            net_change = data['inbound'] - data['outbound']
            print(f"{month:<10} {data['inbound']:<10} {data['cbm_inbound']:<12.2f} {data['outbound']:<10} {data['cbm_outbound']:<12.2f} {net_change:<10}")
        
        return monthly_data
    
    def analyze_flow_efficiency(self):
        """물류 흐름 효율성 분석"""
        print(f"\n🔄 물류 흐름 효율성 분석")
        print("-" * 80)
        
        flow_patterns = defaultdict(int)
        flow_cbm = defaultdict(float)
        
        for event in self.rdf_data:
            if len(event['warehouse_timeline']) > 1:
                warehouses = [wh['warehouse'] for wh in event['warehouse_timeline']]
                cbm = event['cbm'] or 0
                
                # 창고 간 흐름 패턴 분석
                for i in range(len(warehouses) - 1):
                    flow = f"{warehouses[i]} → {warehouses[i+1]}"
                    flow_patterns[flow] += 1
                    flow_cbm[flow] += cbm
        
        print(f"{'흐름 패턴':<45} {'건수':<8} {'총 CBM':<12} {'평균 CBM':<12}")
        print("-" * 80)
        
        # 건수 기준 정렬
        sorted_flows = sorted(flow_patterns.items(), key=lambda x: x[1], reverse=True)
        
        for flow, count in sorted_flows[:15]:  # 상위 15개 흐름
            total_cbm = flow_cbm[flow]
            avg_cbm = total_cbm / count if count > 0 else 0
            print(f"{flow:<45} {count:<8} {total_cbm:<12.2f} {avg_cbm:<12.2f}")
        
        return flow_patterns, flow_cbm
    
    def check_inventory_status(self):
        """현재 재고 상태 확인"""
        print(f"\n📦 현재 재고 상태")
        print("-" * 80)
        
        if not self.warehouse_movements:
            self.analyze_warehouse_movements()
        
        total_inventory_cases = 0
        total_inventory_cbm = 0
        
        print(f"{'창고명':<25} {'재고 건수':<10} {'재고 CBM':<12} {'평균 CBM':<12}")
        print("-" * 80)
        
        # 재고 많은 순으로 정렬
        sorted_inventory = sorted(
            self.warehouse_movements.items(),
            key=lambda x: len(x[1]['inventory']),
            reverse=True
        )
        
        for warehouse, stats in sorted_inventory:
            inventory_count = len(stats['inventory'])
            inventory_cbm = sum(item['cbm'] for item in stats['inventory'])
            avg_cbm = inventory_cbm / inventory_count if inventory_count > 0 else 0
            
            if inventory_count > 0:
                print(f"{warehouse:<25} {inventory_count:<10} {inventory_cbm:<12.2f} {avg_cbm:<12.2f}")
                total_inventory_cases += inventory_count
                total_inventory_cbm += inventory_cbm
        
        print("-" * 80)
        print(f"{'총 재고':<25} {total_inventory_cases:<10} {total_inventory_cbm:<12.2f} {total_inventory_cbm/total_inventory_cases if total_inventory_cases > 0 else 0:<12.2f}")
        
        return total_inventory_cases, total_inventory_cbm
    
    def generate_recommendations(self):
        """개선 방안 제안"""
        print(f"\n💡 입고/출고 최적화 제안")
        print("=" * 80)
        
        # 분석 데이터 기반 제안
        if not self.warehouse_movements:
            self.analyze_warehouse_movements()
        
        recommendations = []
        
        # 1. 재고 과다 창고 식별
        high_inventory = []
        for warehouse, stats in self.warehouse_movements.items():
            inventory_count = len(stats['inventory'])
            if inventory_count > 100:  # 임계값
                high_inventory.append((warehouse, inventory_count))
        
        if high_inventory:
            high_inventory.sort(key=lambda x: x[1], reverse=True)
            recommendations.append(f"🔴 재고 과다 창고: {high_inventory[0][0]} ({high_inventory[0][1]}건)")
            recommendations.append(f"   → 출고 계획 수립 및 재고 회전율 개선 필요")
        
        # 2. 비효율적 흐름 패턴 식별
        flow_patterns, flow_cbm = self.analyze_flow_efficiency()
        inefficient_flows = []
        
        for flow, count in flow_patterns.items():
            if "→" in flow and count < 10:  # 소량 흐름
                inefficient_flows.append(flow)
        
        if inefficient_flows:
            recommendations.append(f"🟡 비효율적 흐름: {len(inefficient_flows)}개 경로")
            recommendations.append(f"   → 직접 연결 경로 검토 및 중간 경유 최소화")
        
        # 3. 창고 활용도 분석
        utilization = {}
        for warehouse, stats in self.warehouse_movements.items():
            total_movements = len(stats['inbound']) + len(stats['outbound'])
            utilization[warehouse] = total_movements
        
        if utilization:
            max_util = max(utilization.values())
            min_util = min(utilization.values())
            
            if max_util > min_util * 3:  # 불균형 감지
                recommendations.append(f"🟠 창고 활용도 불균형 감지")
                recommendations.append(f"   → 저활용 창고의 역할 재정의 필요")
        
        # 제안 출력
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        if not recommendations:
            print("✅ 현재 입고/출고 시스템이 효율적으로 운영되고 있습니다.")
        
        return recommendations
    
    def comprehensive_analysis(self):
        """종합 입고/출고 분석"""
        print("🚀 HVDC 입고/출고 종합 분석")
        print("=" * 80)
        
        # 1. 창고 이동 분석
        movements = self.analyze_warehouse_movements()
        
        # 2. 입고/출고 요약
        self.print_inbound_outbound_summary()
        
        # 3. 월별 패턴 분석
        monthly_patterns = self.analyze_monthly_patterns()
        
        # 4. 흐름 효율성 분석
        flow_patterns, flow_cbm = self.analyze_flow_efficiency()
        
        # 5. 재고 상태 확인
        inventory_cases, inventory_cbm = self.check_inventory_status()
        
        # 6. 개선 제안
        recommendations = self.generate_recommendations()
        
        return {
            'movements': movements,
            'monthly_patterns': monthly_patterns,
            'flow_patterns': flow_patterns,
            'inventory_status': (inventory_cases, inventory_cbm),
            'recommendations': recommendations
        }

def main():
    """메인 실행 함수"""
    print("🏭 HVDC 입고/출고 분석 시스템")
    print("=" * 60)
    
    analyzer = HVDCInboundOutboundAnalyzer()
    
    # 데이터 로드
    if analyzer.load_rdf_data():
        # 종합 분석 실행
        results = analyzer.comprehensive_analysis()
        
        # 결과 요약
        print(f"\n📋 분석 완료 요약")
        print("-" * 40)
        print(f"분석 이벤트: {len(analyzer.rdf_data):,}개")
        print(f"분석 창고: {len(analyzer.warehouse_movements)}개")
        print(f"재고 현황: {results['inventory_status'][0]}건")
        print(f"재고 CBM: {results['inventory_status'][1]:.2f}")
        
        # 추천 명령어
        print(f"\n🔧 추천 명령어:")
        print("   /warehouse-inventory --real-time")
        print("   /flow-optimization --efficiency-analysis")
        print("   /monthly-report --inbound-outbound")
        
    else:
        print("❌ 데이터 로드 실패")
        print("💡 먼저 'python hvdc_simple_rdf_converter.py'를 실행하세요.")

if __name__ == "__main__":
    main() 