@echo off
REM HVDC MACHO-GPT Git 자동 커밋/푸시 스크립트

REM 1. 변경사항 스테이징
git add .

REM 2. 커밋 (메시지 자동 생성: 날짜/시간)
set dt=%date:~0,10% %time:~0,8%
git commit -m "Auto-commit: %dt%"

REM 3. 원격 저장소와 병합(충돌 방지)
git pull origin main --allow-unrelated-histories

REM 4. 푸시
git push origin main

pause