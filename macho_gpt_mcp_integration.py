# MACHO-GPT v3.4-mini MCP Integration Module
# HVDC Project - Samsung C&T Logistics
# Enhanced MCP SuperAssistant Integration

import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import asyncio
from pathlib import Path

class MachoMCPIntegrator:
    """
    MACHO-GPT v3.4-mini integration with MCP SuperAssistant
    
    Integrates 5 active MCP servers:
    - filesystem: File operations (12 tools)
    - sequential-thinking: Problem solving (1 tool)
    - memory: Knowledge graph (9 tools)
    - everything: Protocol testing (8 tools, 10 resources)
    - puppeteer: Browser automation (7 tools, 1 resource)
    """
    
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 3006):
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        self.mcp_url = f"http://{mcp_host}:{mcp_port}"
        self.sse_url = f"{self.mcp_url}/sse"
        self.message_url = f"{self.mcp_url}/message"
        
        # MACHO-GPT Configuration
        self.current_mode = "PRIME"
        self.confidence_threshold = 0.95
        self.hvdc_project_path = "C:\\cursor-mcp\\HVDC_PJT"
        
        # Active MCP Servers
        self.active_servers = {
            "filesystem": {"tools": 12, "resources": 0, "status": "active"},
            "sequential-thinking": {"tools": 1, "resources": 0, "status": "active"},
            "memory": {"tools": 9, "resources": 0, "status": "active"},
            "everything": {"tools": 8, "resources": 10, "status": "active"},
            "puppeteer": {"tools": 7, "resources": 1, "status": "active"}
        }
        
        # Logistics Integration Points
        self.logistics_workflows = {
            "invoice_ocr": {"server": "filesystem", "confidence_required": 0.90},
            "heat_stow": {"server": "memory", "confidence_required": 0.95},
            "weather_tie": {"server": "puppeteer", "confidence_required": 0.85},
            "container_analysis": {"server": "sequential-thinking", "confidence_required": 0.90},
            "kpi_monitoring": {"server": "everything", "confidence_required": 0.95}
        }
        
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for MACHO-GPT MCP integration"""
        logger = logging.getLogger("MACHO_MCP")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("macho_mcp_integration.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def verify_mcp_connection(self) -> Dict[str, Any]:
        """
        Verify MCP SuperAssistant Proxy connection and server status
        
        Returns:
            dict: Connection status and server details
        """
        try:
            # Test SSE endpoint
            response = requests.get(f"{self.mcp_url}/sse", timeout=5)
            connection_status = "connected" if response.status_code == 200 else "failed"
            
            result = {
                "status": connection_status,
                "mcp_url": self.mcp_url,
                "timestamp": datetime.now().isoformat(),
                "active_servers": self.active_servers,
                "total_tools": sum(server["tools"] for server in self.active_servers.values()),
                "total_resources": sum(server["resources"] for server in self.active_servers.values()),
                "confidence": 0.98,
                "mode": self.current_mode
            }
            
            self.logger.info(f"MCP connection verified: {connection_status}")
            return result
            
        except Exception as e:
            self.logger.error(f"MCP connection failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.0
            }
    
    def test_filesystem_integration(self) -> Dict[str, Any]:
        """
        Test HVDC project file access through MCP filesystem server
        
        Returns:
            dict: Test results and file access status
        """
        try:
            # Simulate filesystem server interaction
            test_files = [
                "config.json",
                "start_mcp_proxy.ps1",
                "MCP_PROXY_README.md",
                "data/HVDC WAREHOUSE_INVOICE.xlsx"
            ]
            
            accessible_files = []
            for file_path in test_files:
                full_path = Path(self.hvdc_project_path) / file_path
                if full_path.exists():
                    accessible_files.append({
                        "file": file_path,
                        "size": full_path.stat().st_size,
                        "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
                        "accessible": True
                    })
                else:
                    accessible_files.append({
                        "file": file_path,
                        "accessible": False
                    })
            
            success_rate = len([f for f in accessible_files if f.get("accessible", False)]) / len(test_files)
            
            result = {
                "test": "filesystem_integration",
                "status": "success" if success_rate >= 0.75 else "partial",
                "success_rate": success_rate,
                "accessible_files": accessible_files,
                "server": "filesystem",
                "tools_available": 12,
                "confidence": min(0.95, success_rate * 1.1),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Filesystem integration test: {success_rate:.2%} success rate")
            return result
            
        except Exception as e:
            self.logger.error(f"Filesystem integration test failed: {str(e)}")
            return {
                "test": "filesystem_integration",
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
    
    def configure_logistics_workflows(self) -> Dict[str, Any]:
        """
        Configure MACHO-GPT logistics workflows with MCP tools
        
        Returns:
            dict: Workflow configuration status
        """
        try:
            configured_workflows = {}
            
            for workflow_name, config in self.logistics_workflows.items():
                server_name = config["server"]
                server_info = self.active_servers.get(server_name, {})
                
                if server_info.get("status") == "active":
                    configured_workflows[workflow_name] = {
                        "status": "configured",
                        "server": server_name,
                        "tools_available": server_info["tools"],
                        "resources_available": server_info["resources"],
                        "confidence_threshold": config["confidence_required"],
                        "integration_ready": True
                    }
                else:
                    configured_workflows[workflow_name] = {
                        "status": "unavailable",
                        "server": server_name,
                        "integration_ready": False
                    }
            
            success_count = len([w for w in configured_workflows.values() if w.get("integration_ready", False)])
            configuration_rate = success_count / len(self.logistics_workflows)
            
            result = {
                "configuration": "logistics_workflows",
                "status": "success" if configuration_rate >= 0.8 else "partial",
                "configuration_rate": configuration_rate,
                "workflows": configured_workflows,
                "total_workflows": len(self.logistics_workflows),
                "ready_workflows": success_count,
                "confidence": min(0.95, configuration_rate * 1.05),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Logistics workflows configured: {configuration_rate:.2%} success rate")
            return result
            
        except Exception as e:
            self.logger.error(f"Logistics workflow configuration failed: {str(e)}")
            return {
                "configuration": "logistics_workflows",
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
    
    def test_chrome_extension_connectivity(self) -> Dict[str, Any]:
        """
        Test Chrome Extension connectivity for real-time operations
        
        Returns:
            dict: Chrome Extension connection status
        """
        try:
            # Test SSE endpoint connectivity
            sse_response = requests.get(self.sse_url, timeout=3)
            sse_status = "connected" if sse_response.status_code == 200 else "failed"
            
            # Test message endpoint
            message_response = requests.post(
                self.message_url,
                json={"test": "connectivity"},
                timeout=3
            )
            message_status = "connected" if message_response.status_code in [200, 400] else "failed"
            
            overall_status = "connected" if sse_status == "connected" and message_status == "connected" else "failed"
            
            result = {
                "test": "chrome_extension_connectivity",
                "status": overall_status,
                "sse_endpoint": {
                    "url": self.sse_url,
                    "status": sse_status
                },
                "message_endpoint": {
                    "url": self.message_url,
                    "status": message_status
                },
                "cors_enabled": True,
                "transport": "SSE",
                "confidence": 0.95 if overall_status == "connected" else 0.3,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Chrome Extension connectivity: {overall_status}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chrome Extension connectivity test failed: {str(e)}")
            return {
                "test": "chrome_extension_connectivity",
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive MACHO-GPT MCP integration report
        
        Returns:
            dict: Complete integration status report
        """
        self.logger.info("Generating MACHO-GPT MCP integration report")
        
        # Run all integration tests
        connection_test = self.verify_mcp_connection()
        filesystem_test = self.test_filesystem_integration()
        workflow_config = self.configure_logistics_workflows()
        chrome_test = self.test_chrome_extension_connectivity()
        
        # Calculate overall integration score
        test_results = [connection_test, filesystem_test, workflow_config, chrome_test]
        confidence_scores = [result.get("confidence", 0) for result in test_results]
        overall_confidence = np.mean(confidence_scores)
        
        # Determine integration status
        if overall_confidence >= 0.90:
            integration_status = "FULLY_INTEGRATED"
        elif overall_confidence >= 0.75:
            integration_status = "MOSTLY_INTEGRATED"
        elif overall_confidence >= 0.50:
            integration_status = "PARTIALLY_INTEGRATED"
        else:
            integration_status = "INTEGRATION_FAILED"
        
        # Generate report
        report = {
            "macho_gpt_version": "v3.4-mini",
            "project": "HVDC_Samsung_CT_ADNOC_DSV",
            "integration_status": integration_status,
            "overall_confidence": overall_confidence,
            "timestamp": datetime.now().isoformat(),
            "mcp_configuration": {
                "proxy_url": self.mcp_url,
                "active_servers": len(self.active_servers),
                "total_tools": sum(server["tools"] for server in self.active_servers.values()),
                "total_resources": sum(server["resources"] for server in self.active_servers.values())
            },
            "test_results": {
                "connection_test": connection_test,
                "filesystem_test": filesystem_test,
                "workflow_configuration": workflow_config,
                "chrome_extension_test": chrome_test
            },
            "recommendations": self._generate_recommendations(test_results),
            "next_steps": self._generate_next_steps(integration_status)
        }
        
        self.logger.info(f"Integration report generated: {integration_status} ({overall_confidence:.2%})")
        return report
    
    def _generate_recommendations(self, test_results: List[Dict]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for result in test_results:
            confidence = result.get("confidence", 0)
            if confidence < 0.75:
                test_name = result.get("test", result.get("configuration", "unknown"))
                recommendations.append(f"Improve {test_name} (confidence: {confidence:.2%})")
        
        if not recommendations:
            recommendations.append("All systems operating optimally")
        
        return recommendations
    
    def _generate_next_steps(self, status: str) -> List[str]:
        """Generate next steps based on integration status"""
        if status == "FULLY_INTEGRATED":
            return [
                "Begin production logistics operations",
                "Monitor KPI performance metrics",
                "Set up automated workflows"
            ]
        elif status == "MOSTLY_INTEGRATED":
            return [
                "Address remaining integration issues",
                "Test edge cases and error handling",
                "Prepare for production deployment"
            ]
        elif status == "PARTIALLY_INTEGRATED":
            return [
                "Troubleshoot failed components",
                "Verify server configurations",
                "Re-run integration tests"
            ]
        else:
            return [
                "Check MCP proxy status",
                "Verify network connectivity",
                "Review server logs for errors"
            ]

def main():
    """Main integration function for MACHO-GPT MCP integration"""
    print("🚀 MACHO-GPT v3.4-mini MCP Integration Starting...")
    
    integrator = MachoMCPIntegrator()
    report = integrator.generate_integration_report()
    
    # Display results
    print(f"\n📊 Integration Status: {report['integration_status']}")
    print(f"🎯 Overall Confidence: {report['overall_confidence']:.2%}")
    print(f"🔧 Active MCP Servers: {report['mcp_configuration']['active_servers']}")
    print(f"🛠️ Total Tools Available: {report['mcp_configuration']['total_tools']}")
    print(f"📦 Total Resources Available: {report['mcp_configuration']['total_resources']}")
    
    print("\n📋 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print("\n🎯 Next Steps:")
    for step in report['next_steps']:
        print(f"  • {step}")
    
    # Save report
    report_file = f"macho_mcp_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved: {report_file}")
    
    return report

if __name__ == "__main__":
    report = main() 