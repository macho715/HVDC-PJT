# HVDC 실데이터 검증 보고서
**Date:** 2025-06-29
**Validator:** MACHO-GPT v3.4-mini

## 📋 Executive Summary

실제 Excel 데이터 **0행**을 v2.8 및 v2.8.1 알고리즘으로 분석한 결과:
- **v2.8 정확도**: 0.0%
- **v2.8.1 정확도**: 37.7%
- **개선도**: +37.7%p

## 📊 데이터 구조 분석

- **총 파일 수**: 4개
- **총 데이터**: 8,675행

### HVDC_STATUS
- 행 수: 637
- 컬럼 수: 76
- Location 컬럼: ✅
- Status 컬럼: ✅
- WH 관련 컬럼: ['DSV\n Indoor', 'DSV\n Outdoor', 'DSV\n MZD']
- MOSB 관련 컬럼: ['MOSB']

### HITACHI
- 행 수: 5,346
- 컬럼 수: 53
- Location 컬럼: ✅
- Status 컬럼: ✅
- WH 관련 컬럼: ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor']
- MOSB 관련 컬럼: ['MOSB']

### SIMENSE
- 행 수: 2,227
- 컬럼 수: 53
- Location 컬럼: ✅
- Status 컬럼: ✅
- WH 관련 컬럼: ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor']
- MOSB 관련 컬럼: ['MOSB']

### INVOICE
- 행 수: 465
- 컬럼 수: 32
- Location 컬럼: ❌
- Status 컬럼: ❌

## 📈 Flow Code 분포 비교

| Code | 정의 | 보고서 | v2.8 | v2.8.1 | v2.8 갭 | v2.8.1 갭 |
|:----:|:-----|:-----:|:----:|:------:|:-------:|:---------:|
| 0 | Pre Arrival | 163 | 0 | 547 | -163 | +384 |
| 1 | Port→Site | 3,593 | 0 | 3,885 | -3593 | +292 |
| 2 | Port→WH→Site | 1,183 | 0 | 3,730 | -1183 | +2547 |
| 3 | Port→WH→MOSB→Site | 402 | 0 | 508 | -402 | +106 |
| 4 | Port→WH→wh→MOSB→Site | 5 | 0 | 5 | -5 | 0 |

## ⚠️ 발견된 문제점

- hvdc_status: WH 관련 컬럼 발견 - ['DSV\n Indoor', 'DSV\n Outdoor', 'DSV\n MZD']
- hvdc_status: MOSB 관련 컬럼 발견 - ['MOSB']
- hitachi: WH 관련 컬럼 발견 - ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor']
- hitachi: MOSB 관련 컬럼 발견 - ['MOSB']
- simense: WH 관련 컬럼 발견 - ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor']
- simense: MOSB 관련 컬럼 발견 - ['MOSB']
- invoice: Location 컬럼 부재
- invoice: Status 컬럼 부재
