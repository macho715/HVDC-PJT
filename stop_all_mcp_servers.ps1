# MACHO-GPT v3.4-mini - All MCP Servers Stopper
# HVDC Project - Samsung C&T Logistics
# ADNOC·DSV Partnership

param(
    [switch]$Force,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# MCP Server Ports
$MCP_PORTS = @(8080, 8081, 8082, 8083, 8084, 8085, 8086, 8087, 8090, 8091, 8092, 8093)

# Logging Functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "mcp_servers_stop.log" -Value $logMessage
}

function Stop-ProcessByPort {
    param([int]$Port)
    
    try {
        # Find processes using the port
        $portPattern = ":$($Port)\s"
        $connections = netstat -ano | Select-String $portPattern
        
        if ($connections) {
            foreach ($connection in $connections) {
                $parts = $connection -split '\s+'
                $processId = $parts[-1]
                
                if ($processId -and $processId -ne "0") {
                    try {
                        $process = Get-Process -Id $processId -ErrorAction Stop
                        Write-Log "Stopping process $($process.ProcessName) (PID: $processId) on port $Port" "INFO"
                        
                        if ($Force) {
                            Stop-Process -Id $processId -Force -ErrorAction Stop
                            Write-Log "Force stopped process $($process.ProcessName) (PID: $processId)" "SUCCESS"
                        } else {
                            Stop-Process -Id $processId -ErrorAction Stop
                            Write-Log "Gracefully stopped process $($process.ProcessName) (PID: $processId)" "SUCCESS"
                        }
                    }
                    catch {
                        Write-Log "Error stopping process $processId: $($_.Exception.Message)" "ERROR"
                    }
                }
            }
        } else {
            Write-Log "No processes found on port $Port" "INFO"
        }
    }
    catch {
        Write-Log "Error checking port $Port: $($_.Exception.Message)" "ERROR"
    }
}

function Stop-NodeProcesses {
    Write-Log "Stopping all Node.js processes..." "INFO"
    
    try {
        $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
        
        if ($nodeProcesses) {
            foreach ($process in $nodeProcesses) {
                try {
                    Write-Log "Stopping Node.js process (PID: $($process.Id))" "INFO"
                    
                    if ($Force) {
                        Stop-Process -Id $process.Id -Force -ErrorAction Stop
                        Write-Log "Force stopped Node.js process (PID: $($process.Id))" "SUCCESS"
                    } else {
                        Stop-Process -Id $process.Id -ErrorAction Stop
                        Write-Log "Gracefully stopped Node.js process (PID: $($process.Id))" "SUCCESS"
                    }
                }
                catch {
                    Write-Log "Error stopping Node.js process $($process.Id): $($_.Exception.Message)" "ERROR"
                }
            }
        } else {
            Write-Log "No Node.js processes found" "INFO"
        }
    }
    catch {
        Write-Log "Error stopping Node.js processes: $($_.Exception.Message)" "ERROR"
    }
}

function Stop-PythonProcesses {
    Write-Log "Stopping Python processes related to MCP servers..." "INFO"
    
    try {
        $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
        
        if ($pythonProcesses) {
            foreach ($process in $pythonProcesses) {
                try {
                    # Check if this is our shrimp task manager
                    $commandLine = (Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
                    
                    if ($commandLine -and $commandLine.Contains("shrimp_task_manager")) {
                        Write-Log "Stopping Shrimp Task Manager (PID: $($process.Id))" "INFO"
                        
                        if ($Force) {
                            Stop-Process -Id $process.Id -Force -ErrorAction Stop
                            Write-Log "Force stopped Shrimp Task Manager (PID: $($process.Id))" "SUCCESS"
                        } else {
                            Stop-Process -Id $process.Id -ErrorAction Stop
                            Write-Log "Gracefully stopped Shrimp Task Manager (PID: $($process.Id))" "SUCCESS"
                        }
                    }
                }
                catch {
                    Write-Log "Error stopping Python process $($process.Id): $($_.Exception.Message)" "ERROR"
                }
            }
        } else {
            Write-Log "No Python processes found" "INFO"
        }
    }
    catch {
        Write-Log "Error stopping Python processes: $($_.Exception.Message)" "ERROR"
    }
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

function Wait-ForPortsToClose {
    param([int]$TimeoutSeconds = 30)
    
    Write-Log "Waiting for ports to close (timeout: $TimeoutSeconds seconds)..." "INFO"
    
    $startTime = Get-Date
    $timeout = $startTime.AddSeconds($TimeoutSeconds)
    
    while ((Get-Date) -lt $timeout) {
        $activePorts = @()
        
        foreach ($port in $MCP_PORTS) {
            if (Test-Port -Port $port) {
                $activePorts += $port
            }
        }
        
        if ($activePorts.Count -eq 0) {
            Write-Log "All MCP server ports are now closed" "SUCCESS"
            return $true
        }
        
        if ($Verbose) {
            Write-Log "Still active ports: $($activePorts -join ', ')" "INFO"
        }
        
        Start-Sleep -Seconds 2
    }
    
    Write-Log "Timeout reached. Some ports may still be active: $($activePorts -join ', ')" "WARNING"
    return $false
}

# Main Execution
function Stop-AllMCPServers {
    Write-Log "=== MACHO-GPT v3.4-mini MCP Servers Stopper ===" "INFO"
    Write-Log "Project: HVDC_Samsung_CT_ADNOC_DSV" "INFO"
    Write-Log "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
    Write-Log "Working Directory: $PWD" "INFO"
    Write-Log "Force mode: $Force" "INFO"
    
    # Initialize counters
    $totalPorts = $MCP_PORTS.Count
    $stoppedPorts = 0
    $failedPorts = 0
    
    # Stop processes by port
    foreach ($port in $MCP_PORTS) {
        try {
            Stop-ProcessByPort -Port $port
            $stoppedPorts++
        }
        catch {
            Write-Log "Failed to stop processes on port $port: $($_.Exception.Message)" "ERROR"
            $failedPorts++
        }
    }
    
    # Stop Node.js processes
    Stop-NodeProcesses
    
    # Stop Python processes
    Stop-PythonProcesses
    
    # Wait for ports to close
    $portsClosed = Wait-ForPortsToClose -TimeoutSeconds 30
    
    # Generate Summary Report
    Write-Log "=== Summary Report ===" "INFO"
    Write-Log "Total Ports: $totalPorts" "INFO"
    Write-Log "Stopped: $stoppedPorts" "SUCCESS"
    Write-Log "Failed: $failedPorts" "ERROR"
    Write-Log "Success Rate: $([math]::Round(($stoppedPorts / $totalPorts) * 100, 2))%" "INFO"
    Write-Log "All Ports Closed: $portsClosed" "INFO"
    
    # Save detailed report
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.ffffff"
        system_version = "MACHO-GPT v3.4-mini"
        project = "HVDC_Samsung_CT_ADNOC_DSV"
        total_ports = $totalPorts
        stopped_ports = $stoppedPorts
        failed_ports = $failedPorts
        success_rate = [math]::Round(($stoppedPorts / $totalPorts) * 100, 2)
        all_ports_closed = $portsClosed
        force_mode = $Force
    }
    
    $reportPath = "mcp_servers_stop_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Log "Detailed report saved to: $reportPath" "INFO"
    
    return @{
        TotalPorts = $totalPorts
        StoppedPorts = $stoppedPorts
        FailedPorts = $failedPorts
        SuccessRate = [math]::Round(($stoppedPorts / $totalPorts) * 100, 2)
        AllPortsClosed = $portsClosed
    }
}

# Main execution
try {
    $results = Stop-AllMCPServers
    
    Write-Log "=== MCP Servers Stop Complete ===" "SUCCESS"
    Write-Log "Check mcp_servers_stop.log for detailed logs" "INFO"
    Write-Log "Check $reportPath for detailed report" "INFO"
    
    if ($results.SuccessRate -eq 100) {
        Write-Log "All MCP servers stopped successfully!" "SUCCESS"
        exit 0
    } else {
        Write-Log "Some MCP servers may still be running. Use -Force flag to force stop." "WARNING"
        exit 1
    }
}
catch {
    Write-Log "Critical error: $($_.Exception.Message)" "ERROR"
    exit 1
} 