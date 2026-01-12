#!/usr/bin/env python3
"""MACHO-GPT KPI Dashboard Runner."""

from __future__ import annotations

from typing import Any

from hvdc_logi_master_integrated import HVDCLogiMaster


def _format_value(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    if isinstance(value, dict):
        formatted = {key: _format_value(item) for key, item in value.items()}
        return str(formatted)
    if isinstance(value, list):
        return str([_format_value(item) for item in value])
    return str(value)


def run_dashboard() -> None:
    """KPI 대시보드를 실행합니다/Run the KPI dashboard."""
    print("🔧 MACHO-GPT KPI Dashboard 실행 중...")

    logi_master = HVDCLogiMaster()
    result = logi_master.generate_kpi_dash()

    print("\n📊 KPI Dashboard 결과:")
    print(f"Status: {result.get('status', 'UNKNOWN')}")
    print(f"Confidence: {_format_value(result.get('confidence', 0))}")
    print(f"Mode: {result.get('mode', 'UNKNOWN')}")
    print(f"Triggers: {result.get('triggers', [])}")
    print(f"Next Cmds: {result.get('next_cmds', [])}")

    kpi_data = result.get('data', {})
    if kpi_data:
        print("\n📈 KPI Data:")
        for key, value in kpi_data.items():
            print(f"  {key}: {_format_value(value)}")

    confidence = result.get("confidence", 0)
    if isinstance(confidence, (int, float)):
        print(f"\n🎯 System Confidence: {confidence:.2%}")
    else:
        print(f"\n🎯 System Confidence: {confidence}")


if __name__ == "__main__":
    try:
        run_dashboard()
    except Exception as exc:
        print(f"❌ Error: {exc}")
        print("KPI Dashboard 실행 중 오류가 발생했습니다.")
