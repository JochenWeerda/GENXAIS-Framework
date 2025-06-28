"""
GENXAIS Framework - Robust Error Handling Framework
PREVENTS UNNECESSARY OVERWRITES - EXTENDS ONLY CAREFULLY
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

class SDKErrorHandler:
    """
    Robust error handling for Enterprise SDK.
    RULE: NEVER OVERWRITE CODE - ONLY EXTEND!
    """
    
    def __init__(self):
        self.error_log_file = "logs/sdk_errors.log"
        self.recovery_strategies = {}
        self.setup_logging()
        self.setup_recovery_strategies()
        
    def setup_logging(self):
        """Initializes robust logging system."""
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.error_log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SDK_ErrorHandler")
        self.logger.info("🛡️ SDK Error Handler initialized")
        
    def setup_recovery_strategies(self):
        """Defines recovery strategies for different error types."""
        
        self.recovery_strategies = {
            "api_key_missing": self.recover_api_keys,
            "file_not_found": self.recover_missing_files,
            "import_error": self.recover_import_errors,
            "permission_denied": self.recover_permission_errors,
            "network_error": self.recover_network_errors,
            "apm_cycle_interrupted": self.recover_apm_cycle,
            "rag_storage_failed": self.recover_rag_storage,
            "dependency_missing": self.recover_dependencies
        }
        
    def handle_error(self, error_type: str, error_details: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """
        Central error handling with recovery strategies.
        IMPORTANT: NEVER OVERWRITE CODE - ONLY EXTEND!
        """
        
        self.logger.error(f"🚨 Error detected: {error_type}")
        self.logger.error(f"📋 Details: {error_details}")
        self.logger.error(f"🔍 Context: {context}")
        
        # Document error comprehensively
        error_doc = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_details": error_details,
            "context": context,
            "stack_trace": traceback.format_exc(),
            "recovery_attempted": False,
            "recovery_successful": False
        }
        
        try:
            # Attempt recovery strategy
            if error_type in self.recovery_strategies:
                self.logger.info(f"🔧 Starting recovery strategy for: {error_type}")
                error_doc["recovery_attempted"] = True
                
                recovery_result = self.recovery_strategies[error_type](error_details, context)
                
                if recovery_result.get("success", False):
                    error_doc["recovery_successful"] = True
                    error_doc["recovery_details"] = recovery_result
                    self.logger.info(f"✅ Recovery successful: {error_type}")
                    return {"status": "recovered", "details": recovery_result}
                else:
                    self.logger.warning(f"⚠️ Recovery failed: {error_type}")
                    error_doc["recovery_details"] = recovery_result
            else:
                self.logger.warning(f"❌ No recovery strategy for: {error_type}")
                
        except Exception as recovery_error:
            self.logger.error(f"💥 Recovery error: {str(recovery_error)}")
            error_doc["recovery_error"] = str(recovery_error)
            
        # Save error documentation
        self.save_error_documentation(error_doc)
        
        return {"status": "failed", "error_doc": error_doc}
        
    def recover_api_keys(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery of missing API keys."""
        
        self.logger.info("🔑 Attempting API Key Recovery...")
        
        # 1. Search in .env files
        env_files = [".env", ".env.local", ".env.production", "config/.env"]
        found_keys = {}
        
        for env_file in env_files:
            if os.path.exists(env_file):
                self.logger.info(f"📁 Checking {env_file}...")
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if '=' in line and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if 'API' in key.upper() or 'KEY' in key.upper():
                                    found_keys[key] = value
                                    self.logger.info(f"🔑 Found: {key}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error reading {env_file}: {e}")
        
        # 2. Search in environment variables
        for env_var in os.environ:
            if 'API' in env_var.upper() or 'KEY' in env_var.upper():
                found_keys[env_var] = os.environ[env_var]
                self.logger.info(f"🌍 Environment variable found: {env_var}")
        
        # 3. Create .env template if nothing found
        if not found_keys:
            self.logger.info("📝 Creating .env template...")
            env_template = """# GENXAIS Framework API Configuration
# Please enter valid API keys:

OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
MONGODB_URI=mongodb://localhost:27017
RAG_API_KEY=your_rag_key_here

# Enterprise-specific APIs
IOT_SENSOR_API_KEY=your_iot_key_here
ML_SERVICE_API_KEY=your_ml_key_here
"""
            
            try:
                with open(".env.template", 'w') as f:
                    f.write(env_template)
                self.logger.info("✅ .env.template created")
                
                return {
                    "success": True,
                    "message": ".env.template created - please enter keys",
                    "template_created": True,
                    "next_steps": ["Enter API keys in .env.template", "Rename file to .env"]
                }
            except Exception as e:
                return {"success": False, "error": f"Template creation failed: {e}"}
        
        return {
            "success": True,
            "found_keys": list(found_keys.keys()),
            "message": f"{len(found_keys)} API keys found"
        }
        
    def recover_missing_files(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery of missing files."""
        
        missing_file = error_details.get("file_path", "unknown")
        self.logger.info(f"📁 Attempting recovery of: {missing_file}")
        
        # 1. Search in alternative paths
        search_paths = [
            ".",
            "genxais",
            "backend",
            "src",
            "scripts",
            "../genxais",
            "apm_framework"
        ]
        
        filename = os.path.basename(missing_file)
        
        for search_path in search_paths:
            potential_path = os.path.join(search_path, filename)
            if os.path.exists(potential_path):
                self.logger.info(f"✅ File found in: {potential_path}")
                return {
                    "success": True,
                    "found_path": potential_path,
                    "message": f"File found in {potential_path}"
                }

    def create_minimal_python_file(self, file_path: str) -> Dict[str, Any]:
        """Creates a minimal Python file with basic structure."""
        
        try:
            minimal_content = f'''"""
{os.path.basename(file_path)} - GENXAIS Framework Component
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from typing import Dict, Any, Optional

def main():
    """Main function placeholder."""
    pass

if __name__ == "__main__":
    main()
'''
            with open(file_path, 'w') as f:
                f.write(minimal_content)
                
            return {
                "success": True,
                "message": f"Created minimal Python file: {file_path}",
                "content_type": "python"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_minimal_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Creates a minimal Markdown file with basic structure."""
        
        try:
            minimal_content = f'''# {os.path.basename(file_path)}

## Overview

[Description needed]

## Features

- Feature 1
- Feature 2

## Usage

```python
# Usage example
```

## Configuration

[Configuration details needed]

## License

[License information]
'''
            with open(file_path, 'w') as f:
                f.write(minimal_content)
                
            return {
                "success": True,
                "message": f"Created minimal Markdown file: {file_path}",
                "content_type": "markdown"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_minimal_json_file(self, file_path: str) -> Dict[str, Any]:
        """Creates a minimal JSON file with basic structure."""
        
        try:
            minimal_content = {
                "name": os.path.basename(file_path),
                "version": "0.1.0",
                "created": datetime.now().isoformat(),
                "description": "Auto-generated configuration file",
                "settings": {},
                "metadata": {
                    "auto_generated": True,
                    "requires_review": True
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(minimal_content, f, indent=2)
                
            return {
                "success": True,
                "message": f"Created minimal JSON file: {file_path}",
                "content_type": "json"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def recover_import_errors(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery strategy for import errors."""
        
        missing_module = error_details.get("module", "unknown")
        self.logger.info(f"📦 Attempting to recover import error for: {missing_module}")
        
        try:
            # Check if it's a standard library module
            if missing_module in sys.stdlib_module_names:
                return {
                    "success": True,
                    "message": f"{missing_module} is a standard library module",
                    "action_required": "Check Python version compatibility"
                }
            
            # Try pip install
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", missing_module],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully installed {missing_module}",
                    "pip_output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to install {missing_module}",
                    "pip_error": result.stderr
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def recover_apm_cycle(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery strategy for interrupted APM cycles."""
        
        self.logger.info("🔄 Attempting APM cycle recovery...")
        
        try:
            # Load last known state
            state_file = "apm_framework/last_state.json"
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    last_state = json.load(f)
                    
                return {
                    "success": True,
                    "last_state": last_state,
                    "message": "APM state recovered",
                    "next_step": last_state.get("next_phase", "VAN")
                }
            else:
                # Create new state file
                new_state = {
                    "phase": "VAN",
                    "timestamp": datetime.now().isoformat(),
                    "status": "recovered",
                    "next_phase": "PLAN"
                }
                
                os.makedirs(os.path.dirname(state_file), exist_ok=True)
                with open(state_file, 'w') as f:
                    json.dump(new_state, f, indent=2)
                    
                return {
                    "success": True,
                    "message": "Created new APM state",
                    "new_state": new_state
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def recover_rag_storage(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery strategy for RAG storage failures."""
        
        self.logger.info("📚 Attempting RAG storage recovery...")
        
        try:
            # Check for backup storage
            backup_paths = [
                "rag_system/backup",
                "../rag_backup",
                "memory-bank/rag_backup"
            ]
            
            for backup_path in backup_paths:
                if os.path.exists(backup_path):
                    self.logger.info(f"Found RAG backup in: {backup_path}")
                    return {
                        "success": True,
                        "backup_path": backup_path,
                        "message": "RAG backup found"
                    }
            
            # Create new RAG storage
            os.makedirs("rag_system/storage", exist_ok=True)
            
            return {
                "success": True,
                "message": "Created new RAG storage",
                "storage_path": "rag_system/storage"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def recover_network_errors(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery strategy for network errors."""
        
        self.logger.info("🌐 Attempting network recovery...")
        
        # Implementation depends on specific network requirements
        return {
            "success": False,
            "message": "Network recovery requires manual intervention",
            "required_action": "Check network connectivity and firewall settings"
        }

    def recover_permission_errors(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery strategy for permission errors."""
        
        self.logger.info("🔒 Attempting permission recovery...")
        
        return {
            "success": False,
            "message": "Permission recovery requires manual intervention",
            "required_action": "Check file/directory permissions and user access rights"
        }

    def recover_dependencies(self, error_details: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Recovery strategy for missing dependencies."""
        
        self.logger.info("📦 Attempting dependency recovery...")
        
        try:
            # Try to install from requirements.txt
            if os.path.exists("requirements.txt"):
                import subprocess
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Dependencies installed from requirements.txt",
                        "pip_output": result.stdout
                    }
                    
            return {
                "success": False,
                "message": "Could not find requirements.txt",
                "required_action": "Create requirements.txt or manually install dependencies"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_error_documentation(self, error_doc: Dict[str, Any]):
        """Saves comprehensive error documentation."""
        
        try:
            os.makedirs("logs/error_docs", exist_ok=True)
            
            filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("logs/error_docs", filename)
            
            with open(filepath, 'w') as f:
                json.dump(error_doc, f, indent=2)
                
            self.logger.info(f"📝 Error documentation saved: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save error documentation: {e}")


def safe_execute(func, *args, **kwargs):
    """
    Safe execution wrapper with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Dict containing execution result or error details
    """
    
    error_handler = SDKErrorHandler()
    
    try:
        result = func(*args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        return error_handler.handle_error(
            error_type="execution_error",
            error_details={
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs,
                "error": str(e)
            }
        ) 