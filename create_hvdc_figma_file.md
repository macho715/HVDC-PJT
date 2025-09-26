# ğŸ¨ HVDC Figma íŒŒì¼ ìƒì„± ê°€ì´ë“œ

## âœ… API í‚¤ í™•ì¸ ì™„ë£Œ

**ì‚¬ìš©ì ì •ë³´:**
- ğŸ‘¤ **ì‚¬ìš©ì**: MINKYU CHA
- ğŸ“§ **ì´ë©”ì¼**: mscho715@gmail.com
- ğŸ¢ **íŒ€**: Personal

## ğŸš€ HVDC Figma íŒŒì¼ ìƒì„± ë‹¨ê³„

### 1. Figmaì—ì„œ ìƒˆ íŒŒì¼ ìƒì„±

1. **Figma ì›¹ì‚¬ì´íŠ¸ ì ‘ì†**: https://www.figma.com
2. **ìƒˆ íŒŒì¼ ìƒì„±**: "New design file" í´ë¦­
3. **íŒŒì¼ëª… ì„¤ì •**: `HVDC Warehouse 3D Visualization`
4. **í”„ë ˆì„ í¬ê¸°**: 1200x800px

### 2. ê¸°ë³¸ ë ˆì´ì•„ì›ƒ êµ¬ì„±

#### ğŸ“ í”„ë ˆì„ êµ¬ì¡°
```
HVDC Warehouse 3D Visualization/
â”œâ”€â”€ Header (1200x60px)
â”‚   â”œâ”€â”€ Logo
â”‚   â”œâ”€â”€ Title: "HVDC Warehouse 3D Visualization"
â”‚   â””â”€â”€ User Info
â”œâ”€â”€ Sidebar (300x740px)
â”‚   â”œâ”€â”€ File Upload Section
â”‚   â”œâ”€â”€ 3D Settings
â”‚   â”œâ”€â”€ Export Options
â”‚   â””â”€â”€ KPI Dashboard
â”œâ”€â”€ Main View (900x740px)
â”‚   â”œâ”€â”€ 3D Viewport
â”‚   â”œâ”€â”€ Grid System
â”‚   â””â”€â”€ Crate Boxes
â””â”€â”€ Footer (1200x60px)
    â”œâ”€â”€ Status Bar
    â””â”€â”€ Legend
```

### 3. ë””ìì¸ ì‹œìŠ¤í…œ ì„¤ì •

#### ğŸ¨ ìƒ‰ìƒ íŒ”ë ˆíŠ¸
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

#### ğŸ“ ê°„ê²© ì‹œìŠ¤í…œ
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
```

### 4. ì»´í¬ë„ŒíŠ¸ ë¼ì´ë¸ŒëŸ¬ë¦¬ ìƒì„±

#### ğŸ“¦ ê¸°ë³¸ ì»´í¬ë„ŒíŠ¸
1. **WarehouseCrate**
   - Plastic, Wood, Steel ë²„ì „
   - ìƒíƒœë³„ ìƒ‰ìƒ (placed, excluded, pending)

2. **KPICard**
   - ì„±ê³µ, ê²½ê³ , ìœ„í—˜, ì •ë³´ ìƒ‰ìƒ
   - íŠ¸ë Œë“œ ì•„ì´ì½˜ (up, down, stable)

3. **Button**
   - Primary, Secondary, Danger ìŠ¤íƒ€ì¼
   - Hover, Active ìƒíƒœ

4. **Input**
   - Text, Number, File upload
   - Validation ìƒíƒœ

### 5. íŒŒì¼ ID í™•ì¸

íŒŒì¼ ìƒì„± í›„ URLì—ì„œ íŒŒì¼ IDë¥¼ í™•ì¸:
```
https://www.figma.com/file/XXXXXXXXXXXXXXX/HVDC-Warehouse-3D-Visualization
                                    â†‘
                              íŒŒì¼ ID (ë³µì‚¬)
```

## ğŸ”§ ë‹¤ìŒ ë‹¨ê³„

### 1. íŒŒì¼ ìƒì„± í›„
```bash
# íŒŒì¼ IDë¥¼ ì‚¬ìš©í•˜ì—¬ ë””ìì¸ í† í° ì¶”ì¶œ
python figma_mcp_commands.py extract_tokens YOUR_FILE_ID

# React ì»´í¬ë„ŒíŠ¸ ìƒì„±
python figma_mcp_commands.py generate_components YOUR_FILE_ID src/components
```

### 2. SVG ì™€ì´ì–´í”„ë ˆì„ ê°€ì ¸ì˜¤ê¸°
```bash
# ê¸°ì¡´ SVG ì™€ì´ì–´í”„ë ˆì„ì„ Figmaë¡œ ê°€ì ¸ì˜¤ê¸°
python figma_mcp_commands.py import_svg src/warehouse_ui_wireframe.svg YOUR_FILE_ID
```

### 3. ì‹¤ì‹œê°„ ë™ê¸°í™” ì„¤ì •
```python
# ì‹¤ì‹œê°„ ë””ìì¸-ì½”ë“œ ë™ê¸°í™”
from figma_mcp_integration import FigmaMCPIntegration

figma = FigmaMCPIntegration()
figma.watch_figma_changes("YOUR_FILE_ID", 60)  # 1ë¶„ë§ˆë‹¤ í™•ì¸
```

## ğŸ“‹ ì²´í¬ë¦¬ìŠ¤íŠ¸

- [ ] Figma íŒŒì¼ ìƒì„±
- [ ] ê¸°ë³¸ ë ˆì´ì•„ì›ƒ êµ¬ì„±
- [ ] ìƒ‰ìƒ íŒ”ë ˆíŠ¸ ì„¤ì •
- [ ] ì»´í¬ë„ŒíŠ¸ ë¼ì´ë¸ŒëŸ¬ë¦¬ ìƒì„±
- [ ] íŒŒì¼ ID í™•ì¸
- [ ] ë””ìì¸ í† í° ì¶”ì¶œ í…ŒìŠ¤íŠ¸
- [ ] React ì»´í¬ë„ŒíŠ¸ ìƒì„± í…ŒìŠ¤íŠ¸

## ğŸ¯ ê¶Œì¥ ì›Œí¬í”Œë¡œìš°

1. **ë””ìì¸ ë‹¨ê³„**: Figmaì—ì„œ UI ë””ìì¸ ì™„ì„±
2. **í† í° ì¶”ì¶œ**: ë””ìì¸ í† í° ìë™ ì¶”ì¶œ
3. **ì»´í¬ë„ŒíŠ¸ ìƒì„±**: React ì»´í¬ë„ŒíŠ¸ ìë™ ìƒì„±
4. **3D í†µí•©**: 3D ì‹œê°í™” ì‹œìŠ¤í…œì— í†µí•©
5. **ì‹¤ì‹œê°„ ë™ê¸°í™”**: ë””ìì¸ ë³€ê²½ì‚¬í•­ ìë™ ë°˜ì˜

---

ğŸ”§ **ì¶”ì²œ ëª…ë ¹ì–´:**
/figma create_file [ìƒˆ Figma íŒŒì¼ ìƒì„±]
/figma import_svg warehouse_ui_wireframe.svg [SVG ê°€ì ¸ì˜¤ê¸°]
/figma extract_tokens [FILE_ID] [í† í° ì¶”ì¶œ]
/figma generate_components [FILE_ID] [ì»´í¬ë„ŒíŠ¸ ìƒì„±]
/3d_visualization integrate_figma [3D ì‹œê°í™” í†µí•©] 