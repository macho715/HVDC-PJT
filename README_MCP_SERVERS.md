# MACHO-GPT v3.4-mini MCP Servers Management

## 🎯 개요
HVDC 프로젝트의 모든 MCP 서버를 한번에 관리할 수 있는 스크립트 모음입니다.

## 📁 파일 구조
```
HVDC_PJT/
├── start_all_mcp_servers.ps1      # PowerShell 시작 스크립트
├── stop_all_mcp_servers.ps1       # PowerShell 중지 스크립트
├── start_all_mcp_servers.bat      # 배치 시작 파일
├── stop_all_mcp_servers.bat       # 배치 중지 파일
├── mcp_servers_manager.bat        # 통합 관리 도구
└── README_MCP_SERVERS.md          # 이 파일
```

## 🚀 사용법

### 1. 통합 관리 도구 (권장)
```bash
# 메뉴 기반 관리 도구 실행
mcp_servers_manager.bat
```

**메뉴 옵션:**
- **1**: 모든 MCP 서버 시작
- **2**: 모든 MCP 서버 중지
- **3**: 서버 가용성 테스트
- **4**: 현재 서버 상태 확인
- **5**: 강제 중지
- **6**: 종료

### 2. 개별 스크립트 사용

#### 시작 스크립트
```bash
# 기본 시작
start_all_mcp_servers.bat

# 백그라운드 시작
start_all_mcp_servers.bat -Background

# 테스트 모드 (실제 시작하지 않음)
start_all_mcp_servers.bat -TestOnly

# 상세 로그
start_all_mcp_servers.bat -Verbose
```

#### 중지 스크립트
```bash
# 기본 중지
stop_all_mcp_servers.bat

# 강제 중지
stop_all_mcp_servers.bat -Force

# 상세 로그
stop_all_mcp_servers.bat -Verbose
```

### 3. PowerShell 직접 실행
```powershell
# 시작
.\start_all_mcp_servers.ps1

# 중지
.\stop_all_mcp_servers.ps1
```

## 🔧 관리되는 MCP 서버 목록

### 기본 MCP 서버 (10개)
| 서버명 | 포트 | 패키지 | 기능 |
|--------|------|--------|------|
| filesystem | 8080 | @modelcontextprotocol/server-filesystem | 파일 시스템 작업 |
| playwright | 8081 | @executeautomation/playwright-mcp-server | 웹 브라우저 자동화 |
| win-cli | 8082 | @simonb97/server-win-cli | Windows CLI 작업 |
| desktop-commander | 8083 | @wonderwhy-er/desktop-commander | 데스크톱 자동화 |
| context7 | 8084 | @upstash/context7-mcp | 컨텍스트 관리 |
| memory | 8085 | @modelcontextprotocol/server-memory | 메모리 관리 |
| everything | 8086 | @modelcontextprotocol/server-everything | 시스템 검색 |
| puppeteer | 8087 | @hisma/server-puppeteer | 고급 웹 자동화 |
| sequential-thinking | 8090 | @modelcontextprotocol/server-sequential-thinking | 구조적 추론 |
| brave-search | 8091 | @modelcontextprotocol/server-brave-search | 실시간 웹 검색 |

### 커스텀 서버 (2개)
| 서버명 | 포트 | 타입 | 기능 |
|--------|------|------|------|
| shrimp-task-manager | 8092 | Python | HVDC 프로젝트 작업 관리 |
| figma-context-mcp | 8093 | Node.js | Figma 컨텍스트 관리 |

## 📊 모니터링 및 로깅

### 로그 파일
- **시작 로그**: `mcp_servers.log`
- **중지 로그**: `mcp_servers_stop.log`
- **상세 리포트**: `mcp_servers_report_YYYYMMDD_HHMMSS.json`

### 상태 확인
```powershell
# Node.js 프로세스 확인
Get-Process -Name "node"

# Python 프로세스 확인
Get-Process -Name "python"

# 포트 상태 확인
netstat -ano | findstr ":808"
netstat -ano | findstr ":809"
```

## ⚠️ 주의사항

### 1. 권한 요구사항
- PowerShell 실행 정책 설정 필요
- 관리자 권한 권장 (포트 바인딩)

### 2. 포트 충돌
- 8080-8093 포트가 사용됨
- 다른 서비스와 포트 충돌 가능성

### 3. 리소스 사용량
- 총 메모리: ~100MB (12개 서버)
- CPU: ~15% (평균)

## 🔧 문제 해결

### 서버 시작 실패
1. 포트 사용 중 확인
2. Node.js/npm 설치 확인
3. Python 환경 확인
4. 권한 확인

### 서버 중지 실패
1. 강제 중지 옵션 사용
2. 작업 관리자에서 수동 종료
3. 시스템 재부팅

### 로그 확인
```powershell
# 최신 로그 확인
Get-Content mcp_servers.log -Tail 20

# 오류만 확인
Get-Content mcp_servers.log | Select-String "ERROR"
```

## 📈 성능 최적화

### 메모리 최적화
- 불필요한 서버 비활성화
- 백그라운드 모드 사용
- 주기적 재시작

### CPU 최적화
- 서버 우선순위 조정
- 프로세스 제한 설정
- 모니터링 간격 조정

## 🔄 자동화

### 스케줄러 등록
```powershell
# 시작 작업 등록
SCHTASKS /CREATE /SC ONSTART /TN "MCP_Servers_Start" /TR "C:\cursor-mcp\HVDC_PJT\start_all_mcp_servers.bat"

# 종료 작업 등록
SCHTASKS /CREATE /SC ONLOGON /TN "MCP_Servers_Stop" /TR "C:\cursor-mcp\HVDC_PJT\stop_all_mcp_servers.bat"
```

### 서비스 등록
```powershell
# Windows 서비스로 등록 (고급)
New-Service -Name "MCP_Servers" -BinaryPathName "C:\cursor-mcp\HVDC_PJT\start_all_mcp_servers.bat"
```

## 📞 지원

### 문제 보고
- 로그 파일 첨부
- 시스템 정보 포함
- 재현 단계 명시

### 연락처
- 프로젝트: HVDC_Samsung_CT_ADNOC_DSV
- 버전: MACHO-GPT v3.4-mini
- 날짜: 2025-07-11

---

**🔧 추천 명령어:**
`mcp_servers_manager.bat` [통합 관리 도구 실행 - 모든 기능 접근]
`start_all_mcp_servers.bat -TestOnly` [서버 가용성 테스트 - 안전한 검증]
`stop_all_mcp_servers.bat -Force` [강제 중지 - 문제 해결] 