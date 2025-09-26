#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini HTTP Server
HVDC Project - Samsung C&T | ADNOC·DSV Partnership

Simple HTTP server for HTML dashboard integration
Provides REST API endpoints for MACHO-GPT commands
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from macho_gpt_integration import MachoGPTIntegration

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize MACHO-GPT integration
macho_integration = MachoGPTIntegration()

@app.route('/')
def index():
    """Serve the main index page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve static HTML files"""
    return send_from_directory('.', filename)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        health = macho_integration.system_health_check()
        return jsonify({
            'status': 'healthy',
            'macho_gpt': health['health_check'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/command', methods=['POST'])
def execute_command():
    """Execute MACHO-GPT command"""
    try:
        data = request.get_json()
        command = data.get('command')
        args = data.get('args', {})
        
        if not command:
            return jsonify({
                'status': 'ERROR',
                'message': 'No command specified'
            }), 400
        
        result = macho_integration.execute_command(command, args)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/dashboard-data')
def get_dashboard_data():
    """Get current dashboard data"""
    try:
        dashboard_data = macho_integration.get_dashboard_data()
        return jsonify({
            'status': 'SUCCESS',
            'data': {
                'total_inventory': dashboard_data.total_inventory,
                'warehouses': dashboard_data.warehouses,
                'flow_code_0': dashboard_data.flow_code_0,
                'flow_code_1': dashboard_data.flow_code_1,
                'flow_code_2': dashboard_data.flow_code_2,
                'flow_code_3': dashboard_data.flow_code_3,
                'total_value': dashboard_data.total_value,
                'handling_rate': dashboard_data.handling_rate,
                'warehouse_status': dashboard_data.warehouse_status,
                'system_status': dashboard_data.system_status,
                'last_updated': dashboard_data.last_updated,
                'current_mode': macho_integration.current_mode,
                'confidence': macho_integration.system_confidence
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/kpi-report')
def get_kpi_report():
    """Get KPI report"""
    try:
        result = macho_integration.generate_kpi_report()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/warehouse-status')
def get_warehouse_status():
    """Get warehouse status"""
    try:
        dashboard_data = macho_integration.get_dashboard_data()
        return jsonify({
            'status': 'SUCCESS',
            'warehouse_status': dashboard_data.warehouse_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/switch-mode', methods=['POST'])
def switch_mode():
    """Switch MACHO-GPT mode"""
    try:
        data = request.get_json()
        new_mode = data.get('mode', 'PRIME')
        
        result = macho_integration.switch_mode(new_mode)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/system-info')
def get_system_info():
    """Get system information"""
    try:
        health = macho_integration.system_health_check()
        return jsonify({
            'status': 'SUCCESS',
            'system_info': {
                'current_mode': macho_integration.current_mode,
                'confidence': macho_integration.system_confidence,
                'active_warehouses': macho_integration.active_warehouses,
                'total_items': macho_integration.total_items,
                'last_update': macho_integration.last_update.isoformat(),
                'health_status': health['health_check']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/commands')
def get_available_commands():
    """Get list of available commands"""
    commands = [
        {
            'name': 'switch_mode',
            'description': 'Switch MACHO-GPT containment mode',
            'parameters': ['mode'],
            'valid_modes': ['PRIME', 'ORACLE', 'ZERO', 'LATTICE', 'RHYTHM', 'COST-GUARD']
        },
        {
            'name': 'get_dashboard_data',
            'description': 'Get current dashboard data',
            'parameters': []
        },
        {
            'name': 'update_warehouse_status',
            'description': 'Update warehouse status',
            'parameters': ['warehouse', 'updates']
        },
        {
            'name': 'generate_kpi_report',
            'description': 'Generate KPI report',
            'parameters': []
        },
        {
            'name': 'system_health_check',
            'description': 'Perform system health check',
            'parameters': []
        }
    ]
    
    return jsonify({
        'status': 'SUCCESS',
        'commands': commands,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'ERROR',
        'message': 'Endpoint not found',
        'available_endpoints': [
            '/health',
            '/command',
            '/dashboard-data',
            '/kpi-report',
            '/warehouse-status',
            '/switch-mode',
            '/system-info',
            '/api/commands'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'ERROR',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

def main():
    """Main function to run the server"""
    print("🚀 MACHO-GPT v3.4-mini HTTP Server")
    print("=" * 50)
    print("HVDC Project - Samsung C&T | ADNOC·DSV Partnership")
    print("-" * 50)
    
    # Initialize MACHO-GPT integration
    print("🔧 Initializing MACHO-GPT integration...")
    health = macho_integration.system_health_check()
    print(f"✅ System Status: {health['health_check']['system_status']}")
    print(f"🎯 Current Mode: {health['health_check']['current_mode']}")
    print(f"📊 Confidence: {health['health_check']['confidence']:.1%}")
    
    print(f"\n🌐 Starting HTTP server...")
    print(f"   Server will be available at: http://localhost:8000")
    print(f"   API endpoints:")
    print(f"   - GET  /health - System health check")
    print(f"   - POST /command - Execute MACHO-GPT command")
    print(f"   - GET  /dashboard-data - Get dashboard data")
    print(f"   - GET  /kpi-report - Get KPI report")
    print(f"   - GET  /warehouse-status - Get warehouse status")
    print(f"   - POST /switch-mode - Switch MACHO-GPT mode")
    print(f"   - GET  /system-info - Get system information")
    print(f"   - GET  /api/commands - Get available commands")
    
    print(f"\n📱 HTML Dashboard:")
    print(f"   - Main Dashboard: http://localhost:8000/index.html")
    print(f"   - Interactive API: http://localhost:8000/hvdc_dashboard_api.html")
    print(f"   - Static Dashboard: http://localhost:8000/hvdc_dashboard_main.html")
    print(f"   - Warehouse Monitor: http://localhost:8000/hvdc_warehouse_monitor.html")
    print(f"   - Inventory Tracking: http://localhost:8000/hvdc_inventory_tracking.html")
    
    print(f"\n🔧 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == '__main__':
    main() 