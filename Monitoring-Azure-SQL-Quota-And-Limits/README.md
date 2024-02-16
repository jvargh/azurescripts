# Azure SQL Region Capability and Quota Reporter
This PowerShell script is designed to connect to an Azure account, set the subscription context, and retrieve the capabilities and quotas for Azure SQL in specified regions.

## Prerequisites
- Azure PowerShell module installed.
- Azure account with the required permissions to fetch subscription and service details.

## Usage
To run the script, you must pass the subscription ID as the first argument.

```powershell
.\script_name.ps1 <subscription-id>
```

## Script Workflow
1. `Login to Azure`: The script starts by ensuring there is a connection to an Azure account.
2. `Set Subscription Context`: After successfully connecting, it sets the context to the provided subscription ID.
3. `Retrieve AAD Token`: The script then retrieves a bearer token from Azure Active Directory (AAD) for authenticating REST calls.
4. `Get SQL Available Locations`: It fetches the locations where Azure SQL is available, excluding specified regions.
5. `Fetch Regional Capabilities and Quotas`:
  - For each of the available locations, the script retrieves the regional capabilities and current quota settings for Azure SQL.
  - It uses the REST API endpoints provided in the comments to fetch the service level objectives (SLOs) and subscription quotas.
6. `Compile Results`: The retrieved data is compiled into a custom object for each location.
7. `Output`: The results are displayed in a table format and copied to the clipboard.

## Output
The script outputs a table with the following columns:
- `Location`: The Azure region location.
- `DisplayName`: The display name of the region.
- `CurrentSqlServerCount`: The current count of SQL Servers in the region.
- `SqlServerQuotaLimit`: The quota limit for SQL Servers in the region.
- `Status`: The status of the regional capabilities for Azure SQL.
- `Reason`: The reason provided by Azure SQL regional capabilities, if any.

## Customization
You can modify the $skipLocations array to include or exclude different regions based on your needs.

## Notes
- Ensure that the Azure AD app registration has the necessary permissions to perform these actions.
- The REST API versions are specified in the script. Make sure they are up to date with the Azure REST API versions you intend to use.

## Output
- The script when run using the sub-id argument, connects to an Azure account and check the current SQL Server quota settings for that subscription. It eventually gets the subscription quota settings for SQL. 
- The output table lists the specified Azure regions (like Central US, East US, etc.), displays the current SQL Server count in each region and the SQL Server quota limit. Each region listed in this case has a quota limit of 20 SQL Servers, with East US already having some 1 SQL Servers deployed, while the other regions have none deployed.
  
![image](https://github.com/jvargh/azurescripts/assets/3197295/3586d06f-4e15-4d9c-955f-c9e0c773d203)

 




