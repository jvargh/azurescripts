
# Disk Health Check and Azure VM Validation Script

This script is designed to automate the process of **disk health checks**, **boot recovery validation**, and **Azure VM snapshot and critical services** verification. It ensures that virtual machines and disks in Azure environments are properly monitored, allowing for automatic detection of common issues such as missing snapshots, disk space shortages, improper disk mounts, and status of critical services like MongoDB and SAP HANA. 

Additionally, the script provides system-specific checks for **RHEL** and **SUSE** Linux environments, including repository health validation and service monitoring.

---

## Features

- **Azure VM Snapshot Validation**: Automatically checks for snapshots associated with each VM’s OS and data disks to verify their availability and status.
- **Operating System Detection**: Identifies whether the system is running **RHEL** or **SUSE** and runs corresponding OS-specific checks.
- **Disk Health Checks**: Validates disk mounts, runs filesystem consistency checks (`fsck`), verifies LVM status, and ensures that at least 30% disk space is available before any upgrade or operations.
- **Service Health Monitoring**: Monitors critical services like **MongoDB** and **SAP HANA** and reports their status (running, stopped, failed, or unknown).
- **Comprehensive Logging**: Outputs results and warnings to a log file (`/var/log/disk_health_check.log`), enabling easy monitoring and troubleshooting.
  
---

### Sample output
![image](https://github.com/user-attachments/assets/eaaa8317-81f7-4973-a683-2eb23c36b4f7)

---
## Prerequisites

Before running the script, ensure the following:

1. **Azure CLI**: Installed and configured with access to the necessary resource groups in Azure.
2. **Sudo/Root Access**: The script needs to be run with root privileges.
3. **Systemd Services**: MongoDB (`mongod`) and SAP HANA (`sapinit`) services should be available for monitoring.
4. **Azure Resource Group**: Specify the appropriate resource group for checking snapshots in the `RESOURCE_GROUP` variable.
5. **OS-Specific Tools**:
    - **RHEL**: Ensure `subscription-manager` and `yum/dnf` are installed and accessible.
    - **SUSE**: Ensure `SUSEConnect` and `zypper` are installed.

---

## How It Works

1. **Azure VM Snapshot Validation**: The script first retrieves the list of VMs in the specified resource group. For each VM, it checks the status of associated snapshots for both the OS and data disks. It flags missing or incomplete snapshots.
   
2. **OS-Specific Checks**: Depending on whether the system is running **RHEL** or **SUSE**, the script performs different checks. It verifies repository health, system registration status (SUSEConnect or subscription-manager), and other system settings.
   
3. **Disk Health Checks**: The script performs multiple disk-related validations:
    - Checks if expected disks are mounted correctly.
    - Runs `fsck` on all partitions to ensure filesystem consistency.
    - Verifies the status of LVM (Logical Volume Management).
    - Ensures that each partition has at least 30% free space.

4. **Service Health Monitoring**: Monitors the status of **MongoDB** and **SAP HANA** services using `systemctl`. It reports if the services are running, stopped, or failed.

---

## How to Use

1. **Clone or Download the Script**:
    Download the `disk_health_check.sh` script to your server.
   
2. **Edit Configuration**:
    Modify the `RESOURCE_GROUP` variable in the script to reflect the Azure resource group where your VMs are located.

    ```bash
    RESOURCE_GROUP="your-resource-group"
    ```

3. **Run the Script**:
    The script requires root privileges, so run it with `sudo`:

    ```bash
    sudo ./disk_health_check.sh
    ```

4. **Check the Output**:
    Results will be logged to `/var/log/disk_health_check.log`. You can review the log for warnings or errors related to disk health, snapshot status, or service failures.

---

## FAQ

**1. Can this script run on non-Azure systems?**

   - The script is specifically designed to work with Azure environments. However, the disk health and service checks should still function on non-Azure systems, although Azure-specific functionality (like snapshot checks) won’t work.

**2. What happens if MongoDB or SAP HANA services are not installed?**

   - If the services are not found, the script will log a message indicating that the services are not installed or found and will skip further checks for that service.

**3. How can I customize the disk mount checks?**

   - You can modify the `EXPECTED_DISKS` array in the script to match the expected disk names for your environment.

---

## Contributing

If you would like to contribute to the improvement of this script, please follow these steps:

1. Fork this repository.
2. Make your changes.
3. Submit a pull request for review.

All contributions are welcome, whether it’s code improvements, bug fixes, or new features.

---

## License

This script is provided "as-is," without any warranty of any kind. You are free to use, modify, and distribute it, but the authors are not responsible for any damage or loss caused by its use. Ensure you test it thoroughly in your environment before deploying it in production systems.

By using this script, you agree to the terms above and assume full responsibility for its use.
