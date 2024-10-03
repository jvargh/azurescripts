#!/bin/bash
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

# Define Node.js versions to be used
NODE_VERSION="20"  # You can change this to "18" or another supported version
NVM_VERSION="v0.39.3"

# Function to uninstall Node.js 16.x if present
uninstall_nodejs16() {
    echo "Checking if Node.js 16.x is installed..."
    
    if command -v node &>/dev/null && [[ "$(node -v)" == v16* ]]; then
        echo "Node.js 16.x is detected, uninstalling..."
        
        # For Debian/Ubuntu systems
        if [ -f /etc/debian_version ]; then
            sudo apt-get purge --auto-remove -y nodejs
        fi
        
        # For RHEL/CentOS systems
        if [ -f /etc/redhat-release ]; then
            sudo yum remove -y nodejs
        fi
        
        echo "Node.js 16.x uninstalled."
    else
        echo "Node.js 16.x is not installed."
    fi
}

# Function to install Node.js using NodeSource
install_nodejs() {
    echo "Installing Node.js $NODE_VERSION.x..."

    # For Debian/Ubuntu systems
    if [ -f /etc/debian_version ]; then
        curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    # For RHEL/CentOS systems
    if [ -f /etc/redhat-release ]; then
        curl -fsSL https://rpm.nodesource.com/setup_${NODE_VERSION}.x | sudo bash -
        sudo yum install -y nodejs
    fi

    echo "Node.js $NODE_VERSION.x installed."
}

# Function to install Node.js using nvm
install_nodejs_nvm() {
    echo "Installing Node.js $NODE_VERSION.x using nvm..."

    # Install nvm
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh | bash
    source ~/.bashrc

    # Install and use the desired Node.js version
    nvm install $NODE_VERSION
    nvm use $NODE_VERSION

    echo "Node.js $NODE_VERSION.x installed using nvm."
}

# Function to remove residual Node.js 16.x directories
cleanup_nodejs_directories() {
    echo "Cleaning up residual Node.js 16.x directories..."
    sudo rm -rf /usr/bin/node16
    sudo rm -rf /usr/share/licenses/nodejs16
    sudo rm -rf /usr/share/doc/packages/nodejs16
    sudo rm -rf /usr/share/man/man1/node16.1.gz
    echo "Cleanup complete."
}

# Function to update Azure Pipelines Agent
update_azure_agent() {
    echo "Updating Azure Pipelines Agent..."

    AGENT_DIR="/var/opt/azagent"
    AGENT_VERSION="3.220.5"  # Set this to the latest agent version

    # Stop the agent
    sudo systemctl stop azure-pipelines-agent

    # Download and extract the latest agent
    cd $AGENT_DIR
    wget https://vstsagentpackage.azureedge.net/agent/$AGENT_VERSION/vsts-agent-linux-x64-$AGENT_VERSION.tar.gz
    tar zxvf vsts-agent-linux-x64-$AGENT_VERSION.tar.gz

    # Reconfigure the agent
    ./config.sh

    # Start the agent
    sudo systemctl start azure-pipelines-agent

    echo "Azure Pipelines Agent updated."
}

# Function to verify Node.js installation
verify_nodejs_installation() {
    echo "Verifying Node.js installation..."
    node_version=$(node -v)

    if [[ $node_version == v${NODE_VERSION}* ]]; then
        echo "Node.js $node_version successfully installed."
    else
        echo "Failed to install Node.js $NODE_VERSION.x."
    fi
}

# Main script logic
echo "Starting Node.js 16.x removal and upgrade process..."

# 1. Uninstall Node.js 16.x
uninstall_nodejs16

# 2. Remove residual files
cleanup_nodejs_directories

# 3. Install the new version of Node.js (either from NodeSource or using nvm)
# Option 1: Install using package manager
install_nodejs

# Option 2: Install using nvm (comment out install_nodejs if using nvm)
# install_nodejs_nvm

# 4. Update Azure Pipelines Agent
update_azure_agent

# 5. Verify the Node.js installation
verify_nodejs_installation

echo "Node.js remediation process completed."

