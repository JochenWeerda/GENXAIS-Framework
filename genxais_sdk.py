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
        self._init_error_handling()
        self._init_rag_system()
        self.logger.info("GENXAIS Framework initialized")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "token_optimization": True,
            "parallel_execution": True,
            "logging_level": "INFO",
            "max_retries": 3,
            "timeout": 60,
            "rag_storage": "mongodb",
            "mongodb_uri": "mongodb://localhost:27017/",
            "error_handling": {
                "retry_on_failure": True,
                "max_retries": 3,
                "backoff_factor": 2
            }
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

    def _init_error_handling(self):
        """Initialize error handling system"""
        try:
            from error_handling.framework import ErrorHandler
            self.error_handler = ErrorHandler(self.config["error_handling"])
            self.logger.info("Error handling system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize error handling: {e}")
            raise

    def _init_rag_system(self):
        """Initialize RAG system"""
        try:
            from rag_system.init_storage import init_storage
            self.rag_storage = init_storage(
                storage_type=self.config["rag_storage"],
                connection_uri=self.config.get("mongodb_uri")
            )
            self.logger.info("RAG system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            raise

    def register_agent(self, name: str, agent_class: type) -> bool:
        """Register a new agent
        
        Args:
            name: Name of the agent
            agent_class: Agent class to register
            
        Returns:
            bool: True if registration was successful
        """
        try:
            if name in self.agents:
                self.logger.warning(f"Agent {name} already registered, updating...")
            self.agents[name] = agent_class(self.config)
            self.logger.info(f"Agent {name} registered successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register agent {name}: {e}")
            return False

    def execute_pipeline(self, pipeline_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a pipeline
        
        Args:
            pipeline_name: Name of the pipeline to execute
            **kwargs: Additional arguments for the pipeline
            
        Returns:
            Dict[str, Any]: Pipeline execution results
        """
        try:
            if pipeline_name not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_name} not found")
                
            pipeline = self.pipelines[pipeline_name]
            with self.error_handler.context():
                result = pipeline.execute(**kwargs)
                self.logger.info(f"Pipeline {pipeline_name} executed successfully")
                return result
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise
