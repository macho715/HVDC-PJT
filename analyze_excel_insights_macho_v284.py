#!/usr/bin/env python3
"""
🎯 MACHO Excel Insights Analyzer v2.8.4
MACHO-GPT v3.4-mini │ Samsung C&T Logistics

Excel 파일 심화 분석 및 물류 최적화 인사이트 생성
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

class MACHOExcelInsightsAnalyzer:
    def __init__(self):
        print("🎯 MACHO Excel Insights Analyzer v2.8.4")
        print("=" * 80)
        print("📊 Excel 파일 심화 분석 및 물류 최적화 인사이트 생성")
        print("-" * 80)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Excel 파일 찾기
        excel_files = [f for f in os.listdir('.') if f.startswith('MACHO_WH_HANDLING') and f.endswith('.xlsx')]
        if not excel_files:
            raise FileNotFoundError("❌ MACHO WH HANDLING Excel 파일을 찾을 수 없습니다.")
        
        self.excel_file = excel_files[0]
        print(f"📁 분석 대상: {self.excel_file}")
        
        # 데이터 로드
        self.data = {}
        self.insights = {}
        self.recommendations = []
        
    def load_all_data(self):
        """모든 시트 데이터 로드"""
        print(f"\n📂 Excel 시트 데이터 로드 중...")
        print("-" * 50)
        
        try:
            all_sheets = pd.read_excel(self.excel_file, sheet_name=None)
            
            for sheet_name, df in all_sheets.items():
                self.data[sheet_name] = df
                print(f"✅ {sheet_name}: {len(df):,}행 × {len(df.columns)}열")
            
            print(f"🎉 총 {len(all_sheets)}개 시트 로드 완료")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def analyze_flow_code_patterns(self):
        """Flow Code 패턴 상세 분석"""
        print(f"\n🚚 Flow Code 패턴 상세 분석")
        print("-" * 50)
        
        df_main = self.data['전체_트랜잭션데이터']
        
        # 1. Flow Code별 벤더 분포
        flow_vendor = df_main.groupby(['FLOW_CODE', 'VENDOR']).size().unstack(fill_value=0)
        print(f"📊 Flow Code별 벤더 분포:")
        print(flow_vendor.to_string())
        
        # 2. Flow Code 효율성 분석
        flow_efficiency = {}
        total_transactions = len(df_main)
        
        for flow_code in range(4):
            flow_data = df_main[df_main['FLOW_CODE'] == flow_code]
            count = len(flow_data)
            percentage = count / total_transactions * 100
            
            # 창고 경유 효율성 계산 (직접운송이 가장 효율적)
            efficiency_score = 100 - (flow_code * 20)  # Code 0: 100%, Code 1: 80%, Code 2: 60%, Code 3: 40%
            
            flow_efficiency[flow_code] = {
                'count': count,
                'percentage': percentage,
                'efficiency_score': efficiency_score,
                'cost_index': flow_code + 1  # 경유 횟수에 비례한 비용 지수
            }
        
        self.insights['flow_patterns'] = flow_efficiency
        
        # 3. 최적화 기회 분석
        code_2_3_count = len(df_main[df_main['FLOW_CODE'] >= 2])
        optimization_potential = code_2_3_count / total_transactions * 100
        
        print(f"\n💡 Flow Code 최적화 인사이트:")
        print(f"   🎯 최적화 대상: Code 2+3 = {code_2_3_count:,}건 ({optimization_potential:.1f}%)")
        print(f"   💰 예상 비용 절감 기회: {optimization_potential:.1f}% 물류비 절감 가능")
        
        if optimization_potential > 15:
            self.recommendations.append("창고 경유 최소화를 통한 물류비 절감 (15% 이상 개선 기회)")
    
    def analyze_vendor_efficiency(self):
        """벤더별 효율성 분석"""
        print(f"\n🏭 벤더별 효율성 분석")
        print("-" * 50)
        
        df_main = self.data['전체_트랜잭션데이터']
        
        vendor_analysis = {}
        
        for vendor in ['HITACHI', 'SIMENSE']:
            vendor_data = df_main[df_main['VENDOR'] == vendor]
            
            # 효율성 지표 계산
            flow_dist = vendor_data['FLOW_CODE'].value_counts().sort_index()
            direct_rate = flow_dist.get(0, 0) / len(vendor_data) * 100
            avg_wh_handling = vendor_data['WH_HANDLING'].mean()
            
            # 효율성 점수 (직접운송 비율 높을수록 효율적)
            efficiency_score = direct_rate * 0.6 + (100 - avg_wh_handling * 25) * 0.4
            
            vendor_analysis[vendor] = {
                'total_transactions': len(vendor_data),
                'direct_rate': direct_rate,
                'avg_wh_handling': avg_wh_handling,
                'efficiency_score': efficiency_score,
                'flow_distribution': flow_dist.to_dict()
            }
            
            print(f"📈 {vendor} 효율성 지표:")
            print(f"   📊 총 트랜잭션: {len(vendor_data):,}건")
            print(f"   🚀 직접운송률: {direct_rate:.1f}%")
            print(f"   🏠 평균 창고경유: {avg_wh_handling:.2f}회")
            print(f"   ⭐ 효율성 점수: {efficiency_score:.1f}점")
            print()
        
        self.insights['vendor_efficiency'] = vendor_analysis
        
        # 벤더 간 비교 및 추천
        hitachi_eff = vendor_analysis['HITACHI']['efficiency_score']
        simense_eff = vendor_analysis['SIMENSE']['efficiency_score']
        
        if abs(hitachi_eff - simense_eff) > 10:
            better_vendor = 'HITACHI' if hitachi_eff > simense_eff else 'SIMENSE'
            self.recommendations.append(f"{better_vendor} 벤더의 물류 패턴을 벤치마킹하여 효율성 개선")
    
    def analyze_warehouse_utilization(self):
        """창고별 활용도 상세 분석"""
        print(f"\n🏠 창고별 활용도 상세 분석")
        print("-" * 50)
        
        df_main = self.data['전체_트랜잭션데이터']
        
        # 창고 컬럼 리스트
        warehouse_columns = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 
                           'Hauler Indoor', 'DSV MZP', 'MOSB']
        
        warehouse_analysis = {}
        
        for wh in warehouse_columns:
            if wh in df_main.columns:
                # 사용 빈도
                usage_count = df_main[wh].notna().sum()
                usage_rate = usage_count / len(df_main) * 100
                
                # 벤더별 사용 패턴
                vendor_usage = df_main[df_main[wh].notna()]['VENDOR'].value_counts()
                
                # Flow Code별 사용 패턴
                flow_usage = df_main[df_main[wh].notna()]['FLOW_CODE'].value_counts().sort_index()
                
                warehouse_analysis[wh] = {
                    'usage_count': usage_count,
                    'usage_rate': usage_rate,
                    'vendor_breakdown': vendor_usage.to_dict(),
                    'flow_breakdown': flow_usage.to_dict()
                }
                
                print(f"🏢 {wh}:")
                print(f"   📊 사용 건수: {usage_count:,}건 ({usage_rate:.1f}%)")
                print(f"   🏭 주요 벤더: {vendor_usage.index[0] if len(vendor_usage) > 0 else 'N/A'}")
                print(f"   🚚 주요 Flow: Code {flow_usage.index[0] if len(flow_usage) > 0 else 'N/A'}")
                print()
        
        self.insights['warehouse_utilization'] = warehouse_analysis
        
        # 활용도 기반 추천
        usage_rates = [(wh, data['usage_rate']) for wh, data in warehouse_analysis.items()]
        usage_rates.sort(key=lambda x: x[1], reverse=True)
        
        # 저활용 창고 식별
        low_usage_warehouses = [wh for wh, rate in usage_rates if rate < 20]
        if low_usage_warehouses:
            self.recommendations.append(f"저활용 창고 최적화: {', '.join(low_usage_warehouses)} 재배치 검토")
    
    def analyze_cost_optimization(self):
        """비용 최적화 분석"""
        print(f"\n💰 비용 최적화 분석")
        print("-" * 50)
        
        df_main = self.data['전체_트랜잭션데이터']
        
        # 비용 모델 (가정: Flow Code에 따른 상대적 비용)
        cost_multipliers = {0: 1.0, 1: 1.5, 2: 2.2, 3: 3.0}
        
        cost_analysis = {}
        total_cost_index = 0
        
        for flow_code in range(4):
            flow_data = df_main[df_main['FLOW_CODE'] == flow_code]
            count = len(flow_data)
            cost_multiplier = cost_multipliers[flow_code]
            flow_cost_index = count * cost_multiplier
            
            cost_analysis[flow_code] = {
                'transaction_count': count,
                'cost_multiplier': cost_multiplier,
                'total_cost_index': flow_cost_index,
                'percentage_of_total_cost': 0  # 나중에 계산
            }
            
            total_cost_index += flow_cost_index
        
        # 비용 비율 계산
        for flow_code in cost_analysis:
            cost_analysis[flow_code]['percentage_of_total_cost'] = \
                cost_analysis[flow_code]['total_cost_index'] / total_cost_index * 100
        
        print(f"📊 Flow Code별 비용 분석:")
        for flow_code, data in cost_analysis.items():
            print(f"   Code {flow_code}: {data['transaction_count']:,}건 "
                  f"× {data['cost_multiplier']}배 = 비용지수 {data['total_cost_index']:,.0f} "
                  f"({data['percentage_of_total_cost']:.1f}%)")
        
        # 최적화 시나리오
        current_avg_cost = total_cost_index / len(df_main)
        
        # 시나리오: Code 2,3을 Code 1로 최적화
        optimizable_transactions = len(df_main[df_main['FLOW_CODE'] >= 2])
        potential_savings = optimizable_transactions * (cost_multipliers[2] - cost_multipliers[1])
        savings_percentage = potential_savings / total_cost_index * 100
        
        print(f"\n💡 비용 최적화 시나리오:")
        print(f"   🎯 최적화 대상: {optimizable_transactions:,}건 (Code 2+3 → Code 1)")
        print(f"   💰 예상 비용 절감: {savings_percentage:.1f}%")
        print(f"   📈 현재 평균 비용지수: {current_avg_cost:.2f}")
        
        self.insights['cost_optimization'] = {
            'current_analysis': cost_analysis,
            'optimization_potential': {
                'optimizable_transactions': optimizable_transactions,
                'potential_savings_percentage': savings_percentage,
                'current_avg_cost_index': current_avg_cost
            }
        }
        
        if savings_percentage > 10:
            self.recommendations.append(f"비용 최적화 우선순위: {savings_percentage:.1f}% 절감 가능한 물류 경로 재설계")
    
    def generate_business_insights(self):
        """비즈니스 인사이트 생성"""
        print(f"\n🎯 비즈니스 인사이트 및 전략적 추천")
        print("-" * 50)
        
        df_main = self.data['전체_트랜잭션데이터']
        
        # 핵심 KPI
        total_transactions = len(df_main)
        direct_rate = len(df_main[df_main['FLOW_CODE'] == 0]) / total_transactions * 100
        multi_warehouse_rate = len(df_main[df_main['FLOW_CODE'] >= 2]) / total_transactions * 100
        
        print(f"📊 핵심 KPI:")
        print(f"   📈 총 트랜잭션: {total_transactions:,}건")
        print(f"   🚀 직접운송률: {direct_rate:.1f}%")
        print(f"   🏠 복합창고경유률: {multi_warehouse_rate:.1f}%")
        
        # 효율성 등급 평가
        if direct_rate >= 40:
            efficiency_grade = "A (우수)"
        elif direct_rate >= 30:
            efficiency_grade = "B (양호)"
        elif direct_rate >= 20:
            efficiency_grade = "C (보통)"
        else:
            efficiency_grade = "D (개선필요)"
        
        print(f"   ⭐ 물류 효율성 등급: {efficiency_grade}")
        
        # 전략적 추천사항
        strategic_recommendations = []
        
        if direct_rate < 35:
            strategic_recommendations.append("직접운송 비율 증대를 통한 물류비 절감")
        
        if multi_warehouse_rate > 15:
            strategic_recommendations.append("복합창고경유 최소화를 통한 리드타임 단축")
        
        # 벤더별 불균형 체크
        hitachi_ratio = len(df_main[df_main['VENDOR'] == 'HITACHI']) / total_transactions
        if hitachi_ratio > 0.8 or hitachi_ratio < 0.2:
            strategic_recommendations.append("벤더 포트폴리오 균형 조정 검토")
        
        strategic_recommendations.extend(self.recommendations)
        
        self.insights['business_summary'] = {
            'total_transactions': total_transactions,
            'direct_rate': direct_rate,
            'multi_warehouse_rate': multi_warehouse_rate,
            'efficiency_grade': efficiency_grade,
            'strategic_recommendations': strategic_recommendations
        }
        
        print(f"\n🎯 전략적 추천사항:")
        for i, rec in enumerate(strategic_recommendations, 1):
            print(f"   {i}. {rec}")
    
    def generate_insights_report(self):
        """종합 인사이트 리포트 생성"""
        print(f"\n📋 종합 인사이트 리포트 생성 중...")
        print("-" * 50)
        
        # Excel 리포트 생성
        output_file = f"MACHO_Excel_인사이트분석리포트_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # 스타일 정의
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2E8B57',
                'font_color': 'white',
                'border': 1
            })
            
            # 1. 종합 요약
            summary_data = []
            business_summary = self.insights.get('business_summary', {})
            
            summary_data.append(['구분', '값', '설명'])
            summary_data.append(['총 트랜잭션', f"{business_summary.get('total_transactions', 0):,}건", 'HITACHI + SIMENSE 통합'])
            summary_data.append(['직접운송률', f"{business_summary.get('direct_rate', 0):.1f}%", 'Flow Code 0 비율'])
            summary_data.append(['복합창고경유률', f"{business_summary.get('multi_warehouse_rate', 0):.1f}%", 'Flow Code 2+3 비율'])
            summary_data.append(['효율성 등급', business_summary.get('efficiency_grade', 'N/A'), '물류 효율성 평가'])
            
            summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
            summary_df.to_excel(writer, sheet_name='종합요약', index=False)
            
            # 2. Flow Code 분석
            if 'flow_patterns' in self.insights:
                flow_data = []
                flow_data.append(['Flow Code', '트랜잭션 수', '비율', '효율성 점수', '비용 지수'])
                
                for code, data in self.insights['flow_patterns'].items():
                    flow_data.append([
                        f"Code {code}",
                        f"{data['count']:,}건",
                        f"{data['percentage']:.1f}%",
                        f"{data['efficiency_score']}점",
                        f"{data['cost_index']}배"
                    ])
                
                flow_df = pd.DataFrame(flow_data[1:], columns=flow_data[0])
                flow_df.to_excel(writer, sheet_name='Flow_Code_분석', index=False)
            
            # 3. 벤더별 효율성
            if 'vendor_efficiency' in self.insights:
                vendor_data = []
                vendor_data.append(['벤더', '트랜잭션 수', '직접운송률', '평균 창고경유', '효율성 점수'])
                
                for vendor, data in self.insights['vendor_efficiency'].items():
                    vendor_data.append([
                        vendor,
                        f"{data['total_transactions']:,}건",
                        f"{data['direct_rate']:.1f}%",
                        f"{data['avg_wh_handling']:.2f}회",
                        f"{data['efficiency_score']:.1f}점"
                    ])
                
                vendor_df = pd.DataFrame(vendor_data[1:], columns=vendor_data[0])
                vendor_df.to_excel(writer, sheet_name='벤더별_효율성', index=False)
            
            # 4. 창고별 활용도
            if 'warehouse_utilization' in self.insights:
                wh_data = []
                wh_data.append(['창고명', '사용 건수', '활용률', '주요 벤더', '주요 Flow Code'])
                
                for wh, data in self.insights['warehouse_utilization'].items():
                    main_vendor = max(data['vendor_breakdown'].items(), key=lambda x: x[1])[0] if data['vendor_breakdown'] else 'N/A'
                    main_flow = max(data['flow_breakdown'].items(), key=lambda x: x[1])[0] if data['flow_breakdown'] else 'N/A'
                    
                    wh_data.append([
                        wh,
                        f"{data['usage_count']:,}건",
                        f"{data['usage_rate']:.1f}%",
                        main_vendor,
                        f"Code {main_flow}"
                    ])
                
                wh_df = pd.DataFrame(wh_data[1:], columns=wh_data[0])
                wh_df.to_excel(writer, sheet_name='창고별_활용도', index=False)
            
            # 5. 추천사항
            recommendations = business_summary.get('strategic_recommendations', [])
            rec_data = []
            rec_data.append(['순위', '추천사항', '우선순위'])
            
            for i, rec in enumerate(recommendations, 1):
                priority = "높음" if i <= 3 else "보통" if i <= 6 else "낮음"
                rec_data.append([i, rec, priority])
            
            rec_df = pd.DataFrame(rec_data[1:], columns=rec_data[0])
            rec_df.to_excel(writer, sheet_name='전략적_추천사항', index=False)
        
        # JSON 리포트도 생성
        json_file = f"MACHO_Excel_인사이트분석_{self.timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.insights, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Excel 리포트: {output_file}")
        print(f"✅ JSON 리포트: {json_file}")
        
        return output_file, json_file
    
    def run_complete_analysis(self):
        """전체 분석 실행"""
        print(f"\n🚀 MACHO Excel 인사이트 분석 시작")
        print("=" * 80)
        
        try:
            # 1. 데이터 로드
            if not self.load_all_data():
                return False
            
            # 2. 각종 분석 수행
            self.analyze_flow_code_patterns()
            self.analyze_vendor_efficiency()
            self.analyze_warehouse_utilization()
            self.analyze_cost_optimization()
            self.generate_business_insights()
            
            # 3. 리포트 생성
            excel_file, json_file = self.generate_insights_report()
            
            # 4. 최종 결과 출력
            print(f"\n🎉 MACHO Excel 인사이트 분석 완료!")
            print("=" * 80)
            print(f"📊 분석 대상: {self.excel_file}")
            print(f"📁 Excel 인사이트 리포트: {excel_file}")
            print(f"📋 JSON 상세 데이터: {json_file}")
            
            # 핵심 인사이트 요약
            business_summary = self.insights.get('business_summary', {})
            print(f"\n🎯 핵심 인사이트:")
            print(f"   📈 총 트랜잭션: {business_summary.get('total_transactions', 0):,}건")
            print(f"   🚀 직접운송률: {business_summary.get('direct_rate', 0):.1f}%")
            print(f"   ⭐ 효율성 등급: {business_summary.get('efficiency_grade', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    print("🎯 MACHO-GPT v3.4-mini │ Samsung C&T Logistics")
    print("Excel Insights Analyzer - 물류 최적화 인사이트 생성")
    print("=" * 80)
    
    try:
        analyzer = MACHOExcelInsightsAnalyzer()
        success = analyzer.run_complete_analysis()
        
        if success:
            print("\n🔧 **추천 명령어:**")
            print("/generate_optimization_roadmap [물류 최적화 로드맵 생성]")
            print("/create_warehouse_efficiency_dashboard [창고 효율성 대시보드]")
            print("/export_cost_analysis_report [비용 분석 리포트 추출]")
        else:
            print("\n⚠️ 분석이 완료되지 않았습니다. 로그를 확인해주세요.")
            
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    main() 