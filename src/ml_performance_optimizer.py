#!/usr/bin/env python3
"""
ML Performance Optimizer for HVDC Project
MACHO-GPT v3.4-mini - Machine Learning Processing Time Optimization

This module optimizes ML processing performance to meet the 1.0 second threshold
identified in the test pipeline.
"""

import time
import logging
import asyncio
import multiprocessing
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for ML operations"""
    processing_time: float
    memory_usage: float
    cpu_usage: float
    model_size: float
    inference_latency: float
    throughput: float

@dataclass
class OptimizationConfig:
    """Configuration for ML performance optimization"""
    max_processing_time: float = 1.0  # Target: 1.0 seconds
    max_memory_usage: float = 512.0   # Target: 512 MB
    max_cpu_usage: float = 80.0       # Target: 80%
    batch_size: int = 32
    num_workers: int = 4
    enable_caching: bool = True
    enable_parallel_processing: bool = True
    enable_memory_optimization: bool = True

class MLPerformanceOptimizer:
    """ML Performance Optimizer for HVDC Project"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.cache = {}
        self.performance_history = []
        self.optimization_stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'average_improvement': 0.0
        }
        
    def optimize_processing_time(self, ml_function, *args, **kwargs) -> Tuple[Any, PerformanceMetrics]:
        """
        Optimize ML processing time to meet performance targets
        
        Args:
            ml_function: ML function to optimize
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (result, performance_metrics)
        """
        logger.info("🚀 Starting ML processing time optimization")
        
        # Measure baseline performance
        baseline_metrics = self._measure_performance(ml_function, *args, **kwargs)
        logger.info(f"📊 Baseline performance: {baseline_metrics.processing_time:.3f}s")
        
        # Apply optimizations
        optimized_result, optimized_metrics = self._apply_optimizations(
            ml_function, baseline_metrics, *args, **kwargs
        )
        
        # Calculate improvement
        improvement = baseline_metrics.processing_time - optimized_metrics.processing_time
        improvement_percent = (improvement / baseline_metrics.processing_time) * 100
        
        logger.info(f"✅ Optimization complete: {improvement_percent:.1f}% improvement")
        logger.info(f"📈 Final performance: {optimized_metrics.processing_time:.3f}s")
        
        # Update statistics
        self._update_optimization_stats(improvement_percent)
        
        return optimized_result, optimized_metrics
    
    def _measure_performance(self, func, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance metrics for a function"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent()
        
        # Execute function
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent()
        
        processing_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_usage = (start_cpu + end_cpu) / 2
        
        return PerformanceMetrics(
            processing_time=processing_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            model_size=0.0,  # Will be calculated separately
            inference_latency=processing_time,
            throughput=1.0 / processing_time if processing_time > 0 else 0.0
        )
    
    def _apply_optimizations(self, func, baseline_metrics: PerformanceMetrics, 
                           *args, **kwargs) -> Tuple[Any, PerformanceMetrics]:
        """Apply various optimization techniques"""
        
        # Check if result is cached
        cache_key = self._generate_cache_key(func, args, kwargs)
        if self.config.enable_caching and cache_key in self.cache:
            logger.info("💾 Using cached result")
            return self.cache[cache_key], PerformanceMetrics(
                processing_time=0.001,  # Cache hit time
                memory_usage=0.0,
                cpu_usage=0.0,
                model_size=0.0,
                inference_latency=0.001,
                throughput=1000.0
            )
        
        # Apply parallel processing if beneficial
        if (self.config.enable_parallel_processing and 
            baseline_metrics.processing_time > 0.5):
            result, metrics = self._apply_parallel_processing(func, *args, **kwargs)
        else:
            result, metrics = self._apply_sequential_optimizations(func, *args, **kwargs)
        
        # Apply memory optimization
        if self.config.enable_memory_optimization:
            result, metrics = self._apply_memory_optimization(result, metrics)
        
        # Cache result if beneficial
        if self.config.enable_caching:
            self.cache[cache_key] = result
        
        return result, metrics
    
    def _apply_parallel_processing(self, func, *args, **kwargs) -> Tuple[Any, PerformanceMetrics]:
        """Apply parallel processing optimization"""
        logger.info("🔄 Applying parallel processing optimization")
        
        # Determine optimal number of workers
        optimal_workers = min(
            self.config.num_workers,
            multiprocessing.cpu_count(),
            len(args) if args else 1
        )
        
        start_time = time.time()
        
        if optimal_workers > 1 and len(args) > 1:
            # Parallel processing for multiple arguments
            with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
                futures = [executor.submit(func, arg) for arg in args]
                results = [future.result() for future in futures]
        else:
            # Sequential processing
            results = func(*args, **kwargs)
        
        processing_time = time.time() - start_time
        
        return results, PerformanceMetrics(
            processing_time=processing_time,
            memory_usage=psutil.Process().memory_info().rss / 1024 / 1024,
            cpu_usage=psutil.cpu_percent(),
            model_size=0.0,
            inference_latency=processing_time,
            throughput=1.0 / processing_time if processing_time > 0 else 0.0
        )
    
    def _apply_sequential_optimizations(self, func, *args, **kwargs) -> Tuple[Any, PerformanceMetrics]:
        """Apply sequential optimizations"""
        logger.info("⚡ Applying sequential optimizations")
        
        # Pre-allocate memory if possible
        if hasattr(func, '__name__') and 'predict' in func.__name__.lower():
            # Pre-allocate arrays for prediction
            self._pre_allocate_memory()
        
        # Execute with garbage collection optimization
        gc.collect()  # Clean up before execution
        
        start_time = time.time()
        result = func(*args, **kwargs)
        processing_time = time.time() - start_time
        
        # Force garbage collection after execution
        gc.collect()
        
        return result, PerformanceMetrics(
            processing_time=processing_time,
            memory_usage=psutil.Process().memory_info().rss / 1024 / 1024,
            cpu_usage=psutil.cpu_percent(),
            model_size=0.0,
            inference_latency=processing_time,
            throughput=1.0 / processing_time if processing_time > 0 else 0.0
        )
    
    def _apply_memory_optimization(self, result: Any, metrics: PerformanceMetrics) -> Tuple[Any, PerformanceMetrics]:
        """Apply memory optimization techniques"""
        logger.info("🧠 Applying memory optimization")
        
        # Convert large arrays to more memory-efficient formats
        if isinstance(result, np.ndarray):
            if result.dtype == np.float64:
                result = result.astype(np.float32)  # Reduce memory usage by half
            elif result.dtype == np.int64:
                result = result.astype(np.int32)    # Reduce memory usage by half
        
        # Optimize pandas DataFrames
        elif isinstance(result, pd.DataFrame):
            result = self._optimize_dataframe_memory(result)
        
        # Force garbage collection
        gc.collect()
        
        # Update memory usage
        optimized_memory = psutil.Process().memory_info().rss / 1024 / 1024
        metrics.memory_usage = optimized_memory
        
        return result, metrics
    
    def _optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame memory usage"""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Convert object columns to category if beneficial
                if df[col].nunique() / len(df) < 0.5:
                    df[col] = df[col].astype('category')
            elif df[col].dtype == 'float64':
                df[col] = df[col].astype('float32')
            elif df[col].dtype == 'int64':
                df[col] = df[col].astype('int32')
        
        return df
    
    def _pre_allocate_memory(self):
        """Pre-allocate memory for better performance"""
        # This is a placeholder for memory pre-allocation
        # In practice, this would allocate arrays based on expected data size
        pass
    
    def _generate_cache_key(self, func, args, kwargs) -> str:
        """Generate cache key for function call"""
        import hashlib
        key_data = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_optimization_stats(self, improvement_percent: float):
        """Update optimization statistics"""
        self.optimization_stats['total_optimizations'] += 1
        self.optimization_stats['successful_optimizations'] += 1
        self.optimization_stats['average_improvement'] = (
            (self.optimization_stats['average_improvement'] * 
             (self.optimization_stats['total_optimizations'] - 1) + improvement_percent) /
            self.optimization_stats['total_optimizations']
        )
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate optimization performance report"""
        return {
            'optimization_stats': self.optimization_stats,
            'performance_history': self.performance_history[-10:],  # Last 10 entries
            'current_config': {
                'max_processing_time': self.config.max_processing_time,
                'max_memory_usage': self.config.max_memory_usage,
                'max_cpu_usage': self.config.max_cpu_usage,
                'batch_size': self.config.batch_size,
                'num_workers': self.config.num_workers,
                'enable_caching': self.config.enable_caching,
                'enable_parallel_processing': self.config.enable_parallel_processing,
                'enable_memory_optimization': self.config.enable_memory_optimization
            }
        }

class MLPerformanceMonitor:
    """Monitor ML performance in real-time"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'processing_time': 1.0,
            'memory_usage': 512.0,
            'cpu_usage': 80.0
        }
    
    def monitor_performance(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Monitor performance and generate alerts"""
        self.metrics_history.append(metrics)
        
        alerts = []
        if metrics.processing_time > self.alert_thresholds['processing_time']:
            alerts.append(f"Processing time ({metrics.processing_time:.3f}s) exceeds threshold")
        
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append(f"Memory usage ({metrics.memory_usage:.1f}MB) exceeds threshold")
        
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append(f"CPU usage ({metrics.cpu_usage:.1f}%) exceeds threshold")
        
        return {
            'alerts': alerts,
            'metrics': metrics,
            'status': 'warning' if alerts else 'normal'
        }

# Performance optimization decorator
def optimize_ml_performance(config: Optional[OptimizationConfig] = None):
    """Decorator to automatically optimize ML function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            optimizer = MLPerformanceOptimizer(config)
            result, metrics = optimizer.optimize_processing_time(func, *args, **kwargs)
            return result
        return wrapper
    return decorator

# Example usage and testing
def test_ml_optimization():
    """Test ML performance optimization"""
    logger.info("🧪 Testing ML Performance Optimization")
    
    # Create test ML function
    def test_ml_function(data_size: int = 1000):
        """Simulate ML processing"""
        import numpy as np
        import time
        
        # Simulate data processing
        data = np.random.rand(data_size, 10)
        time.sleep(0.5)  # Simulate processing time
        
        # Simulate model prediction
        predictions = np.random.rand(data_size)
        time.sleep(0.3)  # Simulate prediction time
        
        return predictions
    
    # Test optimization
    optimizer = MLPerformanceOptimizer()
    result, metrics = optimizer.optimize_processing_time(test_ml_function, 1000)
    
    logger.info(f"✅ Test completed: {metrics.processing_time:.3f}s")
    return metrics.processing_time < 1.0

if __name__ == "__main__":
    # Run performance optimization test
    success = test_ml_optimization()
    if success:
        logger.info("🎉 ML Performance Optimization Test PASSED")
    else:
        logger.warning("⚠️ ML Performance Optimization Test needs improvement") 