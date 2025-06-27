"""
Example pipeline script for GENXAIS Framework
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add parent directory to path to import framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from genxais_sdk import GENXAISFramework
from core.pipeline_manager import PipelineStep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GENXAIS.Example")

# Define pipeline step functions
async def analyze_requirements(context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze requirements for a feature"""
    logger.info(f"Analyzing requirements for feature: {context.get(\"feature\")}")
    
    # In a real implementation, this would perform actual analysis
    # For this example, we just return a mock result
    return {
        "requirements": [
            f"Requirement 1 for {context.get(\"feature\")}",
            f"Requirement 2 for {context.get(\"feature\")}",
            f"Requirement 3 for {context.get(\"feature\")}"
        ],
        "priority": "high",
        "complexity": "medium"
    }
