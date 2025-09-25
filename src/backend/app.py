"""
HVDC Project Backend API Server
FastAPI 기반 물류 시스템 백엔드
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="HVDC Logistics System API",
    description="삼성물산 HVDC 프로젝트 물류 시스템 백엔드",
    version="3.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 보안 토큰
security = HTTPBearer()

# 데이터 모델
class WarehouseData(BaseModel):
    """창고 데이터 모델"""
    warehouse_id: str
    zone: str
    capacity: float
    current_utilization: float
    temperature: float
    humidity: float
    timestamp: datetime

class ContainerData(BaseModel):
    """컨테이너 데이터 모델"""
    container_id: str
    weight: float
    volume: float
    pressure: float  # t/m²
    location: str
    status: str

class InvoiceData(BaseModel):
    """송장 데이터 모델"""
    invoice_id: str
    hs_code: str
    description: str
    quantity: int
    unit_price: float
    total_amount: float
    confidence: float  # OCR 신뢰도

class KPIData(BaseModel):
    """KPI 데이터 모델"""
    metric_name: str
    value: float
    target: float
    unit: str
    timestamp: datetime
    status: str  # SUCCESS, WARNING, CRITICAL

class ModeSwitchRequest(BaseModel):
    """모드 전환 요청 모델"""
    mode: str

# 상태 저장소 (실제로는 데이터베이스 사용)
warehouse_store: Dict[str, WarehouseData] = {}
container_store: Dict[str, ContainerData] = {}
invoice_store: Dict[str, InvoiceData] = {}
kpi_store: Dict[str, KPIData] = {}

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "HVDC Logistics System API v3.4.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "mode": "PRIME"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.4.0",
        "uptime": "operational"
    }

@app.get("/api/v1/warehouses", response_model=List[WarehouseData])
async def get_warehouses():
    """창고 목록 조회"""
    return list(warehouse_store.values())

@app.post("/api/v1/warehouses", response_model=WarehouseData)
async def create_warehouse(warehouse: WarehouseData):
    """창고 데이터 생성"""
    warehouse_store[warehouse.warehouse_id] = warehouse
    logger.info(f"창고 생성: {warehouse.warehouse_id}")
    return warehouse

@app.get("/api/v1/containers", response_model=List[ContainerData])
async def get_containers():
    """컨테이너 목록 조회"""
    return list(container_store.values())

@app.post("/api/v1/containers", response_model=ContainerData)
async def create_container(container: ContainerData):
    """컨테이너 데이터 생성"""
    # 압력 한계 검증 (4t/m²)
    if container.pressure > 4.0:
        raise HTTPException(
            status_code=400, 
            detail="압력 한계 초과: 4t/m² 이하여야 합니다"
        )
    
    container_store[container.container_id] = container
    logger.info(f"컨테이너 생성: {container.container_id}")
    return container

@app.get("/api/v1/invoices", response_model=List[InvoiceData])
async def get_invoices():
    """송장 목록 조회"""
    return list(invoice_store.values())

@app.post("/api/v1/invoices", response_model=InvoiceData)
async def create_invoice(invoice: InvoiceData):
    """송장 데이터 생성"""
    # OCR 신뢰도 검증 (≥0.90)
    if invoice.confidence < 0.90:
        raise HTTPException(
            status_code=400,
            detail="OCR 신뢰도 부족: 0.90 이상이어야 합니다"
        )
    
    invoice_store[invoice.invoice_id] = invoice
    logger.info(f"송장 생성: {invoice.invoice_id}")
    return invoice

@app.get("/api/v1/kpis", response_model=List[KPIData])
async def get_kpis():
    """KPI 목록 조회"""
    return list(kpi_store.values())

@app.post("/api/v1/kpis", response_model=KPIData)
async def create_kpi(kpi: KPIData):
    """KPI 데이터 생성"""
    kpi_store[kpi.metric_name] = kpi
    logger.info(f"KPI 생성: {kpi.metric_name}")
    return kpi

@app.get("/api/v1/system/status")
async def get_system_status():
    """시스템 상태 조회"""
    return {
        "mode": "PRIME",
        "confidence": 0.95,
        "warehouse_count": len(warehouse_store),
        "container_count": len(container_store),
        "invoice_count": len(invoice_store),
        "kpi_count": len(kpi_store),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/system/switch-mode")
async def switch_mode(request: ModeSwitchRequest):
    """시스템 모드 전환"""
    valid_modes = ["PRIME", "ORACLE", "ZERO", "LATTICE", "RHYTHM", "COST-GUARD"]
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 모드: {request.mode}. 유효한 모드: {valid_modes}"
        )
    
    logger.info(f"모드 전환: {request.mode}")
    return {"message": f"모드가 {request.mode}로 전환되었습니다", "mode": request.mode}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
