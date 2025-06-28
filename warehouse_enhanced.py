#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini WAREHOUSE Management Workflow
HVDC PROJECT - Samsung C&T Logistics | ADNOC·DSV Partnership

창고별/현장별/월별 입고/출고/재고 관리 시스템
실제 HVDC 데이터 구조 기반 (mapping_rules_v2.5.json 적용)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import logging
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HVDCWarehouseCommand:
    """MACHO-GPT WAREHOUSE 명령어 시스템"""
    
    def __init__(self):
        """실제 HVDC 창고 데이터 구조 초기화"""
        # 🔧 수정: 실제 mapping_rules_v2.6.json 기반 창고 분류
        self.real_data = {
            "warehouses": {
                "Indoor": ["DSV Indoor", "DSV Al Markaz", "Hauler Indoor"],
                "Outdoor": ["DSV Outdoor", "DSV MZP", "MOSB"],
                "Site": ["AGI", "DAS", "MIR", "SHU"],
                "dangerous_cargo": ["AAA Storage", "Dangerous Storage"]
            },
            "all_warehouses": [
                "DSV Indoor", "DSV Al Markaz", "Hauler Indoor",
                "DSV Outdoor", "DSV MZP", "MOSB",
                "AGI", "DAS", "MIR", "SHU",
                "AAA Storage", "Dangerous Storage"
            ],
            "sites": ["AGI", "DAS", "MIR", "SHU"],
            "warehouse_types": {
                "DSV Indoor": "Indoor",
                "DSV Al Markaz": "Indoor", 
                "Hauler Indoor": "Indoor",
                "DSV Outdoor": "Outdoor",
                "DSV MZP": "Outdoor",
                "MOSB": "Outdoor",
                "AGI": "Site",
                "DAS": "Site",
                "MIR": "Site",
                "SHU": "Site",
                "AAA Storage": "dangerous_cargo",
                "Dangerous Storage": "dangerous_cargo"
            }
        }
        
        # 수정: WAREHOUSE 폴더 경로 추가
        warehouse_path = os.path.join(os.path.dirname(__file__), "hvdc_macho_gpt", "WAREHOUSE")
        if warehouse_path not in sys.path:
            sys.path.append(warehouse_path)
            print(f"✅ WAREHOUSE 폴더 경로 추가: {warehouse_path}")
        
        # 🔧 수정: 실제 HVDC Excel 데이터 로드
        print("🔧 실제 HVDC Excel 데이터 로드 중...")
        self.df = self._load_real_hvdc_data()
        print(f"✅ 실제 데이터 로드 완료: {self.df.shape}")
        
        print("INFO:warehouse_enhanced:HVDC Warehouse Command System initialized (실제 데이터)")

    def _load_real_hvdc_data(self) -> pd.DataFrame:
        """실제 HVDC Excel 파일에서 데이터 로드"""
        try:
            # 실제 파일 경로들
            excel_files = [
                "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
                "hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx"
            ]
            
            all_data = []
            
            for excel_file in excel_files:
                if os.path.exists(excel_file):
                    print(f"✅ 실제 파일 로드: {os.path.basename(excel_file)}")
                    
                    try:
                        # Excel 파일 읽기
                        xl_file = pd.ExcelFile(excel_file)
                        
                        # Case List 시트 우선 선택
                        sheet_name = xl_file.sheet_names[0]
                        for sheet in xl_file.sheet_names:
                            if 'case' in sheet.lower() and 'list' in sheet.lower():
                                sheet_name = sheet
                                break
                        
                        df = pd.read_excel(excel_file, sheet_name=sheet_name)
                        
                        if not df.empty:
                            # 실제 데이터 전처리
                            processed_df = self._process_real_data(df, excel_file)
                            all_data.append(processed_df)
                            print(f"   ✅ {len(processed_df)}행 실제 데이터 처리")
                        
                    except Exception as e:
                        print(f"   ⚠️ 파일 로드 실패: {e}")
                        continue
            
            if all_data:
                # 모든 데이터 합치기
                combined_df = pd.concat(all_data, ignore_index=True)
                print(f"✅ 총 {len(combined_df)}행 실제 데이터 로드 완료")
                return combined_df
            else:
                print("⚠️ 실제 데이터 로드 실패, 샘플 데이터로 대체")
                return self._create_sample_hvdc_data()
            
        except Exception as e:
            print(f"❌ 실제 데이터 로드 오류: {e}")
            print("🔧 샘플 데이터로 대체")
            return self._create_sample_hvdc_data()

    def _process_real_data(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """실제 Excel 데이터 전처리"""
        processed_data = []
        
        # 날짜 컬럼들 찾기 (창고별 날짜 컬럼)
        date_columns = []
        for col in df.columns:
            if any(warehouse in str(col) for warehouse in self.real_data["all_warehouses"]):
                date_columns.append(col)
        
        # 케이스 컬럼 찾기
        case_col = self._find_case_column(df)
        if not case_col:
            case_col = 'Case'  # 기본값
        
        # 수량 컬럼 찾기
        qty_col = self._find_quantity_column(df)
        if not qty_col:
            qty_col = 'Pkg'  # 기본값
        
        for idx, row in df.iterrows():
            case_id = str(row[case_col]) if pd.notna(row[case_col]) else f"CASE_{idx}"
            quantity = int(row[qty_col]) if pd.notna(row[qty_col]) else 1
            
            # 각 날짜 컬럼에서 이벤트 추출
            for date_col in date_columns:
                if pd.notna(row[date_col]):
                    try:
                        event_date = pd.to_datetime(row[date_col])
                        warehouse = self._extract_warehouse_from_column(date_col)
                        
                        if warehouse in self.real_data["all_warehouses"]:
                            # 실제 트랜잭션 데이터 생성
                            processed_data.append({
                                'Date': event_date,
                                'Location': warehouse,
                                'Site': self._get_site_for_warehouse(warehouse),
                                'Incoming': quantity,
                                'Outgoing': 0,  # 실제 데이터에서는 입고만 기록
                                'Amount': quantity * 1000,  # 가상 가치 (실제로는 별도 계산 필요)
                                'YearMonth': pd.Period(event_date, freq='M'),
                                'Case_ID': case_id,
                                'Source_File': filename
                            })
                    except Exception as e:
                        continue
        
        return pd.DataFrame(processed_data)

    def _find_case_column(self, df: pd.DataFrame) -> str:
        """케이스 컬럼 찾기"""
        case_patterns = ['case', 'carton', 'box', 'mr#', 'mr #', 'sct ship no', 'case no']
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(pattern in col_lower for pattern in case_patterns):
                return col
        return None

    def _find_quantity_column(self, df: pd.DataFrame) -> str:
        """수량 컬럼 찾기"""
        qty_patterns = ['pkg', 'qty', 'quantity', 'pieces', 'piece', 'q\'ty']
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(pattern in col_lower for pattern in qty_patterns):
                return col
            return None

    def _extract_warehouse_from_column(self, col_name: str) -> str:
        """컬럼명에서 창고명 추출"""
        col_lower = str(col_name).lower().strip()
        
        warehouse_mapping = {
            'dsv indoor': 'DSV Indoor',
            'dsv al markaz': 'DSV Al Markaz',
            'dsv outdoor': 'DSV Outdoor',
            'hauler indoor': 'Hauler Indoor',
            'dsv mzp': 'DSV MZP',
            'mosb': 'MOSB',
            'agi': 'AGI',
            'das': 'DAS',
            'mir': 'MIR',
            'shu': 'SHU',
            'aaa storage': 'AAA Storage',
            'dangerous storage': 'Dangerous Storage'
        }
        
        for key, value in warehouse_mapping.items():
            if key in col_lower:
                return value
        
        return 'UNKNOWN'

    def _get_site_for_warehouse(self, warehouse: str) -> str:
        """창고에 해당하는 현장 반환"""
        site_mapping = {
            'AGI': 'AGI',
            'DAS': 'DAS', 
            'MIR': 'MIR',
            'SHU': 'SHU',
            'DSV Indoor': 'AGI',  # 가상 매핑
            'DSV Outdoor': 'DAS',  # 가상 매핑
            'MOSB': 'MIR',         # 가상 매핑
        }
        
        return site_mapping.get(warehouse, 'Unknown')

    def _create_sample_hvdc_data(self) -> pd.DataFrame:
        """실제 HVDC 구조 기반 샘플 데이터 생성"""
        np.random.seed(42)
        
        # 🔧 수정: 실제 창고 목록 사용
        warehouses = self.real_data["all_warehouses"]
        sites = self.real_data["sites"]
        
        # 날짜 범위 설정 (2025년 1월-6월)
        start_date = pd.Timestamp('2025-01-01')
        end_date = pd.Timestamp('2025-06-30')
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 샘플 데이터 생성
        data = []
        for _ in range(500):  # 500개 트랜잭션
            date = np.random.choice(date_range)
            warehouse = np.random.choice(warehouses)
            site = np.random.choice(sites)
            
            # 창고 타입별 특성 반영
            warehouse_type = self.real_data["warehouse_types"].get(warehouse, "Site")
            
            if warehouse_type == "Indoor":
                incoming = np.random.randint(50, 200)
                outgoing = np.random.randint(40, 180)
                amount = np.random.randint(5000, 25000)
            elif warehouse_type == "Outdoor":
                incoming = np.random.randint(80, 300)
                outgoing = np.random.randint(70, 280)
                amount = np.random.randint(8000, 35000)
            elif warehouse_type == "dangerous_cargo":
                incoming = np.random.randint(20, 100)
                outgoing = np.random.randint(15, 90)
                amount = np.random.randint(10000, 50000)
            else:  # Site
                incoming = np.random.randint(30, 150)
                outgoing = np.random.randint(25, 140)
                amount = np.random.randint(3000, 20000)
            
            data.append({
                'Date': date,
                'Location': warehouse,
                'Site': site,
                'Incoming': incoming,
                'Outgoing': outgoing,
                'Amount': amount,
                'YearMonth': pd.Period(date, freq='M')
            })
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        return df

    def logi_master_warehouse_status(self, warehouse_id: str = None) -> Dict[str, Any]:
        """
        /logi_master warehouse-status 명령어
        창고별 현재 상태 조회
        """
        print(f"📦 창고 상태 조회 중... (창고: {warehouse_id or '전체'})")
        
        if warehouse_id and warehouse_id not in self.real_data["warehouses"]:
            return {
                "status": "ERROR",
                "message": f"창고 '{warehouse_id}'를 찾을 수 없습니다.",
                "available_warehouses": self.real_data["warehouses"]
            }
        
        warehouses = [warehouse_id] if warehouse_id else self.real_data["warehouses"]
        results = {}
        
        for wh_id in warehouses:
            wh_data = self.df[self.df['Location'] == wh_id]
            
            # 기본 통계
            total_incoming = wh_data['Incoming'].sum()
            total_outgoing = wh_data['Outgoing'].sum()
            current_stock = total_incoming - total_outgoing
            total_value = wh_data['Amount'].sum()
            
            # 월별 현황
            monthly_data = wh_data.groupby('YearMonth').agg({
                'Incoming': 'sum',
                'Outgoing': 'sum',
                'Amount': 'sum'
            }).tail(6)  # 최근 6개월
            
            # 이동 평균 계산
            avg_monthly_in = monthly_data['Incoming'].mean()
            avg_monthly_out = monthly_data['Outgoing'].mean()
            
            # 회전율 계산
            turnover_rate = (total_outgoing / max(current_stock, 1)) * 100 if current_stock > 0 else 0
            
            results[wh_id] = {
                "basic_info": {
                    "warehouse_name": wh_id,
                    "current_stock": int(current_stock),
                    "total_value_aed": float(total_value),
                    "turnover_rate_percent": round(turnover_rate, 2)
                },
                "monthly_summary": {
                    "avg_monthly_incoming": round(avg_monthly_in, 1),
                    "avg_monthly_outgoing": round(avg_monthly_out, 1),
                    "recent_months": monthly_data.to_dict('index')
                },
                "alerts": self._generate_warehouse_alerts(wh_id, current_stock, avg_monthly_out)
            }
        
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "warehouses": results,
            "summary": {
                "total_warehouses": len(results),
                "total_stock_all": sum([r["basic_info"]["current_stock"] for r in results.values()]),
                "total_value_all": sum([r["basic_info"]["total_value_aed"] for r in results.values()])
            }
        }

    def _generate_warehouse_alerts(self, warehouse_id: str, current_stock: int, avg_monthly_out: float) -> List[str]:
        """창고별 알림 생성"""
        alerts = []
        
        # 재고 부족 알림
        if current_stock <= 0:
            alerts.append("🔴 재고 부족: 즉시 보충 필요")
        elif current_stock < avg_monthly_out * 0.5:
            alerts.append("🟡 재고 주의: 2주분 미만 재고")
        
        # 과재고 알림
        if current_stock > avg_monthly_out * 6:
            alerts.append("🔵 과재고 주의: 6개월분 초과 재고")
        
        # 창고별 특별 알림
        if warehouse_id in ['AGI', 'SHU', 'MIR', 'MOSB']:
            alerts.append("⚡ 현장 창고: 실시간 모니터링 중")
        
        return alerts

    def logi_master_warehouse_monthly(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """
        /logi_master warehouse-monthly 명령어
        월별 입고/출고/재고 분석
        """
        if year is None:
            year = datetime.now().year
        
        print(f"📊 월별 창고 분석 중... ({year}년 {month or '전체'}월)")
        
        # 데이터 필터링
        year_data = self.df[self.df['Date'].dt.year == year].copy()
        if month:
            year_data = year_data[year_data['Date'].dt.month == month]
        
        # 월별 집계 생성
        month_range = pd.period_range(start=f'{year}-01', end=f'{year}-12', freq='M')
        if month:
            month_range = [pd.Period(f'{year}-{month:02d}', freq='M')]
        
        results = {
            "analysis_period": f"{year}-{month or 'ALL'}",
            "warehouse_reports": {},
            "monthly_matrix": {},
            "summary_charts": {}
        }
        
        # 1. 창고별 월별 매트릭스 생성
        warehouse_monthly_matrix = self._create_warehouse_monthly_matrix(year_data, month_range)
        results["monthly_matrix"] = warehouse_monthly_matrix
        
        # 2. 입고/출고 트렌드 분석
        trend_analysis = self._analyze_monthly_trends(year_data)
        results["trend_analysis"] = trend_analysis
        
        # 3. 창고 효율성 분석
        efficiency_analysis = self._analyze_warehouse_efficiency(year_data)
        results["efficiency_analysis"] = efficiency_analysis
        
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "data": results
        }

    def _create_warehouse_monthly_matrix(self, data: pd.DataFrame, month_range) -> Dict[str, Any]:
        """창고별 월별 매트릭스 생성"""
        matrices = {}
        
        # 입고 매트릭스
        incoming_matrix = {}
        for warehouse in self.real_data["warehouses"]:
            warehouse_data = data[data['Location'] == warehouse]
            monthly_incoming = {}
            
            for month in month_range:
                month_data = warehouse_data[warehouse_data['YearMonth'] == month]
                monthly_incoming[str(month)] = month_data['Incoming'].sum()
            
            monthly_incoming['total'] = sum(monthly_incoming.values())
            incoming_matrix[warehouse] = monthly_incoming
        
        # 출고 매트릭스
        outgoing_matrix = {}
        for warehouse in self.real_data["warehouses"]:
            warehouse_data = data[data['Location'] == warehouse]
            monthly_outgoing = {}
            
            for month in month_range:
                month_data = warehouse_data[warehouse_data['YearMonth'] == month]
                monthly_outgoing[str(month)] = month_data['Outgoing'].sum()
            
            monthly_outgoing['total'] = sum(monthly_outgoing.values())
            outgoing_matrix[warehouse] = monthly_outgoing
        
        # 재고 매트릭스 (누적 계산)
        inventory_matrix = {}
        for warehouse in self.real_data["warehouses"]:
            cumulative_inventory = 0
            monthly_inventory = {}
            
            for month in month_range:
                monthly_in = incoming_matrix[warehouse].get(str(month), 0)
                monthly_out = outgoing_matrix[warehouse].get(str(month), 0)
                cumulative_inventory += (monthly_in - monthly_out)
                monthly_inventory[str(month)] = max(0, cumulative_inventory)
            
            monthly_inventory['avg'] = np.mean(list(monthly_inventory.values())) if monthly_inventory else 0
            inventory_matrix[warehouse] = monthly_inventory
        
        return {
            "incoming_matrix": incoming_matrix,
            "outgoing_matrix": outgoing_matrix,
            "inventory_matrix": inventory_matrix
        }

    def _analyze_monthly_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """월별 트렌드 분석"""
        monthly_summary = data.groupby('YearMonth').agg({
            'Incoming': 'sum',
            'Outgoing': 'sum',
            'Amount': 'sum'
        })
        
        # 트렌드 계산
        if len(monthly_summary) > 1:
            incoming_trend = monthly_summary['Incoming'].pct_change().mean()
            outgoing_trend = monthly_summary['Outgoing'].pct_change().mean()
            value_trend = monthly_summary['Amount'].pct_change().mean()
        else:
            incoming_trend = outgoing_trend = value_trend = 0
        
        return {
            "monthly_totals": monthly_summary.to_dict('index'),
            "trends": {
                "incoming_growth_rate": round(incoming_trend * 100, 2),
                "outgoing_growth_rate": round(outgoing_trend * 100, 2),
                "value_growth_rate": round(value_trend * 100, 2)
            },
            "peak_months": {
                "highest_incoming": monthly_summary['Incoming'].idxmax(),
                "highest_outgoing": monthly_summary['Outgoing'].idxmax(),
                "highest_value": monthly_summary['Amount'].idxmax()
            }
        }

    def _analyze_warehouse_efficiency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """창고 효율성 분석"""
        efficiency_scores = {}
        
        for warehouse in self.real_data["warehouses"]:
            wh_data = data[data['Location'] == warehouse]
            
            if wh_data.empty:
                efficiency_scores[warehouse] = {
                    "efficiency_score": 0,
                    "utilization_rate": 0,
                    "throughput_rate": 0,
                    "value_density": 0
                }
                continue
            
            total_incoming = wh_data['Incoming'].sum()
            total_outgoing = wh_data['Outgoing'].sum()
            total_value = wh_data['Amount'].sum()
            
            # 효율성 지표 계산
            utilization_rate = (total_outgoing / max(total_incoming, 1)) * 100
            throughput_rate = total_outgoing / len(wh_data['YearMonth'].unique()) if len(wh_data['YearMonth'].unique()) > 0 else 0
            value_density = total_value / max(total_incoming, 1)
            
            # 종합 효율성 점수 (0-100)
            efficiency_score = min(100, (utilization_rate * 0.4 + min(throughput_rate * 2, 50) * 0.3 + min(value_density / 1000, 50) * 0.3))
            
            efficiency_scores[warehouse] = {
                "efficiency_score": round(efficiency_score, 1),
                "utilization_rate": round(utilization_rate, 1),
                "throughput_rate": round(throughput_rate, 1),
                "value_density": round(value_density, 2)
            }
        
        # 순위 매기기
        sorted_warehouses = sorted(efficiency_scores.items(), key=lambda x: x[1]["efficiency_score"], reverse=True)
        
        return {
            "warehouse_efficiency": efficiency_scores,
            "ranking": [{"rank": i+1, "warehouse": wh, "score": scores["efficiency_score"]} 
                       for i, (wh, scores) in enumerate(sorted_warehouses)]
        }

    def logi_master_warehouse_sites(self, site_id: str = None) -> Dict[str, Any]:
        """
        /logi_master warehouse-sites 명령어
        현장별 창고 현황 분석
        """
        print(f"🏗️ 현장별 창고 현황 분석 중... (현장: {site_id or '전체'})")
        
        if site_id and site_id not in self.real_data["sites"]:
            return {
                "status": "ERROR",
                "message": f"현장 '{site_id}'를 찾을 수 없습니다.",
                "available_sites": self.real_data["sites"]
            }
        
        sites = [site_id] if site_id else self.real_data["sites"]
        results = {}
        
        for site in sites:
            site_data = self.df[self.df['Site'] == site]
            
            # 현장별 창고 매핑 (현장과 같은 이름의 창고가 있는 경우)
            related_warehouses = [wh for wh in self.real_data["warehouses"] if site in wh or wh == site]
            if not related_warehouses and site in self.real_data["warehouses"]:
                related_warehouses = [site]
            
            # 현장별 출고 현황 (현장으로 보내지는 물량)
            site_outgoing = site_data.groupby('YearMonth')['Outgoing'].sum()
            
            # 관련 창고 현황
            warehouse_status = {}
            for wh in related_warehouses:
                wh_data = self.df[self.df['Location'] == wh]
                warehouse_status[wh] = {
                    "current_stock": wh_data['Incoming'].sum() - wh_data['Outgoing'].sum(),
                    "monthly_outgoing": wh_data.groupby('YearMonth')['Outgoing'].sum().to_dict()
                }
            
            results[site] = {
                "site_summary": {
                    "total_received": site_data['Outgoing'].sum(),
                    "monthly_received": site_outgoing.to_dict(),
                    "related_warehouses": related_warehouses
                },
                "warehouse_details": warehouse_status,
                "supply_chain_health": self._assess_site_supply_chain(site, site_data)
            }
        
        return {
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "sites": results
        }

    def _assess_site_supply_chain(self, site: str, site_data: pd.DataFrame) -> Dict[str, Any]:
        """현장 공급망 건강도 평가"""
        if site_data.empty:
            return {
                "health_score": 0,
                "status": "NO_DATA",
                "recommendations": ["데이터 수집 및 모니터링 시작 필요"]
            }
        
        # 공급망 지표 계산
        monthly_variance = site_data.groupby('YearMonth')['Outgoing'].sum().var()
        avg_monthly_supply = site_data.groupby('YearMonth')['Outgoing'].sum().mean()
        supply_consistency = max(0, 100 - (monthly_variance / max(avg_monthly_supply, 1)) * 10)
        
        # 공급사 다양성
        supplier_count = site_data['Location'].nunique()
        supplier_diversity_score = min(100, supplier_count * 25)
        
        # 종합 건강도 (0-100)
        health_score = (supply_consistency * 0.6 + supplier_diversity_score * 0.4)
        
        # 상태 및 권장사항
        if health_score >= 80:
            status = "EXCELLENT"
            recommendations = ["현재 상태 유지", "정기 모니터링 지속"]
        elif health_score >= 60:
            status = "GOOD"
            recommendations = ["공급망 다양성 개선", "재고 최적화 검토"]
        elif health_score >= 40:
            status = "FAIR"
            recommendations = ["공급사 다각화 필요", "비상 재고 확보", "월별 공급량 안정화"]
        else:
            status = "POOR"
            recommendations = ["긴급 공급망 재구성 필요", "대체 공급사 확보", "리스크 관리 강화"]
        
        return {
            "health_score": round(health_score, 1),
            "status": status,
            "metrics": {
                "supply_consistency": round(supply_consistency, 1),
                "supplier_diversity": round(supplier_diversity_score, 1),
                "avg_monthly_supply": round(avg_monthly_supply, 1)
            },
            "recommendations": recommendations
        }

    def visualize_warehouse_dashboard(self) -> str:
        """창고 대시보드 시각화 생성"""
        print("📊 창고 대시보드 시각화 생성 중...")
        
        # 서브플롯 생성
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['월별 입출고 현황', '창고별 재고 현황', '현장별 공급 현황', '효율성 점수'],
            specs=[[{'type': 'bar'}, {'type': 'scatter'}],
                   [{'type': 'bar'}, {'type': 'indicator'}]]
        )
        
        # 1. 월별 입출고 현황
        monthly_data = self.df.groupby('YearMonth').agg({
            'Incoming': 'sum',
            'Outgoing': 'sum'
        })
        
        fig.add_trace(
            go.Bar(name='입고', x=monthly_data.index.astype(str), y=monthly_data['Incoming']),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='출고', x=monthly_data.index.astype(str), y=monthly_data['Outgoing']),
            row=1, col=1
        )
        
        # 2. 창고별 현재 재고
        warehouse_stocks = {}
        for warehouse in self.real_data["warehouses"]:
            wh_data = self.df[self.df['Location'] == warehouse]
            current_stock = wh_data['Incoming'].sum() - wh_data['Outgoing'].sum()
            warehouse_stocks[warehouse] = max(0, current_stock)
        
        fig.add_trace(
            go.Scatter(
                x=list(warehouse_stocks.keys()),
                y=list(warehouse_stocks.values()),
                mode='markers+lines',
                name='현재재고',
                marker=dict(size=10)
            ),
            row=1, col=2
        )
        
        # 3. 현장별 공급 현황
        site_supplies = {}
        for site in self.real_data["sites"]:
            site_data = self.df[self.df['Site'] == site]
            total_supply = site_data['Outgoing'].sum()
            site_supplies[site] = total_supply
        
        fig.add_trace(
            go.Bar(
                x=list(site_supplies.keys()),
                y=list(site_supplies.values()),
                name='공급량'
            ),
            row=2, col=1
        )
        
        # 4. 전체 효율성 점수
        total_incoming = self.df['Incoming'].sum()
        total_outgoing = self.df['Outgoing'].sum()
        efficiency = (total_outgoing / max(total_incoming, 1)) * 100
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=efficiency,
                title={'text': "전체 효율성 (%)"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "darkblue"},
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 80}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="HVDC 창고 관리 대시보드",
            height=800,
            showlegend=True
        )
        
        # HTML 파일로 저장
        output_file = "reports/warehouse_dashboard.html"
        Path("reports").mkdir(exist_ok=True)
        fig.write_html(output_file)
        
        print(f"✅ 대시보드 생성 완료: {output_file}")
        return output_file

    def export_warehouse_excel(self, output_file: str = None) -> str:
        """창고 데이터 Excel 내보내기"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_file = f"HVDC_Warehouse_Report_{timestamp}.xlsx"
        
        print(f"💾 창고 리포트 Excel 내보내기: {output_file}")
        
        # 각종 분석 수행
        warehouse_status = self.logi_master_warehouse_status()
        monthly_analysis = self.logi_master_warehouse_monthly()
        sites_analysis = self.logi_master_warehouse_sites()
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 1. 원본 데이터
                self.df.to_excel(writer, sheet_name='원본데이터', index=False)
                
                # 2. 창고별 현황
                warehouse_summary = []
                for wh_id, wh_info in warehouse_status['warehouses'].items():
                    warehouse_summary.append({
                        '창고명': wh_id,
                        '현재재고': wh_info['basic_info']['current_stock'],
                        '총가치_AED': wh_info['basic_info']['total_value_aed'],
                        '회전율_퍼센트': wh_info['basic_info']['turnover_rate_percent'],
                        '월평균입고': wh_info['monthly_summary']['avg_monthly_incoming'],
                        '월평균출고': wh_info['monthly_summary']['avg_monthly_outgoing']
                    })
                
                pd.DataFrame(warehouse_summary).to_excel(writer, sheet_name='창고별현황', index=False)
                
                # 3. 월별 매트릭스 (입고)
                if 'data' in monthly_analysis and 'monthly_matrix' in monthly_analysis['data']:
                    incoming_matrix = monthly_analysis['data']['monthly_matrix']['incoming_matrix']
                    pd.DataFrame(incoming_matrix).T.to_excel(writer, sheet_name='월별입고매트릭스', index=True)
                    
                    # 4. 월별 매트릭스 (출고)
                    outgoing_matrix = monthly_analysis['data']['monthly_matrix']['outgoing_matrix']
                    pd.DataFrame(outgoing_matrix).T.to_excel(writer, sheet_name='월별출고매트릭스', index=True)
                    
                    # 5. 월별 매트릭스 (재고)
                    inventory_matrix = monthly_analysis['data']['monthly_matrix']['inventory_matrix']
                    pd.DataFrame(inventory_matrix).T.to_excel(writer, sheet_name='월별재고매트릭스', index=True)
                
                # 6. 현장별 현황
                site_summary = []
                for site_id, site_info in sites_analysis['sites'].items():
                    site_summary.append({
                        '현장명': site_id,
                        '총수령량': site_info['site_summary']['total_received'],
                        '관련창고수': len(site_info['site_summary']['related_warehouses']),
                        '공급건강도': site_info['supply_chain_health']['health_score'],
                        '상태': site_info['supply_chain_health']['status']
                    })
                
                pd.DataFrame(site_summary).to_excel(writer, sheet_name='현장별현황', index=False)
                
                # 7. 요약 통계
                summary_stats = {
                    '총 창고 수': len(warehouse_status['warehouses']),
                    '총 현장 수': len(sites_analysis['sites']),
                    '총 입고량': self.df['Incoming'].sum(),
                    '총 출고량': self.df['Outgoing'].sum(),
                    '평균 회전율': sum(wh['basic_info']['turnover_rate_percent'] for wh in warehouse_status['warehouses'].values()) / len(warehouse_status['warehouses']),
                    '생성일시': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                pd.DataFrame([summary_stats]).to_excel(writer, sheet_name='요약통계', index=False)
            
            print(f"✅ Excel 파일 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Excel 내보내기 오류: {str(e)}")
            return None

if __name__ == "__main__":
    # 테스트 실행
    warehouse_cmd = HVDCWarehouseCommand()
    
    print("🔧 HVDC 창고 관리 시스템 테스트")
    print("=" * 50)
    
    # 1. 창고 상태 확인
    print("\n1. 창고 상태 확인:")
    status = warehouse_cmd.logi_master_warehouse_status()
    print(f"   - 처리된 창고 수: {len(status['warehouses'])}")
    
    # 2. 월별 분석
    print("\n2. 월별 분석:")
    monthly = warehouse_cmd.logi_master_warehouse_monthly()
    print(f"   - 분석 기간: {monthly['data']['analysis_period']}")
    
    # 3. 현장별 분석
    print("\n3. 현장별 분석:")
    sites = warehouse_cmd.logi_master_warehouse_sites()
    print(f"   - 처리된 현장 수: {len(sites['sites'])}")
    
    # 4. 대시보드 생성
    print("\n4. 대시보드 생성:")
    dashboard_file = warehouse_cmd.visualize_warehouse_dashboard()
    print(f"   - 생성된 파일: {dashboard_file}")
    
    # 5. Excel 내보내기
    print("\n5. Excel 내보내기:")
    excel_file = warehouse_cmd.export_warehouse_excel()
    print(f"   - 생성된 파일: {excel_file}")
    
    print("\n✅ 모든 테스트 완료!")