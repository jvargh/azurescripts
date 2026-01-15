#!/usr/bin/env python
"""
Explore the health model data plane API to find correct endpoints
"""

import sys
import requests
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from config.env_loader import load_env
import subprocess

def main():
    # Load config
    env = load_env()
    if not env.validate():
        print("Error: Invalid environment configuration")
        return False
    
    # Get auth token
    result = subprocess.run(
        "az account get-access-token --query accessToken -o tsv",
        capture_output=True,
        text=True,
        check=True,
        shell=True
    )
    auth_token = result.stdout.strip()
    
    # Get health model details
    sub_id = env.get("AZURE_SUBSCRIPTION_ID")
    rg = env.get("AZURE_RESOURCE_GROUP")
    hm_name = env.get("HEALTH_MODEL_NAME")
    
    management_url = f"https://management.azure.com/subscriptions/{sub_id}/resourceGroups/{rg}/providers/Microsoft.CloudHealth/healthmodels/{hm_name}?api-version=2025-05-01-preview"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*70}")
    print(f"  Exploring Health Model API: {hm_name}")
    print(f"{'='*70}\n")
    
    # Get health model to find dataplane endpoint
    print("📋 Fetching health model details...")
    response = requests.get(management_url, headers=headers)
    response.raise_for_status()
    
    hm_details = response.json()
    dataplane_endpoint = hm_details["properties"]["dataplaneEndpoint"]
    
    print(f"✓ Health Model: {hm_name}")
    print(f"✓ Data Plane Endpoint: {dataplane_endpoint}")
    print(f"✓ Provisioning State: {hm_details['properties']['provisioningState']}")
    print(f"\n📊 Discovery Settings:")
    print(f"  Scope: {hm_details['properties']['discovery']['scope']}")
    print(f"  Add Recommended Signals: {hm_details['properties']['discovery']['addRecommendedSignals']}")
    
    # Try common endpoints
    print(f"\n🔍 Testing common endpoints...")
    
    test_paths = [
        "",
        "entities",
        "v1/entities",
        "healthmodel/entities",
        "api/entities",
        "signals",
        "metrics"
    ]
    
    for path in test_paths:
        test_url = f"{dataplane_endpoint.rstrip('/')}/{path}"
        if path:
            test_url += "?api-version=2025-05-01-preview"
        
        try:
            print(f"\n  Testing: {path or '(root)'}")
            resp = requests.get(test_url, headers=headers, timeout=5)
            print(f"    Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"    ✓ SUCCESS!")
                try:
                    data = resp.json()
                    print(f"    Response keys: {list(data.keys())}")
                    if isinstance(data, dict) and 'value' in data:
                        print(f"    Items: {len(data['value'])}")
                except:
                    print(f"    Response length: {len(resp.text)} bytes")
            elif resp.status_code == 404:
                print(f"    ✗ Not found")
            else:
                print(f"    ⚠ {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"    ⚠ Error: {e}")
    
    print(f"\n{'='*70}")
    print("  Exploration Complete")
    print(f"{'='*70}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
