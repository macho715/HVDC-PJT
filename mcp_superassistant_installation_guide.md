# 🔌 MCP SuperAssistant 설치 가이드 - HVDC 프로젝트

## 📋 개요

**MCP SuperAssistant**는 Chrome 확장 프로그램으로, Model Context Protocol (MCP)의 강력한 기능을 AI 채팅 플랫폼에 통합합니다. HVDC 프로젝트의 물류 분석 및 시각화를 위한 고급 도구입니다.

---

## 🚀 설치 방법

### 1. **브라우저 확장 스토어에서 설치 (권장)**

#### Chrome/Chromium 기반 브라우저
1. [MCP SuperAssistant Chrome Web Store](https://chrome.google.com/webstore/detail/mcp-superassistant) 방문
2. "Chrome에 추가" 버튼 클릭
3. 설치 확인

#### Firefox
1. [MCP SuperAssistant Firefox Add-ons](https://addons.mozilla.org/firefox/addon/mcp-superassistant) 방문
2. "Firefox에 추가" 버튼 클릭
3. 설치 확인

**호환 브라우저:**
- ✅ Chrome, Firefox
- ✅ Edge, Brave, Arc (Chromium 기반)
- ✅ 기타 Chromium 기반 브라우저

### 2. **수동 설치 (개발자 모드)**

**최신 버전 지원** - 개발자 및 최신 기능이 필요한 사용자용

```bash
# 1. 저장소 클론 또는 GitHub에서 zip 다운로드
git clone https://github.com/srbhptl39/mcp-superassistant.git
# 또는 GitHub에서 zip 파일 다운로드

# 2. 압축 해제
# 3. Chrome에서 chrome://extensions/ 접속
# 4. 개발자 모드 활성화 (우상단 토글)
# 5. "압축해제된 확장 프로그램을 로드합니다" 클릭
# 6. 압축 해제한 폴더 선택
```

**지원 AI 플랫폼:**
- ✅ ChatGPT
- ✅ Perplexity
- ✅ Gemini
- ✅ Grok
- ✅ AIStudio

---

## ⚙️ 설정 구성

### 1. **config.json 생성**

HVDC 프로젝트용 MCP 서버 설정:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\cursor-mcp\\HVDC_PJT"
      ]
    },
    "json": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-json"
      ]
    },
    "calculator": {
      "command": "npx", 
      "args": [
        "-y",
        "@modelcontextprotocol/server-calculator"
      ]
    },
    "deepview": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-deepview"
      ]
    },
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-context7"
      ]
    },
    "android": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-android"
      ]
    },
    "brightdata": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "brightdata/mcp"
      ]
    },
    "vlmrun": {
      "command": "docker",
      "args": [
        "run", 
        "--rm",
        "vlmrun/mcp"
      ]
    },
    "gadmin": {
      "command": "docker",
      "args": [
        "run",
        "--rm", 
        "gadmin/mcp"
      ]
    },
    "email": {
      "command": "pipx",
      "args": [
        "run",
        "mcp-email-server",
        "ui"
      ]
    }
  }
}
```

### 2. **기존 설정 파일 활용**

#### Claude 설정 파일 사용
```bash
# macOS
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ./config.json

# Windows  
copy "%APPDATA%\Claude\claude_desktop_config.json" config.json
```

#### Cursor 설정 파일 사용
```bash
# macOS
cp ~/.cursor/mcp.json ./config.json

# Windows
copy "%APPDATA%\Cursor\mcp.json" config.json
```

---

## 🔧 프록시 서버 설정

### 1. **사전 요구사항**

```bash
# Node.js v16 이상 설치 확인
node --version  # v16.0.0 이상 필요

# npx 확인 (Node.js와 함께 설치됨)
npx --version
```

### 2. **프록시 서버 실행**

#### 커스텀 설정으로 실행
```bash
# HVDC 프로젝트 디렉토리에서
cd C:\cursor-mcp\HVDC_PJT

# 프록시 서버 시작
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./config.json
```

#### 기본 설정으로 실행
```bash
# 기본 설정 사용
npx @srbhptl39/mcp-superassistant-proxy@latest
```

---

## 🎯 HVDC 프로젝트 특화 설정

### 1. **물류 분석용 MCP 서버 우선순위**

```json
{
  "mcpServers": {
    "deepview": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-deepview"],
      "priority": "high"
    },
    "calculator": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-calculator"],
      "priority": "high"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\cursor-mcp\\HVDC_PJT"],
      "priority": "medium"
    },
    "json": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-json"],
      "priority": "medium"
    }
  }
}
```

### 2. **MACHO-GPT 통합 설정**

```json
{
  "mcpServers": {
    "macho_gpt": {
      "command": "python",
      "args": ["hvdc_macho_gpt/src/logi_meta_fixed.py"],
      "env": {
        "MACHO_MODE": "PRIME",
        "CONFIDENCE_THRESHOLD": "0.95"
      }
    }
  },
  "integrations": {
    "samsung_ct": true,
    "adnoc_dsv": true,
    "weather_api": true,
    "port_api": true
  }
}
```

---

## 🔍 설치 검증

### 1. **MCP 서버 상태 확인**

```bash
# 실행 중인 MCP 서버 확인
tasklist | findstr "node.exe"
tasklist | findstr "docker.exe"

# 포트 사용 현황 확인
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8080"
```

### 2. **브라우저 확장 프로그램 테스트**

1. Chrome에서 `chrome://extensions/` 접속
2. MCP SuperAssistant 활성화 확인
3. ChatGPT 또는 다른 AI 플랫폼에서 사이드바 표시 확인

### 3. **기능 테스트**

```bash
# DeepView MCP 테스트
npx @modelcontextprotocol/server-deepview stdio

# Calculator MCP 테스트  
npx @modelcontextprotocol/server-calculator stdio

# Filesystem MCP 테스트
npx @modelcontextprotocol/server-filesystem stdio C:\cursor-mcp\HVDC_PJT
```

---

## 🚨 문제 해결

### 1. **Node.js 관련 문제**

```bash
# Node.js 버전 확인
node --version

# npm 캐시 정리
npm cache clean --force

# npx 재설치
npm install -g npx
```

### 2. **Docker 관련 문제**

```bash
# Docker Desktop 시작 확인
docker --version

# Docker 서비스 상태 확인
docker ps

# Docker 이미지 풀
docker pull brightdata/mcp
docker pull vlmrun/mcp
docker pull gadmin/mcp
```

### 3. **pipx 관련 문제**

```bash
# pipx 설치 (Windows)
python -m pip install --user pipx
python -m pipx ensurepath

# pipx 환경변수 설정
set PATH=%PATH%;%USERPROFILE%\.local\bin

# MCP Email 서버 설치
pipx install mcp-email-server
```

### 4. **포트 충돌 문제**

```bash
# 포트 사용 프로세스 확인
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8080"

# 프로세스 종료
taskkill /F /PID [프로세스ID]
```

---

## 📊 성능 최적화

### 1. **메모리 사용량 최적화**

```json
{
  "performance": {
    "memory_limit": "100MB",
    "cache_enabled": true,
    "compression": true,
    "batch_size": 1000
  }
}
```

### 2. **응답 시간 개선**

```json
{
  "optimization": {
    "parallel_processing": true,
    "data_preloading": true,
    "chart_caching": true,
    "lazy_rendering": true
  }
}
```

---

## 🔧 고급 설정

### 1. **보안 설정**

```json
{
  "security": {
    "allowed_domains": ["chat.openai.com", "perplexity.ai"],
    "file_access": {
      "allowed_paths": ["C:\\cursor-mcp\\HVDC_PJT"],
      "blocked_extensions": [".exe", ".bat", ".cmd"]
    },
    "api_rate_limit": 100
  }
}
```

### 2. **로깅 설정**

```json
{
  "logging": {
    "level": "info",
    "file": "mcp_superassistant.log",
    "max_size": "10MB",
    "retention": "7 days"
  }
}
```

---

## 📋 설치 체크리스트

### ✅ 기본 설치
- [ ] Node.js v16+ 설치
- [ ] 브라우저 확장 프로그램 설치
- [ ] config.json 생성
- [ ] 프록시 서버 실행

### ✅ MCP 서버 설정
- [ ] DeepView MCP (93MB 메모리)
- [ ] Calculator MCP
- [ ] Filesystem MCP
- [ ] JSON MCP
- [ ] Context7 MCP
- [ ] Android MCP

### ✅ Docker 서버 (선택사항)
- [ ] Docker Desktop 시작
- [ ] Bright Data MCP
- [ ] VLM Run MCP
- [ ] Google Admin MCP

### ✅ pipx 서버 (선택사항)
- [ ] pipx 설치
- [ ] Email MCP 서버

### ✅ 통합 테스트
- [ ] 브라우저 확장 프로그램 활성화
- [ ] AI 플랫폼에서 사이드바 확인
- [ ] MCP 서버 연결 테스트
- [ ] 파일 시스템 접근 테스트

---

## 🎯 HVDC 프로젝트 활용 시나리오

### 1. **물류 분석 (DeepView MCP)**
- Sankey Flow Chart 생성
- Treemap 비용 분석
- 3D 창고 지도 시각화

### 2. **계산 분석 (Calculator MCP)**
- 비용 계산 및 최적화
- 용량 예측 모델링
- KPI 지표 계산

### 3. **파일 관리 (Filesystem MCP)**
- Excel 파일 분석
- 보고서 자동 생성
- 데이터 백업 및 동기화

### 4. **JSON 데이터 처리 (JSON MCP)**
- API 응답 처리
- 데이터 변환 및 매핑
- 설정 파일 관리

---

**© 2025 MACHO-GPT v3.4-mini | MCP SuperAssistant 설치 가이드** 