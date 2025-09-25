# LOGI MASTER SYSTEM v3.4-mini

HVDC Project - Samsung C&T | ADNOCÂ·DSV Partnership

---

## ğŸ“¦ í†µí•© ë¬¼ë¥˜ ê´€ë¦¬ ì‹œìŠ¤í…œ (Shrimp Task Manager + ëŒ€ì‹œë³´ë“œ + ì˜¨í†¨ë¡œì§€ + AI)

### ğŸ—ï¸ ì‹œìŠ¤í…œ ì•„í‚¤í…ì²˜

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                LOGI MASTER SYSTEM           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 1. Task Management Layer (Shrimp Task Mgr)  â”‚
â”‚ 2. Dashboard Integration Layer (ëŒ€ì‹œë³´ë“œ)     â”‚
â”‚ 3. Ontology Knowledge Layer (ì˜¨í†¨ë¡œì§€)         â”‚
â”‚ 4. MACHO-GPT AI Layer (AI í†µí•© ì œì–´)          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ì£¼ìš” ê¸°ëŠ¥

- **ì‹¤ì‹œê°„ ì‘ì—… ê´€ë¦¬**: ì‘ì—… ìƒì„±/ì¡°íšŒ/ë¶„ì„/í†µí•©
- **ëŒ€ì‹œë³´ë“œ ì—°ë™**: KPI, ì°½ê³ , ì¬ê³ , TDD ë“± ë‹¤ì–‘í•œ ëŒ€ì‹œë³´ë“œì™€ í†µí•©
- **ì˜¨í†¨ë¡œì§€ ê¸°ë°˜ ì¶”ë¡ **: ë¬¼ë¥˜ ë„ë©”ì¸ ì˜¨í†¨ë¡œì§€ ë° ê·œì • ì¤€ìˆ˜ ì§ˆì˜
- **MACHO-GPT AI í†µí•©**: ëª¨ë“œ ì „í™˜, KPI ìƒì„±, ì ì¬/ë‚ ì”¨ ë¶„ì„ ë“± AI ëª…ë ¹ì–´ ì§€ì›
- **ì¶”ì²œ ëª…ë ¹ì–´ ì•ˆë‚´**: ëª¨ë“  ëª…ë ¹ ì‹¤í–‰ í›„ ë‹¤ìŒ ì¶”ì²œ ëª…ë ¹ì–´ ìë™ ì•ˆë‚´

---

## ì‹¤í–‰ ë°©ë²•

### 1. LOGI MASTER ì‹œìŠ¤í…œ ì‹¤í–‰

```bash
python src/logi_master_system.py
```
- ì‹œìŠ¤í…œ ì´ˆê¸°í™” ë° ì˜ˆì‹œ ëª…ë ¹ì–´ ìë™ ì‹¤í–‰

### 2. í†µí•© ëª…ë ¹ì–´ ì¸í„°í˜ì´ìŠ¤ ì‚¬ìš©

```bash
python src/logi_master_integration.py <category>_<command> [--args key=value ...]
```
- ì˜ˆì‹œ:
    - ì‘ì—… ëª©ë¡: `python src/logi_master_integration.py task_manager_list_tasks`
    - KPI ë¶„ì„: `python src/logi_master_integration.py task_manager_get_analytics`
    - KPI ëŒ€ì‹œë³´ë“œ: `python src/logi_master_integration.py macho_gpt_generate_kpi`
    - AI ëª¨ë“œ ì „í™˜: `python src/logi_master_integration.py macho_gpt_switch_mode --args mode=ORACLE`

---

## ëª…ë ¹ì–´ ì¹´í…Œê³ ë¦¬ ë° ì£¼ìš” ëª…ë ¹

| ì¹´í…Œê³ ë¦¬         | ëª…ë ¹ì–´                | ì„¤ëª…                       |
|------------------|-----------------------|----------------------------|
| task_manager     | list_tasks            | ì‘ì—… ëª©ë¡ ì¡°íšŒ             |
|                  | create_task           | ì‘ì—… ìƒì„±                  |
|                  | get_analytics         | ì‘ì—… KPI/ë¶„ì„              |
|                  | integrate_task        | MACHO-GPT í†µí•©             |
| macho_gpt        | generate_kpi          | ì‹¤ì‹œê°„ KPI ëŒ€ì‹œë³´ë“œ ìƒì„±   |
|                  | switch_mode           | AI ëª¨ë“œ ì „í™˜               |
|                  | weather_check         | ë‚ ì”¨ ì˜í–¥ ë¶„ì„             |
|                  | heat_stow_analysis    | ì ì¬ ìµœì í™” ë¶„ì„           |

---

## ëŒ€ì‹œë³´ë“œ ì—°ë™

- `index.html` : ë©”ì¸ ëŒ€ì‹œë³´ë“œ ì§„ì…ì 
- `hvdc_dashboard_main.html` : í”„ë¡œì íŠ¸ ì¢…í•© ëŒ€ì‹œë³´ë“œ
- `hvdc_warehouse_monitor.html` : ì°½ê³  ëª¨ë‹ˆí„°ë§
- `hvdc_inventory_tracking.html` : ì¬ê³  ì¶”ì 
- `macho_realtime_kpi_dashboard.py` : ì‹¤ì‹œê°„ KPI ëŒ€ì‹œë³´ë“œ (Flask)
- `tdd_progress_dashboard.html` : TDD ì§„í–‰ ìƒí™© ëŒ€ì‹œë³´ë“œ

---

## ì˜¨í†¨ë¡œì§€ ì—°ë™

- `hvdc_ontology_system/ontology/` : ë„ë©”ì¸ ì˜¨í†¨ë¡œì§€(TTL)
- ì˜¨í†¨ë¡œì§€ ì§ˆì˜/ì¶”ë¡ : ì¶”í›„ SPARQL/REST API ì—°ë™ ì˜ˆì •

---

## AI í†µí•© ë° ëª¨ë“œ

- PRIME, LATTICE, RHYTHM, ORACLE, COST-GUARD, ZERO ë“± 6ê°œ ëª¨ë“œ ì§€ì›
- KPI ì„ê³„ê°’, ê·œì • ì¤€ìˆ˜, ì ì¬/ë‚ ì”¨/ë¹„ìš© ë¶„ì„ ë“± ìë™í™”
- ëª¨ë“  ëª…ë ¹ì–´ëŠ” ì‹ ë¢°ë„(â‰¥0.90)ì™€ ì¶”ì²œ ëª…ë ¹ì–´ ë°˜í™˜

---

## ì˜ˆì‹œ ì›Œí¬í”Œë¡œìš°

1. ì‘ì—… ìƒì„± ë° í†µí•©
    ```bash
    python src/logi_master_integration.py task_manager_create_task
    python src/logi_master_integration.py task_manager_integrate_task
    ```
2. KPI ë¶„ì„ ë° ëŒ€ì‹œë³´ë“œ ìƒì„±
    ```bash
    python src/logi_master_integration.py task_manager_get_analytics
    python src/logi_master_integration.py macho_gpt_generate_kpi
    ```
3. AI ëª¨ë“œ ì „í™˜ ë° ë¶„ì„
    ```bash
    python src/logi_master_integration.py macho_gpt_switch_mode --args mode=ORACLE
    python src/logi_master_integration.py macho_gpt_weather_check
    ```

---

## í†µí•© êµ¬ì¡° ë‹¤ì´ì–´ê·¸ë¨

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   ëª…ë ¹ì–´   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   ì‹¤ì‹œê°„   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ì‚¬ìš©ì    â”‚â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶â”‚ LOGI MASTER  â”‚â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶â”‚ ëŒ€ì‹œë³´ë“œ/AI  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜           â”‚  SYSTEM      â”‚           â”‚ ì˜¨í†¨ë¡œì§€     â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ë¬¸ì˜ ë° ìœ ì§€ë³´ìˆ˜
- ì‹œìŠ¤í…œ ë‹´ë‹¹: @mr.cha (mrcha@example.com)
- ìœ ì§€ë³´ìˆ˜: HVDC Project Logistics AI Team 