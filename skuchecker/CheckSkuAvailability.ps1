# Define regions and SKUs to check, including required SKUs and replacements
$regions = @("japaneast", "japanwest")
$skusToCheck = @{
    "japaneast" = @(
        @("Standard_D96s_v5", "Standard_D96as_v5"),
        @("Standard_E8ds_v4", "Standard_E8as_v4"),
        @("Standard_D64s_v5", "Standard_D64as_v5"),
        @("Standard_D16s_v5", "Standard_D16as_v5"),
        @("Standard_D32s_v5", "Standard_D32as_v5"),
        @("Standard_L32s_v2", "Standard_L32as_v3"),
        @("Standard_L8s_v2", "Standard_L8as_v3"),
        @("Standard_E32ds_v4", ""),
        @("Standard_E8ds_v4", "")
    )
    "japanwest" = @(
        @("Standard_D96s_v5", "Standard_D96as_v5"),
        @("Standard_E8ds_v4", "Standard_E8as_v4"),
        @("Standard_D64s_v5", "Standard_D64as_v5"),
        @("Standard_D16s_v5", "Standard_D16as_v5"),
        @("Standard_D32s_v5", "Standard_D32as_v5"),
        @("Standard_L32s_v2", "Standard_L32as_v3"),
        @("Standard_L8s_v2", "Standard_L8as_v3"),
        @("Standard_E32ds_v4", ""),
        @("Standard_E8ds_v4", "")
    )
}

# Login to Azure if not already logged in
Write-Host "Logging into Azure..."
az login

# Function to check SKU availability
function Check-SKUAvailability {
    param (
        [string]$region,
        [array]$skus
    )

    Write-Host "`nFetching available SKUs in region $region..." -ForegroundColor Green
    $availableSkus = az vm list-skus --location $region --query "[].name" -o tsv

    Write-Host "`nChecking SKU availability for $region..." -ForegroundColor Green
    foreach ($skuPair in $skus) {
        $requiredSku = $skuPair[0]
        $replacementSku = $skuPair[1]

        # Check if the required SKU is available
        if ($availableSkus -contains $requiredSku) {
            Write-Host "SKU $requiredSku is AVAILABLE in $region."
        } elseif ($replacementSku -and ($availableSkus -contains $replacementSku)) {
            # If the required SKU is not available, check for replacement
            Write-Host "SKU $requiredSku is NOT available in $region." -ForegroundColor Red
            Write-Host "Suggested replacement: $replacementSku is AVAILABLE in $region." -ForegroundColor Yellow
        } else {
            # If neither required nor replacement SKU is available
            Write-Host "SKU $requiredSku is NOT available in $region." -ForegroundColor Red
            if ($replacementSku) {
                Write-Host "Suggested replacement: $replacementSku is also NOT available in $region." -ForegroundColor Red
            } else {
                Write-Host "No replacement suggested for $requiredSku." -ForegroundColor Yellow
            }
        }
    }
}

# Loop through each region and check SKUs
foreach ($region in $regions) {
    Check-SKUAvailability -region $region -skus $skusToCheck[$region]
}
