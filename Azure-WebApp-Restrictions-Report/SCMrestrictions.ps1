# Tenant ID, Client ID, and Client Secret
$tenantId = "<tenantId>"
$clientId = "<clientId>"
$clientSecret = "<clientSecret>"
$subscriptionId = "<subscriptionId>"
$APIVersion = "2023-01-01" # Replace with the appropriate API version
$targetResourceGroupName = "<rg-name>"

# Resource for which you are requesting a token
$resource = "https://management.azure.com/"

# Prepare the body for the token request
$body = @{
    grant_type    = "client_credentials"
    resource      = $resource
    client_id     = $clientId
    client_secret = $clientSecret
}

# Token endpoint
$tokenUrl = "https://login.microsoftonline.com/$tenantId/oauth2/token"

# Fetch the token
$tokenResponse = Invoke-RestMethod -Uri $tokenUrl -Method Post -Body $body
$token = $tokenResponse.access_token

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

class SiteRestrictions {
    [string]$WebAppName
    [string]$ResourceGroupName
    [Object]$MainSiteRestrictions
    [Object]$ScmSiteRestrictions
}

$allSitesRestrictions = @()

# Get List of Web Apps
$webAppsUri = "https://management.azure.com/subscriptions/$subscriptionId/providers/Microsoft.Web/sites?api-version=$APIVersion"
$webAppsResponse = Invoke-RestMethod -Uri $webAppsUri -Headers $headers
$webApps = $webAppsResponse.value

foreach ($webApp in $webApps) {
    $WebAppName = $webApp.name
    $WebAppRGName = $webApp.id.Split('/')[4]
 
    # Skip if the web app is not in the desired resource group
    if ($WebAppRGName -ne $targetResourceGroupName) {
        continue
    }

    # REST API call to get Main Site IP and SCM IP restrictions
    $mainSiteIpRestrictionsUri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$WebAppRGName/providers/Microsoft.Web/sites/$WebAppName/config/web?api-version=$APIVersion"
    $mainSiteIpRestrictionsResponse = Invoke-RestMethod -Uri $mainSiteIpRestrictionsUri -Headers $headers -Method Get
    $mainSiteIpRestrictions = $mainSiteIpRestrictionsResponse.properties.ipSecurityRestrictions
    $scmIpSecurityRestrictions = $mainSiteIpRestrictionsResponse.properties.scmIpSecurityRestrictions

    # Creating custom object for each site
    $siteRestrictions = [SiteRestrictions]::new()
    $siteRestrictions.WebAppName = $WebAppName
    $siteRestrictions.ResourceGroupName = $WebAppRGName
    $siteRestrictions.MainSiteRestrictions = $mainSiteIpRestrictions
    $siteRestrictions.ScmSiteRestrictions = $scmIpSecurityRestrictions

    # Add to the array
    $allSitesRestrictions += $siteRestrictions
}

# Output the results
# $allSitesRestrictions | Format-Table WebAppName, ResourceGroupName, MainSiteRestrictions, ScmSiteRestrictions



# Function to concatenate restrictions, each on a new line
function Format-Restrictions($restrictions) {
    $formattedRestrictions = $restrictions | ForEach-Object {
        "IP: $($_.ipAddress), Action: $($_.action), Priority: $($_.priority)"
    }
    # Join the individual restriction strings with a line break
    return ($formattedRestrictions -join "`n")
}

# Process and display the results
$allSitesRestrictions | ForEach-Object {
    $mainSiteFormatted = Format-Restrictions $_.MainSiteRestrictions
    $scmSiteFormatted = Format-Restrictions $_.ScmSiteRestrictions

    # Create a custom object with formatted properties
    [PSCustomObject]@{
        WebAppName            = $_.WebAppName
        ResourceGroupName     = $_.ResourceGroupName
        MainSiteRestrictions  = $mainSiteFormatted
        ScmSiteRestrictions   = $scmSiteFormatted
    }
} | Format-Table -Property "WebAppName", "ResourceGroupName", @{
    Name='MainSiteRestrictions'; Expression={$_.MainSiteRestrictions}; Width=50
}, @{
    Name='ScmSiteRestrictions'; Expression={$_.ScmSiteRestrictions}; Width=50
} -Wrap
