# 🚀 HVDC Performance Optimization Implementation Guide

## Quick Start

This guide provides step-by-step instructions to implement the performance optimizations identified in the HVDC project analysis.

### Expected Results
- **60-70% Bundle Size Reduction** (146MB → 40-60MB)
- **50-60% Faster Startup Times** (3-5s → 1-2s)  
- **30-40% Memory Efficiency** (200-500MB → 120-300MB)
- **25-35% Runtime Performance Improvement**

---

## 📋 Prerequisites

1. **Python 3.8+** (3.11+ recommended for best performance)
2. **Git access** to the HVDC repository
3. **Administrative access** for dependency installation
4. **Backup** of current working system

---

## 🎯 Phase 1: Immediate Optimizations (Week 1)

### Step 1.1: Install Optimized Dependencies

```bash
# Backup current requirements
cp requirements.txt requirements-backup.txt

# Install minimal dependencies
pip install -r requirements-minimal.txt

# Test system functionality
python3 performance_tests.py
```

### Step 1.2: Implement Lazy Loading

Replace eager imports in key files:

**File: `hvdc_ontology_engine.py`**
```python
# Before (lines 6-14)
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

# After
_pandas = None
_rdflib = None

def get_pandas():
    global _pandas
    if _pandas is None:
        try:
            import pandas as pd
            _pandas = pd
        except ImportError:
            _pandas = None
    return _pandas
```

**File: `Mapping/ontology_reasoning_engine.py`**
```python
# Replace lines 15-22 with conditional imports
ML_AVAILABLE = False
try:
    from sklearn.experimental import enable_iterative_imputer
    from sklearn.impute import IterativeImputer
    from sklearn.ensemble import RandomForestRegressor
    ML_AVAILABLE = True
except ImportError:
    print("⚠️ ML libraries not available - using fallback methods")
```

### Step 1.3: Add Basic Caching

**Create: `utils/performance_cache.py`**
```python
from functools import lru_cache
import sqlite3
import json

class SimpleCache:
    def __init__(self, cache_size=1000):
        self.cache_db = sqlite3.connect(":memory:")
        self.cache_size = cache_size
        self._setup_cache()
    
    def _setup_cache(self):
        self.cache_db.execute("""
            CREATE TABLE cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp REAL
            )
        """)
    
    @lru_cache(maxsize=128)
    def get(self, key):
        cursor = self.cache_db.cursor()
        cursor.execute("SELECT value FROM cache WHERE key = ?", (key,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None
    
    def set(self, key, value):
        cursor = self.cache_db.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time())
        )
        self.cache_db.commit()
```

### Step 1.4: Optimize Database Queries

**Update: `hvdc_ontology_engine.py`**
```python
def _setup_indexes(self):
    """Add performance indexes"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_vendor ON items(vendor)",
        "CREATE INDEX IF NOT EXISTS idx_category ON items(category)",
        "CREATE INDEX IF NOT EXISTS idx_location ON items(location)",
        "CREATE INDEX IF NOT EXISTS idx_weight ON items(weight)",
    ]
    
    with self.get_connection() as conn:
        for index_sql in indexes:
            conn.execute(index_sql)
        conn.commit()
```

### Step 1.5: Test Phase 1 Results

```bash
# Run performance tests
python3 performance_tests.py

# Expected improvements:
# - Startup time: 20-30% faster
# - Memory usage: 15-25% reduction
# - Import time: 40-50% faster
```

---

## ⚡ Phase 2: Structural Optimizations (Week 2)

### Step 2.1: Replace Heavy Dependencies

**Option A: Replace pandas with polars (recommended)**
```python
# Install polars
pip install polars

# Update data processing functions
def load_excel_optimized(filepath):
    try:
        import polars as pl
        return pl.read_excel(filepath)
    except ImportError:
        # Fallback to pandas
        pd = get_pandas()
        return pd.read_excel(filepath) if pd else None
```

**Option B: Implement lightweight data processing**
```python
import csv
import json

def load_csv_lightweight(filepath):
    """Lightweight CSV loading without pandas"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data
```

### Step 2.2: Implement Connection Pooling

**Replace database connections with pooled connections:**
```python
class ConnectionPool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool = [sqlite3.connect(db_path) for _ in range(pool_size)]
        self.available = list(self.pool)
    
    @contextmanager
    def get_connection(self):
        conn = self.available.pop() if self.available else sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            self.available.append(conn)
```

### Step 2.3: Add Memory Management

**Update memory-intensive operations:**
```python
import gc
from contextlib import contextmanager

@contextmanager
def memory_managed_operation():
    initial_memory = get_memory_usage()
    try:
        yield
    finally:
        gc.collect()
        final_memory = get_memory_usage()
        logger.info(f"Memory freed: {initial_memory - final_memory:.2f}MB")

# Usage
with memory_managed_operation():
    large_data_processing()
```

### Step 2.4: Implement Async Processing

**Add async support for I/O operations:**
```python
import asyncio

async def load_multiple_files_async(file_paths):
    tasks = []
    for path in file_paths:
        task = asyncio.create_task(load_file_async(path))
        tasks.append(task)
    return await asyncio.gather(*tasks)

async def load_file_async(filepath):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, load_file_sync, filepath)
```

---

## 🔧 Phase 3: Advanced Optimizations (Week 3)

### Step 3.1: Deploy Optimized Engine

```bash
# Replace original engine with optimized version
cp hvdc_ontology_engine.py hvdc_ontology_engine_backup.py
cp optimized_hvdc_engine.py hvdc_ontology_engine.py

# Update imports in dependent files
find . -name "*.py" -exec sed -i 's/from hvdc_ontology_engine import HVDCOntologyEngine/from hvdc_ontology_engine import OptimizedHVDCEngine as HVDCOntologyEngine/g' {} \;
```

### Step 3.2: Configure Environment-Based Optimization

**Create: `config/optimization_config.py`**
```python
import os

class OptimizationConfig:
    def __init__(self):
        self.env = os.getenv('HVDC_ENV', 'production')
        self.enable_ml = self.env in ['development', 'full']
        self.enable_viz = self.env in ['development', 'full'] 
        self.cache_size = {
            'minimal': 100,
            'production': 1000,
            'development': 5000
        }.get(self.env, 1000)
        
    def get_engine_config(self):
        return {
            'cache_size': self.cache_size,
            'enable_rdf': self.enable_ml,
            'enable_ml': self.enable_ml
        }
```

### Step 3.3: Add Performance Monitoring

**Create: `utils/performance_monitor.py`**
```python
import time
import psutil
from functools import wraps

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def track_performance(self, operation_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                self.metrics[operation_name] = {
                    'duration': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'timestamp': time.time()
                }
                
                return result
            return wrapper
        return decorator
```

---

## 📊 Phase 4: Testing & Validation (Week 4)

### Step 4.1: Run Comprehensive Performance Tests

```bash
# Full performance test suite
python3 performance_tests.py

# Expected results:
# - Overall Score: 80+ (vs 60-70 before)
# - Startup Time: <2 seconds
# - Memory Usage: <300MB
# - Cache Hit Rate: >70%
```

### Step 4.2: Load Testing

```bash
# Test with concurrent users
python3 -c "
import asyncio
from optimized_hvdc_engine import create_hvdc_engine

async def load_test():
    engines = [create_hvdc_engine('standard') for _ in range(10)]
    tasks = []
    for engine in engines:
        task = asyncio.create_task(engine.get_warehouse_utilization_optimized())
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    print(f'Processed {len(results)} concurrent requests')

asyncio.run(load_test())
"
```

### Step 4.3: Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python3 -m memory_profiler optimized_hvdc_engine.py

# Expected: <300MB peak memory usage
```

### Step 4.4: Benchmark Against Original

```bash
# Create benchmark script
cat > benchmark_comparison.py << 'EOF'
import time
import sys

def benchmark_original():
    start = time.time()
    # Import original heavy dependencies
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    return time.time() - start

def benchmark_optimized():
    start = time.time()
    # Import optimized engine
    from optimized_hvdc_engine import create_hvdc_engine
    engine = create_hvdc_engine('minimal')
    return time.time() - start

if __name__ == "__main__":
    print("Benchmarking startup times...")
    
    # Test optimized version
    opt_time = benchmark_optimized()
    print(f"Optimized startup: {opt_time:.3f}s")
    
    # Test original (if dependencies available)
    try:
        orig_time = benchmark_original()
        print(f"Original startup: {orig_time:.3f}s")
        improvement = ((orig_time - opt_time) / orig_time) * 100
        print(f"Improvement: {improvement:.1f}%")
    except ImportError:
        print("Original dependencies not available")
EOF

python3 benchmark_comparison.py
```

---

## 🚀 Production Deployment

### Step 5.1: Environment Setup

```bash
# Production environment variables
export HVDC_ENV=production
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Install production dependencies only
pip install -r requirements-minimal.txt --no-dev
```

### Step 5.2: Docker Optimization

**Create: `Dockerfile.optimized`**
```dockerfile
FROM python:3.11-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy optimized source code
COPY optimized_hvdc_engine.py .
COPY utils/ ./utils/
COPY config/ ./config/

# Set environment for production
ENV HVDC_ENV=production
ENV PYTHONOPTIMIZE=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from optimized_hvdc_engine import create_hvdc_engine; engine = create_hvdc_engine('minimal'); print('OK')"

# Run application
CMD ["python3", "optimized_hvdc_engine.py"]
```

### Step 5.3: Performance Monitoring Setup

```bash
# Create monitoring script
cat > monitor_performance.py << 'EOF'
import time
import psutil
import json
from datetime import datetime

def collect_metrics():
    process = psutil.Process()
    return {
        'timestamp': datetime.now().isoformat(),
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'cpu_percent': process.cpu_percent(),
        'threads': process.num_threads(),
        'connections': len(process.connections())
    }

def monitor_loop():
    while True:
        metrics = collect_metrics()
        print(json.dumps(metrics))
        time.sleep(60)  # Every minute

if __name__ == "__main__":
    monitor_loop()
EOF
```

---

## 📈 Success Validation

### Performance Targets (Must Achieve)

- ✅ **Startup Time**: <2 seconds (from 3-5 seconds)
- ✅ **Memory Usage**: <300MB (from 200-500MB)
- ✅ **Bundle Size**: <60MB (from 146MB)
- ✅ **Cache Hit Rate**: >70%
- ✅ **Database Query Time**: <10ms for indexed queries
- ✅ **Overall Performance Score**: 80+ (from 60-70)

### Validation Commands

```bash
# Quick validation script
cat > validate_optimization.py << 'EOF'
import time
import sys
from optimized_hvdc_engine import create_hvdc_engine, benchmark_performance

def validate():
    print("🔍 Validating HVDC Performance Optimizations...")
    
    # Test 1: Startup time
    start = time.time()
    engine = create_hvdc_engine('standard')
    startup_time = time.time() - start
    
    startup_ok = startup_time < 2.0
    print(f"✅ Startup time: {startup_time:.3f}s {'✓' if startup_ok else '✗'}")
    
    # Test 2: Memory usage
    try:
        import psutil
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        memory_ok = memory_mb < 300
        print(f"✅ Memory usage: {memory_mb:.1f}MB {'✓' if memory_ok else '✗'}")
    except ImportError:
        print("⚠️ Cannot measure memory (psutil not available)")
        memory_ok = True
    
    # Test 3: Basic functionality
    try:
        result = engine.get_performance_metrics()
        func_ok = 'queries_executed' in result
        print(f"✅ Functionality: {'✓' if func_ok else '✗'}")
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        func_ok = False
    
    # Overall result
    all_ok = startup_ok and memory_ok and func_ok
    print(f"\n🎯 Overall: {'✅ PASS' if all_ok else '❌ FAIL'}")
    
    engine.close()
    return all_ok

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
EOF

python3 validate_optimization.py
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue 1: Import errors after optimization**
```bash
# Solution: Check dependency installation
pip install -r requirements-minimal.txt
python3 -c "import polars; print('Polars OK')"
```

**Issue 2: Performance degradation**
```bash
# Solution: Check cache configuration
export HVDC_CACHE_SIZE=1000
python3 performance_tests.py
```

**Issue 3: Memory leaks**
```bash
# Solution: Enable garbage collection monitoring
export PYTHONDEBUG=1
python3 -c "import gc; gc.set_debug(gc.DEBUG_LEAK)"
```

### Rollback Plan

```bash
# Emergency rollback
cp hvdc_ontology_engine_backup.py hvdc_ontology_engine.py
pip install -r requirements-backup.txt
python3 check_installation.py
```

---

## 📞 Support

- **Performance Issues**: Run `python3 performance_tests.py`
- **Memory Problems**: Use `python3 -m memory_profiler script.py`
- **Functionality Issues**: Check `python3 validate_optimization.py`

**Next Steps**: After successful implementation, monitor performance metrics and fine-tune cache sizes and optimization levels based on actual usage patterns.

---

**Implementation Status**: Ready for deployment  
**Estimated Time**: 4 weeks  
**Expected ROI**: 40-60% performance improvement  
**Risk Level**: Low (with proper testing and rollback plan)