#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini Command Metadata System
HVDC PROJECT - Samsung C&T Logistics | ADNOC·DSV Partnership
Cursor IDE Integration Module
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

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
        return {
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
                CommandInfo("logi_master warehouse", "core_workflow", "WHF capacity management", 
                          ["drive_search", "calculations"], 96.1, "1-3min", "✅ Active", "2025-06-25"),
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
    
    def _initialize_kpi_triggers(self) -> List[KPITrigger]:
        """Initialize KPI trigger configurations"""
        return [
            KPITrigger("ΔRate Change", ">10%", "/web_search market_updates", "✅ Active"),
            KPITrigger("ETA Delay", ">24h", "/weather_tie check_conditions", "✅ Active"),
            KPITrigger("Pressure Load", ">4t/m²", "/safety_verification required", "✅ Active"),
            KPITrigger("Utilization Rate", ">85%", "/capacity_optimization analysis", "✅ Active"),
            KPITrigger("Certificate Expiry", "<30 days", "/cert_renewal_alert", "✅ Active"),
            KPITrigger("Cost Variance", ">15%", "/cost_audit required", "✅ Active"),
            KPITrigger("OCR Confidence", "<85%", "/manual_review required", "✅ Active"),
            KPITrigger("Data Lag", ">1h", "/sync_systems trigger", "✅ Active"),
        ]
    
    def _initialize_tool_integrations(self) -> List[ToolIntegration]:
        """Initialize tool integration status"""
        return [
            ToolIntegration("web_search", ToolStatus.OPERATIONAL, 99.7, "2025-06-25 14:23", "Latest"),
            ToolIntegration("google_drive_search", ToolStatus.OPERATIONAL, 99.2, "2025-06-25 14:23", "Latest"),
            ToolIntegration("filesystem", ToolStatus.OPERATIONAL, 99.8, "2025-06-25 14:23", "Latest"),
            ToolIntegration("repl", ToolStatus.OPERATIONAL, 99.9, "2025-06-25 14:23", "Latest"),
            ToolIntegration("artifacts", ToolStatus.OPERATIONAL, 99.6, "2025-06-25 14:23", "Latest"),
            ToolIntegration("OCR_Engine", ToolStatus.OPERATIONAL, 97.8, "2025-06-25 14:22", "v2.1"),
            ToolIntegration("Weather_API", ToolStatus.OPERATIONAL, 98.3, "2025-06-25 14:21", "v3.0"),
            ToolIntegration("Port_API", ToolStatus.DEGRADED, 89.2, "2025-06-25 14:20", "v1.8"),
        ]

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get complete system status
        
        Returns:
            dict: Complete system metadata and status
        """
        return {
            "system_info": {
                "version": self.version,
                "project": self.project,
                "current_mode": self.current_mode.value,
                "confidence": f"{self.confidence}%",
                "uptime": f"{self.uptime}%",
                "active_modules": f"{self.active_modules}/{self.total_modules}",
                "timestamp": datetime.now().isoformat()
            },
            "integration_status": "✅ FULL",
            "total_commands": sum(len(commands) for commands in self.commands.values()),
            "fail_safe_rate": "<3%"
        }

    def list_commands_by_category(self, category: str = None) -> Dict[str, List[Dict]]:
        """
        List commands by category
        
        Args:
            category: Optional category filter
            
        Returns:
            dict: Commands organized by category
        """
        if category:
            if category in self.commands:
                return {category: [asdict(cmd) for cmd in self.commands[category]]}
            else:
                return {"error": f"Category '{category}' not found"}
        
        return {cat: [asdict(cmd) for cmd in commands] 
                for cat, commands in self.commands.items()}

    def get_kpi_triggers(self) -> List[Dict]:
        """
        Get KPI trigger configurations
        
        Returns:
            list: KPI trigger configurations
        """
        return [asdict(trigger) for trigger in self.kpi_triggers]

    def get_tool_status(self) -> List[Dict]:
        """
        Get tool integration status
        
        Returns:
            list: Tool integration status
        """
        result = []
        for tool in self.tool_integrations:
            tool_dict = asdict(tool)
            # Convert ToolStatus enum to string value for JSON serialization
            tool_dict['status'] = tool.status.value
            result.append(tool_dict)
        return result

    def execute_command(self, command: str, args: Dict = None) -> Dict[str, Any]:
        """
        Execute MACHO-GPT command with metadata tracking
        
        Args:
            command: Command to execute
            args: Optional command arguments
            
        Returns:
            dict: Execution result with metadata
        """
        start_time = datetime.now()
        
        # Find command info
        cmd_info = None
        for category, commands in self.commands.items():
            for cmd in commands:
                if cmd.name.startswith(command):
                    cmd_info = cmd
                    break
            if cmd_info:
                break
        
        if not cmd_info:
            return {
                "status": "ERROR",
                "message": f"Command '{command}' not found",
                "available_commands": self.get_available_commands()
            }
        
        # Simulate command execution
        execution_time = datetime.now() - start_time
        
        # Generate command recommendations
        recommendations = self._generate_command_recommendations(command, cmd_info.category)
        
        return {
            "status": "SUCCESS",
            "command": command,
            "category": cmd_info.category,
            "execution_time": str(execution_time),
            "confidence": cmd_info.success_rate,
            "tools_used": cmd_info.integration,
            "next_commands": recommendations,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_command_recommendations(self, executed_cmd: str, category: str) -> List[str]:
        """
        Generate contextual command recommendations
        
        Args:
            executed_cmd: Command that was executed
            category: Command category
            
        Returns:
            list: Recommended follow-up commands
        """
        recommendations = []
        
        # Context-based recommendations
        if "invoice-audit" in executed_cmd:
            recommendations = [
                "/visualize_data --type=dashboard [Generate audit visualization]",
                "/save_template audit_result [Save audit template]",
                "/logi_master report [Generate audit report]"
            ]
        elif "kpi-dash" in executed_cmd:
            recommendations = [
                "/check_KPI [Validate specific metrics]",
                "/automate_workflow kpi_monitoring [Setup automation]",
                "/schedule_email [Schedule KPI reports]"
            ]
        elif "switch_mode" in executed_cmd:
            recommendations = [
                "/health_check [Verify mode switch]",
                "/logi_meta system [Check system status]",
                "/use_template mode_specific [Load mode templates]"
            ]
        elif category == "visualization":
            recommendations = [
                "/save_template visualization [Save chart template]",
                "/export_data [Export visualization data]",
                "/schedule_email [Share visualization]"
            ]
        else:
            # Default recommendations based on category
            if category == "core_workflow":
                recommendations = [
                    "/visualize_data --type=dashboard [Create visualization]",
                    "/save_template workflow [Save workflow template]",
                    "/health_check [System validation]"
                ]
            elif category == "automation":
                recommendations = [
                    "/schedule_email [Setup notifications]",
                    "/health_check [Monitor automation]",
                    "/optimize_workflow [Improve efficiency]"
                ]
        
        return recommendations[:3]  # Return top 3 recommendations

    def get_available_commands(self) -> List[str]:
        """Get list of all available commands"""
        all_commands = []
        for commands in self.commands.values():
            all_commands.extend([cmd.name for cmd in commands])
        return sorted(all_commands)

    def export_metadata(self, format: str = "json") -> str:
        """
        Export complete metadata
        
        Args:
            format: Export format (json, yaml)
            
        Returns:
            str: Formatted metadata
        """
        metadata = {
            "system_status": self.get_system_status(),
            "commands": self.list_commands_by_category(),
            "kpi_triggers": self.get_kpi_triggers(),
            "tool_integrations": self.get_tool_status()
        }
        
        if format.lower() == "yaml":
            return yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        else:
            return json.dumps(metadata, indent=2, ensure_ascii=False)

    def format_macho_response(self, data: Dict, cmd_recommendations: List[str]) -> str:
        """
        Format response in MACHO-GPT style
        
        Args:
            data: Response data
            cmd_recommendations: Command recommendations
            
        Returns:
            str: Formatted response
        """
        return f"""
{data.get('main_content', 'Operation completed successfully.')}

📊 **Status:** {data.get('confidence', 95.0)}% | {', '.join(data.get('tools_used', ['system']))} | {data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}

🔧 **추천 명령어:**
{chr(10).join(cmd_recommendations[:3])}
"""


# CLI Interface for Cursor IDE
def main():
    """Main CLI interface for Cursor IDE integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MACHO-GPT v3.4-mini Metadata System")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("--list", choices=["all", "containment", "core_workflow", "automation", "visualization"], 
                       help="List commands by category")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--kpi", action="store_true", help="Show KPI triggers")
    parser.add_argument("--tools", action="store_true", help="Show tool integration status")
    parser.add_argument("--export", choices=["json", "yaml"], help="Export metadata")
    
    args = parser.parse_args()
    
    logi_meta = LogiMetaSystem()
    
    if args.status:
        status = logi_meta.get_system_status()
        print("🚛 MACHO-GPT v3.4-mini System Status")
        print("=" * 50)
        for key, value in status["system_info"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print(f"Total Commands: {status['total_commands']}")
        print(f"Fail-safe Rate: {status['fail_safe_rate']}")
        
    elif args.list:
        commands = logi_meta.list_commands_by_category(args.list if args.list != "all" else None)
        print(f"📋 Commands ({args.list})")
        print("=" * 50)
        for category, cmd_list in commands.items():
            print(f"\n{category.upper()}:")
            for cmd in cmd_list:
                print(f"  /{cmd['name']} - {cmd['description']}")
                
    elif args.kpi:
        triggers = logi_meta.get_kpi_triggers()
        print("📈 KPI Triggers")
        print("=" * 50)
        for trigger in triggers:
            print(f"{trigger['condition']} {trigger['threshold']} → {trigger['auto_action']} ({trigger['status']})")
            
    elif args.tools:
        tools = logi_meta.get_tool_status()
        print("🔧 Tool Integration Status")
        print("=" * 50)
        for tool in tools:
            print(f"{tool['name']}: {tool['status']} ({tool['uptime']}% uptime)")
            
    elif args.export:
        metadata = logi_meta.export_metadata(args.export)
        filename = f"macho_gpt_metadata.{args.export}"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(metadata)
        print(f"Metadata exported to {filename}")
        
    elif args.command:
        result = logi_meta.execute_command(args.command)
        if result["status"] == "SUCCESS":
            response_data = {
                "main_content": f"Command '{args.command}' executed successfully.",
                "confidence": result["confidence"],
                "tools_used": result["tools_used"],
                "timestamp": result["timestamp"]
            }
            print(logi_meta.format_macho_response(response_data, result["next_commands"]))
        else:
            print(f"❌ Error: {result['message']}")
            if "available_commands" in result:
                print("\nAvailable commands:")
                for cmd in result["available_commands"][:10]:  # Show first 10
                    print(f"  /{cmd}")
                    
    else:
        # Show quick help
        print("🚛 MACHO-GPT v3.4-mini - Quick Help")
        print("=" * 50)
        print("python logi_meta.py --status          # System status")
        print("python logi_meta.py --list all        # All commands")
        print("python logi_meta.py --kpi             # KPI triggers")
        print("python logi_meta.py --tools           # Tool status")
        print("python logi_meta.py 'command_name'    # Execute command")
        print("python logi_meta.py --export json     # Export metadata")


if __name__ == "__main__":
    main()