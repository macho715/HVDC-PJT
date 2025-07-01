#!/usr/bin/env python3
"""
HVDC Performance Testing Suite
Comprehensive performance benchmarking and validation

This suite tests:
- Startup time optimization
- Memory usage efficiency
- Database query performance
- Caching effectiveness
- Concurrent operation handling
"""

import time
import asyncio
import gc
import sqlite3
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """Performance profiling utilities"""
    
    def __init__(self):
        self.results = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing and return duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.results[operation] = duration
            del self.start_times[operation]
            return duration
        return 0.0
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except ImportError:
            logger.warning("psutil not available - cannot measure memory")
            return 0.0
    
    def profile_function(self, func, *args, **kwargs):
        """Profile a function execution"""
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'memory_usage': end_memory - start_memory,
            'peak_memory': end_memory
        }

class DatabasePerformanceTest:
    """Database operation performance tests"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test database with sample data"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS test_items (
                id INTEGER PRIMARY KEY,
                hvdc_code TEXT UNIQUE,
                vendor TEXT,
                category TEXT,
                weight REAL,
                location TEXT,
                status TEXT
            )
        """)
        
        # Create indexes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_vendor ON test_items(vendor)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_weight ON test_items(weight)")
        
        # Insert test data
        test_data = [
            (f"HVDC-{i:04d}", f"VENDOR_{i % 5}", f"CAT_{i % 10}", 
             1000 + (i * 10), f"LOC_{i % 20}", "active")
            for i in range(10000)
        ]
        
        self.conn.executemany("""
            INSERT OR REPLACE INTO test_items 
            (hvdc_code, vendor, category, weight, location, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_data)
        
        self.conn.commit()
    
    def test_query_performance(self) -> Dict[str, float]:
        """Test various query performance scenarios"""
        results = {}
        
        # Test 1: Simple select
        start_time = time.time()
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_items")
        cursor.fetchone()
        results['simple_count'] = time.time() - start_time
        
        # Test 2: Indexed query
        start_time = time.time()
        cursor.execute("SELECT * FROM test_items WHERE vendor = 'VENDOR_1'")
        cursor.fetchall()
        results['indexed_query'] = time.time() - start_time
        
        # Test 3: Range query
        start_time = time.time()
        cursor.execute("SELECT * FROM test_items WHERE weight BETWEEN 5000 AND 10000")
        cursor.fetchall()
        results['range_query'] = time.time() - start_time
        
        # Test 4: Complex join-like query
        start_time = time.time()
        cursor.execute("""
            SELECT vendor, COUNT(*), AVG(weight) 
            FROM test_items 
            GROUP BY vendor 
            ORDER BY COUNT(*) DESC
        """)
        cursor.fetchall()
        results['aggregate_query'] = time.time() - start_time
        
        return results
    
    def test_bulk_operations(self) -> Dict[str, float]:
        """Test bulk insert/update performance"""
        results = {}
        
        # Bulk insert test
        bulk_data = [
            (f"BULK-{i:04d}", f"BULK_VENDOR_{i % 3}", "BULK_CAT", 
             2000 + i, "BULK_LOC", "bulk")
            for i in range(5000)
        ]
        
        start_time = time.time()
        self.conn.executemany("""
            INSERT OR REPLACE INTO test_items 
            (hvdc_code, vendor, category, weight, location, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, bulk_data)
        self.conn.commit()
        results['bulk_insert'] = time.time() - start_time
        
        # Bulk update test
        start_time = time.time()
        self.conn.execute("UPDATE test_items SET status = 'updated' WHERE vendor LIKE 'BULK_%'")
        self.conn.commit()
        results['bulk_update'] = time.time() - start_time
        
        return results
    
    def close(self):
        """Close database connection"""
        self.conn.close()

class CachePerformanceTest:
    """Cache performance testing"""
    
    def __init__(self):
        self.cache = {}
        self.access_count = 0
        self.hit_count = 0
    
    def test_cache_performance(self, cache_size: int = 1000) -> Dict[str, Any]:
        """Test cache hit rates and performance"""
        # Simulate cache operations
        for i in range(cache_size * 2):  # Exceed cache size to test eviction
            key = f"key_{i % cache_size}"  # Create some repeated keys
            
            self.access_count += 1
            if key in self.cache:
                self.hit_count += 1
                value = self.cache[key]
            else:
                # Simulate expensive operation
                time.sleep(0.001)  # 1ms delay
                value = f"value_{i}"
                self.cache[key] = value
                
                # Simple LRU eviction
                if len(self.cache) > cache_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
        
        hit_rate = (self.hit_count / self.access_count) * 100 if self.access_count > 0 else 0
        
        return {
            'cache_hit_rate': hit_rate,
            'total_accesses': self.access_count,
            'cache_hits': self.hit_count,
            'final_cache_size': len(self.cache)
        }

class StartupPerformanceTest:
    """Test application startup performance"""
    
    def test_import_times(self) -> Dict[str, float]:
        """Test import times for various modules"""
        import_tests = {
            'json': 'import json',
            'sqlite3': 'import sqlite3',
            'datetime': 'from datetime import datetime',
            'pathlib': 'from pathlib import Path',
        }
        
        results = {}
        
        for name, import_stmt in import_tests.items():
            start_time = time.time()
            try:
                exec(import_stmt)
                results[name] = time.time() - start_time
            except ImportError:
                results[name] = -1  # Import failed
        
        return results
    
    def test_heavy_imports(self) -> Dict[str, float]:
        """Test heavy library import times"""
        heavy_imports = {
            'pandas': 'import pandas as pd',
            'numpy': 'import numpy as np',
            'plotly': 'import plotly.graph_objects as go',
            'sklearn': 'from sklearn.ensemble import RandomForestRegressor',
        }
        
        results = {}
        
        for name, import_stmt in heavy_imports.items():
            start_time = time.time()
            try:
                exec(import_stmt)
                results[name] = time.time() - start_time
            except ImportError:
                results[name] = -1  # Not available
        
        return results

class ConcurrencyPerformanceTest:
    """Test concurrent operation performance"""
    
    async def test_async_operations(self, num_operations: int = 100) -> Dict[str, Any]:
        """Test async operation performance"""
        
        async def mock_async_operation(operation_id: int) -> int:
            """Mock async operation"""
            await asyncio.sleep(0.01)  # 10ms delay
            return operation_id * 2
        
        # Test sequential execution
        start_time = time.time()
        sequential_results = []
        for i in range(num_operations):
            result = await mock_async_operation(i)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Test concurrent execution
        start_time = time.time()
        tasks = [mock_async_operation(i) for i in range(num_operations)]
        concurrent_results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
        
        return {
            'sequential_time': sequential_time,
            'concurrent_time': concurrent_time,
            'speedup_factor': speedup,
            'operations_count': num_operations
        }

class PerformanceTestSuite:
    """Main performance test suite"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.results = {}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete performance test suite"""
        logger.info("🚀 Starting HVDC Performance Test Suite")
        
        # Test 1: Startup Performance
        logger.info("Testing startup performance...")
        startup_test = StartupPerformanceTest()
        self.results['startup'] = {
            'basic_imports': startup_test.test_import_times(),
            'heavy_imports': startup_test.test_heavy_imports()
        }
        
        # Test 2: Database Performance
        logger.info("Testing database performance...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_db:
            db_test = DatabasePerformanceTest(tmp_db.name)
            self.results['database'] = {
                'query_performance': db_test.test_query_performance(),
                'bulk_operations': db_test.test_bulk_operations()
            }
            db_test.close()
            os.unlink(tmp_db.name)
        
        # Test 3: Cache Performance
        logger.info("Testing cache performance...")
        cache_test = CachePerformanceTest()
        self.results['cache'] = cache_test.test_cache_performance()
        
        # Test 4: Memory Usage
        logger.info("Testing memory usage...")
        initial_memory = self.profiler.get_memory_usage()
        
        # Simulate memory-intensive operation
        large_data = [f"data_{i}" * 100 for i in range(10000)]
        peak_memory = self.profiler.get_memory_usage()
        
        del large_data
        gc.collect()
        final_memory = self.profiler.get_memory_usage()
        
        self.results['memory'] = {
            'initial_memory_mb': initial_memory,
            'peak_memory_mb': peak_memory,
            'final_memory_mb': final_memory,
            'memory_recovered_mb': peak_memory - final_memory
        }
        
        # Test 5: Concurrency Performance
        logger.info("Testing concurrency performance...")
        concurrency_test = ConcurrencyPerformanceTest()
        self.results['concurrency'] = asyncio.run(
            concurrency_test.test_async_operations(50)
        )
        
        # Generate summary
        self.results['summary'] = self._generate_summary()
        self.results['timestamp'] = datetime.now().isoformat()
        
        logger.info("✅ Performance test suite completed")
        return self.results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        summary = {
            'overall_score': 0,
            'recommendations': []
        }
        
        # Analyze startup performance
        basic_import_time = sum(
            t for t in self.results['startup']['basic_imports'].values() if t > 0
        )
        if basic_import_time > 0.1:
            summary['recommendations'].append("Consider optimizing basic imports")
        
        # Analyze database performance
        db_perf = self.results['database']['query_performance']
        if db_perf.get('indexed_query', 0) > 0.01:
            summary['recommendations'].append("Database queries may need optimization")
        
        # Analyze cache performance
        cache_hit_rate = self.results['cache']['cache_hit_rate']
        if cache_hit_rate < 50:
            summary['recommendations'].append("Cache hit rate is low - consider cache optimization")
        
        # Analyze memory usage
        memory_usage = self.results['memory']
        memory_recovered = memory_usage.get('memory_recovered_mb', 0)
        peak_memory = memory_usage.get('peak_memory_mb', 0)
        
        if memory_recovered / peak_memory < 0.8 if peak_memory > 0 else False:
            summary['recommendations'].append("Memory recovery could be improved")
        
        # Calculate overall score (0-100)
        score_components = []
        
        # Startup score (faster is better)
        startup_score = max(0, 100 - (basic_import_time * 1000))  # Penalize slow imports
        score_components.append(startup_score)
        
        # Database score
        db_score = max(0, 100 - (db_perf.get('indexed_query', 0) * 10000))
        score_components.append(db_score)
        
        # Cache score
        cache_score = cache_hit_rate
        score_components.append(cache_score)
        
        # Memory score
        memory_score = min(100, memory_recovered / peak_memory * 100 if peak_memory > 0 else 100)
        score_components.append(memory_score)
        
        summary['overall_score'] = sum(score_components) / len(score_components)
        
        return summary
    
    def save_results(self, filepath: str = "performance_results.json"):
        """Save test results to file"""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Performance results saved to {filepath}")
    
    def print_summary(self):
        """Print performance summary"""
        if not self.results:
            logger.error("No test results available")
            return
        
        print("\n" + "="*60)
        print("🎯 HVDC PERFORMANCE TEST RESULTS")
        print("="*60)
        
        # Startup Performance
        startup = self.results.get('startup', {})
        basic_imports = startup.get('basic_imports', {})
        heavy_imports = startup.get('heavy_imports', {})
        
        print(f"\n📚 STARTUP PERFORMANCE:")
        print(f"   Basic imports: {sum(t for t in basic_imports.values() if t > 0):.3f}s")
        for name, time_taken in basic_imports.items():
            if time_taken > 0:
                print(f"     - {name}: {time_taken:.3f}s")
        
        print(f"   Heavy imports:")
        for name, time_taken in heavy_imports.items():
            status = f"{time_taken:.3f}s" if time_taken > 0 else "Not available"
            print(f"     - {name}: {status}")
        
        # Database Performance
        db = self.results.get('database', {})
        query_perf = db.get('query_performance', {})
        bulk_ops = db.get('bulk_operations', {})
        
        print(f"\n🗄️  DATABASE PERFORMANCE:")
        for operation, time_taken in query_perf.items():
            print(f"   {operation}: {time_taken:.3f}s")
        for operation, time_taken in bulk_ops.items():
            print(f"   {operation}: {time_taken:.3f}s")
        
        # Cache Performance
        cache = self.results.get('cache', {})
        print(f"\n💾 CACHE PERFORMANCE:")
        print(f"   Hit rate: {cache.get('cache_hit_rate', 0):.1f}%")
        print(f"   Total accesses: {cache.get('total_accesses', 0):,}")
        print(f"   Cache hits: {cache.get('cache_hits', 0):,}")
        
        # Memory Usage
        memory = self.results.get('memory', {})
        print(f"\n🧠 MEMORY USAGE:")
        print(f"   Initial: {memory.get('initial_memory_mb', 0):.1f}MB")
        print(f"   Peak: {memory.get('peak_memory_mb', 0):.1f}MB")
        print(f"   Final: {memory.get('final_memory_mb', 0):.1f}MB")
        print(f"   Recovered: {memory.get('memory_recovered_mb', 0):.1f}MB")
        
        # Concurrency
        concurrency = self.results.get('concurrency', {})
        print(f"\n⚡ CONCURRENCY PERFORMANCE:")
        print(f"   Sequential time: {concurrency.get('sequential_time', 0):.3f}s")
        print(f"   Concurrent time: {concurrency.get('concurrent_time', 0):.3f}s")
        print(f"   Speedup factor: {concurrency.get('speedup_factor', 0):.1f}x")
        
        # Summary
        summary = self.results.get('summary', {})
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Performance Score: {summary.get('overall_score', 0):.1f}/100")
        
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print(f"   Recommendations:")
            for rec in recommendations:
                print(f"     - {rec}")
        else:
            print(f"   ✅ No performance issues detected")
        
        print("="*60)

def main():
    """Run performance tests"""
    test_suite = PerformanceTestSuite()
    
    try:
        results = test_suite.run_all_tests()
        test_suite.print_summary()
        test_suite.save_results()
        
        # Return exit code based on performance score
        score = results.get('summary', {}).get('overall_score', 0)
        if score >= 80:
            logger.info("🎉 Excellent performance!")
            return 0
        elif score >= 60:
            logger.warning("⚠️ Performance needs improvement")
            return 1
        else:
            logger.error("❌ Poor performance - optimization required")
            return 2
    
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        return 3

if __name__ == "__main__":
    exit(main())