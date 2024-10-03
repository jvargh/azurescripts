#!/bin/bash
# Automated Boot Recovery, Disk Health Check, and Azure VM Snapshot Validation Script
#
# Disclaimer:
# This script is provided "as is" without any warranty of any kind, either express or implied.
# The use of this script is at your own risk. The authors and contributors are not responsible
# for any damage or loss, including but not limited to data loss or system corruption, that
# may result from the use of this script.
#
# Before running this script, ensure that you have appropriate backups and have tested it in a
# controlled environment. It is recommended to review the code and modify it to suit your specific
# environment and requirements.
#
# By using this script, you agree to these terms and assume full responsibility for its use.

# Exit if not running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

LOGFILE="/var/log/disk_health_check.log"
REQUIRED_FREE_PERCENT=30
RESOURCE_GROUP="vm-rg" # Modify with your resource group name

echo ""
echo "<<<<<< Starting Disk Health Check and Boot Recovery Script >>>>>>>>" | tee -a $LOGFILE

# Function to Check for Azure VM Snapshots for all VMs in the Resource Group
check_azure_snapshots() {
	echo ""
    echo "################################" | tee -a $LOGFILE
    echo "# Check for Azure VM Snapshots #" | tee -a $LOGFILE
    echo "################################" | tee -a $LOGFILE

    # Get all VM names in the resource group
    VM_NAMES=$(az vm list --resource-group $RESOURCE_GROUP --query "[].name" -o tsv)

    if [ -z "$VM_NAMES" ]; then
      echo "No VMs found in resource group $RESOURCE_GROUP." | tee -a $LOGFILE
      return 1
    fi

    # Iterate through each VM
    for VM_NAME in $VM_NAMES; do
      echo "# Checking VM: $VM_NAME #" | tee -a $LOGFILE

      # Get the VM's OS and Data disks
      OS_DISK=$(az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --query "storageProfile.osDisk.managedDisk.id" -o tsv)
      DATA_DISKS=$(az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --query "storageProfile.dataDisks[].managedDisk.id" -o tsv)

      if [ -z "$OS_DISK" ] && [ -z "$DATA_DISKS" ]; then
        echo "No managed disks found for VM $VM_NAME." | tee -a $LOGFILE
        continue
      fi

      # Combine OS disk and data disks for iteration
      DISKS=("$OS_DISK" $DATA_DISKS)

      # Iterate through each disk and check for snapshots
      for disk in "${DISKS[@]}"; do
        DISK_NAME=$(echo $disk | awk -F/ '{print $NF}')
        
        echo "- Checking snapshots for disk: $DISK_NAME of VM: $VM_NAME #" | tee -a $LOGFILE

        # Get the snapshots for the disk by matching with the sourceResourceId
        SNAPSHOTS=$(az snapshot list --resource-group $RESOURCE_GROUP --query "[?creationData.sourceResourceId=='$disk'].{name:name, status:provisioningState}" -o tsv)

        if [ -z "$SNAPSHOTS" ]; then
          echo "Warning: No snapshots found for disk $DISK_NAME of VM $VM_NAME." | tee -a $LOGFILE
        else
          # Correctly process and handle snapshot information
          while IFS=$'\t' read -r snapshot_name snapshot_status; do
            if [ -z "$snapshot_name" ] || [ -z "$snapshot_status" ]; then
              echo "Warning: Snapshot for disk $DISK_NAME of VM $VM_NAME has missing information (name: $snapshot_name, status: $snapshot_status)." | tee -a $LOGFILE
            elif [ "$snapshot_status" != "Succeeded" ]; then
              echo "Warning: Snapshot $snapshot_name for disk $DISK_NAME of VM $VM_NAME has not completed successfully (status: $snapshot_status)." | tee -a $LOGFILE
            else
              echo "Snapshot $snapshot_name for disk $DISK_NAME of VM $VM_NAME is valid (status: $snapshot_status)." | tee -a $LOGFILE
            fi
          done <<< "$SNAPSHOTS"
        fi
      done
    done
}

# Call the Azure VM Snapshot Check Function for all VMs in the resource group
check_azure_snapshots

##############################################
# OS Detection and SUSE/RHEL Specific Checks #
##############################################

# Detect Operating System
OS_TYPE=$(cat /etc/os-release | grep "^ID=" | cut -d'=' -f2 | tr -d '"')
OS_VERSION=$(cat /etc/os-release | grep "^VERSION_ID=" | cut -d'=' -f2 | tr -d '"')

# Extract Major and Minor versions
MAJOR_VERSION=$(echo $OS_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $OS_VERSION | cut -d. -f2)

# Print the OS type and version
echo ""
echo "<<< Detected Operating System: $OS_TYPE $MAJOR_VERSION.$MINOR_VERSION >>>" | tee -a $LOGFILE


# If the system is SUSE
if [[ "$OS_TYPE" == "sles" || "$OS_TYPE" == "opensuse" ]]; then
  echo ""
  echo "################################" | tee -a $LOGFILE
  echo "# Running SUSE Specific Checks #" | tee -a $LOGFILE
  echo "################################" | tee -a $LOGFILE

  # 6.1 Check SUSEConnect registration status
  echo ""
  echo "# 6.1 Check SUSEConnect Registration #" | tee -a $LOGFILE

  SUSECONNECT_STATUS=$(SUSEConnect --status-text 2>&1)

  if [[ $SUSECONNECT_STATUS == *"Registered"* ]]; then
    echo "SUSEConnect is properly registered." | tee -a $LOGFILE
  else
    echo "Warning: SUSEConnect is not properly registered. Please check the registration status." | tee -a $LOGFILE
    echo "$SUSECONNECT_STATUS" | tee -a $LOGFILE
  fi

  # 6.2 Check repository configuration and health
  echo ""
  echo "# 6.2 Check Repository Configuration #" | tee -a $LOGFILE

  REPO_CHECK=$(zypper repos --check 2>&1)
  REPO_REFRESH=$(zypper refresh 2>&1)

  if [[ $REPO_CHECK == *"error"* ]]; then
    echo "Warning: Repository check returned errors. Please verify repository settings." | tee -a $LOGFILE
    echo "$REPO_CHECK" | tee -a $LOGFILE
  else
    echo "All repositories are correctly configured." | tee -a $LOGFILE
  fi

  if [[ $REPO_REFRESH == *"error"* ]]; then
    echo "Warning: Repository refresh encountered errors. Please ensure repositories are accessible." | tee -a $LOGFILE
    echo "$REPO_REFRESH" | tee -a $LOGFILE
  else
    echo "Repository refresh successful. All repositories are accessible." | tee -a $LOGFILE
  fi

# If the system is RHEL
elif [[ "$OS_TYPE" == "rhel" ]]; then
  echo ""
  echo "################################" | tee -a $LOGFILE
  echo "# Running RHEL Specific Checks #" | tee -a $LOGFILE
  echo "################################" | tee -a $LOGFILE

  # Check RHEL subscription status using subscription-manager
  echo "Checking if the system is registered with Red Hat Subscription Manager..." | tee -a $LOGFILE
  RHSM_STATUS=$(subscription-manager status 2>&1)
  
  if [[ $RHSM_STATUS == *"Overall Status: Current"* ]]; then
    echo "Red Hat subscription is active and current." | tee -a $LOGFILE
  elif [[ $RHSM_STATUS == *"Overall Status: Disabled"* && $RHSM_STATUS == *"Simple Content Access"* ]]; then
    echo "Simple Content Access (SCA) is enabled. The system has access to content even though the subscription status shows 'Disabled'." | tee -a $LOGFILE
    echo "System is properly registered and has access to repositories." | tee -a $LOGFILE
  else
    echo "Warning: Red Hat subscription may not be active. Please verify subscription status." | tee -a $LOGFILE
    echo "$RHSM_STATUS" | tee -a $LOGFILE
  fi

  # Check RHEL repository status using yum/dnf
  echo "Checking repository configurations..." | tee -a $LOGFILE
  REPO_CHECK=$(yum repolist 2>&1)

  if [[ $REPO_CHECK == *"repolist: 0"* ]]; then
    echo "Warning: No active repositories found. Please verify repository settings." | tee -a $LOGFILE
    echo "$REPO_CHECK" | tee -a $LOGFILE
  else
    echo "Repositories are correctly configured." | tee -a $LOGFILE
  fi

else
  echo "Operating System not recognized. No SUSE or RHEL specific checks will be performed." | tee -a $LOGFILE
fi

#########################
# Common Disk Health and Boot Checks for Both RHEL and SUSE #
#########################

# 1. Check for Incorrect Disk Mounts
echo ""
echo "######################################" | tee -a $LOGFILE
echo "# 1. Check for Incorrect Disk Mounts #" | tee -a $LOGFILE
echo "######################################" | tee -a $LOGFILE

MOUNTED_DISKS=$(df -h | grep '^/dev/')
EXPECTED_DISKS=("/dev/sda1" "/dev/sda2" "/dev/sdb1") # Modify with your expected disks

for disk in "${EXPECTED_DISKS[@]}"; do
  if ! echo "$MOUNTED_DISKS" | grep -q "$disk"; then
    echo "Error: $disk is not mounted correctly." | tee -a $LOGFILE
    echo "Attempting to remount $disk..." | tee -a $LOGFILE
    mount $disk /mountpoint # Modify mountpoint
    if [ $? -eq 0 ]; then
      echo "Successfully remounted $disk." | tee -a $LOGFILE
    else
      echo "Failed to remount $disk. Please check manually." | tee -a $LOGFILE
    fi
  else
    echo "$disk is mounted correctly." | tee -a $LOGFILE
  fi
done

# 2. Check for Unknown Physical Volumes (PVs)
echo ""
echo "###############################################" | tee -a $LOGFILE
echo "# 2. Check for Unknown Physical Volumes (PVs) #" | tee -a $LOGFILE
echo "###############################################" | tee -a $LOGFILE

UNKNOWN_PVS=$(pvs | grep "unknown")

if [ -n "$UNKNOWN_PVS" ]; then
  echo "Unknown Physical Volumes detected:" | tee -a $LOGFILE
  echo "$UNKNOWN_PVS" | tee -a $LOGFILE
  echo "Please investigate the status of the unknown PVs and take corrective action." | tee -a $LOGFILE
else
  echo "No unknown PVs found." | tee -a $LOGFILE
fi

# 3. Run fsck on all partitions
echo ""
echo "#################################" | tee -a $LOGFILE
echo "# 3. Run fsck on all partitions #" | tee -a $LOGFILE
echo "#################################" | tee -a $LOGFILE

for partition in $(lsblk -ln | grep part | awk '{print $1}'); do
  echo "Checking /dev/$partition..." | tee -a $LOGFILE
  fsck -y /dev/$partition 2>&1 | tee -a $LOGFILE
  echo ""  # Add an extra newline after each fsck output
done

# 4. Verify LVM Status
echo ""
echo "########################" | tee -a $LOGFILE
echo "# 4. Verify LVM Status #" | tee -a $LOGFILE
echo "########################" | tee -a $LOGFILE

LVM_VG=$(vgdisplay -c | awk -F: '{print $1}')
if [ -n "$LVM_VG" ]; then
  echo "LVM Volume Group found: $LVM_VG" | tee -a $LOGFILE
  echo "Listing logical volumes:" | tee -a $LOGFILE
  lvs | tee -a $LOGFILE

  # Check for inactive LVMs
  INACTIVE_LVS=$(lvs --noheadings -o lv_attr | grep "^..s")
  if [ -n "$INACTIVE_LVS" ]; then
    echo "Inactive logical volumes detected. Attempting to activate..." | tee -a $LOGFILE
    lvchange -ay $LVM_VG
    if [ $? -eq 0 ]; then
      echo "Successfully activated logical volumes." | tee -a $LOGFILE
    else
      echo "Failed to activate logical volumes. Please check manually." | tee -a $LOGFILE
    fi
  else
    echo "All logical volumes are active." | tee -a $LOGFILE
  fi
else
  echo "No LVM volume group detected." | tee -a $LOGFILE
fi

# 5. Disk Space Check and 30% Free Space Requirement
echo ""
echo "######################################################" | tee -a $LOGFILE
echo "# 5. Disk Space Check and 30% Free Space Requirement #" | tee -a $LOGFILE
echo "######################################################" | tee -a $LOGFILE

for partition in $(df -h | grep "^/dev/" | awk '{print $1}'); do
  # Get the used percentage
  USED_PERCENT=$(df -h | grep "$partition" | awk '{print $5}' | sed 's/%//')
  
  # Calculate the available percentage
  FREE_PERCENT=$((100 - USED_PERCENT))
  
  if [ $FREE_PERCENT -lt $REQUIRED_FREE_PERCENT ]; then
    echo "Warning: $partition has only $FREE_PERCENT% free space, which is below the required $REQUIRED_FREE_PERCENT%." | tee -a $LOGFILE
    echo "Please free up space or extend the partition before proceeding with upgrades." | tee -a $LOGFILE
  else
    echo "$partition has sufficient space: $FREE_PERCENT% free." | tee -a $LOGFILE
  fi
done

##########################################
# MongoDB and SAP HANA Health Monitoring #
##########################################

check_service_status() {
  SERVICE=$1

  # Get the status of the service
  SERVICE_STATUS=$(systemctl status $SERVICE 2>&1)

  # Check if the service is loaded
  if echo "$SERVICE_STATUS" | grep -q "Loaded: loaded"; then
    # Check if the service is active (running)
    if echo "$SERVICE_STATUS" | grep -q "Active: active (running)"; then
      echo "Service $SERVICE is running successfully." | tee -a $LOGFILE
    elif echo "$SERVICE_STATUS" | grep -q "Active: inactive (dead)"; then
      echo "Warning: Service $SERVICE is inactive (stopped)." | tee -a $LOGFILE
    elif echo "$SERVICE_STATUS" | grep -q "Active: failed"; then
      echo "Warning: Service $SERVICE has failed. Please investigate." | tee -a $LOGFILE
    else
      echo "Warning: Service $SERVICE is loaded but in an unknown state. Please investigate." | tee -a $LOGFILE
    fi
  else
    # If the service is not found (not loaded)
    echo "Service $SERVICE not found or disabled. Skipping checks for $SERVICE." | tee -a $LOGFILE
  fi
}


# Check MongoDB Service
echo ""
echo "############################" | tee -a $LOGFILE
echo "# Checking MongoDB Service #" | tee -a $LOGFILE
echo "############################" | tee -a $LOGFILE
check_service_status "mongod"

# Check SAP HANA Service
echo ""
echo "#############################" | tee -a $LOGFILE
echo "# Checking SAP HANA Service #" | tee -a $LOGFILE
echo "#############################" | tee -a $LOGFILE
check_service_status "sapinit"

# Summary and Log End
echo " "
echo "=============================================" | tee -a $LOGFILE
echo "Disk Health Check, SUSE/RHEL OS, and Repository Check Completed" | tee -a $LOGFILE
echo "Log saved at: $LOGFILE"

exit 0
