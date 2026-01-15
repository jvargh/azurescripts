# Connect and set the subscription context (only if not already connected)
$context = Get-AzContext
if (-not $context) {
    Connect-AzAccount
    $context = Get-AzContext
}

# Use the current subscription from context, or specify your subscription ID here
$subscriptionId = $context.Subscription.Id
# $subscriptionId = 'your-subscription-id-here'  # Uncomment and set if you want a specific subscription

# Switch subscription if needed
if ($context.Subscription.Id -ne $subscriptionId) {
    Select-AzSubscription -SubscriptionId $subscriptionId | Out-Null
}

# Single API call to get ALL budgets in the subscription (both subscription-scoped and RG-scoped)
$uri = "/subscriptions/$subscriptionId/providers/Microsoft.Consumption/budgets?api-version=2024-08-01"

Write-Host "Fetching all budgets from subscription in a single API call..." -ForegroundColor Cyan

try {
    $response = Invoke-AzRestMethod -Method GET -Path $uri -ErrorAction Stop
    
    if ($response.StatusCode -ne 200) {
        throw "API returned status code $($response.StatusCode): $($response.Content)"
    }
    
    $resp = $response.Content | ConvertFrom-Json
    
    $budgetInfo = foreach ($budget in $resp.value) {
        $prop = $budget.properties
        
        # Extract Resource Group from the budget ID if it's RG-scoped
        # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Consumption/budgets/{name}
        # Or:     /subscriptions/{sub}/providers/Microsoft.Consumption/budgets/{name} (subscription-scoped)
        $resourceGroup = "(Subscription-level)"
        if ($budget.id -match '/resourceGroups/([^/]+)/') {
            $resourceGroup = $matches[1]
        }
        
        # Forecast can be in different locations depending on API version
        $forecast = $null
        if ($prop.forecastSpend.amount) { $forecast = $prop.forecastSpend.amount }
        elseif ($prop.currentSpend.forecast) { $forecast = $prop.currentSpend.forecast }
        
        [pscustomobject]@{
            BudgetName      = $budget.name
            ResourceGroup   = $resourceGroup
            BudgetAmount    = $prop.amount
            CurrentSpend    = if ($prop.currentSpend.amount) { $prop.currentSpend.amount } else { $null }
            ForecastAmount  = $forecast
            BudgetScope     = $budget.id
            BudgetStartDate = $prop.timePeriod.startDate
            BudgetEndDate   = $prop.timePeriod.endDate
            TimeGrain       = $prop.timeGrain
            Category        = $prop.category
        }
    }
    
    # Display results
    if ($budgetInfo) {
        Write-Host "`nFound $($budgetInfo.Count) budget(s) in a single API call:" -ForegroundColor Green
        
        # Create display-friendly output with shortened scope
        $displayData = $budgetInfo | Select-Object `
            BudgetName, 
            ResourceGroup, 
            @{N='BudgetAmount';E={'{0:N2}' -f $_.BudgetAmount}},
            @{N='ForecastAmount';E={if($_.ForecastAmount){'{0:N2}' -f $_.ForecastAmount}else{'-'}}},
            @{N='BudgetScope';E={if($_.ResourceGroup -eq '(Subscription-level)'){'Subscription'}else{"RG: $($_.ResourceGroup)"}}},
            @{N='StartDate';E={([datetime]$_.BudgetStartDate).ToString('yyyy-MM-dd')}},
            @{N='EndDate';E={([datetime]$_.BudgetEndDate).ToString('yyyy-MM-dd')}}
        
        $displayData | Format-Table -AutoSize
        
        # Export to CSV for Power BI
        $budgetInfo | Select-Object BudgetName, ResourceGroup, BudgetAmount, ForecastAmount, BudgetScope, BudgetStartDate, BudgetEndDate | Export-Csv -Path ".\AzureBudgets.csv" -NoTypeInformation
        Write-Host "Exported to AzureBudgets.csv" -ForegroundColor Green
    }
    else {
        Write-Host "`nNo budgets found in subscription." -ForegroundColor Yellow
    }
}
catch {
    Write-Error "Failed to fetch budgets: $($_.Exception.Message)"
}
