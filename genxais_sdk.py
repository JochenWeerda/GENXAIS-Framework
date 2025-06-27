"""
GENXAIS SDK - Core framework for AI-enhanced software development
"""

import os
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union

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
