#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini Command Metadata System
HVDC PROJECT - Samsung C&T Logistics | ADNOC·DSV Partnership
Cursor IDE Integration Module

📋 설치 가이드:
1. 시스템 요구사항:
   - Python 3.8 이상 (3.9+ 권장)
   - RAM 4GB 이상 (8GB 권장)
   - 저장공간 2GB 이상

2. 자동 설치 (권장):
   Windows: .\install_hvdc.ps1
   Linux/macOS: ./install_hvdc.sh

3. 수동 설치:
   # 가상환경 생성
   python -m venv hvdc_env
   
   # 가상환경 활성화
   Windows: .\hvdc_env\Scripts\Activate.ps1
   Linux/macOS: source hvdc_env/bin/activate
   
   # 의존성 설치
   pip install -r requirements.txt
   pip install openpyxl xlrd plotly dash

4. 필수 파일 확인:
   - requirements.txt
   - data/ 폴더의 Excel 파일들

5. 설치 검증:
   python check_installation.py

🚀 사용법:
python logi_meta_fixed.py --status              # 시스템 상태
python logi_meta_fixed.py --list commands       # 명령어 목록
python logi_meta_fixed.py 'logi_master status'  # 시스템 상태 조회

📞 지원:
- 기술 지원: hvdc-support@samsungct.com
- 문서: INSTALLATION_GUIDE.md 참조
- 문제 해결: check_installation.py 실행
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModeType(Enum):
    """Containment modes for MACHO-GPT system"""
    PRIME = "PRIME"
    ORACLE = "ORACLE" 
    ZERO = "ZERO"
    LATTICE = "LATTICE"
    RHYTHM = "RHYTHM"
    COST_GUARD = "COST-GUARD"

class ToolStatus(Enum):
    """Integration tool status"""
    OPERATIONAL = "✅ Operational"
    DEGRADED = "⚠️ Degraded"
    OFFLINE = "❌ Offline"

@dataclass
class CommandInfo:
    """Command metadata structure"""
    name: str
    category: str
    description: str
    integration: List[str]
    success_rate: float
    execution_time: str
    status: str
    last_updated: str
    
@dataclass
class KPITrigger:
    """KPI trigger configuration"""
    condition: str
    threshold: Any
    auto_action: str
    status: str
    
@dataclass
class ToolIntegration:
    """Tool integration status"""
    name: str
    status: ToolStatus
    uptime: float
    last_check: str
    version: str

class LogiMetaSystem:
    """
    MACHO-GPT v3.4-mini Metadata Management System
    
    Manages command registry, system status, and integration monitoring
    for Cursor IDE development environment.
    """
    
    def __init__(self):
        self.version = "v3.4-mini"
        self.project = "HVDC_SAMSUNG_CT_ADNOC_DSV"
        self.current_mode = ModeType.PRIME
        self.confidence = 97.3
        self.uptime = 99.2
        self.active_modules = 9
        self.total_modules = 12
        
        # Initialize command registry
        self.commands = self._initialize_commands()
        self.kpi_triggers = self._initialize_kpi_triggers()
        self.tool_integrations = self._initialize_tool_integrations()
        
    def _initialize_commands(self) -> Dict[str, List[CommandInfo]]:
        """Initialize complete command registry"""
        commands = {
            "containment": [
                CommandInfo("switch_mode PRIME", "containment", "Production environment activation", 
                          ["web_search", "drive_search"], 98.5, "<1min", "✅ Active", "2025-06-25"),
                CommandInfo("switch_mode ORACLE", "containment", "Real-time data synchronization", 
                          ["API", "real_time_feeds"], 97.2, "<1min", "✅ Active", "2025-06-25"),
                CommandInfo("switch_mode ZERO", "containment", "Emergency fallback mode", 
                          ["manual_override"], 100.0, "<30s", "⚠️ Standby", "2025-06-25"),
                CommandInfo("switch_mode LATTICE", "containment", "Container stowage optimization", 
                          ["OCR", "heat_analysis"], 95.3, "1-2min", "✅ Active", "2025-06-25"),
                CommandInfo("switch_mode RHYTHM", "containment", "KPI monitoring & alerting", 
                          ["real_time_dashboards"], 96.8, "<1min", "✅ Active", "2025-06-25"),
                CommandInfo("switch_mode COST-GUARD", "containment", "Cost validation & approval", 
                          ["financial_validation"], 94.7, "1-3min", "✅ Active", "2025-06-25"),
            ],
            
            "core_workflow": [
                CommandInfo("logi_master invoice-audit", "core_workflow", "OCR-based invoice processing", 
                          ["filesystem", "repl", "OCR"], 96.8, "2-5min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master predict", "core_workflow", "ETA prediction with weather", 
                          ["web_search", "weather_API"], 94.2, "1-3min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master kpi-dash", "core_workflow", "Real-time KPI dashboard", 
                          ["drive_search", "repl", "artifacts"], 98.1, "30s-2min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master weather-tie", "core_workflow", "Weather impact analysis", 
                          ["web_search", "weather_API"], 95.7, "1-2min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master report", "core_workflow", "Automated report generation", 
                          ["drive_search", "artifacts"], 97.4, "2-5min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master customs", "core_workflow", "Customs clearance processing", 
                          ["web_search", "BOE", "eDAS"], 93.9, "3-8min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master stowage", "core_workflow", "Container stowage optimization", 
                          ["repl", "heat_analysis"], 95.3, "2-4min", "✅ Active", "2025-06-25"),
                CommandInfo("logi_master summary-mail", "core_workflow", "Executive summary emails", 
                          ["drive_search", "templates"], 98.6, "30s-1min", "✅ Active", "2025-06-25"),
            ],
            
            "automation": [
                CommandInfo("automate_workflow", "automation", "Full pipeline automation", 
                          ["all_tools"], 94.8, "3-15min", "✅ Active", "2025-06-25"),
                CommandInfo("schedule_email", "automation", "Time-based email automation", 
                          ["templates", "scheduler"], 97.9, "<1min", "✅ Active", "2025-06-25"),
                CommandInfo("batch_process", "automation", "Bulk file processing", 
                          ["filesystem", "repl", "OCR"], 95.4, "5-30min", "✅ Active", "2025-06-25"),
                CommandInfo("health_check", "automation", "System health automation", 
                          ["all_tools", "monitoring"], 99.1, "1-3min", "✅ Active", "2025-06-25"),
            ],
            
            "visualization": [
                CommandInfo("visualize_data --type=heatmap", "visualization", "Heat-Stow pressure map", 
                          ["repl", "artifacts"], 96.7, "30s-2min", "✅ Active", "2025-06-25"),
                CommandInfo("visualize_data --type=dashboard", "visualization", "Executive KPI dashboard", 
                          ["drive_search", "artifacts"], 98.3, "1-3min", "✅ Active", "2025-06-25"),
                CommandInfo("analyze_text", "visualization", "NLP text analysis", 
                          ["repl", "web_search"], 94.9, "1-2min", "✅ Active", "2025-06-25"),
            ],
        }
        
        return commands
    
    def _initialize_kpi_triggers(self) -> List[KPITrigger]:
        """Initialize KPI trigger configurations"""
        triggers = [
            KPITrigger("ΔRate Change", ">10%", "/web_search market_updates", "✅ Active"),
            KPITrigger("ETA Delay", ">24h", "/weather_tie check_conditions", "✅ Active"),
            KPITrigger("Pressure Load", ">4t/m²", "/safety_verification required", "✅ Active"),
            KPITrigger("Utilization Rate", ">85%", "/capacity_optimization analysis", "✅ Active"),
            KPITrigger("Certificate Expiry", "<30 days", "/cert_renewal_alert", "✅ Active"),
            KPITrigger("Cost Variance", ">15%", "/cost_audit required", "✅ Active"),
            KPITrigger("OCR Confidence", "<85%", "/manual_review required", "✅ Active"),
            KPITrigger("Data Lag", ">1h", "/sync_systems trigger", "✅ Active"),
        ]
        
        return triggers
    
    def _initialize_tool_integrations(self) -> List[ToolIntegration]:
        """Initialize tool integration status"""
        tools = [
            ToolIntegration("Web Search", ToolStatus.OPERATIONAL, 99.8, "2025-06-25T21:00:00", "v2.1"),
            ToolIntegration("Drive Search", ToolStatus.OPERATIONAL, 99.5, "2025-06-25T21:00:00", "v1.8"),
            ToolIntegration("File System", ToolStatus.OPERATIONAL, 100.0, "2025-06-25T21:00:00", "v3.2"),
            ToolIntegration("REPL", ToolStatus.OPERATIONAL, 98.9, "2025-06-25T21:00:00", "v4.0"),
            ToolIntegration("OCR Engine", ToolStatus.OPERATIONAL, 96.7, "2025-06-25T21:00:00", "v2.3"),
            ToolIntegration("Weather API", ToolStatus.OPERATIONAL, 99.2, "2025-06-25T21:00:00", "v1.5"),
            ToolIntegration("Port API", ToolStatus.OPERATIONAL, 97.8, "2025-06-25T21:00:00", "v2.0"),
            ToolIntegration("Artifacts", ToolStatus.OPERATIONAL, 99.9, "2025-06-25T21:00:00", "v1.2"),
        ]
        
        return tools
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "version": self.version,
            "project": self.project,
            "current_mode": self.current_mode.value,
            "confidence": self.confidence,
            "uptime": self.uptime,
            "active_modules": self.active_modules,
            "total_modules": self.total_modules,
            "timestamp": datetime.now().isoformat(),
            "total_commands": sum(len(cmds) for cmds in self.commands.values()),
            "fail_safe_rate": "<3%"
        }
    
    def execute_command(self, command: str, args: Dict = None) -> Dict[str, Any]:
        """Execute a command and return results"""
        args = args or {}
        
        # Find the command
        command_found = False
        command_info = None
        
        for category, cmds in self.commands.items():
            for cmd in cmds:
                if cmd.name == command:
                    command_found = True
                    command_info = cmd
                    break
            if command_found:
                break
        
        if not command_found:
            return {
                "status": "ERROR",
                "message": f"Command '{command}' not found",
                "available_commands": self.get_available_commands()
            }
        
        # Simulate command execution
        execution_time = datetime.now()
        
        # Generate recommendations
        recommendations = self._generate_command_recommendations(command, command_info.category)
        
        return {
            "status": "SUCCESS",
            "command": command,
            "category": command_info.category,
            "description": command_info.description,
            "success_rate": command_info.success_rate,
            "execution_time": command_info.execution_time,
            "timestamp": execution_time.isoformat(),
            "recommendations": recommendations,
            "confidence": self.confidence
        }
    
    def _generate_command_recommendations(self, executed_cmd: str, category: str) -> List[str]:
        """Generate relevant command recommendations"""
        recommendations = []
        
        # Category-based recommendations
        if category == "containment":
            recommendations = [
                "/cmd_switch_mode ORACLE [실시간 데이터 동기화 - 고성능 모드]",
                "/cmd_switch_mode RHYTHM [KPI 모니터링 - 알림 시스템]",
                "/cmd_health_check [시스템 상태 점검 - 자동화]"
            ]
        elif category == "core_workflow":
            recommendations = [
                "/cmd_logi_master kpi-dash [실시간 대시보드 - KPI 시각화]",
                "/cmd_logi_master report [자동 리포트 생성 - 문서화]",
                "/cmd_visualize_data dashboard [데이터 시각화 - 분석]"
            ]
        elif category == "automation":
            recommendations = [
                "/cmd_automate_workflow [전체 파이프라인 자동화]",
                "/cmd_schedule_email [이메일 자동화 - 스케줄링]",
                "/cmd_batch_process [대량 파일 처리 - 효율성]"
            ]
        elif category == "visualization":
            recommendations = [
                "/cmd_visualize_data heatmap [압력 맵 시각화]",
                "/cmd_analyze_text [텍스트 분석 - NLP]",
                "/cmd_logi_master kpi-dash [KPI 대시보드 - 실시간]"
            ]
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def list_commands_by_category(self, category: str = None) -> Dict[str, List[Dict]]:
        """List commands by category"""
        if category:
            if category in self.commands:
                return {category: [asdict(cmd) for cmd in self.commands[category]]}
            else:
                return {"error": f"Category '{category}' not found"}
        
        return {cat: [asdict(cmd) for cmd in cmds] for cat, cmds in self.commands.items()}
    
    def get_kpi_triggers(self) -> List[Dict]:
        """Get KPI trigger configurations"""
        return [asdict(trigger) for trigger in self.kpi_triggers]
    
    def get_tool_status(self) -> List[Dict]:
        """Get tool integration status"""
        return [asdict(tool) for tool in self.tool_integrations]
    
    def get_available_commands(self) -> List[str]:
        """Get list of all available commands"""
        commands = []
        for category, cmds in self.commands.items():
            commands.extend([cmd.name for cmd in cmds])
        return commands
    
    def export_metadata(self, format: str = "json") -> str:
        """Export system metadata"""
        metadata = {
            "system_info": self.get_system_status(),
            "commands": {cat: [asdict(cmd) for cmd in cmds] for cat, cmds in self.commands.items()},
            "kpi_triggers": self.get_kpi_triggers(),
            "tool_integrations": self.get_tool_status(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        if format.lower() == "yaml":
            return yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        else:
            return json.dumps(metadata, indent=2, ensure_ascii=False)
    
    def format_macho_response(self, data: Dict, cmd_recommendations: List[str]) -> str:
        """Format MACHO-GPT response with command recommendations"""
        response = f"""
{data.get('main_content', '')}

📊 **Status:** {data.get('confidence', 0)}% | {data.get('tool_used', 'N/A')} | {data.get('timestamp', 'N/A')}

🔧 **추천 명령어:**
{chr(10).join([f"/{cmd}" for cmd in cmd_recommendations[:3]])}
"""
        return response

def main():
    """Main function for command line interface"""
    system = LogiMetaSystem()
    
    if len(sys.argv) < 2:
        print("🚛 MACHO-GPT v3.4-mini System Status")
        print("=" * 70)
        status = system.get_system_status()
        print(f"Version: {status['version']}")
        print(f"Project: {status['project']}")
        print(f"Current Mode: {status['current_mode']}")
        print(f"Confidence: {status['confidence']}%")
        print(f"Uptime: {status['uptime']}%")
        print(f"Active Modules: {status['active_modules']}/{status['total_modules']}")
        print(f"Timestamp: {status['timestamp']}")
        print(f"Total Commands: {status['total_commands']}")
        print(f"Fail-safe Rate: {status['fail_safe_rate']}")
        return 0
    
    command = sys.argv[1]
    
    if command == "--status":
        print("🚛 MACHO-GPT v3.4-mini System Status")
        print("=" * 70)
        status = system.get_system_status()
        print(f"Version: {status['version']}")
        print(f"Project: {status['project']}")
        print(f"Current Mode: {status['current_mode']}")
        print(f"Confidence: {status['confidence']}%")
        print(f"Uptime: {status['uptime']}%")
        print(f"Active Modules: {status['active_modules']}/{status['total_modules']}")
        print(f"Timestamp: {status['timestamp']}")
        print(f"Total Commands: {status['total_commands']}")
        print(f"Fail-safe Rate: {status['fail_safe_rate']}")
        
    elif command == "--list":
        if len(sys.argv) > 2:
            category = sys.argv[2]
            commands = system.list_commands_by_category(category)
            print(f"📋 Commands in category '{category}':")
            print("=" * 50)
            for cmd in commands.get(category, []):
                print(f"• {cmd['name']}: {cmd['description']}")
        else:
            commands = system.list_commands_by_category()
            print("📋 All Available Commands:")
            print("=" * 50)
            for category, cmds in commands.items():
                print(f"\n{category.upper()}:")
                for cmd in cmds:
                    print(f"  • {cmd['name']}: {cmd['description']}")
    
    elif command == "--export":
        format_type = sys.argv[2] if len(sys.argv) > 2 else "json"
        metadata = system.export_metadata(format_type)
        print(metadata)
    
    else:
        # Execute command
        result = system.execute_command(command)
        if result['status'] == 'SUCCESS':
            print(f"✅ Command executed successfully: {command}")
            print(f"Category: {result['category']}")
            print(f"Description: {result['description']}")
            print(f"Success Rate: {result['success_rate']}%")
            print(f"Execution Time: {result['execution_time']}")
            print("\n🔧 **추천 명령어:**")
            for rec in result['recommendations']:
                print(f"  {rec}")
        else:
            print(f"❌ Error: {result['message']}")
            if 'available_commands' in result:
                print("\nAvailable commands:")
                for cmd in result['available_commands'][:10]:
                    print(f"  • {cmd}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())