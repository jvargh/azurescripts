# Azure Health Model Integration

Query and monitor Azure Health Models in real-time using Python.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Setup](#setup)
3. [API Reference](#api-reference)
4. [Code Examples](#code-examples)
5. [Configuration](#configuration)
6. [Architecture](#architecture)
7. [Current Status](#current-status)
8. [Example Output](#example-output)

---

## Quick Start

Get started in 2 minutes:

### Prerequisites
- Python 3.8+
- Azure CLI installed and authenticated (`az login`)
- Access to Azure subscription with a health model

### Installation

```bash
# Step 1: Copy the environment template and configure with your Azure values
cp .env.template .env
# Edit .env and fill in your Azure subscription, resource group, and health model name

# Step 2: Install dependencies
pip install -r requirements.txt

# Run setup and query (all-in-one)
python run.py
```

### One-Command Setup & Query

The fastest way to validate and query your health model:

```bash
python run.py
```

This single command will:
- ✅ Validate environment configuration
- ✅ Test Azure authentication
- ✅ Query all entities and their health states
- ✅ Show overall workload health
- ✅ Display health summary with statistics

### First Query (Manual)

```python
from src.integration import HealthModelBuilder

# Load from .env file
integration = HealthModelBuilder.create_from_env()

# Get all entity health states
entities = integration.get_all_entities_health()

for entity_id, health in entities.items():
    print(f"{health['details']['displayName']}: {health['state_color']}")
```

### Available Scripts

| Script | Purpose |
|--------|---------|
| `python run.py` | **All-in-one**: Validate setup + query health (recommended) |
| `python setup.py` | Verify configuration and authentication only |
| `python query_health_model.py` | Detailed health model query |
| `python demo.py` | Quick health status demo |

---

## Setup

### Environment Configuration

The `.env` file in the project root contains your Azure credentials:

```ini
# Azure Subscription ID
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Azure Resource Group
AZURE_RESOURCE_GROUP=your-resource-group

# Health Model Name
HEALTH_MODEL_NAME=your-health-model-name

# Optional: Azure Tenant ID
AZURE_TENANT_ID=

# Optional: Pre-configured auth token (otherwise fetched from Azure CLI)
AZURE_AUTH_TOKEN=
```

**Note:** If the `.env` file doesn't exist, the system will automatically create a template file for you. Simply edit it with your Azure values.

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_SUBSCRIPTION_ID` | ✅ Yes | Azure subscription ID |
| `AZURE_RESOURCE_GROUP` | ✅ Yes | Resource group containing the health model |
| `HEALTH_MODEL_NAME` | ✅ Yes | Name of the health model |
| `AZURE_TENANT_ID` | ❌ No | Tenant ID (uses default if not set) |
| `AZURE_AUTH_TOKEN` | ❌ No | Pre-configured token (fetched from Azure CLI if not set) |

### Verification

Run the all-in-one script to validate and query:

```bash
python run.py
```

Or verify configuration only:

```bash
python setup.py
```

Expected output:
- ✓ Environment configuration loaded
- ✓ Authentication token obtained
- ✓ Integration initialized
- ✓ Health query successful

---


## Azure REST APIs Used

This integration uses the following Azure Management REST APIs:

### Base API Configuration
- **Provider**: `Microsoft.CloudHealth`
- **Resource Type**: `healthmodels`
- **API Version**: `2025-05-01-preview`
- **Authentication**: Azure Management API Bearer Token
- **Base URL**: `https://management.azure.com`

### Primary Endpoints

#### 1. Get All Entities Health (Main API)
```
GET /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.CloudHealth/healthmodels/{healthModelName}/entities?api-version=2025-05-01-preview
```

**Purpose**: Retrieves health state of all entities in the health model

**Response**: Array of entities with:
- Entity ID and name
- Health state (Healthy/Degraded/Unhealthy/Unknown)
- Resource type (e.g., Microsoft.Web/sites)
- Signals and metrics
- Timestamp

**Used by**: `get_all_entities_health()` - Primary function in `run.py`

#### 2. Get Single Entity Health
```
GET /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.CloudHealth/healthmodels/{healthModelName}/entities/{entityId}?api-version=2025-05-01-preview
```

**Purpose**: Retrieves health state of a specific entity

**Used by**: `get_entity_health()`, `get_workload_health()`

#### 3. Get Entity Health Timeline (Optional)
```
GET /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.CloudHealth/healthmodels/{healthModelName}/entities/{entityId}/timeline?api-version=2025-05-01-preview&startTime={iso8601}&endTime={iso8601}&intervalMinutes=5
```

**Purpose**: Retrieves historical health states over time

**Used by**: `get_entity_health_timeline()` - Available but not used in main demo

### Authentication

The integration uses Azure CLI for authentication:

```bash
az account get-access-token --resource https://management.azure.com
```

This returns a bearer token that is automatically included in all API requests.

### API Response Format

All endpoints return JSON with this structure:

```json
{
  "id": "/subscriptions/.../entities/{entityId}",
  "name": "entity-name",
  "type": "Microsoft.CloudHealth/healthmodels/entities",
  "properties": {
    "healthState": "Healthy",
    "displayName": "sre-demo-app",
    "kind": "Microsoft.Web/sites",
    "impact": "Standard",
    "timestamp": "2026-01-15T...",
    "signals": []
  }
}
```

### Health State Mapping

The integration normalizes health states to color codes:

| API State | Enum | Color Code | Emoji |
|-----------|------|------------|-------|
| Healthy | HEALTHY | green | 🟢 |
| Degraded | DEGRADED | amber | 🟡 |
| Unhealthy | UNHEALTHY | red | 🔴 |
| Unknown | UNKNOWN | gray | ⚪ |

### Example API Flow

1. **Authenticate**: `az account get-access-token` → Bearer token
2. **Query All Entities**: `GET .../entities` → Returns all entities
3. **Normalize**: Map health states to colors
4. **Aggregate**: Calculate summary statistics (healthy/degraded/unhealthy counts)
5. **Display**: Show formatted results with emojis

---

## API Reference

### HealthModelBuilder

Factory class for creating health model integrations.

#### `create_from_env(health_model_name=None)`

Creates an integration from the `.env` file.

```python
integration = HealthModelBuilder.create_from_env()
```

**Parameters:**
- `health_model_name` (str, optional): Override the health model name from .env

**Returns:** `HealthModelIntegration` instance

---

### HealthModelIntegration

Main class for interacting with the health model.

#### `get_all_entities_health() -> Dict[str, Dict[str, Any]]`

Get health state of all entities in the model.

```python
entities = integration.get_all_entities_health()
```

**Returns:** Dictionary mapping entity IDs to health states

**Response Format:**
```python
{
    "entity_id": {
        "entity_id": "/subscriptions/.../entities/...",
        "entity_name": "unique-name",
        "state": "Healthy",  # "Healthy", "Degraded", "Unhealthy", "Unknown"
        "state_code": "HEALTHY",
        "state_color": "green",  # "green", "amber", "red", "gray"
        "timestamp": "2026-01-15T22:14:25.412215",
        "signals": {...},
        "details": {
            "displayName": "sre-demo-app",
            "kind": "Microsoft.Web/sites",
            "healthState": "Healthy",
            "impact": "Standard"
        }
    }
}
```

#### `get_entity_health(entity_id: str) -> Dict[str, Any]`

Get health state of a specific entity.

```python
health = integration.get_entity_health("22b8c8ff-da68-affb-1ce4-6c6575879a06")
```

**Parameters:**
- `entity_id` (str): The entity's unique identifier

**Returns:** Health state dictionary (same format as above)

#### `get_workload_health() -> Dict[str, Any]`

Get overall workload health (root entity).

```python
workload = integration.get_workload_health()
print(f"Overall status: {workload['state_color']}")
```

**Returns:** Health state of the root entity

#### `get_health_summary() -> Dict[str, Any]`

Get aggregated health statistics.

```python
summary = integration.get_health_summary()
print(f"Healthy: {summary['healthy_count']}")
print(f"Degraded: {summary['degraded_count']}")
```

**Returns:**
```python
{
    "total_entities": 4,
    "healthy_count": 2,
    "degraded_count": 1,
    "unhealthy_count": 0,
    "unknown_count": 1,
    "health_percentages": {
        "healthy": 50.0,
        "degraded": 25.0,
        "unhealthy": 0.0,
        "unknown": 25.0
    }
}
```

---

### HealthStateClient

Low-level REST API client for Azure Health Models.

#### Constructor

```python
from src.api.health_state_client import HealthStateClient

client = HealthStateClient(
    subscription_id="your-subscription-id",
    resource_group="your-resource-group",
    health_model_name="your-health-model",
    auth_token="your-bearer-token"
)
```

#### `get_entity_health_state(entity_id: str) -> Dict[str, Any]`

Query health state via REST API.

```python
health = client.get_entity_health_state("entity-name")
```

#### `get_all_entities_health() -> Dict[str, Dict[str, Any]]`

Get all entities via REST API.

```python
all_entities = client.get_all_entities_health()
```

#### REST API Details

**Base URL:** `https://management.azure.com`

**Endpoint Pattern:**
```
/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.CloudHealth/healthmodels/{healthModelName}/entities/{entityName}
```

**API Version:** `2025-05-01-preview`

**Authentication:** Bearer token (Azure Management API)

---

## Code Examples

### Example 1: Get All Entity Health States

```python
from src.integration import HealthModelBuilder

integration = HealthModelBuilder.create_from_env()
entities = integration.get_all_entities_health()

for entity_id, health in entities.items():
    display_name = health['details'].get('displayName', 'Unknown')
    state = health['state_color']
    
    emoji = {"green": "🟢", "amber": "🟡", "red": "🔴", "gray": "⚪"}[state]
    print(f"{emoji} {display_name}: {health['state']}")
```

### Example 2: Monitor Specific Entity

```python
from src.integration import HealthModelBuilder
import time

integration = HealthModelBuilder.create_from_env()

# Get entity ID from listing
entities = integration.get_all_entities_health()
app_service_id = [eid for eid, e in entities.items() 
                  if 'Web/sites' in e['details'].get('kind', '')][0]

# Monitor every 30 seconds
while True:
    health = integration.get_entity_health(app_service_id)
    print(f"Status: {health['state_color']} at {health['timestamp']}")
    time.sleep(30)
```

### Example 3: Health Dashboard

```python
from src.integration import HealthModelBuilder

integration = HealthModelBuilder.create_from_env()
summary = integration.get_health_summary()

print("=" * 50)
print("  Health Dashboard")
print("=" * 50)
print(f"Total Entities: {summary['total_entities']}")
print(f"🟢 Healthy:    {summary['healthy_count']} ({summary['health_percentages']['healthy']:.1f}%)")
print(f"🟡 Degraded:   {summary['degraded_count']} ({summary['health_percentages']['degraded']:.1f}%)")
print(f"🔴 Unhealthy:  {summary['unhealthy_count']} ({summary['health_percentages']['unhealthy']:.1f}%)")
print(f"⚪ Unknown:    {summary['unknown_count']} ({summary['health_percentages']['unknown']:.1f}%)")
```

### Example 4: Export Health Report

```python
from src.integration import HealthModelBuilder
import json
from datetime import datetime

integration = HealthModelBuilder.create_from_env()
entities = integration.get_all_entities_health()

report = {
    "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
    "summary": integration.get_health_summary(),
    "entities": [
        {
            "name": e['details'].get('displayName'),
            "type": e['details'].get('kind'),
            "health": e['state'],
            "color": e['state_color']
        }
        for e in entities.values()
    ]
}

with open('health_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Report saved to health_report.json")
```

### Example 5: Alert on Degraded Services

```python
from src.integration import HealthModelBuilder

integration = HealthModelBuilder.create_from_env()
entities = integration.get_all_entities_health()

degraded_or_unhealthy = [
    e for e in entities.values()
    if e['state_color'] in ['amber', 'red']
]

if degraded_or_unhealthy:
    print(f"⚠️  ALERT: {len(degraded_or_unhealthy)} services need attention!")
    for entity in degraded_or_unhealthy:
        name = entity['details'].get('displayName')
        state = entity['state']
        print(f"  - {name}: {state}")
else:
    print("✅ All services healthy!")
```

### Example 6: Using Context Manager

```python
from src.integration import HealthModelBuilder

with HealthModelBuilder.create_from_env() as integration:
    health = integration.get_workload_health()
    print(f"Workload: {health['state_color']}")
# Auto-cleanup on exit
```

---

## Configuration

### Project Structure

```
OD-HealthModel/
├── .env                          # Configuration (DO NOT COMMIT)
├── .gitignore                    # Excludes .env and sensitive files
├── demo.py                       # Quick demo script
├── setup.py                      # Setup verification
├── query_health_model.py         # Detailed query script
├── requirements.txt              # Python dependencies
├── DOCUMENTATION.md              # This file
│
├── src/
│   ├── api/
│   │   └── health_state_client.py    # REST API client
│   ├── config/
│   │   └── env_loader.py             # Environment loader
│   ├── models/
│   │   └── health_model_config.py    # Entity configuration
│   ├── signals/
│   │   └── health_signals.py         # Health signal definitions
│   └── integration.py                # Main integration
│
└── examples/
    └── health_dashboard.py           # Dashboard example
```

### Dependencies

**requirements.txt:**
```
requests>=2.31.0
python-dotenv>=1.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

### Security

**Important:** Never commit your `.env` file!

The `.gitignore` is configured to exclude:
- `.env` and `.env.*` files
- `__pycache__/` directories
- `*.pyc` files
- Build artifacts

### Authentication

The integration uses Azure CLI for authentication by default:

1. Ensure Azure CLI is installed: `az --version`
2. Login to Azure: `az login`
3. Set your subscription: `az account set --subscription <subscription-id>`

Alternatively, provide a pre-configured token in `.env`:
```ini
AZURE_AUTH_TOKEN=your-bearer-token
```

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              HealthModelIntegration                      │
│  (Unified interface for health model operations)        │
└───────┬──────────────────────────┬──────────────────────┘
        │                          │
        ▼                          ▼
┌──────────────────┐    ┌───────────────────────┐
│ HealthStateClient│    │ Health Configuration  │
│  (REST API)      │    │  (Models & Signals)   │
└─────────┬────────┘    └───────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│      Azure Health Models REST API                       │
│  (Microsoft.CloudHealth/healthmodels)                   │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. HealthStateClient
- Low-level REST API client
- Handles authentication
- Makes HTTP requests to Azure
- Normalizes responses

#### 2. HealthModelIntegration
- High-level interface
- Aggregates data from multiple sources
- Provides convenience methods
- Manages configuration

#### 3. EnvLoader
- Loads configuration from `.env`
- Validates required settings
- Provides Azure CLI integration

#### 4. Health Signals & Models
- Define health metrics
- Configure entity relationships
- Set thresholds and rules

### Data Flow

```
1. User calls integration.get_all_entities_health()
                    ↓
2. Integration uses HealthStateClient
                    ↓
3. Client makes REST API call to Azure
                    ↓
4. Azure returns health model data
                    ↓
5. Client normalizes response (maps states to colors)
                    ↓
6. Integration aggregates and enriches data
                    ↓
7. Returns formatted result to user
```

### API Endpoint Structure

**Management Plane (used by this integration):**
```
https://management.azure.com/
  subscriptions/{subscriptionId}/
  resourceGroups/{resourceGroupName}/
  providers/Microsoft.CloudHealth/
  healthmodels/{healthModelName}/
  entities/{entityName}
?api-version=2025-05-01-preview
```

**Authentication:** Azure Management API bearer token

**HTTP Method:** GET

**Response Format:** JSON

---

## Current Status

### ✅ What's Working

1. **REST API Integration**
   - ✓ Query all entities in health model
   - ✓ Query specific entity by ID
   - ✓ Get health states (green/amber/red/gray)
   - ✓ Access entity metadata (name, type, signals)

2. **Authentication**
   - ✓ Azure CLI integration
   - ✓ Bearer token support
   - ✓ Automatic token retrieval

3. **Configuration**
   - ✓ Environment variable loading from `.env`
   - ✓ Validation of required settings
   - ✓ Secure credential management

4. **Health Data**
   - ✓ Real-time health state queries
   - ✓ Entity discovery from service groups
   - ✓ Health aggregation and reporting
   - ✓ Color-coded status (green/amber/red)

### 📊 Example Health Model Data

**Entities discovered from sre-demo-hm:**

| Entity | Type | Status |
|--------|------|--------|
| sre-demo-app-jv12345 | Microsoft.Web/sites | 🟢 Healthy |
| sre-demo-app-jv12345-plan | Microsoft.Web/serverFarms | 🟡 Degraded |
| staging | Microsoft.Web/sites/slots | ⚪ Unknown |
| sre-demo-hm | System_HealthModelRoot | 🟢 Healthy |

### 🔧 Health Model Configuration

**Health Model:** sre-demo-hm
- **Location:** canadacentral
- **API Version:** 2025-05-01-preview
- **Provider:** Microsoft.CloudHealth/healthmodels
- **Discovery:** Automatic from service group "sre-demo-app"

### 🚀 Available Scripts

| Script | Purpose |
|--------|---------|
| `python demo.py` | Quick demo showing current health |
| `python setup.py` | Verify setup and configuration |
| `python query_health_model.py` | Detailed health model query |
| `python src/config/env_loader.py` | Test environment loading |

### 📚 Additional Resources

- **Azure Health Models Documentation:** Search for "Microsoft.CloudHealth" in Azure docs
- **REST API Reference:** [Microsoft Learn - HealthModelResource](https://learn.microsoft.com/en-us/dotnet/api/azure.resourcemanager.cloudhealth.healthmodelresource.gethealthmodelentity)
- **.NET SDK:** Azure.ResourceManager.CloudHealth v1.0.0-beta.1

### 🎯 Next Steps

1. **Explore your health model in Azure Portal**
   - Navigate to portal.azure.com
   - Go to Resource Groups → sre-demo-rg
   - Open the sre-demo-hm health model

2. **Customize the integration**
   - Add custom health signals
   - Configure entity relationships
   - Set up alerting logic

3. **Build automation**
   - Schedule health checks
   - Integrate with monitoring systems
   - Create dashboards and reports

---

## Troubleshooting

### Common Issues

#### Issue: "Environment validation failed"
**Solution:** Check that all required variables are set in `.env`:
- AZURE_SUBSCRIPTION_ID
- AZURE_RESOURCE_GROUP
- HEALTH_MODEL_NAME

#### Issue: "Failed to authenticate"
**Solution:** 
1. Run `az login` to authenticate
2. Verify you're in the correct subscription: `az account show`
3. Set subscription if needed: `az account set --subscription <id>`

#### Issue: "404 Not Found" errors
**Solution:** 
- Verify the health model exists: `az resource list --resource-group <rg-name>`
- Check the health model name matches exactly
- Ensure you have access to the resource group

#### Issue: "Module not found" errors
**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: ".env file not found"
**Solution:**
The system automatically creates a template `.env` file. Edit it with your Azure configuration values.

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from src.integration import HealthModelBuilder
integration = HealthModelBuilder.create_from_env()
```

---
## Health Model Graph
<img width="894" height="463" alt="image" src="https://github.com/user-attachments/assets/82e6410a-65cd-477f-a53c-549bd779643e" />

## Example Output

Here's what you'll see when running `python run.py`:

```
======================================================================
  Azure Health Model Integration
======================================================================

======================================================================
  Azure Health Model - Setup Validation
======================================================================

2026-01-15 17:40:58,344 - INFO - Step 1: Loading environment configuration...
2026-01-15 17:40:58,351 - INFO - ✓ Environment configuration loaded successfully

  Subscription ID:    463a82d4-1896-4332-aeeb-618ee5a5aa93
  Resource Group:     sre-demo-rg
  Health Model Name:  sre-demo-hm

2026-01-15 17:40:58,351 - INFO -
Step 2: Testing Azure authentication...
2026-01-15 17:40:58,353 - INFO -   Attempting to get token from Azure CLI...
2026-01-15 17:41:02,069 - INFO - ✓ Authentication token obtained successfully
2026-01-15 17:41:02,069 - INFO - 
✓ Setup validation complete!

======================================================================
  Health Model Query
======================================================================

📁 Loading integration from .env...
✓ Integration loaded

📊 All Entities Health Status:
  Total Entities: 4

  🟢 sre-demo-app-jv12345
     State: Healthy (GREEN)
     Type: Microsoft.Web/sites

  ⚪ staging
     State: Unknown (GRAY)
     Type: Microsoft.Web/sites/slots

  🟡 sre-demo-app-jv12345-plan
     State: Degraded (AMBER)
     Type: Microsoft.Web/serverFarms

  🟢 sre-demo-hm
     State: Healthy (GREEN)
     Type: System_HealthModelRoot

🎯 Overall Workload Health:
  🟢 Healthy (GREEN)

📈 Health Summary:
  Total Entities: 4
  🟢 Healthy:   2 (50.0%)
  🟡 Degraded:  1 (25.0%)
  🔴 Unhealthy: 0 (0.0%)
  ⚪ Unknown:   1 (25.0%)

======================================================================
  Query Complete
======================================================================

✅ All operations completed successfully!
```

---

## Contributing

To extend or modify the integration:

1. **Add new API methods:** Edit `src/api/health_state_client.py`
2. **Add integration features:** Edit `src/integration.py`
3. **Update configuration:** Modify `src/config/env_loader.py`
4. **Add examples:** Create scripts in root or `examples/` directory

---

## License

See LICENSE file for details.

---

## Support

For questions or issues:
1. Check this documentation
2. Run `python run.py` to validate your setup
3. Review the example scripts (demo.py, query_health_model.py)
4. Check Azure Health Models documentation

---

*Last Updated: January 15, 2026*
*Version: 1.0.0*


