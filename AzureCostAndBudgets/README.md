# Azure Budget Data Collection for FinOps

This solution provides a simplified approach to collecting Azure budget data across all resource groups using a single API call.

## Problem Statement

Collecting Azure budget data for FinOps reporting is complicated because:
1. **Power BI with Custom Connector** - Has limitations when updating reports in Power BI Online
2. **PowerShell per-RG iteration** - Requires querying each resource group individually, adding complexity with pipeline dependencies

## Solution

The Microsoft Consumption API supports querying budgets at the **subscription level**, which returns **all budgets in a single API call** — including those scoped to individual resource groups.

### API Endpoint
```
GET /subscriptions/{subscriptionId}/providers/Microsoft.Consumption/budgets?api-version=2024-08-01
```

## How It Works

When you call the subscription-level Budget API, it returns all budgets regardless of their scope:
- Subscription-level budgets
- Resource group-scoped budgets

The resource group name is embedded in each budget's resource ID, which we extract using pattern matching:
- `/subscriptions/.../resourceGroups/rg-production/providers/.../budgets/ProdBudget` → **rg-production**
- `/subscriptions/.../providers/.../budgets/SubBudget` → **(Subscription-level)**

## Data Fields Returned

| Field | Description |
|-------|-------------|
| Budget Name | Name of the budget |
| Resource Group Name | RG name (or "Subscription-level") |
| Budget Amount | The budget limit amount |
| Forecast Amount | Forecasted spend for the period |
| Budget Scope | Full resource ID of the budget |
| BudgetStartDate | Start date of the budget period |
| BudgetEndDate | End date of the budget period |

## Why This Approach Is Better

| Aspect | Old Approach (Per-RG Iteration) | New Approach (Single API Call) |
|--------|--------------------------------|-------------------------------|
| API Calls | 1 per resource group (could be 100+) | **1 total** |
| Execution Time | Minutes (depends on RG count) | **Seconds** |
| Complexity | Requires parallelism, token management | **Simple single request** |
| Rate Limiting Risk | Higher (many API calls) | **Minimal** |
| Power BI Compatibility | Requires custom connector or pipeline | **Direct REST query or export to storage** |

## Usage

### Prerequisites
- Azure PowerShell module (`Az`) installed
- Authenticated to Azure (`Connect-AzAccount`)
- Reader access to the subscription

### Running the Script

```powershell
.\GetBudgetSubLevel.ps1
```

### Sample Output

```
BudgetName                ResourceGroup        BudgetAmount ForecastAmount BudgetScope          StartDate  EndDate
----------                -------------        ------------ -------------- -----------          ---------  -------
FDPOAzureBudget           (Subscription-level) 3,750.00     1,384.39       Subscription         2024-10-01 2034-10-01
TestBudget-VM-RG          vm-rg                100.00       -              RG: vm-rg            2026-01-01 2026-12-31
TestBudget-NetworkWatcher NetworkWatcherRG     50.00        -              RG: NetworkWatcherRG 2026-01-01 2026-12-31
```

### CSV Export

The script automatically exports data to `AzureBudgets.csv` for Power BI integration.

## Power BI Integration Options

1. **Direct REST Query** — Use Power BI's Web connector to call the API directly (if authentication allows)
2. **Scheduled Export** — Run the PowerShell script on a schedule (Azure Automation or Logic App) to export CSV to a storage account, then connect Power BI to the storage account

## Configuration

Update the `$subscriptionId` variable in the script to match your target subscription:

```powershell
$subscriptionId = 'your-subscription-id-here'
```

## License

MIT
