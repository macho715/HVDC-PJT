#!/usr/bin/env python3
"""
HVDC 창고 이동 네트워크 그래프 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (15, 10)

print("🌐 HVDC 창고 이동 네트워크 분석")
print("=" * 50)

# 데이터 로드
try:
    df = pd.read_excel('data/HVDC WAREHOUSE_HITACHI(HE).xlsx', engine='openpyxl')
    print(f"✅ 데이터 로드 성공: {len(df)}건")
except Exception as e:
    print(f"❌ 데이터 로드 실패: {e}")
    exit(1)

# 위치 관련 컬럼 찾기
location_columns = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                   'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting']

existing_cols = [col for col in location_columns if col in df.columns]
print(f"📍 발견된 위치 컬럼: {existing_cols}")

if not existing_cols:
    print("❌ 위치 컬럼을 찾을 수 없습니다.")
    exit(1)

# 날짜 형식 변환
print("📅 날짜 변환 중...")
for col in existing_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 간단한 이동 패턴 생성 (샘플 데이터)
print("🔄 이동 패턴 생성...")

# 실제 데이터에서 이동 패턴 추출
movements = []
for _, row in df.iterrows():
    locations_with_dates = {}
    for col in existing_cols:
        if pd.notna(row[col]):
            locations_with_dates[col] = row[col]
    
    if len(locations_with_dates) >= 2:
        sorted_locs = sorted(locations_with_dates.items(), key=lambda x: x[1])
        for i in range(len(sorted_locs) - 1):
            from_loc = sorted_locs[i][0]
            to_loc = sorted_locs[i + 1][0]
            if from_loc != to_loc:
                movements.append((from_loc, to_loc))

print(f"📈 총 이동 건수: {len(movements)}")

if not movements:
    print("❌ 이동 데이터가 없습니다. 샘플 데이터를 생성합니다.")
    # 샘플 이동 데이터 생성
    sample_movements = [
        ('DHL Warehouse', 'DSV Indoor', 45),
        ('DSV Indoor', 'DSV Outdoor', 38),
        ('DSV Outdoor', 'MOSB', 32),
        ('DSV Al Markaz', 'DSV Indoor', 28),
        ('DSV Indoor', 'Shifting', 25),
        ('AAA  Storage', 'DSV Outdoor', 22),
        ('DSV MZP', 'DSV Indoor', 20),
        ('Hauler Indoor', 'DSV Outdoor', 18),
        ('MOSB', 'Shifting', 15),
        ('DSV Outdoor', 'AAA  Storage', 12)
    ]
    
    movement_df = pd.DataFrame(sample_movements, columns=['From', 'To', 'Count'])
else:
    # 이동 횟수 계산
    from collections import Counter
    movement_counts = Counter(movements)
    
    movement_df = pd.DataFrame([
        (from_loc, to_loc, count) 
        for (from_loc, to_loc), count in movement_counts.items()
    ], columns=['From', 'To', 'Count'])

movement_df = movement_df.sort_values('Count', ascending=False)
print(f"📊 고유 이동 경로: {len(movement_df)}개")

# 상위 이동 경로 출력
print("\n🚛 상위 이동 경로:")
for i, (_, row) in enumerate(movement_df.head(10).iterrows(), 1):
    print(f"   {i:2d}. {row['From']:<15} → {row['To']:<15}: {row['Count']:>3}회")

# 네트워크 그래프 생성
print("\n🌐 네트워크 그래프 생성...")
G = nx.DiGraph()

# 상위 12개 경로로 네트워크 구성
top_movements = movement_df.head(12)
for _, row in top_movements.iterrows():
    G.add_edge(row['From'], row['To'], weight=row['Count'])

print(f"   노드: {G.number_of_nodes()}개")
print(f"   엣지: {G.number_of_edges()}개")

# 그래프 시각화
plt.figure(figsize=(16, 12))

# 레이아웃 설정
pos = nx.spring_layout(G, k=2, seed=42, iterations=100)

# 엣지 설정
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
max_weight = max(edge_weights) if edge_weights else 1
min_weight = min(edge_weights) if edge_weights else 1

# 엣지 두께와 색상
edge_widths = []
for weight in edge_weights:
    if max_weight > min_weight:
        width = 1 + 8 * (weight - min_weight) / (max_weight - min_weight)
    else:
        width = 5
    edge_widths.append(width)

# 노드 설정
node_degrees = dict(G.degree())
node_sizes = [1000 + 800 * node_degrees[node] for node in G.nodes()]

# 그래프 그리기
print("🎨 그래프 렌더링...")

# 노드 그리기
nodes = nx.draw_networkx_nodes(G, pos,
                              node_size=node_sizes,
                              node_color='lightcoral',
                              alpha=0.8,
                              edgecolors='black',
                              linewidths=2)

# 엣지 그리기
edges = nx.draw_networkx_edges(G, pos,
                              width=edge_widths,
                              edge_color='steelblue',
                              arrowsize=25,
                              arrowstyle='->',
                              connectionstyle='arc3,rad=0.1',
                              alpha=0.7)

# 라벨 그리기
labels = {}
for node in G.nodes():
    # 라벨 단순화
    label = node.replace('DSV ', '').replace('Warehouse', 'WH')
    if len(label) > 8:
        label = label[:6] + '..'
    labels[node] = label

nx.draw_networkx_labels(G, pos, labels, 
                       font_size=11, 
                       font_weight='bold',
                       font_color='white')

# 엣지 라벨 (상위 6개만)
top_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:6]
edge_labels = {(u, v): str(data['weight']) for u, v, data in top_edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                            font_size=10, 
                            font_color='red',
                            bbox=dict(boxstyle='round,pad=0.2', 
                                     facecolor='white', 
                                     alpha=0.8))

# 제목 및 설정
plt.title('HVDC Warehouse Movement Network\n'
          f'Top {len(top_movements)} Routes | Node Size = Connection Degree | Edge Width = Movement Count',
          fontsize=16, fontweight='bold', pad=20)

plt.axis('off')
plt.tight_layout()

# 범례 추가
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
               markersize=15, label='Warehouse (size = connections)'),
    plt.Line2D([0], [0], color='steelblue', linewidth=5, 
               label='Movement Path (width = frequency)')
]
plt.legend(handles=legend_elements, loc='upper right', fontsize=12)

# 저장 및 표시
plt.savefig('hvdc_warehouse_network.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f"💾 그래프 저장: hvdc_warehouse_network.png")

plt.show()

# 통계 출력
print(f"\n📊 네트워크 분석 결과:")
print(f"   총 노드 수: {G.number_of_nodes()}")
print(f"   총 엣지 수: {G.number_of_edges()}")
if G.number_of_nodes() > 0:
    avg_degree = sum(node_degrees.values()) / len(node_degrees)
    print(f"   평균 연결도: {avg_degree:.2f}")

# 중심성 분석
centrality = nx.degree_centrality(G)
if centrality:
    most_central = max(centrality.items(), key=lambda x: x[1])
    print(f"   가장 중요한 허브: {most_central[0]} (중심성: {most_central[1]:.3f})")

print(f"\n✅ 네트워크 그래프 생성 완료!") 