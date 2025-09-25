# 🦐 Shrimp Task Manager - HVDC Project 설치 가이드

## 📋 개요

Shrimp Task Manager는 HVDC 프로젝트를 위한 MACHO-GPT 통합 프로젝트 관리 시스템입니다. AI와 협력하여 복잡한 물류 프로젝트를 효율적으로 관리할 수 있습니다.

## 🎯 주요 기능

- **작업 관리**: 생성, 조회, 업데이트, 삭제
- **MACHO-GPT 통합**: 6가지 containment mode 지원
- **KPI 분석**: 실시간 성과 지표 모니터링
- **자동화**: AI 기반 작업 최적화 및 추천
- **물류 특화**: 창고, 운송, 분석 카테고리 지원

## 🚀 설치 단계

### 1. 필수 요구사항

- **Python**: 3.8 이상
- **SQLite**: 기본 포함
- **Git**: 소스 코드 관리용

### 2. 파일 구조 확인

```
HVDC_PJT/
├── src/
│   ├── shrimp_task_manager.py      # 메인 서버
│   ├── macho_gpt.py               # MACHO-GPT 핵심 클래스
│   └── mcp_server_config.json     # MCP 서버 설정
├── hvdc_tasks.db                  # 작업 데이터베이스 (자동 생성)
└── shrimp_task_manager.log        # 로그 파일 (자동 생성)
```

### 3. 실행 방법

#### 기본 실행

```bash
cd src
python shrimp_task_manager.py
```

#### MCP 서버로 실행

```bash
# Cursor IDE에서 MCP 서버 설정
# mcp_server_config.json 파일을 Cursor 설정에 추가
```

## 📊 사용 방법

### 1. 작업 관리 명령어

#### 작업 생성

```python
from src.shrimp_task_manager import ShrimpTaskManager

task_manager = ShrimpTaskManager()

new_task = task_manager.create_task({
    'title': 'HVDC 창고 최적화',
    'description': 'DSV 창고별 입출고 패턴 분석',
    'priority': 'high',
    'category': 'warehouse',
    'assignee': 'MACHO-GPT',
    'tags': ['HVDC', 'DSV', '창고분석']
})
```

#### 작업 조회

```python
# 모든 작업 조회
tasks = task_manager.list_tasks()

# 필터링된 작업 조회
high_priority_tasks = task_manager.list_tasks({
    'priority': 'high',
    'category': 'warehouse'
})
```

#### 작업 업데이트

```python
task_manager.update_task(task_id, {
    'status': 'in_progress',
    'confidence': 0.95
})
```

### 2. MACHO-GPT 통합

#### 모드 전환

```python
from src.macho_gpt import mode_manager

result = mode_manager.switch_mode('LATTICE')
print(f"모드 전환: {result['previous_mode']} → {result['current_mode']}")
```

#### 물류 작업 실행

```python
from src.macho_gpt import LogiMaster, ContainerStow, WeatherTie

# 송장 OCR 처리
logi_master = LogiMaster()
result = logi_master.invoice_audit('invoice.pdf')

# Heat-Stow 분석
container_stow = ContainerStow()
result = container_stow.heat_stow_analysis(container_data)

# 창고 용량 분석
warehouse_data = {'capacity': 1000, 'current_usage': 850}
whf_result = container_stow.whf_capacity_check(warehouse_data)

# 날씨 영향 분석
weather_tie = WeatherTie()
result = weather_tie.check_weather_conditions('AEJEA')
```

### 3. 분석 및 리포팅

#### 작업 분석

```python
analytics = task_manager.get_task_analytics()
print(f"총 작업 수: {analytics['total_tasks']}")
print(f"완료율: {analytics['completion_rate']}%")
print(f"상태별 분포: {analytics['status_distribution']}")
```

#### MACHO-GPT 통합 분석

```python
integration = task_manager.integrate_with_macho_gpt(task_id)
print(f"권장 모드: {integration['macho_integration']['mode']}")
print(f"신뢰도: {integration['macho_integration']['confidence']}")
```

## 🔧 MCP 서버 설정

### Cursor IDE 설정

1. **설정 파일 열기**: `Ctrl+,` (설정)
2. **MCP 서버 추가**: 다음 설정을 추가

```json
{
  "mcpServers": {
    "shrimp-task-manager": {
      "command": "python",
      "args": ["src/shrimp_task_manager.py"],
      "env": {
        "PYTHONPATH": ".",
        "HVDC_PROJECT_MODE": "PRODUCTION"
      }
    }
  }
}
```

### 사용 가능한 명령어

#### 작업 관리

- `/task_manager list_tasks` - 모든 작업 조회
- `/task_manager create_task` - 새 작업 생성
- `/task_manager update_task` - 작업 업데이트
- `/task_manager delete_task` - 작업 삭제
- `/task_manager get_analytics` - 작업 분석

#### MACHO-GPT 통합

- `/macho_gpt switch_mode` - 모드 전환
- `/macho_gpt invoice_audit` - 송장 OCR 처리
- `/macho_gpt predict_eta` - ETA 예측
- `/macho_gpt heat_stow_analysis` - Heat-Stow 분석
- `/macho_gpt weather_check` - 날씨 확인
- `/macho_gpt generate_kpi` - KPI 생성

## 📈 Containment Modes

### 1. PRIME 모드

- **용도**: 일반 물류 작업
- **특징**: 기본 모드, 모든 기능 활성화
- **신뢰도**: ≥0.90

### 2. LATTICE 모드

- **용도**: 창고 및 적재 최적화
- **특징**: Heat-Stow 분석, 압력 제한 4t/m²
- **신뢰도**: ≥0.95

### 3. ORACLE 모드

- **용도**: 데이터 분석 및 예측
- **특징**: 실시간 데이터 검증, 예측 모델
- **신뢰도**: ≥0.92

### 4. RHYTHM 모드

- **용도**: KPI 모니터링 및 알림
- **특징**: 실시간 KPI 추적, 자동 알림
- **신뢰도**: ≥0.91

### 5. COST-GUARD 모드

- **용도**: 비용 관리 및 승인
- **특징**: 비용 검증, 승인 워크플로우
- **신뢰도**: ≥0.93

### 6. ZERO 모드

- **용도**: 오류 복구 및 안전 모드
- **특징**: Fail-safe, 수동 개입 필요
- **신뢰도**: 0.0 (수동 모드)

## 🔍 문제 해결

### 일반적인 문제

#### 1. 데이터베이스 오류

```bash
# 데이터베이스 재생성
rm hvdc_tasks.db
python shrimp_task_manager.py
```

#### 2. 로그 확인

```bash
# 로그 파일 확인
tail -f shrimp_task_manager.log
```

#### 3. MCP 서버 연결 오류

- Python 경로 확인
- 환경 변수 설정 확인
- 포트 충돌 확인

### 성능 최적화

#### 1. 데이터베이스 최적화

```sql
-- 인덱스 생성
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_category ON tasks(category);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

#### 2. 로그 로테이션

- 로그 파일 크기 제한: 10MB
- 백업 파일 수: 5개

## 📞 지원 및 문의

### 로그 분석

```python
import logging
logging.getLogger('shrimp_task_manager').setLevel(logging.DEBUG)
```

### 성능 모니터링

```python
# KPI 메트릭 확인
analytics = task_manager.get_task_analytics()
print(f"처리 성능: {analytics['completion_rate']}%")
```

## 🎯 추천 워크플로우

### 1. 새 프로젝트 시작

1. `/task_manager create_task` - 프로젝트 작업 생성
2. `/macho_gpt switch_mode PRIME` - 기본 모드 설정
3. `/task_manager get_analytics` - 초기 상태 확인

### 2. 창고 최적화 작업

1. `/macho_gpt switch_mode LATTICE` - LATTICE 모드 전환
2. `/macho_gpt heat_stow_analysis` - 적재 분석
3. `/task_manager update_task` - 결과 업데이트

### 3. KPI 모니터링

1. `/macho_gpt switch_mode RHYTHM` - RHYTHM 모드 전환
2. `/macho_gpt generate_kpi` - KPI 생성
3. `/task_manager get_analytics` - 성과 분석

---

🔧 **추천 명령어:**
`/task_manager list_tasks` [모든 작업 조회 - 현재 상태 확인]
`/macho_gpt switch_mode PRIME` [기본 모드 설정 - 안정적인 작업 환경]
`/task_manager get_analytics` [작업 분석 - 성과 지표 확인]

---

## 🧠 Multi-Model Coding Script Template (Cursor 최적화)

### 1️⃣ Task Objective

- 구현할 기능 요약: 예) PDF 인보이스 OCR 후 CSV로 정제
- 사용 언어: Python
- 환경: Cursor + Terminal
- 외부 모듈: pdfplumber, pandas, openai, pyperclip 등

---

### 2️⃣ 모델 활용 전략

| 단계 | 모델       | 역할 및 특징                               |
| ---- | ---------- | ------------------------------------------ |
| A    | O3         | 빠른 아이디어 스케치, 구조 설계            |
| B    | Gemini 2.5 | 구조 보완, 오류에 강함, 함수 재정리        |
| C    | O3 Pro     | 성능 향상 코드 리팩토링, Prompt 최적화     |
| D    | Cursor     | 실행 및 디버깅, Chat 기록 연동 자동화 사용 |

---

### 3️⃣ 단계별 스크립트 운영 계획

#### Step A. O3 (초안 생성)

> Prompt 예시: text "PDF에서 인보이스 데이터를 추출하고, 각 항목을 JSON으로 구조화하는 Python 코드를 작성해줘."
> ✅ 코드 초안 확보
> 🔁 필요 시: "이 코드에서 수량이 없는 경우 예외처리도 추가해줘"

#### Step B. Gemini 2.5 (보완)

> Prompt 예시: "O3가 만든 코드에 대해 에러 핸들링과 주석을 추가해줘. 그리고 모듈 구조로 리팩토링해줘."
> ✅ 함수 분리 및 에러 처리 보강
> ✅ Chat Prompt 개선
> 🔁 필요 시 "OCR 실패 시 경고 메시지 추가해줘"

#### Step C. O3 Pro (최적화)

> Prompt 예시: "성능 향상 및 메모리 효율을 고려해 최적화해줘. Pandas 속도 개선 포함해서."
> ✅ 성능·메모리 개선
> ✅ 반복문 최적화, 조건문 간소화
> 🔁 필요 시: "대용량 PDF 대응 구조로 바꿔줘"

#### Step D. Cursor (실행/디버깅)

- Terminal에서 실행
- Chat 연동 단축키 사용 (예: Ctrl + /)
- 코드 오류 발생 시:
  "이 오류 원인을 분석하고 수정 코드를 제시해줘."

### 4️⃣ 오류 대응 루프

┌──────────┐
│ Cursor 실행 │
└────┬─────┘
     ↓ 오류 발생
┌────┴─────┐
│ 모델 재질문 (O3 → Gemini) │
└────┬─────┘
     ↓ 수정 적용
     ← 반복 (완료 시까지)

### 5️⃣ 확장 명령어 (추천)

| 명령               | 설명                                    |
| ------------------ | --------------------------------------- |
| /debug-loop        | 반복 오류 시 자동 모델 순환 디버깅 구조 |
| /optimize-function | 함수 단위 성능 개선 요청                |
| /docstring-gen     | 전체 함수에 주석 자동 생성              |

### ✅ 완료 체크리스트

- [ ] 코드 실행 성공
- [ ] 주석/예외처리 포함
- [ ] 테스트 케이스 포함
- [ ] RePrompt용 마크업 저장

---

### 📂 활용 방법 (Cursor에서)

1. 위 스크립트를 Markdown 파일로 저장 → README.md 또는 00_MODEL_FLOW.md
2. 코드 작성 시 모델에 위 전략 적용
3. 문제 발생 시 해당 단계 Prompt를 복사해 GPT에 붙여넣기
4. 모든 내용은 Cursor 내 GPT창 + 코드창 사이에서 반복 가능

---

### ✳️ 다음 단계 제안

- 🔁 스크립트 템플릿을 /save_template 으로 저장
- 💡 Slack or TG로 자동화 → LLM별 반응 비교 결과 저장
- 📊 logi-master 연동하여 자동 코드 검증 추가

---

원하시면 이 내용을 .md 파일이나 .py 코드 주석 형식으로 변환해드릴 수도 있습니다.
→ 어떤 기능을 이 워크플로에 적용할지 알려주시면 바로 맞춤 설정도 가능합니다.
