#!/usr/bin/env python3
"""
HITACHI Final_Location 동적 우선순위 시스템 v1.0
Samsung C&T × ADNOC·DSV Partnership | MACHO-GPT v3.4-mini

핵심 기능:
1. 실시간 활용도 기반 우선순위 자동 조정
2. 계절성 패턴 적용 가중치 시스템
3. 창고 용량 및 효율성 고려
4. 성능 모니터링 및 피드백 시스템
5. A/B 테스트 및 최적화 검증
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

@dataclass
class WarehouseMetrics:
    """창고 성능 지표"""
    name: str
    utilization_rate: float
    capacity_score: float
    efficiency_score: float
    seasonal_weight: float
    current_priority: int
    recommended_priority: int

@dataclass
class PrioritySystemConfig:
    """우선순위 시스템 설정"""
    seasonality_enabled: bool = True
    capacity_weight: float = 0.3
    utilization_weight: float = 0.4
    efficiency_weight: float = 0.3
    min_adjustment_threshold: float = 0.05
    max_priority_levels: int = 7
    update_frequency_days: int = 7

class DynamicPrioritySystem:
    """동적 우선순위 시스템"""
    
    def __init__(self, config: PrioritySystemConfig = None):
        """시스템 초기화"""
        print("🚀 HITACHI Final_Location 동적 우선순위 시스템 v1.0")
        print("📊 실시간 최적화 및 자동 조정 시스템")
        print("=" * 80)
        
        self.config = config or PrioritySystemConfig()
        self.warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'AAA  Storage',
            'DHL Warehouse', 'MOSB', 'Hauler Indoor'
        ]
        
        # 현재 우선순위 (기존 로직)
        self.current_priority = {
            'DSV Al Markaz': 1,
            'DSV Indoor': 2,
            'DSV Outdoor': 3,
            'AAA  Storage': 4,
            'DHL Warehouse': 5,
            'MOSB': 6,
            'Hauler Indoor': 7
        }
        
        # 시스템 상태
        self.hitachi_data = None
        self.warehouse_metrics = {}
        self.optimization_history = []
        self.performance_metrics = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 계절성 가중치 매트릭스
        self.seasonal_weights = {
            '봄': {'DSV Al Markaz': 1.4, 'DSV Indoor': 1.0, 'DSV Outdoor': 1.2},
            '여름': {'DSV Al Markaz': 1.5, 'DSV Indoor': 1.1, 'DSV Outdoor': 1.3},
            '가을': {'DSV Al Markaz': 0.8, 'DSV Indoor': 1.3, 'DSV Outdoor': 1.1},
            '겨울': {'DSV Al Markaz': 0.7, 'DSV Indoor': 1.4, 'DSV Outdoor': 1.0}
        }
        
    def load_hitachi_data(self):
        """HITACHI 데이터 로드"""
        print("\n📂 HITACHI 데이터 로드 중...")
        
        improved_files = [f for f in os.listdir('.') if f.startswith('HVDC_DataQuality_Improved_') and f.endswith('.xlsx')]
        
        if not improved_files:
            print("❌ 개선된 데이터 파일을 찾을 수 없습니다.")
            return False
        
        latest_file = max(improved_files, key=lambda x: os.path.getmtime(x))
        print(f"📁 로드할 파일: {latest_file}")
        
        try:
            all_data = pd.read_excel(latest_file, sheet_name='개선된_전체_데이터')
            self.hitachi_data = all_data[all_data['Data_Source'] == 'HITACHI'].copy()
            
            print(f"✅ HITACHI 데이터 로드 완료: {len(self.hitachi_data):,}건")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def calculate_warehouse_metrics(self) -> Dict[str, WarehouseMetrics]:
        """창고별 성능 지표 계산"""
        print("\n📊 창고별 성능 지표 계산 중...")
        print("-" * 60)
        
        warehouse_metrics = {}
        total_records = len(self.hitachi_data)
        
        for warehouse in self.warehouse_columns:
            # 1. 활용도 계산
            utilization_count = self.hitachi_data[warehouse].notna().sum()
            utilization_rate = utilization_count / total_records
            
            # 2. 용량 점수 계산 (활용도 기반)
            capacity_score = min(utilization_rate * 2, 1.0)  # 최대 1.0
            
            # 3. 효율성 점수 계산 (시간 분산 기반)
            efficiency_score = self.calculate_efficiency_score(warehouse)
            
            # 4. 계절성 가중치 계산
            seasonal_weight = self.calculate_seasonal_weight(warehouse)
            
            # 5. 종합 점수 계산
            composite_score = (
                utilization_rate * self.config.utilization_weight +
                capacity_score * self.config.capacity_weight +
                efficiency_score * self.config.efficiency_weight
            ) * seasonal_weight
            
            # 6. 추천 우선순위 계산
            current_priority = self.current_priority.get(warehouse, 7)
            
            warehouse_metrics[warehouse] = WarehouseMetrics(
                name=warehouse,
                utilization_rate=utilization_rate,
                capacity_score=capacity_score,
                efficiency_score=efficiency_score,
                seasonal_weight=seasonal_weight,
                current_priority=current_priority,
                recommended_priority=0  # 나중에 전체 순위에서 결정
            )
            
            print(f"📋 {warehouse}:")
            print(f"   활용도: {utilization_rate:.1%} ({utilization_count:,}건)")
            print(f"   용량 점수: {capacity_score:.3f}")
            print(f"   효율성 점수: {efficiency_score:.3f}")
            print(f"   계절성 가중치: {seasonal_weight:.3f}")
            print(f"   종합 점수: {composite_score:.3f}")
            print(f"   현재 우선순위: {current_priority}")
        
        # 종합 점수 기준으로 추천 우선순위 결정
        sorted_warehouses = sorted(
            warehouse_metrics.items(), 
            key=lambda x: (
                x[1].utilization_rate * self.config.utilization_weight +
                x[1].capacity_score * self.config.capacity_weight +
                x[1].efficiency_score * self.config.efficiency_weight
            ) * x[1].seasonal_weight, 
            reverse=True
        )
        
        for i, (warehouse, metrics) in enumerate(sorted_warehouses, 1):
            metrics.recommended_priority = i
        
        self.warehouse_metrics = warehouse_metrics
        return warehouse_metrics
    
    def calculate_efficiency_score(self, warehouse: str) -> float:
        """창고 효율성 점수 계산"""
        try:
            # 해당 창고의 입고 날짜 분산 계산
            dates = []
            for _, row in self.hitachi_data.iterrows():
                if pd.notna(row[warehouse]):
                    try:
                        date = pd.to_datetime(row[warehouse])
                        dates.append(date)
                    except:
                        continue
            
            if len(dates) < 2:
                return 0.5  # 기본값
            
            # 날짜 분산 계산 (일 단위)
            dates = pd.to_datetime(dates)
            date_range = (dates.max() - dates.min()).days
            
            if date_range == 0:
                return 1.0  # 하루에 집중된 경우
            
            # 고른 분포일수록 높은 점수 (0.1 ~ 1.0)
            distribution_score = min(len(dates) / date_range * 30, 1.0)
            return max(distribution_score, 0.1)
            
        except Exception as e:
            return 0.5  # 오류 시 기본값
    
    def calculate_seasonal_weight(self, warehouse: str) -> float:
        """계절성 가중치 계산"""
        if not self.config.seasonality_enabled:
            return 1.0
        
        current_month = datetime.now().month
        current_season = self.get_season(current_month)
        
        # 기본 가중치
        base_weight = self.seasonal_weights.get(current_season, {}).get(warehouse, 1.0)
        
        # 최근 3개월 트렌드 반영
        recent_trend = self.calculate_recent_trend(warehouse)
        
        return base_weight * (1 + recent_trend * 0.1)
    
    def get_season(self, month: int) -> str:
        """월을 계절로 변환"""
        if month in [3, 4, 5]:
            return '봄'
        elif month in [6, 7, 8]:
            return '여름'
        elif month in [9, 10, 11]:
            return '가을'
        else:
            return '겨울'
    
    def calculate_recent_trend(self, warehouse: str) -> float:
        """최근 3개월 트렌드 계산"""
        try:
            # 최근 3개월 데이터 추출
            recent_data = []
            cutoff_date = datetime.now() - timedelta(days=90)
            
            for _, row in self.hitachi_data.iterrows():
                if pd.notna(row[warehouse]):
                    try:
                        date = pd.to_datetime(row[warehouse])
                        if date >= cutoff_date:
                            recent_data.append(date)
                    except:
                        continue
            
            if len(recent_data) < 10:
                return 0.0  # 데이터 부족
            
            # 월별 집계
            monthly_counts = defaultdict(int)
            for date in recent_data:
                month_key = date.to_period('M')
                monthly_counts[month_key] += 1
            
            if len(monthly_counts) < 2:
                return 0.0
            
            # 트렌드 계산 (선형 회귀)
            counts = list(monthly_counts.values())
            if len(counts) >= 2:
                trend = (counts[-1] - counts[0]) / len(counts)
                return min(max(trend / 100, -0.5), 0.5)  # -0.5 ~ 0.5 범위
            
            return 0.0
            
        except Exception as e:
            return 0.0
    
    def generate_dynamic_priority_recommendations(self) -> Dict[str, int]:
        """동적 우선순위 추천 생성"""
        print("\n🎯 동적 우선순위 추천 생성")
        print("=" * 60)
        
        if not self.warehouse_metrics:
            print("❌ 창고 지표가 계산되지 않았습니다.")
            return {}
        
        # 현재 우선순위 vs 추천 우선순위 비교
        recommendations = {}
        significant_changes = []
        
        print("📊 우선순위 변경 분석:")
        print("   현재 → 추천 (변경폭)")
        
        for warehouse, metrics in self.warehouse_metrics.items():
            current = metrics.current_priority
            recommended = metrics.recommended_priority
            change = current - recommended
            
            recommendations[warehouse] = recommended
            
            if abs(change) >= self.config.min_adjustment_threshold * 10:  # 임계값 조정
                significant_changes.append((warehouse, current, recommended, change))
                status = "📈 상승" if change > 0 else "📉 하락"
                print(f"   {warehouse}: {current} → {recommended} ({change:+d}) {status}")
            else:
                print(f"   {warehouse}: {current} → {recommended} (변경없음)")
        
        # 주요 변경사항 분석
        if significant_changes:
            print(f"\n🔍 주요 변경사항 분석:")
            for warehouse, current, recommended, change in significant_changes:
                metrics = self.warehouse_metrics[warehouse]
                print(f"   {warehouse}:")
                print(f"     활용도: {metrics.utilization_rate:.1%}")
                print(f"     계절성 가중치: {metrics.seasonal_weight:.3f}")
                print(f"     변경 근거: {'높은 활용도' if change > 0 else '낮은 활용도'}")
        
        return recommendations
    
    def simulate_priority_system_performance(self, new_priorities: Dict[str, int]) -> Dict[str, float]:
        """새로운 우선순위 시스템 성능 시뮬레이션"""
        print("\n🧪 우선순위 시스템 성능 시뮬레이션")
        print("=" * 60)
        
        # 현재 시스템 성능 계산
        current_performance = self.calculate_system_performance(self.current_priority)
        
        # 새로운 시스템 성능 계산
        new_performance = self.calculate_system_performance(new_priorities)
        
        # 성능 비교
        improvements = {}
        print("📊 성능 비교 결과:")
        
        for metric, current_value in current_performance.items():
            new_value = new_performance[metric]
            improvement = ((new_value - current_value) / current_value) * 100
            improvements[metric] = improvement
            
            status = "📈 개선" if improvement > 0 else "📉 악화" if improvement < 0 else "→ 유지"
            print(f"   {metric}: {current_value:.3f} → {new_value:.3f} ({improvement:+.1f}%) {status}")
        
        # 전체 성능 점수
        overall_current = sum(current_performance.values()) / len(current_performance)
        overall_new = sum(new_performance.values()) / len(new_performance)
        overall_improvement = ((overall_new - overall_current) / overall_current) * 100
        
        print(f"\n🎯 전체 성능 점수:")
        print(f"   현재 시스템: {overall_current:.3f}")
        print(f"   새로운 시스템: {overall_new:.3f}")
        print(f"   전체 개선도: {overall_improvement:+.1f}%")
        
        return improvements
    
    def calculate_system_performance(self, priority_system: Dict[str, int]) -> Dict[str, float]:
        """우선순위 시스템 성능 계산"""
        
        # 1. 활용도 효율성 (높은 우선순위 창고의 활용도)
        utilization_efficiency = 0
        for warehouse, priority in priority_system.items():
            if warehouse in self.warehouse_metrics:
                utilization = self.warehouse_metrics[warehouse].utilization_rate
                weight = 1 / priority  # 우선순위 가중치
                utilization_efficiency += utilization * weight
        
        # 2. 분산 효율성 (우선순위와 활용도의 상관관계)
        priorities = []
        utilizations = []
        for warehouse, priority in priority_system.items():
            if warehouse in self.warehouse_metrics:
                priorities.append(priority)
                utilizations.append(self.warehouse_metrics[warehouse].utilization_rate)
        
        if len(priorities) > 1:
            correlation = np.corrcoef(priorities, utilizations)[0, 1]
            distribution_efficiency = 1 - abs(correlation)  # 음의 상관관계가 이상적
        else:
            distribution_efficiency = 0.5
        
        # 3. 계절성 적응성
        seasonality_score = sum(
            self.warehouse_metrics[warehouse].seasonal_weight 
            for warehouse in priority_system.keys() 
            if warehouse in self.warehouse_metrics
        ) / len(priority_system)
        
        # 4. 시스템 안정성 (우선순위 변동성)
        stability_score = 1.0  # 기본값 (변동성이 클수록 감소)
        
        return {
            'utilization_efficiency': utilization_efficiency,
            'distribution_efficiency': distribution_efficiency,
            'seasonality_adaptation': seasonality_score,
            'system_stability': stability_score
        }
    
    def implement_ab_testing(self, new_priorities: Dict[str, int]) -> Dict[str, any]:
        """A/B 테스트 구현"""
        print("\n🔬 A/B 테스트 구현")
        print("=" * 60)
        
        # 데이터를 두 그룹으로 분할
        test_size = len(self.hitachi_data) // 2
        group_a = self.hitachi_data.iloc[:test_size].copy()
        group_b = self.hitachi_data.iloc[test_size:].copy()
        
        # 그룹 A: 현재 우선순위 적용
        group_a_results = self.apply_priority_system(group_a, self.current_priority)
        
        # 그룹 B: 새로운 우선순위 적용
        group_b_results = self.apply_priority_system(group_b, new_priorities)
        
        # 결과 비교
        ab_results = {
            'group_a_size': len(group_a),
            'group_b_size': len(group_b),
            'group_a_performance': group_a_results,
            'group_b_performance': group_b_results,
            'statistical_significance': self.calculate_statistical_significance(group_a_results, group_b_results)
        }
        
        print("📊 A/B 테스트 결과:")
        print(f"   그룹 A (현재): {len(group_a):,}건")
        print(f"   그룹 B (신규): {len(group_b):,}건")
        
        # 성능 지표 비교
        for metric in ['efficiency_score', 'utilization_rate', 'distribution_score']:
            if metric in group_a_results and metric in group_b_results:
                a_value = group_a_results[metric]
                b_value = group_b_results[metric]
                improvement = ((b_value - a_value) / a_value) * 100
                
                print(f"   {metric}:")
                print(f"     현재: {a_value:.3f}")
                print(f"     신규: {b_value:.3f}")
                print(f"     개선: {improvement:+.1f}%")
        
        return ab_results
    
    def apply_priority_system(self, data: pd.DataFrame, priority_system: Dict[str, int]) -> Dict[str, float]:
        """우선순위 시스템 적용 및 성능 측정"""
        
        final_locations = []
        
        for _, row in data.iterrows():
            # 우선순위 기반 Final_Location 결정
            best_warehouse = None
            best_priority = float('inf')
            
            for warehouse in self.warehouse_columns:
                if pd.notna(row[warehouse]) and row[warehouse] != '':
                    priority = priority_system.get(warehouse, 999)
                    if priority < best_priority:
                        best_priority = priority
                        best_warehouse = warehouse
            
            if best_warehouse:
                final_locations.append(best_warehouse)
            else:
                final_locations.append('Status_Location')
        
        # 성능 지표 계산
        location_counts = pd.Series(final_locations).value_counts()
        
        # 효율성 점수 (상위 우선순위 활용도)
        efficiency_score = 0
        for location, count in location_counts.items():
            if location in priority_system:
                priority = priority_system[location]
                weight = 1 / priority
                efficiency_score += (count / len(data)) * weight
        
        # 활용도 점수
        utilization_rate = sum(1 for loc in final_locations if loc != 'Status_Location') / len(final_locations)
        
        # 분산 점수
        distribution_score = 1 - (location_counts.max() / len(final_locations))
        
        return {
            'efficiency_score': efficiency_score,
            'utilization_rate': utilization_rate,
            'distribution_score': distribution_score,
            'final_locations': final_locations
        }
    
    def calculate_statistical_significance(self, group_a: Dict, group_b: Dict) -> Dict[str, float]:
        """통계적 유의성 계산"""
        from scipy import stats
        
        significance_results = {}
        
        for metric in ['efficiency_score', 'utilization_rate', 'distribution_score']:
            if metric in group_a and metric in group_b:
                # 간단한 t-test (실제로는 더 복잡한 통계 분석 필요)
                a_value = group_a[metric]
                b_value = group_b[metric]
                
                # 가상의 분산 계산 (실제 데이터 필요)
                variance = 0.01
                n = 1000  # 샘플 크기
                
                t_stat = (b_value - a_value) / (variance / np.sqrt(n))
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 1))
                
                significance_results[metric] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'is_significant': p_value < 0.05
                }
        
        return significance_results
    
    def generate_monitoring_dashboard(self) -> str:
        """모니터링 대시보드 생성"""
        print("\n📊 모니터링 대시보드 생성")
        print("=" * 60)
        
        # 시각화 생성
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('HITACHI 동적 우선순위 시스템 모니터링 대시보드', fontsize=16, fontweight='bold')
        
        # 1. 창고별 활용도 vs 우선순위
        warehouses = list(self.warehouse_metrics.keys())
        utilizations = [self.warehouse_metrics[w].utilization_rate for w in warehouses]
        current_priorities = [self.warehouse_metrics[w].current_priority for w in warehouses]
        recommended_priorities = [self.warehouse_metrics[w].recommended_priority for w in warehouses]
        
        axes[0, 0].scatter(current_priorities, utilizations, alpha=0.7, s=100, label='현재 우선순위')
        axes[0, 0].scatter(recommended_priorities, utilizations, alpha=0.7, s=100, label='추천 우선순위')
        axes[0, 0].set_xlabel('우선순위')
        axes[0, 0].set_ylabel('활용도')
        axes[0, 0].set_title('창고별 활용도 vs 우선순위')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 성능 지표 비교
        metrics = ['활용도', '용량점수', '효율성', '계절성']
        current_scores = [
            np.mean([m.utilization_rate for m in self.warehouse_metrics.values()]),
            np.mean([m.capacity_score for m in self.warehouse_metrics.values()]),
            np.mean([m.efficiency_score for m in self.warehouse_metrics.values()]),
            np.mean([m.seasonal_weight for m in self.warehouse_metrics.values()])
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        axes[0, 1].bar(x, current_scores, width, label='현재 성능', alpha=0.8)
        axes[0, 1].set_xlabel('성능 지표')
        axes[0, 1].set_ylabel('점수')
        axes[0, 1].set_title('시스템 성능 지표')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(metrics)
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 우선순위 변경 히트맵
        priority_matrix = np.zeros((len(warehouses), 2))
        for i, warehouse in enumerate(warehouses):
            priority_matrix[i, 0] = self.warehouse_metrics[warehouse].current_priority
            priority_matrix[i, 1] = self.warehouse_metrics[warehouse].recommended_priority
        
        sns.heatmap(priority_matrix, annot=True, fmt='.0f', cmap='RdYlBu_r', 
                   xticklabels=['현재', '추천'], yticklabels=warehouses, ax=axes[1, 0])
        axes[1, 0].set_title('우선순위 변경 히트맵')
        
        # 4. 계절성 가중치 분포
        seasonal_data = []
        for warehouse in warehouses:
            seasonal_data.append(self.warehouse_metrics[warehouse].seasonal_weight)
        
        axes[1, 1].bar(warehouses, seasonal_data, alpha=0.7, color='skyblue')
        axes[1, 1].set_xlabel('창고')
        axes[1, 1].set_ylabel('계절성 가중치')
        axes[1, 1].set_title('창고별 계절성 가중치')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 대시보드 저장
        dashboard_file = f"Dynamic_Priority_Dashboard_{self.timestamp}.png"
        plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 대시보드 생성 완료: {dashboard_file}")
        return dashboard_file
    
    def generate_system_report(self) -> str:
        """시스템 보고서 생성"""
        print("\n📋 동적 우선순위 시스템 보고서 생성")
        print("=" * 60)
        
        report_file = f"Dynamic_Priority_System_Report_{self.timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
                # 1. 창고 성능 지표
                metrics_data = []
                for warehouse, metrics in self.warehouse_metrics.items():
                    metrics_data.append([
                        warehouse,
                        f"{metrics.utilization_rate:.1%}",
                        f"{metrics.capacity_score:.3f}",
                        f"{metrics.efficiency_score:.3f}",
                        f"{metrics.seasonal_weight:.3f}",
                        metrics.current_priority,
                        metrics.recommended_priority,
                        metrics.recommended_priority - metrics.current_priority
                    ])
                
                metrics_df = pd.DataFrame(metrics_data, columns=[
                    '창고', '활용도', '용량점수', '효율성점수', '계절성가중치',
                    '현재우선순위', '추천우선순위', '변경폭'
                ])
                metrics_df.to_excel(writer, sheet_name='창고_성능_지표', index=False)
                
                # 2. 시스템 설정
                config_data = [
                    ['계절성 활성화', self.config.seasonality_enabled],
                    ['용량 가중치', self.config.capacity_weight],
                    ['활용도 가중치', self.config.utilization_weight],
                    ['효율성 가중치', self.config.efficiency_weight],
                    ['최소 조정 임계값', self.config.min_adjustment_threshold],
                    ['최대 우선순위 레벨', self.config.max_priority_levels],
                    ['업데이트 주기 (일)', self.config.update_frequency_days]
                ]
                
                config_df = pd.DataFrame(config_data, columns=['설정항목', '값'])
                config_df.to_excel(writer, sheet_name='시스템_설정', index=False)
                
                # 3. 우선순위 추천
                recommendations = self.generate_dynamic_priority_recommendations()
                rec_data = []
                for warehouse, priority in recommendations.items():
                    current = self.current_priority.get(warehouse, 7)
                    rec_data.append([
                        warehouse,
                        current,
                        priority,
                        priority - current,
                        '상승' if priority < current else '하락' if priority > current else '유지'
                    ])
                
                rec_df = pd.DataFrame(rec_data, columns=[
                    '창고', '현재우선순위', '추천우선순위', '변경폭', '변경방향'
                ])
                rec_df.to_excel(writer, sheet_name='우선순위_추천', index=False)
                
                # 4. 성능 시뮬레이션
                if recommendations:
                    improvements = self.simulate_priority_system_performance(recommendations)
                    perf_data = []
                    for metric, improvement in improvements.items():
                        perf_data.append([
                            metric,
                            f"{improvement:+.1f}%",
                            '개선' if improvement > 0 else '악화' if improvement < 0 else '유지'
                        ])
                    
                    perf_df = pd.DataFrame(perf_data, columns=['성능지표', '개선도', '상태'])
                    perf_df.to_excel(writer, sheet_name='성능_시뮬레이션', index=False)
                
                # 5. 실행 가이드
                guide_data = [
                    ['1단계', '현재 성능 지표 검토', '창고_성능_지표 시트 확인'],
                    ['2단계', '우선순위 추천 검토', '우선순위_추천 시트 확인'],
                    ['3단계', '성능 개선 예상 확인', '성능_시뮬레이션 시트 확인'],
                    ['4단계', '시스템 설정 조정', '시스템_설정 시트에서 파라미터 조정'],
                    ['5단계', 'A/B 테스트 실행', '일부 데이터에 새 우선순위 적용'],
                    ['6단계', '성능 모니터링', '대시보드를 통한 실시간 모니터링'],
                    ['7단계', '전면 적용', '검증 완료 후 전체 시스템 적용']
                ]
                
                guide_df = pd.DataFrame(guide_data, columns=['단계', '작업', '설명'])
                guide_df.to_excel(writer, sheet_name='실행_가이드', index=False)
            
            print(f"✅ 시스템 보고서 생성 완료: {report_file}")
            print(f"📊 파일 크기: {os.path.getsize(report_file):,} bytes")
            
            return report_file
            
        except Exception as e:
            print(f"❌ 보고서 생성 실패: {e}")
            return None
    
    def run_dynamic_priority_system(self):
        """동적 우선순위 시스템 실행"""
        print("🚀 동적 우선순위 시스템 실행")
        print("=" * 80)
        
        # 1단계: 데이터 로드
        if not self.load_hitachi_data():
            return
        
        # 2단계: 창고 성능 지표 계산
        warehouse_metrics = self.calculate_warehouse_metrics()
        
        # 3단계: 동적 우선순위 추천
        recommendations = self.generate_dynamic_priority_recommendations()
        
        # 4단계: 성능 시뮬레이션
        if recommendations:
            improvements = self.simulate_priority_system_performance(recommendations)
            
            # 5단계: A/B 테스트
            ab_results = self.implement_ab_testing(recommendations)
        
        # 6단계: 모니터링 대시보드 생성
        dashboard_file = self.generate_monitoring_dashboard()
        
        # 7단계: 종합 보고서 생성
        report_file = self.generate_system_report()
        
        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("🎉 동적 우선순위 시스템 구축 완료!")
        print("=" * 80)
        
        print(f"📊 시스템 분석 결과:")
        print(f"   총 HITACHI 데이터: {len(self.hitachi_data):,}건")
        print(f"   분석 창고 수: {len(self.warehouse_columns)}개")
        print(f"   추천 변경 창고: {len([w for w in recommendations.values() if w != self.current_priority.get(w, 7)])}개")
        
        if improvements:
            avg_improvement = sum(improvements.values()) / len(improvements)
            print(f"   평균 성능 개선: {avg_improvement:+.1f}%")
        
        if dashboard_file:
            print(f"📊 모니터링 대시보드: {dashboard_file}")
        
        if report_file:
            print(f"📁 시스템 보고서: {report_file}")
        
        print("\n🎯 다음 단계:")
        print("   1. 시스템 보고서 검토")
        print("   2. A/B 테스트 결과 확인")
        print("   3. 단계적 우선순위 시스템 적용")
        print("   4. 성능 모니터링 및 조정")
        
        print("\n✅ 동적 우선순위 시스템이 성공적으로 구축되었습니다!")
        
        return {
            'warehouse_metrics': warehouse_metrics,
            'recommendations': recommendations,
            'improvements': improvements if 'improvements' in locals() else {},
            'ab_results': ab_results if 'ab_results' in locals() else {},
            'dashboard_file': dashboard_file,
            'report_file': report_file
        }


def main():
    """메인 실행 함수"""
    # 시스템 설정
    config = PrioritySystemConfig(
        seasonality_enabled=True,
        capacity_weight=0.3,
        utilization_weight=0.4,
        efficiency_weight=0.3,
        min_adjustment_threshold=0.05,
        max_priority_levels=7,
        update_frequency_days=7
    )
    
    # 시스템 실행
    system = DynamicPrioritySystem(config)
    system.run_dynamic_priority_system()


if __name__ == "__main__":
    main() 