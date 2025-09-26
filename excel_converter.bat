@echo off
REM MACHO-GPT v3.4-mini - Excel Converter for ChatGPT
REM HVDC Project - Samsung C&T Logistics
REM ADNOC·DSV Partnership

setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo MACHO-GPT Excel Converter for ChatGPT
echo Project: HVDC_Samsung_CT_ADNOC_DSV
echo ========================================
echo.
echo Excel 파일을 ChatGPT가 읽을 수 있는 형태로 변환
echo.
echo 1. 파일을 드래그하여 변환 (모든 형식)
echo 2. JSON 형식으로 변환
echo 3. CSV 형식으로 변환
echo 4. 텍스트 형식으로 변환
echo 5. Markdown 형식으로 변환
echo 6. 요약 정보 생성
echo 7. 지원 형식 확인
echo 8. 종료
echo.
set /p choice="선택하세요 (1-8): "

if "%choice%"=="1" goto :drag_convert
if "%choice%"=="2" goto :json_convert
if "%choice%"=="3" goto :csv_convert
if "%choice%"=="4" goto :txt_convert
if "%choice%"=="5" goto :md_convert
if "%choice%"=="6" goto :summary_convert
if "%choice%"=="7" goto :show_formats
if "%choice%"=="8" goto :exit
goto :menu

:drag_convert
cls
echo ========================================
echo 파일을 드래그하여 변환 (모든 형식)
echo ========================================
echo.
echo Excel 파일을 이 창에 드래그하세요...
echo.
set /p file_path="파일 경로: "
if "%file_path%"=="" goto :menu

echo.
echo 변환 중...
python excel_converter.py "%file_path%" -f all
echo.
echo 변환 완료! Enter 키를 누르세요...
pause >nul
goto :menu

:json_convert
cls
echo ========================================
echo JSON 형식으로 변환
echo ========================================
echo.
set /p file_path="Excel 파일 경로: "
if "%file_path%"=="" goto :menu

echo.
echo JSON 변환 중...
python excel_converter.py "%file_path%" -f json
echo.
echo 변환 완료! Enter 키를 누르세요...
pause >nul
goto :menu

:csv_convert
cls
echo ========================================
echo CSV 형식으로 변환
echo ========================================
echo.
set /p file_path="Excel 파일 경로: "
if "%file_path%"=="" goto :menu

echo.
echo CSV 변환 중...
python excel_converter.py "%file_path%" -f csv
echo.
echo 변환 완료! Enter 키를 누르세요...
pause >nul
goto :menu

:txt_convert
cls
echo ========================================
echo 텍스트 형식으로 변환
echo ========================================
echo.
set /p file_path="Excel 파일 경로: "
if "%file_path%"=="" goto :menu

echo.
echo 텍스트 변환 중...
python excel_converter.py "%file_path%" -f txt
echo.
echo 변환 완료! Enter 키를 누르세요...
pause >nul
goto :menu

:md_convert
cls
echo ========================================
echo Markdown 형식으로 변환
echo ========================================
echo.
set /p file_path="Excel 파일 경로: "
if "%file_path%"=="" goto :menu

echo.
echo Markdown 변환 중...
python excel_converter.py "%file_path%" -f md
echo.
echo 변환 완료! Enter 키를 누르세요...
pause >nul
goto :menu

:summary_convert
cls
echo ========================================
echo 요약 정보 생성
echo ========================================
echo.
set /p file_path="Excel 파일 경로: "
if "%file_path%"=="" goto :menu

echo.
echo 요약 정보 생성 중...
python excel_converter.py "%file_path%" -f summary
echo.
echo 변환 완료! Enter 키를 누르세요...
pause >nul
goto :menu

:show_formats
cls
echo ========================================
echo 지원되는 형식
echo ========================================
echo.
python excel_converter.py --list-formats
echo.
echo Enter 키를 누르세요...
pause >nul
goto :menu

:exit
cls
echo ========================================
echo Excel Converter 종료
echo Thank you for using MACHO-GPT v3.4-mini
echo ========================================
echo.
exit /b 0 