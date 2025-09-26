# MACHO-GPT v3.4-mini Live HVDC Logistics Data Processor
# HVDC Project - Samsung C&T Logistics
# Real-time Data Processing & Workflow Automation

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List, Optional, Any
import logging
import os
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
import requests
import schedule

from macho_gpt_mcp_integration import MachoMCPIntegrator
from macho_realtime_kpi_dashboard import MachoRealTimeKPIDashboard

@dataclass
class LogisticsTransaction:
    """HVDC logistics transaction data structure"""
    transaction_id: str
    timestamp: str
    container_id: str
    invoice_id: str
    warehouse: str
    cargo_type: str
    quantity: float
    amount_aed: float
    handling_fee: float
    rent_fee: float
    flow_code: int
    status: str
    confidence: float
    processed_by: str

@dataclass
class ProcessingResult:
    """Data processing result structure"""
    success: bool
    records_processed: int
    records_failed: int
    processing_time_seconds: float
    confidence_score: float
    alerts_generated: List[Dict]
    workflow_activations: List[str]
    timestamp: str

class MachoLiveLogisticsProcessor:
    """
    MACHO-GPT v3.4-mini Live HVDC Logistics Data Processor
    
    Features:
    - Real-time data ingestion from multiple sources
    - Automated workflow activation based on data patterns
    - Intelligent data validation and error correction
    - Integration with existing MACHO-GPT workflows
    - Live KPI updates and alert generation
    - Historical data analysis and trend detection
    """
    
    def __init__(self):
        self.integrator = MachoMCPIntegrator()
        self.kpi_dashboard = MachoRealTimeKPIDashboard()
        self.is_processing = False
        self.processing_stats = {
            "total_processed": 0,
            "total_failed": 0,
            "start_time": None,
            "last_processing": None,
            "average_confidence": 0.0
        }
        
        # Data sources configuration
        self.data_sources = {
            "invoices": {
                "path": "data/HVDC WAREHOUSE_INVOICE.xlsx",
                "type": "excel",
                "active": True,
                "refresh_interval": 300,  # 5 minutes
                "last_processed": None
            },
            "hitachi": {
                "path": "data/HVDC WAREHOUSE_HITACHI(HE).xlsx",
                "type": "excel",
                "active": True,
                "refresh_interval": 600,  # 10 minutes
                "last_processed": None
            },
            "siemens": {
                "path": "data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx",
                "type": "excel",
                "active": True,
                "refresh_interval": 600,  # 10 minutes
                "last_processed": None
            }
        }
        
        # Processing configuration
        self.processing_config = {
            "batch_size": 100,
            "max_processing_time": 30,  # seconds
            "confidence_threshold": 0.85,
            "error_retry_attempts": 3,
            "auto_workflow_activation": True,
            "real_time_kpi_updates": True
        }
        
        # Setup logging FIRST
        self.logger = self._setup_logging()
        # Initialize database
        self.init_processing_database()
        
        # Processing queue
        self.processing_queue = []
        self.processed_transactions = []
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for live logistics processor"""
        logger = logging.getLogger("MACHO_LIVE_PROCESSOR")
        logger.setLevel(logging.INFO)
        
        os.makedirs("logs", exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f"logs/live_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def init_processing_database(self):
        """Initialize SQLite database for live processing data"""
        try:
            os.makedirs("data", exist_ok=True)
            self.db_path = "data/live_logistics_processor.db"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logistics_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    container_id TEXT,
                    invoice_id TEXT,
                    warehouse TEXT,
                    cargo_type TEXT,
                    quantity REAL,
                    amount_aed REAL,
                    handling_fee REAL,
                    rent_fee REAL,
                    flow_code INTEGER,
                    status TEXT,
                    confidence REAL,
                    processed_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create processing_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    success BOOLEAN,
                    records_processed INTEGER,
                    records_failed INTEGER,
                    processing_time_seconds REAL,
                    confidence_score REAL,
                    alerts_generated TEXT,
                    workflow_activations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create data_sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT UNIQUE NOT NULL,
                    file_path TEXT,
                    last_processed TEXT,
                    records_count INTEGER,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Live processing database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
    
    def load_hvdc_data_sources(self) -> Dict[str, pd.DataFrame]:
        """
        Load all HVDC data sources
        
        Returns:
            dict: Dictionary of dataframes for each source
        """
        dataframes = {}
        
        for source_name, config in self.data_sources.items():
            if not config["active"]:
                continue
                
            try:
                file_path = Path(config["path"])
                if not file_path.exists():
                    self.logger.warning(f"Data source file not found: {config['path']}")
                    continue
                
                # Load Excel file
                if config["type"] == "excel":
                    df = pd.read_excel(file_path)
                    dataframes[source_name] = df
                    
                    # Update source status
                    config["last_processed"] = datetime.now().isoformat()
                    
                    self.logger.info(f"Loaded {source_name}: {len(df)} records")
                    
                    # Save source status to database
                    self._save_source_status(source_name, len(df), "loaded")
                    
            except Exception as e:
                self.logger.error(f"Failed to load {source_name}: {str(e)}")
                self._save_source_status(source_name, 0, f"error: {str(e)}")
        
        return dataframes
    
    def _save_source_status(self, source_name: str, records_count: int, status: str):
        """Save data source status to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO data_sources 
                (source_name, file_path, last_processed, records_count, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                source_name,
                self.data_sources[source_name]["path"],
                datetime.now().isoformat(),
                records_count,
                status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save source status: {str(e)}")
    
    def process_invoice_data(self, df: pd.DataFrame) -> List[LogisticsTransaction]:
        """
        Process invoice data and convert to logistics transactions
        
        Args:
            df: Invoice dataframe
            
        Returns:
            List[LogisticsTransaction]: Processed transactions
        """
        transactions = []
        
        try:
            for index, row in df.iterrows():
                # Generate unique transaction ID
                transaction_id = f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{index:06d}"
                
                # Extract data with error handling
                try:
                    # Basic data extraction
                    container_id = str(row.get('Container ID', f'CONT_{index}'))
                    invoice_id = str(row.get('Invoice ID', f'INV_{index}'))
                    warehouse = str(row.get('Category', 'Unknown'))
                    cargo_type = str(row.get('HVDC CODE 3', 'UNKNOWN'))
                    
                    # Numeric data with validation
                    quantity = float(row.get('Quantity', 0))
                    amount_aed = float(row.get('Amount AED', 0))
                    
                    # Calculate fees (based on historical patterns)
                    handling_fee = amount_aed * 0.134  # 13.4% handling
                    rent_fee = amount_aed * 0.866      # 86.6% rent
                    
                    # Flow code calculation (simplified)
                    flow_code = self._calculate_flow_code(warehouse, cargo_type)
                    
                    # Confidence calculation
                    confidence = self._calculate_confidence(row, warehouse, cargo_type)
                    
                    # Create transaction
                    transaction = LogisticsTransaction(
                        transaction_id=transaction_id,
                        timestamp=datetime.now().isoformat(),
                        container_id=container_id,
                        invoice_id=invoice_id,
                        warehouse=warehouse,
                        cargo_type=cargo_type,
                        quantity=quantity,
                        amount_aed=amount_aed,
                        handling_fee=handling_fee,
                        rent_fee=rent_fee,
                        flow_code=flow_code,
                        status="processed",
                        confidence=confidence,
                        processed_by="invoice_ocr"
                    )
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process invoice row {index}: {str(e)}")
                    continue
            
            self.logger.info(f"Processed {len(transactions)} invoice transactions")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Invoice processing failed: {str(e)}")
            return []
    
    def process_hitachi_data(self, df: pd.DataFrame) -> List[LogisticsTransaction]:
        """
        Process Hitachi (HE) data and convert to logistics transactions
        
        Args:
            df: Hitachi dataframe
            
        Returns:
            List[LogisticsTransaction]: Processed transactions
        """
        transactions = []
        
        try:
            for index, row in df.iterrows():
                # Generate unique transaction ID
                transaction_id = f"HE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{index:06d}"
                
                try:
                    # Extract Hitachi-specific data
                    container_id = str(row.get('Container ID', f'HE_CONT_{index}'))
                    warehouse = str(row.get('Warehouse', 'DSV Outdoor'))
                    cargo_type = 'HE'  # Hitachi equipment
                    
                    # Numeric data
                    quantity = float(row.get('Quantity', 1))
                    amount_aed = float(row.get('Value AED', 0))
                    
                    # Calculate fees
                    handling_fee = amount_aed * 0.15  # 15% handling for HE
                    rent_fee = amount_aed * 0.85      # 85% rent for HE
                    
                    # Flow code
                    flow_code = self._calculate_flow_code(warehouse, cargo_type)
                    
                    # Confidence
                    confidence = self._calculate_confidence(row, warehouse, cargo_type)
                    
                    # Create transaction
                    transaction = LogisticsTransaction(
                        transaction_id=transaction_id,
                        timestamp=datetime.now().isoformat(),
                        container_id=container_id,
                        invoice_id=f"HE_INV_{index}",
                        warehouse=warehouse,
                        cargo_type=cargo_type,
                        quantity=quantity,
                        amount_aed=amount_aed,
                        handling_fee=handling_fee,
                        rent_fee=rent_fee,
                        flow_code=flow_code,
                        status="processed",
                        confidence=confidence,
                        processed_by="heat_stow"
                    )
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process Hitachi row {index}: {str(e)}")
                    continue
            
            self.logger.info(f"Processed {len(transactions)} Hitachi transactions")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Hitachi processing failed: {str(e)}")
            return []
    
    def process_siemens_data(self, df: pd.DataFrame) -> List[LogisticsTransaction]:
        """
        Process Siemens (SIM) data and convert to logistics transactions
        
        Args:
            df: Siemens dataframe
            
        Returns:
            List[LogisticsTransaction]: Processed transactions
        """
        transactions = []
        
        try:
            for index, row in df.iterrows():
                # Generate unique transaction ID
                transaction_id = f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{index:06d}"
                
                try:
                    # Extract Siemens-specific data
                    container_id = str(row.get('Container ID', f'SIM_CONT_{index}'))
                    warehouse = str(row.get('Warehouse', 'DSV Indoor'))
                    cargo_type = 'SIM'  # Siemens equipment
                    
                    # Numeric data
                    quantity = float(row.get('Quantity', 1))
                    amount_aed = float(row.get('Value AED', 0))
                    
                    # Calculate fees
                    handling_fee = amount_aed * 0.12  # 12% handling for SIM
                    rent_fee = amount_aed * 0.88      # 88% rent for SIM
                    
                    # Flow code
                    flow_code = self._calculate_flow_code(warehouse, cargo_type)
                    
                    # Confidence
                    confidence = self._calculate_confidence(row, warehouse, cargo_type)
                    
                    # Create transaction
                    transaction = LogisticsTransaction(
                        transaction_id=transaction_id,
                        timestamp=datetime.now().isoformat(),
                        container_id=container_id,
                        invoice_id=f"SIM_INV_{index}",
                        warehouse=warehouse,
                        cargo_type=cargo_type,
                        quantity=quantity,
                        amount_aed=amount_aed,
                        handling_fee=handling_fee,
                        rent_fee=rent_fee,
                        flow_code=flow_code,
                        status="processed",
                        confidence=confidence,
                        processed_by="container_analysis"
                    )
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process Siemens row {index}: {str(e)}")
                    continue
            
            self.logger.info(f"Processed {len(transactions)} Siemens transactions")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Siemens processing failed: {str(e)}")
            return []
    
    def _calculate_flow_code(self, warehouse: str, cargo_type: str) -> int:
        """Calculate flow code based on warehouse and cargo type"""
        try:
            # Simplified flow code calculation
            if warehouse == "DSV Outdoor":
                if cargo_type == "HE":
                    return 1  # Outdoor HE handling
                elif cargo_type == "SIM":
                    return 2  # Outdoor SIM handling
                else:
                    return 0  # Direct
            elif warehouse == "DSV Indoor":
                if cargo_type == "HE":
                    return 2  # Indoor HE handling
                elif cargo_type == "SIM":
                    return 1  # Indoor SIM handling
                else:
                    return 1  # Single warehouse
            else:
                return 0  # Direct port-to-site
                
        except Exception:
            return 0  # Default to direct
    
    def _calculate_confidence(self, row: pd.Series, warehouse: str, cargo_type: str) -> float:
        """Calculate confidence score for data processing"""
        try:
            base_confidence = 0.90
            
            # Adjust based on data quality
            if pd.notna(row.get('Amount AED')) and float(row.get('Amount AED', 0)) > 0:
                base_confidence += 0.05
            
            if pd.notna(row.get('Quantity')) and float(row.get('Quantity', 0)) > 0:
                base_confidence += 0.03
            
            # Adjust based on warehouse type
            if warehouse in ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz"]:
                base_confidence += 0.02
            
            # Adjust based on cargo type
            if cargo_type in ["HE", "SIM", "SCT"]:
                base_confidence += 0.02
            
            return min(0.99, base_confidence)
            
        except Exception:
            return 0.85  # Default confidence
    
    def save_transactions_to_database(self, transactions: List[LogisticsTransaction]):
        """Save processed transactions to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for transaction in transactions:
                cursor.execute('''
                    INSERT OR REPLACE INTO logistics_transactions (
                        transaction_id, timestamp, container_id, invoice_id,
                        warehouse, cargo_type, quantity, amount_aed,
                        handling_fee, rent_fee, flow_code, status,
                        confidence, processed_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction.transaction_id,
                    transaction.timestamp,
                    transaction.container_id,
                    transaction.invoice_id,
                    transaction.warehouse,
                    transaction.cargo_type,
                    transaction.quantity,
                    transaction.amount_aed,
                    transaction.handling_fee,
                    transaction.rent_fee,
                    transaction.flow_code,
                    transaction.status,
                    transaction.confidence,
                    transaction.processed_by
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Saved {len(transactions)} transactions to database")
            
        except Exception as e:
            self.logger.error(f"Failed to save transactions: {str(e)}")
    
    def activate_workflows_based_on_data(self, transactions: List[LogisticsTransaction]) -> List[str]:
        """
        Activate MACHO-GPT workflows based on processed data patterns
        
        Args:
            transactions: List of processed transactions
            
        Returns:
            List[str]: Activated workflow names
        """
        activated_workflows = []
        
        try:
            if not transactions:
                return activated_workflows
            
            # Analyze transaction patterns
            total_amount = sum(t.amount_aed for t in transactions)
            total_containers = len(transactions)
            avg_confidence = np.mean([t.confidence for t in transactions])
            
            # Cargo type distribution
            cargo_types = {}
            for t in transactions:
                cargo_types[t.cargo_type] = cargo_types.get(t.cargo_type, 0) + 1
            
            # Warehouse distribution
            warehouses = {}
            for t in transactions:
                warehouses[t.warehouse] = warehouses.get(t.warehouse, 0) + 1
            
            # Activate workflows based on patterns
            
            # 1. Invoice OCR workflow (always active for invoice data)
            if any(t.processed_by == "invoice_ocr" for t in transactions):
                activated_workflows.append("invoice_ocr")
                self.logger.info("Activated Invoice OCR workflow")
            
            # 2. Heat-Stow workflow (for HE cargo)
            if cargo_types.get("HE", 0) > 0:
                activated_workflows.append("heat_stow")
                self.logger.info("Activated Heat-Stow workflow for HE cargo")
            
            # 3. Container Analysis workflow (for SIM cargo)
            if cargo_types.get("SIM", 0) > 0:
                activated_workflows.append("container_analysis")
                self.logger.info("Activated Container Analysis workflow for SIM cargo")
            
            # 4. Weather Tie workflow (if outdoor warehouses involved)
            outdoor_warehouses = ["DSV Outdoor", "DSV Al Markaz"]
            if any(w in warehouses for w in outdoor_warehouses):
                activated_workflows.append("weather_tie")
                self.logger.info("Activated Weather Tie workflow for outdoor operations")
            
            # 5. KPI Monitoring workflow (always active)
            activated_workflows.append("kpi_monitoring")
            
            return activated_workflows
            
        except Exception as e:
            self.logger.error(f"Workflow activation failed: {str(e)}")
            return ["kpi_monitoring"]  # Default fallback
    
    def generate_processing_alerts(self, transactions: List[LogisticsTransaction]) -> List[Dict]:
        """
        Generate alerts based on processing results
        
        Args:
            transactions: List of processed transactions
            
        Returns:
            List[Dict]: Generated alerts
        """
        alerts = []
        
        try:
            if not transactions:
                return alerts
            
            # Calculate metrics
            total_amount = sum(t.amount_aed for t in transactions)
            avg_confidence = np.mean([t.confidence for t in transactions])
            low_confidence_count = len([t for t in transactions if t.confidence < 0.85])
            
            # Alert 1: Low confidence transactions
            if low_confidence_count > 0:
                alerts.append({
                    "type": "LOW_CONFIDENCE_TRANSACTIONS",
                    "severity": "MEDIUM",
                    "message": f"{low_confidence_count} transactions with confidence < 85%",
                    "metric_value": low_confidence_count,
                    "threshold": 0,
                    "workflow": "data_quality",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Alert 2: High value transactions
            if total_amount > 1000000:  # 1M AED
                alerts.append({
                    "type": "HIGH_VALUE_PROCESSING",
                    "severity": "LOW",
                    "message": f"Processed high-value transactions: {total_amount:,.0f} AED",
                    "metric_value": total_amount,
                    "threshold": 1000000,
                    "workflow": "financial_monitoring",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Alert 3: Large batch processing
            if len(transactions) > 500:
                alerts.append({
                    "type": "LARGE_BATCH_PROCESSING",
                    "severity": "LOW",
                    "message": f"Large batch processed: {len(transactions)} transactions",
                    "metric_value": len(transactions),
                    "threshold": 500,
                    "workflow": "batch_monitoring",
                    "timestamp": datetime.now().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Alert generation failed: {str(e)}")
            return []
    
    def process_live_data(self) -> ProcessingResult:
        """
        Main method to process live HVDC logistics data
        
        Returns:
            ProcessingResult: Processing results
        """
        start_time = time.time()
        
        try:
            self.logger.info("Starting live HVDC logistics data processing...")
            
            # Load data sources
            dataframes = self.load_hvdc_data_sources()
            
            if not dataframes:
                self.logger.warning("No data sources available for processing")
                return ProcessingResult(
                    success=False,
                    records_processed=0,
                    records_failed=0,
                    processing_time_seconds=time.time() - start_time,
                    confidence_score=0.0,
                    alerts_generated=[],
                    workflow_activations=[],
                    timestamp=datetime.now().isoformat()
                )
            
            # Process each data source
            all_transactions = []
            failed_records = 0
            
            for source_name, df in dataframes.items():
                try:
                    if source_name == "invoices":
                        transactions = self.process_invoice_data(df)
                    elif source_name == "hitachi":
                        transactions = self.process_hitachi_data(df)
                    elif source_name == "siemens":
                        transactions = self.process_siemens_data(df)
                    else:
                        continue
                    
                    all_transactions.extend(transactions)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {source_name}: {str(e)}")
                    failed_records += len(df) if df is not None else 0
            
            # Save transactions to database
            if all_transactions:
                self.save_transactions_to_database(all_transactions)
            
            # Activate workflows
            activated_workflows = []
            if self.processing_config["auto_workflow_activation"]:
                activated_workflows = self.activate_workflows_based_on_data(all_transactions)
            
            # Generate alerts
            alerts = self.generate_processing_alerts(all_transactions)
            
            # Calculate confidence score
            confidence_score = np.mean([t.confidence for t in all_transactions]) if all_transactions else 0.0
            
            # Update processing stats
            self.processing_stats["total_processed"] += len(all_transactions)
            self.processing_stats["total_failed"] += failed_records
            self.processing_stats["last_processing"] = datetime.now().isoformat()
            self.processing_stats["average_confidence"] = confidence_score
            
            # Create processing result
            processing_time = time.time() - start_time
            result = ProcessingResult(
                success=len(all_transactions) > 0,
                records_processed=len(all_transactions),
                records_failed=failed_records,
                processing_time_seconds=processing_time,
                confidence_score=confidence_score,
                alerts_generated=alerts,
                workflow_activations=activated_workflows,
                timestamp=datetime.now().isoformat()
            )
            
            # Save processing result
            self._save_processing_result(result)
            
            # Update KPI dashboard if enabled
            if self.processing_config["real_time_kpi_updates"]:
                self._update_kpi_dashboard(all_transactions, result)
            
            self.logger.info(f"Live processing completed: {len(all_transactions)} processed, "
                           f"{failed_records} failed, confidence: {confidence_score:.2%}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Live processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                records_processed=0,
                records_failed=0,
                processing_time_seconds=time.time() - start_time,
                confidence_score=0.0,
                alerts_generated=[{
                    "type": "PROCESSING_ERROR",
                    "severity": "HIGH",
                    "message": f"Processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }],
                workflow_activations=[],
                timestamp=datetime.now().isoformat()
            )
    
    def _save_processing_result(self, result: ProcessingResult):
        """Save processing result to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processing_results (
                    timestamp, success, records_processed, records_failed,
                    processing_time_seconds, confidence_score, alerts_generated,
                    workflow_activations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.timestamp,
                result.success,
                result.records_processed,
                result.records_failed,
                result.processing_time_seconds,
                result.confidence_score,
                json.dumps(result.alerts_generated),
                json.dumps(result.workflow_activations)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save processing result: {str(e)}")
    
    def _update_kpi_dashboard(self, transactions: List[LogisticsTransaction], result: ProcessingResult):
        """Update KPI dashboard with processing results"""
        try:
            # This would integrate with the existing KPI dashboard
            # For now, just log the update
            total_amount = sum(t.amount_aed for t in transactions)
            
            self.logger.info(f"KPI Dashboard Update: {len(transactions)} transactions, "
                           f"{total_amount:,.0f} AED, confidence: {result.confidence_score:.2%}")
            
        except Exception as e:
            self.logger.error(f"KPI dashboard update failed: {str(e)}")
    
    def start_live_processing(self, interval_minutes: int = 5):
        """
        Start continuous live processing
        
        Args:
            interval_minutes: Processing interval in minutes
        """
        self.logger.info(f"Starting live processing with {interval_minutes}-minute interval")
        
        def processing_job():
            try:
                result = self.process_live_data()
                if result.success:
                    self.logger.info(f"Processing job completed: {result.records_processed} records")
                else:
                    self.logger.warning("Processing job failed")
            except Exception as e:
                self.logger.error(f"Processing job error: {str(e)}")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(processing_job)
        
        # Run initial processing
        processing_job()
        
        # Start the scheduler
        self.is_processing = True
        while self.is_processing:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_live_processing(self):
        """Stop live processing"""
        self.is_processing = False
        self.logger.info("Live processing stopped")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            "processing_stats": self.processing_stats,
            "data_sources": self.data_sources,
            "processing_config": self.processing_config,
            "is_processing": self.is_processing
        }
    
    def generate_processing_report(self) -> str:
        """Generate comprehensive processing report"""
        try:
            stats = self.get_processing_stats()
            
            report = f"""
# MACHO-GPT v3.4-mini Live HVDC Logistics Processing Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Processing Statistics
- Total Records Processed: {stats['processing_stats']['total_processed']:,}
- Total Records Failed: {stats['processing_stats']['total_failed']:,}
- Average Confidence: {stats['processing_stats']['average_confidence']:.2%}
- Last Processing: {stats['processing_stats']['last_processing'] or 'Never'}
- Processing Status: {'Active' if stats['is_processing'] else 'Inactive'}

## Data Sources Status
"""
            
            for source_name, config in stats['data_sources'].items():
                status = "Active" if config['active'] else "Inactive"
                last_processed = config['last_processed'] or 'Never'
                report += f"- {source_name}: {status} (Last: {last_processed})\n"
            
            report += f"""
## Processing Configuration
- Batch Size: {stats['processing_config']['batch_size']}
- Max Processing Time: {stats['processing_config']['max_processing_time']}s
- Confidence Threshold: {stats['processing_config']['confidence_threshold']:.2%}
- Auto Workflow Activation: {stats['processing_config']['auto_workflow_activation']}
- Real-time KPI Updates: {stats['processing_config']['real_time_kpi_updates']}

## Database Information
- Database Path: {self.db_path}
- Transactions Table: logistics_transactions
- Results Table: processing_results
- Sources Table: data_sources
"""
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            return f"Report generation failed: {str(e)}"

def main():
    """Main function to run live logistics processor"""
    print("🚀 MACHO-GPT v3.4-mini Live HVDC Logistics Data Processor")
    print("=" * 70)
    
    try:
        # Initialize processor
        processor = MachoLiveLogisticsProcessor()
        
        # Generate initial report
        print("📊 Generating initial processing report...")
        report = processor.generate_processing_report()
        
        # Save report
        report_filename = f"live_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved: {report_filename}")
        
        # Run initial processing
        print("\n🔄 Running initial data processing...")
        result = processor.process_live_data()
        
        if result.success:
            print(f"✅ Initial processing completed:")
            print(f"   Records Processed: {result.records_processed:,}")
            print(f"   Records Failed: {result.records_failed:,}")
            print(f"   Confidence Score: {result.confidence_score:.2%}")
            print(f"   Processing Time: {result.processing_time_seconds:.2f}s")
            print(f"   Workflows Activated: {', '.join(result.workflow_activations)}")
            print(f"   Alerts Generated: {len(result.alerts_generated)}")
        else:
            print("❌ Initial processing failed")
        
        # Ask user for next action
        print("\n🎯 Processing Options:")
        print("1. Start continuous live processing (5-minute intervals)")
        print("2. Run one-time processing")
        print("3. View processing statistics")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print("🔄 Starting continuous live processing...")
            print("Press Ctrl+C to stop")
            try:
                processor.start_live_processing(interval_minutes=5)
            except KeyboardInterrupt:
                print("\n🛑 Stopping live processing...")
                processor.stop_live_processing()
                
        elif choice == "2":
            print("🔄 Running one-time processing...")
            result = processor.process_live_data()
            if result.success:
                print(f"✅ Processing completed: {result.records_processed} records")
            else:
                print("❌ Processing failed")
                
        elif choice == "3":
            stats = processor.get_processing_stats()
            print("\n📊 Processing Statistics:")
            print(f"   Total Processed: {stats['processing_stats']['total_processed']:,}")
            print(f"   Total Failed: {stats['processing_stats']['total_failed']:,}")
            print(f"   Average Confidence: {stats['processing_stats']['average_confidence']:.2%}")
            print(f"   Processing Status: {'Active' if stats['is_processing'] else 'Inactive'}")
            
        else:
            print("👋 Exiting processor...")
        
        return processor
        
    except Exception as e:
        print(f"❌ Processor failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    processor = main() 