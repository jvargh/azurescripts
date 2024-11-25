# Check Azure SKU Availability

This PowerShell script checks the availability of required Azure VM SKUs in specified regions and suggests replacements if the required SKUs are unavailable. The script optimizes the process by fetching all available SKUs in a region in a single call and comparing the results for both required and replacement SKUs.

## Features

- **Region-Specific Checks**:
  - Supports checking SKU availability for both `Japan East` and `Japan West` regions.
  
- **Replacement Suggestions**:
  - If the required SKU is unavailable, the script checks for a predefined replacement SKU and suggests it if available.
  
- **Optimized Execution**:
  - Uses a single Azure CLI call to fetch all available SKUs in a region, reducing execution time.

- **Detailed Feedback**:
  - Outputs availability status and replacement suggestions in a clear format.

## Prerequisites

1. **Azure CLI**:
   - Install Azure CLI on your local system. [Azure CLI Installation Guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

2. **Azure Login**:
   - Ensure you're logged into your Azure account:
     ```powershell
     az login
     ```

3. **PowerShell**:
   - Use a PowerShell environment to execute the script.

## How to Use

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/check-azure-sku-availability.git
cd check-azure-sku-availability
```
### 2. Run the Script
Execute the script in a PowerShell terminal:
```bash
.\Check-SKU-Availability.ps1
```
### 3. Review the output
![image](https://github.com/user-attachments/assets/5c8cedb0-2265-4f70-8c7b-3ffce6dca88a)

## Script Logic

1. **Define Regions and SKUs**:
   - Lists of required and replacement SKUs for both `Japan East` and `Japan West` regions are defined in the script.

2. **Fetch Available SKUs**:
   - The script uses the Azure CLI to fetch all available SKUs in the target region:
     ```powershell
     az vm list-skus --location <region> --query "[].name" -o tsv
     ```

3. **Check SKU Availability**:
   - Each required SKU is checked for availability.
   - If unavailable, the script checks the replacement SKU (if defined).

4. **Output Results**:
   - Outputs availability status and replacement suggestions.

## Customization
- To add new regions or SKUs, modify the `$regions` and `$skusToCheck` variables in the script.

## License
- This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
- Contributions are welcome! Please fork the repository and submit a pull request.

