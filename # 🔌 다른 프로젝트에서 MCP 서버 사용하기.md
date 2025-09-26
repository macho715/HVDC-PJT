# ğŸ”Œ ë‹¤ë¥¸ í”„ë¡œì íŠ¸ì—ì„œ MCP ì„œë²„ ì‚¬ìš©í•˜ê¸°

## ğŸ“‹ ê°œìš”

í˜„ì¬ ì„¤ì •ëœ MCP ì„œë²„ë“¤ì„ ë‹¤ë¥¸ Cursor IDE í”„ë¡œì íŠ¸ì—ì„œë„ ì‚¬ìš©í•  ìˆ˜ ìˆìŠµë‹ˆë‹¤. MCP ì„œë²„ëŠ” ì „ì—­ì ìœ¼ë¡œ ì„¤ì¹˜ë˜ì–´ ëª¨ë“  í”„ë¡œì íŠ¸ì—ì„œ ê³µìœ í•  ìˆ˜ ìˆìŠµë‹ˆë‹¤.

## ğŸ¯ í˜„ì¬ ì„¤ì •ëœ MCP ì„œë²„ë“¤

í˜„ì¬ í”„ë¡œì íŠ¸ì—ëŠ” ë‹¤ìŒ MCP ì„œë²„ë“¤ì´ ì„¤ì •ë˜ì–´ ìˆìŠµë‹ˆë‹¤:

| ì„œë²„ëª… | ê¸°ëŠ¥ | ì„¤ëª… |
|-------|------|------|
| **filesystem** | íŒŒì¼ ì‹œìŠ¤í…œ ì‘ì—… | íŒŒì¼ ì½ê¸°/ì“°ê¸°/ìƒì„± |
| **playwright** | ì›¹ ë¸Œë¼ìš°ì € ìë™í™” | ì›¹ ìŠ¤í¬ë˜í•‘, í…ŒìŠ¤íŒ… |
| **win-cli** | Windows CLI ì‘ì—… | PowerShell ëª…ë ¹ ì‹¤í–‰ |
| **desktop-commander** | ë°ìŠ¤í¬í†± ìë™í™” | í‚¤ë³´ë“œ/ë§ˆìš°ìŠ¤ ì œì–´ |
| **context7** | ì»¨í…ìŠ¤íŠ¸ ê´€ë¦¬ | ë¬¸ì„œ ê²€ìƒ‰ ë° ì¿¼ë¦¬ |
| **seq-think** | êµ¬ì¡°í™”ëœ ì‚¬ê³  | ì²´ê³„ì  ë¬¸ì œ í•´ê²° |
| **brave-search** | ì›¹ ê²€ìƒ‰ | ì‹¤ì‹œê°„ ê²€ìƒ‰ ê¸°ëŠ¥ |

## ğŸš€ ë°©ë²• 1: Cursor IDE ê¸€ë¡œë²Œ ì„¤ì • (ê¶Œì¥)

### 1ë‹¨ê³„: Cursor ì„¤ì • íŒŒì¼ ìœ„ì¹˜ ì°¾ê¸°

```powershell
# Windowsì—ì„œ Cursor ì„¤ì • íŒŒì¼ ê²½ë¡œ
%APPDATA%\Cursor\User\settings.json
```

### 2ë‹¨ê³„: í˜„ì¬ ì„¤ì • ë³µì‚¬

í˜„ì¬ í”„ë¡œì íŠ¸ì˜ `cursor-settings-phase3-complete.json` ë‚´ìš©ì„ ê¸€ë¡œë²Œ ì„¤ì •ì— ì¶”ê°€:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/c"],
      "description": "File system operations MCP server"
    },
    "playwright": {
      "command": "npx", 
      "args": ["-y", "@executeautomation/playwright-mcp-server"],
      "description": "Web browser automation MCP server"
    },
    "win-cli": {
      "command": "npx",
      "args": ["-y", "@simonb97/server-win-cli"],
      "description": "Windows CLI operations MCP server"
    },
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander"],
      "description": "Desktop automation MCP server"
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "description": "Context management MCP server"
    },
    "seq-think": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking", "--port", "8090"],
      "description": "Structured reasoning MCP server"
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search", "--port", "8091", "--api-key", "${BRAVE_API_KEY}"],
      "description": "Live web search MCP server"
    }
  }
}
```

### 3ë‹¨ê³„: í™˜ê²½ ë³€ìˆ˜ ì„¤ì •

```powershell
# Brave Search API í‚¤ ì„¤ì • (ì‹œìŠ¤í…œ í™˜ê²½ ë³€ìˆ˜)
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "your-api-key-here", "User")
```

## ğŸ”§ ë°©ë²• 2: í”„ë¡œì íŠ¸ë³„ ì„¤ì •

### 1ë‹¨ê³„: ìƒˆ í”„ë¡œì íŠ¸ì— ì„¤ì • íŒŒì¼ ë³µì‚¬

```powershell
# ìƒˆ í”„ë¡œì íŠ¸ í´ë”ë¡œ ì´ë™
cd "C:\path\to\your\new\project"

# ì„¤ì • íŒŒì¼ ë³µì‚¬
copy "C:\cursor-mcp\cursor-settings-phase3-complete.json" ".\.cursor\settings.json"
```

### 2ë‹¨ê³„: í”„ë¡œì íŠ¸ë³„ í™˜ê²½ ë³€ìˆ˜ ì„¤ì •

ìƒˆ í”„ë¡œì íŠ¸ì—ì„œ `.env` íŒŒì¼ ìƒì„±:

```env
BRAVE_API_KEY=your-api-key-here
```

## ğŸ› ï¸ ë°©ë²• 3: ìë™ ì„¤ì • ìŠ¤í¬ë¦½íŠ¸ ì‚¬ìš©

í˜„ì¬ í”„ë¡œì íŠ¸ì˜ ìŠ¤í¬ë¦½íŠ¸ë¥¼ ì‚¬ìš©í•´ì„œ ë‹¤ë¥¸ í”„ë¡œì íŠ¸ì— ì ìš©:

```powershell
# í˜„ì¬ cursor-mcp í´ë”ì—ì„œ ì‹¤í–‰
.\apply-phase3-settings-fixed.ps1

# ë˜ëŠ” ë³´ì•ˆ ì„¤ì • í¬í•¨
.\apply-secure-settings-fixed.ps1
```

## ğŸ“‹ ë‹¨ê³„ë³„ ì„¤ì • ê°€ì´ë“œ

### 1ë‹¨ê³„: í™˜ê²½ ì¤€ë¹„

```powershell
# Node.js ë° npm í™•ì¸
node --version
npm --version

# Cursor IDE ë²„ì „ í™•ì¸ (ìµœì‹  ë²„ì „ ê¶Œì¥)
```

### 2ë‹¨ê³„: API í‚¤ ì„¤ì •

```powershell
# Brave Search API í‚¤ ì„¤ì •
$env:BRAVE_API_KEY = "your-api-key-here"
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "your-api-key-here", "User")
```

### 3ë‹¨ê³„: Cursor ì„¤ì • ì ìš©

**ë°©ë²• A: ìˆ˜ë™ ì„¤ì •**
1. Cursor IDEì—ì„œ `Ctrl+Shift+P`
2. "Preferences: Open Settings (JSON)" ê²€ìƒ‰
3. MCP ì„œë²„ ì„¤ì • ì¶”ê°€

**ë°©ë²• B: ì„¤ì • íŒŒì¼ ì§ì ‘ í¸ì§‘**
```powershell
# Cursor ì‚¬ìš©ì ì„¤ì • íŒŒì¼ ì—´ê¸°
notepad "%APPDATA%\Cursor\User\settings.json"
```

### 4ë‹¨ê³„: ì„¤ì • í™•ì¸

```powershell
# Cursor IDE ì¬ì‹œì‘ í›„ í™•ì¸
# AI ì±„íŒ…ì—ì„œ ë‹¤ìŒ ëª…ë ¹ì–´ë¡œ í…ŒìŠ¤íŠ¸:
```

```
@filesystem ls
```
```
@playwright Navigate to https://google.com
```
```
@seq-think Analyze this problem step by step
```

## ğŸ” í…ŒìŠ¤íŠ¸ ë°©ë²•

### ê¸°ë³¸ ê¸°ëŠ¥ í…ŒìŠ¤íŠ¸

```
# íŒŒì¼ ì‹œìŠ¤í…œ í…ŒìŠ¤íŠ¸
@filesystem Create a test file with hello world content

# ì›¹ ê²€ìƒ‰ í…ŒìŠ¤íŠ¸  
@brave-search Search for latest JavaScript frameworks

# êµ¬ì¡°í™”ëœ ì‚¬ê³  í…ŒìŠ¤íŠ¸
@seq-think How to build a REST API step by step
```

### í†µí•© ì›Œí¬í”Œë¡œ í…ŒìŠ¤íŠ¸

```
Use @seq-think to plan building a web scraper, then @playwright to implement it, and @filesystem to save results
```

## âš¡ ë¹ ë¥¸ ì„¤ì • ëª…ë ¹ì–´

ìƒˆ í”„ë¡œì íŠ¸ì—ì„œ í•œ ë²ˆì— ì„¤ì •í•˜ê¸°:

```powershell
# 1. í™˜ê²½ ë³€ìˆ˜ ì„¤ì •
$env:BRAVE_API_KEY = "your-api-key-here"

# 2. Cursor ì„¤ì • í´ë” ìƒì„±
mkdir .cursor -ErrorAction SilentlyContinue

# 3. ì„¤ì • íŒŒì¼ ë³µì‚¬ (í˜„ì¬ cursor-mcp í”„ë¡œì íŠ¸ì—ì„œ)
copy "cursor-settings-phase3-complete.json" ".cursor\settings.json"

# 4. Cursor IDE ì¬ì‹œì‘
```

## ğŸš¨ ì£¼ì˜ì‚¬í•­

### ë³´ì•ˆ ê³ ë ¤ì‚¬í•­
- API í‚¤ë¥¼ ì½”ë“œì— í•˜ë“œì½”ë”©í•˜ì§€ ë§ˆì„¸ìš”
- í™˜ê²½ ë³€ìˆ˜ë‚˜ ë³´ì•ˆ ì €ì¥ì†Œ ì‚¬ìš© ê¶Œì¥
- ê³µê°œ ì €ì¥ì†Œì— ì„¤ì • íŒŒì¼ ì—…ë¡œë“œ ì£¼ì˜

### ì„±ëŠ¥ ìµœì í™”
- ì‚¬ìš©í•˜ì§€ ì•ŠëŠ” MCP ì„œë²„ëŠ” ë¹„í™œì„±í™”
- í¬íŠ¸ ì¶©ëŒ ë°©ì§€ë¥¼ ìœ„í•´ ê° ì„œë²„ë§ˆë‹¤ ë‹¤ë¥¸ í¬íŠ¸ ì‚¬ìš©
- ë©”ëª¨ë¦¬ ì‚¬ìš©ëŸ‰ ëª¨ë‹ˆí„°ë§

### í˜¸í™˜ì„±
- Cursor IDE ìµœì‹  ë²„ì „ ì‚¬ìš© ê¶Œì¥
- Node.js 18+ ë²„ì „ í•„ìš”
- Windows PowerShell ë˜ëŠ” WSL í™˜ê²½

## ğŸ”§ ë¬¸ì œ í•´ê²°

### ìì£¼ ë°œìƒí•˜ëŠ” ë¬¸ì œ

**1. MCP ì„œë²„ê°€ ì¸ì‹ë˜ì§€ ì•ŠëŠ” ê²½ìš°**
```powershell
# Cursor IDE ì™„ì „ ì¬ì‹œì‘
taskkill /f /im "Cursor.exe"
# ë‹¤ì‹œ Cursor ì‹¤í–‰
```

**2. API í‚¤ ê´€ë ¨ ì˜¤ë¥˜**
```powershell
# í™˜ê²½ ë³€ìˆ˜ í™•ì¸
echo $env:BRAVE_API_KEY
# ì¬ì„¤ì •
[Environment]::SetEnvironmentVariable("BRAVE_API_KEY", "new-key", "User")
```

**3. í¬íŠ¸ ì¶©ëŒ**
```powershell
# ì‚¬ìš© ì¤‘ì¸ í¬íŠ¸ í™•ì¸
netstat -ano | findstr :8090
netstat -ano | findstr :8091
# ì¶©ëŒí•˜ëŠ” í”„ë¡œì„¸ìŠ¤ ì¢…ë£Œ
```

## ğŸ“Š ì„±ëŠ¥ ëª¨ë‹ˆí„°ë§

### ë¦¬ì†ŒìŠ¤ ì‚¬ìš©ëŸ‰ í™•ì¸

```powershell
# Node.js í”„ë¡œì„¸ìŠ¤ í™•ì¸
Get-Process -Name "node" | Format-Table ProcessName, Id, CPU, WorkingSet

# MCP ì„œë²„ ìƒíƒœ í™•ì¸
netstat -ano | findstr :809
```

### ë¡œê·¸ í™•ì¸

```powershell
# Cursor ë¡œê·¸ í´ë”
%APPDATA%\Cursor\logs

# ìµœê·¼ ë¡œê·¸ í™•ì¸
Get-Content "%APPDATA%\Cursor\logs\main.log" -Tail 50
```

## ğŸ‰ ì„±ê³µ í™•ì¸

ëª¨ë“  ì„¤ì •ì´ ì™„ë£Œë˜ë©´ Cursor IDEì—ì„œ ë‹¤ìŒ ê¸°ëŠ¥ë“¤ì„ ì‚¬ìš©í•  ìˆ˜ ìˆìŠµë‹ˆë‹¤:

- âœ… `@filesystem` - íŒŒì¼ ì‘ì—…
- âœ… `@playwright` - ì›¹ ìë™í™”  
- âœ… `@win-cli` - Windows ëª…ë ¹
- âœ… `@desktop-commander` - ë°ìŠ¤í¬í†± ì œì–´
- âœ… `@context7` - ë¬¸ì„œ ê²€ìƒ‰
- âœ… `@seq-think` - êµ¬ì¡°í™”ëœ ì‚¬ê³ 
- âœ… `@brave-search` - ì›¹ ê²€ìƒ‰

## ğŸ“š ì¶”ê°€ ìë£Œ

- [Cursor MCP ê³µì‹ ë¬¸ì„œ](https://docs.cursor.com/context/model-context-protocol)
- [MCP ì„œë²„ ëª©ë¡](https://github.com/modelcontextprotocol/servers)
- [Brave Search API ë¬¸ì„œ](https://brave.com/search/api/)

---

**ğŸ’¡ íŒ**: ì—¬ëŸ¬ í”„ë¡œì íŠ¸ì—ì„œ ë™ì¼í•œ MCP ì„œë²„ë¥¼ ì‚¬ìš©í•˜ë ¤ë©´ ê¸€ë¡œë²Œ ì„¤ì •ì„ ê¶Œì¥í•©ë‹ˆë‹¤. í”„ë¡œì íŠ¸ë³„ë¡œ ë‹¤ë¥¸ ì„¤ì •ì´ í•„ìš”í•œ ê²½ìš°ì—ë§Œ í”„ë¡œì íŠ¸ë³„ ì„¤ì •ì„ ì‚¬ìš©í•˜ì„¸ìš”. 

# ìƒˆ í”„ë¡œì íŠ¸ì— MCP ì„¤ì • ì ìš©
.\new-project-mcp-setup.ps1 -ProjectPath "C:\path\to\new\project" -CreateProjectFolder