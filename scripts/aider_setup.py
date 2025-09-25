#!/usr/bin/env python3
"""
Aider setup script for HVDC Project
Configures Aider CLI with HVDC-specific settings and integrations
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def check_aider_installation():
    """Check if Aider is installed"""
    try:
        result = subprocess.run(['aider', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Aider installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Aider not found")
            return False
    except FileNotFoundError:
        print("❌ Aider not found")
        return False

def install_aider():
    """Install Aider using pip"""
    print("📦 Installing Aider...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'aider-chat'], check=True)
        print("✅ Aider installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Aider: {e}")
        return False

def setup_hvdc_aider_config():
    """Setup HVDC-specific Aider configuration"""
    print("🔧 Setting up HVDC Aider configuration...")
    
    # Check if .aider.yaml exists
    aider_config = Path('.aider.yaml')
    if aider_config.exists():
        print("✅ .aider.yaml already exists")
    else:
        print("❌ .aider.yaml not found - please ensure it's in the project root")
        return False
    
    # Create aider workspace
    workspace_dir = Path('.aider_workspace')
    workspace_dir.mkdir(exist_ok=True)
    
    # Create HVDC-specific prompts
    prompts_dir = workspace_dir / 'prompts'
    prompts_dir.mkdir(exist_ok=True)
    
    # HVDC-specific prompts
    hvdc_prompts = {
        'logistics_optimization.md': """# Logistics Optimization Prompt

When working on logistics optimization code:
1. Consider Samsung C&T and ADNOC·DSV requirements
2. Maintain pressure limits (≤4t/m² for containers)
3. Ensure FANR/MOIAT compliance
4. Optimize for real-time performance
5. Include comprehensive error handling
""",
        'tdd_development.md': """# TDD Development Prompt

When following TDD principles:
1. Write failing test first (Red)
2. Implement minimal code to pass (Green)
3. Refactor without changing behavior (Refactor)
4. Follow Kent Beck's "Tidy First" approach
5. Separate structural and behavioral changes
""",
        'macho_integration.md': """# MACHO-GPT Integration Prompt

When maintaining MACHO-GPT v3.4-mini integration:
1. Preserve existing API interfaces
2. Maintain command compatibility
3. Follow established patterns
4. Include confidence reporting
5. Ensure mode compatibility
"""
    }
    
    for filename, content in hvdc_prompts.items():
        prompt_file = prompts_dir / filename
        prompt_file.write_text(content, encoding='utf-8')
    
    print("✅ HVDC Aider configuration setup complete")
    return True

def create_aider_aliases():
    """Create convenient aliases for HVDC development"""
    print("🔗 Creating Aider aliases...")
    
    aliases = {
        'hvdc-fix': 'aider --config .aider.yaml',
        'hvdc-test': 'aider --config .aider.yaml --prompt "Add comprehensive tests for the selected code"',
        'hvdc-refactor': 'aider --config .aider.yaml --prompt "Refactor following TDD principles"',
        'hvdc-optimize': 'aider --config .aider.yaml --prompt "Optimize for logistics operations"',
        'hvdc-docs': 'aider --config .aider.yaml --prompt "Add comprehensive documentation"'
    }
    
    # Create shell script for aliases
    script_content = "#!/bin/bash\n# HVDC Aider Aliases\n\n"
    for alias_name, command in aliases.items():
        script_content += f"alias {alias_name}='{command}'\n"
    
    script_file = Path('scripts/aider_aliases.sh')
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    print("✅ Aider aliases created in scripts/aider_aliases.sh")
    print("💡 To use aliases, run: source scripts/aider_aliases.sh")
    
    return True

def test_aider_integration():
    """Test Aider integration with HVDC project"""
    print("🧪 Testing Aider integration...")
    
    try:
        # Test basic aider command
        result = subprocess.run([
            'aider', '--config', '.aider.yaml', '--help'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Aider integration test passed")
            return True
        else:
            print(f"❌ Aider integration test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Aider integration test timed out")
        return False
    except Exception as e:
        print(f"❌ Aider integration test error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 HVDC Aider Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('.aider.yaml').exists():
        print("❌ Please run this script from the HVDC project root directory")
        sys.exit(1)
    
    # Check/install Aider
    if not check_aider_installation():
        if not install_aider():
            print("❌ Failed to install Aider")
            sys.exit(1)
    
    # Setup configuration
    if not setup_hvdc_aider_config():
        print("❌ Failed to setup Aider configuration")
        sys.exit(1)
    
    # Create aliases
    if not create_aider_aliases():
        print("❌ Failed to create Aider aliases")
        sys.exit(1)
    
    # Test integration
    if not test_aider_integration():
        print("⚠️ Aider integration test failed, but setup may still work")
    
    print("\n🎉 HVDC Aider setup complete!")
    print("\n📚 Usage:")
    print("  aider --config .aider.yaml                    # Start Aider chat")
    print("  source scripts/aider_aliases.sh              # Load aliases")
    print("  hvdc-fix                                     # Quick fix command")
    print("  hvdc-test                                    # Add tests")
    print("  hvdc-refactor                                # Refactor code")
    print("  hvdc-optimize                                # Optimize logistics")
    print("  hvdc-docs                                    # Add documentation")
    
    print("\n🔧 Configuration:")
    print("  - Model: GPT-4o")
    print("  - Temperature: 0.1")
    print("  - Max tokens: 8000")
    print("  - Auto commits: enabled")
    print("  - HVDC project context: enabled")

if __name__ == "__main__":
    main()
