
# Identifying Pipeline Responsible for Azure Resource Modifications

## Problem Statement

Tracking which Azure DevOps pipeline and build is responsible for modifying Azure resources is crucial for maintaining traceability and accountability in Azure environments. This repository demonstrates two approaches to achieve this:

- **Approach 1** is proactive by using Azure DevOps pipeline tags applied during resource creation and hence embedding traceability into the resource itself using tags.
- **Approach 2** is reactive, relying on Azure Activity Logs to analyze past changes. It cross-reference pipeline logs and identify the responsible build.

Both approaches are implemented with the relevant scripts available in the `src` folder.

---

## Approach 1: Tagging Azure Resources in Pipelines

### Overview of Solution

In this approach, Azure resources (e.g., App Service Plans, Function Apps) are tagged with metadata (`PipelineName`, `PipelineId`, `RunId`) during their creation. These tags allow for easy identification of the pipeline build responsible for the modification.

### Code Location

- Script file: [src/PipelineTaggingResources.yml](https://github.com/jvargh/azurescripts/blob/main/azdevops/pipelineidentify/src/PipelineTaggingResources.yml)

### How It Works

- A pipeline triggers on changes to the `main` branch.
- The pipeline dynamically generates metadata for each run (e.g., pipeline name and ID, run ID).
- Resources are created and tagged with this metadata during deployment.
- Logs and artifacts are published to verify the tags.

### Usage

1. Update the variable placeholders e.g., `resourceGroup`, `vnetName`.
2. Add the pipeline YAML to your Azure DevOps project.
3. Trigger the pipeline by committing changes to the `main` branch.

### Output

- Resources are tagged with:
  - `PipelineName`, `PipelineId`, `RunId` and will look as seen below
    
    ![image](https://github.com/user-attachments/assets/d03949df-fe8a-4fb9-b3d7-a149deab29af)
    
- The pipeline logs display the tags for verification.
- Published logs contain metadata for audit purposes.

---

## Approach 2: Using Azure Activity Logs to Trace Resource Changes

### Overview of Solution

This approach uses Azure Activity Logs to extract key metadata (e.g., subscription ID, resource type) for resource modifications. These details are then cross-referenced with Azure DevOps build logs to identify the responsible pipeline run.

### Code Location

- Script file: [src/ActivityLogsTrace.ps1](https://github.com/jvargh/azurescripts/blob/main/azdevops/pipelineidentify/src/ActivityLogsTrace.ps1)

### Usage

1. Update the variable placeholders in `src/ActivityLogsTrace.ps1` (e.g., `$organization`, `$resourceGroup`, `$startTime`).
2. Install PowerShell 7 and Azure CLI if not already installed.
3. Run the script in PowerShell 7:
   ```powershell
   pwsh src/ActivityLogsTrace.ps1
   ```
   
### How It Works

#### **1. Set Input Parameters**
- **Purpose:** Define the required variables for the script, such as Azure DevOps organization/project details, resource group, and time range.
- **Key Variables:**
  - `$organization`: Azure DevOps organization name.
  - `$project`: Azure DevOps project name.
  - `$personalAccessToken`: Personal Access Token for authenticating with Azure DevOps APIs.
  - `$resourceGroup` and `$resourceId`: The Azure resource to track.
  - `$startTime` and `$endTime`: Time range for querying Azure Activity Logs.

#### **2. Authenticate with Azure DevOps**
- **Purpose:** Encode the Personal Access Token (PAT) in Base64 for authentication with Azure DevOps APIs.
- **Code:**
  ```powershell
  $base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$personalAccessToken"))
  ```

#### **3. Query Azure Activity Logs**
- **Purpose:** Use the Azure CLI to retrieve activity logs for the specified resource within the given time range.
- **Operation Details:**
  - Filter logs based on the `operationName` (e.g., `Microsoft.Web/serverfarms/write`).
  - Extract fields such as `Subscription ID`, `Resource Group`, and `Resource Type`.
- **Command Example:**
  ```powershell
  $activityLogs = az monitor activity-log list \
    --resource-group $resourceGroup \
    --resource-id $resourceId \
    --start-time $startTime \
    --end-time $endTime \
    --query "[?operationName.value == 'Microsoft.Web/serverfarms/write']" \
    | ConvertFrom-Json
  ```

#### **4. List All Pipelines**
- **Purpose:** Use Azure DevOps APIs to retrieve all pipelines in the specified project.
- **API Endpoint:** `https://dev.azure.com/<organization>/<project>/_apis/pipelines`
- **Command Example:**
  ```powershell
  $pipelinesUrl = "$baseUrl/pipelines?api-version=7.1-preview.1"
  $pipelinesResponse = Invoke-RestMethod -Uri $pipelinesUrl -Method Get -Headers @{Authorization=("Basic {0}" -f $base64AuthInfo)}
  $pipelines = $pipelinesResponse.value
  ```

#### **5. Search Pipeline Runs**
- **Purpose:** Iterate through each pipeline and its runs to find logs matching the activity log details.
- **Operation Details:**
  - For each pipeline, retrieve its runs using the Azure DevOps API.
  - Examine each run for relevant logs.

#### **6. Retrieve Build Logs**
- **Purpose:** For each pipeline run, fetch build logs and inspect their content.
- **Details:**
  - Use Azure CLI and Azure DevOps APIs to fetch logs.
  - Identify the log entry with the most lines (`lineCount`) for detailed inspection.
- **Command Example:**
  ```powershell
  $pipelineLogs = az devops invoke \
    --org "https://dev.azure.com/$organization" \
    --area pipelines \
    --resource logs \
    --route-parameters project=$project pipelineId=$pipelineId runId=$runId \
    --api-version=7.0 \
    | ConvertFrom-Json
  ```

#### **7. Match Activity Log Metadata**
- **Purpose:** Compare activity log details (`Subscription ID`, `Resource Group`, `Resource Type`) with the pipeline logs.
- **Operation:**
  - Inspect the log content for matches using string comparisons or regex.
  - Identify the responsible pipeline when a match is found.

#### **8. Output Results**
- **Purpose:** Display the pipeline name, run ID, and log ID for the matching build.
- **Example Output:**
  ```
  Match Found: Pipeline 'PipelineName', Run ID: 12345, Log ID: 67890
  ```

#### **9. Handle Edge Cases**
- **Scenarios:**
  - You could have scenarios where no activity logs are found for the resource, so this will need to be manually verified first.
  - You could have scenarios where no pipelines or runs match the criteria.
  - You could have scenarios build logs do not contain the expected metadata.

---

### Output

- Logs matching the resource modification details are identified.
- The responsible pipeline is displayed with:
  - `PipelineName`
  - `RunId`
  - `LogId`
    
![image](https://github.com/user-attachments/assets/f92e3e7b-d6ce-49e4-b946-12d2bd7f6d1f)


---

## Conclusion

- Both approaches provide a reliable way to identify the pipeline responsible for resource modifications.
- Choose the method that best suits your requirements or combine both for comprehensive traceability. For further details, refer to the code files in the `src` folder.
- Contributions and feedback are welcome!
