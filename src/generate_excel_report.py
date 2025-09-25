import pandas as pd
import numpy as np
from datetime import datetime
from improved_warehouse_inbound_calculator import ImprovedWarehouseInboundCalculator


def generate_enhanced_excel_report():
    """
    개선된 입고 계산기를 사용하여 Enhanced 엑셀 리포트 생성
    """
    print("🚀 Enhanced 엑셀 리포트 생성 시작...")
    
    try:
        # 계산기 생성
        calculator = ImprovedWarehouseInboundCalculator()
        
        # 실제 데이터 로드
        print("📊 실제 데이터 로드 중...")
        hitachi_df = pd.read_excel("../data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
        simense_df = pd.read_excel("../data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
        
        # 데이터 표준화
        hitachi_df['Item'] = hitachi_df.get('HVDC CODE', hitachi_df.get('no.', hitachi_df.index))
        simense_df['Item'] = simense_df.get('HVDC CODE', simense_df.get('No.', simense_df.index))
        
        # 데이터 통합
        combined_df = pd.concat([hitachi_df, simense_df], ignore_index=True)
        
        print(f"📊 데이터 로드 완료: {len(combined_df)}건")
        
        # 종합 리포트 생성
        report = calculator.generate_comprehensive_report(combined_df)
        
        # 엑셀 파일 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../output/HVDC_Warehouse_Enhanced_Report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. 요약 시트
            summary_data = {
                'Metric': [
                    'KPI - 출고-입고 일치율',
                    'KPI - 재고 정확도',
                    'KPI - 월별 Balance 정확도',
                    'Total Items',
                    'Warehouse Items',
                    'Site Items',
                    'Direct Delivery Items',
                    'Fail-safe Mode Recommended',
                    'Monthly Outbound Events',
                    'Monthly Site Inbound Events',
                    'Warehouse Transfer Events',
                    'Analysis Timestamp'
                ],
                'Value': [
                    f"{report['kpi_metrics']['outbound_inbound_accuracy']:.3f}",
                    f"{report['kpi_metrics']['inventory_accuracy']:.3f}",
                    f"{report['kpi_metrics']['monthly_balance_accuracy']:.3f}",
                    report['data_quality']['total_items'],
                    report['data_quality']['warehouse_items'],
                    report['data_quality']['site_items'],
                    report['data_quality']['direct_delivery_items'],
                    report['zero_mode_recommendation']['switch_to_zero'],
                    report['monthly_outbound']['total_outbound'],
                    report['monthly_site_inbound']['total_site_inbound'],
                    report['warehouse_transfer']['total_transfer'],
                    report['timestamp']
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # 2. 월별 출고 시트
            if 'outbound_events' in report['monthly_outbound']:
                outbound_events = report['monthly_outbound']['outbound_events']
                outbound_df = pd.DataFrame(outbound_events)
                if not outbound_df.empty:
                    outbound_df.to_excel(writer, sheet_name='Monthly_Outbound', index=False)
            
            # 3. 월별 현장 입고 시트
            if 'site_inbound_items' in report['monthly_site_inbound']:
                site_inbound_items = report['monthly_site_inbound']['site_inbound_items']
                site_inbound_df = pd.DataFrame(site_inbound_items)
                if not site_inbound_df.empty:
                    site_inbound_df.to_excel(writer, sheet_name='Monthly_Site_Inbound', index=False)
            
            # 4. 직송 상세 시트
            if 'direct_delivery' in report['monthly_site_inbound'] and 'direct_items' in report['monthly_site_inbound']['direct_delivery']:
                direct_items = report['monthly_site_inbound']['direct_delivery']['direct_items']
                if direct_items:
                    direct_df = pd.DataFrame(direct_items)
                    direct_df.to_excel(writer, sheet_name='Direct_Delivery', index=False)
            
            # 5. 창고 재고 시트
            if 'inventory_by_location' in report['warehouse_inventory']:
                inventory_data = []
                for location, items in report['warehouse_inventory']['inventory_by_location'].items():
                    inventory_data.append({
                        'Location': location,
                        'Item_Count': len(items),
                        'Items': ', '.join([f"{item['item']} ({item['date']})" 
                                          for item in items[:5]]) + ('...' if len(items) > 5 else '')
                    })
                
                if inventory_data:
                    inventory_df = pd.DataFrame(inventory_data)
                    inventory_df.to_excel(writer, sheet_name='Warehouse_Inventory', index=False)
            
            # 6. 월별 Balance 검증 시트
            if 'monthly_results' in report['balance_validation']:
                balance_data = []
                for month, result in report['balance_validation']['monthly_results'].items():
                    balance_data.append({
                        'Month': month,
                        'Outbound_Count': result['outbound_count'],
                        'Site_Inbound_Count': result['site_inbound_count'],
                        'Balance_OK': result['balance_ok'],
                        'Note': result['note']
                    })
                
                if balance_data:
                    balance_df = pd.DataFrame(balance_data)
                    balance_df.to_excel(writer, sheet_name='Monthly_Balance', index=False)
            
            # 7. 월별 출고 요약 시트
            if 'monthly_total' in report['monthly_outbound']:
                outbound_monthly_data = []
                for month, count in report['monthly_outbound']['monthly_total'].items():
                    outbound_monthly_data.append({
                        'Month': month,
                        'Outbound_Count': count
                    })
                
                if outbound_monthly_data:
                    outbound_monthly_df = pd.DataFrame(outbound_monthly_data)
                    outbound_monthly_df.to_excel(writer, sheet_name='Monthly_Outbound_Summary', index=False)
            
            # 8. 월별 현장 입고 요약 시트
            if 'monthly_total' in report['monthly_site_inbound']:
                site_monthly_data = []
                for month, count in report['monthly_site_inbound']['monthly_total'].items():
                    site_monthly_data.append({
                        'Month': month,
                        'Site_Inbound_Count': count
                    })
                
                if site_monthly_data:
                    site_monthly_df = pd.DataFrame(site_monthly_data)
                    site_monthly_df.to_excel(writer, sheet_name='Monthly_Site_Inbound_Summary', index=False)
            
            # 9. 원본 데이터 샘플 시트
            sample_data = combined_df.head(100)
            sample_data.to_excel(writer, sheet_name='Sample_Data', index=False)
            
        print(f"✅ Enhanced 엑셀 리포트 생성 완료: {filename}")
        
        # 결과 요약 출력
        print(f"\n📊 리포트 요약:")
        print(f"   출고-입고 일치율: {report['kpi_metrics']['outbound_inbound_accuracy']:.3f}")
        print(f"   월별 Balance 정확도: {report['kpi_metrics']['monthly_balance_accuracy']:.3f}")
        print(f"   Fail-safe 권장: {report['zero_mode_recommendation']['switch_to_zero']}")
        print(f"   전체 항목: {report['data_quality']['total_items']}건")
        print(f"   창고 항목: {report['data_quality']['warehouse_items']}건")
        print(f"   직송 항목: {report['data_quality']['direct_delivery_items']}건")
        
        return filename
        
    except Exception as e:
        print(f"❌ 엑셀 리포트 생성 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    generate_enhanced_excel_report() 