#!/bin/bash

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
