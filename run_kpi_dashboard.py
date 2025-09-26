#!/usr/bin/env python3
"""
MACHO-GPT KPI Dashboard Runner
"""

try:
    from src.macho_gpt import LogiMaster
    
    print("🔧 MACHO-GPT KPI Dashboard 실행 중...")
    
    # Initialize LogiMaster
    lm = LogiMaster()
    
    # Generate KPI Dashboard
    result = lm.generate_kpi_dash()
    
    print("\n📊 KPI Dashboard 결과:")
    print(f"Status: {result.get('status', 'UNKNOWN')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print(f"Mode: {result.get('mode', 'UNKNOWN')}")
    print(f"Triggers: {result.get('triggers', [])}")
    print(f"Next Cmds: {result.get('next_cmds', [])}")
    
    # Display KPI Data
    kpi_data = result.get('data', {})
    if kpi_data:
        print("\n📈 KPI Data:")
        for key, value in kpi_data.items():
            print(f"  {key}: {value}")
    
    print(f"\n🎯 System Confidence: {result.get('confidence', 0):.1%}")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("MACHO-GPT 모듈을 찾을 수 없습니다.")
except Exception as e:
    print(f"❌ Error: {e}")
    print("KPI Dashboard 실행 중 오류가 발생했습니다.") 