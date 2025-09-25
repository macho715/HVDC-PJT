sssssssssssssssss
# HVDC Hitachi + Simense 통합 **5‑시트 Excel 리포트** 작성 **완전 가이드**
*버전 v2.8.4 | 업데이트 2025-07-06*

---

## 목차
1. 개요 & 핵심 수치
2. 폴더 구조 & 환경 준비
3. 파이프라인 총괄 아키텍처
4. 모듈·클래스·함수 심층 설명
5. 엔드‑투‑엔드 실행 예
6. 시트별 생성 로직
7. 엑셀 서식 규칙 & UX 디테일
8. 검증(Assert) 스위트
9. 배치·CI 통합 스크립트
10. 부록 A — 테이블/모델 DDL
11. FAQ & 트러블슈팅

**RAW DATA** :

- `C:\cursor-mcp\HVDC_PJT\data\HVDC WAREHOUSE_HITACHI(HE).xlsx`
- `C:\cursor-mcp\HVDC_PJT\data\HVDC WAREHOUSE_SIMENSE(SIM).xlsx`

## 1. 개요 & 핵심 수치
| 항목 | Hitachi | Simense | 합계 |
|------|-------:|--------:|-----:|
| RAW 레코드 (Case List) | **5,552** | **1,853** | **7,405** |
| Pre‑Arrival (FLOW 0)   | **102**  | **10**    | **112**   |
| Flow Code 범위         | —        | —         | **0-4**   |

---

## 2. 폴더 구조 & 환경 준비
### 2‑1. 권장 폴더 구조
```text
project/
├─ data/
│   ├─ HVDC WAREHOUSE_HITACHI(HE).xlsx
│   └─ HVDC WAREHOUSE_SIMENSE(SIM).xlsx
├─ 06_로직함수/
│   ├─ create_final_report_complete.py
│   ├─ calc_flow_code_v2.py
│   ├─ warehouse_calcs.py
│   └─ excel_writer_utils.py
└─ tests/
    └─ test_assert_suite.py
```

### 2‑2. 의존 패키지
```bash
python -m venv venv && source venv/bin/activate   # 선택
pip install pandas==1.5.3 openpyxl==3.1.2 python-dateutil==2.9.0
```

---

## 3. 파이프라인 총괄 아키텍처
```mermaid
graph TD
 A[Excel 2종 - Case List] --> B[standardize_case_list()]
 B --> C[FlowCodeCalculatorV2]
 C --> D[VENDOR Tag]
 D --> E[assert_suite()]
 E --> F[make_pivots()]
 F --> G[write_excel_sheets()]
```
## 3-1. 핵심함수

| 레이어       | 함수 (파일)                                                        | 한줄 설명         |
| --------- | -------------------------------------------------------------- | ------------- |
| 정규화       | `standardize_case_list()` (`create_final_report_complete.py`)  | 헤더·공백·대소문자 정리 |
| Flow Code | `FlowCodeCalculatorV2().calc()` (`calc_flow_code_v2.py`)       | 0-4 코드 계산     |
| 입·출고      | `calculate_warehouse_inbound_correct()` / `...outbound_real()` | 월별 In/Out 벡터  |
| 재고        | `calculate_site_inventory_correct()`                           | 월말 보수적 재고     |
| Pivot     | `_build_multi_header_df()`                                     | 2-레벨 헤더 구성    |
| Excel     | `_write_excel_sheets()`                                        | 5 시트+서식·병합    |
| 검증        | `assert_suite()`                                               | 행수·코드·헤더 체크   |


## 3-2.시트별 생성 로직 요약
| 시트                    | DataFrame                               | 만드는 방법                            |
| --------------------- | --------------------------------------- | --------------------------------- |
| 전체\_트랜잭션\_FLOWCODE0-4 | `all_cases`                             | 정규화+Flow Code 컬럼 포함, `to_excel()` |
| FLOWCODE0-4\_분석요약     | `all_cases.groupby('FLOW_CODE').size()` | pivot 결과                          |
| Pre\_Arrival\_상세분석    | `all_cases.query('FLOW_CODE==0')`       | 112 건                             |
| 창고별\_월별\_입출고          | `make_warehouse_io_table(all_cases)`    | 월×창고 MultiIndex                   |
| 현장별\_월별\_입고재고         | `make_site_stock_table(all_cases)`      | 월×현장 MultiIndex                   |



---

## 4. 모듈·클래스·함수 심층 설명

### 4‑1. `standardize_case_list(df)`
* **Input**  : 원본 DataFrame (Hitachi 또는 Simense 케이스)
* **Process**
  1. 헤더 정규화
     - 'total handling' -> 'FLOW_' + 번호(0~5)
     - 중복 공백 제거, Title‑case 변환
  2. 값 정규화
     - 전각 공백, 탭 제거
     - `Status_Storage`, `Status_Location` 대문자화
  3. dtype 캐스팅 (`FLOW_*` -> Int64 nullable)
* **Output** : 정규화 DataFrame, 행/인덱스 동일

### 4‑2. `FlowCodeCalculatorV2`
```python
class FlowCodeCalculatorV2:
    def calc(self, df: pd.DataFrame) -> pd.Series:
        """MOSB 및 Warehouse 이동 패턴 분석 후 0~4 코드 반환"""
```
**규칙표**

| 조건                     | 결과 코드 |
|--------------------------|-----------|
| `Status_Storage` == PRE ARRIVAL | 0 |
| 첫 Warehouse 입고       | 1 |
| MOSB 경유 이후 Warehouse | 2 |
| Warehouse → Site 이동    | 3 |
| Site 최종 위치           | 4 |

### 4‑3. `warehouse_calcs.py`
| 함수 | 설명 | 반환 |
|------|------|------|
| `calculate_warehouse_inbound_correct` | 월별 창고 입고 (`FLOW_1`) 피벗 | DataFrame |
| `calculate_warehouse_outbound_real`   | 월별 창고 출고 (`FLOW_3`) 피벗 | DataFrame |
| `calculate_stock_levels`              | 누적 재고 = 입고 cum - 출고 cum | DataFrame |

### 4‑4. `_build_multi_header_df`
단일 인덱스 DF -> `pd.MultiIndex.from_product([level0, level1])` 로 상/하 2‑레벨 헤더 변환.

### 4‑5. `_write_excel_sheets`
`openpyxl` 로 5개 시트 저장 +
- 상위 헤더 병합/회색 채움/볼드
- 조건부 서식: `ABS(In-Out)/In > 0.05` 빨강

### 4‑6. `assert_suite`
필수 검증:
```python
assert len(df_all)==7405
assert (df_all.FLOW_CODE==0).sum()==112
assert df_all.FLOW_CODE.between(0,4).all()
assert wh_io.columns.nlevels==2
```

---

## 5. 엔드‑투‑엔드 실행 예
```bash
python 06_로직함수/create_final_report_complete.py        --source "data/HVDC WAREHOUSE_*xlsx"        --out    "HVDC_Final_5Sheet_Report.xlsx"        --keep_raw
```
*실행 시간*: 10‑20 초

---

## 6. 시트별 생성 로직
| 시트명 | 원본 DF | 주요 열 | 비고 |
|-------|---------|--------|------|
| 전체_트랜잭션_FLOWCODE0-4 | all_cases | RAW + FLOW_CODE | 행 7,405 |
| FLOWCODE0-4_분석요약     | summary   | Flow Code, Count | 5행 |
| Pre_Arrival_상세분석     | pre_df    | RAW subset       | 112행 |
| 창고별_월별_입출고_완전체계 | wh_io     | In/Out 값        | MultiIndex |
| 현장별_월별_입고재고_완전체계 | site_stock| In/Stock         | MultiIndex |

---

## 7. 엑셀 서식 규칙 & UX 디테일
1. 두 줄 헤더: 상위(입고·출고·재고) 회색, 굵게
2. 월 열 포맷: `YYYY-MM`, 열 너비 14
3. 합계 행: `=SUM()`, 두꺼운 테두리
4. 숫자 포맷: `#,##0` 또는 `#,##0.00`
5. 조건부 서식: 오차 5 % 초과 셀 빨강

---

## 8. 검증(Assert) 스위트
`pytest -k "assert_suite"` 로 CI 파이프라인 연동 가능.
추가 KPI (PKG Accuracy ≥ 99 %) 검증 예:
```python
acc = df_all.SYSTEM_PKG.sum() / df_all.ACTUAL_PKG.sum()
assert round(acc*100,2) >= 99
```

---

## 9. 배치·CI 통합 스크립트 (GitHub Actions)
```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: '3.11'
  - run: pip install pandas openpyxl
  - run: |
      python 06_로직함수/create_final_report_complete.py              --source "data/HVDC WAREHOUSE_*xlsx"              --out "reports/HVDC_Final_5Sheet_${ github.run_id }.xlsx"
```

---

## 부록 A — 테이블/모델 DDL
```sql
CREATE TABLE warehouse_transactions (
  id INTEGER PRIMARY KEY,
  vendor TEXT,
  flow_code INTEGER CHECK(flow_code BETWEEN 0 AND 4),
  status_storage TEXT,
  status_location TEXT,
  month DATE,
  inbound_pkg INTEGER,
  outbound_pkg INTEGER,
  stock_pkg INTEGER
);
```

---

## FAQ & 트러블슈팅
| 문제 | 해결책 |
|------|--------|
| 헤더 'total handling' 매핑 안됨 | `standardize_case_list` 내부 매핑 dict 확인 |
| Pre‑Arrival 건수 다름 | Simense `Status_Storage` 대문자, 집계행 제외 확인 |
| 멀티 헤더 병합 실패 | `_write_excel_sheets` 의 `merge_cells` 옵션 확인 |
| 조건부 서식 미반영 | `with_format=True` 인자 전달 |

---

© 2025 MACHO‑GPT v3.4 mini — 지원 요청: `/logi-master help`
