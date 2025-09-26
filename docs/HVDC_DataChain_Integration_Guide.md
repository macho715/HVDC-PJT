# HVDC DataChain 통합 가이드 문서

## 📋 개요

이 문서는 HVDC 프로젝트에서 DataChain 프레임워크를 활용한 실시간 물류 데이터 처리 시스템의 통합 가이드입니다.

### 🎯 목적
- 실제 HVDC 물류 데이터의 DataChain 파이프라인 처리
- 벤더별 데이터 정규화 및 분석
- 실시간 KPI 계산 및 리포트 생성
- MACHO-GPT 시스템과의 완전 통합

## 🏗️ 시스템 아키텍처

### 📊 데이터 플로우
```
HVDC Excel 데이터 → 정규화 → DataChain 파이프라인 → 분석 결과 → Excel 리포트
```

### 🔧 핵심 컴포넌트
1. **데이터 정규화 모듈**: 컬럼명, 타입, NaN 처리
2. **DataChain 파이프라인**: 벤더 정규화, 장비 분류, 이용률 계산
3. **통합 분석 엔진**: 다중 데이터소스 통합 처리
4. **리포트 생성기**: Excel 기반 분석 리포트 자동 생성

## 📁 파일 구조

```
HVDC_PJT/
├── data_cleaned/                          # 정제된 데이터
│   ├── HVDC_WAREHOUSE_HITACHI_CLEANED_*.xlsx
│   ├── HVDC_WAREHOUSE_SIMENSE_CLEANED_*.xlsx
│   └── HVDC_WAREHOUSE_INVOICE_CLEANED_*.xlsx
├── output/datachain_processed/            # 처리 결과
│   ├── hvdc_processed_data_*.xlsx
│   └── hvdc_processing_report_*.xlsx
└── docs/                                  # 문서
    └── HVDC_DataChain_Integration_Guide.md
```

## 🚀 사용 방법

### 1. 환경 설정
```bash
# DataChain 설치
pip install datachain

# 테스트 실행
cd datachain-main
python -m pytest HVDC_REAL_DATA_INTEGRATION.py -v -s
```

### 2. 개별 테스트 실행
```bash
# HITACHI 데이터 처리
python -m pytest HVDC_REAL_DATA_INTEGRATION.py::TestHVDCRealDataIntegration::test_hitachi_warehouse_data_processing -v -s

# SIEMENS 데이터 처리
python -m pytest HVDC_REAL_DATA_INTEGRATION.py::TestHVDCRealDataIntegration::test_siemens_warehouse_data_processing -v -s

# 송장 데이터 처리
python -m pytest HVDC_REAL_DATA_INTEGRATION.py::TestHVDCRealDataIntegration::test_invoice_data_processing -v -s

# 통합 데이터 분석
python -m pytest HVDC_REAL_DATA_INTEGRATION.py::TestHVDCRealDataIntegration::test_combined_data_analysis -v -s

# 데이터 내보내기
python -m pytest HVDC_REAL_DATA_INTEGRATION.py::TestHVDCRealDataIntegration::test_data_export_and_reporting -v -s
```

### 3. 결과 확인
```bash
cd HVDC_PJT
python check_datachain_report.py
```

## 📊 처리 결과 예시

### HITACHI 데이터 처리
- **총 레코드**: 5,552건
- **벤더 분포**: HITACHI 100%
- **장비 분류**: 일반장비 98.2%, 중장비 1.6%, 전기장비 0.1%
- **평균 이용률**: 100.00%

### SIEMENS 데이터 처리
- **총 레코드**: 2,227건
- **벤더 분포**: SIEMENS 100%
- **장비 분류**: 일반장비 97.8%, 중장비 1.9%, 전기장비 0.4%
- **평균 이용률**: 92.11%

### 송장 데이터 처리
- **총 레코드**: 465건
- **유효 송장**: 465건 (100%)
- **송장 분류**: 기타 100%
- **총 세금**: 3,204,916.34

## 🔧 커스터마이징

### 새로운 벤더 추가
```python
def normalize_vendor(hvdc_code):
    hvdc_str = str(hvdc_code).upper()
    if 'HE' in hvdc_str:
        return 'HITACHI'
    elif 'SIM' in hvdc_str:
        return 'SIEMENS'
    elif 'NEW_VENDOR' in hvdc_str:  # 새로운 벤더 추가
        return 'NEW_VENDOR'
    else:
        return 'OTHER'
```

### 새로운 장비 분류 추가
```python
def classify_equipment(equipment_type):
    equipment_str = str(equipment_type).upper()
    if 'NEW_TYPE' in equipment_str:  # 새로운 장비 유형 추가
        return 'NEW_EQUIPMENT_TYPE'
    # ... 기존 로직
```

## 📈 성능 최적화

### 메모리 사용량 최적화
- 대용량 데이터 처리 시 청크 단위 처리
- 불필요한 컬럼 제거
- 데이터 타입 최적화

### 처리 속도 개선
- 병렬 처리 활용
- 캐싱 메커니즘 도입
- 인덱스 최적화

## 🛠️ 문제 해결

### 일반적인 오류
1. **NaN 값 오류**: `convert_all_to_string()` 함수로 해결
2. **컬럼명 오류**: `normalize_column_names()` 함수로 해결
3. **타입 불일치**: 모든 반환값을 문자열로 통일

### 디버깅 방법
```python
# 데이터 상태 확인
print(f"데이터 형태: {df.shape}")
print(f"컬럼 목록: {list(df.columns)}")
print(f"데이터 타입: {df.dtypes}")

# NaN 값 확인
print(f"NaN 값 개수: {df.isna().sum().sum()}")
```

## 📋 체크리스트

### 배포 전 확인사항
- [ ] 모든 테스트 통과
- [ ] 데이터 파일 경로 확인
- [ ] 출력 디렉토리 권한 확인
- [ ] 메모리 사용량 확인
- [ ] 처리 시간 측정

### 운영 중 모니터링
- [ ] 처리 성공률 100% 유지
- [ ] 파일 생성 확인
- [ ] 리포트 내용 검증
- [ ] 성능 지표 추적

## 🔗 연관 문서

- [MACHO-GPT TDD 개발 지침](./MACHO_TDD_Guidelines.md)
- [HVDC 프로젝트 구조](./HVDC_Project_Structure.md)
- [DataChain API 문서](https://datachain.readthedocs.io/)

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-07-18  
**작성자**: MACHO-GPT v3.4-mini 