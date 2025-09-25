# MCP SuperAssistant Proxy Startup Script
# HVDC Project - MACHO-GPT v3.4-mini Integration

Write-Host "🚀 Starting MCP SuperAssistant Proxy..." -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configuration Status:" -ForegroundColor Yellow
Write-Host "  ✅ Filesystem Server: ACTIVE (12 tools)" -ForegroundColor Green
Write-Host "  ❌ JSON Server: REMOVED (npm 404)" -ForegroundColor Red
Write-Host "  ❌ Context7 Server: REMOVED (npm 404)" -ForegroundColor Red
Write-Host "  ❌ Android Server: REMOVED (npm 404)" -ForegroundColor Red
Write-Host "  ❌ Docker Servers: REMOVED (Docker not running)" -ForegroundColor Red
Write-Host "  ❌ Email Server: REMOVED (pipx not installed)" -ForegroundColor Red
Write-Host ""
Write-Host "🌐 Server Details:" -ForegroundColor Yellow
Write-Host "  Port: 3006" -ForegroundColor Cyan
Write-Host "  CORS: Enabled (*)" -ForegroundColor Cyan
Write-Host "  SSE Path: /sse" -ForegroundColor Cyan
Write-Host "  Message Path: /message" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Chrome Extension URL:" -ForegroundColor Yellow
Write-Host "  http://localhost:3006" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "C:\cursor-mcp\HVDC_PJT"

# Start the proxy
try {
    Write-Host "Starting proxy server..." -ForegroundColor Green
    npx @srbhptl39/mcp-superassistant-proxy@latest --config ./config.json
}
catch {
    Write-Host "❌ Error starting proxy: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 