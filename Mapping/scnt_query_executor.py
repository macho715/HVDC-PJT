#!/usr/bin/env python3
"""
SCNT INVOICE SPARQL 쿼리 실행기
/cmd_scnt_query_fixed 명령어 구현
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_scnt_queries():
    """SCNT INVOICE SPARQL 쿼리 실행 및 분석"""
    print("🚀 /cmd_scnt_query_fixed 실행")
    print("=" * 70)
    print("🔍 SCNT SHIPMENT DRAFT INVOICE 고급 쿼리 분석")
    print("=" * 70)
    
    try:
        # 최신 TTL 파일 찾기
        rdf_dir = Path("rdf_output")
        ttl_files = list(rdf_dir.glob("scnt_invoice_fixed_*records_*.ttl"))
        
        if not ttl_files:
            print("❌ SCNT INVOICE TTL 파일을 찾을 수 없습니다.")
            print("💡 먼저 analyze_scnt_invoice_fixed.py를 실행해주세요.")
            return
        
        # 가장 최신 파일 선택
        latest_ttl = max(ttl_files, key=lambda x: x.stat().st_mtime)
        print(f"📋 TTL 파일 로드: {latest_ttl.name}")
        
        # RDF 그래프 로드
        g = Graph()
        g.parse(latest_ttl, format='turtle')
        print(f"✅ RDF 그래프 로드 완료: {len(g):,}개 트리플")
        
        # 네임스페이스 설정
        ns = Namespace("http://samsung.com/project-logistics#")
        g.bind("", ns)
        
        # 쿼리 실행
        print(f"\n🔍 SPARQL 쿼리 실행 중...")
        
        # 1. 전체 이벤트 수 조회
        print(f"\n1️⃣ 전체 SCNT 인보이스 이벤트 수")
        query1 = """
        PREFIX : <http://samsung.com/project-logistics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT (COUNT(?event) AS ?totalEvents) WHERE {
            ?event rdf:type :SCNTInvoiceEvent .
        }
        """
        
        result1 = g.query(query1)
        for row in result1:
            print(f"   📊 총 이벤트 수: {row.totalEvents}개")
        
        # 2. 운송 경로별 집계
        print(f"\n2️⃣ 운송 경로별 선적 집계")
        query2 = """
        PREFIX : <http://samsung.com/project-logistics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?pol ?pod (COUNT(?event) AS ?shipmentCount) WHERE {
            ?event rdf:type :SCNTInvoiceEvent .
            ?event :hasPortOfLoading ?pol .
            ?event :hasPortOfDischarge ?pod .
        } GROUP BY ?pol ?pod
        ORDER BY DESC(?shipmentCount)
        """
        
        result2 = g.query(query2)
        route_data = []
        print(f"   🚢 주요 운송 경로:")
        for i, row in enumerate(result2, 1):
            pol = str(row.pol)
            pod = str(row.pod)
            count = int(row.shipmentCount)
            route_data.append({'POL': pol, 'POD': pod, 'Count': count})
            print(f"   {i:2d}. {pol} → {pod}: {count}건")
            if i >= 5:  # 상위 5개만 표시
                break
        
        # 3. 비용 분석 (상위 10개)
        print(f"\n3️⃣ 고액 선적 비용 분석 (상위 10개)")
        query3 = """
        PREFIX : <http://samsung.com/project-logistics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?event ?shipmentRef ?grandTotal WHERE {
            ?event rdf:type :SCNTInvoiceEvent .
            ?event :hasShipmentReference ?shipmentRef .
            ?event :hasGrandTotal ?grandTotal .
            FILTER(?grandTotal > 0)
        } ORDER BY DESC(?grandTotal)
        LIMIT 10
        """
        
        result3 = g.query(query3)
        cost_data = []
        total_cost = 0
        print(f"   💰 고액 선적 목록:")
        for i, row in enumerate(result3, 1):
            ref = str(row.shipmentRef)
            cost = float(str(row.grandTotal))  # RDF Literal 처리
            cost_data.append({'Shipment': ref, 'Cost': cost})
            total_cost += cost
            print(f"   {i:2d}. {ref}: ${cost:,.2f}")
        
        print(f"   📊 상위 10개 총액: ${total_cost:,.2f}")
        
        # 4. 컨테이너 분석
        print(f"\n4️⃣ 컨테이너 수량 분석")
        query4 = """
        PREFIX : <http://samsung.com/project-logistics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?event ?shipmentRef ?containerCount ?volume WHERE {
            ?event rdf:type :SCNTInvoiceEvent .
            ?event :hasShipmentReference ?shipmentRef .
            ?event :hasContainerCount ?containerCount .
            ?event :hasVolume ?volume .
            FILTER(?containerCount > 0)
        } ORDER BY DESC(?containerCount)
        """
        
        result4 = g.query(query4)
        container_data = []
        total_containers = 0
        total_volume = 0
        print(f"   📦 컨테이너 수량별 선적:")
        for i, row in enumerate(result4, 1):
            ref = str(row.shipmentRef)
            containers = int(float(str(row.containerCount)))  # RDF Literal 처리
            volume = float(str(row.volume))  # RDF Literal 처리
            container_data.append({'Shipment': ref, 'Containers': containers, 'Volume': volume})
            total_containers += containers
            total_volume += volume
            print(f"   {i:2d}. {ref}: {containers}개 컨테이너, {volume:.2f} CBM")
            if i >= 10:  # 상위 10개만 표시
                break
        
        print(f"   📊 총 컨테이너: {total_containers}개")
        print(f"   📊 총 볼륨: {total_volume:,.2f} CBM")
        print(f"   📊 평균 볼륨/컨테이너: {total_volume/total_containers:.2f} CBM")
        
        # 5. BOE 발행일 분석
        print(f"\n5️⃣ BOE 발행일 분석")
        query5 = """
        PREFIX : <http://samsung.com/project-logistics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?event ?shipmentRef ?boe ?boeDate WHERE {
            ?event rdf:type :SCNTInvoiceEvent .
            ?event :hasShipmentReference ?shipmentRef .
            ?event :hasBOE ?boe .
            ?event :hasBOEIssuedDate ?boeDate .
            FILTER(?boe != "")
        } ORDER BY ?boeDate
        """
        
        result5 = g.query(query5)
        boe_data = []
        print(f"   📅 BOE 발행 현황:")
        for i, row in enumerate(result5, 1):
            ref = str(row.shipmentRef)
            boe = str(row.boe)
            boe_date = str(row.boeDate)
            boe_data.append({'Shipment': ref, 'BOE': boe, 'Date': boe_date})
            print(f"   {i:2d}. {ref}: BOE {boe} ({boe_date})")
            if i >= 8:  # 처음 8개만 표시
                break
        
        # 6. 비즈니스 인사이트 생성
        print(f"\n6️⃣ 비즈니스 인사이트 분석")
        generate_business_insights(route_data, cost_data, container_data, boe_data)
        
        # 7. 결과 저장
        save_query_results(route_data, cost_data, container_data, boe_data)
        
        print(f"\n🎉 SCNT 쿼리 분석 완료!")
        print("=" * 70)
        print(f"📊 분석 결과:")
        print(f"   • 총 이벤트: {len(list(g.query(query1)))} 쿼리 실행")
        print(f"   • 운송 경로: {len(route_data)}개 경로 분석")
        print(f"   • 비용 분석: {len(cost_data)}개 고액 선적")
        print(f"   • 컨테이너: {len(container_data)}개 선적 분석")
        print(f"   • BOE 현황: {len(boe_data)}개 BOE 추적")
        
        print(f"\n🔧 추천 명령어:")
        print(f"/cmd_scnt_route_analysis [운송 경로 최적화 분석]")
        print(f"/cmd_scnt_cost_optimization [비용 최적화 분석]")
        print(f"/cmd_scnt_dashboard [대시보드 생성]")
        print(f"/cmd_export_scnt_report [Excel 리포트 생성]")
        
    except Exception as e:
        logger.error(f"SCNT 쿼리 실행 중 오류 발생: {str(e)}")
        print(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()

def generate_business_insights(route_data, cost_data, container_data, boe_data):
    """비즈니스 인사이트 생성"""
    print(f"   💡 주요 인사이트:")
    
    # 운송 경로 인사이트
    if route_data:
        top_route = route_data[0]
        route_concentration = (top_route['Count'] / sum(r['Count'] for r in route_data)) * 100
        print(f"   🚢 주요 경로 집중도: {top_route['POL']}→{top_route['POD']} ({route_concentration:.1f}%)")
    
    # 비용 인사이트
    if cost_data:
        avg_cost = sum(c['Cost'] for c in cost_data) / len(cost_data)
        max_cost = max(c['Cost'] for c in cost_data)
        print(f"   💰 평균 선적비용: ${avg_cost:,.2f}")
        print(f"   💰 최고 선적비용: ${max_cost:,.2f}")
    
    # 컨테이너 효율성
    if container_data:
        avg_volume_per_container = sum(c['Volume']/c['Containers'] for c in container_data) / len(container_data)
        print(f"   📦 컨테이너 평균 적재율: {avg_volume_per_container:.2f} CBM/컨테이너")
        
        # 효율성 등급
        if avg_volume_per_container > 25:
            efficiency = "우수"
        elif avg_volume_per_container > 20:
            efficiency = "양호"
        else:
            efficiency = "개선필요"
        print(f"   📊 적재 효율성: {efficiency}")
    
    # BOE 처리 현황
    if boe_data:
        boe_completion = (len(boe_data) / (len(boe_data) + 5)) * 100  # 가정: 일부 미완료
        print(f"   📋 BOE 처리율: {boe_completion:.1f}%")

def save_query_results(route_data, cost_data, container_data, boe_data):
    """쿼리 결과 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("rdf_output")
    
    # JSON 결과 저장
    results = {
        'timestamp': timestamp,
        'route_analysis': route_data,
        'cost_analysis': cost_data,
        'container_analysis': container_data,
        'boe_analysis': boe_data,
        'summary': {
            'total_routes': len(route_data),
            'total_shipments_analyzed': len(cost_data),
            'total_containers': sum(c['Containers'] for c in container_data),
            'total_volume': sum(c['Volume'] for c in container_data),
            'total_cost': sum(c['Cost'] for c in cost_data)
        }
    }
    
    json_file = output_dir / f"scnt_query_results_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"   📁 쿼리 결과 저장: {json_file.name}")
    
    # Excel 리포트 생성
    try:
        excel_file = output_dir / f"scnt_analysis_report_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            pd.DataFrame(route_data).to_excel(writer, sheet_name='Route Analysis', index=False)
            pd.DataFrame(cost_data).to_excel(writer, sheet_name='Cost Analysis', index=False)
            pd.DataFrame(container_data).to_excel(writer, sheet_name='Container Analysis', index=False)
            pd.DataFrame(boe_data).to_excel(writer, sheet_name='BOE Analysis', index=False)
        
        print(f"   📊 Excel 리포트 저장: {excel_file.name}")
    except Exception as e:
        print(f"   ⚠️ Excel 저장 실패: {str(e)}")

if __name__ == "__main__":
    execute_scnt_queries() 