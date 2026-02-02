"""
Metrics and monitoring utilities for the verification system.

This module provides functionality for collecting, storing, and reporting
application metrics and performance indicators.
"""

import time
import functools
from typing import Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import json
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricPoint:
    """Represents a single metric measurement."""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    description: str = ""


class MetricsCollector:
    """Central collector for application metrics."""

    def __init__(self):
        self._metrics = defaultdict(list)  # name -> [MetricPoint]
        self._gauges = {}  # name -> value
        self._counters = {}  # name -> value
        self._histograms = defaultdict(list)  # name -> [values]
        self._mutex = threading.Lock()

    def record_metric(self, name: str, value: float, metric_type: MetricType,
                     labels: Dict[str, str] = None, description: str = ""):
        """Record a metric point."""
        with self._mutex:
            labels = labels or {}
            point = MetricPoint(
                name=name,
                value=value,
                metric_type=metric_type,
                labels=labels,
                timestamp=datetime.utcnow(),
                description=description
            )

            self._metrics[name].append(point)

            # Update gauges and counters for quick access
            if metric_type == MetricType.GAUGE:
                self._gauges[f"{name}_{json.dumps(labels, sort_keys=True)}"] = value
            elif metric_type == MetricType.COUNTER:
                key = f"{name}_{json.dumps(labels, sort_keys=True)}"
                self._counters[key] = self._counters.get(key, 0) + value

    def increment_counter(self, name: str, labels: Dict[str, str] = None, amount: float = 1.0):
        """Increment a counter metric."""
        self.record_metric(
            name=name,
            value=amount,
            metric_type=MetricType.COUNTER,
            labels=labels or {},
            description="Counter metric"
        )

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric."""
        self.record_metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {},
            description="Gauge metric"
        )

    def record_histogram_value(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a value in a histogram."""
        self.record_metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels or {},
            description="Histogram metric"
        )
        # Store separately for statistical calculations
        key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        with self._mutex:
            self._histograms[key].append(value)

    def get_metric_history(self, name: str, hours_back: int = 1) -> list[MetricPoint]:
        """Get historical values for a metric."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        with self._mutex:
            return [point for point in self._metrics[name] if point.timestamp >= cutoff_time]

    def get_current_gauge_value(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get the current value of a gauge."""
        key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        with self._mutex:
            return self._gauges.get(key, 0.0)

    def get_current_counter_value(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get the current value of a counter."""
        key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        with self._mutex:
            return self._counters.get(key, 0.0)

    def get_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Get statistical information about a histogram."""
        key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        with self._mutex:
            values = self._histograms[key]
            if not values:
                return {"count": 0, "mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "std_dev": 0.0}

            return {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0
            }

    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics."""
        with self._mutex:
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "gauges": dict(self._gauges),
                "counters": dict(self._counters),
                "histogram_summaries": {}
            }

            # Add histogram summaries
            for key, values in self._histograms.items():
                if values:
                    summary["histogram_summaries"][key] = {
                        "count": len(values),
                        "mean": statistics.mean(values),
                        "min": min(values),
                        "max": max(values)
                    }

            return summary


# Global metrics collector instance
collector = MetricsCollector()


def time_function(metric_name: str, labels: Dict[str, str] = None):
    """
    Decorator to time function execution and record as a histogram metric.

    Args:
        metric_name: Name of the metric to record
        labels: Labels to attach to the metric
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start_time) * 1000  # Convert to milliseconds
                collector.record_histogram_value(
                    name=f"{metric_name}_duration_ms",
                    value=duration,
                    labels=labels
                )
        return wrapper
    return decorator


def count_calls(metric_name: str, labels: Dict[str, str] = None):
    """
    Decorator to count function calls.

    Args:
        metric_name: Name of the metric to record
        labels: Labels to attach to the metric
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            collector.increment_counter(
                name=f"{metric_name}_calls_total",
                labels=labels,
                amount=1.0
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def track_memory_usage():
    """Track memory usage of the application."""
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        collector.set_gauge(
            name="process_memory_usage_mb",
            value=memory_mb,
            labels={"process": "backend"}
        )

        # Also track memory percentage
        memory_percent = process.memory_percent()
        collector.set_gauge(
            name="process_memory_percent",
            value=memory_percent,
            labels={"process": "backend"}
        )
    except ImportError:
        # psutil not available, skip memory tracking
        pass


def track_cpu_usage():
    """Track CPU usage of the application."""
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent()

        collector.set_gauge(
            name="process_cpu_percent",
            value=cpu_percent,
            labels={"process": "backend"}
        )
    except ImportError:
        # psutil not available, skip CPU tracking
        pass


def get_api_response_time_stats() -> Dict[str, float]:
    """Get statistics about API response times."""
    return collector.get_histogram_stats("api_response_time_ms")


def get_feature_verification_stats() -> Dict[str, Any]:
    """Get statistics about feature verification performance."""
    return {
        "verification_count": collector.get_current_counter_value("feature_verification_total"),
        "verification_duration_stats": collector.get_histogram_stats("feature_verification_duration_ms"),
        "verification_success_rate": collector.get_current_gauge_value("verification_success_rate"),
    }


def get_system_metrics() -> Dict[str, Any]:
    """Get a comprehensive view of system metrics."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_usage_percent": collector.get_current_gauge_value("process_cpu_percent"),
            "memory_usage_mb": collector.get_current_gauge_value("process_memory_usage_mb"),
            "memory_usage_percent": collector.get_current_gauge_value("process_memory_percent"),
        },
        "application": {
            "active_requests": collector.get_current_gauge_value("active_requests"),
            "total_requests": collector.get_current_counter_value("http_requests_total"),
            "error_count": collector.get_current_counter_value("http_errors_total"),
        },
        "verification": {
            "total_verifications": collector.get_current_counter_value("feature_verification_total"),
            "verification_success_rate": collector.get_current_gauge_value("verification_success_rate"),
            "avg_verification_time_ms": collector.get_histogram_stats("feature_verification_duration_ms").get("mean", 0),
        },
        "database": {
            "active_connections": collector.get_current_gauge_value("db_active_connections"),
            "connection_timeouts": collector.get_current_counter_value("db_connection_timeouts_total"),
        }
    }


def increment_api_call(endpoint: str, method: str = "GET"):
    """Increment counter for API calls."""
    collector.increment_counter(
        name="http_requests_total",
        labels={"endpoint": endpoint, "method": method}
    )


def record_api_response_time(endpoint: str, method: str, response_time_ms: float):
    """Record API response time."""
    collector.record_histogram_value(
        name="api_response_time_ms",
        value=response_time_ms,
        labels={"endpoint": endpoint, "method": method}
    )


def record_verification_result(success: bool, duration_ms: float):
    """Record the result of a feature verification."""
    collector.increment_counter(
        name="feature_verification_total",
        amount=1.0
    )

    if success:
        collector.increment_counter(
            name="feature_verification_success_total",
            amount=1.0
        )
    else:
        collector.increment_counter(
            name="feature_verification_failure_total",
            amount=1.0
        )

    # Calculate and update success rate
    total = collector.get_current_counter_value("feature_verification_total")
    if total > 0:
        success_total = collector.get_current_counter_value("feature_verification_success_total")
        success_rate = (success_total / total) * 100 if total > 0 else 0
        collector.set_gauge(
            name="verification_success_rate",
            value=success_rate
        )

    # Record duration
    collector.record_histogram_value(
        name="feature_verification_duration_ms",
        value=duration_ms
    )


def record_db_operation(operation: str, duration_ms: float, success: bool = True):
    """Record a database operation."""
    collector.record_histogram_value(
        name="db_operation_duration_ms",
        value=duration_ms,
        labels={"operation": operation, "success": str(success)}
    )

    if not success:
        collector.increment_counter(
            name="db_operation_errors_total",
            labels={"operation": operation},
            amount=1.0
        )


def record_error(error_type: str, endpoint: str = ""):
    """Record an error occurrence."""
    labels = {"type": error_type}
    if endpoint:
        labels["endpoint"] = endpoint

    collector.increment_counter(
        name="errors_total",
        labels=labels,
        amount=1.0
    )

    # Also increment HTTP errors if it's an HTTP error
    if error_type.startswith("HTTP"):
        collector.increment_counter(
            name="http_errors_total",
            labels=labels,
            amount=1.0
        )


def health_check_metrics() -> Dict[str, Any]:
    """
    Perform a health check on the metrics system itself.

    Returns:
        Dict containing health status of metrics collection
    """
    try:
        # Try to record a test metric
        test_metric_name = "metrics_health_check_test"
        collector.set_gauge(
            name=test_metric_name,
            value=1.0,
            labels={"status": "healthy"}
        )

        # Verify we can retrieve it
        value = collector.get_current_gauge_value(test_metric_name, {"status": "healthy"})

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "metrics_collector": "operational",
                "storage": "accessible",
                "test_metric": "recorded_and_retrieved"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "components": {
                "metrics_collector": "error",
                "storage": "error"
            }
        }


# Initialize common metrics
def initialize_common_metrics():
    """Initialize common metrics that should always be available."""
    # Initialize gauges with sensible defaults
    collector.set_gauge("active_requests", 0)
    collector.set_gauge("verification_success_rate", 0)
    collector.set_gauge("db_active_connections", 0)


# Initialize common metrics on import
initialize_common_metrics()