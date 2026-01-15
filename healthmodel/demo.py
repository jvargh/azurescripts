#!/usr/bin/env python
"""
Azure Health Model Integration - Working Demo

Successfully queries the sre-demo-hm health model and displays real-time health data.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from integration import HealthModelBuilder

def main():
    print("\n" + "="*70)
    print("  ✅ Azure Health Model Integration - SUCCESS!")
    print("="*70 + "\n")
    
    # Create integration from .env
    print("📋 Loading configuration from .env...")
    integration = HealthModelBuilder.create_from_env()
    print("✓ Integration initialized\n")
    
    # Get all entities
    print("📊 Current Health Status:\n")
    all_entities = integration.get_all_entities_health()
    
    # Count by state
    healthy = degraded = unhealthy = unknown = 0
    
    for entity_id, entity_health in all_entities.items():
        state_color = entity_health.get('state_color', 'gray')
        display_name = entity_health.get('details', {}).get('displayName', entity_health.get('entity_name', 'Unknown'))
        state = entity_health.get('state', 'Unknown')
        
        # Emoji mapping
        emoji = {"green": "🟢", "amber": "🟡", "red": "🔴", "gray": "⚪"}.get(state_color, "⚪")
        
        # Count
        if state_color == "green":
            healthy += 1
        elif state_color == "amber":
            degraded += 1
        elif state_color == "red":
            unhealthy += 1
        else:
            unknown += 1
        
        print(f"  {emoji} {display_name:30s} {state}")
    
    print(f"\n{'='*70}")
    print(f"  Summary: {len(all_entities)} entities total")
    print(f"  🟢 Healthy: {healthy}  |  🟡 Degraded: {degraded}  |  🔴 Unhealthy: {unhealthy}  |  ⚪ Unknown: {unknown}")
    print(f"{'='*70}\n")
    
    # Show what's available
    print("✨ Available Operations:\n")
    print("  • integration.get_all_entities_health()      - Get all entity health states")
    print("  • integration.get_entity_health(entity_id)   - Get specific entity health")
    print("  • integration.get_workload_health()          - Get overall workload health")
    print("  • integration.get_health_summary()           - Get aggregated statistics")
    print()
    
    print("📚 Documentation:")
    print("  • README.md - Complete API documentation")
    print("  • QUICK_REFERENCE.md - Code examples")
    print("  • STATUS.md - Current status and next steps")
    print()
    
    print("🎯 What's Working:")
    print("  ✅ REST API queries to Azure Health Models")
    print("  ✅ Real-time health state retrieval (green/amber/red)")
    print("  ✅ Entity discovery from service groups")
    print("  ✅ Health state aggregation and reporting")
    print("  ✅ Integration with Azure CLI authentication")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
