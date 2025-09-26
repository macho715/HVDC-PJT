import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime
import json

print("🗺️ HVDC 창고 3D 지도 시각화 시스템")
print("=" * 50)
print("🔄 시작 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# HVDC 창고 실제 위치 정보 (UAE 기준)
warehouse_locations = {
    'DSV Outdoor': {
        'name': 'DSV Outdoor Warehouse',
        'longitude': 55.3781,
        'latitude': 25.1172,
        'capacity': 15996.25,  # m²
        'utilization': 36.8,
        'packages': 1024,
        'zone_type': 'outdoor'
    },
    'DSV Indoor': {
        'name': 'DSV Indoor Warehouse', 
        'longitude': 55.3845,
        'latitude': 25.1204,
        'capacity': 12500.0,
        'utilization': 45.2,
        'packages': 1297,
        'zone_type': 'indoor'
    },
    'DSV Al Markaz': {
        'name': 'DSV Al Markaz',
        'longitude': 55.3912,
        'latitude': 25.1156,
        'capacity': 8000.0,
        'utilization': 42.1,
        'packages': 1066,
        'zone_type': 'indoor'
    },
    'DSV MZP': {
        'name': 'DSV MZP Hub',
        'longitude': 55.3723,
        'latitude': 25.1098,
        'capacity': 20000.0,
        'utilization': 55.8,
        'packages': 5552,
        'zone_type': 'hub'
    },
    'AAA Storage': {
        'name': 'AAA Storage Facility',
        'longitude': 55.3654,
        'latitude': 25.1234,
        'capacity': 6000.0,
        'utilization': 28.5,
        'packages': 392,
        'zone_type': 'storage'
    }
}

# 창고 데이터 준비
warehouse_data = []
for warehouse_code, info in warehouse_locations.items():
    warehouse_data.append({
        'warehouse_code': warehouse_code,
        'name': info['name'],
        'longitude': info['longitude'],
        'latitude': info['latitude'],
        'capacity': info['capacity'],
        'utilization': info['utilization'],
        'packages': info['packages'],
        'zone_type': info['zone_type'],
        'elevation': int(info['packages'] / 100),  # 패키지 수 기반 높이
        'color': [
            255 if info['utilization'] > 50 else 100,  # Red component
            255 if info['utilization'] < 30 else 100,  # Green component
            100,  # Blue component
            160   # Alpha
        ]
    })

df_warehouses = pd.DataFrame(warehouse_data)

print(f"📊 창고 수: {len(df_warehouses)}개")
print(f"📍 위치 범위: {df_warehouses['longitude'].min():.4f}~{df_warehouses['longitude'].max():.4f}, {df_warehouses['latitude'].min():.4f}~{df_warehouses['latitude'].max():.4f}")

# 창고 구역 폴리곤 생성 (각 창고 주변 직사각형 영역)
def create_warehouse_polygon(lng, lat, width=0.002, height=0.002):
    """창고 위치 기반 폴리곤 생성"""
    return [
        [lng - width/2, lat - height/2],
        [lng + width/2, lat - height/2], 
        [lng + width/2, lat + height/2],
        [lng - width/2, lat + height/2],
        [lng - width/2, lat - height/2]
    ]

# 폴리곤 데이터 생성
polygon_data = []
for idx, row in df_warehouses.iterrows():
    polygon_data.append({
        'warehouse_code': row['warehouse_code'],
        'name': row['name'],
        'coordinates': create_warehouse_polygon(row['longitude'], row['latitude']),
        'elevation': row['elevation'],
        'color': row['color'],
        'utilization': row['utilization'],
        'packages': row['packages']
    })

df_polygons = pd.DataFrame(polygon_data)

# 이동 경로 데이터 생성 (주요 이동 경로)
movement_routes = [
    {
        'source': 'DSV MZP',
        'target': 'DSV Outdoor',
        'movements': 1300,
        'path': [
            [warehouse_locations['DSV MZP']['longitude'], warehouse_locations['DSV MZP']['latitude']],
            [warehouse_locations['DSV Outdoor']['longitude'], warehouse_locations['DSV Outdoor']['latitude']]
        ]
    },
    {
        'source': 'DSV MZP', 
        'target': 'DSV Indoor',
        'movements': 1297,
        'path': [
            [warehouse_locations['DSV MZP']['longitude'], warehouse_locations['DSV MZP']['latitude']],
            [warehouse_locations['DSV Indoor']['longitude'], warehouse_locations['DSV Indoor']['latitude']]
        ]
    },
    {
        'source': 'DSV Indoor',
        'target': 'DSV Al Markaz', 
        'movements': 636,
        'path': [
            [warehouse_locations['DSV Indoor']['longitude'], warehouse_locations['DSV Indoor']['latitude']],
            [warehouse_locations['DSV Al Markaz']['longitude'], warehouse_locations['DSV Al Markaz']['latitude']]
        ]
    },
    {
        'source': 'DSV MZP',
        'target': 'AAA Storage',
        'movements': 392,
        'path': [
            [warehouse_locations['DSV MZP']['longitude'], warehouse_locations['DSV MZP']['latitude']],
            [warehouse_locations['AAA Storage']['longitude'], warehouse_locations['AAA Storage']['latitude']]
        ]
    }
]

df_routes = pd.DataFrame(movement_routes)

# 1. 창고 3D 폴리곤 레이어
print("🏗️ 3D 창고 폴리곤 레이어 생성...")
polygon_layer = pdk.Layer(
    "PolygonLayer",
    data=df_polygons,
    get_polygon="coordinates",
    get_fill_color="color",
    get_line_color=[255, 255, 255, 100],
    pickable=True,
    extruded=True,
    elevation_scale=20,
    get_elevation="elevation",
    line_width_min_pixels=2,
    auto_highlight=True
)

# 2. 창고 포인트 레이어 (라벨용)
print("📍 창고 포인트 레이어 생성...")
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_warehouses,
    get_position=["longitude", "latitude"],
    get_color="color",
    get_radius="packages",
    radius_scale=0.5,
    pickable=True,
    auto_highlight=True
)

# 3. 이동 경로 레이어
print("🚚 이동 경로 레이어 생성...")
path_layer = pdk.Layer(
    "PathLayer",
    data=df_routes,
    get_path="path",
    get_width="movements",
    width_scale=0.01,
    width_min_pixels=2,
    get_color=[255, 140, 0, 200],  # Orange color for routes
    pickable=True,
    auto_highlight=True
)

# 4. 텍스트 레이어 (창고 이름)
print("🏷️ 텍스트 레이어 생성...")
text_layer = pdk.Layer(
    "TextLayer",
    data=df_warehouses,
    get_position=["longitude", "latitude"],
    get_text="warehouse_code",
    get_size=16,
    get_color=[255, 255, 255, 255],
    get_angle=0,
    pickable=True
)

# 뷰포트 설정 (UAE 두바이 지역 중심)
center_lng = df_warehouses['longitude'].mean()
center_lat = df_warehouses['latitude'].mean()

initial_view = pdk.ViewState(
    longitude=center_lng,
    latitude=center_lat,
    zoom=13,
    pitch=45,
    bearing=0
)

print(f"📍 중심점: {center_lng:.4f}, {center_lat:.4f}")

# 툴팁 설정
tooltip_warehouse = {
    "html": """
    <b>창고:</b> {name}<br>
    <b>코드:</b> {warehouse_code}<br>
    <b>용량:</b> {capacity:,.0f} m²<br>
    <b>사용률:</b> {utilization}%<br>
    <b>패키지:</b> {packages:,}개
    """,
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
        "border": "1px solid white",
        "borderRadius": "5px",
        "padding": "10px"
    }
}

tooltip_route = {
    "html": """
    <b>경로:</b> {source} → {target}<br>
    <b>이동량:</b> {movements:,}건
    """,
    "style": {
        "backgroundColor": "orange",
        "color": "white",
        "border": "1px solid white", 
        "borderRadius": "5px",
        "padding": "10px"
    }
}

# Deck 객체 생성
print("🎨 3D 지도 생성...")
deck = pdk.Deck(
    layers=[polygon_layer, path_layer, point_layer, text_layer],
    initial_view_state=initial_view,
    map_style="mapbox://styles/mapbox/satellite-v9",
    tooltip=tooltip_warehouse
)

# HTML 파일로 내보내기
output_file = "hvdc_warehouse_3d_map.html"
deck.to_html(output_file, notebook_display=False)
print(f"✅ 3D 지도 저장: {output_file}")

# 추가 분석용 간단한 2D 지도도 생성
print("\n🗺️ 2D 분석 지도 생성...")
view_2d = pdk.ViewState(
    longitude=center_lng,
    latitude=center_lat,
    zoom=13,
    pitch=0,
    bearing=0
)

# 2D 버전 (분석용)
deck_2d = pdk.Deck(
    layers=[point_layer, path_layer, text_layer],
    initial_view_state=view_2d,
    map_style="mapbox://styles/mapbox/light-v10",
    tooltip=tooltip_warehouse
)

output_file_2d = "hvdc_warehouse_2d_map.html"
deck_2d.to_html(output_file_2d, notebook_display=False)
print(f"✅ 2D 지도 저장: {output_file_2d}")

# 창고 정보 요약 리포트
print("\n📊 창고 위치 및 활용도 분석")
print("=" * 40)
print(f"{'창고명':<15} {'위치':<20} {'사용률':<8} {'패키지':<8}")
print("-" * 60)

for _, row in df_warehouses.iterrows():
    pos = f"{row['latitude']:.3f},{row['longitude']:.3f}"
    print(f"{row['warehouse_code']:<15} {pos:<20} {row['utilization']:>6.1f}% {row['packages']:>7,}개")

print(f"\n📈 이동 경로 분석:")
print("-" * 30)
for _, route in df_routes.iterrows():
    print(f"{route['source']} → {route['target']}: {route['movements']:,}건")

# 지도 사용 가이드
print(f"\n🎯 3D 지도 사용 가이드:")
print("=" * 30)
print("1. 마우스 드래그: 지도 이동")
print("2. 스크롤: 줌 인/아웃")
print("3. Shift + 드래그: 시점 회전")
print("4. Ctrl + 드래그: 틸트 조정")
print("5. 창고 클릭: 상세 정보 표시")

# 데이터 저장 (numpy 타입을 Python 타입으로 변환)
def convert_numpy_types(obj):
    """numpy 타입을 Python 타입으로 변환"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

warehouse_summary = {
    'warehouses': convert_numpy_types(df_warehouses.to_dict('records')),
    'routes': convert_numpy_types(df_routes.to_dict('records')),
    'center_coordinates': [float(center_lng), float(center_lat)],
    'total_capacity': float(df_warehouses['capacity'].sum()),
    'average_utilization': float(df_warehouses['utilization'].mean()),
    'total_packages': int(df_warehouses['packages'].sum())
}

with open('hvdc_warehouse_map_data.json', 'w', encoding='utf-8') as f:
    json.dump(warehouse_summary, f, ensure_ascii=False, indent=2)

print(f"\n💾 지도 데이터 저장: hvdc_warehouse_map_data.json")
print(f"📊 총 창고 용량: {warehouse_summary['total_capacity']:,.0f} m²")
print(f"📊 평균 사용률: {warehouse_summary['average_utilization']:.1f}%")
print(f"📊 총 패키지: {warehouse_summary['total_packages']:,}개")

print(f"\n🔧 추천 명령어:")
print("/geospatial-analysis [지리공간 분석]")
print("/route-optimization [경로 최적화]")
print("/capacity-heatmap [용량 히트맵]") 