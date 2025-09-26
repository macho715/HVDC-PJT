@echo off
REM MACHO-GPT v3.4-mini - All MCP Servers Stopper
REM HVDC Project - Samsung C&T Logistics
REM ADNOC·DSV Partnership

setlocal enabledelayedexpansion

echo ========================================
echo MACHO-GPT v3.4-mini MCP Servers Stopper
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
set "FORCE="
set "VERBOSE="

:parse_args
if "%1"=="" goto :end_parse
if /i "%1"=="-Force" set "FORCE=-Force"
if /i "%1"=="-Verbose" set "VERBOSE=-Verbose"
shift
goto :parse_args
:end_parse

REM Change to script directory
cd /d "%~dp0"

REM Execute PowerShell script
echo Stopping MCP servers...
powershell -ExecutionPolicy Bypass -File "stop_all_mcp_servers.ps1" %FORCE% %VERBOSE%

if errorlevel 1 (
    echo.
    echo WARNING: Some MCP servers may still be running
    echo Use -Force flag to force stop all servers
    echo Check the log files for details
    pause
    exit /b 1
) else (
    echo.
    echo All MCP servers stopped successfully!
    echo Check mcp_servers_stop.log for detailed logs
)

pause 