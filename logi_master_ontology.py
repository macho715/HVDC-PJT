# logi_master_ontology.py - logi-master 명령어 온톨로지 통합
"""
기존 logi_meta_fixed.py와 연동하여 온톨로지 기능을 제공하는 확장 모듈
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse
from hvdc_ontology_engine import HVDCOntologyEngine, HVDCItem, Warehouse

class LogiMasterOntology:
    """logi-master 명령어 온톨로지 통합 클래스"""
    
    def __init__(self):
        self.engine = HVDCOntologyEngine()
        self.command_registry = {}
        self.setup_commands()
        
    def setup_commands(self):
        """명령어 등록"""
        self.command_registry = {
            'warehouse-status': self.cmd_warehouse_status,
            'invoice-audit': self.cmd_invoice_audit,
            'risk-check': self.cmd_risk_check,
            'track-items': self.cmd_track_items,
            'capacity-forecast': self.cmd_capacity_forecast,
            'validate-ontology': self.cmd_validate_ontology,
            'semantic-search': self.cmd_semantic_search,
            'load-excel': self.cmd_load_excel,
            'export-rdf': self.cmd_export_rdf
        }
        
    def execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """명령어 실행"""
        if command not in self.command_registry:
            return {
                "status": "ERROR",
                "message": f"알 수 없는 명령어: {command}",
                "available_commands": list(self.command_registry.keys())
            }
            
        try:
            return self.command_registry[command](**kwargs)
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"명령어 실행 실패: {str(e)}"
            }
    
    def cmd_warehouse_status(self, **kwargs) -> Dict[str, Any]:
        """창고 현황 조회"""
        include_capacity = kwargs.get('include_capacity', False)
        location = kwargs.get('location', 'all')
        
        df = self.engine.get_warehouse_utilization()
        
        if location != 'all':
            df = df[df['name'].str.contains(location, case=False)]
            
        result = {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "total_warehouses": len(df),
            "warehouses": df.to_dict('records')
        }
        
        if include_capacity:
            result["capacity_summary"] = {
                "total_capacity": float(df['capacity_sqm'].sum()),
                "total_utilization": float(df['current_utilization'].sum()),
                "average_utilization_percent": float(df['utilization_percent'].mean())
            }
            
        return result
    
    def cmd_invoice_audit(self, **kwargs) -> Dict[str, Any]:
        """Invoice 감사"""
        tolerance = kwargs.get('tolerance', 0.03)  # 3% 허용 오차
        auto_approve = kwargs.get('auto_approve', False)
        
        # 간단한 Invoice 검증 시뮬레이션
        cursor = self.engine.conn.cursor()
        cursor.execute('''
            SELECT hvdc_code, vendor, weight 
            FROM items 
            WHERE status = 'warehouse'
        ''')
        
        items = cursor.fetchall()
        audit_results = []
        
        for item in items:
            hvdc_code, vendor, weight = item
            
            # 가상의 계약 요율 vs 실제 요율 비교
            contract_rate = 50.0  # USD per ton (예시)
            actual_rate = contract_rate + (hash(hvdc_code) % 10 - 5) * contract_rate * 0.02
            
            variance = abs(actual_rate - contract_rate) / contract_rate
            
            if variance > tolerance:
                status = "FLAGGED"
                action = "MANUAL_REVIEW"
            else:
                status = "APPROVED" if auto_approve else "PENDING"
                action = "AUTO_APPROVED" if auto_approve else "READY_FOR_APPROVAL"
                
            audit_results.append({
                "hvdc_code": hvdc_code,
                "vendor": vendor,
                "contract_rate": contract_rate,
                "actual_rate": round(actual_rate, 2),
                "variance_percent": round(variance * 100, 2),
                "status": status,
                "action": action
            })
            
        flagged_count = sum(1 for r in audit_results if r['status'] == 'FLAGGED')
        
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "total_items": len(audit_results),
            "flagged_items": flagged_count,
            "approval_rate": round((len(audit_results) - flagged_count) / len(audit_results) * 100, 2),
            "tolerance_percent": tolerance * 100,
            "results": audit_results[:10]  # 처음 10개만 반환
        }
    
    def cmd_risk_check(self, **kwargs) -> Dict[str, Any]:
        """위험 아이템 체크"""
        threshold = kwargs.get('threshold', 'high')
        cost_alert = kwargs.get('cost_alert', False)
        
        # 중량 기준 위험도 분류
        weight_thresholds = {
            'low': 5000,
            'medium': 15000, 
            'high': 25000
        }
        
        min_weight = weight_thresholds.get(threshold, 25000)
        
        cursor = self.engine.conn.cursor()
        cursor.execute('''
            SELECT hvdc_code, vendor, category, weight, location, status
            FROM items 
            WHERE weight > ?
            ORDER BY weight DESC
        ''', (min_weight,))
        
        risk_items = []
        total_risk_cost = 0
        
        for item in cursor.fetchall():
            hvdc_code, vendor, category, weight, location, status = item
            
            # 위험도 평가
            if weight > 50000:
                risk_level = "CRITICAL"
                estimated_cost = 5000
            elif weight > 25000:
                risk_level = "HIGH"
                estimated_cost = 2000
            else:
                risk_level = "MEDIUM"
                estimated_cost = 500
                
            total_risk_cost += estimated_cost
            
            risk_item = {
                "hvdc_code": hvdc_code,
                "vendor": vendor,
                "weight": weight,
                "location": location,
                "risk_level": risk_level,
                "estimated_handling_cost": estimated_cost
            }
            
            if cost_alert:
                risk_item["cost_alert"] = estimated_cost > 1000
                
            risk_items.append(risk_item)
            
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "threshold": threshold,
            "min_weight": min_weight,
            "total_risk_items": len(risk_items),
            "total_estimated_cost": total_risk_cost,
            "risk_items": risk_items
        }
    
    def cmd_track_items(self, **kwargs) -> Dict[str, Any]:
        """아이템 추적"""
        warehouse = kwargs.get('warehouse')
        vendor = kwargs.get('vendor')
        status = kwargs.get('status')
        
        cursor = self.engine.conn.cursor()
        
        # 동적 쿼리 빌드
        where_clauses = []
        params = []
        
        if warehouse:
            where_clauses.append("location LIKE ?")
            params.append(f"%{warehouse}%")
            
        if vendor:
            where_clauses.append("vendor LIKE ?")
            params.append(f"%{vendor}%")
            
        if status:
            where_clauses.append("status = ?")
            params.append(status)
            
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f'''
            SELECT hvdc_code, vendor, category, weight, location, status
            FROM items 
            WHERE {where_sql}
            ORDER BY weight DESC
        '''
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        tracked_items = []
        for item in items:
            tracked_items.append({
                "hvdc_code": item[0],
                "vendor": item[1],
                "category": item[2],
                "weight": item[3],
                "location": item[4],
                "status": item[5]
            })
            
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "filters": {
                "warehouse": warehouse,
                "vendor": vendor,
                "status": status
            },
            "total_items": len(tracked_items),
            "items": tracked_items
        }
    
    def cmd_capacity_forecast(self, **kwargs) -> Dict[str, Any]:
        """창고 용량 예측"""
        warehouse = kwargs.get('warehouse', 'all')
        horizon = kwargs.get('horizon', '3_months')
        
        df = self.engine.get_warehouse_utilization()
        
        if warehouse != 'all':
            df = df[df['name'].str.contains(warehouse, case=False)]
            
        # 간단한 선형 예측 (실제로는 더 복잡한 모델 사용)
        forecasts = []
        
        for _, row in df.iterrows():
            current_util = row['utilization_percent']
            capacity = row['capacity_sqm']
            
            # 월 5% 증가 가정
            if horizon == '3_months':
                months = 3
            elif horizon == '6_months':
                months = 6
            else:
                months = 3
                
            projected_util = current_util + (months * 5)  # 월 5% 증가
            
            status = "NORMAL"
            if projected_util > 90:
                status = "CRITICAL"
            elif projected_util > 80:
                status = "WARNING"
                
            forecasts.append({
                "warehouse": row['name'],
                "current_utilization": round(current_util, 2),
                "projected_utilization": round(projected_util, 2),
                "months_to_capacity": max(0, round((95 - current_util) / 5, 1)),
                "status": status
            })
            
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "horizon": horizon,
            "warehouse_filter": warehouse,
            "forecasts": forecasts
        }
    
    def cmd_validate_ontology(self, **kwargs) -> Dict[str, Any]:
        """온톨로지 검증"""
        all_items = kwargs.get('all', False)
        
        # 기본 무결성 체크
        cursor = self.engine.conn.cursor()
        
        # 1. 중복 코드 체크
        cursor.execute('''
            SELECT hvdc_code, COUNT(*) as cnt 
            FROM items 
            GROUP BY hvdc_code 
            HAVING COUNT(*) > 1
        ''')
        duplicates = cursor.fetchall()
        
        # 2. 필수 필드 누락 체크
        cursor.execute('''
            SELECT hvdc_code 
            FROM items 
            WHERE vendor IS NULL OR vendor = '' 
               OR location IS NULL OR location = ''
        ''')
        missing_fields = cursor.fetchall()
        
        # 3. 비정상 중량 체크
        cursor.execute('''
            SELECT hvdc_code, weight 
            FROM items 
            WHERE weight <= 0 OR weight > 100000
        ''')
        abnormal_weights = cursor.fetchall()
        
        validation_results = {
            "duplicate_codes": len(duplicates),
            "missing_required_fields": len(missing_fields),
            "abnormal_weights": len(abnormal_weights),
            "duplicates": duplicates,
            "missing_fields": missing_fields,
            "abnormal_weights_list": abnormal_weights
        }
        
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "validation_results": validation_results
        }
    
    def cmd_semantic_search(self, **kwargs) -> Dict[str, Any]:
        """시맨틱 검색"""
        query_text = kwargs.get('query_text', '')
        results = self.engine.semantic_search(query_text)
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "query": query_text,
            "results": results
        }
    
    def cmd_load_excel(self, **kwargs) -> Dict[str, Any]:
        """엑셀 데이터 로드"""
        filepath = kwargs.get('filepath')
        sheet_name = kwargs.get('sheet_name', 'Sheet1')
        count = self.engine.load_from_excel(filepath, sheet_name)
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "loaded_count": count,
            "filepath": filepath,
            "sheet_name": sheet_name
        }
    
    def cmd_export_rdf(self, **kwargs) -> Dict[str, Any]:
        """RDF 내보내기"""
        filepath = kwargs.get('filepath', 'hvdc_ontology.ttl')
        success = self.engine.export_to_turtle(filepath)
        return {
            "status": "SUCCESS" if success else "ERROR",
            "timestamp": datetime.now().isoformat(),
            "filepath": filepath
        }

# CLI 인터페이스
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="logi-master 온톨로지 명령어 확장")
    parser.add_argument("command", help="실행할 명령어")
    parser.add_argument("--kwargs", help="명령어 인자(JSON)", default="{}")
    args = parser.parse_args()
    kwargs = json.loads(args.kwargs)
    lmo = LogiMasterOntology()
    result = lmo.execute_command(args.command, **kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2)) 