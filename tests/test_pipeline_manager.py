"""
Tests for the Pipeline Manager
"""

import os
import sys
import pytest
import asyncio
from typing import Dict, Any

# Add parent directory to path to import framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline_manager import PipelineManager, PipelineStep

# Test pipeline step functions
async def test_function(context: Dict[str, Any]) -> Dict[str, Any]:
    """Test function for pipeline steps"""
    return {"result": "success", "input": context.get("input", "none")}

async def failing_function(context: Dict[str, Any]) -> Dict[str, Any]:
    """Function that fails for testing error handling"""
    raise ValueError("Test error")

async def error_handler(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Error handler for testing"""
    return {"error_handled": True, "error_type": str(type(error).__name__)}

# Tests
@pytest.mark.asyncio
async def test_pipeline_creation():
    """Test creating a pipeline"""
    manager = PipelineManager()
    
    pipeline_id = await manager.create_pipeline(
        "test_pipeline",
        [
            PipelineStep(
                name="step1",
                function=test_function,
                requires=["input1"],
                provides=["output1"]
            )
        ]
    )
    
    assert pipeline_id is not None
    assert pipeline_id in manager.pipelines
    assert manager.pipelines[pipeline_id]["name"] == "test_pipeline"
    assert len(manager.pipelines[pipeline_id]["steps"]) == 1
