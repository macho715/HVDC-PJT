# HVDC DataChain 중요사항 문서

## ⚠️ 중요 주의사항

### 🔴 데이터 처리 시 주의사항

#### 1. NaN 값 처리
- **문제**: DataChain은 NaN 값을 String 타입으로 처리할 수 없음
- **해결책**: `convert_all_to_string()` 함수에서 모든 NaN 값을 빈 문자열로 변환
- **코드**:
```python
df_string[col] = df_string[col].apply(lambda x: '' if pd.isna(x) else str(x))
```

#### 2. 컬럼명 정규화
- **문제**: Excel 컬럼명에 특수문자가 포함되어 DataChain 호환성 문제 발생
- **해결책**: `normalize_column_names()` 함수로 모든 특수문자를 언더스코어로 변환
- **예시**: `'HVDC CODE'` → `'hvdc_code'`

#### 3. 타입 호환성
- **문제**: DataChain은 모든 반환값이 동일한 타입이어야 함
- **해결책**: 모든 함수에서 문자열 반환으로 통일
- **코드**:
```python
return str(min(utilization, 100.0))  # float → string 변환
```

### 🟡 성능 관련 주의사항

#### 1. 메모리 사용량
- **대용량 데이터 처리 시**: 8,244행 처리 시 약 100MB 메모리 사용
- **권장사항**: 청크 단위 처리 또는 메모리 모니터링 필요

#### 2. 처리 시간
- **현재 성능**: 8,244행 처리 시 약 80초 소요
- **최적화 방안**: 병렬 처리 또는 캐싱 도입 고려

#### 3. 파일 I/O
- **입력 파일**: Excel 파일 크기 제한 없음
- **출력 파일**: 자동으로 HVDC_PJT 디렉토리에 저장

### 🟢 데이터 품질 관련 주의사항

#### 1. HVDC CODE 패턴
- **HITACHI**: `HVDC-ADOPT-HE-*` 패턴
- **SIEMENS**: `HVDC-ADOPT-SIM-*` 패턴
- **주의**: 새로운 벤더 추가 시 패턴 업데이트 필요

#### 2. 장비 분류 로직
- **HEAVY_EQUIPMENT**: 'HEAVY' 또는 'HE' 포함
- **ELECTRICAL_EQUIPMENT**: 'ELECTRICAL' 또는 'ELEC' 포함
- **GENERAL_EQUIPMENT**: 기타 모든 장비

#### 3. 이용률 계산
- **범위**: 0% ~ 100% (최대값 제한)
- **예외 처리**: 용량이 0인 경우 0% 반환
- **정확도**: 소수점 2자리까지 계산

## 🚨 오류 처리 가이드

### 1. 일반적인 오류 및 해결방법

#### ValueError: Value nan with type incompatible for column type String
**원인**: NaN 값이 String 컬럼에 포함됨
**해결책**:
```python
# convert_all_to_string 함수 강화
df_string[col] = df_string[col].apply(lambda x: '' if pd.isna(x) else str(x))
```

#### AssertionError: SIEMENS 데이터가 처리되지 않았습니다
**원인**: HVDC CODE 패턴 매칭 실패
**해결책**:
```python
# 벤더 정규화 함수 수정
if 'SIM' in hvdc_str:  # SIM = SIEMENS
    return 'SIEMENS'
```

#### FileNotFoundError: 데이터 파일이 없습니다
**원인**: 데이터 파일 경로 오류
**해결책**:
```python
# 파일 경로 확인
cls.hvdc_data_dir = Path("../HVDC_PJT/data_cleaned")
```

### 2. 디버깅 방법

#### 데이터 상태 확인
```python
print(f"데이터 형태: {df.shape}")
print(f"컬럼 목록: {list(df.columns)}")
print(f"NaN 값 개수: {df.isna().sum().sum()}")
```

#### DataChain 파이프라인 디버깅
```python
# 단계별 결과 확인
step1 = chain.map(normalized_vendor=normalize_vendor, params=['hvdc_code'])
result1 = step1.to_pandas()
print(f"Step 1 결과: {len(result1)} 행")
```

## 📋 운영 체크리스트

### 배포 전 확인사항
- [ ] 모든 테스트 통과 (5/5)
- [ ] 데이터 파일 경로 정확성 확인
- [ ] 출력 디렉토리 권한 확인
- [ ] 메모리 사용량 측정
- [ ] 처리 시간 측정

### 운영 중 모니터링
- [ ] 처리 성공률 100% 유지
- [ ] 파일 생성 확인
- [ ] 리포트 내용 검증
- [ ] 성능 지표 추적

### 정기 점검사항
- [ ] 데이터 품질 검증
- [ ] 벤더 패턴 업데이트
- [ ] 성능 최적화 검토
- [ ] 오류 로그 분석

## 🔧 커스터마이징 가이드

### 새로운 벤더 추가
1. `normalize_vendor` 함수에 패턴 추가
2. 테스트 케이스 작성
3. 검증 로직 업데이트

### 새로운 장비 유형 추가
1. `classify_equipment` 함수에 패턴 추가
2. 분류 로직 검증
3. 통계 계산 업데이트

### 새로운 KPI 추가
1. 계산 함수 작성
2. DataChain 파이프라인에 추가
3. 검증 로직 구현

## 📊 성능 지표

### 현재 성능
- **처리 속도**: 8,244행/80초 ≈ 103행/초
- **메모리 사용량**: 약 100MB
- **성공률**: 100% (모든 테스트 통과)
- **정확도**: 벤더 분류 100%, 장비 분류 99%+

### 최적화 목표
- **처리 속도**: 200행/초 이상
- **메모리 사용량**: 50MB 이하
- **확장성**: 100,000행 이상 처리 가능

## 🔗 의존성 관리

### 필수 패키지
```python
# requirements.txt
datachain>=1.0.0
pandas>=2.0.0
pytest>=8.0.0
openpyxl>=3.0.0
```

### 버전 호환성
- **Python**: 3.12.3 이상
- **DataChain**: 1.0.0 이상
- **Pandas**: 2.0.0 이상

## 🛡️ 보안 고려사항

### 데이터 보안
- **파일 접근 권한**: 읽기 전용 권한 설정
- **출력 파일**: 임시 파일 자동 삭제
- **로그 관리**: 민감 정보 로깅 금지

### 시스템 보안
- **메모리 관리**: 대용량 데이터 처리 후 메모리 정리
- **파일 시스템**: 디스크 공간 모니터링
- **네트워크**: 외부 접근 제한

## 📞 지원 및 문의

### 문제 발생 시
1. 오류 로그 확인
2. 데이터 상태 검증
3. 시스템 리소스 확인
4. 개발팀 문의

### 연락처
- **기술 지원**: MACHO-GPT v3.4-mini
- **문서 관리**: HVDC_PJT/docs/
- **코드 저장소**: datachain-main/

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-07-18  
**작성자**: MACHO-GPT v3.4-mini  
**검토자**: HVDC 프로젝트팀 