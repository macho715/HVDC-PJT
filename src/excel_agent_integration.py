#!/usr/bin/env python3
"""
Excel Agent Integration Module for MACHO-GPT System
==================================================
HVDC 프로젝트에 Excel Agent를 완전 통합하여 자연어 Excel 데이터 분석 기능 제공
"""

import pandas as pd
import numpy as np
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import sys
import os

# Excel Agent 관련 import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'python_excel_agent-main'))
try:
    from app import ExcelAgent
except ImportError:
    # Excel Agent가 없는 경우를 위한 대체 클래스
    class ExcelAgent:
        def __init__(self):
            self.logger = logging.getLogger(__name__)
        
        async def process_query(self, df: pd.DataFrame, query: str) -> Dict[str, Any]:
            """기본 쿼리 처리 (대체 구현)"""
            try:
                # 간단한 키워드 기반 쿼리 처리
                query_lower = query.lower()
                
                if '행' in query_lower or 'row' in query_lower:
                    return {
                        'answer': f'총 {len(df)}개의 행이 있습니다.',
                        'data': {'total_rows': len(df)},
                        'confidence': 0.95
                    }
                elif '컬럼' in query_lower or 'column' in query_lower:
                    return {
                        'answer': f'총 {len(df.columns)}개의 컬럼이 있습니다.',
                        'data': {'total_columns': len(df.columns)},
                        'confidence': 0.95
                    }
                elif '통계' in query_lower or 'statistics' in query_lower:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        stats = df[numeric_cols].describe()
                        return {
                            'answer': f'숫자 컬럼 {len(numeric_cols)}개의 통계를 계산했습니다.',
                            'data': stats.to_dict(),
                            'confidence': 0.90
                        }
                    else:
                        return {
                            'answer': '숫자 컬럼이 없어 통계를 계산할 수 없습니다.',
                            'data': {},
                            'confidence': 0.80
                        }
                else:
                    return {
                        'answer': f'쿼리 "{query}"를 처리했습니다. (기본 처리)',
                        'data': {'query': query},
                        'confidence': 0.70
                    }
            except Exception as e:
                return {
                    'answer': f'쿼리 처리 중 오류가 발생했습니다: {str(e)}',
                    'data': {},
                    'confidence': 0.0,
                    'error': str(e)
                }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelAgentIntegration:
    """Excel Agent 통합 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.excel_agent = ExcelAgent()
        self.loaded_dataframes: Dict[str, pd.DataFrame] = {}
        self.current_dataframe: Optional[pd.DataFrame] = None
        self.logger = logging.getLogger(__name__)
        
        # HVDC 특화 설정
        self.hvdc_config = {
            'warehouse_columns': [
                'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 
                'DSV MZP', 'AAA  Storage', 'Hauler Indoor', 'DHL Warehouse'
            ],
            'site_columns': ['MIR', 'SHU', 'DAS', 'AGI'],
            'hvdc_code_columns': ['HVDC CODE', 'HVDC CODE 1', 'HVDC CODE 2', 'HVDC CODE 3'],
            'status_columns': [col for col in ['Status_Current', 'Status_Location', 'Status_WAREHOUSE'] if col]
        }
    
    async def initialize(self) -> bool:
        """Excel Agent 통합 초기화"""
        try:
            self.logger.info("Excel Agent Integration initializing...")
            
            # 기본 HVDC 데이터 로드 (있는 경우)
            hvdc_data_path = Path("data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
            if hvdc_data_path.exists():
                await self.load_excel_file(str(hvdc_data_path), "hvdc_default")
                self.logger.info(f"Default HVDC data loaded: {len(self.current_dataframe)} rows")
            
            self.logger.info("Excel Agent Integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel Agent Integration initialization failed: {e}")
            return False
    
    async def load_excel_file(self, file_path: str, dataframe_name: str = None) -> Dict[str, Any]:
        """Excel 파일 로드"""
        try:
            if not os.path.exists(file_path):
                return {
                    'status': 'ERROR',
                    'error': f'File not found: {file_path}',
                    'confidence': 0.0
                }
            
            # Excel 파일 읽기
            df = pd.read_excel(file_path)
            
            # 데이터프레임 저장
            name = dataframe_name or f"df_{len(self.loaded_dataframes)}"
            self.loaded_dataframes[name] = df
            self.current_dataframe = df
            
            # 데이터 품질 검증
            quality_report = self._validate_data_quality(df)
            
            result = {
                'status': 'SUCCESS',
                'dataframe_name': name,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'file_size': os.path.getsize(file_path),
                'quality_report': quality_report,
                'confidence': 0.95
            }
            
            self.logger.info(f"Excel file loaded: {file_path} -> {len(df)} rows, {len(df.columns)} columns")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to load Excel file {file_path}: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0
            }
    
    def _validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 품질 검증"""
        try:
            # 기본 통계
            total_rows = len(df)
            total_columns = len(df.columns)
            
            # 결측값 분석
            missing_data = df.isnull().sum()
            total_missing = missing_data.sum()
            missing_percentage = (total_missing / (total_rows * total_columns)) * 100
            
            # HVDC 특화 검증
            hvdc_validation = self._validate_hvdc_data(df)
            
            # 데이터 타입 분석
            data_types = df.dtypes.value_counts().to_dict()
            
            return {
                'total_rows': total_rows,
                'total_columns': total_columns,
                'missing_data': {
                    'total_missing': total_missing,
                    'missing_percentage': round(missing_percentage, 2),
                    'columns_with_missing': missing_data[missing_data > 0].to_dict()
                },
                'data_types': data_types,
                'hvdc_validation': hvdc_validation
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_rows': len(df) if df is not None else 0
            }
    
    def _validate_hvdc_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """HVDC 데이터 특화 검증"""
        try:
            validation_result = {
                'has_warehouse_columns': False,
                'has_site_columns': False,
                'has_hvdc_codes': False,
                'warehouse_columns_found': [],
                'site_columns_found': [],
                'hvdc_code_columns_found': []
            }
            
            # 창고 컬럼 확인
            warehouse_found = [col for col in self.hvdc_config['warehouse_columns'] if col in df.columns]
            validation_result['has_warehouse_columns'] = len(warehouse_found) > 0
            validation_result['warehouse_columns_found'] = warehouse_found
            
            # 현장 컬럼 확인
            site_found = [col for col in self.hvdc_config['site_columns'] if col in df.columns]
            validation_result['has_site_columns'] = len(site_found) > 0
            validation_result['site_columns_found'] = site_found
            
            # HVDC 코드 컬럼 확인
            hvdc_found = [col for col in self.hvdc_config['hvdc_code_columns'] if col in df.columns]
            validation_result['has_hvdc_codes'] = len(hvdc_found) > 0
            validation_result['hvdc_code_columns_found'] = hvdc_found
            
            return validation_result
            
        except Exception as e:
            return {'error': str(e)}
    
    async def process_natural_language_query(self, query: str, dataframe_name: str = None) -> Dict[str, Any]:
        """자연어 쿼리 처리"""
        try:
            if self.current_dataframe is None:
                return {
                    'status': 'ERROR',
                    'error': 'No data loaded. Please load an Excel file first.',
                    'confidence': 0.0
                }
            
            # Excel Agent로 쿼리 처리
            result = await self.excel_agent.process_query(self.current_dataframe, query)
            
            # HVDC 특화 쿼리 처리
            hvdc_result = await self._process_hvdc_specific_query(query)
            
            # 결과 통합
            combined_result = {
                'status': 'SUCCESS',
                'query': query,
                'answer': result.get('answer', ''),
                'data': result.get('data', {}),
                'hvdc_analysis': hvdc_result,
                'confidence': result.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Query processed: {query} -> Confidence: {combined_result['confidence']}")
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _process_hvdc_specific_query(self, query: str) -> Dict[str, Any]:
        """HVDC 특화 쿼리 처리"""
        try:
            if self.current_dataframe is None:
                return {}
            
            df = self.current_dataframe
            query_lower = query.lower()
            
            # 창고별 분석
            if '창고' in query_lower or 'warehouse' in query_lower:
                warehouse_analysis = {}
                for col in self.hvdc_config['warehouse_columns']:
                    if col in df.columns:
                        count = df[col].notna().sum()
                        if count > 0:
                            warehouse_analysis[col] = count
                
                return {
                    'warehouse_analysis': warehouse_analysis,
                    'total_warehouse_items': sum(warehouse_analysis.values())
                }
            
            # 현장별 분석
            elif '현장' in query_lower or 'site' in query_lower:
                site_analysis = {}
                for col in self.hvdc_config['site_columns']:
                    if col in df.columns:
                        count = df[col].notna().sum()
                        if count > 0:
                            site_analysis[col] = count
                
                return {
                    'site_analysis': site_analysis,
                    'total_site_items': sum(site_analysis.values())
                }
            
            # HVDC 코드 분석
            elif 'hvdc' in query_lower or '코드' in query_lower:
                code_analysis = {}
                for col in self.hvdc_config['hvdc_code_columns']:
                    if col in df.columns:
                        unique_count = df[col].nunique()
                        code_analysis[col] = unique_count
                
                return {
                    'hvdc_code_analysis': code_analysis,
                    'total_unique_codes': sum(code_analysis.values())
                }
            
            # 상태 분석
            elif '상태' in query_lower or 'status' in query_lower:
                status_analysis = {}
                for col in self.hvdc_config['status_columns']:
                    if col in df.columns:
                        status_counts = df[col].value_counts().to_dict()
                        status_analysis[col] = status_counts
                
                return {
                    'status_analysis': status_analysis
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"HVDC specific query processing failed: {e}")
            return {'error': str(e)}
    
    async def get_dataframe_info(self, dataframe_name: str = None) -> Dict[str, Any]:
        """데이터프레임 정보 조회"""
        try:
            df = self.current_dataframe
            if df is None:
                return {
                    'status': 'ERROR',
                    'error': 'No data loaded',
                    'confidence': 0.0
                }
            
            info = {
                'status': 'SUCCESS',
                'shape': df.shape,
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
                'confidence': 0.95
            }
            
            return info
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def export_analysis_report(self, output_path: str = None) -> Dict[str, Any]:
        """분석 리포트 내보내기"""
        try:
            if self.current_dataframe is None:
                return {
                    'status': 'ERROR',
                    'error': 'No data loaded for analysis',
                    'confidence': 0.0
                }
            
            df = self.current_dataframe
            
            # 기본 통계
            basic_stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_data_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            }
            
            # HVDC 특화 분석
            hvdc_analysis = await self._process_hvdc_specific_query("창고 현장 HVDC 코드 상태 분석")
            
            # 리포트 생성
            report = {
                'timestamp': datetime.now().isoformat(),
                'basic_statistics': basic_stats,
                'hvdc_analysis': hvdc_analysis,
                'data_quality': self._validate_data_quality(df)
            }
            
            # 파일로 저장
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            return {
                'status': 'SUCCESS',
                'report': report,
                'output_path': output_path,
                'confidence': 0.95
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        try:
            status = {
                'status': 'ACTIVE',
                'loaded_dataframes': len(self.loaded_dataframes),
                'current_dataframe': {
                    'name': 'None' if self.current_dataframe is None else 'Active',
                    'shape': self.current_dataframe.shape if self.current_dataframe is not None else None
                },
                'excel_agent_status': 'READY',
                'hvdc_integration': 'ACTIVE',
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.95
            }
            
            return status
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0
            }

# MACHO-GPT 시스템 통합을 위한 어댑터 클래스
class ExcelAgentMACHOAdapter:
    """Excel Agent를 MACHO-GPT 시스템에 통합하는 어댑터"""
    
    def __init__(self, excel_agent_integration: ExcelAgentIntegration):
        self.excel_agent = excel_agent_integration
        self.logger = logging.getLogger(__name__)
    
    async def execute_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """MACHO-GPT 명령어 실행"""
        try:
            parameters = parameters or {}
            
            if command == "load_excel":
                file_path = parameters.get('file_path')
                dataframe_name = parameters.get('dataframe_name')
                return await self.excel_agent.load_excel_file(file_path, dataframe_name)
            
            elif command == "query_data":
                query = parameters.get('query')
                dataframe_name = parameters.get('dataframe_name')
                return await self.excel_agent.process_natural_language_query(query, dataframe_name)
            
            elif command == "get_info":
                dataframe_name = parameters.get('dataframe_name')
                return await self.excel_agent.get_dataframe_info(dataframe_name)
            
            elif command == "export_report":
                output_path = parameters.get('output_path')
                return await self.excel_agent.export_analysis_report(output_path)
            
            elif command == "get_status":
                return await self.excel_agent.get_system_status()
            
            else:
                return {
                    'status': 'ERROR',
                    'error': f'Unknown command: {command}',
                    'confidence': 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0
            }
    
    def get_available_commands(self) -> List[Dict[str, Any]]:
        """사용 가능한 명령어 목록"""
        return [
            {
                'name': 'load_excel',
                'description': 'Excel 파일 로드',
                'parameters': ['file_path', 'dataframe_name']
            },
            {
                'name': 'query_data',
                'description': '자연어 데이터 쿼리',
                'parameters': ['query', 'dataframe_name']
            },
            {
                'name': 'get_info',
                'description': '데이터프레임 정보 조회',
                'parameters': ['dataframe_name']
            },
            {
                'name': 'export_report',
                'description': '분석 리포트 내보내기',
                'parameters': ['output_path']
            },
            {
                'name': 'get_status',
                'description': '시스템 상태 조회',
                'parameters': []
            }
        ]

# 테스트 함수
async def test_excel_agent_integration():
    """Excel Agent 통합 테스트"""
    print("=== Excel Agent Integration Test ===")
    
    # 통합 모듈 초기화
    integration = ExcelAgentIntegration()
    success = await integration.initialize()
    
    if not success:
        print("❌ Integration initialization failed")
        return
    
    print("✅ Integration initialized successfully")
    
    # 시스템 상태 확인
    status = await integration.get_system_status()
    print(f"System status: {status}")
    
    # 데이터프레임 정보 조회
    if integration.current_dataframe is not None:
        info = await integration.get_dataframe_info()
        print(f"Dataframe info: {info}")
    
    print("✅ Excel Agent Integration test completed")

if __name__ == "__main__":
    asyncio.run(test_excel_agent_integration()) 