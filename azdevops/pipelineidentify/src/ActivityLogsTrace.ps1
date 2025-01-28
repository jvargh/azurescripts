# Must install Powersheell7 extension or use PS7 to run this script
# https://stackoverflow.com/questions/74099826/how-can-i-get-azure-pipeline-log-file-from-command-line
# Inputs
$organization = "<AzDevOps-ORG>" 
$project = "<AzDevOps-PROJECT>" 
$personalAccessToken = "<AzDevOps-PAT>" 
$resourceGroup = "<Azure-ResourceGroup>" 
$resourceId = "<Azure-Resource>" 
$startTime = "<Event-StartTime>" # e.g., "2023-10-01T00:00:00Z" 
$endTime = "<Event-EndTime>"  # e.g., "2023-10-02T00:00:00Z" 

# Base64 encode the PAT for authentication
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$personalAccessToken"))

# Azure DevOps API Base URL
$baseUrl = "https://dev.azure.com/$organization/$project/_apis"

# Step 1: Query Azure Activity Logs
Write-Host "Querying Azure Activity Logs..."
$activityLogs = az monitor activity-log list `
  --resource-group $resourceGroup `
  --resource-id $resourceId `
  --start-time $startTime `
  --end-time $endTime `
  --query "[?operationName.value == 'Microsoft.Web/serverfarms/write']" `
  | ConvertFrom-Json

# Check if Activity Logs were found
if (-not $activityLogs -or $activityLogs.Count -eq 0) {
    Write-Host "No matching activity logs found."
    exit
}

# Extract Fields from Activity Logs (take the first value if it's a list)
$activityLog = $activityLogs[0]  # Take the first log entry

# Extract Fields from Activity Logs
$operationName = $activityLog.operationName.value
$subscriptionId = $activityLog.subscriptionId
$resourceGroupName = $activityLog.resourceGroupName
$resourceType = $activityLog.resourceType.value

Write-Host "Operation Name: $operationName"
Write-Host "Subscription ID: $subscriptionId"
Write-Host "Resource Group: $resourceGroupName"
Write-Host "Resource Type: $resourceType"

# Step 2: List All Pipelines
Write-Host "Fetching pipelines..."
$pipelinesUrl = "$baseUrl/pipelines?api-version=7.1-preview.1"
$pipelinesResponse = Invoke-RestMethod -Uri $pipelinesUrl -Method Get -Headers @{Authorization=("Basic {0}" -f $base64AuthInfo)}
$pipelines = $pipelinesResponse.value

# Step 3: Search Pipeline Runs for Matching Fields
Write-Host "Searching pipeline runs..."
foreach ($pipeline in $pipelines) {
    $pipelineId = $pipeline.id
    $pipelineName = $pipeline.name

    # List Pipeline Runs
    $runsUrl = "$baseUrl/pipelines/$pipelineId/runs?api-version=7.1-preview.1"
    $runsResponse = Invoke-RestMethod -Uri $runsUrl -Method Get -Headers @{Authorization=("Basic {0}" -f $base64AuthInfo)}
    $runs = $runsResponse.value

    foreach ($run in $runs) {
        $runId = $run.id

        # Step 4: Retrieve the top log ID
        Write-Host "Retrieving logs for Pipeline '$pipelineName', Run ID: $runId..."
        $pipelineLogs = az devops invoke `
          --org "https://dev.azure.com/$organization" `
          --area pipelines `
          --resource logs `
          --route-parameters project=$project pipelineId=$pipelineId runId=$runId `
          --api-version=7.0 `
          | ConvertFrom-Json

        if (-not $pipelineLogs -or -not $pipelineLogs.Logs) {
            Write-Host "No logs found for Pipeline '$pipelineName', Run ID: $runId"
            continue
        }

        # Get the log with the highest lineCount
        $longestLogId = ($pipelineLogs.Logs | Sort-Object -Property lineCount -Descending | Select-Object -First 1).id

        if (-not $longestLogId) {
            Write-Host "No valid log ID found for Pipeline '$pipelineName', Run ID: $runId"
            continue
        }

        # Write-Host "Top log ID: $longestLogId"

        # Step 5: Retrieve the build log 
        Write-Host "Retrieving build log for Pipeline '$pipelineName', Run ID: $runId, Log ID: $longestLogId..."
        $buildLog = az devops invoke `
          --org "https://dev.azure.com/$organization" `
          --area build `
          --resource logs `
          --route-parameters project=$project buildId=$runId logId=$longestLogId `
          --api-version=7.0 `
          --only-show-errors `
          | ConvertFrom-Json

        if (-not $buildLog) {
            Write-Host "Failed to retrieve build log for Pipeline '$pipelineName', Run ID: $runId, Log ID: $longestLogId"
            continue
        }

        # Step 6: Check Logs for Matching Fields
        $logContent = $buildLog.Value

        if ($logContent -match $subscriptionId -and
            $logContent -match $resourceGroupName -and
            $logContent -match $resourceType) {
            Write-Host "Match Found: Pipeline '$pipelineName', Run ID: $runId, Log ID: $longestLogId"            
            break
        } else {
            Write-Host "No match found in logs for Pipeline '$pipelineName', Run ID: $runId, Log ID: $longestLogId"
        }
    }
}
