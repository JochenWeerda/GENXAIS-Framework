"""
Tests for RAG storage initialization
"""

import os
import pytest
import mongomock
from datetime import datetime
from ..init_storage import RAGStorageInitializer

@pytest.fixture
def storage_initializer():
    """Create a test instance of RAGStorageInitializer."""
    return RAGStorageInitializer("mongodb://test:27017")

@pytest.fixture
def mock_mongodb():
    """Create a mock MongoDB client."""
    return mongomock.MongoClient()

def test_init_filesystem(storage_initializer, tmp_path):
    """Test filesystem initialization."""
    
    # Set up test environment
    os.chdir(tmp_path)
    os.makedirs("rag_system", exist_ok=True)
    
    # Initialize filesystem
    result = storage_initializer.init_filesystem()
    
    # Check result
    assert result["success"] is True
    assert "directories" in result
    assert "metadata_path" in result
    
    # Check directories
    for directory in result["directories"]:
        assert os.path.exists(os.path.join("rag_system", directory))
        
    # Check metadata file
    assert os.path.exists(result["metadata_path"])
    
def test_init_mongodb(storage_initializer, monkeypatch):
    """Test MongoDB initialization."""
    
    # Mock MongoDB client
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("pymongo.MongoClient", lambda x: mock_client)
    
    # Initialize MongoDB
    result = storage_initializer.init_mongodb()
    
    # Check result
    assert result["success"] is True
    assert "collections" in result
    assert "database" in result
    
    # Check collections
    db = mock_client[storage_initializer.db_name]
    for collection in storage_initializer.required_collections:
        assert collection in db.list_collection_names()
        
def test_init_error_handling(storage_initializer, tmp_path):
    """Test error handling initialization."""
    
    # Set up test environment
    os.chdir(tmp_path)
    os.makedirs("rag_system", exist_ok=True)
    
    # Initialize error handling
    result = storage_initializer.init_error_handling()
    
    # Check result
    assert result["success"] is True
    assert "log_file" in result
    
    # Check log file
    assert os.path.exists(result["log_file"])
    
def test_initialize_all(storage_initializer, tmp_path, monkeypatch):
    """Test complete initialization."""
    
    # Set up test environment
    os.chdir(tmp_path)
    os.makedirs("rag_system", exist_ok=True)
    
    # Mock MongoDB client
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("pymongo.MongoClient", lambda x: mock_client)
    
    # Initialize everything
    result = storage_initializer.initialize_all()
    
    # Check result
    assert result["success"] is True
    assert "results" in result
    assert "timestamp" in result
    
    # Check individual results
    assert result["results"]["filesystem"]["success"] is True
    assert result["results"]["mongodb"]["success"] is True
    assert result["results"]["error_handling"]["success"] is True
    
def test_mongodb_validation(storage_initializer, monkeypatch):
    """Test MongoDB schema validation."""
    
    # Mock MongoDB client
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("pymongo.MongoClient", lambda x: mock_client)
    
    # Initialize MongoDB
    storage_initializer.init_mongodb()
    db = mock_client[storage_initializer.db_name]
    
    # Test document validation
    valid_doc = {
        "title": "Test",
        "content": "Content",
        "created_at": datetime.now()
    }
    db.documents.insert_one(valid_doc)  # Should work
    
    # Test invalid document
    invalid_doc = {
        "title": "Test"  # Missing required fields
    }
    with pytest.raises(mongomock.OperationFailure):
        db.documents.insert_one(invalid_doc)
        
def test_connection_error(storage_initializer):
    """Test handling of MongoDB connection errors."""
    
    # Use invalid MongoDB URI
    initializer = RAGStorageInitializer("mongodb://invalid:1234")
    result = initializer.init_mongodb()
    
    assert result["success"] is False
    assert result["type"] == "connection_error" 