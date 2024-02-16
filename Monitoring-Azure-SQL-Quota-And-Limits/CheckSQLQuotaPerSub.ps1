# set subscription id
$SubscriptionId = $args[0]

# ------------------------------------------------------------------
 
# first login to Azure Account
Write-Host "`n`nConnecting to Azure Account..."
if((Get-AzContext) -eq $null)
{
    Connect-AzAccount
}
 
# set subscription context
Write-Host "Selecting subscription..."
$context = Set-AzContext -Subscription $SubscriptionId
 
# get AAD token for REST calls
Write-Host "Getting Bearer token from AAD for REST calls..."
$apiToken = [Microsoft.Azure.Commands.Common.Authentication.AzureSession]::Instance.AuthenticationFactory.Authenticate($context.Account, $context.Environment, $context.Tenant.Id, $null, "Never", $null)
$headers = @{ 'authorization' = ('Bearer {0}' -f ($apiToken.AccessToken)) }
 
# Get Locations where Sql is available
Write-Host "Getting Locations where Sql is available..."
# Define the list of locations to searched
$skipLocations = @('eastus', 'eastus2', 'centralus', 'northeurope', 'westeurope')

# Retrieve and filter locations
$SqlLocations = Get-AzLocation |
    Where-Object { 
        $_.Providers -contains "Microsoft.Sql" -and 
        $_.Location -in $skipLocations
    } |
    Sort-Object Location |
    Select-Object Location, DisplayName

# ------------------------------------------------------------------------------
# get subscription quota and regional available SLOs for Sql SQL
 
Write-Host "Getting subscription quota settings for Sql..."
$quotaResults = [System.Collections.ObjectModel.Collection[psobject]]@()

foreach($location in $SqlLocations)
{
    # ------------------
    # available slos
    # https://review.learn.microsoft.com/en-us/rest/api/sql/capabilities/list-by-location?view=rest-sql-2021-11-01&branch=main&tabs=HTTP
    $capabilitiesUri = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.Sql/locations/$($location.Location)/capabilities?api-version=2021-11-01"
    $regionalCapabilities = ConvertFrom-Json (Invoke-WebRequest -Method Get -Uri $capabilitiesUri -Headers $headers).Content

    # ------------------
    # subscription quota
    # https://review.learn.microsoft.com/en-us/rest/api/sql/subscription-usages/list-by-location?view=rest-sql-2021-11-01&branch=main&tabs=HTTP
    $subscriptionQuotaUri = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.Sql/locations/$($location.Location)/usages/ServerQuota?api-version=2021-11-01"
    $currentQuotaResult = (ConvertFrom-Json (Invoke-WebRequest -Method Get -Uri $subscriptionQuotaUri -Headers $headers).Content).properties
    
    # ------------------------------------
 
    $quotaResults += [PSCustomObject]@{
        Location = $location.Location;
        DisplayName = $location.DisplayName;
        CurrentSqlServerCount = $currentQuotaResult.currentValue;
        SqlServerQuotaLimit = $currentQuotaResult.limit;
        Status = $regionalCapabilities.status;
        Reason = $regionalCapabilities.supportedServerVersions.reason;
    }
}

# ---------------
# Output

$quotaResults | ft -AutoSize
 
Write-Host "`nResults copied to clipboard`n`n" -ForegroundColor Green
$quotaResults | ConvertTo-Csv -NoTypeInformation | Set-Clipboard
