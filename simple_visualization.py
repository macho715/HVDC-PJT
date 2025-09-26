#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACHO-GPT v3.4-mini Simple Data Visualization Dashboard
HVDC Project - Samsung C&T Logistics
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import json

def create_simple_dashboard():
    """간단한 대시보드 생성"""
    print("🚀 MACHO-GPT v3.4-mini Data Visualization Dashboard")
    print("=" * 60)
    
    # 샘플 데이터 생성
    data = {
        '월': ['1월', '2월', '3월', '4월', '5월', '6월'],
        '컨테이너_처리량': [850, 920, 780, 950, 880, 810],
        '송장_처리량': [45, 52, 38, 58, 42, 47],
        '비용_절약_AED': [12000, 13500, 9800, 15600, 11200, 13626],
        '신뢰도_퍼센트': [92.5, 94.1, 91.8, 95.2, 93.7, 93.86]
    }
    
    df = pd.DataFrame(data)
    
    # 시각화 생성
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('MACHO-GPT v3.4-mini HVDC Project Dashboard', fontsize=16, fontweight='bold')
    
    # 1. 컨테이너 처리량 트렌드
    axes[0, 0].plot(df['월'], df['컨테이너_처리량'], marker='o', linewidth=3, color='#667eea')
    axes[0, 0].set_title('월별 컨테이너 처리량', fontweight='bold')
    axes[0, 0].set_ylabel('컨테이너 수')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 송장 처리량 바 차트
    bars = axes[0, 1].bar(df['월'], df['송장_처리량'], color='#764ba2', alpha=0.8)
    axes[0, 1].set_title('월별 송장 처리량', fontweight='bold')
    axes[0, 1].set_ylabel('송장 수')
    for bar in bars:
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{int(height)}', ha='center', va='bottom')
    
    # 3. 비용 절약 파이 차트
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']
    axes[1, 0].pie(df['비용_절약_AED'], labels=df['월'], autopct='%1.1f%%', colors=colors)
    axes[1, 0].set_title('월별 비용 절약 분포', fontweight='bold')
    
    # 4. 신뢰도 라인 차트
    axes[1, 1].plot(df['월'], df['신뢰도_퍼센트'], marker='s', linewidth=3, color='#27ae60')
    axes[1, 1].set_title('시스템 신뢰도 트렌드', fontweight='bold')
    axes[1, 1].set_ylabel('신뢰도 (%)')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_ylim(90, 96)
    
    plt.tight_layout()
    
    # 파일 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"macho_dashboard_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ 대시보드 저장됨: {filename}")
    
    # 통계 요약
    print("\n📊 통계 요약:")
    print(f"   평균 컨테이너 처리량: {df['컨테이너_처리량'].mean():.0f}개")
    print(f"   평균 송장 처리량: {df['송장_처리량'].mean():.1f}건")
    print(f"   총 비용 절약: {df['비용_절약_AED'].sum():,} AED")
    print(f"   평균 신뢰도: {df['신뢰도_퍼센트'].mean():.1f}%")
    
    return filename

if __name__ == "__main__":
    try:
        filename = create_simple_dashboard()
        print(f"\n🎉 MACHO-GPT 데이터 시각화 완료!")
        print(f"📁 파일 위치: {filename}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}") 