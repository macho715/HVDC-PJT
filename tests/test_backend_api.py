"""
HVDC Backend API 테스트
TDD 방식으로 API 기능 검증
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# src 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from app import app

client = TestClient(app)

class TestBackendAPI:
    """백엔드 API 테스트 클래스"""
    
    def test_root_endpoint_should_return_system_info(self):
        """루트 엔드포인트가 시스템 정보를 반환해야 함"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "HVDC Logistics System API v3.4.0"
        assert data["status"] == "operational"
        assert "timestamp" in data
        assert data["mode"] == "PRIME"
    
    def test_health_check_should_return_healthy_status(self):
        """헬스 체크가 정상 상태를 반환해야 함"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "3.4.0"
        assert "timestamp" in data
    
    def test_create_warehouse_should_store_data_correctly(self):
        """창고 데이터 생성이 올바르게 저장되어야 함"""
        warehouse_data = {
            "warehouse_id": "WH001",
            "zone": "A",
            "capacity": 1000.0,
            "current_utilization": 750.0,
            "temperature": 22.5,
            "humidity": 45.0,
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post("/api/v1/warehouses", json=warehouse_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["warehouse_id"] == "WH001"
        assert data["zone"] == "A"
        assert data["capacity"] == 1000.0
    
    def test_get_warehouses_should_return_stored_data(self):
        """창고 목록 조회가 저장된 데이터를 반환해야 함"""
        response = client.get("/api/v1/warehouses")
        assert response.status_code == 200
        
        warehouses = response.json()
        assert len(warehouses) > 0
        assert any(w["warehouse_id"] == "WH001" for w in warehouses)
    
    def test_create_container_with_valid_pressure_should_succeed(self):
        """유효한 압력으로 컨테이너 생성이 성공해야 함"""
        container_data = {
            "container_id": "CONT001",
            "weight": 500.0,
            "volume": 25.0,
            "pressure": 3.5,  # 4t/m² 이하
            "location": "Zone A",
            "status": "active"
        }
        
        response = client.post("/api/v1/containers", json=container_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["container_id"] == "CONT001"
        assert data["pressure"] == 3.5
    
    def test_create_container_with_excessive_pressure_should_fail(self):
        """과도한 압력으로 컨테이너 생성이 실패해야 함"""
        container_data = {
            "container_id": "CONT002",
            "weight": 800.0,
            "volume": 20.0,
            "pressure": 5.0,  # 4t/m² 초과
            "location": "Zone B",
            "status": "active"
        }
        
        response = client.post("/api/v1/containers", json=container_data)
        assert response.status_code == 400
        assert "압력 한계 초과" in response.json()["detail"]
    
    def test_create_invoice_with_high_confidence_should_succeed(self):
        """높은 신뢰도로 송장 생성이 성공해야 함"""
        invoice_data = {
            "invoice_id": "INV001",
            "hs_code": "8471.30.00",
            "description": "Laptop Computer",
            "quantity": 100,
            "unit_price": 1200.0,
            "total_amount": 120000.0,
            "confidence": 0.95  # 0.90 이상
        }
        
        response = client.post("/api/v1/invoices", json=invoice_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["invoice_id"] == "INV001"
        assert data["confidence"] == 0.95
    
    def test_create_invoice_with_low_confidence_should_fail(self):
        """낮은 신뢰도로 송장 생성이 실패해야 함"""
        invoice_data = {
            "invoice_id": "INV002",
            "hs_code": "8471.30.00",
            "description": "Desktop Computer",
            "quantity": 50,
            "unit_price": 800.0,
            "total_amount": 40000.0,
            "confidence": 0.85  # 0.90 미만
        }
        
        response = client.post("/api/v1/invoices", json=invoice_data)
        assert response.status_code == 400
        assert "OCR 신뢰도 부족" in response.json()["detail"]
    
    def test_create_kpi_should_store_metric_data(self):
        """KPI 생성이 메트릭 데이터를 저장해야 함"""
        kpi_data = {
            "metric_name": "warehouse_utilization",
            "value": 75.0,
            "target": 80.0,
            "unit": "%",
            "timestamp": datetime.now().isoformat(),
            "status": "SUCCESS"
        }
        
        response = client.post("/api/v1/kpis", json=kpi_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metric_name"] == "warehouse_utilization"
        assert data["value"] == 75.0
        assert data["status"] == "SUCCESS"
    
    def test_get_system_status_should_return_current_state(self):
        """시스템 상태 조회가 현재 상태를 반환해야 함"""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["mode"] == "PRIME"
        assert data["confidence"] == 0.95
        assert "warehouse_count" in data
        assert "container_count" in data
        assert "invoice_count" in data
        assert "kpi_count" in data
    
    def test_switch_mode_with_valid_mode_should_succeed(self):
        """유효한 모드로 전환이 성공해야 함"""
        response = client.post("/api/v1/system/switch-mode", json={"mode": "LATTICE"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "모드가 LATTICE로 전환되었습니다"
        assert data["mode"] == "LATTICE"
    
    def test_switch_mode_with_invalid_mode_should_fail(self):
        """유효하지 않은 모드로 전환이 실패해야 함"""
        response = client.post("/api/v1/system/switch-mode", json={"mode": "INVALID_MODE"})
        assert response.status_code == 400
        assert "유효하지 않은 모드" in response.json()["detail"]
    
    def test_get_containers_should_return_stored_data(self):
        """컨테이너 목록 조회가 저장된 데이터를 반환해야 함"""
        response = client.get("/api/v1/containers")
        assert response.status_code == 200
        
        containers = response.json()
        assert len(containers) > 0
        assert any(c["container_id"] == "CONT001" for c in containers)
    
    def test_get_invoices_should_return_stored_data(self):
        """송장 목록 조회가 저장된 데이터를 반환해야 함"""
        response = client.get("/api/v1/invoices")
        assert response.status_code == 200
        
        invoices = response.json()
        assert len(invoices) > 0
        assert any(i["invoice_id"] == "INV001" for i in invoices)
    
    def test_get_kpis_should_return_stored_data(self):
        """KPI 목록 조회가 저장된 데이터를 반환해야 함"""
        response = client.get("/api/v1/kpis")
        assert response.status_code == 200
        
        kpis = response.json()
        assert len(kpis) > 0
        assert any(k["metric_name"] == "warehouse_utilization" for k in kpis)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])






