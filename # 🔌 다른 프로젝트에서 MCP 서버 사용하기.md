# 🔌 다른 프로젝트에서 MCP 서버 사용하기

## 📋 개요

현재 설정된 MCP 서버들을 다른 Cursor IDE 프로젝트에서도 사용할 수 있습니다. MCP 서버는 전역적으로 설치되어 모든 프로젝트에서 공유할 수 있습니다.

## 🎯 현재 설정된 MCP 서버들

현재 프로젝트에는 다음 MCP 서버들이 설정되어 있습니다:

| 서버명 | 기능 | 설명 |
|-------|------|------|
| **filesystem** | 파일 시스템 작업 | 파일 읽기/쓰기/생성 |
| **playwright** | 웹 브라우저 자동화 | 웹 스크래핑, 테스팅 |
| **win-cli** | Windows CLI 작업 | PowerShell 명령 실행 |
| **desktop-commander** | 데스크톱 자동화 | 키보드/마우스 제어 |
| **context7** | 컨텍스트 관리 | 문서 검색 및 쿼리 |
| **seq-think** | 구조화된 사고 | 체계적 문제 해결 |
| **brave-search** | 웹 검색 | 실시간 검색 기능 |

## 🚀 방법 1: Cursor IDE 글로벌 설정 (권장)

### 1단계: Cursor 설정 파일 위치 찾기

```powershell
# Windows에서 Cursor 설정 파일 경로
%APPDATA%\Cursor\User\settings.json
```

### 2단계: 현재 설정 복사

현재 프로젝트의 `cursor-settings-phase3-complete.json` 내용을 글로벌 설정에 추가:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/c"],
      "description": "File system operations MCP server"
    },
    "playwright": {
      "command": "npx", 
      "args": ["-y", "@executeautomation/playwright-mcp-server"],
      "description": "Web browser automation MCP server"
    },
    "win-cli": {
      "command": "npx",
      "args": ["-y", "@simonb97/server-win-cli"],
      "description": "Windows CLI operations MCP server"
    },
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander"],
      "description": "Desktop automation MCP server"
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "description": "Context management MCP server"
    },
    "seq-think": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking", "--port", "8090"],
      "description": "Structured reasoning MCP server"
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search", "--port", "8091", "--api-key", "${BRAVE_API_KEY}"],
      "description": "Live web search MCP server"
    }
  }
}
```

### 3단계: 환경 변수 설정

```powershell
# Brave Search API 키 설정 (시스템 환경 변수)
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "your-api-key-here", "User")
```

## 🔧 방법 2: 프로젝트별 설정

### 1단계: 새 프로젝트에 설정 파일 복사

```powershell
# 새 프로젝트 폴더로 이동
cd "C:\path\to\your\new\project"

# 설정 파일 복사
copy "C:\cursor-mcp\cursor-settings-phase3-complete.json" ".\.cursor\settings.json"
```

### 2단계: 프로젝트별 환경 변수 설정

새 프로젝트에서 `.env` 파일 생성:

```env
BRAVE_API_KEY=your-api-key-here
```

## 🛠️ 방법 3: 자동 설정 스크립트 사용

현재 프로젝트의 스크립트를 사용해서 다른 프로젝트에 적용:

```powershell
# 현재 cursor-mcp 폴더에서 실행
.\apply-phase3-settings-fixed.ps1

# 또는 보안 설정 포함
.\apply-secure-settings-fixed.ps1
```

## 📋 단계별 설정 가이드

### 1단계: 환경 준비

```powershell
# Node.js 및 npm 확인
node --version
npm --version

# Cursor IDE 버전 확인 (최신 버전 권장)
```

### 2단계: API 키 설정

```powershell
# Brave Search API 키 설정
$env:BRAVE_API_KEY = "your-api-key-here"
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "your-api-key-here", "User")
```

### 3단계: Cursor 설정 적용

**방법 A: 수동 설정**
1. Cursor IDE에서 `Ctrl+Shift+P`
2. "Preferences: Open Settings (JSON)" 검색
3. MCP 서버 설정 추가

**방법 B: 설정 파일 직접 편집**
```powershell
# Cursor 사용자 설정 파일 열기
notepad "%APPDATA%\Cursor\User\settings.json"
```

### 4단계: 설정 확인

```powershell
# Cursor IDE 재시작 후 확인
# AI 채팅에서 다음 명령어로 테스트:
```

```
@filesystem ls
```
```
@playwright Navigate to https://google.com
```
```
@seq-think Analyze this problem step by step
```

## 🔍 테스트 방법

### 기본 기능 테스트

```
# 파일 시스템 테스트
@filesystem Create a test file with hello world content

# 웹 검색 테스트  
@brave-search Search for latest JavaScript frameworks

# 구조화된 사고 테스트
@seq-think How to build a REST API step by step
```

### 통합 워크플로 테스트

```
Use @seq-think to plan building a web scraper, then @playwright to implement it, and @filesystem to save results
```

## ⚡ 빠른 설정 명령어

새 프로젝트에서 한 번에 설정하기:

```powershell
# 1. 환경 변수 설정
$env:BRAVE_API_KEY = "your-api-key-here"

# 2. Cursor 설정 폴더 생성
mkdir .cursor -ErrorAction SilentlyContinue

# 3. 설정 파일 복사 (현재 cursor-mcp 프로젝트에서)
copy "cursor-settings-phase3-complete.json" ".cursor\settings.json"

# 4. Cursor IDE 재시작
```

## 🚨 주의사항

### 보안 고려사항
- API 키를 코드에 하드코딩하지 마세요
- 환경 변수나 보안 저장소 사용 권장
- 공개 저장소에 설정 파일 업로드 주의

### 성능 최적화
- 사용하지 않는 MCP 서버는 비활성화
- 포트 충돌 방지를 위해 각 서버마다 다른 포트 사용
- 메모리 사용량 모니터링

### 호환성
- Cursor IDE 최신 버전 사용 권장
- Node.js 18+ 버전 필요
- Windows PowerShell 또는 WSL 환경

## 🔧 문제 해결

### 자주 발생하는 문제

**1. MCP 서버가 인식되지 않는 경우**
```powershell
# Cursor IDE 완전 재시작
taskkill /f /im "Cursor.exe"
# 다시 Cursor 실행
```

**2. API 키 관련 오류**
```powershell
# 환경 변수 확인
echo $env:BRAVE_API_KEY
# 재설정
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "new-key", "User")
```

**3. 포트 충돌**
```powershell
# 사용 중인 포트 확인
netstat -ano | findstr :8090
netstat -ano | findstr :8091
# 충돌하는 프로세스 종료
```

## 📊 성능 모니터링

### 리소스 사용량 확인

```powershell
# Node.js 프로세스 확인
Get-Process -Name "node" | Format-Table ProcessName, Id, CPU, WorkingSet

# MCP 서버 상태 확인
netstat -ano | findstr :809
```

### 로그 확인

```powershell
# Cursor 로그 폴더
%APPDATA%\Cursor\logs

# 최근 로그 확인
Get-Content "%APPDATA%\Cursor\logs\main.log" -Tail 50
```

## 🎉 성공 확인

모든 설정이 완료되면 Cursor IDE에서 다음 기능들을 사용할 수 있습니다:

- ✅ `@filesystem` - 파일 작업
- ✅ `@playwright` - 웹 자동화  
- ✅ `@win-cli` - Windows 명령
- ✅ `@desktop-commander` - 데스크톱 제어
- ✅ `@context7` - 문서 검색
- ✅ `@seq-think` - 구조화된 사고
- ✅ `@brave-search` - 웹 검색

## 📚 추가 자료

- [Cursor MCP 공식 문서](https://docs.cursor.com/context/model-context-protocol)
- [MCP 서버 목록](https://github.com/modelcontextprotocol/servers)
- [Brave Search API 문서](https://brave.com/search/api/)

---

**💡 팁**: 여러 프로젝트에서 동일한 MCP 서버를 사용하려면 글로벌 설정을 권장합니다. 프로젝트별로 다른 설정이 필요한 경우에만 프로젝트별 설정을 사용하세요. 

# 새 프로젝트에 MCP 설정 적용
.\new-project-mcp-setup.ps1 -ProjectPath "C:\path\to\new\project" -CreateProjectFolder