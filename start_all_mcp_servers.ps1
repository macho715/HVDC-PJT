# MACHO-GPT v3.4-mini - All MCP Servers Launcher
# HVDC Project - Samsung C&T Logistics
# ADNOC·DSV Partnership

param(
    [switch]$Verbose,
    [switch]$TestOnly,
    [switch]$Background
)

# Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# MCP Server Configuration
$MCP_SERVERS = @{
    "filesystem" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-filesystem", "C:\cursor-mcp\HVDC_PJT")
        "port" = 8080
        "description" = "File system operations MCP server"
    }
    "playwright" = @{
        "command" = "npx"
        "args" = @("-y", "@executeautomation/playwright-mcp-server")
        "port" = 8081
        "description" = "Web browser automation MCP server"
    }
    "win-cli" = @{
        "command" = "npx"
        "args" = @("-y", "@simonb97/server-win-cli")
        "port" = 8082
        "description" = "Windows CLI operations MCP server"
    }
    "desktop-commander" = @{
        "command" = "npx"
        "args" = @("-y", "@wonderwhy-er/desktop-commander")
        "port" = 8083
        "description" = "Desktop automation MCP server"
    }
    "context7" = @{
        "command" = "npx"
        "args" = @("-y", "@upstash/context7-mcp")
        "port" = 8084
        "description" = "Context management MCP server"
    }
    "memory" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-memory")
        "port" = 8085
        "description" = "Memory management MCP server"
    }
    "everything" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-everything")
        "port" = 8086
        "description" = "System-wide search MCP server"
    }
    "puppeteer" = @{
        "command" = "npx"
        "args" = @("-y", "@hisma/server-puppeteer")
        "port" = 8087
        "description" = "Advanced web automation MCP server"
    }
    "sequential-thinking" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-sequential-thinking", "--port", "8090")
        "port" = 8090
        "description" = "Structured reasoning MCP server"
    }
    "brave-search" = @{
        "command" = "npx"
        "args" = @("-y", "@modelcontextprotocol/server-brave-search", "--port", "8091")
        "port" = 8091
        "description" = "Live web search MCP server"
    }
}

# Shrimp Task Manager Configuration
$SHRIMP_TASK_MANAGER = @{
    "command" = "python"
    "args" = @("src/shrimp_task_manager.py")
    "port" = 8092
    "description" = "HVDC Project Task Manager"
}

# Figma Context MCP Configuration
$FIGMA_CONTEXT_MCP = @{
    "command" = "node"
    "args" = @("Figma-Context-MCP/dist/cli.js")
    "port" = 8093
    "description" = "Figma Context MCP server"
}

# Logging Functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "mcp_servers.log" -Value $logMessage
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Start-MCPServer {
    param(
        [string]$ServerName,
        [hashtable]$Config,
        [switch]$Background
    )
    
    Write-Log "Starting $ServerName server..." "INFO"
    
    try {
        $processArgs = @{
            FilePath = $Config.command
            ArgumentList = $Config.args
            WorkingDirectory = $PWD
            PassThru = $true
            WindowStyle = if ($Background) { "Hidden" } else { "Normal" }
        }
        
        if ($Background) {
            $processArgs.NoNewWindow = $true
        }
        
        $process = Start-Process @processArgs
        
        # Wait for server to start
        Start-Sleep -Seconds 3
        
        # Test port connectivity
        $maxAttempts = 10
        $attempt = 0
        $connected = $false
        
        while ($attempt -lt $maxAttempts -and -not $connected) {
            $connected = Test-Port -Port $Config.port
            if (-not $connected) {
                Start-Sleep -Seconds 2
                $attempt++
            }
        }
        
        if ($connected) {
            Write-Log "$ServerName server started successfully on port $($Config.port)" "SUCCESS"
            return @{
                Name = $ServerName
                ProcessId = $process.Id
                Port = $Config.port
                Status = "RUNNING"
                StartTime = Get-Date
            }
        } else {
            Write-Log "$ServerName server failed to start on port $($Config.port)" "ERROR"
            return @{
                Name = $ServerName
                ProcessId = $process.Id
                Port = $Config.port
                Status = "FAILED"
                StartTime = Get-Date
            }
        }
    }
    catch {
        Write-Log "Error starting $ServerName server: $($_.Exception.Message)" "ERROR"
        return @{
            Name = $ServerName
            ProcessId = $null
            Port = $Config.port
            Status = "ERROR"
            StartTime = Get-Date
            Error = $_.Exception.Message
        }
    }
}

function Start-ShrimpTaskManager {
    param([switch]$Background)
    
    Write-Log "Starting Shrimp Task Manager..." "INFO"
    
    try {
        $processArgs = @{
            FilePath = $SHRIMP_TASK_MANAGER.command
            ArgumentList = $SHRIMP_TASK_MANAGER.args
            WorkingDirectory = $PWD
            PassThru = $true
            WindowStyle = if ($Background) { "Hidden" } else { "Normal" }
        }
        
        if ($Background) {
            $processArgs.NoNewWindow = $true
        }
        
        $process = Start-Process @processArgs
        
        Start-Sleep -Seconds 2
        
        Write-Log "Shrimp Task Manager started successfully" "SUCCESS"
        return @{
            Name = "shrimp-task-manager"
            ProcessId = $process.Id
            Port = $SHRIMP_TASK_MANAGER.port
            Status = "RUNNING"
            StartTime = Get-Date
        }
    }
    catch {
        Write-Log "Error starting Shrimp Task Manager: $($_.Exception.Message)" "ERROR"
        return @{
            Name = "shrimp-task-manager"
            ProcessId = $null
            Port = $SHRIMP_TASK_MANAGER.port
            Status = "ERROR"
            StartTime = Get-Date
            Error = $_.Exception.Message
        }
    }
}

function Start-FigmaContextMCP {
    param([switch]$Background)
    
    Write-Log "Starting Figma Context MCP..." "INFO"
    
    try {
        $processArgs = @{
            FilePath = $FIGMA_CONTEXT_MCP.command
            ArgumentList = $FIGMA_CONTEXT_MCP.args
            WorkingDirectory = $PWD
            PassThru = $true
            WindowStyle = if ($Background) { "Hidden" } else { "Normal" }
        }
        
        if ($Background) {
            $processArgs.NoNewWindow = $true
        }
        
        $process = Start-Process @processArgs
        
        Start-Sleep -Seconds 2
        
        Write-Log "Figma Context MCP started successfully" "SUCCESS"
        return @{
            Name = "figma-context-mcp"
            ProcessId = $process.Id
            Port = $FIGMA_CONTEXT_MCP.port
            Status = "RUNNING"
            StartTime = Get-Date
        }
    }
    catch {
        Write-Log "Error starting Figma Context MCP: $($_.Exception.Message)" "ERROR"
        return @{
            Name = "figma-context-mcp"
            ProcessId = $null
            Port = $FIGMA_CONTEXT_MCP.port
            Status = "ERROR"
            StartTime = Get-Date
            Error = $_.Exception.Message
        }
    }
}

# Main Execution
function Start-AllMCPServers {
    param([switch]$Background)
    
    Write-Log "=== MACHO-GPT v3.4-mini MCP Servers Launcher ===" "INFO"
    Write-Log "Project: HVDC_Samsung_CT_ADNOC_DSV" "INFO"
    Write-Log "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
    Write-Log "Working Directory: $PWD" "INFO"
    
    # Initialize results array
    $results = @()
    
    # Start MCP Servers
    foreach ($serverName in $MCP_SERVERS.Keys) {
        $config = $MCP_SERVERS[$serverName]
        $result = Start-MCPServer -ServerName $serverName -Config $config -Background:$Background
        $results += $result
    }
    
    # Start Shrimp Task Manager
    $shrimpResult = Start-ShrimpTaskManager -Background:$Background
    $results += $shrimpResult
    
    # Start Figma Context MCP
    $figmaResult = Start-FigmaContextMCP -Background:$Background
    $results += $figmaResult
    
    # Generate Summary Report
    $totalServers = $results.Count
    $runningServers = ($results | Where-Object { $_.Status -eq "RUNNING" }).Count
    $failedServers = ($results | Where-Object { $_.Status -eq "FAILED" -or $_.Status -eq "ERROR" }).Count
    
    Write-Log "=== Summary Report ===" "INFO"
    Write-Log "Total Servers: $totalServers" "INFO"
    Write-Log "Running: $runningServers" "SUCCESS"
    Write-Log "Failed: $failedServers" "ERROR"
    Write-Log "Success Rate: $([math]::Round(($runningServers / $totalServers) * 100, 2))%" "INFO"
    
    # Save detailed report
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.ffffff"
        system_version = "MACHO-GPT v3.4-mini"
        project = "HVDC_Samsung_CT_ADNOC_DSV"
        total_servers = $totalServers
        running_servers = $runningServers
        failed_servers = $failedServers
        success_rate = [math]::Round(($runningServers / $totalServers) * 100, 2)
        servers = $results
    }
    
    $reportPath = "mcp_servers_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Log "Detailed report saved to: $reportPath" "INFO"
    
    # Display running servers
    Write-Log "=== Running Servers ===" "INFO"
    $runningResults = $results | Where-Object { $_.Status -eq "RUNNING" }
    foreach ($server in $runningResults) {
        Write-Log "$($server.Name): PID $($server.ProcessId), Port $($server.Port)" "SUCCESS"
    }
    
    # Display failed servers
    if ($failedServers -gt 0) {
        Write-Log "=== Failed Servers ===" "ERROR"
        $failedResults = $results | Where-Object { $_.Status -eq "FAILED" -or $_.Status -eq "ERROR" }
        foreach ($server in $failedResults) {
            Write-Log "$($server.Name): $($server.Status) - $($server.Error)" "ERROR"
        }
    }
    
    return $results
}

# Test Mode
if ($TestOnly) {
    Write-Log "=== Test Mode - Checking Server Availability ===" "INFO"
    
    foreach ($serverName in $MCP_SERVERS.Keys) {
        $config = $MCP_SERVERS[$serverName]
        $portAvailable = -not (Test-Port -Port $config.port)
        $status = if ($portAvailable) { "AVAILABLE" } else { "IN_USE" }
        Write-Log "$serverName (Port $($config.port)): $status" "INFO"
    }
    
    $shrimpPortAvailable = -not (Test-Port -Port $SHRIMP_TASK_MANAGER.port)
    $shrimpStatus = if ($shrimpPortAvailable) { "AVAILABLE" } else { "IN_USE" }
    Write-Log "shrimp-task-manager (Port $($SHRIMP_TASK_MANAGER.port)): $shrimpStatus" "INFO"
    
    $figmaPortAvailable = -not (Test-Port -Port $FIGMA_CONTEXT_MCP.port)
    $figmaStatus = if ($figmaPortAvailable) { "AVAILABLE" } else { "IN_USE" }
    Write-Log "figma-context-mcp (Port $($FIGMA_CONTEXT_MCP.port)): $figmaStatus" "INFO"
    
    exit 0
}

# Main execution
try {
    $results = Start-AllMCPServers -Background:$Background
    
    if ($Verbose) {
        Write-Log "Verbose mode: All server details logged" "INFO"
    }
    
    Write-Log "=== MCP Servers Launch Complete ===" "SUCCESS"
    Write-Log "Check mcp_servers.log for detailed logs" "INFO"
    Write-Log "Check $reportPath for detailed report" "INFO"
    
    # Keep script running if not in background mode
    if (-not $Background) {
        Write-Log "Press Ctrl+C to stop all servers" "INFO"
        try {
            while ($true) {
                Start-Sleep -Seconds 10
                # Check if any servers are still running
                $runningCount = ($results | Where-Object { $_.Status -eq "RUNNING" -and $_.ProcessId -ne $null } | ForEach-Object { Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue } | Measure-Object).Count
                if ($runningCount -eq 0) {
                    Write-Log "All servers have stopped" "WARNING"
                    break
                }
            }
        }
        catch {
            Write-Log "Script interrupted by user" "INFO"
        }
    }
}
catch {
    Write-Log "Critical error: $($_.Exception.Message)" "ERROR"
    exit 1
} 