/*
 * Disclaimer: 
 *
 * This code is provided "as-is" without any warranties or guarantees of any kind, express or implied,
 * including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.
 * The author assumes no responsibility or liability for the accuracy, completeness, or functionality of the code.
 *
 * By using this code, you acknowledge that the author is not responsible for any damages or losses, including but not
 * limited to direct, indirect, incidental, consequential, or punitive damages, arising out of or related to your use,
 * misuse, or inability to use the code, even if the author has been advised of the possibility of such damages.
 *
 * This code is intended for educational and informational purposes only. It is the user's responsibility to ensure
 * that the code is suitable for their intended use and to thoroughly test the code in their own environment.
 * Users are advised to seek professional advice and conduct their own due diligence before relying on the code
 * for any critical application.
 *
 * Use at your own risk.
 */
 
$resourceGroup = "DeloitteTools"
$backupDaysAgoLimit = 90

# Function to send alerts or log messages, customize as needed
function alert($msg) {
    Write-Host $msg -ForegroundColor Red
}

# Temporarily suppress warnings for commands that raise them
$WarningPreference = 'SilentlyContinue'

<# Check for VM's/Disks which are not protected by Azure Backup/ASR, scoped to a particular resource group.

This checks for a number of failure modes whereby your VM's may not be replicated, or partially replicated:

1. If backup is not enabled for the VM.
2. If backup is enabled, but paused.
3. If backup is enabled, but newly added data disks are not picked up for backup. (See: 'Include Future Disks' setting in advanced plan)
4. If backup is enabled, but first backup is still pending.
5. If backup is enabled, but status is not 'Healthy'.
6. If backup is enabled, but pre-checks are not passed.
7. If backup is enabled, but initial backup is not complete
8. If backup is enabled, but the most recent backup is older than 90 days.
9. If replication is not configured for the VM.
10. If replication is configured, but newly created data disks are not picked up for replication.
#>

# Step 1: Get all Recovery Services Vaults in the subscription
$vaults = Get-AzRecoveryServicesVault

# Process each vault to check for unprotected disks and backup configurations
foreach ($vault in $vaults) {
    # Retrieve vault settings file
    $file = Get-AzRecoveryServicesVaultSettingsFile -Vault $vault
    # Import settings file for Site Recovery operations
    Import-AzRecoveryServicesAsrVaultSettingsFile -Path $file.FilePath

    # Set context for the vault
    $context = Get-AzRecoveryServicesAsrVaultContext
    $fabrics = Get-AzRecoveryServicesAsrFabric  # Retrieve fabrics in the vault (representing different environments)

    # Initialize collections for later use
    $unprotecteddisks = @{}  # To store unprotected disks
    $protectedVMs = @()  # To store replicated VM IDs

    # Step 2: Process each fabric (site or environment) and its protection containers
    foreach ($fabric in $fabrics) {
        $containers = Get-AzRecoveryServicesAsrProtectionContainer -Fabric $fabric

        # Process each protection container (collection of VMs)
        foreach ($container in $containers) {
            $items = Get-AzRecoveryServicesAsrReplicationProtectedItem -ProtectionContainer $container

            # Step 3: For each replicated item, check its protection status
            foreach ($item in $items) {
                $resobj = Get-AzResource -ResourceId $item.ProviderSpecificDetails.FabricObjectId

                # Ensure we are only processing VMs in the desired resource group
                if ($resobj.ResourceGroupName -eq $resourceGroup) {
                    $vmobj = Get-AzVM -Name $resobj.Name -ResourceGroupName $resourceGroup

                    # Add this VM to the list of protected VMs
                    $protectedVMs += $vmobj.Id

                    # Get the full path to the disks associated with the VM
                    $rgPath = ($vmobj.Id -split "virtualMachines/")[0] + "disks/"

                    # Step 4: Check if all data and OS disks are protected (Check #10: Replication for newly created disks)
                    $disklist = $item.ProviderSpecificDetails.A2ADiskDetails | ForEach-Object { $rgPath + $_.DiskName }

                    # Compare with disks attached to the VM, check if any are unprotected
                    foreach ($disk in $vmobj.StorageProfile.DataDisks) {
                        $diskId = $rgPath + $disk.Name
                        if (-not $disklist.Contains($diskId)) {
                            # Check #10: Replication is configured, but newly created disks are not picked up
                            $unprotecteddisks[$diskId] = $vmobj.Id
                        }
                    }

                    # Check if the OS disk is protected
                    $osDiskId = $rgPath + $vmobj.StorageProfile.OsDisk.Name
                    if (-not $disklist.Contains($osDiskId)) {
                        $unprotecteddisks[$osDiskId] = $vmobj.Id
                    }
                }
            }
        }
    }
}

# Re-enable warnings for other parts of the script
$WarningPreference = 'Continue'

# Step 5: Alert for unprotected disks
if ($unprotecteddisks.Count -gt 0) {
    foreach ($key in $unprotecteddisks.Keys) {
        alert -msg "WARNING: Detected unprotected disk $key across local vaults!"
    }
}

# Step 6: Ensure all VMs in the resource group are replicated under some vault (Check #9: Replication not configured for the VM)
$allVMs = Get-AzVM -ResourceGroupName $resourceGroup
foreach ($vm in $allVMs) {
    if ($protectedVMs -notcontains $vm.Id) {
        alert -msg "WARNING: Detected unprotected VM $($vm.Id) across local vaults!"
    }
}

# Step 7: Ensure all VMs have backup configured
$vaultList = @()  # To store vault IDs protecting VMs
foreach ($vm in $allVMs) {
    Write-Host "Checking: $($vm.Name) for Backup status..." -ForegroundColor Green
    $status = Get-AzRecoveryServicesBackupStatus -Name $vm.Name -ResourceGroupName $resourceGroup -Type AzureVM

    # Check #1: If backup is not enabled for the VM
    if (-not $status.BackedUp) {
        alert -msg "WARNING: Virtual Machine $($vm.Name) in resource group $resourceGroup has no backups configured!"
    } else {
        Write-Host "INFO: VM $($vm.Name) is protected by vault: $($status.VaultId)"
        $vaultList += $status.VaultId  # Add the vault ID to the list
    }
}

# Step 8: Check for issues with backup configuration or status
<# Ensure all VM's configured for backup have no issues with the backup status

Checks made:

1. Protection is not paused
2. First backup is not pending
3. Protection Status is anything but 'Healthy'
4. Backup pre-checks are passed
5. Most recent backup is inside some minimum value (sample script is 90 days)
6. Checks to ensure all data disks have their LUN's listed to be protected
#>
foreach ($vaultid in ($vaultList | Get-Unique)) {
    # Set the context to the vault
    $vault = Get-AzRecoveryServicesVault -ResourceGroupName $vaultid.Split('/')[4] -Name $vaultid.Split('/')[8]
    Set-AzRecoveryServicesVaultContext -Vault $vault

    $containers = Get-AzRecoveryServicesBackupContainer -ContainerType AzureVM -VaultId $vaultid
    foreach ($container in $containers) {
        $backupItems = Get-AzRecoveryServicesBackupItem -Container $container -WorkloadType AzureVM

        foreach ($backupVM in $backupItems) {
            # Check #2: Backup is enabled but paused (ProtectionStopped)
            if ($backupVM.ProtectionState -eq "ProtectionStopped") {
                alert -msg "WARNING: VM: $($backupVM.virtualMachineId) has backup protection stopped!"
            }
            # Check #4: Backup is enabled, but first backup is still pending
            if ($backupVM.ProtectionState -eq "IRPending") {
                alert -msg "WARNING: VM: $($backupVM.virtualMachineId) has first backup pending!"
            }
            # Check #5: Backup is enabled, but status is not 'Healthy'
            if ($backupVM.ProtectionStatus -ne "Healthy") {
                alert -msg "WARNING: VM: $($backupVM.virtualMachineId) shows backup protection as not healthy!"
            }
            # Check #6: Backup is enabled, but pre-checks are not passed
            if ($backupVM.HealthStatus -ne "Passed") {
                alert -msg "WARNING: VM: $($backupVM.virtualMachineId) pre-checks failed!"
            }

            # Check #8: Backup is enabled, but the most recent backup is older than 90 days
            $timestampAgo = (Get-Date) - $backupVM.LastBackupTime
            if ($timestampAgo.Days -ge $backupDaysAgoLimit) {
                alert -msg "WARNING: VM: $($backupVM.virtualMachineId) has last backup over $backupDaysAgoLimit days ago!"
            }

            # Check #3: Backup is enabled, but newly added data disks are not picked up for backup
            $compareVM = Get-AzVM -ResourceGroupName $backupVM.VirtualMachineId.Split('/')[4] -Name $backupVM.VirtualMachineId.Split('/')[8]
            foreach ($disk in $compareVM.StorageProfile.DataDisks) {
                if (-not $backupVM.DiskLunList.Contains($disk.Lun)) {
                    alert -msg "WARNING: VM: $($backupVM.virtualMachineId) has LUN: $($disk.Lun) not selected for backup!"
                }
            }
        }
    }
}

