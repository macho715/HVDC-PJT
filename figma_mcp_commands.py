"""
Figma MCP Commands for HVDC Warehouse Visualization
HVDC PROJECT | Samsung C&T | ADNOC·DSV Partnership

Command system for seamless Figma MCP integration
"""

import sys
import json
import os
from typing import Dict, Any, Optional
from figma_mcp_integration import FigmaMCPIntegration

class FigmaMCPCommands:
    """
    Command system for Figma MCP integration
    
    Provides easy-to-use commands for HVDC warehouse visualization workflow
    """
    
    def __init__(self):
        self.integration = FigmaMCPIntegration()
        self.commands = {
            'setup_server': self.setup_server,
            'import_svg': self.import_svg,
            'extract_tokens': self.extract_tokens,
            'generate_components': self.generate_components,
            'create_template': self.create_template,
            'test_connection': self.test_connection,
            'help': self.show_help
        }
    
    def setup_server(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Setup Figma MCP server configuration"""
        print("🔧 Setting up Figma MCP server...")
        result = self.integration.setup_mcp_server()
        
        if result['status'] == 'SUCCESS':
            print(f"✅ MCP server configuration created: {result['config_path']}")
            print(f"📋 Next steps:")
            print(f"   1. Get Figma API key from: https://help.figma.com/hc/en-us/articles/8085703771159")
            print(f"   2. Update {result['config_path']} with your API key")
            print(f"   3. Restart your IDE to load the MCP server")
        else:
            print(f"❌ Setup failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def import_svg(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Import SVG wireframe to Figma"""
        svg_path = args[0] if args and len(args) > 0 else "src/warehouse_ui_wireframe.svg"
        figma_file_id = args[1] if args and len(args) > 1 else "YOUR_FIGMA_FILE_ID"
        
        print(f"📁 Importing SVG to Figma: {svg_path}")
        result = self.integration.import_svg_to_figma(svg_path, figma_file_id)
        
        if result['status'] == 'SUCCESS':
            print(f"✅ SVG import prepared successfully")
            print(f"🔗 Figma file ID: {result['figma_file_id']}")
            print(f"📋 Next steps:")
            for step in result.get('next_steps', []):
                print(f"   {step}")
        else:
            print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def extract_tokens(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Extract design tokens from Figma file"""
        figma_file_id = args[0] if args and len(args) > 0 else "YOUR_FIGMA_FILE_ID"
        
        print(f"🎨 Extracting design tokens from Figma file: {figma_file_id}")
        result = self.integration.extract_figma_design_tokens(figma_file_id)
        
        if result['status'] == 'SUCCESS':
            print(f"✅ Design tokens extracted: {result['tokens_path']}")
            print(f"📊 Tokens found:")
            tokens = result['design_tokens']
            print(f"   - Colors: {len(tokens.get('colors', {}))}")
            print(f"   - Typography: {len(tokens.get('typography', {}))}")
            print(f"   - Components: {len(tokens.get('components', {}))}")
        else:
            print(f"❌ Token extraction failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def generate_components(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Generate React components from Figma design"""
        figma_file_id = args[0] if args and len(args) > 0 else "YOUR_FIGMA_FILE_ID"
        output_dir = args[1] if args and len(args) > 1 else "src/components"
        
        print(f"⚛️ Generating React components from Figma file: {figma_file_id}")
        result = self.integration.generate_react_components(figma_file_id, output_dir)
        
        if result['status'] == 'SUCCESS':
            print(f"✅ React components generated: {result['output_dir']}")
            print(f"📦 Components created:")
            for component in result.get('components_generated', []):
                print(f"   - {component}.tsx")
        else:
            print(f"❌ Component generation failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def create_template(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Create HVDC Figma template"""
        print("📋 Creating HVDC Figma template...")
        result = self.integration.create_hvdc_figma_template()
        
        if result['status'] == 'SUCCESS':
            print(f"✅ HVDC template created: {result['template_path']}")
            template = result['template_data']
            print(f"📊 Template details:")
            print(f"   - Name: {template['name']}")
            print(f"   - Frames: {len(template['frames'])}")
            print(f"   - Design tokens: {len(template['design_tokens'])} categories")
        else:
            print(f"❌ Template creation failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def test_connection(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Test Figma MCP connection"""
        print("🔍 Testing Figma MCP connection...")
        
        # Test MCP server availability
        try:
            import subprocess
            result = subprocess.run(
                ['npx', 'figma-developer-mcp', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Figma MCP server is available")
                print("✅ Command line interface working")
                
                # Test API key if available
                if self.integration.figma_api_key:
                    print("✅ Figma API key is configured")
                    return {'status': 'SUCCESS', 'message': 'All tests passed'}
                else:
                    print("⚠️ Figma API key not configured")
                    return {'status': 'PARTIAL', 'message': 'MCP server available but API key missing'}
            else:
                print("❌ Figma MCP server not available")
                return {'status': 'FAIL', 'error': 'MCP server not found'}
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def show_help(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Show help information"""
        print("🎨 Figma MCP Commands for HVDC Warehouse Visualization")
        print("=" * 70)
        print()
        print("Available commands:")
        print()
        print("  setup_server                    Setup Figma MCP server configuration")
        print("  import_svg <svg_path> [file_id] Import SVG wireframe to Figma")
        print("  extract_tokens <file_id>        Extract design tokens from Figma file")
        print("  generate_components <file_id> [output_dir] Generate React components")
        print("  create_template                 Create HVDC Figma template")
        print("  test_connection                 Test Figma MCP connection")
        print("  help                            Show this help message")
        print()
        print("Examples:")
        print("  python figma_mcp_commands.py setup_server")
        print("  python figma_mcp_commands.py import_svg src/warehouse_ui_wireframe.svg")
        print("  python figma_mcp_commands.py extract_tokens YOUR_FIGMA_FILE_ID")
        print("  python figma_mcp_commands.py generate_components YOUR_FIGMA_FILE_ID")
        print()
        print("Environment Variables:")
        print("  FIGMA_API_KEY                  Your Figma Personal Access Token")
        print()
        print("Next Steps:")
        print("  1. Get Figma API key from: https://help.figma.com/hc/en-us/articles/8085703771159")
        print("  2. Set FIGMA_API_KEY environment variable")
        print("  3. Create Figma file and get file ID")
        print("  4. Run setup_server command")
        print("  5. Import SVG and generate components")
        
        return {'status': 'SUCCESS', 'message': 'Help displayed'}
    
    def run_command(self, command: str, args: Optional[list] = None) -> Dict[str, Any]:
        """Run a command"""
        if command in self.commands:
            return self.commands[command](args)
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'help' to see available commands")
            return {'status': 'FAIL', 'error': f'Unknown command: {command}'}


def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("❌ No command specified")
        print("Run 'python figma_mcp_commands.py help' for usage information")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else None
    
    # Initialize command system
    cmd_system = FigmaMCPCommands()
    
    # Run command
    result = cmd_system.run_command(command, args)
    
    # Exit with appropriate code
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main() 