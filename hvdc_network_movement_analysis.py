# Create a network graph visualization with the top movements
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# Set up matplotlib for better visualization
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

print("🌐 HVDC 창고 이동 네트워크 분석 시스템")
print("=" * 60)
print("📅 분석 시작:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 대체 파일 경로 목록
alternative_paths = [
    'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
    'HVDC WAREHOUSE_HITACHI(HE).xlsx',
    'data_cleaned/HVDC_WAREHOUSE_HITACHI_CLEANED_20250709_201121.xlsx',
    'hvdc_macho_gpt/HVDC STATUS/data/HVDC-STATUS.xlsx',
    'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
    'hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
]

df = None
file_path = None

# 파일 로드 시도
for path in alternative_paths:
    if os.path.exists(path):
        print(f"📁 데이터 로드 시도: {path}")
        try:
            # 다양한 엔진으로 시도
            try:
                df = pd.read_excel(path, sheet_name='Case List', engine='calamine')
                print(f"✅ 데이터 로드 성공 (calamine): {path} ({len(df)}건)")
                file_path = path
                break
            except:
                try:
                    df = pd.read_excel(path, sheet_name='Case List', engine='openpyxl')
                    print(f"✅ 데이터 로드 성공 (openpyxl): {path} ({len(df)}건)")
                    file_path = path
                    break
                except:
                    # 시트 이름 없이 시도
                    df = pd.read_excel(path, engine='calamine')
                    print(f"✅ 데이터 로드 성공 (기본 시트): {path} ({len(df)}건)")
                    file_path = path
                    break
        except Exception as e:
            print(f"❌ 로드 실패: {path} - {str(e)}")
            continue

if df is None:
    print("❌ 사용 가능한 데이터 파일을 찾을 수 없습니다.")
    print("다음 위치에 HVDC WAREHOUSE_HITACHI(HE).xlsx 파일이 있는지 확인하세요:")
    for path in alternative_paths:
        print(f"   - {path}")
    exit()

# 데이터 기본 정보 확인
print(f"\n📊 데이터 정보:")
print(f"   - 파일: {file_path}")
print(f"   - 행 수: {len(df)}")
print(f"   - 열 수: {len(df.columns)}")
print(f"   - 컬럼 목록: {list(df.columns)}")

# Create a list of all location columns
location_columns = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                   'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting', 
                   'MIR', 'SHU', 'DAS', 'AGI']

# Check which columns exist in the dataset
existing_columns = [col for col in location_columns if col in df.columns]
print(f"\n📊 사용 가능한 위치 컬럼: {len(existing_columns)}개")
if existing_columns:
    print(f"   {existing_columns}")
else:
    print("   위치 컬럼을 찾을 수 없습니다. 대체 컬럼을 찾는 중...")
    # 날짜나 위치 관련 컬럼을 자동으로 찾기
    date_like_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'warehouse', 'storage', 'location', 'dsv', 'dhl', 'aaa'])]
    if date_like_columns:
        existing_columns = date_like_columns
        print(f"   발견된 관련 컬럼: {existing_columns}")
    else:
        print("   관련 컬럼을 찾을 수 없습니다.")
        exit()

# Convert date columns to datetime format
for col in existing_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Function to identify movements between locations
def identify_movements(row):
    # Filter only the location columns that have dates
    valid_locations = {col: row[col] for col in existing_columns if pd.notna(row[col])}
    
    if len(valid_locations) < 2:
        return []
    
    # Sort locations by date
    sorted_locations = sorted(valid_locations.items(), key=lambda x: x[1])
    
    # Create pairs of consecutive locations (from -> to)
    movements = []
    for i in range(len(sorted_locations) - 1):
        from_loc = sorted_locations[i][0]
        to_loc = sorted_locations[i + 1][0]
        if from_loc != to_loc:  # 같은 위치 이동 제외
            movements.append((from_loc, to_loc))
    
    return movements

print("\n🔄 이동 패턴 분석 중...")

# Apply the function to each row and collect all movements
all_movements = []
for _, row in df.iterrows():
    movements = identify_movements(row)
    all_movements.extend(movements)

print(f"📈 총 이동 건수: {len(all_movements)}건")

if len(all_movements) == 0:
    print("❌ 이동 패턴을 찾을 수 없습니다.")
    exit()

# Count the frequency of each movement
movement_counts = {}
for movement in all_movements:
    if movement in movement_counts:
        movement_counts[movement] += 1
    else:
        movement_counts[movement] = 1

# Convert to DataFrame for easier analysis
movement_df = pd.DataFrame([(from_loc, to_loc, count) 
                           for (from_loc, to_loc), count in movement_counts.items()],
                          columns=['From_Location', 'To_Location', 'Count'])

# Sort by count in descending order
movement_df = movement_df.sort_values('Count', ascending=False)

print(f"\n📊 고유 이동 경로: {len(movement_df)}개")
print("상위 10개 이동 경로:")
if len(movement_df) > 0:
    print(movement_df.head(10).to_string(index=False))
else:
    print("이동 경로가 없습니다.")
    exit()

# Create a network graph of the top movements
top_n = min(20, len(movement_df))  # Use top 20 or all if less than 20
top_movements = movement_df.head(top_n)

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges with weights
for _, row in top_movements.iterrows():
    from_loc = row['From_Location']
    to_loc = row['To_Location']
    count = row['Count']
    
    # Add nodes if they don't exist
    if from_loc not in G.nodes():
        G.add_node(from_loc)
    if to_loc not in G.nodes():
        G.add_node(to_loc)
    
    # Add edge with weight
    G.add_edge(from_loc, to_loc, weight=count)

print(f"\n🌐 네트워크 그래프 생성:")
print(f"   노드 수: {G.number_of_nodes()}개")
print(f"   엣지 수: {G.number_of_edges()}개")

# Set up the figure with multiple subplots
fig = plt.figure(figsize=(20, 12))

# Main network graph
ax1 = plt.subplot(2, 2, (1, 2))

# Create a layout for the nodes
pos = nx.spring_layout(G, k=0.5, seed=42, iterations=50)

# Get edge weights for line thickness and color
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
if len(edge_weights) > 0:
    max_weight = max(edge_weights)
    min_weight = min(edge_weights)
    
    # Normalize edge weights for thickness
    if max_weight > min_weight:
        normalized_weights = [2 + 8 * (weight - min_weight) / (max_weight - min_weight) for weight in edge_weights]
    else:
        normalized_weights = [5] * len(edge_weights)
    
    # Create node colors based on degree (centrality)
    node_degrees = dict(G.degree())
    node_colors = [node_degrees[node] for node in G.nodes()]
    
    # Draw the nodes with varying sizes based on degree
    node_sizes = [500 + 300 * node_degrees[node] for node in G.nodes()]
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                                   node_color=node_colors, cmap=plt.cm.Reds, 
                                   alpha=0.8, ax=ax1)
    
    # Draw the edges with varying thickness based on weight
    edge_colors = edge_weights
    edges = nx.draw_networkx_edges(G, pos, width=normalized_weights, 
                                  edge_color=edge_colors, edge_cmap=plt.cm.Blues,
                                  arrowsize=20, connectionstyle='arc3,rad=0.1', 
                                  alpha=0.7, ax=ax1)
    
    # Draw the labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax1)
    
    # Add edge labels (counts) for top edges only
    top_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:10]
    edge_labels = {(u, v): data['weight'] for u, v, data in top_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax1)

ax1.set_title(f'HVDC 창고 이동 네트워크 (상위 {top_n}개 경로)', fontsize=14, fontweight='bold')
ax1.axis('off')

# Movement frequency bar chart
ax2 = plt.subplot(2, 2, 3)
top_10_movements = movement_df.head(10)
movement_labels = [f"{row['From_Location']} → {row['To_Location']}" 
                   for _, row in top_10_movements.iterrows()]
# 라벨 길이 제한
movement_labels = [label if len(label) <= 30 else label[:27] + "..." for label in movement_labels]

ax2.barh(range(len(movement_labels)), top_10_movements['Count'], 
         color=plt.cm.Blues(np.linspace(0.3, 0.8, len(movement_labels))))
ax2.set_yticks(range(len(movement_labels)))
ax2.set_yticklabels(movement_labels, fontsize=9)
ax2.set_xlabel('이동 횟수')
ax2.set_title('상위 10개 이동 경로 빈도', fontsize=12, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# Node centrality analysis
ax3 = plt.subplot(2, 2, 4)
centrality = nx.degree_centrality(G)
centrality_df = pd.DataFrame(list(centrality.items()), columns=['Location', 'Centrality'])
centrality_df = centrality_df.sort_values('Centrality', ascending=True)

ax3.barh(range(len(centrality_df)), centrality_df['Centrality'], 
         color=plt.cm.Reds(np.linspace(0.3, 0.8, len(centrality_df))))
ax3.set_yticks(range(len(centrality_df)))
ax3.set_yticklabels(centrality_df['Location'], fontsize=9)
ax3.set_xlabel('중심성 점수')
ax3.set_title('창고별 중심성 분석', fontsize=12, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('hvdc_warehouse_movement_network.png', dpi=300, bbox_inches='tight')
plt.show()

# Additional analysis and statistics
print("\n📊 네트워크 분석 결과:")
print("=" * 50)

# Network statistics
print(f"🔍 네트워크 통계:")
print(f"   - 총 노드 수: {G.number_of_nodes()}")
print(f"   - 총 엣지 수: {G.number_of_edges()}")
if G.number_of_nodes() > 0:
    print(f"   - 평균 degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")

# Most central nodes
if len(centrality) > 0:
    print(f"\n🎯 가장 중요한 창고 (중심성 기준):")
    centrality_sorted = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    for i, (location, cent) in enumerate(centrality_sorted[:5], 1):
        print(f"   {i}. {location}: {cent:.3f}")

# Busiest routes
print(f"\n🚛 가장 활발한 이동 경로:")
for i, (_, row) in enumerate(movement_df.head(5).iterrows(), 1):
    print(f"   {i}. {row['From_Location']} → {row['To_Location']}: {row['Count']}회")

# Save detailed analysis to Excel
analysis_results = {
    'Movement_Analysis': movement_df,
    'Node_Centrality': centrality_df,
    'Network_Statistics': pd.DataFrame([
        ['Total Nodes', G.number_of_nodes()],
        ['Total Edges', G.number_of_edges()],
        ['Average Degree', sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0],
        ['Most Central Node', centrality_sorted[0][0] if centrality_sorted else 'N/A'],
        ['Busiest Route', f"{movement_df.iloc[0]['From_Location']} → {movement_df.iloc[0]['To_Location']}" if len(movement_df) > 0 else 'N/A']
    ], columns=['Metric', 'Value'])
}

with pd.ExcelWriter('HVDC_Network_Movement_Analysis.xlsx', engine='openpyxl') as writer:
    for sheet_name, df_data in analysis_results.items():
        df_data.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\n💾 분석 결과 저장 완료:")
print(f"   - 이미지: hvdc_warehouse_movement_network.png")
print(f"   - 데이터: HVDC_Network_Movement_Analysis.xlsx")

print(f"\n🔧 추천 명령어:")
print("/flow-optimization [이동 경로 최적화 분석]")
print("/bottleneck-analysis [병목 지점 분석]")
print("/efficiency-metrics [효율성 지표 계산]") 