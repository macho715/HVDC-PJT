# HVDC 핵심 로직 가이드
## Samsung C&T Logistics | ADNOC·DSV Partnership

---

## 📋 목차
1. [개요](#개요)
2. [Flow Code 로직](#flow-code-로직)
3. [입고/출고 로직](#입고출고-로직)
4. [Heat-Stow 최적화](#heat-stow-최적화)
5. [Weather-Tie 분석](#weather-tie-분석)
6. [OCR 처리 로직](#ocr-처리-로직)
7. [KPI 계산 로직](#kpi-계산-로직)
8. [데이터 검증 로직](#데이터-검증-로직)
9. [성능 최적화](#성능-최적화)
10. [오류 처리](#오류-처리)

---

## 🎯 개요

### 핵심 로직의 중요성
HVDC 프로젝트의 핵심 로직은 물류 시스템의 정확성과 효율성을 보장하는 기반입니다. 각 로직은 TDD 원칙에 따라 개발되었으며, 95% 이상의 정확도를 목표로 합니다.

### 주요 특징
- **TDD 기반 개발**: 테스트 우선 개발로 안정성 보장
- **비동기 처리**: 고성능 비동기 처리로 동시성 확보
- **오류 복구**: 자동 오류 감지 및 복구 메커니즘
- **확장성**: 모듈화된 설계로 유지보수성 향상

---

## 🔄 Flow Code 로직

### Flow Code 정의
Flow Code는 물류 흐름에서 창고 경유 횟수를 나타내는 핵심 지표입니다.

### Flow Code 계산 로직
```python
def calculate_flow_code(warehouse_data: pd.DataFrame) -> pd.DataFrame:
    """
    Flow Code 계산 로직
    
    Flow Code 규칙:
    - 0: Port → Site 직접 (창고 경유 없음)
    - 1: 창고 1개 경유
    - 2: 창고 2개 경유  
    - 3: 창고 3개 이상 경유
    """
    
    def count_warehouse_visits(row):
        """창고 방문 횟수 계산"""
        warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 
            'DSV MZP', 'AAA Storage'
        ]
        
        visit_count = 0
        for warehouse in warehouse_columns:
            if warehouse in row and pd.notna(row[warehouse]) and row[warehouse] > 0:
                visit_count += 1
        
        return visit_count
    
    # Flow Code 계산
    warehouse_data['Flow_Code'] = warehouse_data.apply(count_warehouse_visits, axis=1)
    
    # Flow Code 검증
    warehouse_data['Flow_Code_Valid'] = warehouse_data['Flow_Code'].between(0, 3)
    
    return warehouse_data
```

### Flow Code 검증 로직
```python
def validate_flow_code(flow_code: int, warehouse_visits: List[str]) -> bool:
    """
    Flow Code 검증 로직
    
    Args:
        flow_code: 계산된 Flow Code
        warehouse_visits: 실제 창고 방문 목록
    
    Returns:
        bool: Flow Code가 유효한지 여부
    """
    
    # Flow Code 범위 검증
    if not (0 <= flow_code <= 3):
        return False
    
    # 창고 방문 횟수와 Flow Code 일치 검증
    actual_visits = len([w for w in warehouse_visits if w])
    if flow_code != actual_visits:
        return False
    
    return True
```

### Flow Code 통계 분석
```python
def analyze_flow_code_distribution(warehouse_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Flow Code 분포 분석
    
    Returns:
        Dict: Flow Code별 통계 정보
    """
    
    flow_stats = warehouse_data['Flow_Code'].value_counts().sort_index()
    
    analysis = {
        'total_records': len(warehouse_data),
        'flow_code_distribution': flow_stats.to_dict(),
        'average_flow_code': warehouse_data['Flow_Code'].mean(),
        'most_common_flow': flow_stats.idxmax(),
        'efficiency_score': calculate_efficiency_score(warehouse_data)
    }
    
    return analysis
```

---

## 📦 입고/출고 로직

### 입고 로직
```python
class InboundLogic:
    """입고 처리 로직"""
    
    def __init__(self):
        self.warehouse_priority = {
            'DSV Indoor': 1,      # 최우선
            'DSV Outdoor': 2,     # 2순위
            'DSV Al Markaz': 3,   # 3순위
            'DSV MZP': 4,         # 4순위
            'AAA Storage': 5      # 5순위
        }
    
    def determine_final_location(self, item_data: Dict[str, Any]) -> str:
        """
        최종 입고 위치 결정 로직
        
        Args:
            item_data: 아이템 데이터
            
        Returns:
            str: 최종 입고 위치
        """
        
        # 1. 상태 기반 위치 결정
        status = item_data.get('Status', '').upper()
        
        if 'PRE-ARRIVAL' in status:
            return 'Pre-Arrival'
        
        if 'IN TRANSIT' in status:
            return 'In Transit'
        
        # 2. 창고 우선순위 기반 위치 결정
        for warehouse, priority in sorted(self.warehouse_priority.items(), key=lambda x: x[1]):
            if item_data.get(warehouse, 0) > 0:
                return warehouse
        
        # 3. 기본값 (DSV Indoor)
        return 'DSV Indoor'
    
    def calculate_inbound_metrics(self, inbound_data: pd.DataFrame) -> Dict[str, Any]:
        """
        입고 지표 계산
        
        Args:
            inbound_data: 입고 데이터
            
        Returns:
            Dict: 입고 지표
        """
        
        metrics = {
            'total_inbound': len(inbound_data),
            'warehouse_distribution': inbound_data['Final_Location'].value_counts().to_dict(),
            'average_processing_time': self.calculate_avg_processing_time(inbound_data),
            'efficiency_score': self.calculate_efficiency_score(inbound_data)
        }
        
        return metrics
```

### 출고 로직
```python
class OutboundLogic:
    """출고 처리 로직"""
    
    def __init__(self):
        self.site_priority = {
            'Site A': 1,
            'Site B': 2,
            'Site C': 3
        }
    
    def determine_outbound_route(self, item_data: Dict[str, Any]) -> List[str]:
        """
        출고 경로 결정 로직
        
        Args:
            item_data: 아이템 데이터
            
        Returns:
            List[str]: 출고 경로
        """
        
        route = []
        current_location = item_data.get('Current_Location', 'DSV Indoor')
        destination = item_data.get('Destination', 'Site A')
        
        # 1. 현재 위치에서 목적지까지 경로 계산
        if current_location != destination:
            route.append(current_location)
            
            # 중간 창고 경유 여부 결정
            if self.needs_warehouse_transfer(current_location, destination):
                intermediate_warehouse = self.select_intermediate_warehouse(current_location, destination)
                route.append(intermediate_warehouse)
            
            route.append(destination)
        
        return route
    
    def needs_warehouse_transfer(self, source: str, destination: str) -> bool:
        """창고 전송 필요 여부 판단"""
        
        # 같은 창고 내 이동은 전송 불필요
        if source == destination:
            return False
        
        # 사이트 간 이동은 전송 필요
        if 'Site' in source and 'Site' in destination:
            return True
        
        return False
```

---

## 🔥 Heat-Stow 최적화

### Heat-Stow 알고리즘
```python
class HeatStowOptimizer:
    """Heat-Stow 최적화 알고리즘"""
    
    def __init__(self, pressure_limit: float = 4.0):
        self.pressure_limit = pressure_limit  # t/m²
        self.thermal_variance_threshold = 0.1
        self.position_quality_weight = 0.6
        self.thermal_weight = 0.4
    
    def optimize_stowage(self, containers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        컨테이너 적재 최적화
        
        Args:
            containers: 컨테이너 목록
            
        Returns:
            Dict: 최적화 결과
        """
        
        # 1. 컨테이너 분류 및 우선순위 설정
        classified_containers = self.classify_containers(containers)
        
        # 2. 위치별 압력 계산
        pressure_map = self.calculate_pressure_distribution(classified_containers)
        
        # 3. 열 분포 최적화
        thermal_optimized = self.optimize_thermal_distribution(classified_containers)
        
        # 4. 최종 배치 결정
        final_layout = self.determine_final_layout(thermal_optimized, pressure_map)
        
        return {
            'layout': final_layout,
            'pressure_analysis': self.analyze_pressure(final_layout),
            'thermal_analysis': self.analyze_thermal_distribution(final_layout),
            'efficiency_score': self.calculate_efficiency_score(final_layout)
        }
    
    def classify_containers(self, containers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """컨테이너 분류"""
        
        classified = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        for container in containers:
            priority = self.calculate_priority(container)
            if priority >= 0.8:
                classified['high_priority'].append(container)
            elif priority >= 0.5:
                classified['medium_priority'].append(container)
            else:
                classified['low_priority'].append(container)
        
        return classified
    
    def calculate_priority(self, container: Dict[str, Any]) -> float:
        """컨테이너 우선순위 계산"""
        
        # 크기 기반 우선순위 (큰 컨테이너 우선)
        size_priority = min(container.get('volume', 0) / 100, 1.0)
        
        # 무게 기반 우선순위 (무거운 컨테이너 우선)
        weight_priority = min(container.get('weight', 0) / 1000, 1.0)
        
        # 온도 민감도 기반 우선순위
        temp_sensitivity = container.get('temperature_sensitivity', 0)
        temp_priority = 1.0 - temp_sensitivity  # 낮은 온도 민감도가 높은 우선순위
        
        # 종합 우선순위 계산
        priority = (size_priority * 0.4 + weight_priority * 0.4 + temp_priority * 0.2)
        
        return priority
    
    def validate_pressure_limit(self, layout: List[Dict[str, Any]]) -> bool:
        """압력 한계 검증"""
        
        for position in layout:
            pressure = position.get('pressure', 0)
            if pressure > self.pressure_limit:
                return False
        
        return True
```

### 압력 계산 로직
```python
def calculate_pressure(container_data: Dict[str, Any], area: float) -> float:
    """
    압력 계산 로직
    
    Args:
        container_data: 컨테이너 데이터
        area: 면적 (m²)
        
    Returns:
        float: 압력 (t/m²)
    """
    
    weight = container_data.get('weight', 0)  # kg
    area_m2 = area  # m²
    
    # kg을 ton으로 변환 후 압력 계산
    pressure = (weight / 1000) / area_m2
    
    return pressure
```

---

## 🌤️ Weather-Tie 분석

### Weather-Tie 알고리즘
```python
class WeatherTieAnalyzer:
    """Weather-Tie 분석 알고리즘"""
    
    def __init__(self):
        self.weather_impact_thresholds = {
            'storm': 0.8,      # 폭풍 임계값
            'high_wind': 0.6,  # 강풍 임계값
            'rain': 0.4,       # 비 임계값
            'fog': 0.3         # 안개 임계값
        }
        
        self.delay_multipliers = {
            'storm': 2.0,      # 폭풍 시 2배 지연
            'high_wind': 1.5,  # 강풍 시 1.5배 지연
            'rain': 1.2,       # 비 시 1.2배 지연
            'fog': 1.1         # 안개 시 1.1배 지연
        }
    
    async def analyze_weather_impact(self, weather_data: Dict[str, Any], eta_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기상 영향 분석
        
        Args:
            weather_data: 기상 데이터
            eta_data: ETA 데이터
            
        Returns:
            Dict: 기상 영향 분석 결과
        """
        
        # 1. 기상 조건 분석
        weather_condition = self.classify_weather_condition(weather_data)
        
        # 2. 지연 시간 계산
        delay_hours = self.calculate_delay_hours(weather_condition, eta_data)
        
        # 3. ETA 업데이트
        updated_eta = self.update_eta(eta_data, delay_hours)
        
        # 4. 경로 최적화
        optimized_route = await self.optimize_route_for_weather(weather_condition, eta_data)
        
        return {
            'weather_condition': weather_condition,
            'delay_hours': delay_hours,
            'updated_eta': updated_eta,
            'optimized_route': optimized_route,
            'risk_level': self.calculate_risk_level(weather_condition),
            'recommendations': self.generate_recommendations(weather_condition, delay_hours)
        }
    
    def classify_weather_condition(self, weather_data: Dict[str, Any]) -> str:
        """기상 조건 분류"""
        
        wind_speed = weather_data.get('wind_speed', 0)
        precipitation = weather_data.get('precipitation', 0)
        visibility = weather_data.get('visibility', 10)
        
        # 폭풍 조건
        if wind_speed > 25 or precipitation > 50:
            return 'storm'
        
        # 강풍 조건
        if wind_speed > 15:
            return 'high_wind'
        
        # 비 조건
        if precipitation > 10:
            return 'rain'
        
        # 안개 조건
        if visibility < 5:
            return 'fog'
        
        return 'normal'
    
    def calculate_delay_hours(self, weather_condition: str, eta_data: Dict[str, Any]) -> float:
        """지연 시간 계산"""
        
        base_delay = eta_data.get('base_delay', 0)
        multiplier = self.delay_multipliers.get(weather_condition, 1.0)
        
        delay_hours = base_delay * multiplier
        
        return delay_hours
    
    async def optimize_route_for_weather(self, weather_condition: str, eta_data: Dict[str, Any]) -> List[str]:
        """기상 조건에 따른 경로 최적화"""
        
        if weather_condition == 'storm':
            # 폭풍 시 안전한 대안 경로 선택
            return await self.find_safe_alternative_route(eta_data)
        
        elif weather_condition == 'high_wind':
            # 강풍 시 바람이 적은 경로 선택
            return await self.find_wind_sheltered_route(eta_data)
        
        else:
            # 일반적인 최적 경로
            return await self.find_optimal_route(eta_data)
```

---

## 📄 OCR 처리 로직

### OCR 처리 알고리즘
```python
class OCRProcessor:
    """OCR 처리 알고리즘"""
    
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold
        self.fallback_mode = "ZERO"
    
    async def process_invoice(self, image_path: str) -> Dict[str, Any]:
        """
        송장 OCR 처리
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            Dict: OCR 처리 결과
        """
        
        try:
            # 1. 이미지 전처리
            processed_image = await self.preprocess_image(image_path)
            
            # 2. OCR 실행
            ocr_result = await self.extract_text(processed_image)
            
            # 3. 신뢰도 검증
            if ocr_result['confidence'] < self.confidence_threshold:
                return await self.handle_low_confidence(ocr_result)
            
            # 4. 데이터 추출 및 검증
            extracted_data = await self.extract_invoice_data(ocr_result)
            
            # 5. FANR/MOIAT 규정 준수 검증
            compliance_result = await self.validate_compliance(extracted_data)
            
            return {
                'status': 'SUCCESS',
                'confidence': ocr_result['confidence'],
                'extracted_data': extracted_data,
                'compliance': compliance_result,
                'mode': 'PRIME'
            }
            
        except Exception as e:
            return await self.handle_ocr_error(e)
    
    async def extract_invoice_data(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """송장 데이터 추출"""
        
        extracted_data = {
            'invoice_number': None,
            'amount': None,
            'hs_code': None,
            'vendor': None,
            'date': None
        }
        
        text = ocr_result.get('text', '')
        
        # 송장 번호 추출
        invoice_pattern = r'INV[-\s]?(\d+)'
        invoice_match = re.search(invoice_pattern, text, re.IGNORECASE)
        if invoice_match:
            extracted_data['invoice_number'] = invoice_match.group(1)
        
        # 금액 추출
        amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        amount_matches = re.findall(amount_pattern, text)
        if amount_matches:
            # 가장 큰 금액을 송장 금액으로 간주
            amounts = [float(amt.replace(',', '')) for amt in amount_matches]
            extracted_data['amount'] = max(amounts)
        
        # HS 코드 추출
        hs_pattern = r'(\d{4}\.\d{2}\.\d{2})'
        hs_match = re.search(hs_pattern, text)
        if hs_match:
            extracted_data['hs_code'] = hs_match.group(1)
        
        return extracted_data
    
    async def handle_low_confidence(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """낮은 신뢰도 처리"""
        
        return {
            'status': 'FALLBACK',
            'confidence': ocr_result['confidence'],
            'mode': self.fallback_mode,
            'error_message': f"OCR 신뢰도가 임계값({self.confidence_threshold}) 미만입니다.",
            'recommendation': '수동 검토가 필요합니다.',
            'original_data': ocr_result
        }
```

---

## 📊 KPI 계산 로직

### KPI 계산 알고리즘
```python
class KPICalculator:
    """KPI 계산 알고리즘"""
    
    def __init__(self):
        self.kpi_thresholds = {
            'utilization': 85,      # 창고 활용률 임계값 (%)
            'throughput': 90,       # 처리량 임계값 (%)
            'accuracy': 95,         # 정확도 임계값 (%)
            'eta_delay': 24,        # ETA 지연 임계값 (시간)
            'rate_change': 10       # 요율 변화 임계값 (%)
        }
    
    def calculate_warehouse_kpis(self, warehouse_data: pd.DataFrame) -> Dict[str, Any]:
        """
        창고 KPI 계산
        
        Args:
            warehouse_data: 창고 데이터
            
        Returns:
            Dict: KPI 계산 결과
        """
        
        kpis = {
            'utilization': self.calculate_utilization(warehouse_data),
            'throughput': self.calculate_throughput(warehouse_data),
            'accuracy': self.calculate_accuracy(warehouse_data),
            'efficiency': self.calculate_efficiency(warehouse_data),
            'cost_per_unit': self.calculate_cost_per_unit(warehouse_data)
        }
        
        # 임계값 대비 성과 분석
        performance_analysis = self.analyze_performance(kpis)
        
        return {
            'kpis': kpis,
            'performance_analysis': performance_analysis,
            'recommendations': self.generate_recommendations(performance_analysis)
        }
    
    def calculate_utilization(self, warehouse_data: pd.DataFrame) -> float:
        """창고 활용률 계산"""
        
        total_capacity = warehouse_data['capacity'].sum()
        used_capacity = warehouse_data['used_capacity'].sum()
        
        utilization = (used_capacity / total_capacity) * 100 if total_capacity > 0 else 0
        
        return round(utilization, 2)
    
    def calculate_throughput(self, warehouse_data: pd.DataFrame) -> float:
        """처리량 계산"""
        
        total_processed = warehouse_data['processed_items'].sum()
        total_received = warehouse_data['received_items'].sum()
        
        throughput = (total_processed / total_received) * 100 if total_received > 0 else 0
        
        return round(throughput, 2)
    
    def check_auto_triggers(self, kpi_data: Dict[str, Any]) -> List[str]:
        """자동 트리거 조건 확인"""
        
        triggers = []
        
        # 창고 활용률 임계값 초과
        if kpi_data.get('utilization', 0) > self.kpi_thresholds['utilization']:
            triggers.append('/warehouse_optimization')
        
        # ETA 지연 임계값 초과
        if kpi_data.get('eta_delay', 0) > self.kpi_thresholds['eta_delay']:
            triggers.append('/weather_tie')
        
        # 요율 변화 임계값 초과
        if abs(kpi_data.get('rate_change', 0)) > self.kpi_thresholds['rate_change']:
            triggers.append('/market_update')
        
        return triggers
```

---

## ✅ 데이터 검증 로직

### 데이터 검증 알고리즘
```python
class DataValidator:
    """데이터 검증 알고리즘"""
    
    def __init__(self):
        self.validation_rules = {
            'required_fields': ['invoice_number', 'amount', 'vendor'],
            'numeric_fields': ['amount', 'weight', 'volume'],
            'date_fields': ['invoice_date', 'eta_date'],
            'email_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone_pattern': r'^\+?[\d\s\-\(\)]+$'
        }
    
    def validate_invoice_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        송장 데이터 검증
        
        Args:
            invoice_data: 송장 데이터
            
        Returns:
            Dict: 검증 결과
        """
        
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'confidence_score': 1.0
        }
        
        # 1. 필수 필드 검증
        missing_fields = self.check_required_fields(invoice_data)
        if missing_fields:
            validation_result['errors'].extend(missing_fields)
            validation_result['is_valid'] = False
        
        # 2. 데이터 타입 검증
        type_errors = self.validate_data_types(invoice_data)
        if type_errors:
            validation_result['errors'].extend(type_errors)
            validation_result['is_valid'] = False
        
        # 3. 데이터 범위 검증
        range_warnings = self.validate_data_ranges(invoice_data)
        if range_warnings:
            validation_result['warnings'].extend(range_warnings)
        
        # 4. 비즈니스 규칙 검증
        business_errors = self.validate_business_rules(invoice_data)
        if business_errors:
            validation_result['errors'].extend(business_errors)
            validation_result['is_valid'] = False
        
        # 5. 신뢰도 점수 계산
        validation_result['confidence_score'] = self.calculate_confidence_score(validation_result)
        
        return validation_result
    
    def check_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """필수 필드 검증"""
        
        missing_fields = []
        for field in self.validation_rules['required_fields']:
            if field not in data or pd.isna(data[field]) or data[field] == '':
                missing_fields.append(f"필수 필드 누락: {field}")
        
        return missing_fields
    
    def validate_data_types(self, data: Dict[str, Any]) -> List[str]:
        """데이터 타입 검증"""
        
        type_errors = []
        
        # 숫자 필드 검증
        for field in self.validation_rules['numeric_fields']:
            if field in data and data[field] is not None:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    type_errors.append(f"숫자 필드 형식 오류: {field}")
        
        # 날짜 필드 검증
        for field in self.validation_rules['date_fields']:
            if field in data and data[field] is not None:
                if not self.is_valid_date(data[field]):
                    type_errors.append(f"날짜 필드 형식 오류: {field}")
        
        return type_errors
    
    def calculate_confidence_score(self, validation_result: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        
        base_score = 1.0
        
        # 오류당 0.1점 감점
        error_penalty = len(validation_result['errors']) * 0.1
        
        # 경고당 0.05점 감점
        warning_penalty = len(validation_result['warnings']) * 0.05
        
        confidence_score = max(0.0, base_score - error_penalty - warning_penalty)
        
        return round(confidence_score, 2)
```

---

## ⚡ 성능 최적화

### 캐싱 전략
```python
class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get(self, key: str) -> Any:
        """캐시에서 데이터 조회"""
        
        if key in self.cache:
            # 접근 횟수 증가
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """캐시에 데이터 저장"""
        
        # 캐시 크기 제한 확인
        if len(self.cache) >= self.max_size:
            self.evict_least_used()
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        self.access_count[key] = 0
    
    def evict_least_used(self) -> None:
        """LRU 정책으로 캐시 정리"""
        
        if not self.access_count:
            return
        
        # 가장 적게 사용된 항목 제거
        least_used_key = min(self.access_count.keys(), key=lambda k: self.access_count[k])
        del self.cache[least_used_key]
        del self.access_count[least_used_key]
```

### 비동기 처리 최적화
```python
class AsyncProcessor:
    """비동기 처리 최적화"""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.task_queue = asyncio.Queue()
    
    async def process_batch(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """배치 처리"""
        
        async def process_single_task(task):
            async with self.semaphore:
                return await self.execute_task(task)
        
        # 병렬 실행
        results = await asyncio.gather(*[process_single_task(task) for task in tasks])
        
        return results
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """단일 작업 실행"""
        
        start_time = time.time()
        
        try:
            result = await self.perform_task(task)
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'SUCCESS',
                'result': result,
                'execution_time': execution_time,
                'task_id': task.get('id')
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return {
                'status': 'ERROR',
                'error': str(e),
                'execution_time': execution_time,
                'task_id': task.get('id')
            }
```

---

## 🛡️ 오류 처리

### 오류 처리 전략
```python
class ErrorHandler:
    """오류 처리 관리자"""
    
    def __init__(self):
        self.error_counts = {}
        self.circuit_breaker_threshold = 5
        self.recovery_timeout = 60  # 초
    
    async def execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
        """재시도 메커니즘"""
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # 지수 백오프
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    def handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """오류 처리"""
        
        error_type = type(error).__name__
        error_key = f"{context}_{error_type}"
        
        # 오류 카운트 증가
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # 서킷 브레이커 확인
        if self.error_counts[error_key] >= self.circuit_breaker_threshold:
            return {
                'status': 'CIRCUIT_OPEN',
                'error': str(error),
                'context': context,
                'recommendation': '서킷 브레이커가 활성화되었습니다. 잠시 후 재시도하세요.'
            }
        
        return {
            'status': 'ERROR',
            'error': str(error),
            'context': context,
            'error_count': self.error_counts[error_key]
        }
    
    def reset_error_count(self, context: str) -> None:
        """오류 카운트 리셋"""
        
        keys_to_remove = [key for key in self.error_counts.keys() if key.startswith(context)]
        for key in keys_to_remove:
            del self.error_counts[key]
```

---

## 📚 참고 자료

### 문서
- [HVDC 프로젝트 전체 가이드](./HVDC_PROJECT_COMPREHENSIVE_GUIDE.md)
- [Context Engineering Integration 가이드](./HVDC_CONTEXT_ENGINEERING_INTEGRATION_GUIDE.md)
- [API 문서](./API_DOCUMENTATION.md)

### 코드 저장소
- **메인 로직**: `src/` 디렉토리
- **테스트 코드**: `tests/` 디렉토리
- **설정 파일**: `config/` 디렉토리

### 연락처
- **개발팀**: dev-team@samsumg-ct.com
- **운영팀**: ops-team@samsumg-ct.com
- **긴급 연락**: emergency@samsumg-ct.com

---

## 🔄 버전 히스토리

| 버전 | 날짜 | 변경사항 | 작성자 |
|------|------|----------|--------|
| 1.0.0 | 2025-01-17 | 초기 버전 작성 | MACHO-GPT |
| 1.1.0 | 2025-01-17 | 핵심 로직 상세 추가 | MACHO-GPT |
| 1.2.0 | 2025-01-17 | 성능 최적화 및 오류 처리 추가 | MACHO-GPT |

---

**© 2025 Samsung C&T Logistics. All rights reserved.** 