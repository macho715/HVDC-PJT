@echo off
echo Starting MCP SuperAssistant Proxy...
echo.
echo Configuration: Only filesystem server (working)
echo Port: 3006
echo CORS: enabled
echo.
cd /d "C:\cursor-mcp\HVDC_PJT"
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./config.json
pause 