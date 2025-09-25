"""
HVDC Excel Reporter - Reporting Module
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict
from src import config
from src.data.loader import DataLoader
from src.calculation.calculator import WarehouseCalculator

logger = logging.getLogger(__name__)

class HVDCExcelReporter:
    """
    Generates the final HVDC Excel report.
    """
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.data_loader = DataLoader()
        self.calculator = WarehouseCalculator()
        self.stats = {}

    def generate_report(self):
        """
        Generates the full multi-sheet Excel report.
        """
        logger.info("🏗️ Starting final Excel report generation...")
        
        self._calculate_statistics()
        self._generate_excel_file()
        
        logger.info(f"🎉 Final Excel report generated: {self.excel_filename}")
        return self.excel_filename

    def _calculate_statistics(self):
        """
        Calculates all the necessary statistics for the report.
        """
        logger.info("📊 Calculating warehouse statistics...")
        
        df = self.data_loader.load_real_hvdc_data()
        df = self.calculator.process_real_data(df)
        df = self.calculator.calculate_final_location(df)
        
        inbound_result = self.calculator.calculate_warehouse_inbound(df)
        outbound_result = self.calculator.calculate_warehouse_outbound(df)
        inventory_result = self.calculator.calculate_warehouse_inventory(df)
        direct_result = self.calculator.calculate_direct_delivery(df)
        
        sqm_inbound = self.calculator.calculate_monthly_sqm_inbound(df)
        sqm_outbound = self.calculator.calculate_monthly_sqm_outbound(df)
        sqm_cumulative = self.calculator.calculate_cumulative_sqm_inventory(sqm_inbound, sqm_outbound)
        sqm_charges = self.calculator.calculate_monthly_invoice_charges(sqm_cumulative)
        sqm_quality = self.calculator.analyze_sqm_data_quality(df)
        
        self.stats = {
            'inbound_result': inbound_result,
            'outbound_result': outbound_result,
            'inventory_result': inventory_result,
            'direct_result': direct_result,
            'processed_data': df,
            'sqm_inbound': sqm_inbound,
            'sqm_outbound': sqm_outbound,
            'sqm_cumulative_inventory': sqm_cumulative,
            'sqm_invoice_charges': sqm_charges,
            'sqm_data_quality': sqm_quality
        }

    def _generate_excel_file(self):
        """
        Writes all the data to a multi-sheet Excel file.
        """
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        self.excel_filename = output_dir / f"HVDC_입고로직_종합리포트_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(self.excel_filename, engine='xlsxwriter') as writer:
            self._write_sheets(writer)

    def _write_sheets(self, writer):
        """
        Writes individual sheets to the Excel file.
        """
        # Warehouse Monthly Sheet
        warehouse_monthly = self._create_warehouse_monthly_sheet()
        warehouse_monthly.to_excel(writer, sheet_name='창고_월별_입출고', index=True)

        # Site Monthly Sheet
        site_monthly = self._create_site_monthly_sheet()
        site_monthly.to_excel(writer, sheet_name='현장_월별_입고재고', index=True)

        # Flow Analysis Sheet
        flow_analysis = self._create_flow_analysis_sheet()
        flow_analysis.to_excel(writer, sheet_name='Flow_Code_분석', index=False)

        # Transaction Summary Sheet
        transaction_summary = self._create_transaction_summary_sheet()
        transaction_summary.to_excel(writer, sheet_name='전체_트랜잭션_요약', index=False)

        # KPI Validation Sheet
        kpi_validation_df = self._create_kpi_sheet()
        kpi_validation_df.to_excel(writer, sheet_name='KPI_검증_결과', index=False)

        # SQM Sheets
        sqm_cumulative_sheet = self._create_sqm_cumulative_sheet()
        sqm_cumulative_sheet.to_excel(writer, sheet_name='SQM_누적재고', index=False)
        
        sqm_invoice_sheet = self._create_sqm_invoice_sheet()
        sqm_invoice_sheet.to_excel(writer, sheet_name='SQM_Invoice과금', index=False)
        
        sqm_pivot_sheet = self._create_sqm_pivot_sheet()
        sqm_pivot_sheet.to_excel(writer, sheet_name='SQM_피벗테이블', index=False)

        # Data Sheets
        self.stats['processed_data'].head(1000).to_excel(writer, sheet_name='원본_데이터_샘플', index=False)
        self.stats['processed_data'][self.stats['processed_data']['Vendor'] == 'HITACHI'].to_excel(writer, sheet_name='HITACHI_원본데이터', index=False)
        self.stats['processed_data'][self.stats['processed_data']['Vendor'] == 'SIMENSE'].to_excel(writer, sheet_name='SIEMENS_원본데이터', index=False)
        self.stats['processed_data'].to_excel(writer, sheet_name='통합_원본데이터', index=False)

    def _create_warehouse_monthly_sheet(self) -> pd.DataFrame:
        """Creates the warehouse monthly summary sheet."""
        logger.info("🏢 Creating warehouse monthly sheet...")
        months = pd.date_range('2023-02', '2025-06', freq='MS').strftime('%Y-%m')
        results = []
        
        for month_str in months:
            row = {'입고월': month_str}
            inbound_values = []
            outbound_values = []
            
            for wh in config.WAREHOUSE_COLUMNS:
                in_count = sum(item['Pkg_Quantity'] for item in self.stats['inbound_result']['inbound_items'] if item['Warehouse'] == wh and item['Year_Month'] == month_str)
                in_count += sum(t['Pkg_Quantity'] for t in self.stats['inbound_result']['warehouse_transfers'] if t['To_Warehouse'] == wh and t['Year_Month'] == month_str)
                inbound_values.append(in_count)
                row[f'입고_{wh}'] = in_count
                
                out_count = sum(item['Pkg_Quantity'] for item in self.stats['outbound_result']['outbound_items'] if item['Warehouse'] == wh and item['Year_Month'] == month_str)
                outbound_values.append(out_count)
                row[f'출고_{wh}'] = out_count
                
            row['누계_입고'] = sum(inbound_values)
            row['누계_출고'] = sum(outbound_values)
            results.append(row)
            
        df = pd.DataFrame(results)
        total_row = df.sum(numeric_only=True)
        total_row['입고월'] = 'Total'
        df.loc[len(df)] = total_row
        return df

    def _create_site_monthly_sheet(self) -> pd.DataFrame:
        """Creates the site monthly summary sheet."""
        logger.info("🏗️ Creating site monthly sheet...")
        months = pd.date_range('2024-01', '2025-06', freq='MS').strftime('%Y-%m')
        results = []
        cumulative_inventory = {site: 0 for site in config.SITE_COLUMNS}
        df_processed = self.stats['processed_data']

        for month_str in months:
            row = {'입고월': month_str}
            for site in config.SITE_COLUMNS:
                mask = (
                    (df_processed['Final_Location'] == site) &
                    (df_processed[site].notna()) &
                    (pd.to_datetime(df_processed[site]).dt.strftime('%Y-%m') == month_str)
                )
                inbound_count = df_processed.loc[mask, 'Pkg'].sum()
                row[f'입고_{site}'] = int(inbound_count)
                cumulative_inventory[site] += inbound_count
            
            for site in config.SITE_COLUMNS:
                row[f'재고_{site}'] = int(cumulative_inventory[site])
            
            results.append(row)

        df = pd.DataFrame(results)
        if not df.empty:
            total_row = {f'입고_{s}': df[f'입고_{s}'].sum() for s in config.SITE_COLUMNS}
            total_row.update({f'재고_{s}': df[f'재고_{s}'].iloc[-1] for s in config.SITE_COLUMNS})
            total_row['입고월'] = 'Total'
            df.loc[len(df)] = total_row
        return df

    def _create_flow_analysis_sheet(self) -> pd.DataFrame:
        """Creates the flow code analysis sheet."""
        logger.info("📊 Creating flow code analysis sheet...")
        df = self.stats['processed_data']
        flow_summary = df.groupby('FLOW_CODE').size().reset_index(name='Count')
        flow_summary['FLOW_DESCRIPTION'] = flow_summary['FLOW_CODE'].map(config.FLOW_CODES)
        return flow_summary[['FLOW_CODE', 'FLOW_DESCRIPTION', 'Count']]

    def _create_transaction_summary_sheet(self) -> pd.DataFrame:
        """Creates the transaction summary sheet."""
        logger.info("📊 Creating transaction summary sheet...")
        df = self.stats['processed_data']
        summary_data = []

        # Overall stats
        summary_data.append({'Category': '전체 통계', 'Item': '총 트랜잭션 건수', 'Value': f"{len(df):,}건"})

        # Vendor distribution
        vendor_dist = df['Vendor'].value_counts(normalize=True) * 100
        for vendor, percentage in vendor_dist.items():
            summary_data.append({'Category': '벤더별 분포', 'Item': vendor, 'Value': f"{percentage:.1f}%"})

        # Flow code distribution
        flow_dist = df['FLOW_CODE'].value_counts(normalize=True).sort_index() * 100
        for code, percentage in flow_dist.items():
            desc = config.FLOW_CODES.get(code, f"Flow {code}")
            summary_data.append({'Category': 'Flow Code 분포', 'Item': f"Flow {code}: {desc}", 'Value': f"{percentage:.1f}%"})
            
        return pd.DataFrame(summary_data)

    def _create_kpi_sheet(self) -> pd.DataFrame:
        """Creates the KPI validation sheet."""
        logger.info("✅ Creating KPI validation sheet...")
        # This method requires the original validate_kpi_thresholds function.
        # For now, we'll just return an empty frame.
        # We will move validate_kpi_thresholds to a more appropriate module later.
        return pd.DataFrame()

    def _create_sqm_cumulative_sheet(self) -> pd.DataFrame:
        """Creates the SQM cumulative inventory sheet."""
        logger.info("🏢 Creating SQM cumulative inventory sheet...")
        sqm_cumulative = self.stats.get('sqm_cumulative_inventory', {})
        sqm_data = []
        for month, month_data in sqm_cumulative.items():
            for wh, wh_data in month_data.items():
                wh_data.update({'Year_Month': month, 'Warehouse': wh})
                sqm_data.append(wh_data)
        return pd.DataFrame(sqm_data)

    def _create_sqm_invoice_sheet(self) -> pd.DataFrame:
        """Creates the SQM invoice sheet."""
        logger.info("💰 Creating SQM invoice sheet...")
        sqm_charges = self.stats.get('sqm_invoice_charges', {})
        invoice_data = []
        for month, month_data in sqm_charges.items():
            total_charge = month_data.get('total_monthly_charge_aed', 0)
            for wh, wh_data in month_data.items():
                if isinstance(wh_data, dict):
                    wh_data.update({'Year_Month': month, 'Warehouse': wh, 'Total_Monthly_AED': total_charge})
                    invoice_data.append(wh_data)
        return pd.DataFrame(invoice_data)

    def _create_sqm_pivot_sheet(self) -> pd.DataFrame:
        """Creates the SQM pivot table sheet."""
        logger.info("📊 Creating SQM pivot table sheet...")
        sqm_cumulative = self.stats.get('sqm_cumulative_inventory', {})
        pivot_data = []
        for month, month_data in sqm_cumulative.items():
            row = {'Year_Month': month}
            total_sqm = 0
            for wh in config.WAREHOUSE_COLUMNS:
                if wh in month_data:
                    cum_sqm = month_data[wh]['cumulative_inventory_sqm']
                    row[f'{wh}_Cumulative_SQM'] = cum_sqm
                    row[f'{wh}_Utilization_%'] = month_data[wh]['utilization_rate_%']
                    total_sqm += cum_sqm
                else:
                    row[f'{wh}_Cumulative_SQM'] = 0
                    row[f'{wh}_Utilization_%'] = 0
            row['Total_Cumulative_SQM'] = total_sqm
            pivot_data.append(row)
        return pd.DataFrame(pivot_data)