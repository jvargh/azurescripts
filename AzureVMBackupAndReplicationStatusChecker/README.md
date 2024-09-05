

# Azure VM Backup and Replication Status Checker

This PowerShell script is designed to check for unprotected Virtual Machines (VMs) and disks in Azure Backup and Site Recovery (ASR). It ensures that all VMs and their attached disks are correctly backed up and replicated within a specified Azure resource group. The script performs a number of failure checks to help identify potential issues with backup and replication configurations.

## Features

The script checks the following failure modes for each VM and its disks:

1. **Backup Status**:
   - If backup is not enabled for the VM.
   - If backup is enabled but paused.
   - If backup is enabled, but newly added data disks are not picked up for backup.
   - If backup is enabled, but the first backup is still pending.
   - If backup is enabled, but the backup status is not 'Healthy'.
   - If backup is enabled, but pre-checks are not passed.
   - If backup is enabled, but the most recent backup is older than a set number of days (default: 90 days).

2. **Replication Status**:
   - If replication is not configured for the VM.
   - If replication is configured, but newly created data disks are not picked up for replication.

## Prerequisites

- Azure PowerShell module installed (`Az` module).
- Permissions to access the Azure Subscription and Resource Group.
- Virtual Machines in Azure should be deployed in the specified resource group and have Recovery Services Vault and Backup configured.

### Installation of Azure PowerShell

If you don't have Azure PowerShell installed, you can install it via PowerShell with the following command:

```powershell
Install-Module -Name Az -AllowClobber -Force
```

## How to Use

### Script Parameters

You need to modify the script with the appropriate values before running it:

- **$resourceGroup**: The Azure resource group that contains the VMs.
- **$backupDaysAgoLimit**: The number of days since the last backup, used to flag VMs with outdated backups (default: 90 days).

### Steps to Execute

1. Clone this repository or download the script to your local machine.
2. Open PowerShell and navigate to the directory where the script is located.
3. Run the script:

   ```powershell
   .\Check-UnprotectedDisks.ps1
   ```

### Output

- The script will print information to the console, alerting you if:
  - VMs are not protected by Azure Backup.
  - Replication is not configured for VMs.
  - Backup is enabled but has issues such as being paused, missing disks, or failing health checks.
  - Backup is outdated beyond the specified limit (90 days by default).

### Sample Output

```plaintext
Checking: vm-name for Backup status...
INFO: VM vm-name is protected by vault: /subscriptions/<id>/resourceGroups/<group>/providers/Microsoft.RecoveryServices/vaults/vault-name
WARNING: Detected unprotected VM /subscriptions/<id>/resourceGroups/<group>/providers/Microsoft.Compute/virtualMachines/vm-name across local vaults!
```

## Script Breakdown

### Key Sections

1. **Backup Check**: Ensures that VMs are correctly backed up and highlights any issues such as paused backups or missing disks.
2. **Replication Check**: Ensures that VMs are replicated under Azure Site Recovery and flags any missing replication.
3. **Disk Protection Check**: Ensures that newly added disks are picked up for both backup and replication.
4. **Error Handling**: Alerts users with warnings when a VM or disk is not properly configured.

### Comments in the Script

Each part of the script is well-documented with inline comments, explaining the logic and checks being performed.

## Customization

- You can modify the `$backupDaysAgoLimit` variable to change the threshold for checking outdated backups.
- You can customize the `alert` function to integrate with logging systems, notification services (e.g., SendGrid), or IT ticketing systems (e.g., ServiceNow).

## Output
![image](https://github.com/user-attachments/assets/4501c566-3de8-4137-af73-4bdecfb72ca5)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit pull requests or report issues to improve the script.
