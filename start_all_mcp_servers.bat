@echo off
REM MACHO-GPT v3.4-mini - All MCP Servers Launcher
REM HVDC Project - Samsung C&T Logistics
REM ADNOC·DSV Partnership

setlocal enabledelayedexpansion

echo ========================================
echo MACHO-GPT v3.4-mini MCP Servers Launcher
echo Project: HVDC_Samsung_CT_ADNOC_DSV
echo ========================================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell available'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is not available
    pause
    exit /b 1
)

REM Parse command line arguments
set "VERBOSE="
set "TESTONLY="
set "BACKGROUND="

:parse_args
if "%1"=="" goto :end_parse
if /i "%1"=="-Verbose" set "VERBOSE=-Verbose"
if /i "%1"=="-TestOnly" set "TESTONLY=-TestOnly"
if /i "%1"=="-Background" set "BACKGROUND=-Background"
shift
goto :parse_args
:end_parse

REM Change to script directory
cd /d "%~dp0"

REM Execute PowerShell script
echo Starting MCP servers...
powershell -ExecutionPolicy Bypass -File "start_all_mcp_servers.ps1" %VERBOSE% %TESTONLY% %BACKGROUND%

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start MCP servers
    echo Check the log files for details
    pause
    exit /b 1
) else (
    echo.
    echo MCP servers started successfully!
    echo Check mcp_servers.log for detailed logs
)

pause 