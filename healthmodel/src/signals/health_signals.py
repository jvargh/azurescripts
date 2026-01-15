"""
Health Signal Definitions

Defines custom health signals that can be used in Azure Monitor Health Models.
Signals are the individual metrics, logs, or custom indicators that contribute to entity health.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from enum import Enum
import json


class SignalType(Enum):
    """Types of health signals"""
    METRIC = "metric"
    LOG_QUERY = "log_query"
    CUSTOM = "custom"
    AZURE_RESOURCE_HEALTH = "azure_resource_health"


class ThresholdOperator(Enum):
    """Threshold comparison operators"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "neq"


@dataclass
class HealthThreshold:
    """Defines health state thresholds for a signal"""
    healthy_min: Optional[float] = None
    healthy_max: Optional[float] = None
    degraded_min: Optional[float] = None
    degraded_max: Optional[float] = None
    unhealthy_min: Optional[float] = None
    unhealthy_max: Optional[float] = None
    operator: ThresholdOperator = ThresholdOperator.GREATER_THAN
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "healthyMin": self.healthy_min,
            "healthyMax": self.healthy_max,
            "degradedMin": self.degraded_min,
            "degradedMax": self.degraded_max,
            "unhealthyMin": self.unhealthy_min,
            "unhealthyMax": self.unhealthy_max,
            "operator": self.operator.value
        }


@dataclass
class HealthSignal:
    """Defines a health signal for an entity"""
    name: str
    signal_type: SignalType
    display_name: str
    description: str
    thresholds: HealthThreshold
    enabled: bool = True
    weight: float = 1.0  # Weight in health aggregation (0.0 - 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API submission"""
        return {
            "name": self.name,
            "type": self.signal_type.value,
            "displayName": self.display_name,
            "description": self.description,
            "thresholds": self.thresholds.to_dict(),
            "enabled": self.enabled,
            "weight": self.weight
        }


# ==============================================================================
# COMPUTE & INFRASTRUCTURE SIGNALS
# ==============================================================================

def create_cpu_utilization_signal() -> HealthSignal:
    """
    CPU Utilization health signal
    
    Standard signal for monitoring CPU usage on VMs, app services, or containers
    """
    return HealthSignal(
        name="cpu_utilization",
        signal_type=SignalType.METRIC,
        display_name="CPU Utilization",
        description="CPU utilization percentage. High values indicate compute pressure.",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=70,        # Healthy if < 70%
            degraded_min=70,
            degraded_max=85,       # Degraded if 70-85%
            unhealthy_min=85       # Unhealthy if > 85%
        ),
        weight=0.25
    )


def create_memory_utilization_signal() -> HealthSignal:
    """
    Memory Utilization health signal
    
    Monitors available memory percentage
    """
    return HealthSignal(
        name="memory_utilization",
        signal_type=SignalType.METRIC,
        display_name="Memory Utilization",
        description="Memory utilization percentage. High values indicate memory pressure.",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=80,
            degraded_min=80,
            degraded_max=90,
            unhealthy_min=90
        ),
        weight=0.25
    )


def create_disk_space_signal() -> HealthSignal:
    """
    Disk Space health signal
    
    Monitors available disk space percentage
    """
    return HealthSignal(
        name="disk_space_available",
        signal_type=SignalType.METRIC,
        display_name="Disk Space Available",
        description="Available disk space percentage",
        thresholds=HealthThreshold(
            healthy_min=20,        # Healthy if > 20% available
            degraded_min=10,
            degraded_max=20,       # Degraded if 10-20% available
            unhealthy_max=10       # Unhealthy if < 10% available
        ),
        weight=0.15
    )


def create_network_latency_signal() -> HealthSignal:
    """
    Network Latency health signal
    
    Monitors network round-trip time in milliseconds
    """
    return HealthSignal(
        name="network_latency",
        signal_type=SignalType.METRIC,
        display_name="Network Latency (ms)",
        description="Average network latency in milliseconds",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=100,       # Healthy if < 100ms
            degraded_min=100,
            degraded_max=500,      # Degraded if 100-500ms
            unhealthy_min=500      # Unhealthy if > 500ms
        ),
        weight=0.15
    )


# ==============================================================================
# APPLICATION PERFORMANCE SIGNALS
# ==============================================================================

def create_response_time_signal() -> HealthSignal:
    """
    Application Response Time health signal
    
    Monitors p95 response time in milliseconds
    """
    return HealthSignal(
        name="response_time_p95",
        signal_type=SignalType.METRIC,
        display_name="Response Time (p95)",
        description="95th percentile response time in milliseconds",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=500,       # Healthy if p95 < 500ms
            degraded_min=500,
            degraded_max=1000,     # Degraded if 500-1000ms
            unhealthy_min=1000     # Unhealthy if > 1000ms
        ),
        weight=0.25
    )


def create_error_rate_signal() -> HealthSignal:
    """
    Application Error Rate health signal
    
    Monitors percentage of failed requests
    """
    return HealthSignal(
        name="error_rate",
        signal_type=SignalType.METRIC,
        display_name="Error Rate (%)",
        description="Percentage of requests that result in errors",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=1,         # Healthy if < 1% errors
            degraded_min=1,
            degraded_max=5,        # Degraded if 1-5% errors
            unhealthy_min=5        # Unhealthy if > 5% errors
        ),
        weight=0.30
    )


def create_availability_signal() -> HealthSignal:
    """
    Service Availability health signal
    
    Monitors uptime percentage (0-100)
    """
    return HealthSignal(
        name="availability",
        signal_type=SignalType.METRIC,
        display_name="Availability (%)",
        description="Service availability percentage (uptime)",
        thresholds=HealthThreshold(
            healthy_min=99.5,
            healthy_max=100,       # Healthy if 99.5%+ available
            degraded_min=99,
            degraded_max=99.5,     # Degraded if 99-99.5%
            unhealthy_max=99       # Unhealthy if < 99%
        ),
        weight=0.30
    )


def create_request_rate_signal() -> HealthSignal:
    """
    Request Rate health signal
    
    Monitors requests per second (RPS)
    """
    return HealthSignal(
        name="request_rate_rps",
        signal_type=SignalType.METRIC,
        display_name="Request Rate (RPS)",
        description="Requests per second",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=1000,      # Healthy if < 1000 RPS
            degraded_min=1000,
            degraded_max=2000,     # Degraded if 1000-2000 RPS
            unhealthy_min=2000     # Unhealthy if > 2000 RPS
        ),
        weight=0.15
    )


# ==============================================================================
# DATABASE SIGNALS
# ==============================================================================

def create_database_connection_pool_signal() -> HealthSignal:
    """
    Database Connection Pool health signal
    
    Monitors percentage of pool utilization
    """
    return HealthSignal(
        name="db_connection_pool_utilization",
        signal_type=SignalType.METRIC,
        display_name="DB Connection Pool Utilization (%)",
        description="Percentage of available database connections in use",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=70,        # Healthy if < 70% used
            degraded_min=70,
            degraded_max=85,       # Degraded if 70-85% used
            unhealthy_min=85       # Unhealthy if > 85% used
        ),
        weight=0.25
    )


def create_database_query_latency_signal() -> HealthSignal:
    """
    Database Query Latency health signal
    
    Monitors p95 query execution time in milliseconds
    """
    return HealthSignal(
        name="db_query_latency_p95",
        signal_type=SignalType.METRIC,
        display_name="DB Query Latency (p95 ms)",
        description="95th percentile database query execution time",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=100,       # Healthy if p95 < 100ms
            degraded_min=100,
            degraded_max=500,      # Degraded if 100-500ms
            unhealthy_min=500      # Unhealthy if > 500ms
        ),
        weight=0.25
    )


def create_database_deadlock_signal() -> HealthSignal:
    """
    Database Deadlock health signal
    
    Monitors deadlock count
    """
    return HealthSignal(
        name="db_deadlocks",
        signal_type=SignalType.METRIC,
        display_name="DB Deadlocks",
        description="Number of database deadlocks detected",
        thresholds=HealthThreshold(
            healthy_min=0,
            healthy_max=0,         # Healthy if 0 deadlocks
            degraded_min=1,
            degraded_max=5,        # Degraded if 1-5 deadlocks
            unhealthy_min=5        # Unhealthy if > 5 deadlocks
        ),
        weight=0.20
    )


# ==============================================================================
# CUSTOM BUSINESS LOGIC SIGNALS
# ==============================================================================

def create_custom_business_metric_signal(
    metric_name: str,
    display_name: str,
    description: str,
    healthy_threshold: float,
    degraded_threshold: float,
    weight: float = 0.20
) -> HealthSignal:
    """
    Create a custom business metric signal
    
    Allows defining domain-specific health metrics
    
    Args:
        metric_name: Internal metric identifier
        display_name: User-friendly display name
        description: Metric description
        healthy_threshold: Value for healthy state
        degraded_threshold: Value for degraded state
        weight: Signal weight in aggregation
    """
    return HealthSignal(
        name=metric_name,
        signal_type=SignalType.CUSTOM,
        display_name=display_name,
        description=description,
        thresholds=HealthThreshold(
            healthy_min=healthy_threshold,
            degraded_min=degraded_threshold
        ),
        weight=weight
    )


# ==============================================================================
# SIGNAL COLLECTIONS
# ==============================================================================

class SignalCollection:
    """Pre-defined collections of signals for common entity types"""
    
    @staticmethod
    def vm_signals() -> Dict[str, HealthSignal]:
        """Signals for Virtual Machine health"""
        return {
            "cpu": create_cpu_utilization_signal(),
            "memory": create_memory_utilization_signal(),
            "disk": create_disk_space_signal(),
            "network_latency": create_network_latency_signal(),
        }
    
    @staticmethod
    def web_service_signals() -> Dict[str, HealthSignal]:
        """Signals for Web Service/API health"""
        return {
            "response_time": create_response_time_signal(),
            "error_rate": create_error_rate_signal(),
            "availability": create_availability_signal(),
            "request_rate": create_request_rate_signal(),
            "cpu": create_cpu_utilization_signal(),
            "memory": create_memory_utilization_signal(),
        }
    
    @staticmethod
    def database_signals() -> Dict[str, HealthSignal]:
        """Signals for Database health"""
        return {
            "connection_pool": create_database_connection_pool_signal(),
            "query_latency": create_database_query_latency_signal(),
            "deadlocks": create_database_deadlock_signal(),
            "cpu": create_cpu_utilization_signal(),
            "memory": create_memory_utilization_signal(),
        }
    
    @staticmethod
    def app_service_signals() -> Dict[str, HealthSignal]:
        """Signals for App Service health"""
        return {
            "response_time": create_response_time_signal(),
            "error_rate": create_error_rate_signal(),
            "availability": create_availability_signal(),
            "cpu": create_cpu_utilization_signal(),
            "memory": create_memory_utilization_signal(),
        }


# ==============================================================================
# UTILITIES
# ==============================================================================

def export_signals_to_json(signals: Dict[str, HealthSignal], filepath: str) -> None:
    """Export signal definitions to JSON for Azure Monitor"""
    data = {
        "signals": [signal.to_dict() for signal in signals.values()]
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def print_signal_details(signal: HealthSignal) -> None:
    """Print detailed information about a signal"""
    print(f"\n{signal.display_name}")
    print(f"  Type: {signal.signal_type.value}")
    print(f"  Description: {signal.description}")
    print(f"  Weight: {signal.weight}")
    print(f"  Thresholds:")
    print(f"    Healthy: {signal.thresholds.healthy_min} - {signal.thresholds.healthy_max}")
    print(f"    Degraded: {signal.thresholds.degraded_min} - {signal.thresholds.degraded_max}")
    print(f"    Unhealthy: {signal.thresholds.unhealthy_min} - {signal.thresholds.unhealthy_max}")


if __name__ == "__main__":
    # Example: Print all web service signals
    print("=== Web Service Health Signals ===")
    for signal_name, signal in SignalCollection.web_service_signals().items():
        print_signal_details(signal)
    
    # Example: Export signals to JSON
    # export_signals_to_json(
    #     SignalCollection.web_service_signals(),
    #     "web_service_signals.json"
    # )
