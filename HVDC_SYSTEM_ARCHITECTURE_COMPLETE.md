# 🏗️ HVDC PROJECT 시스템 전체 구조 분석

## 📋 시스템 개요

**HVDC PROJECT**는 Samsung C&T와 ADNOC·DSV 파트너십을 위한 고급 물류 AI 시스템으로, **MACHO-GPT v3.4-mini**를 핵심으로 하는 완전한 물류 자동화 플랫폼입니다.

**프로젝트 상태**: ✅ **OPERATIONAL** | **데이터 품질**: **100%** | **시스템 신뢰도**: **95%+**

---

## 🎯 핵심 시스템 아키텍처

### 🏗️ **4계층 통합 아키텍처**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MACHO-GPT v3.4-mini                         │
│                  (통합 AI 제어 시스템)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
      ┌───▼───┐   ┌───▼───┐   ┌───▼────┐
      │ DATA  │   │ LOGIC │   │ OUTPUT │
      │ENGINE │   │ENGINE │   │ENGINE  │
      └───────┘   └───────┘   └────────┘
```

### 🔧 **6개 Containment Modes**

| **Mode** | **신뢰도** | **용도** | **주요 기능** |
|----------|------------|----------|---------------|
| **PRIME** | ≥95% | 기본 운영 | 일반 물류 작업, 데이터 분석 |
| **ORACLE** | ≥95% | 실시간 검증 | 데이터 동기화, 예측 분석 |
| **LATTICE** | ≥95% | 적재 최적화 | OCR 처리, Heat-Stow 분석 |
| **RHYTHM** | ≥91% | KPI 모니터링 | 실시간 대시보드, 알림 시스템 |
| **COST-GUARD** | ≥93% | 비용 관리 | 비용 검증, 승인 워크플로우 |
| **ZERO** | 0% | 안전 모드 | 오류 복구, 수동 개입 |

---

## 📁 **프로젝트 구조 상세**

### 🧠 **핵심 시스템 디렉토리**

```
📦 HVDC PJT/
├── 🧠 hvdc_macho_gpt/           # 메인 AI 시스템
│   ├── WAREHOUSE/               # 창고 관리 시스템
│   │   ├── analyze_hitachi.py   # HITACHI 창고 분석
│   │   ├── analyze_hvdc_status.py # HVDC 상태 분석
│   │   ├── analyze_real_movement.py # 실제 이동 분석
│   │   ├── core/                # 핵심 모듈
│   │   ├── data/                # 데이터 파일
│   │   ├── reports/             # 분석 리포트
│   │   └── dashboard_output/    # 대시보드 출력
│   ├── HVDC STATUS/            # 상태 관리 시스템
│   │   ├── analyze_data.py     # 데이터 분석
│   │   ├── fcast.py           # 예측 모델
│   │   ├── models/            # ML 모델
│   │   └── output/            # 출력 결과
│   └── hvdc_ontology_system/   # 온톨로지 엔진
│       ├── config/            # 설정 파일
│       ├── data/              # 온톨로지 데이터
│       ├── schemas/           # 스키마 정의
│       └── reports/           # 온톨로지 리포트
├── 🗺️ Mapping/                  # 데이터 매핑 시스템
│   ├── analyze_hvdc_status.py # HVDC 상태 매핑
│   ├── analyze_inland_trucking_v27.py # 내륙 운송 분석
│   ├── analyze_scnt_invoice_fixed.py # SCNT 인보이스 분석
│   ├── ontology/              # 온톨로지 매핑
│   └── reasoning_output/      # 추론 결과
├── 📊 hvdc_ontology_system/     # 통합 온톨로지
│   ├── config/                # 설정
│   ├── data/                  # 데이터
│   ├── exports/               # 내보내기
│   ├── logs/                  # 로그
│   ├── reports/               # 리포트
│   ├── schemas/               # 스키마
│   └── scripts/               # 스크립트
├── 📋 inland invoice/           # 내륙 운송 인보이스
│   ├── contract_inland_trucking_charge_rates_v1.1.md
│   ├── DOMESTIC_DELIVERY_APRIL_VERIFICATION.md
│   └── Domestic_Rate_Additional_Analysis.md
├── 📁 src/                      # 소스 코드
│   ├── logi_master_system.py   # 통합 물류 관리 시스템
│   ├── macho_gpt.py            # MACHO-GPT 핵심 클래스
│   ├── logi_meta_fixed.py      # 메타데이터 관리
│   ├── components/             # UI 컴포넌트
│   ├── core/                   # 핵심 모듈
│   ├── integrations/           # 외부 시스템 연동
│   ├── workflows/              # 워크플로우
│   └── utils/                  # 유틸리티
├── 📁 tests/                    # 테스트 프레임워크
│   ├── test_macho_gpt_integration.py # MACHO-GPT 통합 테스트
│   ├── test_3d_network_visualizer.py # 3D 네트워크 시각화
│   ├── test_advanced_integration_production.py # 고급 통합 테스트
│   └── test_compliance_security.py # 규정 준수 보안 테스트
├── 📁 templates/                # HTML 템플릿
│   └── dashboard.html          # 대시보드 템플릿
├── 📁 docs/                     # 문서화
│   ├── changelog.md            # 변경 이력
│   └── excel_agent_guide.md    # Excel 에이전트 가이드
├── 📁 data/                     # 데이터 파일
│   ├── HVDC STATUS.xlsx        # HVDC 상태 데이터
│   ├── HVDC WAREHOUSE_HITACHI(HE).xlsx # HITACHI 창고 데이터
│   ├── HVDC WAREHOUSE_SIMENSE(SIM).xlsx # SIEMENS 창고 데이터
│   └── backup_*/               # 백업 데이터
├── 📁 output/                   # 출력 결과
│   ├── validation_reports/     # 검증 리포트
│   └── *.xlsx                  # Excel 출력 파일
├── 📁 reports/                  # 시스템 리포트
├── 📁 logs/                     # 시스템 로그
├── 📁 config/                   # 설정 파일
│   └── wh_priority.yaml        # 창고 우선순위 설정
└── 📁 MACHO_통합관리_20250702_205301/ # MACHO 통합 관리
    ├── 01_원본파일/            # 원본 파일
    ├── 02_통합결과/            # 통합 결과
    ├── 03_자동화스크립트/      # 자동화 스크립트
    ├── 04_작업리포트/          # 작업 리포트
    └── 06_로직함수/            # 로직 함수
```

---

## 🔄 **4계층 시스템 구조**

### **1️⃣ Task Management Layer (작업 관리)**
- **파일**: `src/logi_master_system.py` (TaskManagementLayer)
- **기능**: Shrimp Task Manager 통합
- **주요 클래스**: 
  - `LogiTask`: 물류 작업 데이터 구조
  - `TaskManagementLayer`: 작업 관리 레이어
- **데이터베이스**: SQLite 기반 작업 관리
- **기본 작업**:
  - 송장 OCR 처리 시스템 구축
  - 컨테이너 적재 최적화
  - 창고 입출고 분석

### **2️⃣ Dashboard Integration Layer (대시보드 통합)**
- **파일**: `src/logi_master_system.py` (DashboardIntegrationLayer)
- **기능**: 다중 대시보드 통합 관리
- **주요 클래스**: 
  - `LogiDashboard`: 대시보드 데이터 구조
  - `DashboardIntegrationLayer`: 대시보드 통합 레이어
- **지원 형식**: HTML, API, 실시간 대시보드
- **통합 대시보드**:
  - HVDC 메인 대시보드
  - 창고 모니터링 대시보드
  - 재고 추적 대시보드
  - API 통합 대시보드

### **3️⃣ Ontology Knowledge Layer (온톨로지 지식)**
- **파일**: `src/logi_master_system.py` (OntologyKnowledgeLayer)
- **기능**: RDF/SPARQL 기반 지식 관리
- **주요 클래스**: 
  - `LogiOntology`: 온톨로지 데이터 구조
  - `OntologyKnowledgeLayer`: 온톨로지 지식 레이어
- **지원 형식**: TTL, SPARQL 쿼리
- **온톨로지 기능**:
  - 시맨틱 분류 엔진
  - RDF/OWL 스키마 매핑
  - SQLite 온톨로지 저장소
  - TTL 그래프 생성기

### **4️⃣ MACHO-GPT AI Layer (AI 통합 제어)**
- **파일**: `src/logi_master_system.py` (MachoGPTAILayer)
- **기능**: 60+ 명령어 지원, 모드 전환
- **주요 클래스**: 
  - `LogiCommand`: 명령어 데이터 구조
  - `MachoGPTAILayer`: MACHO-GPT AI 레이어
- **통합**: MCP 서버, 외부 API
- **AI 기능**:
  - Excel Agent 통합
  - 대시보드 강화
  - 모드 전환
  - KPI 데이터 조회
  - FANR 규정 준수 검증
  - 컨테이너 적재 최적화
  - 기상 조건 연동 분석

---

## 🧪 **TDD 개발 프레임워크**

### **테스트 구조**
```
📁 tests/
├── test_macho_gpt_integration.py    # MACHO-GPT 통합 테스트
├── test_3d_network_visualizer.py    # 3D 네트워크 시각화
├── test_advanced_integration_production.py  # 고급 통합 테스트
├── test_compliance_security.py      # 규정 준수 보안 테스트
├── test_data_validation.py          # 데이터 검증 테스트
├── test_warehouse_operations.py     # 창고 운영 테스트
├── test_ontology_queries.py         # 온톨로지 쿼리 테스트
├── test_mcp_integration.py          # MCP 통합 테스트
├── test_excel_processing.py         # Excel 처리 테스트
├── test_weather_analysis.py         # 기상 분석 테스트
├── test_cost_optimization.py        # 비용 최적화 테스트
├── test_real_time_monitoring.py     # 실시간 모니터링 테스트
├── test_api_integration.py          # API 통합 테스트
├── test_dashboard_functionality.py  # 대시보드 기능 테스트
├── test_data_sync.py                # 데이터 동기화 테스트
└── test_error_recovery.py           # 오류 복구 테스트
```

### **핵심 테스트 클래스**

#### **MACHOGPTIntegration**
- **파일**: `tests/test_macho_gpt_integration.py`
- **기능**: 통합 시스템 테스트
- **주요 메서드**:
  - `switch_mode()`: 모드 전환 테스트
  - `register_command()`: 명령어 등록 테스트
  - `execute_command()`: 명령어 실행 테스트
  - `get_mode_info()`: 모드 정보 조회 테스트

#### **ContainmentMode**
- **기능**: 모드 관리 테스트
- **속성**:
  - `name`: 모드 이름
  - `confidence_threshold`: 신뢰도 임계값
  - `auto_triggers`: 자동 트리거 여부
  - `description`: 모드 설명
  - `capabilities`: 지원 기능 목록

#### **CommandRequest/Response**
- **기능**: 명령어 실행 테스트
- **CommandRequest 속성**:
  - `command`: 명령어 이름
  - `args`: 명령어 인수
  - `user_role`: 사용자 역할
  - `mode`: 실행 모드
  - `timestamp`: 실행 시간
- **CommandResponse 속성**:
  - `status`: 실행 상태
  - `data`: 실행 결과 데이터
  - `confidence`: 신뢰도
  - `mode`: 현재 모드
  - `triggers`: 트리거 목록
  - `execution_time`: 실행 시간

### **테스트 시나리오**

#### **Phase 1: Core Infrastructure Tests [✅ 완료]**
- [x] `test_meta_system_initialization` - 메타 시스템 초기화
- [x] `test_containment_mode_switching` - 모드 전환 테스트

#### **Phase 2: Data Processing Tests [✅ 완료]**
- [x] `test_enhanced_data_sync` - 향상된 데이터 동기화
- [x] `test_macho_flow_corrected` - MACHO 플로우 수정
- [x] `test_wh_handling_analysis` - WH 처리 분석

#### **Phase 3: Compliance & Security Tests [✅ 완료]**
- [x] `test_fanr_compliance_validation` - FANR 규제 준수 검증

#### **Phase 4: Advanced Analytics Tests [60% 완료]**
- [x] `test_predictive_analytics` - 예측 분석 테스트
- [x] `test_anomaly_detection` - 이상 탐지 테스트
- [🟡] `test_real_time_optimization` - 실시간 최적화 테스트
- [⭕] `test_machine_learning_integration` - 머신러닝 통합 테스트

#### **Phase 5: Integration Tests [40% 완료]**
- [x] `test_samsung_ct_api_integration` - Samsung C&T API 통합 테스트
- [🟡] `test_adnoc_dsv_connectivity` - ADNOC·DSV 연결성 테스트
- [⭕] `test_real_time_dashboard` - 실시간 대시보드 테스트
- [⭕] `test_mobile_app_integration` - 모바일 앱 통합 테스트

---

## 🔌 **MCP 서버 통합**

### **활성 서버 (6개)**

| **서버명** | **상태** | **프로세스 ID** | **도구 수** | **메모리** | **신뢰도** |
|------------|----------|-----------------|-------------|------------|------------|
| **JSON MCP** | ✅ 실행 중 | 21652 | 12 | 1.9MB | 95% |
| **Calculator MCP** | ✅ 실행 중 | 21668 | 1 | 1.9MB | 95% |
| **MCP Aggregator** | ✅ 실행 중 | 21828 | - | 1.9MB | 95% |
| **Context7 MCP** | ✅ 실행 중 | 22256 | 9 | 8.8MB | 95% |
| **DeepView MCP** | ✅ 실행 중 | 29276 | 8 | 93MB | 95% |
| **Android MCP** | ✅ 실행 중 | 33184 | 7 | 50MB | 95% |

### **통합 실패 서버 (4개)**

| **서버명** | **상태** | **오류 원인** | **해결 방안** |
|------------|----------|---------------|---------------|
| **Bright Data MCP** | ❌ 미실행 | Docker Desktop 미실행 | Docker Desktop 시작 필요 |
| **VLM Run MCP** | ❌ 미실행 | Docker Desktop 미실행 | Docker Desktop 시작 필요 |
| **Google Admin MCP** | ❌ 미실행 | Docker Desktop 미실행 | Docker Desktop 시작 필요 |
| **Email MCP** | ❌ 미실행 | pipx 명령어 인식 안됨 | PATH 설정 필요 |

### **MACHO-GPT 통합 현황**

#### **시스템 상태**
- **Version**: v3.4-mini
- **Current Mode**: PRIME
- **Confidence**: 97.3%
- **Uptime**: 99.2%
- **Active Modules**: 9/12
- **Total Commands**: 21
- **Fail-safe Rate**: <3%

#### **통합된 명령어들**
1. `switch_mode` - 모드 전환 (6개 모드 지원)
2. `logi_master invoice-audit` - 송장 OCR 처리
3. `logi_master predict` - ETA 예측
4. `logi_master kpi-dash` - KPI 대시보드
5. `logi_master weather-tie` - 날씨 영향 분석

---

## 📊 **데이터 처리 엔진**

### **Enhanced Data Sync v2.8.4**

#### **시스템 성과**
- **총 처리 아이템**: **8,038건** (완전 동기화)
- **데이터 품질 점수**: **100.0%** (목표 90%+ 초과 달성! 🎉)
- **UNKNOWN 비율**: **0.0%** (완벽한 데이터 정규화)
- **처리 시간**: **4초** (최적화된 성능)

#### **Excel 파일 처리 현황**
```
✅ HITACHI (HE): 5,346행 - 완료
✅ SIEMENS (SIM): 2,227행 - 완료  
✅ INVOICE: 465행 - 완료
```

#### **데이터 품질 분석**
- **구조 준수율**: 86.7%
- **신뢰도**: ≥90% MACHO-GPT 표준 달성
- **가용성**: 24/7 연속 운영 가능

### **MACHO Flow Corrected v2.8.4**

#### **Flow Code 분포**
| **Code** | **상태** | **경로** | **건수** | **비율** | **설명** |
|----------|----------|----------|----------|----------|----------|
| **0** | **Pre Arrival** | `pre_arrival` | **302건** | **4.0%** | **사전 도착 대기 상태** |
| **1** | Active | `port→site` | **3,268건** | **43.2%** | Port → Site (직송) |
| **2** | Active | `port→warehouse→site` | **3,518건** | **46.5%** | Port → Warehouse → Site (창고 경유) |
| **3** | Active | `port→warehouse→offshore→site` | **480건** | **6.3%** | Port → Warehouse → MOSB → Site (해상기지 포함) |
| **4** | Active | `port→warehouse→warehouse→offshore→site` | **5건** | **0.1%** | Port → Warehouse → Warehouse → MOSB → Site (복합 경유) |

#### **WH HANDLING 분포**
| **WH** | **건수** | **비율** | **설명** |
|--------|----------|----------|----------|
| **-1** | **302건** | **4.0%** | **Pre Arrival (아직 창고 경유 없음)** |
| **0** | **3,505건** | **46.3%** | 0개 창고 경유 (직송) |
| **1** | **3,112건** | **41.1%** | 1개 창고 경유 |
| **2** | **654건** | **8.6%** | 2개 창고 경유 |

---

## 🎯 **핵심 기능 모듈**

### **1. 물류 마스터 시스템**
- **파일**: `src/logi_master_system.py`
- **기능**: 4계층 통합 관리
- **명령어**: 60+ 지원
- **주요 클래스**: `LogiMasterSystem`
- **통합 기능**:
  - 작업 관리 (TaskManagementLayer)
  - 대시보드 통합 (DashboardIntegrationLayer)
  - 온톨로지 지식 (OntologyKnowledgeLayer)
  - MACHO-GPT AI (MachoGPTAILayer)

### **2. 창고 관리 시스템**
- **위치**: `hvdc_macho_gpt/WAREHOUSE/`
- **기능**: 6개 창고 통합 관리
- **분석**: Heat-Stow, WHF/Cap
- **주요 파일**:
  - `analyze_hitachi.py`: HITACHI 창고 분석
  - `analyze_hvdc_status.py`: HVDC 상태 분석
  - `analyze_real_movement.py`: 실제 이동 분석
- **창고별 트랜잭션 분포**:
  1. **DSV Outdoor:** 312건 (최대 규모)
  2. **DSV Indoor:** 127건
  3. **DSV MZP:** 9건
  4. **DSV Al Markaz:** 6건  
  5. **AAA Storage:** 5건
  6. **Shifting:** 2건 (특수 운영)

### **3. 온톨로지 엔진**
- **위치**: `hvdc_ontology_system/`
- **기능**: RDF/SPARQL 완전 지원
- **매핑**: 16개 필드 표준화
- **주요 기능**:
  - 시맨틱 분류 엔진 (4개 규칙)
  - SQLite 온톨로지 저장소
  - TTL 그래프 생성기
  - 다중 파일 로더 (4개 소스)
  - 컬럼 표준화 매퍼 (90개 → 표준)
  - 트랜잭션 분석기
  - 리포트 생성기

### **4. MACHO Flow 시스템**
- **파일**: `MACHO_통합관리_20250702_205301/`
- **기능**: FLOW CODE 0-4 완전 체계
- **정확도**: 100% (Excel 피벗 테이블 일치)
- **주요 파일**:
  - `complete_transaction_data_wh_handling_v284.py`: 전체 트랜잭션 처리
  - `create_final_report_complete.py`: 완전한 리포트 생성기
  - `create_final_report_original_logic.py`: 원본 로직 리포트 생성

### **5. MACHO-GPT 핵심 클래스**
- **파일**: `src/macho_gpt.py`
- **주요 클래스**:
  - `LogiMaster`: 핵심 물류 작업 처리
  - `ContainerStow`: 컨테이너 적재 최적화
  - `WeatherTie`: 날씨 영향 분석
- **기능**:
  - 송장 OCR 처리 및 FANR/MOIAT 규정 준수 검증
  - Heat-Stow 분석을 통한 적재 최적화
  - 창고 용량 및 처리 요인 확인
  - 날씨 조건 확인 및 영향도 분석

---

## 🔧 **명령어 시스템**

### **주요 명령어 카테고리 (10개)**

#### **1. Containment (모드 관리)**
- `switch_mode`: 모드 전환 및 관리
- `get_mode_info`: 모드 정보 조회
- `set_mode_config`: 모드 설정 변경

#### **2. Logistics (물류 작업)**
- `logi_master invoice-audit`: 송장 OCR 처리
- `logi_master predict`: ETA 예측
- `logi_master kpi-dash`: KPI 대시보드
- `logi_master weather-tie`: 날씨 영향 분석

#### **3. Analytics (데이터 분석)**
- `analyze_integrated_data`: 통합 데이터 분석
- `analyze_stack_sqm`: SQM/STACK 분석
- `create_final_report`: 최종 리포트 생성

#### **4. Warehouse (창고 운영)**
- `warehouse_analysis`: 창고 분석
- `inventory_tracking`: 재고 추적
- `capacity_check`: 용량 확인

#### **5. Weather (기상 조건)**
- `weather_check`: 날씨 조건 확인
- `weather_tie_analysis`: 날씨 연동 분석
- `eta_update`: ETA 업데이트

#### **6. Cost (비용 관리)**
- `cost_guard_analysis`: 비용 가드 분석
- `cost_optimization`: 비용 최적화
- `approval_workflow`: 승인 워크플로우

#### **7. Compliance (규정 준수)**
- `validate_fanr`: FANR 규정 준수 검증
- `validate_moiat`: MOIAT 규정 준수 검증
- `certificate_validation`: 인증서 검증

#### **8. Integration (외부 시스템 연동)**
- `samsung_ct_api`: Samsung C&T API 연동
- `adnoc_dsv_connectivity`: ADNOC·DSV 연결성
- `mcp_integration`: MCP 서버 통합

#### **9. Reporting (리포트 생성)**
- `generate_report`: 리포트 생성
- `export_data`: 데이터 내보내기
- `dashboard_update`: 대시보드 업데이트

#### **10. Security (보안 및 감사)**
- `security_audit`: 보안 감사
- `access_control`: 접근 제어
- `audit_trail`: 감사 추적

---

## 📈 **성능 지표 (KPI)**

### **시스템 성능**
- **신뢰도**: ≥95% (MACHO-GPT 표준)
- **가용성**: 99.2% (24/7 연속 운영)
- **처리 속도**: 8,038건/4초 (실시간)
- **오류율**: <3% (Fail-safe 시스템)
- **데이터 품질**: 100.0% (목표 90%+ 초과 달성)

### **비즈니스 성과**
- **창고 운영 효율성**: 6개 창고 통합 분석
- **화물 추적 정확도**: 8개 타입 완전 분류
- **비용 투명성**: 상세 트랜잭션 분석 제공
- **규정 준수**: FANR·MOIAT 컴플라이언스 달성

### **실제 데이터 분석 결과**

#### **창고별 트랜잭션 분포**
1. **DSV Outdoor:** 312건 (최대 규모)
2. **DSV Indoor:** 127건
3. **DSV MZP:** 9건
4. **DSV Al Markaz:** 6건  
5. **AAA Storage:** 5건
6. **Shifting:** 2건 (특수 운영)

#### **비용 구조 분석**
- **총액**: 11,401,986 AED
- **HANDLING**: 13.4%
- **추정 RENT**: 86.6%

#### **화물 유형 분포**
- **HE**: HITACHI 전기 장비
- **SIM**: SIEMENS 장비
- **SCT**: 특수 화물
- **기타**: 다양한 특수 화물

---

## 🚀 **실행 방법**

### **1. 메인 시스템 실행**
```bash
python src/logi_master_system.py
```

### **2. 테스트 파이프라인 실행**
```bash
/automate test-pipeline
```

### **3. MACHO-GPT 통합**
```bash
/macho_gpt integrate_macho
```

### **4. MCP 서버 상태 확인**
```bash
cmd_setup_mcp_servers
```

### **5. 시스템 상태 조회**
```bash
python src/logi_master_system.py --status
```

---

## 🔧 **개발 환경 설정**

### **필수 의존성**
```python
# requirements.txt
pandas>=2.2.0
numpy>=1.24.0
sqlite3
yaml
asyncio
logging
pathlib
dataclasses
abc
typing
```

### **설정 파일**
```yaml
# config/logi_master_config.yaml
task_management:
  database_path: "logi_tasks.db"
  
dashboard_integration:
  dashboards: {}
  
ontology_knowledge:
  ontology_path: "hvdc_ontology_system/"
  
macho_gpt_ai:
  confidence_threshold: 0.90
```

### **환경 변수**
```bash
# .env
MACHO_GPT_MODE=PRIME
MACHO_GPT_CONFIDENCE_THRESHOLD=0.95
HVDC_PROJECT_PATH=/c%3A/cursor-mcp/HVDC_PJT
MCP_HOST=localhost
MCP_PORT=3006
```

---

## 📋 **모니터링 및 유지보수**

### **로그 관리**
- **위치**: `logs/`
- **형식**: `macho_integration_YYYYMMDD_HHMMSS.log`
- **레벨**: INFO, WARNING, ERROR, DEBUG

### **백업 시스템**
- **위치**: `backup_*/`
- **주기**: 자동 백업 (일일/주간/월간)
- **형식**: Excel, JSON, SQLite

### **성능 모니터링**
- **실시간 KPI**: 대시보드에서 확인
- **시스템 상태**: `/logi_master system_status`
- **오류 추적**: 자동 로깅 및 알림

---

## 🔧 **추천 명령어**

### **시스템 관리**
- `/automate test-pipeline` [전체 시스템 테스트 실행 - 현재 상태 확인]
- `/macho_gpt switch_mode PRIME` [기본 운영 모드 활성화 - 시스템 안정화]
- `/logi_master system_status` [시스템 상태 조회 - 성능 모니터링]

### **데이터 분석**
- `/analyze_integrated_data` [통합 데이터 분석 - 전체 현황 파악]
- `/warehouse_analysis` [창고 분석 - 운영 효율성 확인]
- `/generate_kpi_dashboard` [KPI 대시보드 생성 - 성과 지표 확인]

### **운영 관리**
- `/validate_fanr_compliance` [FANR 규정 준수 검증 - 규정 준수 확인]
- `/weather_tie_analysis` [날씨 영향 분석 - ETA 예측]
- `/cost_guard_analysis` [비용 가드 분석 - 비용 최적화]

---

## 📞 **지원 및 문의**

### **시스템 정보**
- **버전**: MACHO-GPT v3.4-mini
- **프로젝트**: HVDC_SAMSUNG_CT_ADNOC_DSV
- **개발팀**: HVDC Team
- **라이선스**: MIT

### **문서화**
- **API 문서**: `docs/`
- **사용자 가이드**: `docs/excel_agent_guide.md`
- **변경 이력**: `docs/changelog.md`

---

**📅 생성일**: 2025-01-11  
**🔄 최종 업데이트**: 2025-01-11  
**📊 시스템 상태**: ✅ OPERATIONAL  
**🎯 신뢰도**: 97.3% 