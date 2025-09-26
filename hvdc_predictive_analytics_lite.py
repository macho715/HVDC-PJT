#!/usr/bin/env python3
"""
HVDC Predictive Analytics Engine Lite v1.0
기본 라이브러리만 사용하는 예측 분석 시스템
Author: MACHO-GPT v3.4-mini │ Samsung C&T Logistics
"""

import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class HVDCPredictiveAnalyticsLite:
    """HVDC 예측 분석 라이트 엔진"""
    
    def __init__(self, db_path="hvdc_ontology.db"):
        self.db_path = db_path
        self.results = {}
        self.predictions = {}
        
    def load_data(self):
        """데이터 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 아이템 데이터 로드
            self.items_df = pd.read_sql_query("""
                SELECT hvdc_code, vendor, category, weight, location, status, risk_level
                FROM items
            """, conn)
            
            # 창고 데이터 로드 (가상)
            self.warehouse_df = pd.DataFrame({
                'name': ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA Storage', 'MOSB', 'DAS', 'AGI'],
                'capacity_sqm': [10000, 8000, 12000, 5000, 8000, 6000, 4000],
                'current_utilization': [8500, 6400, 8040, 3000, 3600, 2400, 1600],
                'type': ['Indoor', 'Indoor', 'Outdoor', 'Dangerous', 'Outdoor', 'Site', 'Site']
            })
            
            conn.close()
            
            print(f"✅ 데이터 로드 완료: {len(self.items_df)}개 아이템, {len(self.warehouse_df)}개 창고")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def predict_capacity_utilization(self, days_ahead=30):
        """창고 용량 사용률 예측"""
        predictions = []
        
        for _, warehouse in self.warehouse_df.iterrows():
            current_util = warehouse['current_utilization']
            capacity = warehouse['capacity_sqm']
            current_rate = current_util / capacity
            
            # 간단한 선형 예측 (계절성 고려)
            seasonal_factor = 1.1 if datetime.now().month in [11, 12, 1, 2] else 1.0
            growth_rate = 0.02 * seasonal_factor  # 월 2% 증가 (계절 조정)
            
            future_util = current_util * (1 + growth_rate * days_ahead / 30)
            future_rate = min(future_util / capacity, 1.0)  # 100% 초과 방지
            
            risk_level = "HIGH" if future_rate > 0.9 else "MEDIUM" if future_rate > 0.75 else "LOW"
            
            predictions.append({
                'warehouse': warehouse['name'],
                'current_utilization': f"{current_rate:.1%}",
                'predicted_utilization': f"{future_rate:.1%}",
                'days_ahead': days_ahead,
                'risk_level': risk_level,
                'recommended_action': self._get_action_recommendation(future_rate)
            })
        
        return predictions
    
    def _get_action_recommendation(self, util_rate):
        """행동 권고사항 생성"""
        if util_rate > 0.9:
            return "URGENT: 추가 저장 공간 확보 필요"
        elif util_rate > 0.8:
            return "WARNING: 용량 모니터링 강화 필요"
        elif util_rate > 0.7:
            return "WATCH: 정기 모니터링 유지"
        else:
            return "NORMAL: 현재 수준 유지"
    
    def predict_risk_trends(self):
        """위험 아이템 트렌드 예측"""
        # 중량별 위험도 분석
        weight_analysis = {
            'CRITICAL': len(self.items_df[self.items_df['weight'] > 50000]),
            'HIGH': len(self.items_df[(self.items_df['weight'] > 25000) & (self.items_df['weight'] <= 50000)]),
            'MEDIUM': len(self.items_df[(self.items_df['weight'] > 10000) & (self.items_df['weight'] <= 25000)]),
            'LOW': len(self.items_df[self.items_df['weight'] <= 10000])
        }
        
        total_items = sum(weight_analysis.values())
        
        # 예측 트렌드 (향후 30일)
        trend_predictions = {}
        for level, count in weight_analysis.items():
            # 계절성 및 프로젝트 진행률 고려
            if level == 'CRITICAL':
                growth_factor = 0.05  # 5% 증가 예상
            elif level == 'HIGH':
                growth_factor = 0.08  # 8% 증가 예상
            else:
                growth_factor = 0.03  # 3% 증가 예상
            
            predicted_count = int(count * (1 + growth_factor))
            trend_predictions[level] = {
                'current': count,
                'predicted_30days': predicted_count,
                'change': predicted_count - count,
                'change_percent': f"{growth_factor:.1%}"
            }
        
        return {
            'current_distribution': weight_analysis,
            'total_items': total_items,
            'predictions': trend_predictions,
            'overall_risk_score': self._calculate_risk_score(weight_analysis, total_items)
        }
    
    def _calculate_risk_score(self, weight_analysis, total_items):
        """전체 위험 점수 계산"""
        if total_items == 0:
            return 0
        
        # 가중치 적용 위험 점수
        weights = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        weighted_score = sum(weight_analysis[level] * weights[level] for level in weights)
        max_score = total_items * 4  # 모든 아이템이 CRITICAL인 경우
        
        return round((weighted_score / max_score) * 100, 1) if max_score > 0 else 0
    
    def predict_vendor_performance(self):
        """벤더 성능 예측"""
        vendor_stats = {}
        
        for vendor in self.items_df['vendor'].unique():
            vendor_items = self.items_df[self.items_df['vendor'] == vendor]
            
            # 현재 통계
            avg_weight = vendor_items['weight'].mean()
            total_items = len(vendor_items)
            high_risk_items = len(vendor_items[vendor_items['weight'] > 25000])
            
            # 성능 점수 계산 (0-100)
            weight_score = min(100, (avg_weight / 50000) * 100)  # 50톤 기준
            risk_ratio = high_risk_items / total_items if total_items > 0 else 0
            risk_score = risk_ratio * 100
            
            overall_score = max(0, 100 - weight_score * 0.3 - risk_score * 0.7)
            
            # 예측 트렌드
            performance_trend = "IMPROVING" if overall_score > 70 else "STABLE" if overall_score > 50 else "DECLINING"
            
            vendor_stats[vendor] = {
                'total_items': total_items,
                'avg_weight_kg': round(avg_weight, 2),
                'high_risk_items': high_risk_items,
                'risk_ratio': f"{risk_ratio:.1%}",
                'performance_score': round(overall_score, 1),
                'predicted_trend': performance_trend,
                'recommendation': self._get_vendor_recommendation(overall_score)
            }
        
        return vendor_stats
    
    def _get_vendor_recommendation(self, score):
        """벤더 권고사항"""
        if score > 80:
            return "EXCELLENT: 현재 수준 유지"
        elif score > 60:
            return "GOOD: 소폭 개선 권장"
        elif score > 40:
            return "FAIR: 성능 개선 필요"
        else:
            return "POOR: 집중 관리 필요"
    
    def generate_predictions_report(self):
        """종합 예측 보고서 생성"""
        if not self.load_data():
            return None
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_version': 'HVDC Predictive Analytics Lite v1.0',
            'total_items_analyzed': len(self.items_df),
            'predictions': {
                'capacity_utilization': self.predict_capacity_utilization(),
                'risk_trends': self.predict_risk_trends(),
                'vendor_performance': self.predict_vendor_performance()
            },
            'summary': self._generate_summary()
        }
        
        return report
    
    def _generate_summary(self):
        """요약 정보 생성"""
        capacity_pred = self.predict_capacity_utilization()
        risk_pred = self.predict_risk_trends()
        vendor_pred = self.predict_vendor_performance()
        
        # 주요 위험 요소 식별
        high_risk_warehouses = [w for w in capacity_pred if w['risk_level'] == 'HIGH']
        critical_risk_items = risk_pred['current_distribution']['CRITICAL']
        
        return {
            'high_risk_warehouses': len(high_risk_warehouses),
            'critical_risk_items': critical_risk_items,
            'overall_risk_score': risk_pred['overall_risk_score'],
            'vendor_count': len(vendor_pred),
            'key_recommendations': [
                f"{len(high_risk_warehouses)}개 창고 용량 초과 위험",
                f"{critical_risk_items}개 초고위험 아이템 모니터링 필요",
                f"전체 위험 점수: {risk_pred['overall_risk_score']}/100"
            ]
        }

def main():
    """메인 실행 함수"""
    print("🔮 HVDC Predictive Analytics Lite v1.0 시작")
    print("=" * 60)
    
    engine = HVDCPredictiveAnalyticsLite()
    report = engine.generate_predictions_report()
    
    if not report:
        print("❌ 예측 분석 실패")
        return
    
    # 보고서 출력
    print(f"\n📊 예측 분석 완료: {report['timestamp'][:19]}")
    print(f"📈 분석 아이템: {report['total_items_analyzed']}개")
    
    # 1. 창고 용량 예측
    print("\n🏭 창고 용량 사용률 예측 (30일 후):")
    for pred in report['predictions']['capacity_utilization']:
        risk_icon = "🔴" if pred['risk_level'] == 'HIGH' else "🟡" if pred['risk_level'] == 'MEDIUM' else "🟢"
        print(f"  {risk_icon} {pred['warehouse']}: {pred['current_utilization']} → {pred['predicted_utilization']}")
        print(f"     → {pred['recommended_action']}")
    
    # 2. 위험 트렌드 예측
    print(f"\n🚨 위험 트렌드 예측:")
    risk_trends = report['predictions']['risk_trends']
    print(f"  📊 전체 위험 점수: {risk_trends['overall_risk_score']}/100")
    for level, data in risk_trends['predictions'].items():
        change_icon = "📈" if data['change'] > 0 else "📉" if data['change'] < 0 else "➡️"
        print(f"  {change_icon} {level}: {data['current']}개 → {data['predicted_30days']}개 ({data['change_percent']})")
    
    # 3. 벤더 성능 예측
    print(f"\n🏢 벤더 성능 예측:")
    for vendor, perf in report['predictions']['vendor_performance'].items():
        score_icon = "🟢" if perf['performance_score'] > 70 else "🟡" if perf['performance_score'] > 50 else "🔴"
        print(f"  {score_icon} {vendor}: {perf['performance_score']}점 ({perf['predicted_trend']})")
        print(f"     → {perf['recommendation']}")
    
    # 4. 요약 및 권고사항
    summary = report['summary']
    print(f"\n📋 종합 요약:")
    print(f"  🎯 고위험 창고: {summary['high_risk_warehouses']}개")
    print(f"  ⚠️ 초고위험 아이템: {summary['critical_risk_items']}개")
    print(f"  📊 전체 위험 점수: {summary['overall_risk_score']}/100")
    
    print(f"\n🔧 주요 권고사항:")
    for i, rec in enumerate(summary['key_recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # 리포트 저장
    output_dir = Path("prediction_output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"prediction_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 보고서 저장: {report_file}")
    print("✅ 예측 분석 완료!")
    
    # 추천 명령어
    print(f"\n🔧 추천 명령어:")
    print(f"  /capacity_forecast - 상세 용량 예측")
    print(f"  /risk_monitor - 실시간 위험 모니터링")
    print(f"  /vendor_optimization - 벤더 최적화 분석")

if __name__ == "__main__":
    main() 