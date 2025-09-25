# 📋 test_site_patch.py 주요 내용 및 함수 로직 가이드

## 🎯 개요
`test_site_patch.py`는 HVDC 프로젝트의 현장 재고 계산 로직이 패치 적용 후 올바르게 작동하는지 검증하는 테스트 스크립트입니다.

## 📊 주요 기능

### 1. 테스트 목적
- **패치 검증**: `create_site_monthly_sheet` 함수의 수정된 로직 검증
- **재고 정확성**: 4개 현장(AGI, DAS, MIR, SHU)의 재고 수량 정확성 확인
- **데이터 일관성**: 계산된 값과 기대값 간의 일치 여부 검증

### 2. 핵심 함수: `test_site_inventory()`

#### 2.1 초기화 및 데이터 준비
```python
reporter = HVDCExcelReporterFinal()
stats = reporter.calculate_warehouse_statistics()
site_sheet = reporter.create_site_monthly_sheet(stats)
```
- **HVDCExcelReporterFinal**: 메인 리포터 클래스 인스턴스 생성
- **calculate_warehouse_statistics()**: 웨어하우스 통계 계산
- **create_site_monthly_sheet()**: 현장별 월간 시트 생성

#### 2.2 결과 추출
```python
last_row = site_sheet.iloc[-1]  # Total 행 추출
```
- 시트의 마지막 행(Total 행)에서 각 현장의 재고 수량 추출

#### 2.3 기대값 정의
```python
expected = {
    'AGI': 85,      # AGI 현장 기대 재고
    'DAS': 1233,    # DAS 현장 기대 재고
    'MIR': 1254,    # MIR 현장 기대 재고
    'SHU': 1905,    # SHU 현장 기대 재고
    'TOTAL': 4477   # 전체 기대 재고
}
```

## 🔍 검증 로직

### 1. 개별 현장 검증
```python
agi_match = last_row['재고_AGI'] == expected['AGI']
das_match = last_row['재고_DAS'] == expected['DAS']
mir_match = last_row['재고_MIR'] == expected['MIR']
shu_match = last_row['재고_SHU'] == expected['SHU']
```

### 2. 전체 합계 검증
```python
total = last_row['재고_AGI'] + last_row['재고_DAS'] + last_row['재고_MIR'] + last_row['재고_SHU']
total_match = total == expected['TOTAL']
```

### 3. 종합 결과 판정
```python
all_match = agi_match and das_match and mir_match and shu_match and total_match
```

## 🐛 디버깅 기능

### 1. 내부 로직 복제
테스트는 `create_site_monthly_sheet` 함수의 내부 로직을 복제하여 디버깅 정보를 제공합니다:

```python
# 데이터 준비
df = stats['processed_data'].copy()
if "PKG_ID" not in df.columns:
    df["PKG_ID"] = df.index.astype(str)

# 현장 필터링
site_cols = ['AGI', 'DAS', 'MIR', 'SHU']
site_mask = df['Status_Location'].isin(site_cols)
site_rows = df[site_mask].copy()

# 날짜 처리
month_end = pd.Timestamp('2025-06-30')
row_idx = np.arange(len(site_rows))
col_idx = site_rows.columns.get_indexer(site_rows['Status_Location'])
date_vals = site_rows.to_numpy()[row_idx, col_idx]
site_rows['InvDate'] = pd.to_datetime(date_vals, errors='coerce')
site_rows = site_rows[site_rows['InvDate'] <= month_end]

# 최신 데이터 추출
latest = (site_rows.sort_values('InvDate').drop_duplicates('PKG_ID', keep='last'))
```

### 2. 디버그 정보 출력
```python
print(f"latest['Pkg'].sum(): {latest['Pkg'].sum()}")
print(f"latest['Pkg'].count(): {latest['Pkg'].count()}")
print(f"latest.shape: {latest.shape}")
```

## 📈 출력 형식

### 1. 현장별 재고 결과
```
📊 현장 재고 결과 (패치 적용):
  AGI: 85 PKG
  DAS: 1233 PKG
  MIR: 1254 PKG
  SHU: 1905 PKG
  총계: 4477 PKG
```

### 2. 기대값 표시
```
🎯 기대값:
  AGI: 85 PKG
  DAS: 1233 PKG
  MIR: 1254 PKG
  SHU: 1905 PKG
  총계: 4477 PKG
```

### 3. 검증 결과
```
✅ 검증 결과:
  AGI: ✅ 일치
  DAS: ✅ 일치
  MIR: ✅ 일치
  SHU: ✅ 일치
  총계: ✅ 일치

🎉 전체 결과: ✅ 모든 값 일치
```

## 🔧 패치 적용 사항

### 1. 주요 수정 내용
- **PKG 값 무시**: 재고 계산 시 PKG 값을 1로 취급하여 중복 계산 방지
- **날짜 필터링 제거**: 재고 계산에서 날짜 필터링을 제거하여 모든 현장 데이터 포함
- **Status_Location 기반**: 현장 구분을 Status_Location 컬럼 기준으로 수행

### 2. 계산 로직 개선
```python
# 기존: PKG 값으로 계산 (중복 발생)
inventory = df[df['Status_Location'] == site]['Pkg'].sum()

# 수정: 개별 아이템으로 계산 (PKG 값 무시)
inventory = len(df[df['Status_Location'] == site])
```

## 🚀 실행 방법

### 1. 직접 실행
```bash
python test_site_patch.py
```

### 2. 테스트 결과 해석
- **✅ 모든 값 일치**: 패치가 성공적으로 적용됨
- **❌ 일부 값 불일치**: 추가 디버깅 필요

## 📋 검증 체크리스트

- [ ] AGI 현장 재고: 85 PKG
- [ ] DAS 현장 재고: 1233 PKG  
- [ ] MIR 현장 재고: 1254 PKG
- [ ] SHU 현장 재고: 1905 PKG
- [ ] 전체 합계: 4477 PKG
- [ ] 모든 값 일치 확인

## 🔍 문제 해결

### 1. 값이 불일치하는 경우
1. **데이터 소스 확인**: `processed_data`의 Status_Location 값 검증
2. **날짜 필터링 확인**: month_end 설정값 검토
3. **PKG_ID 중복 확인**: drop_duplicates 로직 검증

### 2. 디버그 정보 활용
- `latest['Pkg'].sum()`: PKG 값 합계
- `latest['Pkg'].count()`: 아이템 개수
- `latest.shape`: 데이터프레임 크기

## 📊 비즈니스 로직

### 1. 현장 재고 계산 원칙
- **현장별 분류**: Status_Location 기준으로 4개 현장 구분
- **최신 데이터**: 각 PKG_ID별 최신 날짜 데이터만 사용
- **개별 카운트**: PKG 값과 관계없이 개별 아이템으로 계산

### 2. 데이터 처리 흐름
1. **데이터 로드** → `calculate_warehouse_statistics()`
2. **현장 필터링** → Status_Location 기준
3. **날짜 처리** → InvDate 기준 정렬 및 중복 제거
4. **재고 계산** → 현장별 아이템 개수 집계
5. **결과 검증** → 기대값과 비교

---

🔧 **추천 명령어:**
`/test-scenario site-inventory` [현장 재고 테스트 시나리오 실행]
`/validate-data inventory-calculation` [재고 계산 로직 검증]
`/automate test-pipeline` [전체 테스트 파이프라인 실행] 