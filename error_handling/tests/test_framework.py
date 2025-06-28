"""
Tests for the Error Handling Framework
"""

import os
import pytest
from ..framework import SDKErrorHandler, safe_execute

@pytest.fixture
def error_handler():
    """Create a fresh error handler instance for each test."""
    handler = SDKErrorHandler()
    return handler

def test_error_handler_initialization(error_handler):
    """Test basic initialization of error handler."""
    assert error_handler.error_log_file == "logs/sdk_errors.log"
    assert isinstance(error_handler.recovery_strategies, dict)

def test_api_key_recovery(error_handler):
    """Test API key recovery strategy."""
    result = error_handler.recover_api_keys(
        error_details={"service": "test"},
        context="test"
    )
    assert isinstance(result, dict)
    assert "success" in result

def test_missing_file_recovery(error_handler):
    """Test missing file recovery strategy."""
    result = error_handler.recover_missing_files(
        error_details={"file_path": "nonexistent.txt"},
        context="test"
    )
    assert isinstance(result, dict)
    assert "success" in result

def test_safe_execute():
    """Test safe execution wrapper."""
    def good_function():
        return "success"
        
    def bad_function():
        raise ValueError("test error")
        
    # Test successful execution
    result = safe_execute(good_function)
    assert result["success"] is True
    assert result["result"] == "success"
    
    # Test error handling
    result = safe_execute(bad_function)
    assert result["success"] is False
    assert "error_doc" in result

def test_error_documentation(error_handler, tmp_path):
    """Test error documentation creation."""
    error_doc = {
        "error_type": "test_error",
        "error_details": {"test": True},
        "context": "test"
    }
    
    # Temporarily redirect logs to test directory
    original_log_file = error_handler.error_log_file
    error_handler.error_log_file = str(tmp_path / "test.log")
    
    error_handler.save_error_documentation(error_doc)
    
    # Check if log directory was created
    assert os.path.exists(os.path.dirname(error_handler.error_log_file))
    
    # Restore original log file
    error_handler.error_log_file = original_log_file

def test_recovery_strategies_exist(error_handler):
    """Test that all advertised recovery strategies exist."""
    expected_strategies = [
        "api_key_missing",
        "file_not_found",
        "import_error",
        "permission_denied",
        "network_error",
        "apm_cycle_interrupted",
        "rag_storage_failed",
        "dependency_missing"
    ]
    
    for strategy in expected_strategies:
        assert strategy in error_handler.recovery_strategies 