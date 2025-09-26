#!/usr/bin/env python3
"""
Quick MACHO-GPT MCP Integration Test
HVDC Project - Samsung C&T Logistics
"""

from macho_gpt_mcp_integration import MachoMCPIntegrator
import json

def main():
    print("🚀 MACHO-GPT v3.4-mini MCP Integration Test")
    print("=" * 50)
    
    try:
        # Initialize integrator
        integrator = MachoMCPIntegrator()
        
        # Test 1: MCP Connection
        print("\n📡 Testing MCP Connection...")
        connection_result = integrator.verify_mcp_connection()
        print(f"   Status: {connection_result['status']}")
        print(f"   Confidence: {connection_result.get('confidence', 0):.2%}")
        
        # Test 2: Filesystem Integration
        print("\n📁 Testing Filesystem Integration...")
        filesystem_result = integrator.test_filesystem_integration()
        print(f"   Status: {filesystem_result['status']}")
        print(f"   Success Rate: {filesystem_result.get('success_rate', 0):.2%}")
        
        # Test 3: Workflow Configuration
        print("\n⚙️ Testing Workflow Configuration...")
        workflow_result = integrator.configure_logistics_workflows()
        print(f"   Status: {workflow_result['status']}")
        print(f"   Ready Workflows: {workflow_result.get('ready_workflows', 0)}/{workflow_result.get('total_workflows', 0)}")
        
        # Test 4: Chrome Extension Connectivity
        print("\n🌐 Testing Chrome Extension Connectivity...")
        chrome_result = integrator.test_chrome_extension_connectivity()
        print(f"   Status: {chrome_result['status']}")
        print(f"   Confidence: {chrome_result.get('confidence', 0):.2%}")
        
        # Generate Full Report
        print("\n📊 Generating Full Integration Report...")
        full_report = integrator.generate_integration_report()
        
        print(f"\n🎯 INTEGRATION SUMMARY:")
        print(f"   Status: {full_report['integration_status']}")
        print(f"   Overall Confidence: {full_report['overall_confidence']:.2%}")
        print(f"   Active Servers: {full_report['mcp_configuration']['active_servers']}")
        print(f"   Total Tools: {full_report['mcp_configuration']['total_tools']}")
        print(f"   Total Resources: {full_report['mcp_configuration']['total_resources']}")
        
        # Save report
        report_filename = f"macho_integration_test_report_{full_report['timestamp'][:19].replace(':', '-')}.json"
        with open(report_filename, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print(f"\n💾 Report saved: {report_filename}")
        
        # Recommendations
        print(f"\n📋 Recommendations:")
        for rec in full_report['recommendations']:
            print(f"   • {rec}")
        
        # Next Steps
        print(f"\n🎯 Next Steps:")
        for step in full_report['next_steps']:
            print(f"   • {step}")
        
        return full_report
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print("\n✅ MACHO-GPT MCP Integration Test Completed Successfully!")
    else:
        print("\n❌ MACHO-GPT MCP Integration Test Failed!") 