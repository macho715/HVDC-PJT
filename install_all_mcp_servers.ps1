# MCP 서버 일괄 설치 스크립트
$commands = @(
    'npx -y @gongrzhe/server-json-mcp | Tee-Object -FilePath mcp_json_install.log',
    'npx -y calculator-mcp-server | Tee-Object -FilePath mcp_calculator_install.log',
    'npx -y combine-mcp | Tee-Object -FilePath mcp_aggregator_install.log',
    'npx -y octagon-deep-research-mcp | Tee-Object -FilePath mcp_octagon_install.log',
    'npx -y allvoicelab-mcp stdio | Tee-Object -FilePath mcp_voice_install.log',
    'npx -y android-mcp-server | Tee-Object -FilePath mcp_android_install.log',
    'npx -y deepview-mcp stdio | Tee-Object -FilePath mcp_deepview_install.log',
    'npx -y @upstash/context7-mcp | Tee-Object -FilePath mcp_context7_install.log',
    # Docker 기반 서버 (설치된 경우만 실행)
    'docker run --rm brightdata/mcp > mcp_brightdata_install.log 2>&1',
    'docker run --rm vlmrun/mcp > mcp_vlmrun_install.log 2>&1',
    'docker run --rm gadmin/mcp > mcp_gadmin_install.log 2>&1',
    # pipx 기반 서버 (설치된 경우만 실행)
    'pipx run mcp-email-server ui > mcp_email_install.log 2>&1'
)

Write-Host "=== MCP 서버 일괄 설치 시작 ==="
foreach ($cmd in $commands) {
    Write-Host "실행: $cmd"
    try {
        Invoke-Expression $cmd
    } catch {
        Write-Host "실패: $cmd"
    }
}
Write-Host "=== MCP 서버 설치 완료 ===" 