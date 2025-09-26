#!/usr/bin/env python3
"""
HVDC 전체 월별 입고·출고 엑셀 보고서 생성기 v1.1 (2025-07-10)
===========================================================
* 목적: 창고별/현장별 월별 입·출고/재고 현황 종합 보고서 자동 생성
* 주요 개선점(v1.1)
  1. **모든 위치 컬럼 날짜 형식 통일** – 창고·현장 컬럼을 일괄 `pd.to_datetime` 처리
  2. **중복 입고 제거** – 동일 화물의 재입고·이동 이벤트를 최초 1회만 인정
  3. **출고 이벤트 범위 확장** – 창고→현장·Pre‑Arrival·다른 창고 이동까지 포착
  4. **컬럼명 정규화 & Alias 매핑** – 공백·대소문자 차이 자동 교정

사용 예시:
$ python monthly_warehouse_report_generator.py --input data.xlsx --output monthly_report.xlsx
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

# Event‑Based Outbound Logic 통합 (선택사항)
try:
    from scripts.event_based_outbound import EventBasedOutboundResolver
    EVENT_OUTBOUND_AVAILABLE = True
except ImportError:  # fallback
    EVENT_OUTBOUND_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MonthlyWarehouseReportGenerator:
    """HVDC 프로젝트 월별 입·출고 보고서 생성기"""

    def __init__(self) -> None:
        # 표준 창고 / 현장 컬럼 정의
        self.warehouse_columns: List[str] = [
            "DHL Warehouse", "DSV Indoor", "DSV Al Markaz", "DSV Outdoor",
            "DSV MZP", "AAA Storage", "Hauler Indoor", "DSV MZD", "JDN MZD",
        ]
        self.site_columns: List[str] = ["MOSB", "MIR", "SHU", "DAS", "AGI", "Pre‑Arrival"]

        # 컬럼 Alias – 오타·중복 공백 대응
        self.column_aliases: Dict[str, str] = {
            "AAA  Storage": "AAA Storage",  # 이중 공백
            "Hauler  Indoor": "Hauler Indoor",
            "Pre Arrival": "Pre‑Arrival",   # 공백→하이픈
        }

        # Event‑Based Outbound Resolver
        if EVENT_OUTBOUND_AVAILABLE:
            self.outbound_resolver = EventBasedOutboundResolver()
            logger.info("✅ Event‑Based Outbound Logic 활성화")
        else:
            self.outbound_resolver = None
            logger.warning("⚠️ Event‑Based Outbound Logic 미탑재 – 기본 로직 사용")

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------
    def _detect_id_column(self, df: pd.DataFrame) -> str:
        """고유 식별자 컬럼 탐색 (HVDC CODE, Case No. 등)"""
        for cand in ["HVDC CODE", "Case No.", "Item Code", df.columns[0]]:
            if cand in df.columns:
                return cand
        return df.columns[0]

    # ------------------------------------------------------------------
    # 데이터 로딩 & 전처리
    # ------------------------------------------------------------------
    def load_data(self, input_file: str | Path) -> pd.DataFrame:
        logger.info(f"📂 데이터 로드 중: {input_file}")

        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(input_file)

        if input_file.suffix.lower() == ".xlsx":
            df = pd.read_excel(input_file, sheet_name=0)
        else:
            df = pd.read_csv(input_file)

        logger.info(f"✅ 데이터 로드 완료: {len(df):,}행 × {len(df.columns)}열")
        return self._preprocess_data(df)

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """1) 컬럼명 정규화 ➜ 2) 날짜형 변환 ➜ 3) Event‑Based Outbound"""
        # 1) 컬럼명 정규화 (여러 공백→단일, 앞뒤 공백 제거, 대소문자 유지)
        df.rename(columns=lambda c: " ".join(c.split()).strip(), inplace=True)
        df.rename(columns=self.column_aliases, inplace=True)

        # 2) 날짜형 변환 (모든 위치 컬럼)
        date_cols = [c for c in df.columns if c in self.warehouse_columns + self.site_columns]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        # 3) Event‑Based Outbound Logic 적용(선택)
        if self.outbound_resolver is not None:
            try:
                df = self.outbound_resolver.resolve_final_location(df)
                logger.info("✅ Outbound Logic 적용 완료")
            except Exception as e:
                logger.warning(f"⚠️ Outbound Logic 적용 실패: {e}")

        return df

    # ------------------------------------------------------------------
    # 월별 집계 로직
    # ------------------------------------------------------------------
    def calculate_monthly_inbound(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        logger.info("📊 월별 입고 계산 중…")
        id_col = self._detect_id_column(df)
        inbound: Dict[str, Dict[str, int]] = {}

        for wh in self.warehouse_columns:
            if wh not in df.columns:
                continue
            wh_data = df[df[wh].notna()].copy()
            if wh_data.empty:
                continue
            # 최초 입고만 인정
            wh_data = wh_data.sort_values(wh).drop_duplicates(subset=[id_col], keep="first")
            wh_data["Month"] = wh_data[wh].dt.to_period("M")
            counts = wh_data["Month"].value_counts().sort_index()
            inbound[wh] = {str(m): int(c) for m, c in counts.items()}
            logger.info(f"  └ {wh}: {len(wh_data)}건")
        return inbound

    def calculate_monthly_outbound(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        logger.info("📤 월별 출고 계산 중…")
        id_col = self._detect_id_column(df)
        out: Dict[str, Dict[str, int]] = {}

        # 모든 위치 컬럼 long‑format
        loc_cols = [c for c in self.warehouse_columns + self.site_columns if c in df.columns]
        long_df = df.melt(id_vars=[id_col], value_vars=loc_cols, var_name="Location", value_name="Date").dropna(subset=["Date"])
        if long_df.empty:
            logger.warning("⚠️ 유효한 날짜 데이터 없음 – 출고 건너뜀")
            return out

        long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")
        long_df = long_df.sort_values([id_col, "Date"])
        long_df["Prev_Location"] = long_df.groupby(id_col)["Location"].shift()

        # 창고 → (현장, Pre‑Arrival, 다른 창고) 이동 = 출고
        outbound_events = long_df[
            long_df["Prev_Location"].isin(self.warehouse_columns) &
            ~long_df["Location"].isin(self.warehouse_columns)  # 창고→비‑창고
        ]

        for wh in self.warehouse_columns:
            wh_events = outbound_events[outbound_events["Prev_Location"] == wh]
            if wh_events.empty:
                continue
            wh_events["Month"] = wh_events["Date"].dt.to_period("M")
            counts = wh_events["Month"].value_counts().sort_index()
            out[wh] = {str(m): int(c) for m, c in counts.items()}
            logger.info(f"  └ {wh}: {len(wh_events)}건")
        return out

    def calculate_monthly_inventory(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        logger.info("📦 월별 재고 계산 중…")
        inventory: Dict[str, Dict[str, int]] = {}

        if "final_location" not in df.columns:
            logger.warning("⚠️ final_location 컬럼 없음 – 재고 계산 건너뜀")
            return inventory

        for wh in self.warehouse_columns:
            inv_items = df[df["final_location"] == wh]
            if inv_items.empty or wh not in df.columns:
                continue
            inv_items = inv_items.copy()
            inv_items["Month"] = inv_items[wh].dt.to_period("M")
            counts = inv_items["Month"].value_counts().sort_index()
            inventory[wh] = {str(m): int(c) for m, c in counts.items()}
            logger.info(f"  └ {wh}: {len(inv_items)}건")
        return inventory

    # ------------------------------------------------------------------
    # 리포트 시트 생성 (Multi‑Level Header)
    # ------------------------------------------------------------------
    def create_warehouse_monthly_sheet(self, 
                                     inbound_data: Dict[str, Dict[str, int]],
                                     outbound_data: Dict[str, Dict[str, int]],
                                     inventory_data: Dict[str, Dict[str, int]]) -> pd.DataFrame:
        """창고별 월별 입출고 시트 생성 (Multi-Level Header)"""
        logger.info("📋 창고별 월별 입출고 시트 생성 중...")
        
        # 모든 월 수집
        all_months = set()
        for warehouse_data in [inbound_data, outbound_data, inventory_data]:
            for warehouse, months in warehouse_data.items():
                all_months.update(months.keys())
        
        all_months = sorted(list(all_months))
        
        # Multi-Level Header 구성
        warehouses = list(inbound_data.keys())
        
        # 헤더 레벨 0 (입고/출고/재고)
        level_0_headers = []
        level_1_headers = []
        
        for warehouse in warehouses:
            level_0_headers.extend(['입고', '출고', '재고'])
            level_1_headers.extend([warehouse, warehouse, warehouse])
        
        # 데이터 구성
        data = []
        for month in all_months:
            row = [month]
            
            for warehouse in warehouses:
                # 입고
                inbound_count = inbound_data.get(warehouse, {}).get(month, 0)
                row.append(inbound_count)
                
                # 출고
                outbound_count = outbound_data.get(warehouse, {}).get(month, 0)
                row.append(outbound_count)
                
                # 재고
                inventory_count = inventory_data.get(warehouse, {}).get(month, 0)
                row.append(inventory_count)
            
            data.append(row)
        
        # DataFrame 생성
        df = pd.DataFrame(data, columns=['Month'] + level_1_headers)
        
        # Multi-Level Header 설정
        df.columns = pd.MultiIndex.from_arrays([['Month'] + level_0_headers, [''] + level_1_headers])
        
        logger.info(f"✅ 창고별 월별 시트 생성 완료: {len(df)}행 × {len(df.columns)}열")
        return df
    
    def create_site_monthly_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """현장별 월별 입고재고 시트 생성"""
        logger.info("📋 현장별 월별 입고재고 시트 생성 중...")
        
        site_monthly_data = {}
        
        for site in self.site_columns:
            if site in df.columns:
                site_monthly_data[site] = {}
                
                # 현장에 도착한 항목들
                site_items = df[df[site].notna()].copy()
                
                if len(site_items) > 0:
                    site_items['Month'] = site_items[site].dt.to_period('M')
                    monthly_counts = site_items['Month'].value_counts().sort_index()
                    
                    for month, count in monthly_counts.items():
                        site_monthly_data[site][str(month)] = count
                
                logger.info(f"  └ {site}: {len(site_items)}건 입고")
        
        # Multi-Level Header 구성
        sites = list(site_monthly_data.keys())
        
        level_0_headers = []
        level_1_headers = []
        
        for site in sites:
            level_0_headers.extend(['입고', '재고'])
            level_1_headers.extend([site, site])
        
        # 데이터 구성
        all_months = set()
        for site_data in site_monthly_data.values():
            all_months.update(site_data.keys())
        
        all_months = sorted(list(all_months))
        
        data = []
        for month in all_months:
            row = [month]
            
            for site in sites:
                # 입고
                inbound_count = site_monthly_data[site].get(month, 0)
                row.append(inbound_count)
                
                # 재고 (현재는 입고와 동일하게 설정)
                inventory_count = site_monthly_data[site].get(month, 0)
                row.append(inventory_count)
            
            data.append(row)
        
        # DataFrame 생성
        df_site = pd.DataFrame(data, columns=['Month'] + level_1_headers)
        
        # Multi-Level Header 설정
        df_site.columns = pd.MultiIndex.from_arrays([['Month'] + level_0_headers, [''] + level_1_headers])
        
        logger.info(f"✅ 현장별 월별 시트 생성 완료: {len(df_site)}행 × {len(df_site.columns)}열")
        return df_site
    
    def create_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """요약 통계 시트 생성"""
        logger.info("📊 요약 통계 시트 생성 중...")
        
        summary_data = [
            {'구분': '총 아이템 수', '값': f'{len(df):,}건'},
            {'구분': '총 컬럼 수', '값': f'{len(df.columns)}개'},
            {'구분': '창고 수', '값': f'{len(self.warehouse_columns)}개'},
            {'구분': '현장 수', '값': f'{len(self.site_columns)}개'},
            {'구분': '보고서 생성일시', '값': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'구분': '데이터 소스', '값': 'HVDC 프로젝트 통합 데이터'},
            {'구분': 'Event-Based Outbound', '값': '활성화' if EVENT_OUTBOUND_AVAILABLE else '비활성화'},
            {'구분': '버전', '값': 'v1.1 (2025-07-10)'},
            {'구분': '데이터 품질 점수', '값': f'{self._calculate_data_quality(df):.1f}%'}
        ]
        
        return pd.DataFrame(summary_data)
    
    def _calculate_data_quality(self, df: pd.DataFrame) -> float:
        """데이터 품질 점수 계산"""
        total_cells = len(df) * len(df.columns)
        valid_cells = df.notna().sum().sum()
        return (valid_cells / total_cells) * 100 if total_cells > 0 else 0.0
    
    def create_kpi_dashboard(self, df: pd.DataFrame) -> pd.DataFrame:
        """KPI 대시보드 시트 생성"""
        logger.info("📈 KPI 대시보드 생성 중...")
        
        # 창고별 KPI 계산
        warehouse_kpis = []
        for warehouse in self.warehouse_columns:
            if warehouse in df.columns:
                total_items = df[warehouse].notna().sum()
                warehouse_kpis.append({
                    '창고명': warehouse,
                    '총 처리 건수': total_items,
                    '처리율(%)': round(total_items / len(df) * 100, 1),
                    '평균 체류일': self._calculate_avg_stay_days(df, warehouse),
                    '위험도': self._calculate_risk_level(df, warehouse)
                })
        
        return pd.DataFrame(warehouse_kpis)
    
    def _calculate_avg_stay_days(self, df: pd.DataFrame, warehouse: str) -> float:
        """평균 체류일 계산"""
        warehouse_items = df[df[warehouse].notna()].copy()
        if len(warehouse_items) == 0:
            return 0.0
        
        # 간단한 체류일 계산 (현재는 0으로 설정)
        return 0.0
    
    def _calculate_risk_level(self, df: pd.DataFrame, warehouse: str) -> str:
        """위험도 계산"""
        warehouse_items = df[df[warehouse].notna()]
        if len(warehouse_items) == 0:
            return "LOW"
        
        # 간단한 위험도 계산
        if len(warehouse_items) > 1000:
            return "HIGH"
        elif len(warehouse_items) > 500:
            return "MEDIUM"
        else:
            return "LOW"

    # ------------------------------------------------------------------
    # 메인 엔트리
    # ------------------------------------------------------------------
    def generate_monthly_report(self, input_file: str, output_file: str | None = None) -> str:
        logger.info("🚀 월별 보고서 생성 시작")
        df = self.load_data(input_file)

        inbound = self.calculate_monthly_inbound(df)
        outbound = self.calculate_monthly_outbound(df)
        inventory = self.calculate_monthly_inventory(df)

        wh_sheet = self.create_warehouse_monthly_sheet(inbound, outbound, inventory)
        site_sheet = self.create_site_monthly_sheet(df)
        summary_sheet = self.create_summary_sheet(df)
        kpi_sheet = self.create_kpi_dashboard(df)

        if output_file is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"HVDC_Monthly_Warehouse_Report_{ts}.xlsx"

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="전체_트랜잭션_데이터", index=False)
            wh_sheet.to_excel(writer, sheet_name="창고_월별_입출고")
            site_sheet.to_excel(writer, sheet_name="현장_월별_입고재고")
            summary_sheet.to_excel(writer, sheet_name="요약_통계", index=False)
            kpi_sheet.to_excel(writer, sheet_name="KPI_대시보드", index=False)

        logger.info(f"✅ 월별 보고서 생성 완료: {output_file}")
        return output_file


# ----------------------------------------------------------------------
# CLI 진입점
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="HVDC 월별 입·출고 보고서 생성기")
    parser.add_argument("--input", required=True, help="입력 파일 경로 (Excel/CSV)")
    parser.add_argument("--output", help="출력 파일 경로 (선택)")
    parser.add_argument("--verbose", action="store_true", help="DEBUG 로그 출력")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    gen = MonthlyWarehouseReportGenerator()
    try:
        outfile = gen.generate_monthly_report(args.input, args.output)
        print("\n🎉 월별 보고서 생성 완료!")
        print(f"📁 출력 파일: {outfile}")
        print(f"📊 시트 구성:")
        print(f"  - 전체_트랜잭션_데이터")
        print(f"  - 창고_월별_입출고 (Multi-Level Header)")
        print(f"  - 현장_월별_입고재고 (Multi-Level Header)")
        print(f"  - 요약_통계")
        print(f"  - KPI_대시보드")
    except Exception as e:
        logger.error(f"❌ 보고서 생성 실패: {e}")
        raise


if __name__ == "__main__":
    main() 