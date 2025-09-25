# 📊 HVDC 프로젝트 Excel Agent 통합 가이드

## 1. 개요

**Excel Agent**는 HVDC 프로젝트의 대용량 창고/물류 데이터를 자연어로 분석, 쿼리, 리포트 생성까지 자동화하는 AI 기반 데이터 분석 도구입니다. MACHO-GPT 시스템과 완전히 통합되어, 실무자가 복잡한 Excel 데이터를 명령어 한 줄로 분석할 수 있습니다.

---

## 2. 주요 기능
- Excel/CSV 파일 자동 인식 및 로드 (openpyxl 기반)
- 자연어 쿼리 → pandas 코드 자동 변환 및 실행
- KPI, 창고별/월별/상태별 통계 자동 추출
- HVDC 특화 분석(입고/출고/재고, PKG 검증, FANR/MOIAT 규정 등)
- 분석 결과 리포트 자동 생성 및 내보내기
- MACHO-GPT 명령어 체계와 완전 호환

---

## 3. 사용법

### 3.1. Excel 파일 로드
```bash
/cmd excel_load file_path="data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
```
- 여러 파일 동시 로드 가능 (dataframe_name 지정)

### 3.2. 자연어 쿼리 실행
```bash
/cmd excel_query query="2024년 6월 입고된 항목 수는?"
```
- 한글/영문 모두 지원
- 예시: "창고별 재고 현황 보여줘", "DSV Indoor 출고량 월별 추이 분석"

### 3.3. 데이터프레임 정보 확인
```bash
/cmd excel_info
```
- 컬럼, 행 수, 샘플 데이터, 타입 등 요약

### 3.4. HVDC 특화 분석
```bash
/cmd hvdc_analysis analysis_type="warehouse"
```
- analysis_type: warehouse, site, monthly, kpi 등

### 3.5. 분석 결과 리포트 내보내기
```bash
/cmd excel_export format="xlsx" output_path="output/hvdc_report.xlsx"
```
- format: xlsx, csv, json 등 지원

### 3.6. 시스템 상태 확인
```bash
/cmd excel_status
```
- 현재 로드된 데이터, 분석 가능 여부, 최근 쿼리 이력 등

---

## 4. 명령어 요약
| 명령어         | 설명                                 |
|----------------|--------------------------------------|
| excel_load     | Excel/CSV 파일 로드                  |
| excel_query    | 자연어 데이터 분석 쿼리              |
| excel_info     | 데이터프레임 정보 요약               |
| hvdc_analysis  | HVDC 특화 종합 분석                  |
| excel_export   | 분석 결과 리포트 내보내기             |
| excel_status   | Excel Agent 시스템 상태 확인          |

---

## 5. 활용 예시

### 창고별 월별 입고량 분석
```bash
/cmd excel_query query="2024년 5월~6월 DSV Indoor 창고 입고량 월별로 보여줘"
```

### PKG 정확도 검증
```bash
/cmd hvdc_analysis analysis_type="pkg_validation"
```

### FANR/MOIAT 규정 준수 검증
```bash
/cmd hvdc_analysis analysis_type="compliance"
```

---

## 6. 자주 묻는 질문(FAQ)

**Q1. 대용량(10만행 이상) Excel도 지원하나요?**
- 네, openpyxl + pandas 기반으로 수십만 행까지 지원합니다. 단, 메모리/성능 한계에 따라 처리 시간이 늘어날 수 있습니다.

**Q2. 한글 컬럼명/특수문자도 인식되나요?**
- 네, 모든 언어/특수문자 컬럼명 자동 인식 및 쿼리 변환 지원합니다.

**Q3. 자연어 쿼리 실패/오류시 대처법?**
- 쿼리 문장을 더 구체적으로 작성하거나, 컬럼명을 명시적으로 포함해 주세요.
- 오류 메시지와 함께 /excel_status 명령어로 상태를 확인하세요.

**Q4. 분석 결과 신뢰도는 어떻게 확인하나요?**
- 모든 명령어 결과에 confidence(신뢰도) 점수가 포함됩니다(0.90 이상 권장).

**Q5. 리포트 자동화/스케줄링도 가능한가요?**
- 네, /excel_export 명령어를 스케줄러/워크플로우에 연동해 자동화할 수 있습니다.

---

## 7. 오류/예외 대응
- AttributeError 등 시스템 오류 발생 시 최신 버전으로 업데이트 후 재시도
- 데이터 컬럼 누락/오타 → /excel_info로 컬럼명 확인 후 쿼리 재작성
- 시스템 상태 불안정 시 /excel_status로 점검

---

## 8. TDD/통합 기준
- 모든 기능은 pytest 기반 단위/통합 테스트 95% 이상 커버리지 보장
- MACHO-GPT 명령어 체계와 완전 호환(모든 함수는 /cmd로 호출 가능)
- 신뢰도(confidence) 0.90 이상, FANR/MOIAT 규정 준수

---

## 9. 참고/문의
- 시스템 통합, 고급 분석, 자동화 연동 등 추가 문의: 프로젝트 담당자 또는 AI 지원 채널 이용
- 최신 가이드/예제: `/docs/` 폴더 및 공식 리포지토리 참고 