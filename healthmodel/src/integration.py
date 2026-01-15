"""
Health Model Integration

Main integration module that combines REST API client, signals, and model configuration.
Provides a unified interface for health model operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
import logging

from api.health_state_client import HealthStateClient, HealthState
from signals.health_signals import HealthSignal, SignalCollection
from models.health_model_config import (
    HealthModelConfig, HealthModelEntity, 
    create_ecommerce_health_model, 
    create_microservices_health_model
)
from config.env_loader import load_env


logger = logging.getLogger(__name__)


class HealthModelIntegration:
    """
    Unified interface for health model operations
    
    Combines configuration, signal definitions, and REST API access
    """
    
    def __init__(
        self,
        config: HealthModelConfig,
        api_client: HealthStateClient,
        signals_collection: Dict[str, HealthSignal]
    ):
        """
        Initialize the integration
        
        Args:
            config: Health model configuration
            api_client: REST API client for querying health states
            signals_collection: Available health signals
        """
        self.config = config
        self.api_client = api_client
        self.signals_collection = signals_collection
    
    def get_entity_health(self, entity_id: str) -> Dict[str, Any]:
        """
        Get current health state of an entity
        
        Returns simplified response with red/green/amber status
        """
        health = self.api_client.get_entity_health_state(entity_id)
        
        entity = self.config.entities.get(entity_id)
        if entity:
            health["entity_name"] = entity.name
            health["entity_type"] = entity.entity_type.value
        
        return health
    
    def get_workload_health(self) -> Dict[str, Any]:
        """Get overall workload health (root entity)"""
        # Find root entity from API (entity with type System_HealthModelRoot)
        all_entities = self.api_client.get_all_entities_health()
        for entity_id, health in all_entities.items():
            if health.get('details', {}).get('kind') == 'System_HealthModelRoot':
                return health
        # Fallback: return first entity if no root found
        if all_entities:
            return next(iter(all_entities.values()))
        return {"state": "Unknown", "state_color": "gray", "state_code": "UNKNOWN"}
    
    def get_all_entities_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health state of all entities"""
        return self.api_client.get_all_entities_health()
    
    def get_health_tree(self) -> Dict[str, Any]:
        """
        Get complete health tree for all entities
        
        Returns hierarchical structure showing health and dependencies
        """
        tree = {}
        
        # Get all entities' health
        all_health = self.api_client.get_all_entities_health()
        
        for entity_id, entity in self.config.entities.items():
            health = all_health.get(entity_id, {})
            
            tree[entity_id] = {
                "name": entity.name,
                "type": entity.entity_type.value,
                "state": health.get("state", HealthState.UNKNOWN.value),
                "state_color": health.get("state_color", "gray"),
                "timestamp": health.get("timestamp"),
                "parent": entity.parent_entity_id,
                "signals": entity.signals,
                "dependencies": self._get_entity_deps(entity_id)
            }
        
        return tree
    
    def get_dependency_impact(self, entity_id: str) -> Dict[str, Any]:
        """
        Analyze impact of entity failure on dependent services
        
        Shows which services would be affected
        """
        dependents = self.config.get_entity_dependents(entity_id)
        
        impact = {
            "failed_entity": entity_id,
            "failed_entity_name": self.config.entities.get(entity_id, {}).name if entity_id in self.config.entities else None,
            "affected_services": [],
            "impact_severity": "low"
        }
        
        if dependents:
            severity_levels = {"critical": 3, "high": 2, "medium": 1, "low": 0}
            max_severity = max([severity_levels.get(d.criticality, 0) for d in dependents])
            
            severity_map = {3: "critical", 2: "high", 1: "medium", 0: "low"}
            impact["impact_severity"] = severity_map.get(max_severity, "low")
            
            for dep in dependents:
                affected_entity = self.config.entities.get(dep.target_entity_id)
                if affected_entity:
                    impact["affected_services"].append({
                        "entity_id": affected_entity.id,
                        "entity_name": affected_entity.name,
                        "criticality": dep.criticality,
                        "dependency_type": dep.dependency_type
                    })
        
        return impact
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get summary of health across all entities
        
        Returns counts and percentages of health states
        """
        all_health = self.api_client.get_all_entities_health()
        
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_entities": len(all_health),
            "healthy_count": 0,
            "degraded_count": 0,
            "unhealthy_count": 0,
            "unknown_count": 0,
            "health_percentages": {
                "healthy": 0.0,
                "degraded": 0.0,
                "unhealthy": 0.0,
                "unknown": 0.0
            },
            "entities_by_state": {
                "healthy": [],
                "degraded": [],
                "unhealthy": [],
                "unknown": []
            }
        }
        
        # Count entities by their actual state from API
        for entity_id, health in all_health.items():
            state = health.get("state", "Unknown").lower()
            entity_name = health.get('details', {}).get('displayName', entity_id)
            
            if state == "healthy":
                summary["healthy_count"] += 1
                summary["entities_by_state"]["healthy"].append({
                    "entity_id": entity_id,
                    "entity_name": entity_name
                })
            elif state == "degraded":
                summary["degraded_count"] += 1
                summary["entities_by_state"]["degraded"].append({
                    "entity_id": entity_id,
                    "entity_name": entity_name
                })
            elif state == "unhealthy":
                summary["unhealthy_count"] += 1
                summary["entities_by_state"]["unhealthy"].append({
                    "entity_id": entity_id,
                    "entity_name": entity_name
                })
            else:  # unknown or any other state
                summary["unknown_count"] += 1
                summary["entities_by_state"]["unknown"].append({
                    "entity_id": entity_id,
                    "entity_name": entity_name
                })
        
        # Calculate percentages
        total = summary["total_entities"]
        if total > 0:
            for state in ["healthy", "degraded", "unhealthy", "unknown"]:
                count_key = f"{state}_count"
                summary["health_percentages"][state] = (
                    summary[count_key] / total
                ) * 100
        
        return summary
    
    def get_critical_path(self) -> List[str]:
        """
        Identify critical path through dependencies
        
        Returns ordered list of entities that represent the critical execution path
        """
        # Start from root and trace critical dependencies
        critical_path = []
        visited = set()
        
        def trace_critical(entity_id: str):
            if entity_id in visited:
                return
            visited.add(entity_id)
            critical_path.append(entity_id)
            
            dependencies = self.config.get_entity_dependencies(entity_id)
            critical_deps = [d for d in dependencies if d.criticality in ["critical", "high"]]
            
            for dep in critical_deps:
                trace_critical(dep.source_entity_id)
        
        trace_critical("root")
        return critical_path
    
    def get_signal_definitions(self, entity_id: str) -> Dict[str, HealthSignal]:
        """Get signal definitions for a specific entity"""
        entity = self.config.entities.get(entity_id)
        if not entity:
            return {}
        
        signals = {}
        for signal_name, signal_id in entity.signals.items():
            if signal_id in self.signals_collection:
                signals[signal_name] = self.signals_collection[signal_id]
        
        return signals
    
    def export_health_report(self, filepath: str) -> None:
        """Export detailed health report to JSON"""
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": self.config.model_name,
            "summary": self.get_health_summary(),
            "health_tree": self.get_health_tree(),
            "critical_path": self.get_critical_path()
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Health report exported to {filepath}")
    
    def _get_entity_deps(self, entity_id: str) -> Dict[str, List[str]]:
        """Get dependency information for an entity"""
        dependencies = self.config.get_entity_dependencies(entity_id)
        dependents = self.config.get_entity_dependents(entity_id)
        
        return {
            "depends_on": [d.source_entity_id for d in dependencies],
            "depended_by": [d.target_entity_id for d in dependents]
        }
    
    def close(self):
        """Close the API client"""
        self.api_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ==============================================================================
# CONVENIENCE BUILDERS
# ==============================================================================

class HealthModelBuilder:
    """Builder for creating health model integrations"""
    
    @staticmethod
    def create_from_env(health_model_name: Optional[str] = None) -> HealthModelIntegration:
        """
        Create integration from environment variables (.env file)
        
        Args:
            health_model_name: Override health model name (optional)
        
        Returns:
            Configured HealthModelIntegration instance
        """
        env = load_env()
        
        if not env.validate():
            raise ValueError("Environment configuration is invalid. Check .env file.")
        
        azure_config = env.get_azure_config()
        
        # Get auth token
        auth_token = env.get("AZURE_AUTH_TOKEN")
        if not auth_token:
            # Try to get from Azure CLI
            import subprocess
            try:
                result = subprocess.run(
                    "az account get-access-token --query accessToken -o tsv",
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=True
                )
                auth_token = result.stdout.strip()
            except Exception as e:
                raise ValueError(f"Failed to get auth token from Azure CLI: {e}")
        
        # Use provided health model name or from env
        model_name = health_model_name or azure_config['healthModelName']
        
        api_client = HealthStateClient(
            subscription_id=azure_config['subscriptionId'],
            resource_group=azure_config['resourceGroup'],
            health_model_name=model_name,
            auth_token=auth_token
        )
        
        config = create_ecommerce_health_model()
        signals = SignalCollection.web_service_signals()
        signals.update(SignalCollection.database_signals())
        
        return HealthModelIntegration(config, api_client, signals)
    
    @staticmethod
    def create_from_ecommerce_example(
        subscription_id: str,
        resource_group: str,
        auth_token: str,
        health_model_name: str = "my-health-model"
    ) -> HealthModelIntegration:
        """Create integration with e-commerce example configuration"""
        from models.health_model_config import create_ecommerce_health_model
        
        config = create_ecommerce_health_model()
        
        api_client = HealthStateClient(
            subscription_id=subscription_id,
            resource_group=resource_group,
            health_model_name=health_model_name,
            auth_token=auth_token
        )
        
        signals = SignalCollection.web_service_signals()
        signals.update(SignalCollection.database_signals())
        
        return HealthModelIntegration(config, api_client, signals)
    
    @staticmethod
    def create_custom(
        config: HealthModelConfig,
        subscription_id: str,
        resource_group: str,
        auth_token: str,
        health_model_name: str,
        signals: Optional[Dict[str, HealthSignal]] = None
    ) -> HealthModelIntegration:
        """Create integration with custom configuration"""
        api_client = HealthStateClient(
            subscription_id=subscription_id,
            resource_group=resource_group,
            health_model_name=health_model_name,
            auth_token=auth_token
        )
        
        if signals is None:
            signals = SignalCollection.web_service_signals()
        
        return HealthModelIntegration(config, api_client, signals)


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

def example_usage():
    """Example of using the health model integration"""
    
    # Initialize integration from .env file
    integration = HealthModelBuilder.create_from_env()
    
    with integration:
        # Get workload health
        workload_health = integration.get_workload_health()
        print(f"Workload Status: {workload_health['state_color']} ({workload_health['state']})")
        
        # Get health summary
        summary = integration.get_health_summary()
        print(f"\nHealth Summary:")
        print(f"  Healthy: {summary['health_counts']['healthy']}")
        print(f"  Degraded: {summary['health_counts']['degraded']}")
        print(f"  Unhealthy: {summary['health_counts']['unhealthy']}")
        
        # Check impact of a service failure
        impact = integration.get_dependency_impact("product-service")
        print(f"\nIf product-service fails:")
        print(f"  Impact Severity: {impact['impact_severity']}")
        for affected in impact['affected_services']:
            print(f"    - {affected['entity_name']} ({affected['criticality']})")
        
        # Get critical path
        critical = integration.get_critical_path()
        print(f"\nCritical Path: {' -> '.join(critical)}")
        
        # Export report
        integration.export_health_report("health_report.json")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # example_usage()
