#!/bin/bash

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

# Step 1: Check installed kernels and current booted kernel
echo "Checking installed kernels..."
INSTALLED_KERNELS=$(rpm -qa | grep -i kernel | grep -v kernel-headers)
echo "$INSTALLED_KERNELS"

CURRENT_KERNEL=$(uname -r)
echo "Currently booted kernel: $CURRENT_KERNEL"

# Step 2: Get the newest installed kernel
NEWEST_KERNEL=$(rpm -q --last kernel | head -n 1 | awk '{print $1}' | sed 's/kernel-//')

# Step 3: Check if the newest installed kernel is in use
if [[ "$CURRENT_KERNEL" == "$NEWEST_KERNEL" ]]; then
  echo "The system is already running the latest kernel: $NEWEST_KERNEL"
  exit 0
else
  echo "A newer kernel ($NEWEST_KERNEL) is installed but not in use."

  # Ask the user if they want to install and reboot into the latest kernel
  read -p "Would you like to install and reboot into the latest kernel? (y/n): " USER_RESPONSE
  if [[ "$USER_RESPONSE" == "y" || "$USER_RESPONSE" == "Y" ]]; then
    # Step 4: Install the latest kernel if user confirms
    echo "Installing the latest kernel..."
    yum install kernel -y
    echo "Rebooting after kernel installation..."
    reboot
  else
    echo "Exiting without installing the latest kernel."
    exit 0
  fi
fi
