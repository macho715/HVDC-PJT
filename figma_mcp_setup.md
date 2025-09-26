# ğŸ¨ Figma MCP Setup for HVDC Warehouse Visualization

## ğŸ“‹ Overview

Figma MCP (Model Context Protocol) ì„œë²„ë¥¼ ì„¤ì •í•˜ì—¬ HVDC í”„ë¡œì íŠ¸ì˜ 3D ì°½ê³  ì‹œê°í™” UIë¥¼ Figmaì—ì„œ ì§ì ‘ ì‘ì—…í•  ìˆ˜ ìˆìŠµë‹ˆë‹¤.

## ğŸš€ Quick Setup

### 1. Figma API Token ìƒì„±

1. [Figma Personal Access Tokens](https://help.figma.com/hc/en-us/articles/8085703771159-Manage-personal-access-tokens) í˜ì´ì§€ ì ‘ì†
2. **Create new token** í´ë¦­
3. í† í° ì´ë¦„: `HVDC-Warehouse-MCP`
4. í† í° ë³µì‚¬ ë° ì•ˆì „í•œ ê³³ì— ì €ì¥

### 2. MCP ì„œë²„ ì„¤ì¹˜ ë° ì„¤ì •

#### Windows í™˜ê²½
```json
{
  "mcpServers": {
    "Framelink Figma MCP": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "figma-developer-mcp", "--figma-api-key=YOUR-FIGMA-API-KEY", "--stdio"]
    }
  }
}
```

#### í™˜ê²½ë³€ìˆ˜ ì„¤ì • (ì„ íƒì‚¬í•­)
```json
{
  "mcpServers": {
    "Framelink Figma MCP": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "figma-developer-mcp", "--stdio"],
      "env": {
        "FIGMA_API_KEY": "YOUR-FIGMA-API-KEY",
        "PORT": "3000"
      }
    }
  }
}
```

### 3. ë¡œì»¬ ê°œë°œ í™˜ê²½ ì„¤ì •

```bash
# HVDC í”„ë¡œì íŠ¸ ë””ë ‰í† ë¦¬ë¡œ ì´ë™
cd HVDC_PJT/Figma-Context-MCP

# ì˜ì¡´ì„± ì„¤ì¹˜
npm install

# ê°œë°œ ëª¨ë“œ ì‹¤í–‰
npm run dev

# ë˜ëŠ” í”„ë¡œë•ì…˜ ë¹Œë“œ
npm run build
npm start
```

## ğŸ¯ HVDC Warehouse UI Workflow

### 1. Figma íŒŒì¼ ìƒì„±
- ìƒˆ Figma íŒŒì¼ ìƒì„±: `HVDC Warehouse 3D Visualization`
- í”„ë ˆì„ í¬ê¸°: 1200x800px (SVG ì™€ì´ì–´í”„ë ˆì„ê³¼ ë™ì¼)

### 2. ì»´í¬ë„ŒíŠ¸ êµ¬ì¡° ì„¤ê³„

#### ğŸ“ Components
```
HVDC Warehouse UI/
â”œâ”€â”€ Layout/
â”‚   â”œâ”€â”€ Header
â”‚   â”œâ”€â”€ Sidebar
â”‚   â”œâ”€â”€ Main View
â”‚   â””â”€â”€ Footer
â”œâ”€â”€ Controls/
â”‚   â”œâ”€â”€ File Upload
â”‚   â”œâ”€â”€ 3D Settings
â”‚   â”œâ”€â”€ Export Options
â”‚   â””â”€â”€ KPI Dashboard
â”œâ”€â”€ 3D View/
â”‚   â”œâ”€â”€ Viewport
â”‚   â”œâ”€â”€ Grid System
â”‚   â”œâ”€â”€ Crate Boxes
â”‚   â””â”€â”€ Aisle
â””â”€â”€ Data/
    â”œâ”€â”€ Item Table
    â”œâ”€â”€ Legend
    â””â”€â”€ Status Indicators
```

### 3. Material Design System

#### ğŸ¨ Color Palette
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

#### ğŸ“ Spacing System
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
```

## ğŸ”§ Integration Commands

### Figma MCP ëª…ë ¹ì–´
```bash
# Figma íŒŒì¼ ë§í¬ë¡œ ì»¨í…ìŠ¤íŠ¸ ê°€ì ¸ì˜¤ê¸°
/figma import [FIGMA_FILE_URL]

# íŠ¹ì • í”„ë ˆì„/ì»´í¬ë„ŒíŠ¸ ê°€ì ¸ì˜¤ê¸°
/figma frame [FRAME_ID]

# ë””ìì¸ í† í° ì¶”ì¶œ
/figma tokens [FILE_ID]

# ì»´í¬ë„ŒíŠ¸ ì •ë³´ ê°€ì ¸ì˜¤ê¸°
/figma component [COMPONENT_ID]
```

### HVDC íŠ¹í™” ëª…ë ¹ì–´
```bash
# ì°½ê³  ë ˆì´ì•„ì›ƒ ìƒì„±
/warehouse_layout create_3d_view

# KPI ëŒ€ì‹œë³´ë“œ ì—…ë°ì´íŠ¸
/kpi_dashboard update_metrics

# 3D ëª¨ë¸ ë‚´ë³´ë‚´ê¸°
/3d_export generate_stl_gltf

# Figma â†’ HTML ë³€í™˜
/figma_to_html convert_design
```

## ğŸ“Š Workflow Integration

### 1. SVG â†’ Figma Import
```bash
# SVG ì™€ì´ì–´í”„ë ˆì„ì„ Figmaë¡œ ê°€ì ¸ì˜¤ê¸°
/figma import_svg warehouse_ui_wireframe.svg
```

### 2. Figma â†’ Code Generation
```bash
# Figma ë””ìì¸ì„ React/Vue ì»´í¬ë„ŒíŠ¸ë¡œ ë³€í™˜
/figma_to_code generate_react_components
```

### 3. Real-time Sync
```bash
# Figma ë³€ê²½ì‚¬í•­ì„ ì‹¤ì‹œê°„ìœ¼ë¡œ ì½”ë“œì— ë°˜ì˜
/figma_sync enable_realtime
```

## ğŸ¨ Design System Components

### 1. Warehouse Crate Component
```typescript
interface WarehouseCrate {
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
}
```

### 2. KPI Card Component
```typescript
interface KPICard {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  color: 'success' | 'warning' | 'danger' | 'info';
}
```

### 3. 3D Viewport Component
```typescript
interface Viewport3D {
  camera: {
    position: { x: number; y: number; z: number };
    rotation: { x: number; y: number; z: number };
  };
  grid: {
    size: number;
    divisions: number;
  };
  crates: WarehouseCrate[];
}
```

## ğŸ”„ Development Workflow

### 1. Design Phase
1. Figmaì—ì„œ UI ì™€ì´ì–´í”„ë ˆì„ ìƒì„±
2. ì»´í¬ë„ŒíŠ¸ ë¼ì´ë¸ŒëŸ¬ë¦¬ êµ¬ì¶•
3. ë””ìì¸ í† í° ì •ì˜

### 2. Development Phase
1. Figma MCPë¡œ ë””ìì¸ ë°ì´í„° ê°€ì ¸ì˜¤ê¸°
2. ì½”ë“œ ìë™ ìƒì„±
3. ì»´í¬ë„ŒíŠ¸ êµ¬í˜„

### 3. Integration Phase
1. 3D ì‹œê°í™” ì—”ì§„ê³¼ ì—°ë™
2. ì‹¤ì‹œê°„ ë°ì´í„° ì—…ë°ì´íŠ¸
3. ì„±ëŠ¥ ìµœì í™”

## ğŸ“ File Structure

```
HVDC_PJT/
â”œâ”€â”€ Figma-Context-MCP/          # Figma MCP ì„œë²„
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ warehouse_ui_wireframe.svg  # SVG ì™€ì´ì–´í”„ë ˆì„
â”‚   â”œâ”€â”€ warehouse_3d_visualization_system.py
â”‚   â””â”€â”€ warehouse_stl_generator.py
â”œâ”€â”€ figma_mcp_setup.md          # ì´ íŒŒì¼
â””â”€â”€ figma_design_system.json    # ë””ìì¸ ì‹œìŠ¤í…œ ì •ì˜
```

## ğŸš€ Next Steps

1. **Figma API Token ì„¤ì •**
2. **MCP ì„œë²„ êµ¬ì„±**
3. **ë””ìì¸ ì‹œìŠ¤í…œ êµ¬ì¶•**
4. **ì»´í¬ë„ŒíŠ¸ ë¼ì´ë¸ŒëŸ¬ë¦¬ ìƒì„±**
5. **ì‹¤ì‹œê°„ ë™ê¸°í™” ì„¤ì •**

---

ğŸ”§ **ì¶”ì²œ ëª…ë ¹ì–´:**
/figma_mcp setup_server [Figma MCP ì„œë²„ ì„¤ì •]
/warehouse_ui create_design_system [ë””ìì¸ ì‹œìŠ¤í…œ ìƒì„±]
/figma_to_code generate_components [Figma â†’ ì½”ë“œ ë³€í™˜]
/3d_visualization integrate_figma [3D ì‹œê°í™” + Figma ì—°ë™] 