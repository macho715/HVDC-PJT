#!/usr/bin/env python3
"""
HVDC DSV OUTDOOR 창고 SQM 시각적 분석 시스템
MACHO-GPT v3.4-mini | Samsung C&T × ADNOC·DSV Partnership

목적: 실제 현장 사진과 SQM 데이터를 연결한 종합 분석
- DSV OUTDOOR A, B, C 구역별 사진 분석
- GPS 좌표 기반 공간 분석
- SQM 데이터와 실제 현장 매칭
- 창고 효율성 및 최적화 제안
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path
import re
import warnings
warnings.filterwarnings('ignore')

class HVDCVisualSQMAnalyzer:
    """DSV OUTDOOR 창고 시각적 SQM 분석기"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.photo_path = self.base_path / "PHOTO" / "DSV OUTDOOR"
        self.data_path = self.base_path / "data_cleaned"
        
        # 파일 경로
        self.invoice_file = self.data_path / "HVDC_WAREHOUSE_INVOICE_CLEANED_20250709_201121.xlsx"
        
        # 데이터 저장소
        self.invoice_data = None
        self.photo_inventory = {}
        self.gps_data = {}
        
        print("🏭 DSV OUTDOOR 창고 시각적 SQM 분석 시스템")
        print("=" * 70)
        print(f"📍 현장 위치: 아부다비 (Lat 24.364972° Long 54.474662°)")
        print(f"📅 촬영일: 2025년 7월 9일")
        print(f"🏢 분석 대상: DSV OUTDOOR 창고 A, B, C 구역")
        
    def load_invoice_data(self):
        """INVOICE SQM 데이터 로드"""
        try:
            self.invoice_data = pd.read_excel(self.invoice_file)
            print(f"\n📊 INVOICE 데이터 로드: {len(self.invoice_data):,}건")
            return True
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def analyze_photo_inventory(self):
        """사진 인벤토리 분석"""
        print("\n📸 DSV OUTDOOR 사진 분석")
        print("=" * 50)
        
        sections = ['A', 'B', 'C']
        
        for section in sections:
            section_path = self.photo_path / section
            if section_path.exists():
                photo_files = list(section_path.glob("*.jpg"))
                self.photo_inventory[section] = photo_files
                
                print(f"\n📋 {section}구역 사진 현황:")
                print(f"  총 사진 수: {len(photo_files)}장")
                
                # GPS 좌표 추출
                gps_photos = []
                for photo in photo_files:
                    if "GPS" in photo.name or "ByGPSMapCamera" in photo.name:
                        gps_info = self.extract_gps_from_filename(photo.name)
                        if gps_info:
                            gps_photos.append(gps_info)
                
                if gps_photos:
                    self.gps_data[section] = gps_photos
                    print(f"  GPS 정보 포함: {len(gps_photos)}장")
                    
                    # GPS 좌표 범위 분석
                    lats = [float(g['lat']) for g in gps_photos]
                    lons = [float(g['lon']) for g in gps_photos]
                    
                    print(f"  위도 범위: {min(lats):.6f} ~ {max(lats):.6f}")
                    print(f"  경도 범위: {min(lons):.6f} ~ {max(lons):.6f}")
                    
                    # 구역별 면적 추정 (GPS 좌표 기반)
                    area_estimate = self.estimate_area_from_gps(lats, lons)
                    print(f"  추정 면적: {area_estimate:,.0f} m²")
                
                # 촬영 시간 분석
                time_photos = []
                for photo in photo_files:
                    if "20250709" in photo.name:
                        time_info = self.extract_time_from_filename(photo.name)
                        if time_info:
                            time_photos.append(time_info)
                
                if time_photos:
                    times = [t['time'] for t in time_photos]
                    print(f"  촬영 시간: {min(times)} ~ {max(times)}")
    
    def extract_gps_from_filename(self, filename):
        """파일명에서 GPS 좌표 추출"""
        # 패턴: 24_364972_54_474662 형태
        pattern = r'(\d{2})_(\d{6})_(\d{2})_(\d{6})'
        match = re.search(pattern, filename)
        
        if match:
            lat_deg, lat_min, lon_deg, lon_min = match.groups()
            lat = float(lat_deg) + float(lat_min) / 1000000
            lon = float(lon_deg) + float(lon_min) / 1000000
            
            return {
                'filename': filename,
                'lat': lat,
                'lon': lon,
                'lat_formatted': f"{lat:.6f}",
                'lon_formatted': f"{lon:.6f}"
            }
        return None
    
    def extract_time_from_filename(self, filename):
        """파일명에서 촬영 시간 추출"""
        # 패턴: 20250709_21708오후 형태
        pattern = r'20250709_(\d{5})오후'
        match = re.search(pattern, filename)
        
        if match:
            time_str = match.group(1)
            hour = int(time_str[:2])
            minute = int(time_str[2:4])
            second = int(time_str[4:])
            
            return {
                'filename': filename,
                'time': f"{hour:02d}:{minute:02d}:{second:02d}",
                'hour': hour,
                'minute': minute,
                'second': second
            }
        return None
    
    def estimate_area_from_gps(self, lats, lons):
        """GPS 좌표로부터 면적 추정"""
        if len(lats) < 2 or len(lons) < 2:
            return 0
        
        # 간단한 사각형 면적 추정 (미터 단위)
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        
        # 1도 = 약 111,000m (위도), 경도는 위도에 따라 다름
        lat_meters = lat_range * 111000
        lon_meters = lon_range * 111000 * np.cos(np.radians(np.mean(lats)))
        
        return lat_meters * lon_meters
    
    def analyze_sqm_data_for_dsv_outdoor(self):
        """DSV OUTDOOR SQM 데이터 분석"""
        print("\n🏭 DSV OUTDOOR SQM 데이터 분석")
        print("=" * 50)
        
        if self.invoice_data is None:
            print("❌ INVOICE 데이터가 없습니다.")
            return
        
        # DSV Outdoor 데이터 필터링
        dsv_outdoor_data = self.invoice_data[
            (self.invoice_data['HVDC CODE 1'] == 'DSV Outdoor') & 
            (self.invoice_data['HVDC CODE 2'] == 'SQM')
        ].copy()
        
        if len(dsv_outdoor_data) == 0:
            print("❌ DSV Outdoor SQM 데이터가 없습니다.")
            return
        
        print(f"📊 DSV Outdoor SQM 데이터: {len(dsv_outdoor_data):,}건")
        
        # 기본 통계
        if 'Sqm' in dsv_outdoor_data.columns:
            total_sqm = dsv_outdoor_data['Sqm'].sum()
            avg_sqm = dsv_outdoor_data['Sqm'].mean()
            max_sqm = dsv_outdoor_data['Sqm'].max()
            min_sqm = dsv_outdoor_data['Sqm'].min()
            
            print(f"\n📏 면적 통계:")
            print(f"  총 면적: {total_sqm:,.0f} SQM")
            print(f"  평균 면적: {avg_sqm:.1f} SQM")
            print(f"  최대 면적: {max_sqm:.0f} SQM")
            print(f"  최소 면적: {min_sqm:.0f} SQM")
        
        # 비용 분석
        if 'TOTAL' in dsv_outdoor_data.columns:
            total_cost = dsv_outdoor_data['TOTAL'].sum()
            avg_cost = dsv_outdoor_data['TOTAL'].mean()
            
            print(f"\n💰 비용 분석:")
            print(f"  총 비용: ${total_cost:,.0f}")
            print(f"  평균 비용: ${avg_cost:,.0f}")
            
            if 'Sqm' in dsv_outdoor_data.columns and total_sqm > 0:
                price_per_sqm = total_cost / total_sqm
                print(f"  단가: ${price_per_sqm:.2f}/SQM")
        
        # 벤더별 분석
        if 'HVDC CODE 3' in dsv_outdoor_data.columns:
            print(f"\n🏭 벤더별 분포:")
            vendor_dist = dsv_outdoor_data['HVDC CODE 3'].value_counts()
            for vendor, count in vendor_dist.items():
                print(f"  {vendor}: {count:,}건")
        
        return dsv_outdoor_data
    
    def correlate_photos_with_sqm(self):
        """사진과 SQM 데이터 상관관계 분석"""
        print("\n🔗 사진-SQM 데이터 상관관계 분석")
        print("=" * 50)
        
        sqm_data = self.analyze_sqm_data_for_dsv_outdoor()
        
        if sqm_data is None or len(sqm_data) == 0:
            print("❌ DSV Outdoor SQM 데이터가 없습니다.")
            return
        
        # 구역별 분석
        print("\n📋 구역별 종합 분석:")
        
        total_photos = sum(len(photos) for photos in self.photo_inventory.values())
        total_sqm = sqm_data['Sqm'].sum() if 'Sqm' in sqm_data.columns else 0
        total_cost = sqm_data['TOTAL'].sum() if 'TOTAL' in sqm_data.columns else 0
        
        print(f"\n🏭 DSV OUTDOOR 종합 현황:")
        print(f"  총 구역 수: {len(self.photo_inventory)}개 (A, B, C)")
        print(f"  총 사진 수: {total_photos:,}장")
        print(f"  총 SQM 면적: {total_sqm:,.0f} SQM")
        print(f"  총 임대 비용: ${total_cost:,.0f}")
        
        if total_photos > 0 and total_sqm > 0:
            photos_per_sqm = total_photos / total_sqm
            print(f"  사진 밀도: {photos_per_sqm:.3f} 장/SQM")
        
        # 구역별 효율성 분석
        print(f"\n📊 구역별 효율성 분석:")
        
        for section in ['A', 'B', 'C']:
            if section in self.photo_inventory:
                photo_count = len(self.photo_inventory[section])
                
                # 구역별 면적 추정 (전체 면적의 1/3로 가정)
                estimated_sqm = total_sqm / 3
                estimated_cost = total_cost / 3
                
                print(f"\n  📍 {section}구역:")
                print(f"    사진 수: {photo_count:,}장")
                print(f"    추정 면적: {estimated_sqm:,.0f} SQM")
                print(f"    추정 비용: ${estimated_cost:,.0f}")
                
                if photo_count > 0 and estimated_sqm > 0:
                    documentation_ratio = photo_count / estimated_sqm * 1000
                    print(f"    문서화 비율: {documentation_ratio:.1f} 장/1000SQM")
                
                # GPS 기반 면적 추정
                if section in self.gps_data:
                    gps_photos = self.gps_data[section]
                    lats = [float(g['lat']) for g in gps_photos]
                    lons = [float(g['lon']) for g in gps_photos]
                    gps_area = self.estimate_area_from_gps(lats, lons)
                    
                    if gps_area > 0:
                        print(f"    GPS 기반 면적: {gps_area:,.0f} m²")
                        print(f"    면적 활용률: {(gps_area / (estimated_sqm * 1.0)):.1%}")
    
    def generate_optimization_recommendations(self):
        """최적화 권장사항 생성"""
        print("\n🎯 DSV OUTDOOR 최적화 권장사항")
        print("=" * 50)
        
        sqm_data = self.analyze_sqm_data_for_dsv_outdoor()
        
        if sqm_data is None or len(sqm_data) == 0:
            print("❌ 분석 데이터가 없습니다.")
            return
        
        total_photos = sum(len(photos) for photos in self.photo_inventory.values())
        total_sqm = sqm_data['Sqm'].sum() if 'Sqm' in sqm_data.columns else 0
        total_cost = sqm_data['TOTAL'].sum() if 'TOTAL' in sqm_data.columns else 0
        
        print(f"📋 현재 현황 기반 최적화 제안:")
        
        # 1. 면적 활용 최적화
        print(f"\n1️⃣ 면적 활용 최적화:")
        if total_sqm > 0:
            efficiency_score = (total_photos / total_sqm) * 100
            print(f"   현재 문서화 효율성: {efficiency_score:.2f}점")
            
            if efficiency_score < 0.1:
                print("   ⚠️  문서화 부족: 더 많은 현장 사진 필요")
            elif efficiency_score > 0.5:
                print("   ✅ 문서화 양호: 현재 수준 유지")
            else:
                print("   📈 문서화 보통: 주요 구역 추가 촬영 권장")
        
        # 2. 비용 효율성 개선
        print(f"\n2️⃣ 비용 효율성 개선:")
        if total_sqm > 0 and total_cost > 0:
            current_rate = total_cost / total_sqm
            print(f"   현재 임대 단가: ${current_rate:.2f}/SQM")
            
            # 업계 평균과 비교 (가정)
            market_rate = 8.5  # 가정 값
            if current_rate > market_rate:
                saving_potential = (current_rate - market_rate) * total_sqm
                print(f"   💰 비용 절감 잠재력: ${saving_potential:,.0f}")
            else:
                print("   ✅ 경쟁력 있는 임대료 수준")
        
        # 3. 구역별 최적화
        print(f"\n3️⃣ 구역별 최적화:")
        for section in ['A', 'B', 'C']:
            if section in self.photo_inventory:
                photo_count = len(self.photo_inventory[section])
                print(f"   {section}구역: {photo_count:,}장 → ", end="")
                
                if photo_count < 10:
                    print("추가 모니터링 필요")
                elif photo_count < 30:
                    print("적정 수준")
                else:
                    print("충분한 문서화")
        
        # 4. 기술적 권장사항
        print(f"\n4️⃣ 기술적 권장사항:")
        print("   📱 GPS 기반 자동 면적 계산 도입")
        print("   🤖 AI 기반 창고 활용률 분석")
        print("   📊 실시간 SQM 모니터링 시스템")
        print("   🔄 월별 최적화 리포트 자동 생성")
    
    def generate_comprehensive_report(self):
        """종합 보고서 생성"""
        print("\n📋 DSV OUTDOOR 종합 분석 보고서")
        print("=" * 60)
        
        print(f"📅 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏢 프로젝트: HVDC Samsung C&T × ADNOC·DSV")
        print(f"🤖 시스템: MACHO-GPT v3.4-mini")
        print(f"📍 분석 대상: DSV OUTDOOR 창고 (아부다비)")
        
        # 요약 통계
        total_photos = sum(len(photos) for photos in self.photo_inventory.values())
        total_sections = len(self.photo_inventory)
        
        print(f"\n📊 분석 결과 요약:")
        print(f"  분석 구역: {total_sections}개 (A, B, C)")
        print(f"  총 사진 수: {total_photos:,}장")
        print(f"  GPS 데이터: {len(self.gps_data)}개 구역")
        
        if self.invoice_data is not None:
            dsv_outdoor_data = self.invoice_data[
                (self.invoice_data['HVDC CODE 1'] == 'DSV Outdoor') & 
                (self.invoice_data['HVDC CODE 2'] == 'SQM')
            ]
            
            if len(dsv_outdoor_data) > 0:
                if 'Sqm' in dsv_outdoor_data.columns:
                    total_sqm = dsv_outdoor_data['Sqm'].sum()
                    print(f"  총 SQM 면적: {total_sqm:,.0f} SQM")
                
                if 'TOTAL' in dsv_outdoor_data.columns:
                    total_cost = dsv_outdoor_data['TOTAL'].sum()
                    print(f"  총 임대 비용: ${total_cost:,.0f}")
        
        print(f"\n🎯 분석 완료 - 최적화 권장사항 참조")
    
    def run_complete_analysis(self):
        """전체 분석 실행"""
        
        # 1. 데이터 로드
        if not self.load_invoice_data():
            return
        
        # 2. 사진 인벤토리 분석
        self.analyze_photo_inventory()
        
        # 3. SQM 데이터 분석
        self.analyze_sqm_data_for_dsv_outdoor()
        
        # 4. 사진-SQM 상관관계 분석
        self.correlate_photos_with_sqm()
        
        # 5. 최적화 권장사항
        self.generate_optimization_recommendations()
        
        # 6. 종합 보고서
        self.generate_comprehensive_report()
        
        # 7. 추천 명령어
        print("\n🔧 **추천 명령어:**")
        print("/warehouse-optimize [DSV OUTDOOR 최적화 실행 - 면적 효율성 개선]")
        print("/photo-analysis [사진 기반 창고 분석 - AI 비주얼 인식]")
        print("/gps-mapping [GPS 좌표 매핑 - 정확한 면적 계산]")

def main():
    """메인 실행 함수"""
    analyzer = HVDCVisualSQMAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main() 