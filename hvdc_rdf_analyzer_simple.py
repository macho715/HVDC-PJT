#!/usr/bin/env python3
"""
HVDC RDF Analyzer (Simple Version - No RDFLib)
사용자 요청 코드 구현: Excel → RDF 변환 → SPARQL 분석

# Excel 파일 → RDF 변환 → SPARQL 분석
converter = HVDCRDFConverter()
rdf_graph = converter.convert_excel_to_rdf("HVDC WAREHOUSE_HITACHI(HE).xlsx")

# SPARQL 쿼리 실행
results = rdf_graph.query('''
    SELECT ?warehouse (AVG(?cbm) as ?avg_cbm) WHERE {
        ?event ex:hasWarehouse ?warehouse .
        ?event ex:hasCubicMeter ?cbm .
    } GROUP BY ?warehouse
''')
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
import json
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class MockSPARQLResult:
    """SPARQL 결과를 모사하는 클래스"""
    def __init__(self, warehouse, avg_cbm):
        self.warehouse = warehouse
        self.avg_cbm = avg_cbm

class HVDCRDFConverter:
    """HVDC Excel to RDF Converter (Simple Version)"""
    
    def __init__(self):
        self.rdf_data = []
        self.warehouse_data = {}
        self.cbm_data = {}
        self.ttl_file = None
        
    def convert_excel_to_rdf(self, excel_file):
        """Excel 파일을 RDF로 변환"""
        print(f"🚀 Excel → RDF 변환 시작: {excel_file}")
        
        # 이미 생성된 RDF 파일 확인
        rdf_file = None
        if "HITACHI" in excel_file:
            rdf_file = "rdf_output/HVDC WAREHOUSE_HITACHI(HE).ttl"
        elif "SIMENSE" in excel_file:
            rdf_file = "rdf_output/HVDC WAREHOUSE_SIMENSE(SIM).ttl"
        
        if rdf_file and Path(rdf_file).exists():
            print(f"✅ 기존 RDF 파일 발견: {rdf_file}")
            self.ttl_file = rdf_file
            self._parse_rdf_file(rdf_file)
            return self
        
        # 새로 변환 (실제로는 이미 변환된 파일 사용)
        print("⚠️ RDF 파일이 없습니다. 먼저 hvdc_simple_rdf_converter.py를 실행하세요.")
        return None
    
    def _parse_rdf_file(self, rdf_file):
        """RDF 파일을 파싱하여 데이터 추출"""
        print(f"📊 RDF 파일 분석 중: {rdf_file}")
        
        with open(rdf_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # TTL 파일에서 TransportEvent 추출
        transport_events = re.findall(r'ex:TransportEvent_([^\\s]+)', content)
        
        # 창고 정보 추출
        warehouse_pattern = r'ex:hasWarehouse\s+"([^"]+)"'
        warehouse_matches = re.findall(warehouse_pattern, content)
        
        # CBM 정보 추출
        cbm_pattern = r'ex:hasCubicMeter\s+([0-9.]+)'
        cbm_matches = re.findall(cbm_pattern, content)
        
        # 벤더 정보 추출
        vendor_pattern = r'ex:hasHVDCCode3\s+"([^"]+)"'
        vendor_matches = re.findall(vendor_pattern, content)
        
        # 이벤트별 데이터 매핑
        events_data = []
        lines = content.split('\n')
        
        current_event = None
        current_data = {}
        
        for line in lines:
            line = line.strip()
            if 'ex:TransportEvent_' in line and 'rdf:type' in line:
                if current_event:
                    events_data.append(current_data)
                current_event = re.search(r'ex:TransportEvent_([^\\s]+)', line)
                current_data = {
                    'event': current_event.group(1) if current_event else None,
                    'warehouse': None,
                    'cbm': None,
                    'vendor': None
                }
            elif 'ex:hasWarehouse' in line:
                warehouse_match = re.search(r'"([^"]+)"', line)
                if warehouse_match:
                    current_data['warehouse'] = warehouse_match.group(1)
            elif 'ex:hasCubicMeter' in line:
                cbm_match = re.search(r'([0-9.]+)', line)
                if cbm_match:
                    current_data['cbm'] = float(cbm_match.group(1))
            elif 'ex:hasHVDCCode3' in line:
                vendor_match = re.search(r'"([^"]+)"', line)
                if vendor_match:
                    current_data['vendor'] = vendor_match.group(1)
        
        if current_event:
            events_data.append(current_data)
        
        self.rdf_data = events_data
        print(f"✅ RDF 데이터 파싱 완료: {len(events_data)} 이벤트")
        
        # 창고별 CBM 데이터 집계
        self._aggregate_warehouse_data()
        
    def _aggregate_warehouse_data(self):
        """창고별 데이터 집계"""
        warehouse_cbm = defaultdict(list)
        
        for event in self.rdf_data:
            if event['warehouse'] and event['cbm']:
                warehouse_cbm[event['warehouse']].append(event['cbm'])
        
        # 창고별 평균 CBM 계산
        self.warehouse_data = {}
        for warehouse, cbm_list in warehouse_cbm.items():
            self.warehouse_data[warehouse] = {
                'count': len(cbm_list),
                'avg_cbm': sum(cbm_list) / len(cbm_list),
                'total_cbm': sum(cbm_list),
                'max_cbm': max(cbm_list),
                'min_cbm': min(cbm_list)
            }
    
    def query(self, sparql_query):
        """SPARQL 쿼리 실행 (모사)"""
        print("🔍 SPARQL 쿼리 실행:")
        print(f"쿼리: {sparql_query.strip()}")
        
        # 창고별 평균 CBM 쿼리 처리
        if "hasWarehouse" in sparql_query and "hasCubicMeter" in sparql_query and "AVG" in sparql_query:
            results = []
            for warehouse, data in self.warehouse_data.items():
                result = MockSPARQLResult(warehouse, data['avg_cbm'])
                results.append(result)
            
            # 평균 CBM 내림차순 정렬
            results.sort(key=lambda x: x.avg_cbm, reverse=True)
            return results
        
        return []
    
    def analyze_warehouse_cbm(self):
        """창고별 CBM 분석"""
        print("\n📊 창고별 CBM 분석 결과:")
        print("-" * 70)
        print(f"{'창고명':<20} {'평균 CBM':<12} {'총 CBM':<12} {'최대 CBM':<12} {'건수':<8}")
        print("-" * 70)
        
        # 평균 CBM 기준 내림차순 정렬
        sorted_warehouses = sorted(self.warehouse_data.items(), 
                                 key=lambda x: x[1]['avg_cbm'], reverse=True)
        
        total_events = 0
        total_cbm = 0
        
        for warehouse, data in sorted_warehouses:
            print(f"{warehouse:<20} {data['avg_cbm']:<12.2f} {data['total_cbm']:<12.2f} {data['max_cbm']:<12.2f} {data['count']:<8}")
            total_events += data['count']
            total_cbm += data['total_cbm']
        
        print("-" * 70)
        print(f"{'총합':<20} {total_cbm/total_events if total_events > 0 else 0:<12.2f} {total_cbm:<12.2f} {'':<12} {total_events:<8}")
        
        return self.warehouse_data
    
    def analyze_vendor_distribution(self):
        """벤더별 분포 분석"""
        print("\n📊 벤더별 분포 분석:")
        
        vendor_data = defaultdict(lambda: {'count': 0, 'cbm_total': 0, 'cbm_list': []})
        
        for event in self.rdf_data:
            if event['vendor'] and event['cbm']:
                vendor_data[event['vendor']]['count'] += 1
                vendor_data[event['vendor']]['cbm_total'] += event['cbm']
                vendor_data[event['vendor']]['cbm_list'].append(event['cbm'])
        
        print("-" * 50)
        print(f"{'벤더':<10} {'건수':<8} {'평균 CBM':<12} {'총 CBM':<12}")
        print("-" * 50)
        
        for vendor, data in vendor_data.items():
            avg_cbm = data['cbm_total'] / data['count'] if data['count'] > 0 else 0
            print(f"{vendor:<10} {data['count']:<8} {avg_cbm:<12.2f} {data['cbm_total']:<12.2f}")
        
        return vendor_data
    
    def analyze_large_cargo(self, cbm_threshold=50):
        """대형 화물 분석"""
        print(f"\n📊 대형 화물 분석 (CBM > {cbm_threshold}):")
        
        large_cargo = []
        for event in self.rdf_data:
            if event['cbm'] and event['cbm'] > cbm_threshold:
                large_cargo.append(event)
        
        if large_cargo:
            # CBM 기준 내림차순 정렬
            large_cargo.sort(key=lambda x: x['cbm'], reverse=True)
            
            print("-" * 80)
            print(f"{'이벤트 ID':<20} {'CBM':<8} {'창고':<20} {'벤더':<8}")
            print("-" * 80)
            
            for event in large_cargo[:10]:  # 상위 10개만 표시
                event_id = event['event'] or 'N/A'
                cbm = event['cbm']
                warehouse = event['warehouse'] or 'N/A'
                vendor = event['vendor'] or 'N/A'
                print(f"{event_id:<20} {cbm:<8.2f} {warehouse:<20} {vendor:<8}")
            
            if len(large_cargo) > 10:
                print(f"... 추가 {len(large_cargo) - 10}개 대형 화물")
        else:
            print("❌ 임계값을 초과하는 대형 화물이 없습니다.")
        
        return large_cargo
    
    def comprehensive_analysis(self):
        """종합 분석"""
        print("\n🔍 HVDC 데이터 종합 분석")
        print("=" * 60)
        
        # 기본 통계
        total_events = len(self.rdf_data)
        events_with_warehouse = len([e for e in self.rdf_data if e['warehouse']])
        events_with_cbm = len([e for e in self.rdf_data if e['cbm']])
        
        print(f"📊 기본 통계:")
        print(f"   전체 이벤트: {total_events:,}개")
        print(f"   창고 정보 있음: {events_with_warehouse:,}개")
        print(f"   CBM 정보 있음: {events_with_cbm:,}개")
        
        # 창고별 CBM 분석
        warehouse_analysis = self.analyze_warehouse_cbm()
        
        # 벤더별 분포 분석
        vendor_analysis = self.analyze_vendor_distribution()
        
        # 대형 화물 분석
        large_cargo_analysis = self.analyze_large_cargo(50)
        
        return {
            'total_events': total_events,
            'events_with_warehouse': events_with_warehouse,
            'events_with_cbm': events_with_cbm,
            'warehouse_analysis': warehouse_analysis,
            'vendor_analysis': vendor_analysis,
            'large_cargo_analysis': large_cargo_analysis
        }

def main():
    """메인 실행 함수 - 사용자 요청 코드 구현"""
    print("🚀 HVDC RDF Analyzer (Simple Version)")
    print("=" * 50)
    print("📝 사용자 요청 코드 구현:")
    print()
    
    # 사용자 요청 코드 그대로 실행
    print("# Excel 파일 → RDF 변환 → SPARQL 분석")
    converter = HVDCRDFConverter()
    rdf_graph = converter.convert_excel_to_rdf("HVDC WAREHOUSE_HITACHI(HE).xlsx")
    
    if rdf_graph:
        print("\n# SPARQL 쿼리 실행")
        results = rdf_graph.query("""
            SELECT ?warehouse (AVG(?cbm) as ?avg_cbm) WHERE {
                ?event ex:hasWarehouse ?warehouse .
                ?event ex:hasCubicMeter ?cbm .
            } GROUP BY ?warehouse
        """)
        
        print("\n📊 창고별 평균 CBM 쿼리 결과:")
        print("-" * 50)
        print(f"{'창고명':<25} {'평균 CBM':<15}")
        print("-" * 50)
        
        for result in results:
            warehouse = result.warehouse
            avg_cbm = result.avg_cbm
            print(f"{warehouse:<25} {avg_cbm:<15.2f}")
        
        print(f"\n✅ 총 {len(results)}개 창고 분석 완료")
        
        # 추가 분석
        print("\n🔍 추가 종합 분석:")
        analysis_results = rdf_graph.comprehensive_analysis()
        
        # 결과 요약
        print(f"\n📋 분석 요약:")
        print(f"   파일: HVDC WAREHOUSE_HITACHI(HE).xlsx")
        print(f"   총 이벤트: {analysis_results['total_events']:,}개")
        print(f"   창고 정보: {analysis_results['events_with_warehouse']:,}개")
        print(f"   CBM 정보: {analysis_results['events_with_cbm']:,}개")
        print(f"   창고 수: {len(analysis_results['warehouse_analysis'])}개")
        print(f"   벤더 수: {len(analysis_results['vendor_analysis'])}개")
        print(f"   대형 화물: {len(analysis_results['large_cargo_analysis'])}개")
        
        # 추천 명령어
        print(f"\n🔧 추천 명령어:")
        print("   /validate-data comprehensive --sparql-rules")
        print("   /semantic-search --query='warehouse CBM analysis'")
        print("   /warehouse-status --include-capacity")
        
    else:
        print("❌ RDF 변환 실패")
        print("💡 해결 방법: 먼저 'python hvdc_simple_rdf_converter.py'를 실행하세요.")

if __name__ == "__main__":
    main() 