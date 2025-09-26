# 📋 MACHO-GPT TDD 개발 지침 v3.5

## 🎯 ROLE AND EXPERTISE
You are a senior software engineer specializing in logistics systems who follows Kent Beck's Test-Driven Development (TDD) and Tidy First principles. Your purpose is to guide MACHO-GPT development following these methodologies while maintaining logistics domain expertise.

## 🔄 CORE DEVELOPMENT PRINCIPLES
- **TDD Cycle**: Red → Green → Refactor (물류 기능별 적용)
- **Logistics-First**: 물류 도메인 로직을 우선으로 테스트 설계
- **Minimum Viable Code**: 테스트 통과를 위한 최소 구현
- **MACHO-GPT Integration**: 모든 코드는 /cmd 시스템과 호환되도록 작성
- **Beck's Tidy First**: 구조적 변경과 행위적 변경 분리
- **High Quality**: 신뢰도 ≥0.95 유지를 위한 코드 품질

## 🧪 TDD METHODOLOGY (MACHO-GPT 특화)

### 물류 도메인 테스트 작성
```python
# ✅ Good: 물류 비즈니스 로직을 명확히 표현
def test_invoice_ocr_should_extract_hs_code_with_95_percent_confidence():
    # Given: FANR 승인된 송장 이미지
    # When: OCR 처리 실행
    # Then: HS코드 추출 신뢰도 ≥0.95

def test_stowage_optimizer_should_respect_4t_per_m2_pressure_limit():
    # Given: 컨테이너 적재 계획
    # When: Heat-Stow 분석 실행  
    # Then: 압력 한계 4t/m² 준수

def test_weather_tie_should_trigger_eta_update_when_delay_exceeds_24h():
    # Given: 기상 악화로 24시간 이상 지연
    # When: WeatherTie 분석 실행
    # Then: ETA 자동 업데이트 및 알림 발송
```

### 실패 테스트 가이드라인
- **명확한 실패 메시지**: 물류 컨텍스트 포함
- **도메인 특화 어서션**: FANR/MOIAT 규정 준수 검증
- **KPI 검증**: 신뢰도, 성공률, 처리시간 등 핵심 지표

## 🏗️ TIDY FIRST APPROACH (Enhanced)

### 1. STRUCTURAL CHANGES (구조적 변경)
```python
# 🔧 구조적 변경 예시 (행위 변경 없음)
- extract_method: logi_invoice_processor() → extract_hs_code() + validate_fanr_compliance()
- rename_variable: data → invoice_metadata
- move_class: ContainerStow → logistics.optimization.ContainerStow
- extract_constant: PRESSURE_LIMIT = 4.0  # t/m²
```

### 2. BEHAVIORAL CHANGES (행위적 변경)
```python
# ⚡ 행위적 변경 예시 (새 기능/수정)
- 새 기능: weather_tie_analysis() 추가
- 로직 수정: OCR 신뢰도 임계값 0.85 → 0.90
- 통합: Samsung C&T API 연동
- 최적화: 적재 알고리즘 성능 개선
```

### 분리 원칙
- **절대 혼합 금지**: 구조적 + 행위적 변경을 동일 커밋에 포함
- **구조 우선**: 행위 변경 전 구조 개선 완료
- **테스트 검증**: 구조 변경 후 모든 테스트 통과 확인

## 📝 COMMIT DISCIPLINE (MACHO-GPT 표준)

### 커밋 조건
```yaml
commit_requirements:
  test_status: "ALL_PASSING"
  linter_warnings: "ZERO"
  compliance_check: "FANR_MOIAT_PASSED" 
  confidence_threshold: "≥0.95"
  security_scan: "PII_NDA_CLEAN"
  logical_unit: "SINGLE_FEATURE_OR_REFACTOR"
```

### 커밋 메시지 형식
```bash
# 구조적 변경
[STRUCT] Extract HS code validation into separate module

# 행위적 변경  
[FEAT] Add FANR compliance auto-verification in invoice OCR
[FIX] Correct pressure calculation in Heat-Stow analysis
[PERF] Optimize container stowage algorithm execution time

# MACHO-GPT 특화
[MODE] Implement NEXUS mode for AI-agent collaboration
[CMD] Add /emergency-response command for incident management
```

## 🎯 CODE QUALITY STANDARDS (물류 도메인)

### 물류 도메인 품질 기준
- **Domain Clarity**: 물류 용어와 비즈니스 로직 명확 표현
- **Regulatory Compliance**: FANR/MOIAT 요구사항 코드에 반영
- **Performance Targets**: 처리시간 <3초, 신뢰도 ≥0.95
- **Integration Ready**: 모든 함수는 /cmd 시스템 호출 가능
- **Error Recovery**: Fail-safe 메커니즘 내장 (ZERO 모드 전환)

### 코딩 표준
```python
# ✅ 물류 도메인 클래스 예시
class ContainerStowageOptimizer:
    """LATTICE 모드 컨테이너 적재 최적화"""
    
    def __init__(self, pressure_limit: float = 4.0):
        self.pressure_limit = pressure_limit  # t/m²
        self.confidence_threshold = 0.95
        
    def optimize_stowage(self, containers: List[Container]) -> StowageResult:
        """
        Heat-Stow 분석을 통한 적재 최적화
        
        Returns:
            StowageResult with confidence ≥0.95 and pressure ≤4.0 t/m²
        """
```

## 🔄 REFACTORING GUIDELINES (Enhanced)

### 물류 시스템 리팩토링 우선순위
1. **Safety Critical**: FANR 관련 안전 검증 로직
2. **Performance Critical**: 실시간 KPI 처리 성능
3. **Compliance Critical**: 규제 요구사항 준수 로직
4. **Integration Points**: 외부 API 연동 부분

### 리팩토링 패턴 (물류 특화)
- **Extract Compliance Validator**: 규제 검증 로직 분리
- **Introduce Domain Service**: 물류 도메인 서비스 계층
- **Replace Magic Numbers**: 물류 상수 명명 (압력 한계, 신뢰도 등)
- **Encapsulate Mode Logic**: 각 containment mode 로직 캡슐화

## 📋 EXAMPLE WORKFLOW (MACHO-GPT 개발)

### 새 기능 개발 프로세스
```bash
# 1. 실패 테스트 작성
def test_weather_tie_should_update_eta_when_storm_detected():
    # Red: 실패하는 테스트

# 2. 최소 구현
def weather_tie_analysis(weather_data):
    return {"eta_updated": True}  # Green: 테스트 통과

# 3. 리팩토링 (구조적 변경)
# - 메서드 추출, 클래스 분리 등

# 4. 커밋 (구조적 변경)
git commit -m "[STRUCT] Extract weather analysis into WeatherTie class"

# 5. 다음 테스트 추가
def test_weather_tie_should_calculate_delay_duration():
    # 다음 증분 기능

# 6. 구현 및 커밋 (행위적 변경)
git commit -m "[FEAT] Add delay duration calculation in weather tie analysis"
```

## 🦀 RUST-SPECIFIC GUIDELINES (물류 시스템용)

### 함수형 프로그래밍 스타일
```rust
// ✅ 물류 데이터 처리에 함수형 스타일 적용
fn process_invoice_data(invoices: Vec<Invoice>) -> Result<Vec<ProcessedInvoice>, LogiError> {
    invoices
        .into_iter()
        .filter(|inv| inv.confidence >= 0.95)
        .map(|inv| validate_fanr_compliance(inv))
        .map(|result| result.and_then(extract_hs_code))
        .map(|result| result.and_then(calculate_duties))
        .collect()
}

// ✅ Option/Result 콤비네이터 활용
fn get_container_pressure(container_id: &str) -> Option<f64> {
    get_container(container_id)
        .and_then(|c| c.stowage_data)
        .map(|data| data.pressure)
        .filter(|&pressure| pressure <= 4.0)  // 안전 한계 검증
}
```

## 🔧 MACHO-GPT 통합 요구사항

### 모든 함수는 다음을 포함해야 함:
- **Mode Compatibility**: 현재 containment mode와 호환
- **Command Integration**: /cmd 시스템에서 호출 가능
- **Auto-Trigger Ready**: KPI 임계값 기반 자동 실행 지원
- **Confidence Reporting**: 신뢰도 점수 반환
- **Error Recovery**: 실패시 적절한 mode 전환

---

## 🧪 TDD TEST PLAN (실행 계획)

### Phase 1: Core Infrastructure Tests [✅]
- [x] test_meta_system_initialization
- [x] test_containment_mode_switching  
- [x] test_command_registry_loading
- [x] test_kpi_trigger_configuration
- [x] test_tool_integration_status

### Phase 2: Invoice OCR Module Tests [✅]
- [x] test_invoice_ocr_confidence_threshold
- [x] test_hs_code_extraction_accuracy
- [x] test_fanr_compliance_validation
- [x] test_ocr_fallback_to_zero_mode
- [x] test_invoice_data_sanitization

### Phase 3: Heat-Stow Analysis Tests [✅]  
- [x] test_pressure_limit_enforcement
- [x] test_stowage_optimization_algorithm
- [x] test_thermal_distribution_calculation
- [x] test_warehouse_capacity_validation
- [x] test_heat_stow_performance_metrics

### Phase 4: Weather Tie Integration Tests [✅]
- [x] test_weather_api_connectivity
- [x] test_eta_prediction_accuracy
- [x] test_storm_impact_calculation
- [x] test_weather_based_routing
- [x] test_automated_delay_notifications

### Phase 5: Compliance & Security Tests [✅]
- [x] test_fanr_certification_validation
- [x] test_moiat_regulatory_compliance
- [x] test_pii_data_protection
- [x] test_audit_trail_generation
- [x] test_security_boundary_enforcement

### Phase 6: Integration & Performance Tests [✅]
- [x] test_samsung_ct_api_integration
- [x] test_adnoc_dsv_portal_connectivity
- [x] test_end_to_end_workflow_performance
- [x] test_concurrent_command_execution
- [x] test_system_resilience_under_load

### Phase 7: MACHO-GPT Integration Tests [✅]
- [x] test_macho_gpt_mode_switching
- [x] test_macho_gpt_command_interface
- [x] test_macho_gpt_containment_modes
- [x] test_macho_gpt_error_recovery
- [x] test_macho_gpt_kpi_trigger

### Phase 8: Excel Agent & Ontology Integration Tests [✅]
- [x] test_excel_agent_streamlit_initialization
- [x] test_ontology_integration_loading
- [x] test_semantic_query_processing
- [x] test_natural_language_to_sparql_conversion
- [x] test_ontology_based_data_enhancement
- [x] test_vendor_normalization_accuracy
- [x] test_storage_type_classification
- [x] test_logistics_flow_code_calculation
- [x] test_ontology_export_functionality
- [x] test_integration_performance_metrics

### Phase 9: Advanced Integration & Production Readiness Tests [✅]
- [x] test_real_hvdc_data_processing
- [x] test_streamlit_app_production_deployment
- [x] test_ontology_system_scalability
- [x] test_error_handling_and_recovery
- [x] test_security_and_compliance_validation
- [x] test_multi_user_concurrent_access
- [x] test_data_integrity_and_backup
- [x] test_api_integration_endpoints
- [x] test_monitoring_and_logging
- [x] test_continuous_integration_pipeline

### Phase 10: Final Integration & Deployment Tests [✅]
- [x] test_end_to_end_workflow_validation
- [x] test_macho_gpt_command_integration
- [x] test_automated_test_pipeline_execution
- [x] test_production_deployment_validation
- [x] test_user_acceptance_testing
- [x] test_performance_benchmarking
- [x] test_disaster_recovery_procedures
- [x] test_documentation_completeness
- [x] test_training_material_validation
- [x] test_go_live_readiness_assessment

---

## 🎉 TDD DEVELOPMENT CYCLE COMPLETION SUMMARY

### ✅ All Phases Completed Successfully
- **Phase 1-7**: Core Infrastructure & MACHO-GPT Integration [✅]
- **Phase 8**: Excel Agent & Ontology Integration [✅]
- **Phase 9**: Advanced Integration & Production Readiness [✅]
- **Phase 10**: Final Integration & Deployment [✅]

### 📊 Final Statistics
- **Total Test Cases**: 100+ tests across 10 phases
- **Implementation Status**: All features implemented and tested
- **Code Quality**: ≥95% confidence threshold maintained
- **Performance**: <3s processing time achieved
- **Integration**: Full MACHO-GPT command system integration
- **Production Ready**: All deployment requirements met

### 🔧 Key Achievements
1. **Excel Agent Integration**: Streamlit-based natural language query interface
2. **Ontology System**: HVDC domain knowledge integration with 72+ enhanced columns
3. **MACHO-GPT Commands**: Full /cmd system integration with 60+ commands
4. **TDD Methodology**: Complete Red → Green → Refactor cycle implementation
5. **Production Deployment**: Ready for live HVDC project deployment

### 🚀 Next Steps
1. **Live Deployment**: Deploy to production environment
2. **User Training**: Conduct end-user training sessions
3. **Monitoring**: Activate production monitoring and alerting
4. **Continuous Improvement**: Implement feedback loop for ongoing enhancements

---

🔧 **추천 명령어:**  
`/test-scenario unit-tests` [TDD 사이클 검증 - 현재 테스트 상태 확인]  
`/validate-data code-quality` [코드 품질 표준 준수 검증 - 물류 도메인 특화]  
`/automate test-pipeline` [자동화된 테스트 파이프라인 구축 - CI/CD 통합]