"""
Health Model Configuration

Defines entity relationships and signal assignments for a health model.
This is the configuration that ties together entities, signals, and dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime, timezone


class EntityType(Enum):
    """Entity types in the health model"""
    WORKLOAD = "workload"
    SERVICE = "service"
    DATABASE = "database"
    VM = "virtual_machine"
    CONTAINER = "container"
    API = "api"
    LOAD_BALANCER = "load_balancer"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    CUSTOM = "custom"


@dataclass
class EntityDependency:
    """Represents a dependency between two entities"""
    source_entity_id: str  # The entity being depended upon
    target_entity_id: str  # The entity that depends
    dependency_type: str = "direct"  # direct, indirect, optional
    criticality: str = "high"  # high, medium, low


@dataclass
class HealthModelEntity:
    """Represents an entity in the health model"""
    id: str
    name: str
    entity_type: EntityType
    description: str
    parent_entity_id: Optional[str] = None
    azure_resource_id: Optional[str] = None  # Azure resource ID if applicable
    signals: Dict[str, str] = field(default_factory=dict)  # signal_name -> signal_id
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type.value,
            "description": self.description,
            "parentEntityId": self.parent_entity_id,
            "azureResourceId": self.azure_resource_id,
            "signals": self.signals,
            "metadata": self.metadata
        }


@dataclass
class HealthModelConfig:
    """Complete health model configuration"""
    model_id: str
    model_name: str
    description: str
    owner_team: str
    entities: Dict[str, HealthModelEntity] = field(default_factory=dict)
    dependencies: List[EntityDependency] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0.0"
    
    def add_entity(self, entity: HealthModelEntity) -> None:
        """Add an entity to the model"""
        self.entities[entity.id] = entity
        self.last_modified = datetime.now(timezone.utc).isoformat()
    
    def add_dependency(self, dependency: EntityDependency) -> None:
        """Add a dependency between entities"""
        self.dependencies.append(dependency)
        self.last_modified = datetime.now(timezone.utc).isoformat()
    
    def get_entity_dependencies(self, entity_id: str) -> List[EntityDependency]:
        """Get all dependencies for a specific entity"""
        return [d for d in self.dependencies if d.target_entity_id == entity_id]
    
    def get_entity_dependents(self, entity_id: str) -> List[EntityDependency]:
        """Get all entities that depend on a specific entity"""
        return [d for d in self.dependencies if d.source_entity_id == entity_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "modelId": self.model_id,
            "modelName": self.model_name,
            "description": self.description,
            "ownerTeam": self.owner_team,
            "version": self.version,
            "createdAt": self.created_at,
            "lastModified": self.last_modified,
            "entities": {eid: entity.to_dict() for eid, entity in self.entities.items()},
            "dependencies": [
                {
                    "sourceEntityId": d.source_entity_id,
                    "targetEntityId": d.target_entity_id,
                    "dependencyType": d.dependency_type,
                    "criticality": d.criticality
                }
                for d in self.dependencies
            ]
        }
    
    def export_to_json(self, filepath: str) -> None:
        """Export configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load_from_json(filepath: str) -> 'HealthModelConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = HealthModelConfig(
            model_id=data.get("modelId"),
            model_name=data.get("modelName"),
            description=data.get("description"),
            owner_team=data.get("ownerTeam"),
            version=data.get("version", "1.0.0"),
            created_at=data.get("createdAt"),
            last_modified=data.get("lastModified")
        )
        
        # Load entities
        for entity_id, entity_data in data.get("entities", {}).items():
            entity = HealthModelEntity(
                id=entity_data["id"],
                name=entity_data["name"],
                entity_type=EntityType(entity_data["type"]),
                description=entity_data["description"],
                parent_entity_id=entity_data.get("parentEntityId"),
                azure_resource_id=entity_data.get("azureResourceId"),
                signals=entity_data.get("signals", {}),
                metadata=entity_data.get("metadata", {})
            )
            config.add_entity(entity)
        
        # Load dependencies
        for dep_data in data.get("dependencies", []):
            dependency = EntityDependency(
                source_entity_id=dep_data["sourceEntityId"],
                target_entity_id=dep_data["targetEntityId"],
                dependency_type=dep_data.get("dependencyType", "direct"),
                criticality=dep_data.get("criticality", "high")
            )
            config.add_dependency(dependency)
        
        return config


# ==============================================================================
# EXAMPLE CONFIGURATIONS
# ==============================================================================

def create_ecommerce_health_model() -> HealthModelConfig:
    """
    Example: E-commerce application health model
    
    Shows a typical multi-tier application structure
    """
    config = HealthModelConfig(
        model_id="ecommerce-prod",
        model_name="E-Commerce Production",
        description="Health model for e-commerce platform",
        owner_team="Platform Engineering"
    )
    
    # Root entity - overall workload
    root = HealthModelEntity(
        id="ecommerce-root",
        name="E-Commerce Workload",
        entity_type=EntityType.WORKLOAD,
        description="Overall e-commerce platform health"
    )
    config.add_entity(root)
    
    # API Services tier
    api = HealthModelEntity(
        id="api-service",
        name="API Gateway",
        entity_type=EntityType.API,
        description="REST API serving all client requests",
        parent_entity_id="ecommerce-root",
        signals={
            "response_time": "api_response_time_p95",
            "error_rate": "api_error_rate",
            "availability": "api_availability"
        }
    )
    config.add_entity(api)
    
    # Product Service
    product_service = HealthModelEntity(
        id="product-service",
        name="Product Service",
        entity_type=EntityType.SERVICE,
        description="Manages product catalog and information",
        parent_entity_id="ecommerce-root",
        signals={
            "response_time": "product_response_time",
            "error_rate": "product_error_rate"
        }
    )
    config.add_entity(product_service)
    
    # Order Service
    order_service = HealthModelEntity(
        id="order-service",
        name="Order Service",
        entity_type=EntityType.SERVICE,
        description="Handles order processing and management",
        parent_entity_id="ecommerce-root",
        signals={
            "response_time": "order_response_time",
            "error_rate": "order_error_rate"
        }
    )
    config.add_entity(order_service)
    
    # Payment Service
    payment_service = HealthModelEntity(
        id="payment-service",
        name="Payment Service",
        entity_type=EntityType.SERVICE,
        description="Processes payment transactions",
        parent_entity_id="ecommerce-root",
        signals={
            "availability": "payment_availability",
            "error_rate": "payment_error_rate"
        }
    )
    config.add_entity(payment_service)
    
    # Product Database
    product_db = HealthModelEntity(
        id="product-db",
        name="Product Database",
        entity_type=EntityType.DATABASE,
        description="PostgreSQL database for product data",
        parent_entity_id="product-service",
        azure_resource_id="/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.DBforPostgreSQL/servers/product-db",
        signals={
            "connection_pool": "product_db_conn_pool",
            "query_latency": "product_db_latency"
        }
    )
    config.add_entity(product_db)
    
    # Order Database
    order_db = HealthModelEntity(
        id="order-db",
        name="Order Database",
        entity_type=EntityType.DATABASE,
        description="Database for order data",
        parent_entity_id="order-service",
        signals={
            "connection_pool": "order_db_conn_pool",
            "query_latency": "order_db_latency"
        }
    )
    config.add_entity(order_db)
    
    # Cache
    cache = HealthModelEntity(
        id="cache-layer",
        name="Redis Cache",
        entity_type=EntityType.CACHE,
        description="Distributed cache for performance",
        parent_entity_id="ecommerce-root",
        signals={
            "availability": "cache_availability",
            "latency": "cache_latency"
        }
    )
    config.add_entity(cache)
    
    # Service Bus for async processing
    service_bus = HealthModelEntity(
        id="service-bus",
        name="Service Bus",
        entity_type=EntityType.MESSAGE_QUEUE,
        description="Azure Service Bus for asynchronous processing",
        parent_entity_id="ecommerce-root",
        signals={
            "availability": "bus_availability",
            "queue_depth": "bus_queue_depth"
        }
    )
    config.add_entity(service_bus)
    
    # Define dependencies
    # API Gateway depends on Product Service
    config.add_dependency(EntityDependency(
        source_entity_id="product-service",
        target_entity_id="api-service",
        criticality="high"
    ))
    
    # API Gateway depends on Order Service
    config.add_dependency(EntityDependency(
        source_entity_id="order-service",
        target_entity_id="api-service",
        criticality="high"
    ))
    
    # Order Service depends on Payment Service
    config.add_dependency(EntityDependency(
        source_entity_id="payment-service",
        target_entity_id="order-service",
        criticality="critical"
    ))
    
    # Product Service depends on Product DB
    config.add_dependency(EntityDependency(
        source_entity_id="product-db",
        target_entity_id="product-service",
        criticality="high"
    ))
    
    # Order Service depends on Order DB
    config.add_dependency(EntityDependency(
        source_entity_id="order-db",
        target_entity_id="order-service",
        criticality="high"
    ))
    
    # Services use Cache
    config.add_dependency(EntityDependency(
        source_entity_id="cache-layer",
        target_entity_id="product-service",
        dependency_type="optional",
        criticality="medium"
    ))
    
    # Order Service uses Service Bus
    config.add_dependency(EntityDependency(
        source_entity_id="service-bus",
        target_entity_id="order-service",
        dependency_type="direct",
        criticality="high"
    ))
    
    return config


def create_microservices_health_model() -> HealthModelConfig:
    """
    Example: Microservices architecture health model
    
    Shows multiple independent services with shared dependencies
    """
    config = HealthModelConfig(
        model_id="microservices-prod",
        model_name="Microservices Platform",
        description="Health model for microservices architecture",
        owner_team="SRE Team"
    )
    
    # Root
    root = HealthModelEntity(
        id="platform-root",
        name="Microservices Platform",
        entity_type=EntityType.WORKLOAD,
        description="Overall platform health"
    )
    config.add_entity(root)
    
    # Multiple microservices
    services = [
        ("user-service", "User Service", "Manages user accounts and profiles"),
        ("notification-service", "Notification Service", "Sends notifications"),
        ("analytics-service", "Analytics Service", "Tracks user analytics"),
    ]
    
    for service_id, service_name, service_desc in services:
        service = HealthModelEntity(
            id=service_id,
            name=service_name,
            entity_type=EntityType.SERVICE,
            description=service_desc,
            parent_entity_id="platform-root",
            signals={
                "response_time": f"{service_id}_response_time",
                "error_rate": f"{service_id}_error_rate",
                "availability": f"{service_id}_availability"
            }
        )
        config.add_entity(service)
    
    return config


if __name__ == "__main__":
    # Example: Create and export e-commerce model
    model = create_ecommerce_health_model()
    model.export_to_json("ecommerce_health_model.json")
    
    print("E-Commerce Health Model Configuration:")
    print(f"  Model: {model.model_name}")
    print(f"  Entities: {len(model.entities)}")
    print(f"  Dependencies: {len(model.dependencies)}")
    print("\nEntities:")
    for entity in model.entities.values():
        print(f"  - {entity.name} ({entity.entity_type.value})")
