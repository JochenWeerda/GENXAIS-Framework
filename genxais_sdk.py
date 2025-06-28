"""
GENXAIS SDK - Core framework for AI-enhanced software development
"""

import os
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GENXAIS")

class GENXAISFramework:
    """Main framework class for GENXAIS"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the GENXAIS framework
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.agents = {}
        self.pipelines = {}
        self.modes = ["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT", "ARCHIVE"]
        self.current_mode = self._get_current_mode()
        self.logger.info("GENXAIS Framework initialized")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "token_optimization": True,
            "parallel_execution": True,
            "logging_level": "INFO",
            "max_retries": 3,
            "timeout": 60,
        }
        
        if not config_path:
            self.logger.info("Using default configuration")
            return default_config
            
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                self.logger.info(f"Configuration loaded from {config_path}")
                return {**default_config, **config}
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return default_config
            
    def _get_current_mode(self) -> str:
        """Get the current mode from the .genxais directory"""
        mode_file = Path.home() / ".genxais" / "current_mode.txt"
        if mode_file.exists():
            try:
                with open(mode_file, "r") as f:
                    mode = f.read().strip()
                    if mode in self.modes:
                        return mode
            except Exception as e:
                self.logger.error(f"Error reading current mode: {e}")
        
        # Default to VAN mode if no mode is set
        return "VAN"
        
    def set_mode(self, mode: str) -> bool:
        """Set the current mode
        
        Args:
            mode: The mode to set (VAN, PLAN, CREATE, IMPLEMENT, REFLECT, ARCHIVE)
            
        Returns:
            bool: True if the mode was set successfully, False otherwise
        """
        if mode not in self.modes:
            self.logger.error(f"Invalid mode: {mode}")
            return False
            
        try:
            os.makedirs(Path.home() / ".genxais", exist_ok=True)
            with open(Path.home() / ".genxais" / "current_mode.txt", "w") as f:
                f.write(mode)
            self.current_mode = mode
            self.logger.info(f"Mode set to {mode}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting mode: {e}")
            return False
            
    def get_mode(self) -> str:
        """Get the current mode
        
        Returns:
            str: The current mode
        """
        return self.current_mode
