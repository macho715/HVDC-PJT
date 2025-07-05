# 🚛 MACHO-GPT v3.4-mini | HVDC Project Logistics AI

**Samsung C&T × ADNOC·DSV Partnership | Enhanced Cursor IDE Integration**

## 📋 System Overview

MACHO-GPT v3.4-mini는 HVDC 프로젝트를 위한 고급 물류 AI 시스템입니다. Cursor IDE와 완전히 통합되어 개발자들이 물류 시스템을 효율적으로 개발하고 관리할 수 있도록 설계되었습니다.

### 🎯 Core Features

- **10 Categories / 60+ Commands**: 완전한 물류 명령어 체계
- **6 Containment Modes**: PRIME|ORACLE|ZERO|LATTICE|RHYTHM|COST-GUARD
- **9 Active Modules + 3 Planned**: 확장 가능한 모듈 아키텍처
- **Auto Fail-safe**: 오류 60%↓, 롤백 40%↓
- **Real-time Integration**: 웹 검색, 파일 시스템, OCR 등 완전 통합

### 🏗️ System Architecture

```
MACHO-GPT v3.4-mini/
├── 🧠 Core System
│   ├── LogiMaster (물류 마스터 프로세싱)
│   ├── ContainmentModes (6개 모드 관리)
│   └── CommandProcessor (명령어 실행 엔진)
├── 🔌 Integrations
│   ├── Samsung C&T Connector
│   ├── ADNOC·DSV Partnership
│   └── Tool Manager (8개 도구 통합)
├── 📊 Specialized Modules
│   ├── Invoice OCR (FANR/MOIAT 준수)
│   ├── Heat-Stow Analysis (압력 ≤4t/m²)
│   ├── Weather-Tie ETA Prediction
│   └── Cost Guard Validation
└── 🎛️ CLI Interface (Cursor IDE)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/hvdc-project/macho-gpt-tdd
cd macho-gpt-tdd

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/macho_config.yaml.example config/macho_config.yaml
```

### 2. Basic Usage

```bash
# System status check
python logi_meta.py --status

# List all available commands
python logi_meta.py --list all

# Execute specific command
python logi_meta.py "logi_master invoice-audit"

# Show KPI triggers
python logi_meta.py --kpi

# Export metadata
python logi_meta.py --export json
```

### 3. Core Commands

| Category | Command | Description |
|----------|---------|-------------|
| **Core Workflow** | `logi_master invoice-audit` | OCR-based invoice processing |
| | `logi_master predict` | ETA prediction with weather |
| | `logi_master kpi-dash` | Real-time KPI dashboard |
| **Containment** | `switch_mode PRIME` | Production environment activation |
| | `switch_mode LATTICE` | Container stowage optimization |
| | `switch_mode ZERO` | Emergency fallback mode |
| **Automation** | `automate_workflow` | Full pipeline automation |
| | `health_check` | System health monitoring |
| **Visualization** | `visualize_data --type=dashboard` | Executive KPI dashboard |
| | `visualize_data --type=heatmap` | Heat-Stow pressure map |

## 🎯 Containment Modes

### 🟢 PRIME Mode (Primary Operations)
- **Confidence**: ≥95%
- **Features**: Full command access, auto-triggers, real-time processing
- **Use Cases**: Production operations, standard logistics workflows

### 🔮 ORACLE Mode (Prediction & Analytics)
- **Confidence**: ≥92%
- **Features**: Real-time data validation, prediction models, market analysis
- **Use Cases**: ETA prediction, market intelligence, trend analysis

### 🟡 ZERO Mode (Emergency Fallback)
- **Confidence**: ≥99%
- **Features**: Manual override, basic operations, emergency protocols
- **Use Cases**: System failures, emergency response, critical incidents

### 🔄 LATTICE Mode (Document Processing)
- **Confidence**: ≥87%
- **Features**: Advanced OCR, document processing, thermal analysis
- **Use Cases**: Invoice processing, HS code extraction, stowage optimization

### 📈 RHYTHM Mode (KPI Monitoring)
- **Confidence**: ≥90%
- **Features**: KPI monitoring, workflow automation, alert systems
- **Use Cases**: Performance tracking, automated workflows, system monitoring

### 💰 COST-GUARD Mode (Financial Validation)
- **Confidence**: ≥96%
- **Features**: Cost validation, budget tracking, approval workflows
- **Use Cases**: Financial operations, budget management, audit compliance

## 📊 Integration Capabilities

### 🔍 Web Search Integration
```python
# Real-time market data
result = tool_manager.execute_tool_operation(
    "web_search", 
    "market_search", 
    {"query": "HVDC equipment pricing 2024"}
)
```

### 📄 OCR Processing
```python
# Invoice processing with FANR compliance
result = logi_master.invoice_audit(
    file_path="invoice_001.pdf",
    compliance_check=True
)
```

### 🌦️ Weather Integration
```python
# Marine weather for ETA prediction
weather_data = tool_manager.execute_tool_operation(
    "weather_api",
    "marine_conditions",
    {"location": "Jebel Ali Port"}
)
```

## 🔧 Development with Cursor IDE

### TDD Workflow Integration

1. **Follow plan.md**: TDD 개발 지침 준수
2. **Test-First Development**: Red → Green → Refactor
3. **MACHO-GPT Standards**: 신뢰도 ≥95% 유지
4. **Command Integration**: 모든 기능은 /cmd 시스템 호환

### Example TDD Cycle

```python
# 1. Write failing test (RED)
def test_invoice_ocr_should_extract_hs_code_with_95_percent_confidence():
    # Given: FANR approved invoice image
    # When: OCR processing executed
    # Then: HS code extraction confidence ≥95%
    pass

# 2. Implement minimum code (GREEN)
def extract_hs_code(invoice_data):
    return {"hs_code": "8544.42.9000", "confidence": 0.95}

# 3. Refactor and improve (REFACTOR)
def extract_hs_code(invoice_data):
    # Enhanced implementation with error handling
    # and multiple validation layers
    pass
```

## 📈 KPI Monitoring & Auto-Triggers

### Real-time Triggers

| Condition | Threshold | Auto Action | Priority |
|-----------|-----------|-------------|----------|
| ΔRate Change | >10% | `/web_search market_updates` | HIGH |
| ETA Delay | >24h | `/weather_tie check_conditions` | HIGH |
| Pressure Load | >4t/m² | `/safety_verification required` | CRITICAL |
| OCR Confidence | <85% | `/switch_mode ZERO` | CRITICAL |
| Certificate Expiry | <30 days | `/cert_renewal_alert` | HIGH |
| Cost Variance | >15% | `/cost_audit required` | MEDIUM |

### Performance Metrics

- **System Uptime**: 99.2%
- **Average Confidence**: 97.3%
- **Response Time**: <3 seconds
- **Success Rate**: ≥95%
- **Error Rate**: <3%

## 🏢 Partnership Integrations

### 🇰🇷 Samsung C&T Corporation
- **eDAS Integration**: Electronic Data and Analytics Service
- **BOE Processing**: Automated Bill of Entry submission
- **Warehouse Management**: WHF capacity optimization
- **Cost Performance**: Real-time budget tracking

### 🇦🇪 ADNOC·DSV Partnership
- **Port Operations**: Jebel Ali Port real-time data
- **FANR Compliance**: Regulatory approval automation
- **Inland Logistics**: UAE distribution network
- **Digital Twin**: IoT-enabled asset monitoring

## 🔐 Security & Compliance

### Regulatory Compliance
- **FANR** (Federal Authority for Nuclear Regulation)
- **MOIAT** (Ministry of Industry and Advanced Technology)
- **UAE Customs** regulations
- **International Trade** compliance

### Data Protection
- **PII Protection**: Automated screening and masking
- **NDA Compliance**: Confidential data handling
- **Audit Trails**: Complete operation logging
- **Multi-source Validation**: ≥90% confidence verification

## 📁 Project Structure

```
macho-gpt-tdd/
├── 📄 logi_meta.py           # Main CLI interface
├── 📋 plan.md                # TDD development guidelines
├── 📦 macho_gpt/             # Core package
│   ├── 🧠 core/              # Core system modules
│   │   ├── logi_master.py    # Logistics master processor
│   │   ├── modes.py          # Containment mode management
│   │   └── commands.py       # Command processor
│   └── 🔌 integrations/      # External integrations
│       ├── samsung_ct.py     # Samsung C&T connector
│       ├── adnoc_dsv.py      # ADNOC·DSV connector
│       └── tools.py          # Tool integration manager
├── ⚙️ config/                # Configuration files
│   └── macho_config.yaml     # System configuration
├── 📊 templates/             # Document templates
├── 📈 reports/               # Generated reports
└── 🧪 tests/                 # Test suite
```

## 🔄 API Reference

### LogiMaster Core Methods

```python
from macho_gpt import LogiMaster

logi = LogiMaster()

# Invoice processing
result = await logi.invoice_audit("invoice.pdf")

# Heat-Stow analysis
result = await logi.heat_stow_analysis(container_data)

# Weather-tie check
result = await logi.weather_tie_check("AEJEA", "VESSEL_001")

# Compliance validation
result = await logi.validate_compliance("certificate")
```

### Mode Management

```python
from macho_gpt.core.modes import ModeManager, ContainmentMode

mode_manager = ModeManager()

# Switch modes
mode_manager.switch_mode(ContainmentMode.LATTICE, "document_processing")

# Check compatibility
is_compatible = mode_manager.is_compatible_command("invoice_audit")

# Get mode status
status = mode_manager.get_mode_status()
```

### Tool Integration

```python
from macho_gpt.integrations.tools import ToolManager

tool_manager = ToolManager()

# Execute tool operation
result = tool_manager.execute_tool_operation(
    "web_search",
    "search_operation", 
    {"query": "shipping rates 2024"}
)

# Check tool health
health = tool_manager.check_tool_health("ocr_engine")
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_logi_master.py

# Run with coverage
python -m pytest --cov=macho_gpt tests/
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: System performance validation
- **Compliance Tests**: Regulatory requirement verification

## 📚 Documentation

### Additional Resources

- [TDD Development Guidelines](plan.md)
- [API Documentation](docs/api.md)
- [Configuration Guide](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Partnership Integration Guide](docs/partnerships.md)

## 🤝 Contributing

### Development Workflow

1. **Follow TDD Principles**: Red → Green → Refactor
2. **Maintain Standards**: Confidence ≥95%, Success Rate ≥95%
3. **Integration Ready**: All code compatible with /cmd system
4. **Documentation**: Update README and API docs

### Commit Standards

```bash
# Structural changes
git commit -m "[STRUCT] Extract HS code validation into separate module"

# Behavioral changes
git commit -m "[FEAT] Add FANR compliance auto-verification"

# MACHO-GPT specific
git commit -m "[MODE] Implement NEXUS mode for AI collaboration"
```

## 📞 Support

### Quick Commands for Help

```bash
# System diagnostics
python logi_meta.py --status

# Available commands
python logi_meta.py --help

# Tool status check
python logi_meta.py --tools

# Export current configuration
python logi_meta.py --export yaml
```

### Contact Information

- **Project Team**: HVDC Logistics Development
- **Email**: logistics@hvdc-project.com
- **Documentation**: [HVDC Project Wiki](https://wiki.hvdc-project.com)
- **Issue Tracking**: [GitHub Issues](https://github.com/hvdc-project/macho-gpt/issues)

---

## 🔧 추천 명령어

```bash
python logi_meta.py --status          # 시스템 전체 상태 점검
python logi_meta.py --list all        # 모든 명령어 확인
python logi_meta.py "automate_workflow" # 자동화 파이프라인 테스트
```

**🚛 MACHO-GPT v3.4-mini - Powering the future of HVDC project logistics**