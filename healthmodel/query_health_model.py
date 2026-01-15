#!/usr/bin/env python
"""
Quick script to query the existing sre-demo-hm health model
"""

import sys
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from integration import HealthModelBuilder

def print_tree(entity, indent=0):
    """Print entity tree"""
    prefix = "  " * indent
    state = entity.get("state", "Unknown")
    state_color = entity.get("state_color", "gray").upper()
    name = entity.get("name", entity.get("id", "Unknown"))
    
    print(f"{prefix}├─ {name}: {state} ({state_color})")
    
    for child in entity.get("children", []):
        print_tree(child, indent + 1)


def main():
    print("\n" + "=" * 70)
    print("  Querying Existing Health Model: sre-demo-hm")
    print("=" * 70 + "\n")
    
    try:
        # Create integration from .env
        print("📁 Loading integration from .env...")
        integration = HealthModelBuilder.create_from_env()
        print("✓ Integration loaded\n")
        
        # Get all entities first
        print("📊 All Entities Health Status:")
        try:
            all_entities = integration.get_all_entities_health()
            print(f"  Total Entities: {len(all_entities)}")
            print()
            for entity_id, entity_health in all_entities.items():
                state = entity_health.get('state', 'Unknown')
                state_color = entity_health.get('state_color', 'gray').upper()
                display_name = entity_health.get('details', {}).get('displayName', entity_id)
                kind = entity_health.get('details', {}).get('kind', 'Unknown')
                
                # Color emoji
                color_emoji = "🟢" if state_color == "GREEN" else "🟡" if state_color == "AMBER" else "🔴" if state_color == "RED" else "⚪"
                
                print(f"  {color_emoji} {display_name}")
                print(f"     State: {state} ({state_color})")
                print(f"     Type: {kind}")
                print(f"     ID: {entity_id}")
                print()
        except Exception as e:
            print(f"  ⚠ Could not retrieve entities: {e}")
        
        # Get health tree
        print("🌳 Entity Hierarchy:")
        try:
            tree = integration.get_health_tree()
            if tree:
                print_tree(tree)
            else:
                print("  (No root entity found)")
        except Exception as e:
            print(f"  ⚠ Could not retrieve entity tree: {e}")
        
        # Get health summary
        print("📈 Health Summary:")
        try:
            summary = integration.get_health_summary()
            print(f"  Total Entities: {summary.get('total_entities', 0)}")
            print(f"  🟢 Healthy: {summary.get('healthy_count', 0)}")
            print(f"  🟡 Degraded: {summary.get('degraded_count', 0)}")
            print(f"  🔴 Unhealthy: {summary.get('unhealthy_count', 0)}")
            print(f"  ⚪ Unknown: {summary.get('unknown_count', 0)}")
        except Exception as e:
            print(f"  ⚠ Could not retrieve summary: {e}")
        
        # Get configuration details
        print("\n⚙️ Configuration Details:")
        try:
            config = integration.config
            print(f"  Entities Configured: {len(config.entities)}")
            print(f"  Entity Types: {set(e.entity_type.value for e in config.entities.values())}")
        except Exception as e:
            print(f"  ⚠ Could not retrieve config: {e}")
        
        print("\n" + "=" * 70)
        print("  Query Complete")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
