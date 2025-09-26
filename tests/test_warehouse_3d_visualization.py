"""
Test Suite for MACHO-GPT Warehouse 3D Visualization System
HVDC PROJECT | TDD Test Coverage ≥95%
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from datetime import datetime
import json

# Import the module under test
from src.warehouse_3d_visualization_system import Warehouse3DVisualizationSystem


class TestWarehouse3DVisualizationSystem:
    """Test suite for Warehouse3DVisualizationSystem class"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.viz_system = Warehouse3DVisualizationSystem(mode="LATTICE")
        
        # Create sample warehouse data
        self.sample_data = pd.DataFrame({
            'Case No.': [f'CASE_{i:03d}' for i in range(1, 41)],
            'L(CM)': np.random.uniform(200, 300, 40),
            'W(CM)': np.random.uniform(100, 150, 40),
            'H(CM)': np.random.uniform(150, 200, 40),
            'G.W(kgs)': np.random.uniform(500, 2000, 40),
            'Stack': np.random.choice([0, 1, 2], 40)
        })
    
    def test_init_default_parameters(self):
        """Test initialization with default parameters"""
        viz = Warehouse3DVisualizationSystem()
        
        assert viz.mode == "LATTICE"
        assert viz.confidence_threshold == 0.90
        assert viz.success_rate_target == 0.95
        assert viz.warehouse_dimensions['zone_ab']['length'] == 35
        assert viz.warehouse_dimensions['zone_ab']['width'] == 15
        assert viz.warehouse_dimensions['zone_ab']['height'] == 10
        assert viz.kpi_triggers['utilization_threshold'] == 85
        assert viz.kpi_triggers['pressure_limit'] == 4.0
    
    def test_init_custom_mode(self):
        """Test initialization with custom mode"""
        viz = Warehouse3DVisualizationSystem(mode="ZERO")
        assert viz.mode == "ZERO"
    
    def test_validate_warehouse_data_complete(self):
        """Test data validation with complete data"""
        result = self.viz_system._validate_warehouse_data(self.sample_data.copy())
        
        # Check that meter columns were created
        assert 'L(M)' in result.columns
        assert 'W(M)' in result.columns
        assert 'H(M)' in result.columns
        
        # Check that volume and pressure were calculated
        assert 'Volume_M3' in result.columns
        assert 'Pressure_T_M2' in result.columns
        
        # Verify conversions
        assert result['L(M)'].iloc[0] == result['L(CM)'].iloc[0] / 100
        assert result['W(M)'].iloc[0] == result['W(CM)'].iloc[0] / 100
        assert result['H(M)'].iloc[0] == result['H(CM)'].iloc[0] / 100
    
    def test_validate_warehouse_data_missing_columns(self):
        """Test data validation with missing columns"""
        incomplete_data = pd.DataFrame({
            'Case No.': ['CASE_001', 'CASE_002'],
            'L(CM)': [240, 250]
        })
        
        result = self.viz_system._validate_warehouse_data(incomplete_data)
        
        # Check that missing columns were filled with defaults
        assert 'W(CM)' in result.columns
        assert 'H(CM)' in result.columns
        assert 'G.W(kgs)' in result.columns
        
        # Check default values
        assert result['W(CM)'].iloc[0] == 120
        assert result['H(CM)'].iloc[0] == 180
        assert result['G.W(kgs)'].iloc[0] == 1000
    
    def test_generate_zoneab_layout_csv(self):
        """Test Zone AB layout CSV generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_csv = f.name
        
        try:
            result_path = self.viz_system.generate_zoneab_layout_csv(self.sample_data, temp_csv)
            
            # Check that file was created
            assert os.path.exists(result_path)
            
            # Load and validate the generated CSV
            layout_df = pd.read_csv(result_path)
            
            # Check required columns
            required_columns = ['Case_No', 'X', 'Y', 'L', 'W', 'H', 'Weight_kg', 'Pressure_T_M2', 'Stackable']
            for col in required_columns:
                assert col in layout_df.columns
            
            # Check that we have 39 items (Zone AB limit)
            assert len(layout_df) == 39
            
            # Check coordinate ranges
            assert layout_df['X'].min() >= 0
            assert layout_df['Y'].min() >= 0
            assert layout_df['X'].max() <= 35  # warehouse length
            assert layout_df['Y'].max() <= 15  # warehouse width
            
            # Check dimensions are positive
            assert (layout_df['L'] > 0).all()
            assert (layout_df['W'] > 0).all()
            assert (layout_df['H'] > 0).all()
            
        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)
    
    def test_generate_sketchup_ruby_script(self):
        """Test SketchUp Ruby script generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_csv = f.name
        
        try:
            # Create a simple CSV for testing
            test_data = pd.DataFrame({
                'Case_No': ['CASE_001', 'CASE_002'],
                'X': [0, 2.5],
                'Y': [0, 1.5],
                'L': [2.4, 2.4],
                'W': [1.2, 1.2],
                'H': [1.8, 1.8],
                'Weight_kg': [1000, 1200],
                'Pressure_T_M2': [0.35, 0.42],
                'Stackable': [1, 1]
            })
            test_data.to_csv(temp_csv, index=False)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rb', delete=False) as f:
                temp_ruby = f.name
            
            try:
                result_path = self.viz_system.generate_sketchup_ruby_script(temp_csv, temp_ruby)
                
                # Check that file was created
                assert os.path.exists(result_path)
                
                # Read and validate Ruby script content
                with open(result_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                # Check for required Ruby elements
                assert 'require \'csv\'' in script_content
                assert 'def import_warehouse_layout' in script_content
                assert 'CSV.foreach' in script_content
                assert 'entities.add_group' in script_content
                assert 'pushpull' in script_content
                
                # Check for warehouse dimensions
                assert '35.m' in script_content
                assert '15.m' in script_content
                assert '10.m' in script_content
                
            finally:
                if os.path.exists(temp_ruby):
                    os.unlink(temp_ruby)
                    
        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)
    
    def test_generate_blender_python_script(self):
        """Test Blender Python script generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_csv = f.name
        
        try:
            # Create a simple CSV for testing
            test_data = pd.DataFrame({
                'Case_No': ['CASE_001', 'CASE_002'],
                'X': [0, 2.5],
                'Y': [0, 1.5],
                'L': [2.4, 2.4],
                'W': [1.2, 1.2],
                'H': [1.8, 1.8],
                'Weight_kg': [1000, 1200],
                'Pressure_T_M2': [0.35, 0.42],
                'Stackable': [1, 1]
            })
            test_data.to_csv(temp_csv, index=False)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                temp_python = f.name
            
            try:
                result_path = self.viz_system.generate_blender_python_script(temp_csv, temp_python)
                
                # Check that file was created
                assert os.path.exists(result_path)
                
                # Read and validate Python script content
                with open(result_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                # Check for required Blender elements
                assert 'import bpy' in script_content
                assert 'def create_warehouse_floor' in script_content
                assert 'def create_crate' in script_content
                assert 'def setup_lighting' in script_content
                assert 'def setup_camera' in script_content
                assert 'bpy.ops.mesh.primitive_cube_add' in script_content
                assert 'bpy.ops.object.light_add' in script_content
                
                # Check for warehouse dimensions
                assert '35' in script_content
                assert '15' in script_content
                assert '10' in script_content
                
            finally:
                if os.path.exists(temp_python):
                    os.unlink(temp_python)
                    
        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)
    
    def test_generate_workflow_guide(self):
        """Test workflow guide generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_guide = f.name
        
        try:
            result_path = self.viz_system.generate_workflow_guide(
                "test_zoneAB_layout.csv",
                "test_sketchup_import.rb",
                "test_blender_import.py"
            )
            
            # Check that file was created
            assert os.path.exists(result_path)
            
            # Read and validate guide content
            with open(result_path, 'r', encoding='utf-8') as f:
                guide_content = f.read()
            
            # Check for required sections
            assert 'MACHO-GPT Warehouse 3D Visualization Workflow Guide' in guide_content
            assert 'Executive Summary' in guide_content
            assert 'AB 구역' in guide_content
            assert 'SketchUp Free' in guide_content
            assert 'Blender' in guide_content
            assert 'Canva' in guide_content
            assert '무료 리소스' in guide_content
            assert '체크리스트' in guide_content
            
            # Check for file references
            assert 'test_zoneAB_layout.csv' in guide_content
            assert 'test_sketchup_import.rb' in guide_content
            assert 'test_blender_import.py' in guide_content
            
        finally:
            if os.path.exists(temp_guide):
                os.unlink(temp_guide)
    
    @patch('pandas.read_csv')
    @patch('pandas.read_excel')
    def test_load_warehouse_data_csv(self, mock_read_excel, mock_read_csv):
        """Test loading warehouse data from CSV file"""
        mock_read_csv.return_value = self.sample_data
        
        result = self.viz_system.load_warehouse_data("test_data.csv")
        
        mock_read_csv.assert_called_once_with("test_data.csv")
        assert len(result) == len(self.sample_data)
    
    @patch('pandas.read_csv')
    @patch('pandas.read_excel')
    def test_load_warehouse_data_excel(self, mock_read_excel, mock_read_csv):
        """Test loading warehouse data from Excel file"""
        mock_read_excel.return_value = self.sample_data
        
        result = self.viz_system.load_warehouse_data("test_data.xlsx")
        
        mock_read_excel.assert_called_once_with("test_data.xlsx")
        assert len(result) == len(self.sample_data)
    
    def test_load_warehouse_data_unsupported_format(self):
        """Test loading warehouse data with unsupported format"""
        with pytest.raises(ValueError, match="Unsupported file format"):
            self.viz_system.load_warehouse_data("test_data.txt")
    
    def test_run_complete_workflow_success(self):
        """Test complete workflow execution with success"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_data = f.name
        
        try:
            # Create test data file
            self.sample_data.to_csv(temp_data, index=False)
            
            result = self.viz_system.run_complete_workflow(temp_data)
            
            # Check success status
            assert result['status'] == 'SUCCESS'
            assert result['confidence'] >= 0.90
            assert result['mode'] == 'LATTICE'
            
            # Check generated files
            assert 'generated_files' in result
            assert 'csv_layout' in result['generated_files']
            assert 'sketchup_script' in result['generated_files']
            assert 'blender_script' in result['generated_files']
            assert 'workflow_guide' in result['generated_files']
            
            # Check warehouse stats
            assert 'warehouse_stats' in result
            assert result['warehouse_stats']['total_items'] == 40
            assert result['warehouse_stats']['zone_ab_items'] == 39
            
            # Check next commands
            assert 'next_commands' in result
            assert len(result['next_commands']) >= 3
            
        finally:
            if os.path.exists(temp_data):
                os.unlink(temp_data)
    
    def test_run_complete_workflow_failure(self):
        """Test complete workflow execution with failure"""
        result = self.viz_system.run_complete_workflow("nonexistent_file.csv")
        
        assert result['status'] == 'FAIL'
        assert 'error' in result
        assert result['mode'] == 'ZERO'  # Should switch to ZERO mode on failure
    
    def test_pressure_limit_validation(self):
        """Test pressure limit validation"""
        # Create data with high pressure items
        high_pressure_data = self.sample_data.copy()
        high_pressure_data.loc[0, 'G.W(kgs)'] = 10000  # Very heavy item
        high_pressure_data.loc[1, 'L(CM)'] = 50  # Very small footprint
        high_pressure_data.loc[1, 'W(CM)'] = 50
        
        result = self.viz_system._validate_warehouse_data(high_pressure_data)
        
        # Check that pressure was calculated
        assert 'Pressure_T_M2' in result.columns
        
        # Check that high pressure items are flagged
        high_pressure_items = result[result['Pressure_T_M2'] > self.viz_system.kpi_triggers['pressure_limit']]
        assert len(high_pressure_items) > 0


def test_main_function():
    """Test main function execution"""
    # This test verifies that the main function can be called without errors
    # In a real scenario, you might want to mock file operations
    
    # Import and call main function
    from src.warehouse_3d_visualization_system import main
    
    # The main function should not raise exceptions
    try:
        main()
    except Exception as e:
        # If it fails, it should be due to missing data files, which is expected
        assert "warehouse data" in str(e).lower() or "sample" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 