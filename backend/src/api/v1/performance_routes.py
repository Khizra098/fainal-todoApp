"""
Performance API endpoints for the verification system.
This module provides endpoints for performance benchmarking and metrics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime, timedelta
import time
import psutil
import os

from ...database.database import get_db
from ...models.performance_benchmark import PerformanceBenchmark, PerformanceMetricType, PerformanceStatus
from ...models.user import User
from ...middleware.auth import get_current_user
from ...utils.logging import get_logger


router = APIRouter(prefix="/performance", tags=["performance"])
logger = get_logger(__name__)


@router.get("/benchmarks", summary="Get Performance Benchmarks")
async def get_performance_benchmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve performance benchmark results.

    Args:
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: List of performance benchmarks
    """
    try:
        # Query all active performance benchmarks
        benchmarks = db.query(PerformanceBenchmark)\
            .filter(PerformanceBenchmark.is_active == True)\
            .order_by(PerformanceBenchmark.created_at.desc())\
            .all()

        benchmarks_list = []
        for benchmark in benchmarks:
            benchmark_dict = benchmark.to_dict()

            # Add computed status based on current vs target values
            if benchmark.metric_type == "response_time":
                # Lower is better for response time
                if benchmark.current_value <= benchmark.target_value:
                    benchmark_dict["status"] = "pass"
                elif benchmark.current_value <= benchmark.target_value * 1.2:
                    benchmark_dict["status"] = "warn"
                else:
                    benchmark_dict["status"] = "fail"
            elif benchmark.metric_type in ["throughput", "cache_hit_rate"]:
                # Higher is better for throughput and cache hit rate
                if benchmark.current_value >= benchmark.target_value:
                    benchmark_dict["status"] = "pass"
                elif benchmark.current_value >= benchmark.target_value * 0.8:
                    benchmark_dict["status"] = "warn"
                else:
                    benchmark_dict["status"] = "fail"
            else:
                # For other metrics, use the stored status
                benchmark_dict["status"] = benchmark.status

            benchmarks_list.append(benchmark_dict)

        logger.info(f"Retrieved {len(benchmarks_list)} performance benchmarks for user {current_user.id}")

        return {
            "benchmarks": benchmarks_list
        }

    except Exception as e:
        logger.error(f"Error retrieving performance benchmarks: {str(e)}")
        raise


@router.get("/current-metrics", summary="Get Current System Metrics")
async def get_current_metrics(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve current system performance metrics.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Current system metrics
    """
    try:
        # Get system metrics using psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')

        # Get process-specific metrics
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info().rss / 1024 / 1024  # MB
        process_cpu = process.cpu_percent()

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "memory_available_mb": memory_info.available / 1024 / 1024,
                "disk_percent": disk_usage.percent,
                "disk_free_gb": disk_usage.free / 1024 / 1024 / 1024,
            },
            "process": {
                "memory_mb": round(process_memory, 2),
                "cpu_percent": process_cpu,
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if os.name != 'nt' else None  # Not available on Windows
            },
            "application": {
                "uptime_seconds": time.time(),  # Would be actual uptime in real system
                "active_connections": 0,  # Would be actual connection count
                "requests_per_second": 0  # Would be actual request rate
            }
        }

        logger.debug(f"Retrieved current metrics for user {current_user.id}")

        return {
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Error retrieving current metrics: {str(e)}")
        raise


@router.get("/benchmark/{test_name}", summary="Get Specific Benchmark")
async def get_specific_benchmark(
    test_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve a specific performance benchmark by test name.

    Args:
        test_name: Name of the test to retrieve
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Specific benchmark information
    """
    try:
        # Find the most recent benchmark with the given test name
        benchmark = db.query(PerformanceBenchmark)\
            .filter(
                PerformanceBenchmark.test_name == test_name,
                PerformanceBenchmark.is_active == True
            )\
            .order_by(PerformanceBenchmark.created_at.desc())\
            .first()

        if not benchmark:
            return {
                "benchmark": None,
                "message": f"No benchmark found for test name: {test_name}"
            }

        benchmark_dict = benchmark.to_dict()

        # Add computed status based on current vs target values
        if benchmark.metric_type == "response_time":
            # Lower is better for response time
            if benchmark.current_value <= benchmark.target_value:
                benchmark_dict["status"] = "pass"
            elif benchmark.current_value <= benchmark.target_value * 1.2:
                benchmark_dict["status"] = "warn"
            else:
                benchmark_dict["status"] = "fail"
        elif benchmark.metric_type in ["throughput", "cache_hit_rate"]:
            # Higher is better for throughput and cache hit rate
            if benchmark.current_value >= benchmark.target_value:
                benchmark_dict["status"] = "pass"
            elif benchmark.current_value >= benchmark.target_value * 0.8:
                benchmark_dict["status"] = "warn"
            else:
                benchmark_dict["status"] = "fail"
        else:
            # For other metrics, use the stored status
            benchmark_dict["status"] = benchmark.status

        logger.info(f"Retrieved benchmark for {test_name} by user {current_user.id}")

        return {
            "benchmark": benchmark_dict
        }

    except Exception as e:
        logger.error(f"Error retrieving specific benchmark: {str(e)}")
        raise


@router.post("/run-benchmark/{test_name}", summary="Run Performance Benchmark")
async def run_performance_benchmark(
    test_name: str,
    benchmark_params: dict,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Run a performance benchmark test.

    Args:
        test_name: Name of the test to run
        benchmark_params: Parameters for the benchmark
        current_user: Current authenticated user

    Returns:
        dict: Benchmark results
    """
    try:
        # In a real implementation, this would run actual performance tests
        # For now, we'll simulate benchmark results

        start_time = time.time()

        # Simulate different types of benchmarks based on test_name
        if test_name == "api-response-time":
            # Simulate API response time test
            import random
            response_times = [random.uniform(50, 500) for _ in range(10)]  # 10 sample requests
            avg_response_time = sum(response_times) / len(response_times)

            result = {
                "test_name": test_name,
                "metric_type": "response_time",
                "current_value": round(avg_response_time, 2),
                "unit": "ms",
                "samples": len(response_times),
                "min_response_time": round(min(response_times), 2),
                "max_response_time": round(max(response_times), 2),
                "p95_response_time": round(sorted(response_times)[int(0.95 * len(response_times))], 2),
                "target_value": benchmark_params.get("target_value", 200.0),
                "status": "pass" if avg_response_time <= benchmark_params.get("target_value", 200.0) else "fail"
            }
        elif test_name == "database-query-performance":
            # Simulate database query performance test
            import random
            query_times = [random.uniform(10, 100) for _ in range(5)]
            avg_query_time = sum(query_times) / len(query_times)

            result = {
                "test_name": test_name,
                "metric_type": "database_query_time",
                "current_value": round(avg_query_time, 2),
                "unit": "ms",
                "samples": len(query_times),
                "min_query_time": round(min(query_times), 2),
                "max_query_time": round(max(query_times), 2),
                "target_value": benchmark_params.get("target_value", 50.0),
                "status": "pass" if avg_query_time <= benchmark_params.get("target_value", 50.0) else "fail"
            }
        else:
            # Generic benchmark simulation
            result = {
                "test_name": test_name,
                "metric_type": benchmark_params.get("metric_type", "custom"),
                "current_value": benchmark_params.get("current_value", 0.0),
                "unit": benchmark_params.get("unit", ""),
                "samples": benchmark_params.get("samples", 1),
                "target_value": benchmark_params.get("target_value", 1.0),
                "status": "pass"  # Default to pass for simulated test
            }

        execution_time = round(time.time() - start_time, 3)
        result["execution_time_seconds"] = execution_time

        logger.info(f"Ran performance benchmark {test_name} by user {current_user.id}")

        return {
            "result": result
        }

    except Exception as e:
        logger.error(f"Error running performance benchmark: {str(e)}")
        raise


@router.get("/trends", summary="Get Performance Trends")
async def get_performance_trends(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Retrieve performance trends over time.

    Args:
        days: Number of days to look back
        db: Database session dependency
        current_user: Current authenticated user

    Returns:
        dict: Performance trend data
    """
    try:
        # Calculate date range
        from_date = datetime.utcnow() - timedelta(days=days)

        # Get benchmarks from the last N days
        benchmarks = db.query(PerformanceBenchmark)\
            .filter(
                PerformanceBenchmark.created_at >= from_date,
                PerformanceBenchmark.is_active == True
            )\
            .order_by(PerformanceBenchmark.created_at)\
            .all()

        # Group benchmarks by test name
        trends = {}
        for benchmark in benchmarks:
            test_name = benchmark.test_name
            if test_name not in trends:
                trends[test_name] = {
                    "test_name": test_name,
                    "metric_type": benchmark.metric_type,
                    "unit": benchmark.unit,
                    "data_points": []
                }

            trends[test_name]["data_points"].append({
                "timestamp": benchmark.created_at.isoformat(),
                "value": benchmark.current_value,
                "status": benchmark.status
            })

        # Convert to list format
        trends_list = list(trends.values())

        logger.info(f"Retrieved performance trends for last {days} days by user {current_user.id}")

        return {
            "trends": trends_list,
            "days_lookback": days
        }

    except Exception as e:
        logger.error(f"Error retrieving performance trends: {str(e)}")
        raise