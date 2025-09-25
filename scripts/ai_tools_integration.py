#!/usr/bin/env python3
"""
AI Tools Integration Manager for HVDC Project
Manages integration between Continue, Aider, autofix.ci, and Codex Fix
"""

import os
import subprocess
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class AIToolsIntegration:
    """Manages integration between all AI tools in HVDC project"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tools = {
            'continue': self._check_continue,
            'aider': self._check_aider,
            'autofix_ci': self._check_autofix_ci,
            'codex_fix': self._check_codex_fix
        }
    
    def _check_continue(self) -> Dict[str, any]:
        """Check Continue IDE integration status"""
        config_file = self.project_root / '.continue' / 'config.json'
        return {
            'installed': config_file.exists(),
            'config_valid': self._validate_json_config(config_file),
            'api_keys': self._check_api_keys(['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']),
            'status': 'ready' if config_file.exists() else 'not_configured'
        }
    
    def _check_aider(self) -> Dict[str, any]:
        """Check Aider CLI integration status"""
        config_file = self.project_root / '.aider.yaml'
        try:
            result = subprocess.run(['aider', '--version'], capture_output=True, text=True)
            installed = result.returncode == 0
        except FileNotFoundError:
            installed = False
        
        return {
            'installed': installed,
            'config_valid': self._validate_yaml_config(config_file),
            'api_keys': self._check_api_keys(['OPENAI_API_KEY']),
            'status': 'ready' if installed and config_file.exists() else 'not_configured'
        }
    
    def _check_autofix_ci(self) -> Dict[str, any]:
        """Check autofix.ci integration status"""
        config_file = self.project_root / '.autofix.yml'
        workflow_file = self.project_root / '.github' / 'workflows' / 'autofix-ci.yml'
        
        return {
            'installed': config_file.exists() and workflow_file.exists(),
            'config_valid': self._validate_yaml_config(config_file),
            'api_keys': self._check_api_keys(['AUTOFIX_API_KEY', 'OPENAI_API_KEY', 'GITHUB_TOKEN']),
            'status': 'ready' if config_file.exists() and workflow_file.exists() else 'not_configured'
        }
    
    def _check_codex_fix(self) -> Dict[str, any]:
        """Check Codex Fix integration status"""
        script_file = self.project_root / 'tools' / 'codex_fix.py'
        workflow_file = self.project_root / '.github' / 'workflows' / 'codex-fix.yaml'
        
        return {
            'installed': script_file.exists() and workflow_file.exists(),
            'config_valid': True,  # Python script, no config validation needed
            'api_keys': self._check_api_keys(['OPENAI_API_KEY', 'GH_TOKEN']),
            'status': 'ready' if script_file.exists() and workflow_file.exists() else 'not_configured'
        }
    
    def _validate_json_config(self, config_file: Path) -> bool:
        """Validate JSON configuration file"""
        if not config_file.exists():
            return False
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, Exception):
            return False
    
    def _validate_yaml_config(self, config_file: Path) -> bool:
        """Validate YAML configuration file"""
        if not config_file.exists():
            return False
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True
        except (yaml.YAMLError, Exception):
            return False
    
    def _check_api_keys(self, required_keys: List[str]) -> Dict[str, bool]:
        """Check if required API keys are available"""
        return {key: key in os.environ for key in required_keys}
    
    def get_integration_status(self) -> Dict[str, Dict[str, any]]:
        """Get status of all AI tools integration"""
        status = {}
        for tool_name, check_func in self.tools.items():
            status[tool_name] = check_func()
        return status
    
    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""
        status = self.get_integration_status()
        
        report = "# 🤖 HVDC AI Tools Integration Report\n\n"
        report += f"**Generated:** {self._get_timestamp()}\n"
        report += f"**Project:** HVDC Project - Samsung C&T Logistics & ADNOC·DSV Partnership\n\n"
        
        # Summary
        ready_count = sum(1 for tool in status.values() if tool['status'] == 'ready')
        total_count = len(status)
        
        report += f"## 📊 Summary\n\n"
        report += f"- **Ready:** {ready_count}/{total_count} tools\n"
        report += f"- **Status:** {'✅ All Ready' if ready_count == total_count else '⚠️ Some Issues'}\n\n"
        
        # Detailed status
        report += "## 🔧 Tool Status\n\n"
        
        for tool_name, tool_status in status.items():
            status_icon = "✅" if tool_status['status'] == 'ready' else "❌"
            report += f"### {status_icon} {tool_name.replace('_', ' ').title()}\n\n"
            report += f"- **Status:** {tool_status['status']}\n"
            report += f"- **Installed:** {tool_status['installed']}\n"
            report += f"- **Config Valid:** {tool_status['config_valid']}\n"
            
            if tool_status['api_keys']:
                report += f"- **API Keys:**\n"
                for key, available in tool_status['api_keys'].items():
                    key_icon = "✅" if available else "❌"
                    report += f"  - {key_icon} {key}\n"
            
            report += "\n"
        
        # Recommendations
        report += "## 💡 Recommendations\n\n"
        
        if ready_count < total_count:
            report += "### Setup Required\n\n"
            for tool_name, tool_status in status.items():
                if tool_status['status'] != 'ready':
                    report += f"- **{tool_name.replace('_', ' ').title()}:** "
                    if not tool_status['installed']:
                        report += "Install and configure\n"
                    elif not tool_status['config_valid']:
                        report += "Fix configuration\n"
                    elif not all(tool_status['api_keys'].values()):
                        missing_keys = [k for k, v in tool_status['api_keys'].items() if not v]
                        report += f"Add missing API keys: {', '.join(missing_keys)}\n"
        
        # Usage examples
        report += "### Usage Examples\n\n"
        report += "```bash\n"
        report += "# Continue IDE (VS Code/Cursor)\n"
        report += "# Install Continue extension and configure API keys\n\n"
        report += "# Aider CLI\n"
        report += "aider --config .aider.yaml\n"
        report += "hvdc-fix  # Using aliases\n\n"
        report += "# autofix.ci\n"
        report += "# Configure .autofix.yml and GitHub Actions\n\n"
        report += "# Codex Fix\n"
        report += "/codex fix mypy path=src  # In GitHub issue comments\n"
        report += "```\n\n"
        
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_workflow_integration(self) -> str:
        """Create integrated workflow that uses all tools"""
        workflow_content = """name: AI Tools Integration - HVDC Project
on:
  workflow_dispatch:
    inputs:
      tool:
        description: 'AI tool to use'
        required: true
        type: choice
        options:
          - continue
          - aider
          - autofix_ci
          - codex_fix
          - all
      scope:
        description: 'Fix scope'
        required: false
        default: 'all'
        type: choice
        options:
          - all
          - critical
          - security
          - performance

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  ai-tools-integration:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -U pip
          pip install -e ".[dev]"
          pip install aider-chat autofix-ci

      - name: Run AI Tools Integration Check
        run: |
          python scripts/ai_tools_integration.py --check

      - name: Generate Integration Report
        run: |
          python scripts/ai_tools_integration.py --report > integration_report.md

      - name: Upload Integration Report
        uses: actions/upload-artifact@v4
        with:
          name: ai-tools-integration-report
          path: integration_report.md
          retention-days: 30
"""
        return workflow_content
    
    def save_workflow_integration(self):
        """Save integrated workflow to file"""
        workflow_content = self.create_workflow_integration()
        workflow_file = self.project_root / '.github' / 'workflows' / 'ai-tools-integration.yml'
        workflow_file.write_text(workflow_content, encoding='utf-8')
        print(f"✅ Integrated workflow saved to {workflow_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HVDC AI Tools Integration Manager")
    parser.add_argument("--check", action="store_true", help="Check integration status")
    parser.add_argument("--report", action="store_true", help="Generate integration report")
    parser.add_argument("--workflow", action="store_true", help="Create integrated workflow")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).resolve().parents[1]
    integration = AIToolsIntegration(project_root)
    
    if args.check:
        status = integration.get_integration_status()
        print("🤖 HVDC AI Tools Integration Status")
        print("=" * 50)
        for tool_name, tool_status in status.items():
            status_icon = "✅" if tool_status['status'] == 'ready' else "❌"
            print(f"{status_icon} {tool_name.replace('_', ' ').title()}: {tool_status['status']}")
    
    if args.report:
        report = integration.generate_integration_report()
        print(report)
    
    if args.workflow:
        integration.save_workflow_integration()

if __name__ == "__main__":
    main()
