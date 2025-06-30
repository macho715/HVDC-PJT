#!/usr/bin/env python3
"""
HVDC 온톨로지 검증 엔진
- rdflib SPARQL ASK/CONSTRUCT + (선택) pyshacl
"""
import argparse, configparser, pathlib, json
from datetime import datetime
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

EX = Namespace("http://samsung.com/project-logistics#")

# ────────────────────────── SPARQL 제약식 ──────────────────────────
SPARQL_RULES = {
    "class_hierarchy": """
        ASK WHERE { ?w a ex:IndoorWarehouse . FILTER NOT EXISTS { ?w a ex:Warehouse } }
    """,
    "amount_non_negative": """
        ASK WHERE { ?e a ex:TransportEvent ; ex:hasAmount ?amt . FILTER(?amt < 0) }
    """,
    "package_count_positive": """
        ASK WHERE { ?e a ex:TransportEvent ; ex:hasPackageCount ?pkg . FILTER(?pkg < 1) }
    """,
    "cbm_positive": """
        ASK WHERE { ?e a ex:TransportEvent ; ex:hasCBM ?cbm . FILTER(?cbm <= 0) }
    """,
    "data_source_required": """
        ASK WHERE { ?e a ex:TransportEvent . FILTER NOT EXISTS { ?e ex:hasDataSource ?src } }
    """,
    "high_value_tag": """
        CONSTRUCT {
            ?e a ex:HighValueCargo .
        } WHERE {
            ?e a ex:TransportEvent ; ex:hasAmount ?amt .
            FILTER(?amt > 100000 && NOT EXISTS { ?e a ex:HighValueCargo })
        }
    """,
    "large_cargo_tag": """
        CONSTRUCT {
            ?e a ex:LargeCargo .
        } WHERE {
            ?e a ex:TransportEvent ; ex:hasCBM ?cbm .
            FILTER(?cbm > 50 && NOT EXISTS { ?e a ex:LargeCargo })
        }
    """,
    "indoor_storage_type": """
        CONSTRUCT {
            ?e ex:hasStorageType "indoor" .
        } WHERE {
            ?e a ex:TransportEvent ; ex:hasLocation ?loc .
            ?loc a ex:IndoorWarehouse .
            FILTER NOT EXISTS { ?e ex:hasStorageType ?type }
        }
    """,
    "outdoor_storage_type": """
        CONSTRUCT {
            ?e ex:hasStorageType "outdoor" .
        } WHERE {
            ?e a ex:TransportEvent ; ex:hasLocation ?loc .
            ?loc a ex:OutdoorWarehouse .
            FILTER NOT EXISTS { ?e ex:hasStorageType ?type }
        }
    """
}

def run_sparql_checks(graph: Graph) -> dict:
    """SPARQL ASK/CONSTRUCT 기반 검증·자동태깅"""
    print("🔍 SPARQL 규칙 기반 검증 시작...")
    
    result = {"violations": [], "constructs": [], "stats": {}}
    
    # 기본 통계
    total_events = len(list(graph.subjects(RDF.type, EX.TransportEvent)))
    total_triples = len(graph)
    result["stats"]["total_events"] = total_events
    result["stats"]["total_triples_before"] = total_triples
    
    print(f"   📊 총 TransportEvent: {total_events}개")
    print(f"   📊 총 트리플: {total_triples:,}개")
    
    for rule_name, q in SPARQL_RULES.items():
        try:
            if q.strip().upper().startswith("ASK"):
                # ASK 쿼리: 위반 사항 확인
                violated = graph.query(q, initNs={"ex": EX})
                if bool(violated):  # ASK returns True ⇒ 위반
                    result["violations"].append({
                        "rule": rule_name,
                        "description": get_rule_description(rule_name),
                        "severity": get_rule_severity(rule_name)
                    })
                    print(f"   ❌ 위반: {rule_name}")
                else:
                    print(f"   ✅ 통과: {rule_name}")
            else:
                # CONSTRUCT 쿼리: 새 트리플 생성
                new_triples = graph.query(q, initNs={"ex": EX})
                added = 0
                for s, p, o in new_triples:
                    graph.add((s, p, o))
                    added += 1
                if added > 0:
                    result["constructs"].append({
                        "rule": rule_name, 
                        "triples_added": added,
                        "description": get_rule_description(rule_name)
                    })
                    print(f"   🔄 구성: {rule_name} → {added}개 트리플 추가")
        except Exception as e:
            print(f"   ⚠️ {rule_name} 실행 오류: {e}")
            result["violations"].append({
                "rule": rule_name,
                "description": f"규칙 실행 오류: {e}",
                "severity": "error"
            })
    
    # 최종 통계
    final_triples = len(graph)
    result["stats"]["total_triples_after"] = final_triples
    result["stats"]["triples_added"] = final_triples - total_triples
    
    return result

def get_rule_description(rule_name: str) -> str:
    """규칙별 설명 반환"""
    descriptions = {
        "class_hierarchy": "IndoorWarehouse가 Warehouse의 하위 클래스인지 확인",
        "amount_non_negative": "TransportEvent의 금액이 음수가 아닌지 확인",
        "package_count_positive": "TransportEvent의 패키지 수가 양수인지 확인",
        "cbm_positive": "TransportEvent의 CBM이 양수인지 확인",
        "data_source_required": "모든 TransportEvent가 데이터 소스를 가지는지 확인",
        "high_value_tag": "금액 100,000 초과 이벤트에 HighValueCargo 태그 자동 추가",
        "large_cargo_tag": "CBM 50 초과 이벤트에 LargeCargo 태그 자동 추가",
        "indoor_storage_type": "실내 창고 이벤트에 indoor 저장 타입 자동 추가",
        "outdoor_storage_type": "실외 창고 이벤트에 outdoor 저장 타입 자동 추가"
    }
    return descriptions.get(rule_name, "규칙 설명 없음")

def get_rule_severity(rule_name: str) -> str:
    """규칙별 심각도 반환"""
    severity_map = {
        "class_hierarchy": "high",
        "amount_non_negative": "high", 
        "package_count_positive": "high",
        "cbm_positive": "medium",
        "data_source_required": "medium"
    }
    return severity_map.get(rule_name, "low")

def create_ontology_schema():
    """기본 온톨로지 스키마 생성"""
    print("📜 기본 온톨로지 스키마 생성 중...")
    
    schema = Graph()
    schema.bind("ex", EX)
    schema.bind("rdf", RDF)
    schema.bind("rdfs", RDFS)
    
    # 클래스 정의
    classes = [
        (EX.Warehouse, "창고"),
        (EX.IndoorWarehouse, "실내 창고"),
        (EX.OutdoorWarehouse, "실외 창고"),
        (EX.DangerousCargoWarehouse, "위험물 창고"),
        (EX.Site, "현장"),
        (EX.TransportEvent, "운송 이벤트"),
        (EX.StockSnapshot, "재고 스냅샷"),
        (EX.Case, "케이스"),
        (EX.HighValueCargo, "고가 화물"),
        (EX.LargeCargo, "대형 화물")
    ]
    
    for class_uri, label in classes:
        schema.add((class_uri, RDF.type, RDFS.Class))
        schema.add((class_uri, RDFS.label, Literal(label, lang="ko")))
    
    # 클래스 계층
    hierarchies = [
        (EX.IndoorWarehouse, RDFS.subClassOf, EX.Warehouse),
        (EX.OutdoorWarehouse, RDFS.subClassOf, EX.Warehouse),
        (EX.DangerousCargoWarehouse, RDFS.subClassOf, EX.Warehouse),
        (EX.Site, RDFS.subClassOf, EX.Warehouse),
        (EX.HighValueCargo, RDFS.subClassOf, EX.TransportEvent),
        (EX.LargeCargo, RDFS.subClassOf, EX.TransportEvent)
    ]
    
    for subclass, predicate, superclass in hierarchies:
        schema.add((subclass, predicate, superclass))
    
    # 속성 정의
    properties = [
        (EX.hasAmount, "금액"),
        (EX.hasCBM, "부피(CBM)"),
        (EX.hasPackageCount, "패키지 수"),
        (EX.hasLocation, "위치"),
        (EX.hasDataSource, "데이터 소스"),
        (EX.hasStorageType, "저장 타입"),
        (EX.hasCaseNo, "케이스 번호"),
        (EX.hasWeight, "무게"),
        (EX.hasOperationMonth, "작업 월"),
        (EX.hasCategory, "카테고리"),
        (EX.hasContainerType, "컨테이너 타입")
    ]
    
    for prop_uri, label in properties:
        schema.add((prop_uri, RDF.type, RDF.Property))
        schema.add((prop_uri, RDFS.label, Literal(label, lang="ko")))
    
    # 도메인/범위 정의
    domain_ranges = [
        (EX.hasAmount, RDFS.domain, EX.TransportEvent),
        (EX.hasCBM, RDFS.domain, EX.TransportEvent),
        (EX.hasPackageCount, RDFS.domain, EX.TransportEvent),
        (EX.hasLocation, RDFS.domain, EX.TransportEvent),
        (EX.hasDataSource, RDFS.domain, EX.TransportEvent)
    ]
    
    for prop, predicate, class_uri in domain_ranges:
        schema.add((prop, predicate, class_uri))
    
    return schema

def generate_validation_report(report_data: dict, output_dir: pathlib.Path) -> pathlib.Path:
    """상세 검증 리포트 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # HTML 리포트 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HVDC 온톨로지 검증 리포트</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .violations {{ background: #fff5f5; border-left: 4px solid #e53e3e; padding: 15px; margin: 10px 0; }}
        .constructs {{ background: #f0fff4; border-left: 4px solid #38a169; padding: 15px; margin: 10px 0; }}
        .severity-high {{ color: #e53e3e; font-weight: bold; }}
        .severity-medium {{ color: #dd6b20; font-weight: bold; }}
        .severity-low {{ color: #38a169; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 HVDC 온톨로지 검증 리포트</h1>
        <p>생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>총 이벤트</h3>
            <p style="font-size: 24px; color: #667eea;">{report_data['stats'].get('total_events', 0):,}</p>
        </div>
        <div class="stat-box">
            <h3>총 트리플</h3>
            <p style="font-size: 24px; color: #764ba2;">{report_data['stats'].get('total_triples_after', 0):,}</p>
        </div>
        <div class="stat-box">
            <h3>추가된 트리플</h3>
            <p style="font-size: 24px; color: #38a169;">+{report_data['stats'].get('triples_added', 0):,}</p>
        </div>
        <div class="stat-box">
            <h3>위반 사항</h3>
            <p style="font-size: 24px; color: #e53e3e;">{len(report_data['violations'])}</p>
        </div>
    </div>
"""
    
    # 위반 사항
    if report_data['violations']:
        html_content += """
    <h2>❌ 검증 위반 사항</h2>
"""
        for violation in report_data['violations']:
            severity_class = f"severity-{violation.get('severity', 'low')}"
            html_content += f"""
    <div class="violations">
        <h3>{violation['rule']}</h3>
        <p><strong>심각도:</strong> <span class="{severity_class}">{violation.get('severity', 'low').upper()}</span></p>
        <p><strong>설명:</strong> {violation['description']}</p>
    </div>"""
    else:
        html_content += """
    <div class="constructs">
        <h2>✅ 모든 검증 규칙 통과!</h2>
        <p>온톨로지 제약 조건을 모두 만족합니다.</p>
    </div>"""
    
    # 자동 구성
    if report_data['constructs']:
        html_content += """
    <h2>🔄 자동 태깅 및 추론 결과</h2>
"""
        for construct in report_data['constructs']:
            html_content += f"""
    <div class="constructs">
        <h3>{construct['rule']}</h3>
        <p><strong>추가된 트리플:</strong> {construct['triples_added']}개</p>
        <p><strong>설명:</strong> {construct['description']}</p>
    </div>"""
    
    html_content += """
</body>
</html>"""
    
    html_file = output_dir / f"validation_report_{timestamp}.html"
    html_file.write_text(html_content, encoding="utf-8")
    
    return html_file

# ────────────────────────────── main ──────────────────────────────
def main():
    print("🔍 /cmd_validate_ontology 실행")
    print("=" * 70)
    print("🤖 HVDC 온톨로지 검증 엔진 (Pure Python)")
    print("=" * 70)
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="settings.ini", help="설정 파일 경로")
    ap.add_argument("--export-fixed", help="수정된 그래프 TTL 저장 경로")
    ap.add_argument("--create-schema", action="store_true", help="기본 온톨로지 스키마 생성")
    args = ap.parse_args()

    # 설정 파일 읽기
    cfg = configparser.ConfigParser()
    if pathlib.Path(args.config).exists():
        cfg.read(args.config, encoding='utf-8')
    else:
        print(f"⚠️ 설정 파일 {args.config}가 없습니다. 기본값 사용.")
        cfg.add_section('paths')
        cfg.set('paths', 'ontology', 'ontology/hvdc_schema.ttl')
        cfg.set('paths', 'data_graph', 'reasoning_output/hvdc_graph.ttl')
        cfg.add_section('validation')
        cfg.set('validation', 'report_dir', 'reasoning_output/validation')
    
    onto_path = pathlib.Path(cfg["paths"]["ontology"])
    data_path = pathlib.Path(cfg["paths"]["data_graph"])
    report_dir = pathlib.Path(cfg["validation"]["report_dir"])
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # 온톨로지 디렉토리 생성
    onto_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1) 온톨로지 스키마 생성 (없는 경우)
    if args.create_schema or not onto_path.exists():
        print("📜 온톨로지 스키마 생성 중...")
        schema = create_ontology_schema()
        schema.serialize(destination=str(onto_path), format="turtle")
        print(f"✅ 온톨로지 스키마 생성: {onto_path}")
    
    # 2) 데이터 그래프 확인
    if not data_path.exists():
        print(f"❌ 데이터 그래프 파일이 없습니다: {data_path}")
        print("💡 먼저 /cmd_ontology_reasoning을 실행하여 데이터를 생성하세요.")
        
        # 샘플 데이터 그래프 생성
        print("🔄 샘플 데이터 그래프 생성 중...")
        sample_graph = Graph()
        sample_graph.bind("ex", EX)
        
        # 샘플 데이터 추가
        sample_graph.add((EX.event001, RDF.type, EX.TransportEvent))
        sample_graph.add((EX.event001, EX.hasAmount, Literal(150000)))
        sample_graph.add((EX.event001, EX.hasCBM, Literal(75.5)))
        sample_graph.add((EX.event001, EX.hasPackageCount, Literal(10)))
        sample_graph.add((EX.event001, EX.hasDataSource, Literal("HITACHI")))
        
        sample_graph.add((EX.warehouse001, RDF.type, EX.IndoorWarehouse))
        sample_graph.add((EX.warehouse001, RDF.type, EX.Warehouse))
        sample_graph.add((EX.event001, EX.hasLocation, EX.warehouse001))
        
        data_path.parent.mkdir(parents=True, exist_ok=True)
        sample_graph.serialize(destination=str(data_path), format="turtle")
        print(f"✅ 샘플 데이터 그래프 생성: {data_path}")

    # 3) 그래프 로드 (스키마 + 데이터 머지)
    print("📚 그래프 로드 중...")
    g = Graph()
    
    if onto_path.exists():
        g.parse(str(onto_path))
        print(f"   ✅ 온톨로지 로드: {onto_path}")
    
    if data_path.exists():
        g.parse(str(data_path))
        print(f"   ✅ 데이터 로드: {data_path}")
    
    g.bind("ex", EX)

    # 4) 규칙 기반 검증
    report = run_sparql_checks(g)

    # 5) (선택) pyshacl 추가 검증
    try:
        print("🔍 SHACL 검증 시도 중...")
        from pyshacl import validate
        conforms, _, shacl_text = validate(
            data_graph=g, 
            shacl_graph=g, 
            inference='rdfs', 
            serialize_report_graph=True
        )
        report["shacl_conforms"] = conforms
        if not conforms:
            shacl_file = report_dir / "shacl_report.html"
            shacl_file.write_text(shacl_text, encoding="utf-8")
            print(f"   ⚠️ SHACL 위반 발견 → {shacl_file}")
        else:
            print("   ✅ SHACL 검증 통과")
    except ImportError:
        report["shacl_conforms"] = "pyshacl not installed"
        print("   ℹ️ pyshacl이 설치되지 않음 (선택사항)")
    except Exception as e:
        report["shacl_conforms"] = f"SHACL 검증 오류: {e}"
        print(f"   ⚠️ SHACL 검증 오류: {e}")

    # 6) 리포트 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON 리포트
    json_file = report_dir / f"validation_{data_path.stem}_{timestamp}.json"
    json_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # HTML 리포트
    html_file = generate_validation_report(report, report_dir)
    
    print(f"\n✅ 검증 완료!")
    print(f"   📊 JSON 리포트: {json_file}")
    print(f"   📝 HTML 리포트: {html_file}")

    # 7) 수정된 그래프 내보내기
    if args.export_fixed:
        export_path = pathlib.Path(args.export_fixed)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        g.serialize(destination=str(export_path), format="turtle")
        print(f"🔄 추가 태그 포함 그래프 → {export_path}")
    
    # 결과 요약
    print("\n📊 검증 결과 요약:")
    print(f"   • 총 이벤트: {report['stats'].get('total_events', 0):,}개")
    print(f"   • 총 트리플: {report['stats'].get('total_triples_after', 0):,}개")
    print(f"   • 추가된 트리플: +{report['stats'].get('triples_added', 0):,}개")
    print(f"   • 위반 사항: {len(report['violations'])}개")
    print(f"   • 자동 구성: {len(report['constructs'])}개")
    
    if report['violations']:
        print("\n❌ 위반 사항:")
        for violation in report['violations']:
            severity = violation.get('severity', 'low').upper()
            print(f"   • {violation['rule']} [{severity}]")
    
    if report['constructs']:
        print("\n🔄 자동 추가:")
        for construct in report['constructs']:
            print(f"   • {construct['rule']}: +{construct['triples_added']}개 트리플")

if __name__ == "__main__":
    main() 