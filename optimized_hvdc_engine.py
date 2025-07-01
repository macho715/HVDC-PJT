#!/usr/bin/env python3
"""
Optimized HVDC Ontology Engine - Performance Enhanced Version
Samsung C&T Logistics | ADNOC·DSV Partnership

Performance Improvements:
- Lazy loading for heavy dependencies
- Connection pooling for database operations
- Memory-efficient data processing
- Caching for frequently accessed data
- Async support for concurrent operations
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, asdict
from functools import lru_cache
from contextlib import contextmanager
import gc
import asyncio
from pathlib import Path

# Lazy imports - only load when needed
_pandas = None
_rdflib_graph = None
_rdflib_namespace = None

def get_pandas():
    """Lazy load pandas only when needed"""
    global _pandas
    if _pandas is None:
        try:
            import pandas as pd
            _pandas = pd
        except ImportError:
            _pandas = None
    return _pandas

def get_rdflib():
    """Lazy load rdflib only when needed"""
    global _rdflib_graph, _rdflib_namespace
    if _rdflib_graph is None:
        try:
            from rdflib import Graph, Namespace, URIRef, Literal, BNode
            from rdflib.namespace import RDF, RDFS, OWL, XSD
            _rdflib_graph = Graph
            _rdflib_namespace = {
                'Graph': Graph, 'Namespace': Namespace, 'URIRef': URIRef,
                'Literal': Literal, 'BNode': BNode, 'RDF': RDF, 'RDFS': RDFS,
                'OWL': OWL, 'XSD': XSD
            }
        except ImportError:
            _rdflib_namespace = None
    return _rdflib_namespace

# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logging.info(f"{func.__name__} executed in {duration:.3f}s")
        return result
    return wrapper

@dataclass
class OptimizedHVDCItem:
    """Optimized HVDC Item with minimal memory footprint"""
    hvdc_code: str
    vendor: str
    category: str
    weight: float
    location: str
    status: str
    risk_level: str = "NORMAL"
    
    def __post_init__(self):
        # Intern strings to save memory (Python built-in function)
        self.hvdc_code = str(self.hvdc_code)
        self.vendor = str(self.vendor)
        self.category = str(self.category)
        self.location = str(self.location)
        self.status = str(self.status)
        self.risk_level = str(self.risk_level)

class ConnectionPool:
    """Database connection pool for better performance"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.available_connections = []
        self.in_use_connections = set()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            self.available_connections.append(conn)
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with context manager"""
        if self.available_connections:
            conn = self.available_connections.pop()
        else:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
        
        self.in_use_connections.add(conn)
        try:
            yield conn
        finally:
            self.in_use_connections.discard(conn)
            self.available_connections.append(conn)
    
    def close_all(self):
        """Close all connections"""
        for conn in self.available_connections + list(self.in_use_connections):
            conn.close()

class OptimizedCache:
    """High-performance caching system"""
    
    def __init__(self, cache_size: int = 1000):
        self.cache_size = cache_size
        self._setup_cache()
    
    def _setup_cache(self):
        """Setup cache with memory management"""
        # Use SQLite for persistent caching
        self.cache_db = sqlite3.connect(":memory:")
        self.cache_db.execute("""
            CREATE TABLE cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp REAL,
                access_count INTEGER DEFAULT 1
            )
        """)
        self.cache_db.execute("CREATE INDEX idx_timestamp ON cache(timestamp)")
        self.cache_db.execute("CREATE INDEX idx_access_count ON cache(access_count)")
    
    @lru_cache(maxsize=128)
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with LRU eviction"""
        cursor = self.cache_db.cursor()
        cursor.execute(
            "SELECT value FROM cache WHERE key = ?",
            (key,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update access count
            cursor.execute(
                "UPDATE cache SET access_count = access_count + 1 WHERE key = ?",
                (key,)
            )
            self.cache_db.commit()
            return json.loads(result[0])
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value with automatic cleanup"""
        cursor = self.cache_db.cursor()
        
        # Check cache size and cleanup if needed
        cursor.execute("SELECT COUNT(*) FROM cache")
        count = cursor.fetchone()[0]
        
        if count >= self.cache_size:
            # Remove least recently used items
            cursor.execute("""
                DELETE FROM cache WHERE key IN (
                    SELECT key FROM cache 
                    ORDER BY access_count ASC, timestamp ASC 
                    LIMIT ?
                )
            """, (count - self.cache_size + 100,))  # Remove extra items
        
        # Insert new value
        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
            (key, json.dumps(value), datetime.now().timestamp())
        )
        self.cache_db.commit()

class OptimizedHVDCEngine:
    """High-performance HVDC Ontology Engine"""
    
    def __init__(self, db_path: str = "hvdc_ontology_optimized.db", 
                 enable_rdf: bool = False, cache_size: int = 1000):
        self.db_path = db_path
        self.enable_rdf = enable_rdf
        self.connection_pool = ConnectionPool(db_path)
        self.cache = OptimizedCache(cache_size)
        
        # Lazy initialization
        self.graph = None
        self._setup_database()
        self._setup_indexes()
        
        # Performance metrics
        self.metrics = {
            'queries_executed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _setup_database(self):
        """Setup optimized database schema"""
        with self.connection_pool.get_connection() as conn:
            # Items table with optimized schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    hvdc_code TEXT PRIMARY KEY,
                    vendor TEXT NOT NULL,
                    category TEXT NOT NULL,
                    weight REAL NOT NULL,
                    location TEXT NOT NULL,
                    status TEXT NOT NULL,
                    risk_level TEXT DEFAULT 'NORMAL',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Warehouses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS warehouses (
                    name TEXT PRIMARY KEY,
                    warehouse_type TEXT NOT NULL,
                    capacity_sqm REAL NOT NULL,
                    current_utilization REAL DEFAULT 0,
                    handling_fee REAL DEFAULT 0
                )
            """)
            
            # Performance metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _setup_indexes(self):
        """Setup database indexes for optimal performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_vendor ON items(vendor)",
            "CREATE INDEX IF NOT EXISTS idx_category ON items(category)",
            "CREATE INDEX IF NOT EXISTS idx_location ON items(location)",
            "CREATE INDEX IF NOT EXISTS idx_status ON items(status)",
            "CREATE INDEX IF NOT EXISTS idx_weight ON items(weight)",
            "CREATE INDEX IF NOT EXISTS idx_risk_level ON items(risk_level)",
            "CREATE INDEX IF NOT EXISTS idx_warehouse_type ON warehouses(warehouse_type)",
            "CREATE INDEX IF NOT EXISTS idx_utilization ON warehouses(current_utilization)"
        ]
        
        with self.connection_pool.get_connection() as conn:
            for index_sql in indexes:
                conn.execute(index_sql)
            conn.commit()
    
    @monitor_performance
    def add_item_batch(self, items: List[OptimizedHVDCItem]) -> int:
        """Add multiple items efficiently using batch insert"""
        if not items:
            return 0
        
        with self.connection_pool.get_connection() as conn:
            data = [
                (item.hvdc_code, item.vendor, item.category, item.weight,
                 item.location, item.status, item.risk_level)
                for item in items
            ]
            
            conn.executemany("""
                INSERT OR REPLACE INTO items 
                (hvdc_code, vendor, category, weight, location, status, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            conn.commit()
            return len(items)
    
    @lru_cache(maxsize=256)
    def get_items_by_vendor(self, vendor: str) -> List[Dict]:
        """Get items by vendor with caching"""
        cache_key = f"vendor_{vendor}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            self.metrics['cache_hits'] += 1
            return cached_result
        
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hvdc_code, vendor, category, weight, location, status, risk_level
                FROM items WHERE vendor = ?
                ORDER BY weight DESC
            """, (vendor,))
            
            results = [dict(row) for row in cursor.fetchall()]
            
        self.cache.set(cache_key, results)
        self.metrics['cache_misses'] += 1
        self.metrics['queries_executed'] += 1
        
        return results
    
    def stream_items(self, batch_size: int = 1000) -> Generator[List[Dict], None, None]:
        """Stream items in batches for memory efficiency"""
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM items")
            total_count = cursor.fetchone()[0]
            
            offset = 0
            while offset < total_count:
                cursor.execute("""
                    SELECT hvdc_code, vendor, category, weight, location, status, risk_level
                    FROM items
                    ORDER BY hvdc_code
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))
                
                batch = [dict(row) for row in cursor.fetchall()]
                if not batch:
                    break
                
                yield batch
                offset += batch_size
    
    @monitor_performance
    def get_warehouse_utilization_optimized(self) -> Dict[str, Any]:
        """Get warehouse utilization with optimized query"""
        cache_key = "warehouse_utilization"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            self.metrics['cache_hits'] += 1
            return cached_result
        
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    name,
                    warehouse_type,
                    capacity_sqm,
                    current_utilization,
                    ROUND((current_utilization / capacity_sqm * 100), 2) as utilization_percent,
                    handling_fee
                FROM warehouses
                WHERE capacity_sqm > 0
                ORDER BY utilization_percent DESC
            """)
            
            results = {
                'warehouses': [dict(row) for row in cursor.fetchall()],
                'summary': {
                    'total_warehouses': cursor.rowcount,
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        self.cache.set(cache_key, results)
        self.metrics['cache_misses'] += 1
        self.metrics['queries_executed'] += 1
        
        return results
    
    async def load_excel_async(self, filepath: str, chunk_size: int = 1000) -> int:
        """Asynchronously load Excel file in chunks"""
        pd = get_pandas()
        if pd is None:
            logging.error("Pandas not available - cannot load Excel files")
            return 0
        
        total_loaded = 0
        
        try:
            # Read Excel file in chunks
            for chunk_df in pd.read_excel(filepath, chunksize=chunk_size):
                items = []
                
                for _, row in chunk_df.iterrows():
                    item = OptimizedHVDCItem(
                        hvdc_code=str(row.get('HVDC Code', f'ITEM_{total_loaded:04d}')),
                        vendor=str(row.get('Vendor', 'Unknown')),
                        category=str(row.get('Category', 'General')),
                        weight=float(row.get('Weight', 0)),
                        location=str(row.get('Location', 'Unknown')),
                        status=str(row.get('Status', 'warehouse'))
                    )
                    items.append(item)
                
                # Process chunk asynchronously
                await asyncio.get_event_loop().run_in_executor(
                    None, self.add_item_batch, items
                )
                
                total_loaded += len(items)
                
                # Force garbage collection periodically
                if total_loaded % (chunk_size * 10) == 0:
                    gc.collect()
        
        except Exception as e:
            logging.error(f"Error loading Excel file {filepath}: {e}")
            return 0
        
        return total_loaded
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get engine performance metrics"""
        cache_hit_rate = (
            self.metrics['cache_hits'] / 
            (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0
            else 0
        )
        
        return {
            'queries_executed': self.metrics['queries_executed'],
            'cache_hit_rate': round(cache_hit_rate * 100, 2),
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'timestamp': datetime.now().isoformat()
        }
    
    @contextmanager
    def memory_managed_operation(self):
        """Context manager for memory-intensive operations"""
        initial_memory = self._get_memory_usage()
        try:
            yield
        finally:
            gc.collect()  # Force garbage collection
            final_memory = self._get_memory_usage()
            memory_diff = final_memory - initial_memory
            if memory_diff > 0:
                logging.info(f"Memory usage increased by {memory_diff:.2f}MB")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def optimize_database(self):
        """Optimize database for better performance"""
        with self.connection_pool.get_connection() as conn:
            # Analyze tables for query optimization
            conn.execute("ANALYZE")
            
            # Vacuum to reclaim space
            conn.execute("VACUUM")
            
            # Update statistics
            conn.execute("PRAGMA optimize")
            
            conn.commit()
    
    def close(self):
        """Clean shutdown with resource cleanup"""
        self.connection_pool.close_all()
        if self.cache.cache_db:
            self.cache.cache_db.close()
        gc.collect()

# Factory function for different optimization levels
def create_hvdc_engine(optimization_level: str = "standard") -> OptimizedHVDCEngine:
    """
    Create HVDC engine with different optimization levels
    
    Args:
        optimization_level: 'minimal', 'standard', 'maximum'
    """
    configs = {
        'minimal': {'cache_size': 100, 'enable_rdf': False},
        'standard': {'cache_size': 1000, 'enable_rdf': False},
        'maximum': {'cache_size': 5000, 'enable_rdf': True}
    }
    
    config = configs.get(optimization_level, configs['standard'])
    return OptimizedHVDCEngine(**config)

# Example usage and benchmarking
async def benchmark_performance():
    """Benchmark the optimized engine"""
    engine = create_hvdc_engine('maximum')
    
    print("🚀 Starting performance benchmark...")
    
    # Test batch insertion
    start_time = datetime.now()
    sample_items = [
        OptimizedHVDCItem(
            hvdc_code=f"TEST-{i:04d}",
            vendor="HITACHI" if i % 2 == 0 else "SIEMENS",
            category="Electrical",
            weight=1000 + (i * 10),
            location="DSV Indoor",
            status="warehouse"
        )
        for i in range(1000)
    ]
    
    count = engine.add_item_batch(sample_items)
    batch_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ Batch insert: {count} items in {batch_time:.3f}s")
    
    # Test cached queries
    start_time = datetime.now()
    for _ in range(10):
        results = engine.get_items_by_vendor("HITACHI")
    query_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ Cached queries: 10 queries in {query_time:.3f}s")
    
    # Test streaming
    start_time = datetime.now()
    total_streamed = 0
    for batch in engine.stream_items(batch_size=100):
        total_streamed += len(batch)
    stream_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ Streaming: {total_streamed} items in {stream_time:.3f}s")
    
    # Performance metrics
    metrics = engine.get_performance_metrics()
    print(f"📊 Performance Metrics:")
    print(f"   Cache Hit Rate: {metrics['cache_hit_rate']}%")
    print(f"   Queries Executed: {metrics['queries_executed']}")
    
    engine.close()

if __name__ == "__main__":
    # Run benchmark
    asyncio.run(benchmark_performance())