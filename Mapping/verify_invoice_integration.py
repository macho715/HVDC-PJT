#!/usr/bin/env python3

import json
import os

def verify_invoice_integration():
    """인보이스 매핑 통합 검증"""
    
    print("📊 HVDC 인보이스 매핑 통합 검증 v2.8.3")
    print("=" * 50)
    
    # 매핑 규칙 로드
    try:
        with open('mapping_rules_v2.8.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        print("✅ mapping_rules_v2.8.json 로드 성공")
    except Exception as e:
        print(f"❌ 매핑 규칙 로드 실패: {e}")
        return
    
    # 통계 출력
    field_count = len(mapping.get("field_map", {}))
    property_count = len(mapping.get("property_mappings", {}))
    class_count = len(mapping.get("class_mappings", {}))
    sparql_count = len(mapping.get("sparql_templates", {}))
    
    print(f"✅ 총 필드 매핑: {field_count}개")
    print(f"✅ 총 속성 매핑: {property_count}개") 
    print(f"✅ 총 클래스 매핑: {class_count}개")
    print(f"✅ 총 SPARQL 템플릿: {sparql_count}개")
    
    # 인보이스 관련 필드 확인
    invoice_keywords = ['invoice', 'rate', 'total', 'charge', 'customer', 'job', 'document', 'shpt', 'customs', 'detention']
    invoice_fields = []
    
    for field in mapping.get("field_map", {}).keys():
        if any(keyword in field.lower() for keyword in invoice_keywords):
            invoice_fields.append(field)
    
    print(f"\n🔍 인보이스 관련 필드 ({len(invoice_fields)}개):")
    for i, field in enumerate(invoice_fields[:10]):
        mapping_val = mapping["field_map"].get(field, "N/A")
        print(f"  {i+1:2d}. {field:25} → {mapping_val}")
    
    if len(invoice_fields) > 10:
        print(f"     ... 및 {len(invoice_fields) - 10}개 추가 필드")
    
    # 사용자 요청사항 확인
    print(f"\n🎯 사용자 요청사항 검증:")
    required_mappings = {
        "Sheet Name": "hasDocumentRef",
        "Order Ref. Number": "hasCase", 
        "SHPT NO": "hasShippingNumber"
    }
    
    for field, expected in required_mappings.items():
        actual = mapping.get("field_map", {}).get(field)
        status = "✅" if actual == expected else "❌"
        print(f"  {status} {field:20} → {actual or 'MISSING'}")
    
    # RDF 파일 확인
    rdf_file = "invoice_mapping_integration_v283.ttl"
    if os.path.exists(rdf_file):
        with open(rdf_file, 'r', encoding='utf-8') as f:
            rdf_content = f.read()
        rdf_lines = len(rdf_content.split('\n'))
        print(f"\n✅ RDF 온톨로지 파일: {rdf_file} ({rdf_lines} 라인)")
    else:
        print(f"\n❌ RDF 파일 없음: {rdf_file}")
    
    # 보고서 파일 확인
    report_file = "HVDC_Invoice_Mapping_Integration_Report.md"
    if os.path.exists(report_file):
        print(f"✅ 통합 보고서: {report_file}")
    else:
        print(f"❌ 보고서 없음: {report_file}")
    
    print(f"\n📈 통합 성과:")
    baseline = 37  # 기존 필드 수
    increase = ((field_count - baseline) / baseline * 100) if baseline > 0 else 0
    print(f"   기존: {baseline}개 → 현재: {field_count}개 ({increase:.0f}% 증가)")
    
    print(f"\n🏆 인보이스 매핑 통합 v2.8.3 검증 완료!")

if __name__ == "__main__":
    verify_invoice_integration() 