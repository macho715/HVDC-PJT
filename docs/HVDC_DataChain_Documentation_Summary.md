# HVDC DataChain 문서 요약

## 📚 생성된 문서 목록

### 1. HVDC_DataChain_README.md
**목적**: 시스템 전체 개요 및 빠른 시작 가이드
**내용**:
- 🚀 빠른 시작 (설치 및 실행)
- 📊 시스템 개요 및 주요 기능
- 🏗️ 시스템 구조 및 파일 구조
- 🔧 핵심 기능 설명
- 📊 처리 결과 예시
- 🚀 사용 방법 (전체/개별 테스트)
- 🔧 커스터마이징 가이드
- ⚠️ 주의사항
- 📈 성능 최적화

### 2. HVDC_DataChain_Integration_Guide.md
**목적**: 상세한 통합 가이드 및 사용법
**내용**:
- 📋 시스템 아키텍처
- 📁 파일 구조 상세 설명
- 🚀 환경 설정 및 사용 방법
- 📊 처리 결과 예시
- 🔧 커스터마이징 방법
- 📈 성능 최적화 방안
- 🛠️ 문제 해결 가이드
- 📋 체크리스트

### 3. HVDC_DataChain_Core_Logic.md
**목적**: 핵심 로직 및 알고리즘 상세 분석
**내용**:
- 🧠 핵심 로직 아키텍처
- 🔧 핵심 함수 분석
- 📈 데이터 플로우 상세
- 🔍 검증 로직
- 🎯 핵심 알고리즘
- 🔧 확장 가능한 구조

### 4. HVDC_DataChain_Important_Notes.md
**목적**: 중요 주의사항 및 운영 가이드
**내용**:
- ⚠️ 중요 주의사항
- 🚨 오류 처리 가이드
- 📋 운영 체크리스트
- 🔧 커스터마이징 가이드
- 📊 성능 지표
- 🔗 의존성 관리
- 🛡️ 보안 고려사항
- 📞 지원 및 문의

## 🎯 문서별 사용 시나리오

### 초보자용
**추천 문서**: `HVDC_DataChain_README.md`
- 시스템 전체 이해
- 빠른 시작 및 기본 사용법
- 핵심 기능 파악

### 개발자용
**추천 문서**: `HVDC_DataChain_Core_Logic.md`
- 핵심 로직 이해
- 알고리즘 분석
- 확장 개발

### 운영자용
**추천 문서**: `HVDC_DataChain_Important_Notes.md`
- 운영 주의사항
- 오류 처리
- 성능 모니터링

### 통합 담당자용
**추천 문서**: `HVDC_DataChain_Integration_Guide.md`
- 상세한 통합 가이드
- 커스터마이징 방법
- 문제 해결

## 📊 핵심 정보 요약

### 시스템 성능
- **처리 데이터**: 8,244행
- **처리 시간**: 약 80초
- **성공률**: 100%
- **정확도**: 벤더 분류 100%, 장비 분류 99%+

### 주요 기능
1. **데이터 정규화**: 컬럼명, 타입, NaN 처리
2. **벤더 정규화**: HVDC CODE 패턴 기반 식별
3. **장비 분류**: Description 기반 자동 분류
4. **이용률 계산**: 실시간 KPI 산출
5. **Excel 리포트**: 자동화된 분석 리포트

### 처리 결과
- **HITACHI**: 5,552건 (평균 이용률 100.00%)
- **SIEMENS**: 2,227건 (평균 이용률 92.11%)
- **송장**: 465건 (총 세금 3,204,916.34)

## 🔧 핵심 코드 패턴

### 데이터 정규화
```python
def normalize_column_names(df):
    # 특수문자 제거 및 언더스코어 변환
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
    return cleaned.lower()
```

### 벤더 정규화
```python
def normalize_vendor(hvdc_code):
    hvdc_str = str(hvdc_code).upper()
    if 'HE' in hvdc_str: return 'HITACHI'
    elif 'SIM' in hvdc_str: return 'SIEMENS'
    else: return 'OTHER'
```

### DataChain 파이프라인
```python
processed_chain = (chain
    .map(normalized_vendor=normalize_vendor, params=['hvdc_code'])
    .map(equipment_class=classify_equipment, params=['description'])
    .map(utilization_rate=calculate_utilization, params=['cbm', 'n_w_kgs'])
)
```

## ⚠️ 중요 주의사항

### 데이터 처리
- **NaN 값**: 모든 NaN 값은 빈 문자열로 변환
- **컬럼명**: 특수문자는 언더스코어로 변환
- **타입**: 모든 반환값은 문자열로 통일

### 성능
- **메모리**: 대용량 데이터 처리 시 모니터링 필요
- **처리 시간**: 8,244행 처리 시 약 80초
- **파일 저장**: HVDC_PJT 디렉토리에 자동 저장

### 오류 처리
- **파일 없음**: 테스트 스킵
- **패턴 매칭**: 매칭 실패 시 'OTHER' 분류
- **계산 오류**: 실패 시 0% 반환

## 🚀 다음 단계

### 단기 목표
1. **성능 최적화**: 처리 속도 200행/초 이상
2. **메모리 최적화**: 사용량 50MB 이하
3. **확장성**: 100,000행 이상 처리

### 중기 목표
1. **실시간 모니터링**: KPI 대시보드 연동
2. **MCP 서버 배포**: DataChain 파이프라인 노출
3. **자동화**: 정기적인 데이터 처리 자동화

### 장기 목표
1. **AI 통합**: MACHO-GPT와 완전 통합
2. **예측 분석**: 머신러닝 기반 예측 기능
3. **클라우드 배포**: 확장 가능한 클라우드 인프라

## 📞 지원 정보

### 기술 지원
- **담당자**: MACHO-GPT v3.4-mini
- **문서 위치**: HVDC_PJT/docs/
- **코드 위치**: datachain-main/

### 문제 해결 순서
1. 오류 로그 확인
2. 데이터 상태 검증
3. 시스템 리소스 확인
4. 관련 문서 참조
5. 기술 지원 문의

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-07-18  
**작성자**: MACHO-GPT v3.4-mini  
**검토자**: HVDC 프로젝트팀 