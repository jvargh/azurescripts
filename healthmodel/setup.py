#!/usr/bin/env python
"""
Quick Setup Script for Health Model Integration

Uses .env file to initialize and test health model integration.
Run this script to verify your configuration is correct.
"""

import sys
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main setup function"""
    
    print("\n" + "=" * 70)
    print("  Azure Health Model Integration - Setup")
    print("=" * 70 + "\n")
    
    # Step 1: Load environment
    logger.info("Step 1: Loading environment configuration from .env file...")
    try:
        from config.env_loader import load_env
        
        env = load_env()
        
        if not env.validate():
            logger.error("✗ Environment validation failed")
            return False
        
        logger.info("✓ Environment configuration loaded successfully")
        config = env.get_azure_config()
        
        print(f"\n  Subscription ID:    {config['subscriptionId']}")
        print(f"  Resource Group:     {config['resourceGroup']}")
        print(f"  Health Model Name:  {config['healthModelName']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to load environment: {e}")
        return False
    
    # Step 2: Test Azure authentication
    logger.info("\nStep 2: Testing Azure authentication...")
    try:
        auth_token = env.get("AZURE_AUTH_TOKEN")
        if not auth_token:
            logger.info("  Attempting to get token from Azure CLI...")
            import subprocess
            result = subprocess.run(
                "az account get-access-token --query accessToken -o tsv",
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            auth_token = result.stdout.strip()
        
        if auth_token:
            logger.info("✓ Authentication token obtained successfully")
        else:
            logger.error("✗ Failed to obtain authentication token")
            return False
        
    except Exception as e:
        logger.error(f"✗ Failed to authenticate: {e}")
        logger.info("  Hint: Run 'az login' to authenticate with Azure")
        return False
    
    # Step 3: Initialize health model integration
    logger.info("\nStep 3: Initializing health model integration...")
    try:
        from integration import HealthModelBuilder
        
        logger.info("  Creating integration from environment variables...")
        integration = HealthModelBuilder.create_from_env()
        
        logger.info("✓ Integration initialized successfully")
        
        # Step 4: Query health
        logger.info("\nStep 4: Testing health query...")
        try:
            workload_health = integration.get_workload_health()
            logger.info("✓ Health query successful")
            
            print(f"\n  Workload Health Status: {workload_health['state_color'].upper()}")
            print(f"  State: {workload_health['state']}")
            
        except Exception as e:
            logger.warning(f"⚠ Health query test: {e}")
            logger.info("  Note: This is expected if health model doesn't exist yet")
        
        # Step 5: Display usage information
        logger.info("\nStep 5: Setup complete!")
        
        print("\n" + "=" * 70)
        print("  ✓ Setup Successful!")
        print("=" * 70)
        
        print("\nNext steps:")
        print("  1. Run the dashboard:")
        print("     python examples/health_dashboard.py")
        print("\n  2. Query health from Python:")
        print("     from integration import HealthModelBuilder")
        print("     integration = HealthModelBuilder.create_from_env()")
        print("     health = integration.get_workload_health()")
        print("     print(health['state_color'])")
        print("\n  3. Check documentation:")
        print("     - README.md - Complete documentation")
        print("     - QUICK_REFERENCE.md - Common tasks")
        print("     - PROJECT_OVERVIEW.md - High-level overview")
        
        integration.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize integration: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)
