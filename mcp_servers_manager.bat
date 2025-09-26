@echo off
REM MACHO-GPT v3.4-mini - MCP Servers Manager
REM HVDC Project - Samsung C&T Logistics
REM ADNOC·DSV Partnership

setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo MACHO-GPT v3.4-mini MCP Servers Manager
echo Project: HVDC_Samsung_CT_ADNOC_DSV
echo ========================================
echo.
echo Available Actions:
echo 1. Start All MCP Servers
echo 2. Stop All MCP Servers
echo 3. Test Server Availability
echo 4. View Server Status
echo 5. Force Stop All Servers
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto :start_servers
if "%choice%"=="2" goto :stop_servers
if "%choice%"=="3" goto :test_servers
if "%choice%"=="4" goto :view_status
if "%choice%"=="5" goto :force_stop
if "%choice%"=="6" goto :exit
goto :menu

:start_servers
cls
echo ========================================
echo Starting All MCP Servers...
echo ========================================
echo.
call "start_all_mcp_servers.bat"
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:stop_servers
cls
echo ========================================
echo Stopping All MCP Servers...
echo ========================================
echo.
call "stop_all_mcp_servers.bat"
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:test_servers
cls
echo ========================================
echo Testing Server Availability...
echo ========================================
echo.
powershell -ExecutionPolicy Bypass -File "start_all_mcp_servers.ps1" -TestOnly
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:view_status
cls
echo ========================================
echo Current Server Status
echo ========================================
echo.
echo Checking Node.js processes...
powershell -Command "Get-Process -Name 'node' -ErrorAction SilentlyContinue | Select-Object Id, CPU, WorkingSet, StartTime | Format-Table -AutoSize"
echo.
echo Checking Python processes...
powershell -Command "Get-Process -Name 'python' -ErrorAction SilentlyContinue | Select-Object Id, CPU, WorkingSet, StartTime | Format-Table -AutoSize"
echo.
echo Checking MCP ports...
powershell -Command "8080,8081,8082,8083,8084,8085,8086,8087,8090,8091,8092,8093 | ForEach-Object { $port = $_; $status = if (Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue) { 'ACTIVE' } else { 'INACTIVE' }; Write-Host \"Port $port`: $status\" }"
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:force_stop
cls
echo ========================================
echo Force Stopping All MCP Servers...
echo ========================================
echo.
call "stop_all_mcp_servers.bat" -Force
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:exit
cls
echo ========================================
echo Exiting MCP Servers Manager
echo Thank you for using MACHO-GPT v3.4-mini
echo ========================================
echo.
exit /b 0 