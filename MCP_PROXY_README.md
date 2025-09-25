# MCP SuperAssistant Proxy - HVDC Project Setup

## 🚀 Quick Start

### Option 1: Batch File (Windows)
```cmd
start_mcp_proxy.bat
```

### Option 2: PowerShell Script (Recommended)
```powershell
.\start_mcp_proxy.ps1
```

### Option 3: Manual Command
```cmd
cd C:\cursor-mcp\HVDC_PJT
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./config.json
```

## 📋 Current Configuration Status

### ✅ Working Servers
- **Filesystem Server**: ACTIVE (12 tools available)
  - Package: `@modelcontextprotocol/server-filesystem`
  - Directory: `C:\cursor-mcp\HVDC_PJT`
  - Tools: File read/write, directory listing, search, etc.

### ❌ Removed Servers (Failed to Start)
- **JSON Server**: npm 404 error - package not found
- **Context7 Server**: npm 404 error - package not found  
- **Android Server**: npm 404 error - package not found
- **Docker Servers**: Docker Desktop not running
  - brightdata/mcp
  - vlmrun/mcp
  - gadmin/mcp
- **Email Server**: pipx not installed

## 🌐 Server Details

| Setting | Value |
|---------|-------|
| **Port** | 3006 |
| **Host** | localhost |
| **CORS** | Enabled (*) |
| **SSE Path** | /sse |
| **Message Path** | /message |
| **Transport** | Server-Sent Events (SSE) |

## 🔧 Chrome Extension Setup

1. **Install MCP SuperAssistant Extension** from Chrome Web Store
2. **Configure Extension Settings**:
   - Server URL: `http://localhost:3006`
   - Transport: SSE
   - Auto-connect: Enabled
3. **Start Proxy** using one of the methods above
4. **Refresh Extension** to connect

## 📊 Connection Status Indicators

### Successful Connection
```
[mcp-superassistant-proxy] Connected to server: filesystem
[mcp-superassistant-proxy] Server filesystem has 12 tools
[mcp-superassistant-proxy] Successfully initialized server: filesystem
```

### Active Session
```
[mcp-superassistant-proxy] New SSE connection from ::1
[mcp-superassistant-proxy] POST to SSE transport (session ...)
```

## 🛠️ Available Tools (Filesystem Server)

The filesystem server provides 12 tools for file operations:

1. **File Operations**
   - Read files
   - Write files
   - Create directories
   - Delete files/directories

2. **Search Operations**
   - Search file contents
   - List directory contents
   - Find files by pattern

3. **Metadata Operations**
   - Get file stats
   - Check file existence
   - Get file permissions

## 🚨 Troubleshooting

### Port Already in Use
```cmd
netstat -ano | findstr :3006
taskkill /PID <PID> /F
```

### Extension Not Connecting
1. Check if proxy is running on port 3006
2. Verify CORS settings in config.json
3. Refresh Chrome extension
4. Check browser console for errors

### Adding New Servers
1. Verify npm package exists: `npm search @modelcontextprotocol/server-<name>`
2. Add to config.json mcpServers section
3. Restart proxy

## 📁 File Structure

```
C:\cursor-mcp\HVDC_PJT\
├── config.json              # MCP server configuration
├── start_mcp_proxy.bat      # Windows batch startup
├── start_mcp_proxy.ps1      # PowerShell startup (recommended)
├── MCP_PROXY_README.md      # This documentation
└── ...                      # HVDC project files
```

## 🔄 MACHO-GPT Integration

The MCP SuperAssistant Proxy integrates with MACHO-GPT v3.4-mini to provide:

- **File System Access**: Direct access to HVDC project files
- **Real-time Operations**: Live file monitoring and updates
- **Logistics Data Processing**: Excel, CSV, and JSON file handling
- **Automated Workflows**: Integration with HVDC logistics processes

## 📝 Configuration File (config.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\cursor-mcp\\HVDC_PJT"
      ]
    }
  },
  "integrations": {
    "samsung_ct": true,
    "adnoc_dsv": true,
    "weather_api": true,
    "port_api": true
  },
  "performance": {
    "memory_limit": "100MB",
    "cache_enabled": true,
    "compression": true,
    "batch_size": 1000
  },
  "security": {
    "allowed_domains": ["chat.openai.com", "perplexity.ai"],
    "file_access": {
      "allowed_paths": ["C:\\cursor-mcp\\HVDC_PJT"],
      "blocked_extensions": [".exe", ".bat", ".cmd"]
    },
    "api_rate_limit": 100
  }
}
```

## 🎯 Next Steps

1. **Test Connection**: Verify Chrome extension connects successfully
2. **Add More Servers**: Install Docker Desktop for additional servers
3. **Custom Servers**: Develop HVDC-specific MCP servers
4. **Monitoring**: Set up logging and health checks
5. **Automation**: Integrate with HVDC automation workflows

---

**Last Updated**: 2025-07-10  
**Version**: v1.0 (Stable - Filesystem Only)  
**Project**: HVDC Samsung C&T - MACHO-GPT v3.4-mini 