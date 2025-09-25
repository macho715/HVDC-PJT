#!/usr/bin/env python3
"""
HVDC 창고 이동 네트워크 그래프 (단순 버전)
네트워크 그래프만 표시
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import warnings
import os
warnings.filterwarnings('ignore')

# 설정
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 12

print("🌐 HVDC 창고 이동 네트워크 그래프")
print("=" * 50)

# 파일 로드
file_path = 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
try:
    df = pd.read_excel(file_path, sheet_name='Case List', engine='openpyxl')
    print(f"✅ 데이터 로드: {len(df)}건")
except:
    print("❌ 파일 로드 실패")
    exit()

# 위치 컬럼
location_columns = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                   'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting', 
                   'MIR', 'SHU', 'DAS', 'AGI']

existing_columns = [col for col in location_columns if col in df.columns]
print(f"📍 위치 컬럼: {len(existing_columns)}개")

# 날짜 변환
for col in existing_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

def identify_movements(row):
    """이동 패턴 식별"""
    valid_locations = {col: row[col] for col in existing_columns if pd.notna(row[col])}
    
    if len(valid_locations) < 2:
        return []
    
    sorted_locations = sorted(valid_locations.items(), key=lambda x: x[1])
    movements = []
    
    for i in range(len(sorted_locations) - 1):
        from_loc = sorted_locations[i][0]
        to_loc = sorted_locations[i + 1][0]
        if from_loc != to_loc:
            movements.append((from_loc, to_loc))
    
    return movements

# 이동 분석
print("🔄 이동 패턴 분석...")
all_movements = []
for _, row in df.iterrows():
    movements = identify_movements(row)
    all_movements.extend(movements)

print(f"📈 총 이동: {len(all_movements)}건")

# 이동 횟수 계산
movement_counts = {}
for movement in all_movements:
    movement_counts[movement] = movement_counts.get(movement, 0) + 1

# DataFrame 생성
movement_df = pd.DataFrame([(from_loc, to_loc, count) 
                           for (from_loc, to_loc), count in movement_counts.items()],
                          columns=['From', 'To', 'Count'])
movement_df = movement_df.sort_values('Count', ascending=False)

print(f"📊 고유 경로: {len(movement_df)}개")

# 상위 15개 경로로 네트워크 생성
top_movements = movement_df.head(15)
print("\n🚛 상위 15개 이동 경로:")
for i, (_, row) in enumerate(top_movements.iterrows(), 1):
    print(f"   {i:2d}. {row['From']} → {row['To']}: {row['Count']}회")

# 네트워크 그래프 생성
G = nx.DiGraph()

for _, row in top_movements.iterrows():
    from_loc = row['From']
    to_loc = row['To']
    count = row['Count']
    G.add_edge(from_loc, to_loc, weight=count)

print(f"\n🌐 네트워크: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지")

# 그래프 그리기
plt.figure(figsize=(16, 12))

# 레이아웃
pos = nx.spring_layout(G, k=1, seed=42, iterations=50)

# 엣지 가중치
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
max_weight = max(edge_weights) if edge_weights else 1
min_weight = min(edge_weights) if edge_weights else 1

# 엣지 두께 정규화
if max_weight > min_weight:
    edge_widths = [2 + 10 * (weight - min_weight) / (max_weight - min_weight) for weight in edge_weights]
else:
    edge_widths = [6] * len(edge_weights)

# 노드 크기 (degree 기반)
node_degrees = dict(G.degree())
node_sizes = [800 + 500 * node_degrees[node] for node in G.nodes()]
node_colors = [node_degrees[node] for node in G.nodes()]

# 노드 그리기
nodes = nx.draw_networkx_nodes(G, pos, 
                              node_size=node_sizes,
                              node_color=node_colors,
                              cmap=plt.cm.Reds,
                              alpha=0.8)

# 엣지 그리기
edges = nx.draw_networkx_edges(G, pos,
                              width=edge_widths,
                              edge_color=edge_weights,
                              edge_cmap=plt.cm.Blues,
                              arrowsize=25,
                              connectionstyle='arc3,rad=0.1',
                              alpha=0.7)

# 라벨 그리기
labels = {}
for node in G.nodes():
    # 긴 이름 줄이기
    short_name = node.replace('DSV ', '').replace('Warehouse', 'WH').replace('Storage', 'ST')
    if len(short_name) > 10:
        short_name = short_name[:8] + '..'
    labels[node] = short_name

nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')

# 주요 엣지에만 라벨 표시
top_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:8]
edge_labels = {(u, v): str(data['weight']) for u, v, data in top_edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=9, alpha=0.8)

plt.title('HVDC 창고 이동 네트워크\n(상위 15개 경로, 노드 크기=연결도, 엣지 두께=이동 횟수)', 
          fontsize=16, fontweight='bold', pad=20)

plt.axis('off')
plt.tight_layout()

# 컬러바 추가
if edges is not None:
    cbar = plt.colorbar(edges, shrink=0.8, aspect=20)
    cbar.set_label('이동 횟수', rotation=270, labelpad=20)

plt.savefig('hvdc_network_simple.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"\n💾 저장 완료: hvdc_network_simple.png")
print(f"🔧 추천 명령어:")
print("/flow-optimization [경로 최적화]")
print("/bottleneck-analysis [병목 분석]") 