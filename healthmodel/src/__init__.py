"""Azure Health Model Integration Package"""

__version__ = "1.0.0"
__author__ = "Platform Engineering Team"

from api.health_state_client import HealthStateClient, HealthState
from signals.health_signals import HealthSignal, SignalCollection
from models.health_model_config import HealthModelConfig, HealthModelEntity
from integration import HealthModelIntegration, HealthModelBuilder

__all__ = [
    "HealthStateClient",
    "HealthState",
    "HealthSignal",
    "SignalCollection",
    "HealthModelConfig",
    "HealthModelEntity",
    "HealthModelIntegration",
    "HealthModelBuilder",
]
