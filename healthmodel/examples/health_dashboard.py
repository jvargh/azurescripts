"""
Health Model Dashboard Example

Simple example showing how to create a health monitoring dashboard
that displays health states with refresh capabilities.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Dashboard(ABC):
    """Abstract base class for health dashboards"""
    
    @abstractmethod
    def render(self, data: Dict[str, Any]) -> None:
        """Render dashboard with health data"""
        pass


class ConsoleDashboard(Dashboard):
    """Console-based health dashboard"""
    
    def render(self, data: Dict[str, Any]) -> None:
        """Display health data in console"""
        self._clear_screen()
        self._render_header()
        self._render_summary(data.get("summary", {}))
        self._render_entities(data.get("health_tree", {}))
        self._render_footer(data.get("generated_at"))
    
    def _clear_screen(self) -> None:
        """Clear console screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _render_header(self) -> None:
        """Render dashboard header"""
        print("\n" + "=" * 80)
        print(" " * 20 + "HEALTH MODEL DASHBOARD")
        print("=" * 80 + "\n")
    
    def _render_summary(self, summary: Dict[str, Any]) -> None:
        """Render health summary"""
        if not summary:
            return
        
        counts = summary.get("health_counts", {})
        percentages = summary.get("health_percentages", {})
        
        print("HEALTH SUMMARY")
        print("-" * 80)
        print(f"  Healthy:   {counts.get('healthy', 0):3d} ({percentages.get('healthy', 0):5.1f}%) " + 
              self._get_bar("healthy", percentages.get("healthy", 0)))
        print(f"  Degraded:  {counts.get('degraded', 0):3d} ({percentages.get('degraded', 0):5.1f}%) " + 
              self._get_bar("degraded", percentages.get("degraded", 0)))
        print(f"  Unhealthy: {counts.get('unhealthy', 0):3d} ({percentages.get('unhealthy', 0):5.1f}%) " + 
              self._get_bar("unhealthy", percentages.get("unhealthy", 0)))
        print()
    
    def _render_entities(self, tree: Dict[str, Any]) -> None:
        """Render entity health tree"""
        if not tree:
            return
        
        print("ENTITY HEALTH")
        print("-" * 80)
        
        # Group by state
        by_state = {"green": [], "amber": [], "red": [], "gray": []}
        
        for entity_id, entity_data in tree.items():
            color = entity_data.get("state_color", "gray")
            if color in by_state:
                by_state[color].append((entity_id, entity_data))
        
        # Render green entities
        if by_state["green"]:
            print("✓ HEALTHY (Green)")
            for entity_id, data in by_state["green"]:
                self._render_entity_row(data, "✓")
        
        # Render amber entities
        if by_state["amber"]:
            print("\n⚠ DEGRADED (Amber)")
            for entity_id, data in by_state["amber"]:
                self._render_entity_row(data, "⚠")
        
        # Render red entities
        if by_state["red"]:
            print("\n✗ UNHEALTHY (Red)")
            for entity_id, data in by_state["red"]:
                self._render_entity_row(data, "✗")
        
        print()
    
    def _render_entity_row(self, entity: Dict[str, Any], icon: str) -> None:
        """Render single entity row"""
        name = entity.get("name", "Unknown")
        state = entity.get("state", "Unknown")
        entity_type = entity.get("type", "unknown")
        
        print(f"  {icon} {name:30s} [{state:12s}] ({entity_type})")
    
    def _get_bar(self, state: str, percentage: float) -> str:
        """Get progress bar for percentage"""
        bar_length = 30
        filled = int(bar_length * percentage / 100)
        
        if state == "healthy":
            char = "█"
        elif state == "degraded":
            char = "▓"
        else:
            char = "░"
        
        return f"[{char * filled}{' ' * (bar_length - filled)}]"
    
    def _render_footer(self, timestamp: str) -> None:
        """Render dashboard footer"""
        print("-" * 80)
        if timestamp:
            print(f"Updated: {timestamp}")
        print("=" * 80 + "\n")


class HealthDashboardApp:
    """Health dashboard application"""
    
    def __init__(self, integration, refresh_interval: int = 60):
        """
        Initialize dashboard app
        
        Args:
            integration: HealthModelIntegration instance
            refresh_interval: Refresh interval in seconds
        """
        self.integration = integration
        self.refresh_interval = refresh_interval
        self.dashboard = ConsoleDashboard()
        self.running = False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Collect all data for dashboard"""
        try:
            return {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": self.integration.get_health_summary(),
                "health_tree": self.integration.get_health_tree()
            }
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    def run_once(self) -> None:
        """Run dashboard once"""
        data = self.get_dashboard_data()
        self.dashboard.render(data)
    
    def run_continuous(self) -> None:
        """Run dashboard with continuous updates"""
        self.running = True
        logger.info(f"Starting dashboard (refresh every {self.refresh_interval}s)")
        
        try:
            while self.running:
                self.run_once()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            logger.info("Dashboard stopped by user")
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop dashboard"""
        self.running = False
        logger.info("Dashboard stopped")


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

def run_dashboard_example():
    """Example: Run health dashboard"""
    from config.loader import load_settings
    from api.health_state_client import HealthStateClient
    from signals.health_signals import SignalCollection
    from models.health_model_config import create_ecommerce_health_model
    from integration import HealthModelIntegration
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    try:
        # Load configuration
        settings = load_settings()
        
        if not settings.validate():
            logger.error("Configuration validation failed. Please check settings.json")
            return
        
        azure_config = settings.get_azure_config()
        auth_token = settings.get_auth_token()
        
        if not auth_token:
            logger.error("Failed to get authentication token. Please run 'az login'")
            return
        
        logger.info("Creating health model integration...")
        
        # Create API client
        api_client = HealthStateClient(
            subscription_id=azure_config['subscriptionId'],
            resource_group=azure_config['resourceGroup'],
            monitor_account_name=azure_config['monitorAccountName'],
            health_model_name="od-health-model",
            auth_token=auth_token
        )
        
        # Load model and signals
        config = create_ecommerce_health_model()
        signals = SignalCollection.web_service_signals()
        signals.update(SignalCollection.database_signals())
        
        # Create integration
        integration = HealthModelIntegration(config, api_client, signals)
        
        # Create and run dashboard
        app = HealthDashboardApp(integration, refresh_interval=30)
        
        logger.info("Starting health dashboard...")
        print("\nPress Ctrl+C to stop the dashboard\n")
        
        # Run dashboard once for testing
        app.run_once()
        
        # Uncomment to run continuously:
        # app.run_continuous()
        
        # Close integration
        integration.close()
        
        logger.info("Dashboard example completed")
    
    except Exception as e:
        logger.error(f"Dashboard example failed: {e}", exc_info=True)


if __name__ == "__main__":
    run_dashboard_example()
