
# Identifying Pipeline Responsible for Azure Resource Modifications

## Problem Statement

Tracking which Azure DevOps pipeline and build is responsible for modifying Azure resources is crucial for maintaining traceability and accountability in Azure environments. This repository demonstrates two approaches to achieve this:

1. Using Azure DevOps pipeline tags applied during resource creation.
2. Leveraging Azure Activity Logs to cross-reference pipeline logs and identify the responsible build.

Both approaches are implemented with the relevant scripts available in the `src` folder.

---

## Approach 1: Tagging Azure Resources in Pipelines

### Overview of Solution

In this approach, Azure resources (e.g., App Service Plans, Function Apps) are tagged with metadata (`PipelineName`, `PipelineId`, `RunId`) during their creation. These tags allow for easy identification of the pipeline build responsible for the modification.

### Code Location
- Script file: <a href="https://github.com/jvargh/azurescripts/blob/main/azdevops/pipelineidentify/src/PipelineTaggingResources.yml" target="_blank">src/PipelineTaggingResources.yml</a>

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

- Script file: `src/ActivityLogsTrace.ps1`

### How It Works

- Azure Activity Logs are queried to retrieve modification details for a specific resource and time range.
- Azure DevOps APIs are used to list pipelines and their runs.
- Build logs are fetched and inspected for matches with the activity log metadata.

### Usage

1. Update the variable placeholders in `src/ActivityLogsTrace.ps1` (e.g., `$organization`, `$resourceGroup`, `$startTime`).
2. Install PowerShell 7 and Azure CLI if not already installed.
3. Run the script in PowerShell 7:
   ```powershell
   pwsh src/ActivityLogsTrace.ps1
   ```

### Output

- Logs matching the resource modification details are identified.
- The responsible pipeline is displayed with:
  - `PipelineName`
  - `RunId`
  - `LogId`
- Provides a detailed audit trail for resource changes.

---

## Conclusion

Both approaches provide a reliable way to identify the pipeline responsible for resource modifications:

- **Approach 1** is proactive, embedding traceability into the resource itself using tags.
- **Approach 2** is reactive, relying on Azure Activity Logs to analyze past changes.

Choose the method that best suits your requirements or combine both for comprehensive traceability. For further details, refer to the code files in the `src` folder. Contributions and feedback are welcome!
