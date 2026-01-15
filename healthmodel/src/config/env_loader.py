"""
Environment Variable Loader

Loads configuration from .env file for use in health model scripts
"""

import os
from pathlib import Path
from typing import Optional


class EnvLoader:
    """Load environment variables from .env file"""
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize environment loader
        
        Args:
            env_path: Path to .env file (default: .env in project root)
        """
        if env_path is None:
            # Look for .env in project root (3 levels up: src/config/env_loader.py -> src -> project root)
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / ".env"
        
        self.env_path = env_path
        self.env_vars = {}
        self._load_env()
    
    def _load_env(self) -> None:
        """Load variables from .env file"""
        if not os.path.exists(self.env_path):
            print(f"Warning: .env file not found at {self.env_path}")
            self._create_default_env()
            return
        
        with open(self.env_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    self.env_vars[key] = value
                    # Also set in os.environ so subprocess calls can access it
                    if value:
                        os.environ[key] = value
    
    def _create_default_env(self) -> None:
        """Create a default .env file with template values"""
        default_content = """# Azure Health Model Configuration
# These environment variables are used by health model scripts

# Azure Subscription ID
AZURE_SUBSCRIPTION_ID=

# Azure Resource Group
AZURE_RESOURCE_GROUP=

# Health Model Name
HEALTH_MODEL_NAME=

# Azure Tenant ID (optional - will use default if not set)
AZURE_TENANT_ID=

# Auth Token (optional - will be fetched from Azure CLI if not set)
AZURE_AUTH_TOKEN=
"""
        try:
            with open(self.env_path, 'w') as f:
                f.write(default_content)
            print(f"✓ Created default .env file at {self.env_path}")
            print("  Please edit .env and add your Azure configuration values.")
        except Exception as e:
            print(f"Error creating .env file: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable value"""
        return self.env_vars.get(key, os.environ.get(key, default))
    
    def get_azure_config(self) -> dict:
        """Get Azure configuration from env vars"""
        return {
            "subscriptionId": self.get("AZURE_SUBSCRIPTION_ID"),
            "resourceGroup": self.get("AZURE_RESOURCE_GROUP"),
            "healthModelName": self.get("HEALTH_MODEL_NAME"),
            "tenantId": self.get("AZURE_TENANT_ID", ""),
        }
    
    def validate(self) -> bool:
        """Validate required variables are set"""
        required = [
            "AZURE_SUBSCRIPTION_ID",
            "AZURE_RESOURCE_GROUP",
            "HEALTH_MODEL_NAME"
        ]
        
        missing = []
        for key in required:
            if not self.get(key):
                missing.append(key)
        
        if missing:
            print(f"Error: Missing required environment variables: {', '.join(missing)}")
            return False
        
        return True
    
    def __repr__(self) -> str:
        """String representation"""
        return f"EnvLoader(path={self.env_path})"


def load_env(env_path: Optional[str] = None) -> EnvLoader:
    """Convenience function to load environment"""
    return EnvLoader(env_path)


if __name__ == "__main__":
    loader = load_env()
    
    if loader.validate():
        print("✓ Environment variables loaded successfully")
        config = loader.get_azure_config()
        print(f"\nAzure Configuration:")
        print(f"  Subscription: {config['subscriptionId']}")
        print(f"  Resource Group: {config['resourceGroup']}")
        print(f"  Health Model: {config['healthModelName']}")

