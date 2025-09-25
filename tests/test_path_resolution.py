import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hvdc_datachain_pipeline import get_data_dir, main
from pathlib import Path
import pytest

def test_data_dir_resolution(monkeypatch, tmp_path):
    # 1) ENV 변수 override
    fake_root = tmp_path / "HVDC_PJT"
    data = fake_root / "data"
    src  = fake_root / "src"
    data.mkdir(parents=True)
    src.mkdir()

    monkeypatch.setenv("HVDC_ROOT", str(fake_root))
    assert get_data_dir() == data.resolve()

def test_graceful_empty_data(monkeypatch, tmp_path):
    fake_root = tmp_path / "HVDC_PJT"
    (fake_root / "data").mkdir(parents=True)
    (fake_root / "src").mkdir()
    monkeypatch.chdir(fake_root / "src")
    monkeypatch.setenv("HVDC_ROOT", str(fake_root))
    assert main() == 0          # no exception, exit code 0

if __name__ == "__main__":
    # Simple test execution without pytest
    print("Testing path resolution functions...")
    
    # Test 1: Basic functionality
    try:
        from hvdc_datachain_pipeline import get_project_root
        project_root = get_project_root()
        data_dir = get_data_dir()
        print(f"✓ Project root: {project_root}")
        print(f"✓ Data directory: {data_dir}")
        print("✓ Basic path resolution test passed")
    except Exception as e:
        print(f"✗ Basic path resolution test failed: {e}")
    
    # Test 2: Import test
    try:
        from hvdc_datachain_pipeline import get_project_root
        print("✓ Import test passed")
    except Exception as e:
        print(f"✗ Import test failed: {e}")
    
    print("Test execution completed.") 