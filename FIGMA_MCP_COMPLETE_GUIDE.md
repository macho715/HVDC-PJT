# ğŸ¨ Figma MCP Complete Guide for HVDC Warehouse Visualization

## ğŸ“‹ Overview

Figma MCP (Model Context Protocol) ì„œë²„ë¥¼ HVDC í”„ë¡œì íŠ¸ì˜ 3D ì°½ê³  ì‹œê°í™” ì‹œìŠ¤í…œê³¼ í†µí•©í•˜ì—¬ ë””ìì¸-íˆ¬-ì½”ë“œ ì›Œí¬í”Œë¡œìš°ë¥¼ êµ¬ì¶•í•©ë‹ˆë‹¤.

## ğŸš€ Quick Start

### 1. Prerequisites
- Node.js 18.0.0 ì´ìƒ
- Python 3.8 ì´ìƒ
- Figma ê³„ì • ë° Personal Access Token

### 2. Installation

```bash
# HVDC í”„ë¡œì íŠ¸ ë””ë ‰í† ë¦¬ë¡œ ì´ë™
cd HVDC_PJT

# Figma MCP ì„œë²„ ì„¤ì¹˜ í™•ì¸
npx figma-developer-mcp --version

# Python ì˜ì¡´ì„± ì„¤ì¹˜
pip install requests
```

### 3. Environment Setup

```bash
# Figma API í‚¤ ì„¤ì • (Windows PowerShell)
$env:FIGMA_API_KEY="your_figma_personal_access_token_here"

# ë˜ëŠ” í™˜ê²½ë³€ìˆ˜ íŒŒì¼ ìƒì„±
echo "FIGMA_API_KEY=your_figma_personal_access_token_here" > .env
```

## ğŸ”§ Configuration

### MCP Server Configuration

`figma_mcp_config.json` íŒŒì¼ì„ ìƒì„±í•˜ì—¬ MCP ì„œë²„ë¥¼ ì„¤ì •í•©ë‹ˆë‹¤:

```json
{
  "mcpServers": {
    "Framelink Figma MCP": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "figma-developer-mcp",
        "--figma-api-key=YOUR-FIGMA-API-KEY",
        "--stdio"
      ]
    }
  }
}
```

### IDE Integration

Cursor IDEì—ì„œ MCP ì„œë²„ë¥¼ í™œì„±í™”í•˜ë ¤ë©´:

1. Cursor ì„¤ì • íŒŒì¼ ì—´ê¸°
2. MCP ì„œë²„ ì„¤ì • ì¶”ê°€
3. IDE ì¬ì‹œì‘

## ğŸ“ Project Structure

```
HVDC_PJT/
â”œâ”€â”€ Figma-Context-MCP/              # Figma MCP ì„œë²„
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ warehouse_ui_wireframe.svg  # SVG ì™€ì´ì–´í”„ë ˆì„
â”‚   â”œâ”€â”€ components/                 # ìƒì„±ëœ React ì»´í¬ë„ŒíŠ¸
â”‚   â””â”€â”€ warehouse_3d_visualization_system.py
â”œâ”€â”€ figma_mcp_integration.py        # í†µí•© ìŠ¤í¬ë¦½íŠ¸
â”œâ”€â”€ figma_mcp_commands.py           # ëª…ë ¹ì–´ ì‹œìŠ¤í…œ
â”œâ”€â”€ figma_mcp_config.json           # MCP ì„œë²„ ì„¤ì •
â”œâ”€â”€ hvdc_figma_template.json        # HVDC í…œí”Œë¦¿
â””â”€â”€ FIGMA_MCP_COMPLETE_GUIDE.md     # ì´ ê°€ì´ë“œ
```

## ğŸ¯ Workflow

### 1. Design Phase (Figma)

#### SVG Wireframe Import
```bash
# SVG ì™€ì´ì–´í”„ë ˆì„ì„ Figmaë¡œ ê°€ì ¸ì˜¤ê¸°
python figma_mcp_commands.py import_svg src/warehouse_ui_wireframe.svg
```

#### Design System Creation
1. Figmaì—ì„œ ìƒˆ íŒŒì¼ ìƒì„±
2. ì»´í¬ë„ŒíŠ¸ ë¼ì´ë¸ŒëŸ¬ë¦¬ êµ¬ì¶•
3. ë””ìì¸ í† í° ì •ì˜
4. ë ˆì´ì•„ì›ƒ êµ¬ì„±

### 2. Development Phase (Code Generation)

#### Design Tokens Extraction
```bash
# Figma íŒŒì¼ì—ì„œ ë””ìì¸ í† í° ì¶”ì¶œ
python figma_mcp_commands.py extract_tokens YOUR_FIGMA_FILE_ID
```

#### React Components Generation
```bash
# Figma ë””ìì¸ì„ React ì»´í¬ë„ŒíŠ¸ë¡œ ë³€í™˜
python figma_mcp_commands.py generate_components YOUR_FIGMA_FILE_ID src/components
```

### 3. Integration Phase (3D Visualization)

#### Component Integration
```typescript
// ìƒì„±ëœ ì»´í¬ë„ŒíŠ¸ë¥¼ 3D ì‹œê°í™” ì‹œìŠ¤í…œì— í†µí•©
import WarehouseCrate from './components/WarehouseCrate';
import KPICard from './components/KPICard';

// 3D ì‹œê°í™” ì‹œìŠ¤í…œì—ì„œ ì‚¬ìš©
const WarehouseVisualization = () => {
  return (
    <div className="warehouse-3d-view">
      <div className="kpi-dashboard">
        <KPICard 
          title="Total Items"
          value={totalItems}
          color="success"
        />
      </div>
      <div className="3d-viewport">
        {crates.map(crate => (
          <WarehouseCrate
            key={crate.id}
            {...crate}
            onClick={() => handleCrateClick(crate.id)}
          />
        ))}
      </div>
    </div>
  );
};
```

## ğŸ¨ Design System

### Color Palette

```css
/* Primary Colors */
--primary-blue: #2196f3;    /* Plastic crates */
--primary-brown: #8d6e63;   /* Wooden crates */
--primary-gray: #9e9e9e;    /* Steel crates */
--primary-yellow: #ffc107;  /* Aisle */
--primary-red: #dc3545;     /* Excluded items */

/* UI Colors */
--background: #f8f9fa;
--surface: #ffffff;
--border: #dee2e6;
--text-primary: #495057;
--text-secondary: #6c757d;
```

### Component Library

#### WarehouseCrate Component
```typescript
interface WarehouseCrateProps {
  id: string;
  dimensions: {
    length: number;
    width: number;
    height: number;
  };
  material: 'plastic' | 'wood' | 'steel';
  weight: number;
  position: {
    x: number;
    y: number;
    z: number;
  };
  status: 'placed' | 'excluded' | 'pending';
  onClick?: () => void;
}
```

#### KPICard Component
```typescript
interface KPICardProps {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  color: 'success' | 'warning' | 'danger' | 'info';
}
```

## ğŸ”§ Commands Reference

### Setup Commands

```bash
# MCP ì„œë²„ ì„¤ì •
python figma_mcp_commands.py setup_server

# ì—°ê²° í…ŒìŠ¤íŠ¸
python figma_mcp_commands.py test_connection

# HVDC í…œí”Œë¦¿ ìƒì„±
python figma_mcp_commands.py create_template
```

### Design Commands

```bash
# SVG ê°€ì ¸ì˜¤ê¸°
python figma_mcp_commands.py import_svg <svg_path> [file_id]

# ë””ìì¸ í† í° ì¶”ì¶œ
python figma_mcp_commands.py extract_tokens <file_id>

# React ì»´í¬ë„ŒíŠ¸ ìƒì„±
python figma_mcp_commands.py generate_components <file_id> [output_dir]
```

### Help Commands

```bash
# ë„ì›€ë§ ë³´ê¸°
python figma_mcp_commands.py help
```

## ğŸ“Š Integration Examples

### 1. Complete Workflow

```bash
# 1. MCP ì„œë²„ ì„¤ì •
python figma_mcp_commands.py setup_server

# 2. SVG ì™€ì´ì–´í”„ë ˆì„ ê°€ì ¸ì˜¤ê¸°
python figma_mcp_commands.py import_svg src/warehouse_ui_wireframe.svg

# 3. Figmaì—ì„œ ë””ìì¸ ì™„ì„± í›„ í† í° ì¶”ì¶œ
python figma_mcp_commands.py extract_tokens YOUR_FIGMA_FILE_ID

# 4. React ì»´í¬ë„ŒíŠ¸ ìƒì„±
python figma_mcp_commands.py generate_components YOUR_FIGMA_FILE_ID src/components

# 5. 3D ì‹œê°í™” ì‹œìŠ¤í…œì— í†µí•©
# ìƒì„±ëœ ì»´í¬ë„ŒíŠ¸ë¥¼ warehouse_3d_visualization_system.pyì— import
```

### 2. Real-time Sync

```python
# ì‹¤ì‹œê°„ ë™ê¸°í™”ë¥¼ ìœ„í•œ ì›Œì¹˜ ëª¨ë“œ
import time
from figma_mcp_integration import FigmaMCPIntegration

figma = FigmaMCPIntegration()

def watch_figma_changes(file_id: str, interval: int = 30):
    """Figma íŒŒì¼ ë³€ê²½ì‚¬í•­ì„ ì£¼ê¸°ì ìœ¼ë¡œ í™•ì¸"""
    while True:
        try:
            # ë””ìì¸ í† í° ì¶”ì¶œ
            tokens_result = figma.extract_figma_design_tokens(file_id)
            
            if tokens_result['status'] == 'SUCCESS':
                # ë³€ê²½ì‚¬í•­ì´ ìˆìœ¼ë©´ ì»´í¬ë„ŒíŠ¸ ì¬ìƒì„±
                figma.generate_react_components(file_id, "src/components")
                print(f"âœ… Components updated at {time.strftime('%H:%M:%S')}")
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"âŒ Watch error: {e}")
            time.sleep(interval)

# ì›Œì¹˜ ëª¨ë“œ ì‹œì‘
watch_figma_changes("YOUR_FIGMA_FILE_ID", 60)  # 1ë¶„ë§ˆë‹¤ í™•ì¸
```

## ğŸ¯ HVDC Specific Features

### 1. Warehouse Layout Components

```typescript
// ì°½ê³  ë ˆì´ì•„ì›ƒ ì»´í¬ë„ŒíŠ¸
interface WarehouseLayout {
  zones: {
    A: ZoneConfig;
    B: ZoneConfig;
  };
  aisles: AisleConfig[];
  storageAreas: StorageAreaConfig[];
}

interface ZoneConfig {
  dimensions: { width: number; height: number };
  capacity: number;
  materialTypes: string[];
  pressureLimit: number;  // t/mÂ²
}
```

### 2. KPI Dashboard Integration

```typescript
// KPI ëŒ€ì‹œë³´ë“œ ì»´í¬ë„ŒíŠ¸
interface KPIDashboard {
  metrics: {
    totalItems: number;
    utilizationRate: number;
    averageWeight: number;
    pressureLoad: number;
  };
  alerts: Alert[];
  trends: TrendData[];
}
```

### 3. 3D Visualization Controls

```typescript
// 3D ì‹œê°í™” ì»¨íŠ¸ë¡¤
interface Viewport3D {
  camera: {
    position: { x: number; y: number; z: number };
    rotation: { x: number; y: number; z: number };
  };
  grid: {
    size: number;
    divisions: number;
  };
  lighting: {
    ambient: number;
    directional: number;
  };
}
```

## ğŸ”„ Development Workflow

### 1. Design Iteration

1. **Figmaì—ì„œ ë””ìì¸ ìˆ˜ì •**
2. **ë””ìì¸ í† í° ì¶”ì¶œ**
   ```bash
   python figma_mcp_commands.py extract_tokens YOUR_FIGMA_FILE_ID
   ```
3. **ì»´í¬ë„ŒíŠ¸ ì¬ìƒì„±**
   ```bash
   python figma_mcp_commands.py generate_components YOUR_FIGMA_FILE_ID
   ```
4. **3D ì‹œê°í™” ì‹œìŠ¤í…œ ì—…ë°ì´íŠ¸**

### 2. Code Review Process

1. **ìƒì„±ëœ ì»´í¬ë„ŒíŠ¸ ê²€í† **
2. **íƒ€ì… ì•ˆì „ì„± í™•ì¸**
3. **ì„±ëŠ¥ ìµœì í™”**
4. **í…ŒìŠ¤íŠ¸ ì‘ì„±**

### 3. Deployment

1. **ì»´í¬ë„ŒíŠ¸ ë¹Œë“œ**
2. **3D ì‹œê°í™” ì‹œìŠ¤í…œ í†µí•©**
3. **ì„±ëŠ¥ í…ŒìŠ¤íŠ¸**
4. **ë°°í¬**

## ğŸš¨ Troubleshooting

### Common Issues

#### 1. Figma API Key Error
```bash
# í•´ê²°ë°©ë²•
export FIGMA_API_KEY="your_actual_api_key"
# ë˜ëŠ”
$env:FIGMA_API_KEY="your_actual_api_key"
```

#### 2. MCP Server Not Found
```bash
# í•´ê²°ë°©ë²•
npm install -g figma-developer-mcp
# ë˜ëŠ”
npx figma-developer-mcp --help
```

#### 3. Component Generation Failed
```bash
# í•´ê²°ë°©ë²•
# 1. Figma íŒŒì¼ ID í™•ì¸
# 2. API í‚¤ ê¶Œí•œ í™•ì¸
# 3. íŒŒì¼ ì ‘ê·¼ ê¶Œí•œ í™•ì¸
```

### Debug Mode

```bash
# ë””ë²„ê·¸ ëª¨ë“œë¡œ ì‹¤í–‰
python figma_mcp_commands.py test_connection
python figma_mcp_commands.py extract_tokens YOUR_FIGMA_FILE_ID --debug
```

## ğŸ“ˆ Performance Optimization

### 1. Component Optimization

```typescript
// ë©”ëª¨ì´ì œì´ì…˜ì„ í†µí•œ ì„±ëŠ¥ ìµœì í™”
import React, { memo, useMemo } from 'react';

const WarehouseCrate = memo(({ id, dimensions, material, ...props }) => {
  const style = useMemo(() => ({
    width: dimensions.length * 10,
    height: dimensions.width * 10,
    backgroundColor: getMaterialColor(material),
  }), [dimensions, material]);

  return <div style={style} {...props} />;
});
```

### 2. Batch Processing

```python
# ë°°ì¹˜ ì²˜ë¦¬ë¥¼ í†µí•œ ì„±ëŠ¥ ìµœì í™”
def batch_generate_components(file_ids: List[str], output_dir: str):
    """ì—¬ëŸ¬ Figma íŒŒì¼ì—ì„œ ì»´í¬ë„ŒíŠ¸ë¥¼ ë°°ì¹˜ë¡œ ìƒì„±"""
    results = []
    
    for file_id in file_ids:
        result = figma.generate_react_components(file_id, output_dir)
        results.append(result)
    
    return results
```

## ğŸ”® Future Enhancements

### 1. Advanced Features

- **Real-time Collaboration**: ë‹¤ì¤‘ ì‚¬ìš©ì ì‹¤ì‹œê°„ í˜‘ì—…
- **Version Control**: ë””ìì¸ ë²„ì „ ê´€ë¦¬
- **Automated Testing**: ìë™í™”ëœ ì»´í¬ë„ŒíŠ¸ í…ŒìŠ¤íŠ¸
- **Performance Monitoring**: ì„±ëŠ¥ ëª¨ë‹ˆí„°ë§

### 2. Integration Extensions

- **SketchUp Integration**: SketchUp íŒŒì¼ ì§ì ‘ ê°€ì ¸ì˜¤ê¸°
- **Blender Integration**: Blender 3D ëª¨ë¸ í†µí•©
- **CAD Integration**: CAD íŒŒì¼ ì§€ì›
- **IoT Integration**: ì‹¤ì‹œê°„ ì„¼ì„œ ë°ì´í„° ì—°ë™

### 3. AI-Powered Features

- **Auto-Layout**: AI ê¸°ë°˜ ìë™ ë ˆì´ì•„ì›ƒ
- **Smart Components**: ì§€ëŠ¥í˜• ì»´í¬ë„ŒíŠ¸ ìƒì„±
- **Predictive Analytics**: ì˜ˆì¸¡ ë¶„ì„
- **Natural Language Interface**: ìì—°ì–´ ì¸í„°í˜ì´ìŠ¤

## ğŸ“š Resources

### Documentation
- [Figma API Documentation](https://www.figma.com/developers/api)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Framelink Figma MCP](https://www.framelink.ai/)

### Tools
- [Figma Personal Access Tokens](https://help.figma.com/hc/en-us/articles/8085703771159)
- [Cursor IDE](https://cursor.sh/)
- [React Documentation](https://react.dev/)

### Community
- [Figma Community](https://www.figma.com/community)
- [MCP Discord](https://discord.gg/modelcontextprotocol)
- [HVDC Project Repository](https://github.com/your-org/hvdc-project)

---

ğŸ”§ **ì¶”ì²œ ëª…ë ¹ì–´:**
/figma_mcp setup_server [Figma MCP ì„œë²„ ì„¤ì •]
/figma import_svg warehouse_ui_wireframe.svg [SVG ì™€ì´ì–´í”„ë ˆì„ ê°€ì ¸ì˜¤ê¸°]
/figma extract_tokens [FILE_ID] [ë””ìì¸ í† í° ì¶”ì¶œ]
/figma generate_components [FILE_ID] [React ì»´í¬ë„ŒíŠ¸ ìƒì„±]
/3d_visualization integrate_figma [3D ì‹œê°í™” + Figma ì—°ë™] 