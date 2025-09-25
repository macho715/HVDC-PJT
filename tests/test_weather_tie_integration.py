"""
Weather Tie Integration Tests
MACHO-GPT TDD Phase 4: Weather Tie Integration Module

Tests weather API connectivity and ETA prediction accuracy
for logistics decision support.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from unittest.mock import Mock, patch, MagicMock

# Configure logging for MACHO-GPT
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """기상 데이터 클래스"""
    port_code: str
    temperature: float  # °C
    wind_speed: float   # m/s
    wind_direction: float  # degrees
    visibility: float   # km
    precipitation: float  # mm/h
    timestamp: datetime
    forecast_hours: int = 24

@dataclass
class VesselData:
    """선박 데이터 클래스"""
    vessel_id: str
    current_position: Tuple[float, float]  # lat, lon
    destination_port: str
    current_speed: float  # knots
    max_speed: float  # knots
    departure_time: datetime
    estimated_arrival: datetime
    cargo_type: str
    priority: int = 1

class WeatherTieAnalyzer:
    """Weather Tie 분석 클래스"""
    
    # 기상 임계값 상수
    WIND_SPEED_THRESHOLD = 25.0  # m/s (강풍)
    VISIBILITY_THRESHOLD = 5.0   # km (시정 불량)
    PRECIPITATION_THRESHOLD = 10.0  # mm/h (강우)
    ETA_DELAY_THRESHOLD = 24  # hours
    
    def __init__(self, api_key: str = "test_key"):
        """
        Weather Tie 분석기 초기화
        
        Args:
            api_key: 기상 API 키
        """
        self.api_key = api_key
        self.mode = "RHYTHM"  # Weather Tie 분석 모드
        self.confidence_threshold = 0.95
        
    def check_weather_api_connectivity(self, port_code: str) -> Dict:
        """
        기상 API 연결성 검증
        
        Args:
            port_code: 항구 코드
            
        Returns:
            Dict: API 연결 상태 및 기상 데이터
        """
        try:
            # 실제 API 호출 대신 모의 데이터 사용
            weather_data = self._mock_weather_api_call(port_code)
            
            if weather_data:
                return {
                    'status': 'SUCCESS',
                    'port_code': port_code,
                    'weather_data': weather_data,
                    'api_connected': True,
                    'confidence': 0.95,
                    'mode': self.mode,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'ERROR',
                    'port_code': port_code,
                    'api_connected': False,
                    'error': 'Weather data not available',
                    'confidence': 0.0,
                    'mode': self.mode
                }
                
        except Exception as e:
            logger.error(f"Weather API connectivity error: {e}")
            return {
                'status': 'ERROR',
                'port_code': port_code,
                'api_connected': False,
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def predict_eta_with_weather(self, vessel_data: VesselData, 
                               weather_data: WeatherData) -> Dict:
        """
        기상 조건을 고려한 ETA 예측
        
        Args:
            vessel_data: 선박 데이터
            weather_data: 기상 데이터
            
        Returns:
            Dict: ETA 예측 결과
        """
        try:
            # 기본 ETA 계산
            base_eta = vessel_data.estimated_arrival
            
            # 기상 영향 분석
            weather_impact = self._calculate_weather_impact(weather_data)
            
            # 지연 시간 계산
            delay_hours = self._calculate_delay_hours(weather_impact, vessel_data)
            
            # 새로운 ETA 계산
            new_eta = base_eta + timedelta(hours=delay_hours)
            
            # 예측 신뢰도 계산
            confidence = self._calculate_prediction_confidence(weather_data, delay_hours)
            
            # 지연 임계값 확인
            is_significant_delay = delay_hours > self.ETA_DELAY_THRESHOLD
            
            return {
                'status': 'SUCCESS' if not is_significant_delay else 'WARNING',
                'vessel_id': vessel_data.vessel_id,
                'port_code': weather_data.port_code,
                'original_eta': base_eta.isoformat(),
                'predicted_eta': new_eta.isoformat(),
                'delay_hours': round(delay_hours, 1),
                'weather_impact': weather_impact,
                'is_significant_delay': is_significant_delay,
                'confidence': confidence,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ETA prediction error: {e}")
            return {
                'status': 'ERROR',
                'vessel_id': vessel_data.vessel_id,
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def calculate_storm_impact(self, weather_data: WeatherData) -> Dict:
        """
        폭풍 영향 계산
        
        Args:
            weather_data: 기상 데이터
            
        Returns:
            Dict: 폭풍 영향 분석 결과
        """
        try:
            # 폭풍 조건 확인
            is_storm = (weather_data.wind_speed > self.WIND_SPEED_THRESHOLD or
                       weather_data.visibility < self.VISIBILITY_THRESHOLD or
                       weather_data.precipitation > self.PRECIPITATION_THRESHOLD)
            
            # 폭풍 강도 계산
            storm_intensity = 0.0
            if weather_data.wind_speed > self.WIND_SPEED_THRESHOLD:
                storm_intensity += (weather_data.wind_speed - self.WIND_SPEED_THRESHOLD) / 10.0
            if weather_data.visibility < self.VISIBILITY_THRESHOLD:
                storm_intensity += (self.VISIBILITY_THRESHOLD - weather_data.visibility) / 2.0
            if weather_data.precipitation > self.PRECIPITATION_THRESHOLD:
                storm_intensity += (weather_data.precipitation - self.PRECIPITATION_THRESHOLD) / 5.0
            
            # 영향 수준 결정 (바람 30 m/s는 임계값 25 m/s를 5 m/s 초과하므로 storm_intensity = 0.5)
            impact_level = 'LOW' if storm_intensity < 0.5 else 'MEDIUM' if storm_intensity < 2.0 else 'HIGH'
            
            return {
                'status': 'SUCCESS',
                'is_storm': is_storm,
                'storm_intensity': round(storm_intensity, 2),
                'impact_level': impact_level,
                'wind_impact': weather_data.wind_speed > self.WIND_SPEED_THRESHOLD,
                'visibility_impact': weather_data.visibility < self.VISIBILITY_THRESHOLD,
                'precipitation_impact': weather_data.precipitation > self.PRECIPITATION_THRESHOLD,
                'confidence': 0.95 if is_storm else 0.90,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Storm impact calculation error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def generate_weather_based_routing(self, vessel_data: VesselData, 
                                     weather_forecast: List[WeatherData]) -> Dict:
        """
        기상 기반 경로 최적화
        
        Args:
            vessel_data: 선박 데이터
            weather_forecast: 기상 예보 데이터
            
        Returns:
            Dict: 최적화된 경로 정보
        """
        try:
            # 경로상의 기상 조건 분석
            route_weather_analysis = []
            total_impact = 0.0
            
            for weather in weather_forecast:
                impact = self._calculate_weather_impact(weather)
                route_weather_analysis.append({
                    'port_code': weather.port_code,
                    'impact': impact,
                    'timestamp': weather.timestamp.isoformat()
                })
                total_impact += impact
            
            # 평균 영향도 계산
            avg_impact = total_impact / len(weather_forecast) if weather_forecast else 0.0
            
            # 경로 최적화 권장사항
            if avg_impact > 2.0:
                recommendation = 'ALTERNATIVE_ROUTE'
                confidence = 0.85
            elif avg_impact > 1.0:
                recommendation = 'REDUCED_SPEED'
                confidence = 0.90
            else:
                recommendation = 'NORMAL_ROUTE'
                confidence = 0.95
            
            return {
                'status': 'SUCCESS',
                'vessel_id': vessel_data.vessel_id,
                'route_analysis': route_weather_analysis,
                'average_impact': round(avg_impact, 2),
                'recommendation': recommendation,
                'confidence': confidence,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Weather-based routing error: {e}")
            return {
                'status': 'ERROR',
                'vessel_id': vessel_data.vessel_id,
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def _mock_weather_api_call(self, port_code: str) -> Optional[WeatherData]:
        """모의 기상 API 호출"""
        # 실제 구현에서는 실제 API를 호출
        mock_data = {
            'JED': WeatherData('JED', 28.0, 15.0, 180.0, 8.0, 0.0, datetime.now()),
            'DAM': WeatherData('DAM', 32.0, 8.0, 90.0, 12.0, 2.0, datetime.now()),
            'RUH': WeatherData('RUH', 35.0, 20.0, 270.0, 6.0, 5.0, datetime.now()),
        }
        return mock_data.get(port_code)
    
    def _calculate_weather_impact(self, weather_data: WeatherData) -> float:
        """기상 영향도 계산"""
        impact = 0.0
        
        # 바람 영향
        if weather_data.wind_speed > self.WIND_SPEED_THRESHOLD:
            impact += (weather_data.wind_speed - self.WIND_SPEED_THRESHOLD) / 5.0
        
        # 시정 영향
        if weather_data.visibility < self.VISIBILITY_THRESHOLD:
            impact += (self.VISIBILITY_THRESHOLD - weather_data.visibility) / 2.0
        
        # 강우 영향
        if weather_data.precipitation > self.PRECIPITATION_THRESHOLD:
            impact += (weather_data.precipitation - self.PRECIPITATION_THRESHOLD) / 3.0
        
        return impact
    
    def _calculate_delay_hours(self, weather_impact: float, vessel_data: VesselData) -> float:
        """지연 시간 계산"""
        # 기상 영향에 따른 지연 시간 계산
        base_delay = weather_impact * 2.0  # 기본 지연
        
        # 선박 우선순위에 따른 조정
        priority_factor = 1.0 / vessel_data.priority
        adjusted_delay = base_delay * priority_factor
        
        return min(adjusted_delay, 48.0)  # 최대 48시간 지연
    
    def _calculate_prediction_confidence(self, weather_data: WeatherData, delay_hours: float) -> float:
        """예측 신뢰도 계산"""
        base_confidence = 0.95
        
        # 기상 데이터 품질에 따른 조정
        if weather_data.forecast_hours < 12:
            base_confidence -= 0.1
        
        # 지연 시간이 길수록 신뢰도 감소
        if delay_hours > 24:
            base_confidence -= 0.1
        
        return max(base_confidence, 0.70)

    def generate_delay_notification(self, eta_result: Dict, vessel_data: VesselData) -> Dict:
        """
        지연 알림 생성
        
        Args:
            eta_result: ETA 예측 결과
            vessel_data: 선박 데이터
            
        Returns:
            Dict: 알림 정보
        """
        try:
            if eta_result.get('is_significant_delay', False):
                delay_hours = eta_result.get('delay_hours', 0)
                new_eta = eta_result.get('predicted_eta', 'Unknown')
                
                # 알림 우선순위 결정
                priority = 'HIGH' if delay_hours > 24 else 'MEDIUM'
                
                # 알림 메시지 생성
                message = (f"Vessel {vessel_data.vessel_id} ETA delay alert: "
                          f"{delay_hours:.1f} hours delay. "
                          f"New ETA: {new_eta}")
                
                # 수신자 결정
                recipients = ['logistics_team', 'vessel_operator']
                if priority == 'HIGH':
                    recipients.append('emergency_response')
                
                return {
                    'status': 'SUCCESS',
                    'notification_type': 'DELAY_ALERT',
                    'vessel_id': vessel_data.vessel_id,
                    'message': message,
                    'priority': priority,
                    'recipients': recipients,
                    'delay_hours': delay_hours,
                    'confidence': 0.95,
                    'mode': self.mode,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'NO_ALERT',
                    'notification_type': 'NONE',
                    'message': 'No significant delay detected',
                    'confidence': 0.90,
                    'mode': self.mode
                }
                
        except Exception as e:
            logger.error(f"Delay notification generation error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }


class TestWeatherTieIntegration:
    """Weather Tie 통합 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.analyzer = WeatherTieAnalyzer(api_key="test_key")
        
    def test_weather_api_connectivity_success(self):
        """기상 API 연결 성공 테스트"""
        # Given: 유효한 항구 코드
        port_code = "JED"
        
        # When: API 연결 확인
        result = self.analyzer.check_weather_api_connectivity(port_code)
        
        # Then: 성공적으로 연결되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['api_connected'] == True
        assert result['port_code'] == port_code
        assert result['confidence'] >= 0.95
        assert 'weather_data' in result
        
    def test_weather_api_connectivity_failure(self):
        """기상 API 연결 실패 테스트"""
        # Given: 유효하지 않은 항구 코드
        port_code = "INVALID_PORT"
        
        # When: API 연결 확인
        result = self.analyzer.check_weather_api_connectivity(port_code)
        
        # Then: 연결 실패해야 함
        assert result['status'] == 'ERROR'
        assert result['api_connected'] == False
        assert result['port_code'] == port_code
        assert result['confidence'] == 0.0
        
    def test_eta_prediction_accuracy_normal_conditions(self):
        """정상 기상 조건에서 ETA 예측 정확도 테스트"""
        # Given: 정상 기상 조건과 선박 데이터
        weather_data = WeatherData('JED', 25.0, 10.0, 180.0, 10.0, 0.0, datetime.now())
        vessel_data = VesselData(
            'VESSEL001', 
            (21.5, 39.2),  # Jeddah coordinates
            'JED',
            15.0,  # knots
            20.0,  # knots
            datetime.now() - timedelta(hours=24),
            datetime.now() + timedelta(hours=6),
            'CONTAINER'  # cargo_type
        )
        
        # When: ETA 예측 실행
        result = self.analyzer.predict_eta_with_weather(vessel_data, weather_data)
        
        # Then: 정상 조건이므로 지연이 적어야 함
        assert result['status'] == 'SUCCESS'
        assert result['delay_hours'] < 5.0
        assert result['is_significant_delay'] == False
        assert result['confidence'] >= 0.90
        
    def test_eta_prediction_accuracy_storm_conditions(self):
        """폭풍 조건에서 ETA 예측 정확도 테스트"""
        # Given: 폭풍 기상 조건
        weather_data = WeatherData('RUH', 30.0, 30.0, 270.0, 3.0, 15.0, datetime.now())
        vessel_data = VesselData(
            'VESSEL002',
            (24.7, 46.7),  # Riyadh coordinates
            'RUH',
            10.0,  # knots
            20.0,  # knots
            datetime.now() - timedelta(hours=12),
            datetime.now() + timedelta(hours=8),
            'BULK'  # cargo_type
        )
        
        # When: ETA 예측 실행
        result = self.analyzer.predict_eta_with_weather(vessel_data, weather_data)
        
        # Then: 폭풍 조건이므로 지연이 클 수 있음
        assert result['delay_hours'] > 5.0
        assert result['weather_impact'] > 0.0
        assert result['confidence'] >= 0.70
        
    def test_storm_impact_calculation_high_wind(self):
        """강풍 조건에서 폭풍 영향 계산 테스트"""
        # Given: 강풍 조건
        weather_data = WeatherData('DAM', 28.0, 30.0, 180.0, 8.0, 2.0, datetime.now())
        
        # When: 폭풍 영향 계산
        result = self.analyzer.calculate_storm_impact(weather_data)
        
        # Then: 폭풍으로 인식되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['is_storm'] == True
        assert result['wind_impact'] == True
        assert result['storm_intensity'] > 0.0
        assert result['impact_level'] in ['MEDIUM', 'HIGH']
        
    def test_storm_impact_calculation_normal_conditions(self):
        """정상 조건에서 폭풍 영향 계산 테스트"""
        # Given: 정상 기상 조건
        weather_data = WeatherData('JED', 25.0, 8.0, 90.0, 12.0, 0.0, datetime.now())
        
        # When: 폭풍 영향 계산
        result = self.analyzer.calculate_storm_impact(weather_data)
        
        # Then: 폭풍이 아니어야 함
        assert result['status'] == 'SUCCESS'
        assert result['is_storm'] == False
        assert result['wind_impact'] == False
        assert result['storm_intensity'] == 0.0
        assert result['impact_level'] == 'LOW'
        
    def test_weather_based_routing_optimal_route(self):
        """기상 기반 경로 최적화 테스트"""
        # Given: 다양한 기상 조건의 예보
        weather_forecast = [
            WeatherData('JED', 25.0, 10.0, 180.0, 10.0, 0.0, datetime.now()),
            WeatherData('DAM', 28.0, 15.0, 90.0, 8.0, 2.0, datetime.now() + timedelta(hours=6)),
            WeatherData('RUH', 30.0, 12.0, 270.0, 9.0, 1.0, datetime.now() + timedelta(hours=12))
        ]
        vessel_data = VesselData('VESSEL003', (21.5, 39.2), 'RUH', 15.0, 20.0, 
                                datetime.now(), datetime.now() + timedelta(hours=18), 'CONTAINER')
        
        # When: 경로 최적화 실행
        result = self.analyzer.generate_weather_based_routing(vessel_data, weather_forecast)
        
        # Then: 최적화된 경로 정보가 생성되어야 함
        assert result['status'] == 'SUCCESS'
        assert len(result['route_analysis']) == 3
        assert result['average_impact'] >= 0.0
        assert result['recommendation'] in ['NORMAL_ROUTE', 'REDUCED_SPEED', 'ALTERNATIVE_ROUTE']
        assert result['confidence'] >= 0.85
        
    def test_weather_based_routing_storm_conditions(self):
        """폭풍 조건에서 경로 최적화 테스트"""
        # Given: 폭풍 조건의 예보
        weather_forecast = [
            WeatherData('JED', 30.0, 35.0, 180.0, 3.0, 20.0, datetime.now()),
            WeatherData('DAM', 32.0, 40.0, 90.0, 2.0, 25.0, datetime.now() + timedelta(hours=6))
        ]
        vessel_data = VesselData('VESSEL004', (21.5, 39.2), 'DAM', 10.0, 20.0,
                                datetime.now(), datetime.now() + timedelta(hours=12), 'BULK')
        
        # When: 경로 최적화 실행
        result = self.analyzer.generate_weather_based_routing(vessel_data, weather_forecast)
        
        # Then: 대체 경로가 권장되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['average_impact'] > 2.0
        assert result['recommendation'] == 'ALTERNATIVE_ROUTE'
        assert result['confidence'] >= 0.85

    def test_automated_delay_notifications(self):
        """자동 지연 알림 시스템 테스트"""
        # Given: 극심한 폭풍 조건으로 24시간 이상 지연이 예상되는 선박
        weather_data = WeatherData('RUH', 40.0, 50.0, 270.0, 1.0, 50.0, datetime.now())  # 극심한 폭풍
        vessel_data = VesselData(
            'VESSEL005',
            (24.7, 46.7),  # Riyadh coordinates
            'RUH',
            5.0,  # knots (극도로 감속된 속도)
            20.0,  # knots
            datetime.now() - timedelta(hours=48),
            datetime.now() + timedelta(hours=6),  # 원래 ETA
            'CONTAINER',
            priority=1  # 높은 우선순위
        )
        
        # When: ETA 예측 및 알림 생성
        eta_result = self.analyzer.predict_eta_with_weather(vessel_data, weather_data)
        notification_result = self.analyzer.generate_delay_notification(eta_result, vessel_data)
        
        # Then: 24시간 이상 지연 시 자동 알림이 생성되어야 함
        assert eta_result['is_significant_delay'] == True
        assert eta_result['delay_hours'] > 24.0
        assert notification_result['status'] == 'SUCCESS'
        assert notification_result['notification_type'] == 'DELAY_ALERT'
        assert notification_result['priority'] == 'HIGH'
        assert 'ETA' in notification_result['message']
        assert 'delay' in notification_result['message'].lower()
        assert notification_result['recipients'] == ['logistics_team', 'vessel_operator', 'emergency_response']
        assert notification_result['confidence'] >= 0.90


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"]) 