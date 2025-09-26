#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini Quick Start Script
Cursor IDE Integration Setup and Demo
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("=" * 70)
    print("🚛 MACHO-GPT v3.4-mini Quick Start")
    print("   HVDC Project | Samsung C&T × ADNOC·DSV Partnership")
    print("   Enhanced Cursor IDE Integration")
    print("=" * 70)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = ["yaml", "dataclasses", "enum", "datetime", "typing"]
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "yaml":
                import yaml
            elif package == "dataclasses":
                from dataclasses import dataclass
            elif package == "enum":
                from enum import Enum
            elif package == "datetime":
                from datetime import datetime
            elif package == "typing":
                from typing import Dict, List
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("   ✅ All dependencies satisfied")
    return True

def setup_environment():
    """Setup environment and configuration"""
    print("\n⚙️  Setting up environment...")
    
    # Create necessary directories
    directories = ["logs", "reports", "temp", "exports"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"   📁 Created directory: {dir_name}")
        else:
            print(f"   📁 Directory exists: {dir_name}")
    
    # Create basic configuration if not exists
    config_file = Path("config/runtime_config.json")
    if not config_file.exists():
        config_data = {
            "setup_date": datetime.now().isoformat(),
            "version": "v3.4-mini",
            "environment": "development",
            "features_enabled": {
                "auto_triggers": True,
                "web_search": True,
                "ocr_processing": True,
                "weather_integration": True
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        print(f"   ⚙️  Created runtime config: {config_file}")
    
    print("   ✅ Environment setup complete")

def run_system_demo():
    """Run system demonstration"""
    print("\n🎮 Running MACHO-GPT system demo...")
    
    try:
        # Import and initialize the system
        from logi_meta import LogiMetaSystem
        
        system = LogiMetaSystem()
        
        print("   🚛 System initialized successfully")
        print(f"   📊 Version: {system.version}")
        print(f"   🎯 Project: {system.project}")
        print(f"   🔧 Mode: {system.current_mode.value}")
        
        # Get system status
        status = system.get_system_status()
        print(f"   📈 Confidence: {status['system_info']['confidence']}")
        print(f"   ⏱️  Uptime: {status['system_info']['uptime']}")
        print(f"   🔢 Total Commands: {status['total_commands']}")
        
        # Demo command execution
        print("\n   🔄 Executing demo command...")
        result = system.execute_command("logi_master kpi-dash")
        
        if result["status"] == "SUCCESS":
            print(f"   ✅ Demo command executed successfully")
            print(f"   📊 Confidence: {result['confidence']}%")
            print(f"   🔧 Next commands available: {len(result['next_commands'])}")
        else:
            print(f"   ⚠️  Demo command failed: {result.get('message', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Demo failed: {str(e)}")
        return False

def show_quick_commands():
    """Show quick command examples"""
    print("\n🔧 Quick Commands for Cursor IDE:")
    print("-" * 50)
    
    commands = [
        ("System Status", "python logi_meta.py --status"),
        ("List All Commands", "python logi_meta.py --list all"),
        ("Core Workflow Commands", "python logi_meta.py --list core_workflow"),
        ("KPI Triggers", "python logi_meta.py --kpi"), 
        ("Tool Integration Status", "python logi_meta.py --tools"),
        ("Execute Invoice Audit", "python logi_meta.py \"logi_master invoice-audit\""),
        ("Switch to LATTICE Mode", "python logi_meta.py \"switch_mode LATTICE\""),
        ("Export Metadata (JSON)", "python logi_meta.py --export json"),
        ("Export Metadata (YAML)", "python logi_meta.py --export yaml"),
        ("Health Check", "python logi_meta.py \"health_check\"")
    ]
    
    for description, command in commands:
        print(f"   {description:<25} | {command}")

def show_development_tips():
    """Show development tips for Cursor IDE"""
    print("\n💡 Development Tips for Cursor IDE:")
    print("-" * 50)
    
    tips = [
        "Follow TDD principles: Red → Green → Refactor",
        "Maintain ≥95% confidence in all operations",
        "Use plan.md as your development guide",
        "All functions should be /cmd system compatible",
        "Test with different containment modes",
        "Monitor KPI triggers and auto-responses",
        "Document logistics domain knowledge clearly",
        "Separate structural and behavioral changes",
        "Run full test suite before commits",
        "Export metadata regularly for backup"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"   {i:2d}. {tip}")

def main():
    """Main quick start function"""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed due to missing dependencies")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run demo
    demo_success = run_system_demo()
    
    if demo_success:
        print("\n✅ MACHO-GPT v3.4-mini is ready for development!")
    else:
        print("\n⚠️  System demo had issues, but basic setup is complete")
    
    # Show helpful information
    show_quick_commands()
    show_development_tips()
    
    print("\n" + "=" * 70)
    print("🎯 Next Steps:")
    print("   1. Review plan.md for TDD development guidelines")
    print("   2. Run: python logi_meta.py --status")
    print("   3. Start developing with TDD cycle: Red → Green → Refactor")
    print("   4. Use recommended commands for testing and validation")
    print("=" * 70)

if __name__ == "__main__":
    main()