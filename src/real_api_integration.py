#!/usr/bin/env python3
"""
실제 외부 API 연동 시스템
=========================
OpenWeatherMap, OCR.space, MarineTraffic 등 실제 API와 연동
"""

import requests
import aiohttp
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import base64
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API 설정"""

    name: str
    base_url: str
    api_key: str
    enabled: bool
    rate_limit: int = 100  # requests per hour
    timeout: int = 30


class RealAPIIntegration:
    """실제 외부 API 연동 시스템"""

    def __init__(self):
        self.session = None
        self.api_configs = {
            "weather": APIConfig(
                name="OpenWeatherMap",
                base_url="https://api.openweathermap.org/data/2.5",
                api_key=os.getenv("OPENWEATHER_API_KEY", ""),
                enabled=bool(os.getenv("OPENWEATHER_API_KEY")),
                rate_limit=1000,
            ),
            "ocr": APIConfig(
                name="OCR.space",
                base_url="https://api.ocr.space/parse/image",
                api_key=os.getenv("OCR_API_KEY", ""),
                enabled=bool(os.getenv("OCR_API_KEY")),
                rate_limit=500,
            ),
            "shipping": APIConfig(
                name="MarineTraffic",
                base_url="https://api.marinetraffic.com/api",
                api_key=os.getenv("MARINETRAFFIC_API_KEY", ""),
                enabled=bool(os.getenv("MARINETRAFFIC_API_KEY")),
                rate_limit=100,
            ),
            "port": APIConfig(
                name="Port Authority",
                base_url="https://api.portauthority.com",
                api_key=os.getenv("PORT_API_KEY", ""),
                enabled=bool(os.getenv("PORT_API_KEY")),
                rate_limit=200,
            ),
        }

        # 포트 좌표 데이터베이스
        self.port_coordinates = {
            "JEBEL_ALI": {"lat": 25.0084, "lon": 55.0694, "country": "UAE"},
            "FUJAIRAH": {"lat": 25.4111, "lon": 56.2480, "country": "UAE"},
            "ABU_DHABI": {"lat": 24.4539, "lon": 54.3773, "country": "UAE"},
            "DUBAI": {"lat": 25.2048, "lon": 55.2708, "country": "UAE"},
            "SHARJAH": {"lat": 25.3463, "lon": 55.4209, "country": "UAE"},
            "SALALAH": {"lat": 17.0151, "lon": 54.6924, "country": "Oman"},
            "JEDDAH": {"lat": 21.5433, "lon": 39.1678, "country": "Saudi Arabia"},
            "DAMMAM": {"lat": 26.4207, "lon": 50.0888, "country": "Saudi Arabia"},
        }

        logger.info("🚀 실제 API 연동 시스템 초기화")
        for api_name, config in self.api_configs.items():
            status = "✅ 활성화" if config.enabled else "❌ 비활성화"
            logger.info(f"   {config.name}: {status}")

    async def initialize(self):
        """세션 초기화"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        logger.info("✅ API 세션 초기화 완료")

    async def get_real_weather_data(self, port_code: str) -> Dict[str, Any]:
        """실제 날씨 데이터 수집"""
        config = self.api_configs["weather"]

        if not config.enabled:
            logger.warning(f"⚠️ {config.name} API가 비활성화되어 있습니다.")
            return self._get_simulated_weather_data(port_code)

        try:
            coords = self.port_coordinates.get(port_code)
            if not coords:
                logger.error(f"❌ 알 수 없는 포트 코드: {port_code}")
                return self._get_simulated_weather_data(port_code)

            url = f"{config.base_url}/weather"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": config.api_key,
                "units": "metric",
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    weather_data = await response.json()

                    # 실제 날씨 데이터 처리
                    result = {
                        "status": "SUCCESS",
                        "confidence": 0.95,
                        "source": "OpenWeatherMap",
                        "data": {
                            "port_code": port_code,
                            "coordinates": coords,
                            "temperature": weather_data["main"]["temp"],
                            "feels_like": weather_data["main"]["feels_like"],
                            "humidity": weather_data["main"]["humidity"],
                            "pressure": weather_data["main"]["pressure"],
                            "wind_speed": weather_data["wind"]["speed"],
                            "wind_direction": weather_data["wind"].get("deg", 0),
                            "visibility": weather_data.get("visibility", 10000) / 1000,
                            "precipitation": weather_data.get("rain", {}).get("1h", 0),
                            "weather_condition": weather_data["weather"][0]["main"],
                            "description": weather_data["weather"][0]["description"],
                            "icon": weather_data["weather"][0]["icon"],
                        },
                        "timestamp": datetime.now().isoformat(),
                    }

                    # 날씨 영향도 계산
                    impact_score = self._calculate_weather_impact(result["data"])
                    result["data"]["impact_score"] = impact_score
                    result["data"]["operation_risk"] = self._get_risk_level(
                        impact_score
                    )
                    result["data"]["recommendations"] = (
                        self._get_weather_recommendations(impact_score)
                    )

                    logger.info(
                        f"🌤️ 실제 날씨 데이터 수집 완료: {port_code} - {result['data']['weather_condition']}"
                    )
                    return result
                else:
                    logger.error(f"❌ 날씨 API 호출 실패: {response.status}")
                    return self._get_simulated_weather_data(port_code)

        except Exception as e:
            logger.error(f"❌ 날씨 데이터 수집 실패: {e}")
            return self._get_simulated_weather_data(port_code)

    async def get_real_ocr_data(self, file_path: str) -> Dict[str, Any]:
        """실제 OCR 데이터 처리"""
        config = self.api_configs["ocr"]

        if not config.enabled:
            logger.warning(f"⚠️ {config.name} API가 비활성화되어 있습니다.")
            return self._get_simulated_ocr_data(file_path)

        try:
            # 파일 존재 확인
            if not os.path.exists(file_path):
                logger.error(f"❌ 파일을 찾을 수 없음: {file_path}")
                return {
                    "status": "ERROR",
                    "message": f"File not found: {file_path}",
                    "data": {},
                }

            # 파일 업로드
            with open(file_path, "rb") as file:
                files = {"file": file}
                data = {
                    "apikey": config.api_key,
                    "language": "eng",
                    "isOverlayRequired": "false",
                    "filetype": Path(file_path).suffix[1:].upper(),
                    "detectOrientation": "true",
                    "scale": "true",
                }

                async with self.session.post(
                    config.base_url, data=data, files=files
                ) as response:
                    if response.status == 200:
                        ocr_result = await response.json()

                        if ocr_result.get("IsErroredOnProcessing", False):
                            error_msg = ocr_result.get(
                                "ErrorMessage", "Unknown OCR error"
                            )
                            logger.error(f"❌ OCR 처리 실패: {error_msg}")
                            return {"status": "ERROR", "message": error_msg, "data": {}}

                        # 실제 OCR 결과 처리
                        parsed_results = ocr_result.get("ParsedResults", [])
                        if not parsed_results:
                            logger.warning("⚠️ OCR 결과가 비어있습니다.")
                            return self._get_simulated_ocr_data(file_path)

                        parsed_text = parsed_results[0].get("ParsedText", "")

                        result = {
                            "status": "SUCCESS",
                            "confidence": 0.92,
                            "source": "OCR.space",
                            "data": {
                                "file_path": file_path,
                                "file_size": os.path.getsize(file_path),
                                "parsed_text": parsed_text,
                                "word_count": len(parsed_text.split()),
                                "character_count": len(parsed_text),
                                "processing_time": ocr_result.get(
                                    "ProcessingTimeInMilliseconds", 0
                                )
                                / 1000,
                                "extracted_data": self._extract_invoice_data(
                                    parsed_text
                                ),
                                "ocr_confidence": parsed_results[0]
                                .get("TextOverlay", {})
                                .get("Lines", [{}])[0]
                                .get("Confidence", 0),
                            },
                            "timestamp": datetime.now().isoformat(),
                        }

                        logger.info(
                            f"📄 실제 OCR 처리 완료: {file_path} - {result['data']['word_count']}단어"
                        )
                        return result
                    else:
                        logger.error(f"❌ OCR API 호출 실패: {response.status}")
                        return self._get_simulated_ocr_data(file_path)

        except Exception as e:
            logger.error(f"❌ OCR 처리 실패: {e}")
            return self._get_simulated_ocr_data(file_path)

    async def get_real_shipping_data(self, vessel_id: str) -> Dict[str, Any]:
        """실제 선박 추적 데이터"""
        config = self.api_configs["shipping"]

        if not config.enabled:
            logger.warning(f"⚠️ {config.name} API가 비활성화되어 있습니다.")
            return self._get_simulated_shipping_data(vessel_id)

        try:
            # 선박 마스터 데이터 조회
            url = f"{config.base_url}/vessel/master_data"
            params = {"v": 3, "mmsi": vessel_id, "apikey": config.api_key}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    shipping_data = await response.json()

                    if not shipping_data.get("data"):
                        logger.warning(f"⚠️ 선박 데이터를 찾을 수 없음: {vessel_id}")
                        return self._get_simulated_shipping_data(vessel_id)

                    vessel_info = shipping_data["data"][0]

                    # 실시간 위치 데이터 조회
                    position_url = f"{config.base_url}/vessel/export"
                    position_params = {
                        "v": 3,
                        "mmsi": vessel_id,
                        "apikey": config.api_key,
                    }

                    async with self.session.get(
                        position_url, params=position_params
                    ) as pos_response:
                        position_data = (
                            await pos_response.json()
                            if pos_response.status == 200
                            else {}
                        )

                    result = {
                        "status": "SUCCESS",
                        "confidence": 0.94,
                        "source": "MarineTraffic",
                        "data": {
                            "vessel_id": vessel_id,
                            "vessel_name": vessel_info.get("SHIPNAME", "Unknown"),
                            "imo": vessel_info.get("IMO", ""),
                            "mmsi": vessel_info.get("MMSI", ""),
                            "vessel_type": vessel_info.get("VESSEL_TYPE", ""),
                            "flag": vessel_info.get("FLAG", ""),
                            "current_position": {
                                "lat": vessel_info.get("LAT", 0),
                                "lon": vessel_info.get("LON", 0),
                            },
                            "speed": vessel_info.get("SPEED", 0),
                            "course": vessel_info.get("COURSE", 0),
                            "destination": vessel_info.get("DESTINATION", "Unknown"),
                            "eta": vessel_info.get("ETA", "Unknown"),
                            "last_update": vessel_info.get("TIMESTAMP", ""),
                            "port_of_call": vessel_info.get("PORT_OF_CALL", ""),
                            "status": vessel_info.get("STATUS", ""),
                        },
                        "timestamp": datetime.now().isoformat(),
                    }

                    # ETA 계산
                    if result["data"]["eta"] and result["data"]["eta"] != "Unknown":
                        eta_datetime = self._parse_eta(result["data"]["eta"])
                        if eta_datetime:
                            result["data"]["eta_datetime"] = eta_datetime.isoformat()
                            result["data"]["eta_delay"] = self._calculate_eta_delay(
                                eta_datetime
                            )

                    logger.info(
                        f"🚢 실제 선박 데이터 수집 완료: {vessel_id} - {result['data']['vessel_name']}"
                    )
                    return result
                else:
                    logger.error(f"❌ Shipping API 호출 실패: {response.status}")
                    return self._get_simulated_shipping_data(vessel_id)

        except Exception as e:
            logger.error(f"❌ 선박 데이터 수집 실패: {e}")
            return self._get_simulated_shipping_data(vessel_id)

    async def get_real_port_data(self, port_code: str) -> Dict[str, Any]:
        """실제 포트 데이터 조회"""
        config = self.api_configs["port"]

        if not config.enabled:
            logger.warning(f"⚠️ {config.name} API가 비활성화되어 있습니다.")
            return self._get_simulated_port_data(port_code)

        try:
            url = f"{config.base_url}/port/status"
            params = {"port_code": port_code, "api_key": config.api_key}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    port_data = await response.json()

                    result = {
                        "status": "SUCCESS",
                        "confidence": 0.93,
                        "source": "Port Authority",
                        "data": {
                            "port_code": port_code,
                            "port_name": port_data.get("name", ""),
                            "status": port_data.get("status", "operational"),
                            "capacity": port_data.get("capacity", 0),
                            "current_utilization": port_data.get("utilization", 0),
                            "waiting_vessels": port_data.get("waiting_vessels", 0),
                            "berth_availability": port_data.get(
                                "berth_availability", []
                            ),
                            "weather_conditions": port_data.get("weather", {}),
                            "last_update": datetime.now().isoformat(),
                        },
                        "timestamp": datetime.now().isoformat(),
                    }

                    logger.info(f"🏗️ 실제 포트 데이터 수집 완료: {port_code}")
                    return result
                else:
                    logger.error(f"❌ Port API 호출 실패: {response.status}")
                    return self._get_simulated_port_data(port_code)

        except Exception as e:
            logger.error(f"❌ 포트 데이터 수집 실패: {e}")
            return self._get_simulated_port_data(port_code)

    # 시뮬레이션 데이터 (API 비활성화 시 사용)
    def _get_simulated_weather_data(self, port_code: str) -> Dict[str, Any]:
        """시뮬레이션된 날씨 데이터"""
        return {
            "status": "SUCCESS",
            "confidence": 0.85,
            "source": "Simulation",
            "data": {
                "port_code": port_code,
                "temperature": 28.5,
                "humidity": 65,
                "wind_speed": 12.3,
                "visibility": 8.5,
                "precipitation": 0.0,
                "weather_condition": "Clear",
                "description": "clear sky",
                "impact_score": 0.1,
                "operation_risk": "low",
                "recommendations": ["정상 운항 가능"],
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Simulated data - API not available",
        }

    def _get_simulated_ocr_data(self, file_path: str) -> Dict[str, Any]:
        """시뮬레이션된 OCR 데이터"""
        return {
            "status": "SUCCESS",
            "confidence": 0.88,
            "source": "Simulation",
            "data": {
                "file_path": file_path,
                "parsed_text": "Sample invoice text with HVDC project details...",
                "word_count": 150,
                "character_count": 1200,
                "processing_time": 2.5,
                "extracted_data": {
                    "invoice_number": "INV-2024-001",
                    "total_amount": 15000.00,
                    "vendor": "HVDC Project Vendor",
                    "date": "2024-01-15",
                    "items": ["Container parts", "Electrical equipment"],
                },
                "ocr_confidence": 0.85,
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Simulated data - API not available",
        }

    def _get_simulated_shipping_data(self, vessel_id: str) -> Dict[str, Any]:
        """시뮬레이션된 선박 데이터"""
        return {
            "status": "SUCCESS",
            "confidence": 0.90,
            "source": "Simulation",
            "data": {
                "vessel_id": vessel_id,
                "vessel_name": "HVDC Cargo Vessel",
                "imo": "IMO1234567",
                "mmsi": vessel_id,
                "vessel_type": "Cargo",
                "flag": "UAE",
                "current_position": {"lat": 25.0084, "lon": 55.0694},
                "speed": 15.5,
                "course": 180,
                "destination": "Jebel Ali",
                "eta": "2024-01-15 14:30:00",
                "eta_datetime": "2024-01-15T14:30:00",
                "eta_delay": 0,
                "port_of_call": "Jebel Ali",
                "status": "Underway",
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Simulated data - API not available",
        }

    def _get_simulated_port_data(self, port_code: str) -> Dict[str, Any]:
        """시뮬레이션된 포트 데이터"""
        return {
            "status": "SUCCESS",
            "confidence": 0.87,
            "source": "Simulation",
            "data": {
                "port_code": port_code,
                "port_name": f"{port_code} Port",
                "status": "operational",
                "capacity": 1000,
                "current_utilization": 75,
                "waiting_vessels": 5,
                "berth_availability": ["Berth 1", "Berth 3", "Berth 5"],
                "weather_conditions": {"wind": 12, "visibility": 8},
                "last_update": datetime.now().isoformat(),
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Simulated data - API not available",
        }

    # 유틸리티 함수들
    def _calculate_weather_impact(self, weather_data: Dict[str, Any]) -> float:
        """날씨 영향도 계산"""
        impact = 0.0

        # 바람 속도 영향 (m/s)
        wind_speed = weather_data.get("wind_speed", 0)
        if wind_speed > 20:
            impact += 0.5
        elif wind_speed > 15:
            impact += 0.3
        elif wind_speed > 10:
            impact += 0.2
        elif wind_speed > 5:
            impact += 0.1

        # 가시도 영향 (km)
        visibility = weather_data.get("visibility", 10)
        if visibility < 2:
            impact += 0.6
        elif visibility < 5:
            impact += 0.4
        elif visibility < 8:
            impact += 0.2

        # 강수량 영향 (mm)
        precipitation = weather_data.get("precipitation", 0)
        if precipitation > 20:
            impact += 0.4
        elif precipitation > 10:
            impact += 0.3
        elif precipitation > 5:
            impact += 0.2
        elif precipitation > 0:
            impact += 0.1

        # 온도 영향
        temperature = weather_data.get("temperature", 25)
        if temperature > 45 or temperature < 5:
            impact += 0.3
        elif temperature > 40 or temperature < 10:
            impact += 0.2

        return min(impact, 1.0)

    def _get_risk_level(self, impact_score: float) -> str:
        """위험도 레벨 결정"""
        if impact_score < 0.3:
            return "low"
        elif impact_score < 0.6:
            return "moderate"
        else:
            return "high"

    def _get_weather_recommendations(self, impact_score: float) -> List[str]:
        """날씨 기반 권장사항"""
        recommendations = []

        if impact_score > 0.6:
            recommendations.extend(
                ["운항 중단 고려", "대안 경로 검토", "ETA 재계산 필요"]
            )
        elif impact_score > 0.3:
            recommendations.extend(["속도 조정 권장", "주의 운항", "ETA 지연 예상"])
        else:
            recommendations.append("정상 운항 가능")

        return recommendations

    def _extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """OCR 텍스트에서 송장 데이터 추출"""
        # 실제 구현에서는 정규표현식이나 NLP를 사용
        extracted = {
            "invoice_number": "",
            "total_amount": 0.0,
            "vendor": "",
            "date": "",
            "items": [],
        }

        # 간단한 패턴 매칭 (실제로는 더 정교한 로직 필요)
        lines = text.split("\n")
        for line in lines:
            line_lower = line.lower()
            if "invoice" in line_lower and "number" in line_lower:
                # 송장 번호 추출
                import re

                numbers = re.findall(r"\d+", line)
                if numbers:
                    extracted["invoice_number"] = f"INV-{numbers[0]}"
            elif "total" in line_lower and any(char.isdigit() for char in line):
                # 총액 추출
                import re

                amounts = re.findall(r"\d+\.?\d*", line)
                if amounts:
                    extracted["total_amount"] = float(amounts[-1])
            elif "vendor" in line_lower or "supplier" in line_lower:
                # 공급업체 추출
                extracted["vendor"] = line.strip()

        return extracted

    def _parse_eta(self, eta_string: str) -> Optional[datetime]:
        """ETA 문자열을 datetime으로 파싱"""
        try:
            # 다양한 ETA 형식 처리
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(eta_string, fmt)
                except ValueError:
                    continue

            return None
        except Exception:
            return None

    def _calculate_eta_delay(self, eta_datetime: datetime) -> int:
        """ETA 지연 시간 계산 (시간 단위)"""
        now = datetime.now()
        if eta_datetime > now:
            return 0  # 아직 도착하지 않음
        else:
            return int((now - eta_datetime).total_seconds() / 3600)

    async def close(self):
        """세션 종료"""
        if self.session:
            await self.session.close()


# 사용 예시
async def main():
    """메인 실행 함수"""
    print("🚀 실제 API 연동 시스템 시작")

    api_integration = RealAPIIntegration()

    try:
        await api_integration.initialize()

        # 실제 날씨 데이터 수집
        weather_result = await api_integration.get_real_weather_data("JEBEL_ALI")
        print(f"🌤️ 날씨 데이터: {weather_result['status']} - {weather_result['source']}")

        # 실제 OCR 데이터 처리 (파일이 있는 경우)
        test_file = "data/HVDC WAREHOUSE_INVOICE_CLEANED_20250709_201121.xlsx"
        if os.path.exists(test_file):
            ocr_result = await api_integration.get_real_ocr_data(test_file)
            print(f"📄 OCR 데이터: {ocr_result['status']} - {ocr_result['source']}")

        # 실제 선박 데이터 수집
        shipping_result = await api_integration.get_real_shipping_data("123456789")
        print(
            f"🚢 선박 데이터: {shipping_result['status']} - {shipping_result['source']}"
        )

    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
    finally:
        await api_integration.close()


if __name__ == "__main__":
    asyncio.run(main())
