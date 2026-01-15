"""
Azure Health Model - Setup and Query

Combined script that validates setup and queries health model
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def validate_setup():
    """Validate environment and authentication"""
    print_header("Azure Health Model - Setup Validation")
    
    # Step 1: Load environment
    logger.info("Step 1: Loading environment configuration...")
    try:
        from config.env_loader import load_env
        env_loader = load_env()
        
        if not env_loader.validate():
            logger.error("✗ Environment validation failed")
            return False
        
        logger.info("✓ Environment configuration loaded successfully")
        
        config = env_loader.get_azure_config()
        print(f"\n  Subscription ID:    {config['subscriptionId']}")
        print(f"  Resource Group:     {config['resourceGroup']}")
        print(f"  Health Model Name:  {config['healthModelName']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to load environment: {e}")
        return False
    
    # Step 2: Test authentication
    logger.info("\nStep 2: Testing Azure authentication...")
    try:
        logger.info("  Attempting to get token from Azure CLI...")
        import subprocess
        result = subprocess.run(
            "az account get-access-token --resource https://management.azure.com",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"✗ Azure CLI authentication failed: {result.stderr}")
            return False
        
        logger.info("✓ Authentication token obtained successfully")
        
    except Exception as e:
        logger.error(f"✗ Authentication failed: {e}")
        return False
    
    logger.info("\n✓ Setup validation complete!")
    return True


def query_health_model():
    """Query and display health model data"""
    print_header("Health Model Query")
    
    try:
        from integration import HealthModelBuilder
        
        # Load integration
        print("📁 Loading integration from .env...")
        integration = HealthModelBuilder.create_from_env()
        print("✓ Integration loaded\n")
        
        # Get all entities
        print("📊 All Entities Health Status:")
        all_entities = integration.get_all_entities_health()
        print(f"  Total Entities: {len(all_entities)}\n")
        
        for entity_id, entity_health in all_entities.items():
            state = entity_health.get('state', 'Unknown')
            state_color = entity_health.get('state_color', 'gray').upper()
            display_name = entity_health.get('details', {}).get('displayName', entity_id)
            kind = entity_health.get('details', {}).get('kind', 'Unknown')
            
            # Color emoji
            color_emoji = {
                "GREEN": "🟢",
                "AMBER": "🟡",
                "RED": "🔴",
                "GRAY": "⚪"
            }.get(state_color, "⚪")
            
            print(f"  {color_emoji} {display_name}")
            print(f"     State: {state} ({state_color})")
            print(f"     Type: {kind}")
            print()
        
        # Get workload health
        print("🎯 Overall Workload Health:")
        workload = integration.get_workload_health()
        workload_state = workload.get('state', 'Unknown')
        workload_color = workload.get('state_color', 'gray').upper()
        workload_emoji = {
            "GREEN": "🟢",
            "AMBER": "🟡",
            "RED": "🔴",
            "GRAY": "⚪"
        }.get(workload_color, "⚪")
        print(f"  {workload_emoji} {workload_state} ({workload_color})\n")
        
        # Health summary
        print("📈 Health Summary:")
        summary = integration.get_health_summary()
        print(f"  Total Entities: {summary.get('total_entities', 0)}")
        print(f"  🟢 Healthy:   {summary.get('healthy_count', 0)} ({summary['health_percentages']['healthy']:.1f}%)")
        print(f"  🟡 Degraded:  {summary.get('degraded_count', 0)} ({summary['health_percentages']['degraded']:.1f}%)")
        print(f"  🔴 Unhealthy: {summary.get('unhealthy_count', 0)} ({summary['health_percentages']['unhealthy']:.1f}%)")
        print(f"  ⚪ Unknown:   {summary.get('unknown_count', 0)} ({summary['health_percentages']['unknown']:.1f}%)")
        
        print_header("Query Complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("  Azure Health Model Integration")
    print("=" * 70)
    
    # Validate setup
    if not validate_setup():
        print("\n❌ Setup validation failed. Please fix the issues above.")
        return 1
    
    # Query health model
    if not query_health_model():
        print("\n❌ Health query failed. Check the error details above.")
        return 1
    
    print("\n✅ All operations completed successfully!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
