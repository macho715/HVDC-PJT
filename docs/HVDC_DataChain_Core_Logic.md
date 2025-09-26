# HVDC DataChain 핵심 로직 문서

## 🧠 핵심 로직 아키텍처

### 📊 데이터 처리 파이프라인

```
입력 데이터 → 정규화 → DataChain 처리 → 검증 → 출력
    ↓           ↓           ↓           ↓       ↓
Excel 파일   컬럼명/타입   벤더/장비/   품질검증  Excel 리포트
            정규화      이용률계산
```

## 🔧 핵심 함수 분석

### 1. 데이터 정규화 함수들

#### `normalize_column_names(df)`
**목적**: DataChain 호환성을 위한 컬럼명 정규화

**핵심 로직**:
```python
def clean_column_name(col):
    # 특수문자 제거 및 언더스코어로 대체
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
    # 연속된 언더스코어를 하나로
    cleaned = re.sub(r'_+', '_', cleaned)
    # 숫자로 시작하면 'col_' 추가
    if cleaned and cleaned[0].isdigit():
        cleaned = 'col_' + cleaned
    return cleaned.lower()
```

**처리 예시**:
- `'HVDC CODE'` → `'hvdc_code'`
- `'Shipment Invoice No.'` → `'shipment_invoice_no'`
- `'1. No.'` → `'col_1_no'`

#### `convert_datetime_columns(df)`
**목적**: 날짜 컬럼을 문자열로 변환

**핵심 로직**:
```python
if pd.api.types.is_datetime64_any_dtype(df_converted[col]):
    df_converted[col] = df_converted[col].dt.strftime('%Y-%m-%d').fillna('')
```

#### `convert_all_to_string(df)`
**목적**: 모든 데이터를 문자열로 변환하여 DataChain 호환성 확보

**핵심 로직**:
```python
# NaN 값을 빈 문자열로 변환
df_string[col] = df_string[col].fillna('')
# 모든 값을 문자열로 변환
df_string[col] = df_string[col].astype(str)
# 'nan' 문자열을 빈 문자열로 변환
df_string[col] = df_string[col].replace('nan', '')
```

### 2. 비즈니스 로직 함수들

#### `normalize_vendor(hvdc_code)`
**목적**: HVDC CODE에서 벤더 정규화

**핵심 로직**:
```python
hvdc_str = str(hvdc_code).upper()
if 'HE' in hvdc_str:  # HE = HITACHI Equipment
    return 'HITACHI'
elif 'SIM' in hvdc_str:  # SIM = SIEMENS
    return 'SIEMENS'
else:
    return 'OTHER'
```

**HVDC CODE 패턴**:
- `HVDC-ADOPT-HE-LOC-0008` → HITACHI
- `HVDC-ADOPT-SIM-0084` → SIEMENS

#### `classify_equipment(equipment_type)`
**목적**: 장비 유형 자동 분류

**핵심 로직**:
```python
equipment_str = str(equipment_type).upper()
if 'HEAVY' in equipment_str or 'HE' in equipment_str:
    return 'HEAVY_EQUIPMENT'
elif 'ELECTRICAL' in equipment_str or 'ELEC' in equipment_str:
    return 'ELECTRICAL_EQUIPMENT'
else:
    return 'GENERAL_EQUIPMENT'
```

#### `calculate_utilization(capacity, current_stock)`
**목적**: 실시간 이용률 계산

**핵심 로직**:
```python
try:
    capacity_val = float(capacity) if capacity != '' else 0
    current_stock_val = float(current_stock) if current_stock != '' else 0
    if capacity_val == 0:
        return '0.0'
    utilization = (current_stock_val / capacity_val) * 100
    return str(min(utilization, 100.0))  # 최대 100%로 제한
except:
    return '0.0'
```

### 3. DataChain 파이프라인 구성

#### 기본 체이닝 패턴
```python
processed_chain = (chain
    .map(normalized_vendor=normalize_vendor, params=['hvdc_code'])
    .map(equipment_class=classify_equipment, params=['description'])
    .map(utilization_rate=calculate_utilization, params=['cbm', 'n_w_kgs'])
)
```

#### 통합 분석 체이닝
```python
processed_chain = (chain
    .map(source_analysis=data_source_analysis, params=['data_source'])
    .map(record_type=record_type_classification, params=['data_source'])
    .map(processed_at=processing_timestamp, params=['data_source'])
)
```

## 📈 데이터 플로우 상세

### 1. HITACHI 데이터 처리 플로우
```
HVDC_WAREHOUSE_HITACHI_CLEANED_*.xlsx
    ↓
컬럼명 정규화 (62개 → 62개)
    ↓
날짜 컬럼 변환
    ↓
문자열 변환
    ↓
DataChain 파이프라인
    ↓
벤더 정규화 (HITACHI: 5,552건)
    ↓
장비 분류 (일반: 5,455, 중장비: 91, 전기: 6)
    ↓
이용률 계산 (평균: 100.00%)
    ↓
Excel 출력
```

### 2. SIEMENS 데이터 처리 플로우
```
HVDC_WAREHOUSE_SIMENSE_CLEANED_*.xlsx
    ↓
컬럼명 정규화 (58개 → 58개)
    ↓
날짜 컬럼 변환
    ↓
문자열 변환
    ↓
DataChain 파이프라인
    ↓
벤더 정규화 (SIEMENS: 2,227건)
    ↓
장비 분류 (일반: 2,177, 중장비: 42, 전기: 8)
    ↓
이용률 계산 (평균: 92.11%)
    ↓
Excel 출력
```

### 3. 송장 데이터 처리 플로우
```
HVDC_WAREHOUSE_INVOICE_CLEANED_*.xlsx
    ↓
컬럼명 정규화 (32개 → 32개)
    ↓
날짜 컬럼 변환
    ↓
문자열 변환
    ↓
DataChain 파이프라인
    ↓
금액 검증 (유효: 465건)
    ↓
송장 분류 (기타: 465건)
    ↓
세금 계산 (총액: 3,204,916.34)
    ↓
Excel 출력
```

## 🔍 검증 로직

### 1. 기본 검증
```python
# 데이터 존재 확인
assert len(result) > 0, "처리된 데이터가 없습니다"

# 필수 컬럼 확인
assert 'normalized_vendor' in result.columns, "벤더 정규화 컬럼이 없습니다"
assert 'equipment_class' in result.columns, "장비 분류 컬럼이 없습니다"
assert 'utilization_rate' in result.columns, "이용률 컬럼이 없습니다"
```

### 2. 비즈니스 검증
```python
# 벤더별 데이터 확인
hitachi_count = len(result[result['normalized_vendor'] == 'HITACHI'])
assert hitachi_count > 0, "HITACHI 데이터가 처리되지 않았습니다"

# 통계 검증
utilization_values = pd.to_numeric(result['utilization_rate'], errors='coerce')
avg_utilization = utilization_values.mean()
assert 0 <= avg_utilization <= 100, "이용률이 범위를 벗어났습니다"
```

### 3. 파일 출력 검증
```python
# 파일 존재 확인
assert output_file.exists(), "출력 파일이 생성되지 않았습니다"
assert report_file.exists(), "리포트 파일이 생성되지 않았습니다"

# 파일 크기 확인
file_size = output_file.stat().st_size
assert file_size > 0, "출력 파일이 비어있습니다"
```

## 🎯 핵심 알고리즘

### 1. 벤더 식별 알고리즘
```
입력: HVDC CODE 문자열
출력: 벤더명 (HITACHI/SIEMENS/OTHER)

1. 문자열을 대문자로 변환
2. 'HE' 포함 여부 확인 → HITACHI
3. 'SIM' 포함 여부 확인 → SIEMENS
4. 기타 → OTHER
```

### 2. 장비 분류 알고리즘
```
입력: 장비 설명 문자열
출력: 장비 유형 (HEAVY/ELECTRICAL/GENERAL)

1. 문자열을 대문자로 변환
2. 'HEAVY' 또는 'HE' 포함 → HEAVY_EQUIPMENT
3. 'ELECTRICAL' 또는 'ELEC' 포함 → ELECTRICAL_EQUIPMENT
4. 기타 → GENERAL_EQUIPMENT
```

### 3. 이용률 계산 알고리즘
```
입력: 용량(capacity), 현재재고(current_stock)
출력: 이용률(0-100%)

1. 입력값 유효성 검사
2. 용량이 0인지 확인 → 0% 반환
3. 이용률 = (현재재고 / 용량) × 100
4. 최대값 100%로 제한
5. 문자열로 변환하여 반환
```

## 🔧 확장 가능한 구조

### 새로운 벤더 추가
```python
def normalize_vendor(hvdc_code):
    hvdc_str = str(hvdc_code).upper()
    vendor_patterns = {
        'HE': 'HITACHI',
        'SIM': 'SIEMENS',
        'NEW': 'NEW_VENDOR',  # 새로운 패턴 추가
    }
    
    for pattern, vendor in vendor_patterns.items():
        if pattern in hvdc_str:
            return vendor
    return 'OTHER'
```

### 새로운 장비 유형 추가
```python
def classify_equipment(equipment_type):
    equipment_str = str(equipment_type).upper()
    equipment_patterns = {
        ('HEAVY', 'HE'): 'HEAVY_EQUIPMENT',
        ('ELECTRICAL', 'ELEC'): 'ELECTRICAL_EQUIPMENT',
        ('NEW_TYPE',): 'NEW_EQUIPMENT_TYPE',  # 새로운 유형 추가
    }
    
    for patterns, equipment_class in equipment_patterns.items():
        if any(pattern in equipment_str for pattern in patterns):
            return equipment_class
    return 'GENERAL_EQUIPMENT'
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-07-18  
**작성자**: MACHO-GPT v3.4-mini 