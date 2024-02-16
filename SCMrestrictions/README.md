# Azure Web App Restrictions Report Script
This PowerShell script is designed to generate a report on IP restrictions for Azure Web Apps within a specified subscription and target resource group. It retrieves both the main site and SCM (Source Control Management) site restrictions and presents them in a formatted table.

## Prerequisites
Before running this script, you must have:
- Azure PowerShell module installed.
- An Azure Active Directory (AD) app registration with appropriate permissions to access web app details.

## Configuration
Replace the placeholder values for the following variables at the beginning of the script:
- `<tenantId>`: Your Azure AD tenant ID.
- `<clientId>`: The client ID of your Azure AD app registration.
- `<clientSecret>`: The client secret of your Azure AD app registration.
- `<subscriptionId>`: The subscription ID where your Azure Web Apps are located.
- `<rg-name>`: The target resource group name containing the Azure Web Apps.

The API version is set to `2023-01-01`. Ensure that this is the current API version or update it accordingly.

## Usage
1. Open a PowerShell prompt.
2. Navigate to the directory containing the script.
3. Execute the script by typing `.\SCMrestrictions.ps1`.

## Script Flow
1. The script starts by acquiring an OAuth token from Azure AD for the subsequent REST API calls.
2. It then queries the list of all web apps in the specified subscription.
3. The script filters the web apps to include only those within the target resource group.
4. For each web app, it fetches the Main site and SCM IP restrictions using the specified Azure Management REST API.
5. It compiles the restrictions into a custom `SiteRestrictions` object for each web app.
6. Finally, it formats and outputs the restrictions in a table, with each restriction detailed on a new line for clarity.

## Output
The script outputs a table with the following columns:
- `WebAppName`: The name of the web app.
- `ResourceGroupName`: The name of the resource group containing the web app.
- `MainSiteRestrictions`: Formatted details of the main site IP restrictions.
- `ScmSiteRestrictions`: Formatted details of the SCM IP restrictions.

## Customization
You can adjust the width of the `MainSiteRestrictions` and `ScmSiteRestrictions` columns by modifying the `Width` value in the `Format-Table` command.

## Notes
- Ensure that the Azure AD app registration has the `Microsoft.Web/sites/read` permission.
- The script outputs to the console by default. You can redirect the output to a file if needed.

## Output
![image](https://github.com/jvargh/azurescripts/assets/3197295/7a13ce37-dd39-4f65-b500-908d9365cbbe)
