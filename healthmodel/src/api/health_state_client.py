"""
Azure Monitor Health Models REST API Client

This module provides a REST API client for querying health states from Azure Monitor Health Models.
Supports both individual entity queries and batch queries.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthState(Enum):
    """Health state enumeration matching Azure Monitor states"""
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    UNHEALTHY = "Unhealthy"
    UNKNOWN = "Unknown"


class HealthStateClient:
    """
    REST API client for Azure Monitor Health Models
    
    Allows you to query health states of entities in a health model via REST API.
    """
    
    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        health_model_name: str,
        auth_token: str,
        base_url: str = "https://management.azure.com"
    ):
        """
        Initialize the Health State Client
        
        Args:
            subscription_id: Azure subscription ID
            resource_group: Azure resource group name
            health_model_name: Name of the health model
            auth_token: Bearer token for authentication
            base_url: Azure Management API base URL
        """
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.health_model_name = health_model_name
        self.auth_token = auth_token
        self.base_url = base_url
        self.api_version = "2025-05-01-preview"
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        })
    
    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint"""
        # Health models use Microsoft.CloudHealth provider, not Monitor accounts
        # Format: /subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.CloudHealth/healthmodels/{name}
        return (
            f"{self.base_url}/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group}/"
            f"providers/Microsoft.CloudHealth/healthmodels/{self.health_model_name}/"
            f"{endpoint}"
        )
    
    def get_entity_health_state(
        self,
        entity_id: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Query the health state of a specific entity
        
        Args:
            entity_id: Unique identifier of the entity
            timestamp: Optional timestamp for historical data (default: now)
        
        Returns:
            Dict containing:
                - entity_id: The entity identifier
                - state: HealthState (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)
                - timestamp: When the state was recorded
                - signals: List of health signals contributing to the state
                - state_color: "green", "amber", or "red"
                - details: Additional state details
        """
        url = self._build_url(f"entities/{entity_id}")
        
        params = {
            "api-version": self.api_version
        }
        
        if timestamp:
            params["timestamp"] = timestamp.isoformat()
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._normalize_response(data)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query health state for entity {entity_id}: {str(e)}")
            return self._error_response(entity_id, str(e))
    
    def get_root_entity_health(
        self,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Query the health state of the root entity (overall workload health)
        
        Args:
            timestamp: Optional timestamp for historical data
        
        Returns:
            Root entity health state with aggregate status
        """
        return self.get_entity_health_state("root", timestamp)
    
    def get_entity_health_timeline(
        self,
        entity_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get health state timeline for an entity over a time range
        
        Args:
            entity_id: Entity identifier
            start_time: Start of time range (default: 24 hours ago)
            end_time: End of time range (default: now)
            interval_minutes: Data point interval
        
        Returns:
            List of health states ordered by timestamp
        """
        if not start_time:
            start_time = datetime.now(timezone.utc) - timedelta(hours=24)
        if not end_time:
            end_time = datetime.now(timezone.utc)
        
        url = self._build_url(
            f"entities/{entity_id}/timeline"
        )
        
        params = {
            "api-version": self.api_version,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
            "intervalMinutes": interval_minutes
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return [self._normalize_response(item) for item in data.get("values", [])]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query timeline for entity {entity_id}: {str(e)}")
            return []
    
    def get_all_entities_health(
        self,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get health state of all entities in the model
        
        Args:
            timestamp: Optional timestamp for historical data
        
        Returns:
            Dictionary mapping entity_id to health state
        """
        url = self._build_url(f"entities")
        
        params = {
            "api-version": self.api_version
        }
        
        if timestamp:
            params["timestamp"] = timestamp.isoformat()
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            entities = {}
            
            for item in data.get("value", []):
                normalized = self._normalize_response(item)
                entities[item.get("id")] = normalized
            
            return entities
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query all entities: {str(e)}")
            return {}
    
    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize API response to standard format
        
        Maps Azure Monitor response to red/green/amber state
        """
        state_str = data.get("properties", {}).get("healthState", "Unknown")
        
        # Map state string to enum (case-insensitive)
        try:
            health_state = HealthState[state_str.upper()]
        except (KeyError, AttributeError):
            health_state = HealthState.UNKNOWN
        
        # Map to color
        state_colors = {
            HealthState.HEALTHY: "green",
            HealthState.DEGRADED: "amber",
            HealthState.UNHEALTHY: "red",
            HealthState.UNKNOWN: "gray"
        }
        
        return {
            "entity_id": data.get("id"),
            "entity_name": data.get("name"),
            "state": health_state.value,
            "state_code": health_state.name,
            "state_color": state_colors[health_state],
            "timestamp": data.get("properties", {}).get("timestamp", datetime.now(timezone.utc).isoformat()),
            "signals": data.get("properties", {}).get("signals", []),
            "details": data.get("properties", {})
        }
    
    def _error_response(self, entity_id: str, error: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "entity_id": entity_id,
            "state": HealthState.UNKNOWN.value,
            "state_code": HealthState.UNKNOWN.name,
            "state_color": "gray",
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Example usage functions
def example_get_entity_health():
    """Example: Get health state of a specific entity"""
    client = HealthStateClient(
        subscription_id="<your-subscription-id>",
        resource_group="<your-resource-group>",
        health_model_name="<your-health-model>",
        auth_token="<your-auth-token>"
    )
    
    # Get current health state
    health = client.get_entity_health_state("database-entity")
    print(f"Entity Health: {health['state_color']} - {health['state']}")
    
    # Get root workload health
    root_health = client.get_root_entity_health()
    print(f"Workload Health: {root_health['state_color']} - {root_health['state']}")


def example_get_health_timeline():
    """Example: Get health timeline over 24 hours"""
    client = HealthStateClient(
        subscription_id="<your-subscription-id>",
        resource_group="<your-resource-group>",
        health_model_name="<your-health-model>",
        auth_token="<your-auth-token>"
    )
    
    timeline = client.get_entity_health_timeline("api-service")
    for data_point in timeline:
        print(f"{data_point['timestamp']}: {data_point['state_color']}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
