
# Kernel Management Script for RHEL
This repository contains a script to automate the process of checking if the system is running the latest installed kernel on Red Hat Enterprise Linux (RHEL). It helps identify whether the system needs to be updated to the newest kernel version and prompts the user for an update if a newer kernel is available.

## Features
- Checks installed kernels and the currently booted kernel.
- Compares the running kernel version with the latest installed version.
- Prompts the user if a newer kernel is available, allowing them to choose whether to install and reboot into the latest kernel.
- Avoids making any changes if the system is already running the latest kernel.

## Prerequisites
- Red Hat Enterprise Linux 7.x or later.
- Ensure you have `yum` package manager installed and working.
- Root or sudo access to install packages and reboot the system.

## How it works
- Check Installed Kernels: Lists all installed kernels using rpm -qa | grep -i kernel.
- Check Current Booted Kernel: Displays the currently running kernel with uname -r.
- Compare with the Latest Kernel: The script identifies the latest installed kernel using rpm -q --last kernel.
- Prompt the User: If the latest kernel is not in use, the script asks if the user wants to install and reboot into the latest kernel.
  - If the user confirms (y), it proceeds with the installation and reboot.
  - If the user declines (n), the script exits without making changes.
- Latest Kernel Check: If the system is already using the latest kernel, it informs the user and exits.

## How to Use
1. **Make the Script Executable**:
   After downloading script, ensure that the script has execution permissions:
   ```bash
   chmod +x kernelcheck.sh
   ```

3. **Run the Script**:
   Execute the script using `sudo` to check your system’s kernel status:
   ```bash
   sudo ./kernelcheck.sh
   ```

   The script will:
   - Display all installed kernels.
   - Check the currently booted kernel.
   - If a newer kernel is available but not in use, it will prompt the user to install and reboot into it.

4. **Example Output**:
   ```bash
   Checking installed kernels...
   kernel-tools-3.10.0-1160.119.1.el7.x86_64
   kernel-3.10.0-1160.119.1.el7.x86_64
   kernel-3.10.0-1160.el7.x86_64
   kernel-3.10.0-1160.83.1.el7.x86_64
   abrt-addon-kerneloops-2.1.11-60.el7.x86_64
   kernel-tools-libs-3.10.0-1160.119.1.el7.x86_64
   Currently booted kernel: 3.10.0-1160.119.1.el7.x86_64
   The system is already running the latest kernel: 3.10.0-1160.119.1.el7.x86_64
   ```

5. **Testing with an Older Kernel**:
   To simulate a scenario where the system is not running the latest kernel, follow these steps:
   - Reboot the system and manually select an older kernel from the GRUB menu.
   - Run the script again to test its behavior when a newer kernel is available but not in use.

6. Output: Latest Kernel in place
   
![image](https://github.com/user-attachments/assets/f896148a-8ce8-4b9a-9a7a-298422b84798)

8. Output: Older kernel in place
   
![image](https://github.com/user-attachments/assets/79850795-59da-44f9-b567-710d8ac22f6a)

## FAQ

### What happens if I choose not to install the latest kernel?
The script will exit without making any changes to your system, leaving the currently booted kernel as is.

### How do I revert back to the latest kernel after testing?
If you have booted into an older kernel for testing, simply reboot and select the latest kernel from the GRUB menu. Alternatively, you can let the script install and reboot into the latest kernel automatically if you confirm the prompt.

## Contributing
Feel free to open issues or submit pull requests to improve the script or add more features.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

