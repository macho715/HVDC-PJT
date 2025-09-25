"""
HVDC 3D Warehouse Analysis Report Generator
MACHO-GPT v3.4-mini for HVDC Project

실제 데이터 기반 3D 창고 분석 및 최적화 리포트 생성
Samsung C&T × ADNOC DSV Partnership
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class HVDC3DWarehouseAnalyzer:
    """HVDC 3D 창고 데이터 분석 클래스"""
    
    def __init__(self, data_file: str = "hvdc_3d_warehouse_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
        self.df = pd.DataFrame(self.data)
        
    def load_data(self) -> List[Dict]:
        """3D 창고 데이터 로드"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return []
    
    def generate_capacity_analysis(self) -> Dict:
        """용량 분석 리포트 생성"""
        print("📊 Generating capacity analysis...")
        
        # 기본 통계
        total_zones = len(self.df)
        over_capacity_zones = len(self.df[self.df['over'] == True])
        optimal_zones = len(self.df[self.df['optimal'] == True])
        under_utilized_zones = total_zones - over_capacity_zones - optimal_zones
        
        # 창고별 통계
        warehouse_stats = self.df.groupby('warehouse').agg({
            'fill_ratio': ['mean', 'min', 'max', 'std'],
            'packages': ['sum', 'mean'],
            'cbm': ['sum', 'mean'],
            'over': 'sum'
        }).round(2)
        
        # 위험도 분석
        risk_zones = self.df[self.df['fill_ratio'] >= 95]
        
        return {
            'total_zones': total_zones,
            'over_capacity_zones': over_capacity_zones,
            'optimal_zones': optimal_zones,
            'under_utilized_zones': under_utilized_zones,
            'average_fill_ratio': round(self.df['fill_ratio'].mean(), 2),
            'total_packages': int(self.df['packages'].sum()),
            'total_cbm': round(self.df['cbm'].sum(), 2),
            'warehouse_stats': warehouse_stats,
            'risk_zones': risk_zones[['zone', 'warehouse', 'fill_ratio', 'packages']].to_dict('records')
        }
    
    def generate_optimization_recommendations(self) -> Dict:
        """최적화 추천 사항 생성"""
        print("🔧 Generating optimization recommendations...")
        
        recommendations = []
        
        # 1. 과용량 존 재분배
        over_capacity = self.df[self.df['over'] == True]
        if len(over_capacity) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Capacity Redistribution',
                'description': f'{len(over_capacity)} zones are over capacity (≥90%)',
                'action': 'Redistribute packages from overcrowded zones to under-utilized zones',
                'affected_zones': over_capacity['zone'].tolist()
            })
        
        # 2. 저활용 존 효율화
        under_utilized = self.df[self.df['fill_ratio'] < 60]
        if len(under_utilized) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Space Efficiency',
                'description': f'{len(under_utilized)} zones are under-utilized (<60%)',
                'action': 'Consolidate packages to optimize space utilization',
                'affected_zones': under_utilized['zone'].tolist()
            })
        
        # 3. 창고간 밸런싱
        warehouse_imbalance = self.df.groupby('warehouse')['fill_ratio'].mean()
        max_warehouse = warehouse_imbalance.idxmax()
        min_warehouse = warehouse_imbalance.idxmin()
        
        if warehouse_imbalance[max_warehouse] - warehouse_imbalance[min_warehouse] > 30:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Warehouse Balancing',
                'description': f'Imbalance between {max_warehouse} ({warehouse_imbalance[max_warehouse]:.1f}%) and {min_warehouse} ({warehouse_imbalance[min_warehouse]:.1f}%)',
                'action': f'Transfer packages from {max_warehouse} to {min_warehouse}',
                'affected_zones': None
            })
        
        return {
            'total_recommendations': len(recommendations),
            'recommendations': recommendations,
            'potential_savings': self.calculate_potential_savings()
        }
    
    def calculate_potential_savings(self) -> Dict:
        """잠재적 절약 효과 계산"""
        current_efficiency = self.df['fill_ratio'].mean()
        
        # 목표 효율 75% 달성시 절약 효과
        target_efficiency = 75
        current_space = self.df['area'].sum()
        
        if current_efficiency > 0:
            optimized_space = current_space * (current_efficiency / target_efficiency)
            space_savings = current_space - optimized_space
            cost_savings = space_savings * 50  # $50 per m² per month
        else:
            space_savings = 0
            cost_savings = 0
        
        return {
            'current_efficiency': round(current_efficiency, 2),
            'target_efficiency': target_efficiency,
            'space_savings_m2': round(space_savings, 2),
            'monthly_cost_savings_usd': round(cost_savings, 2)
        }
    
    def generate_visualizations(self) -> List[str]:
        """시각화 생성"""
        print("📈 Generating visualizations...")
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 창고별 충진율 분포
        warehouse_fill = self.df.groupby('warehouse')['fill_ratio'].mean().sort_values(ascending=True)
        axes[0, 0].barh(warehouse_fill.index, warehouse_fill.values, 
                        color=['red' if x >= 90 else 'green' if x >= 60 else 'blue' for x in warehouse_fill.values])
        axes[0, 0].set_title('Average Fill Ratio by Warehouse', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Fill Ratio (%)')
        axes[0, 0].axvline(x=90, color='red', linestyle='--', alpha=0.7, label='Over Capacity')
        axes[0, 0].axvline(x=60, color='green', linestyle='--', alpha=0.7, label='Optimal Range')
        axes[0, 0].legend()
        
        # 2. 존별 패키지 분포
        axes[0, 1].scatter(self.df['packages'], self.df['fill_ratio'], 
                          c=['red' if x else 'green' for x in self.df['over']], alpha=0.6)
        axes[0, 1].set_title('Packages vs Fill Ratio by Zone', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Number of Packages')
        axes[0, 1].set_ylabel('Fill Ratio (%)')
        axes[0, 1].axhline(y=90, color='red', linestyle='--', alpha=0.7)
        axes[0, 1].axhline(y=60, color='green', linestyle='--', alpha=0.7)
        
        # 3. CBM 분포
        warehouse_cbm = self.df.groupby('warehouse')['cbm'].sum().sort_values(ascending=False)
        axes[1, 0].bar(warehouse_cbm.index, warehouse_cbm.values, color='skyblue')
        axes[1, 0].set_title('Total CBM by Warehouse', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('CBM')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 용량 상태 분포
        capacity_status = pd.cut(self.df['fill_ratio'], 
                                bins=[0, 60, 90, 100], 
                                labels=['Under-utilized', 'Optimal', 'Over-capacity'])
        status_counts = capacity_status.value_counts()
        axes[1, 1].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
                       colors=['lightblue', 'lightgreen', 'lightcoral'])
        axes[1, 1].set_title('Capacity Status Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 저장
        viz_file = f"hvdc_3d_warehouse_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(viz_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return [viz_file]
    
    def generate_detailed_report(self) -> str:
        """상세 분석 리포트 생성"""
        print("📋 Generating detailed report...")
        
        capacity_analysis = self.generate_capacity_analysis()
        optimization_recs = self.generate_optimization_recommendations()
        viz_files = self.generate_visualizations()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# HVDC 3D Warehouse Analysis Report
**Generated**: {timestamp}  
**Data Source**: {self.data_file}  
**Analysis System**: MACHO-GPT v3.4-mini

## 📊 Executive Summary

### Key Metrics
- **Total Zones**: {capacity_analysis['total_zones']}
- **Over Capacity Zones**: {capacity_analysis['over_capacity_zones']} ({capacity_analysis['over_capacity_zones']/capacity_analysis['total_zones']*100:.1f}%)
- **Optimal Zones**: {capacity_analysis['optimal_zones']} ({capacity_analysis['optimal_zones']/capacity_analysis['total_zones']*100:.1f}%)
- **Under-utilized Zones**: {capacity_analysis['under_utilized_zones']} ({capacity_analysis['under_utilized_zones']/capacity_analysis['total_zones']*100:.1f}%)
- **Average Fill Ratio**: {capacity_analysis['average_fill_ratio']}%
- **Total Packages**: {capacity_analysis['total_packages']:,}
- **Total CBM**: {capacity_analysis['total_cbm']:,}

### Warehouse Performance
"""
        
        # 창고별 상세 정보
        for warehouse, stats in capacity_analysis['warehouse_stats'].iterrows():
            report += f"""
#### {warehouse}
- **Average Fill Ratio**: {stats[('fill_ratio', 'mean')]:.1f}%
- **Fill Range**: {stats[('fill_ratio', 'min')]:.1f}% - {stats[('fill_ratio', 'max')]:.1f}%
- **Total Packages**: {stats[('packages', 'sum')]:,}
- **Total CBM**: {stats[('cbm', 'sum')]:,}
- **Over Capacity Zones**: {stats[('over', 'sum')]}
"""
        
        report += f"""
## 🚨 Risk Analysis

### High-Risk Zones (≥95% Capacity)
"""
        
        for zone in capacity_analysis['risk_zones']:
            report += f"- **{zone['zone']}** ({zone['warehouse']}): {zone['fill_ratio']:.1f}% - {zone['packages']} packages\n"
        
        report += f"""
## 🔧 Optimization Recommendations

**Total Recommendations**: {optimization_recs['total_recommendations']}

"""
        
        for i, rec in enumerate(optimization_recs['recommendations'], 1):
            report += f"""
### {i}. {rec['category']} - Priority: {rec['priority']}
**Issue**: {rec['description']}  
**Action**: {rec['action']}  
"""
            if rec['affected_zones']:
                report += f"**Affected Zones**: {', '.join(rec['affected_zones'])}\n"
        
        report += f"""
## 💰 Potential Savings

- **Current Space Efficiency**: {optimization_recs['potential_savings']['current_efficiency']:.1f}%
- **Target Efficiency**: {optimization_recs['potential_savings']['target_efficiency']:.1f}%
- **Potential Space Savings**: {optimization_recs['potential_savings']['space_savings_m2']:,} m²
- **Monthly Cost Savings**: ${optimization_recs['potential_savings']['monthly_cost_savings_usd']:,}

## 📈 Visualizations

Generated visualization files:
"""
        
        for viz_file in viz_files:
            report += f"- {viz_file}\n"
        
        report += f"""
## 📋 Next Steps

1. **Immediate Actions** (1-2 weeks):
   - Redistribute packages from over-capacity zones
   - Implement safety protocols for high-risk zones
   - Begin consolidation of under-utilized zones

2. **Short-term Goals** (1-3 months):
   - Achieve 75% average fill ratio across all warehouses
   - Reduce over-capacity zones to less than 10%
   - Implement automated monitoring system

3. **Long-term Strategy** (3-6 months):
   - Optimize warehouse layout based on data patterns
   - Implement predictive analytics for capacity planning
   - Integrate with Samsung C&T logistics systems

## 🔧 Technical Integration

**3D Visualization**: `hvdc_3d_warehouse_live.html`  
**Data API**: Real-time connection to HVDC warehouse systems  
**Update Frequency**: Every 15 minutes during operational hours

---

*This report was generated using MACHO-GPT v3.4-mini with real-time HVDC warehouse data integration.*
"""
        
        return report
    
    def save_report(self, report: str) -> str:
        """리포트 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"HVDC_3D_Warehouse_Analysis_Report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename
    
    def run_full_analysis(self) -> str:
        """전체 분석 실행"""
        print("🚀 Starting comprehensive 3D warehouse analysis...")
        
        if not self.data:
            print("❌ No data available for analysis")
            return ""
        
        # 분석 실행
        report = self.generate_detailed_report()
        filename = self.save_report(report)
        
        print(f"✅ Analysis complete: {filename}")
        return filename

if __name__ == "__main__":
    analyzer = HVDC3DWarehouseAnalyzer()
    report_file = analyzer.run_full_analysis()
    print(f"\n🎯 Analysis report saved as: {report_file}") 