"""
Basic tests for the GENXAIS Framework
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch
import numpy as np
from sentence_transformers import SentenceTransformer

from genxais_sdk import GENXAISFramework
from agents.base_agent import AgentMode, BaseAgent
from rag_system.rag_service import RAGService, Document, QueryResult
from error_handling.framework import SDKErrorHandler

@pytest.fixture
def framework():
    """Create a framework instance for testing."""
    return GENXAISFramework()

@pytest.fixture
def rag_service():
    """Create a RAG service instance for testing."""
    config = {
        "embedding_model": "all-MiniLM-L6-v2",
        "chunk_size": 100,
        "chunk_overlap": 20,
        "top_k": 3
    }
    return RAGService(config)

@pytest.fixture
def error_handler():
    """Create an error handler instance for testing."""
    return SDKErrorHandler()

class TestFrameworkBasics:
    """Test basic framework functionality."""
    
    def test_framework_initialization(self, framework):
        """Test framework initialization."""
        assert framework is not None
        assert framework.mode == "VAN"
        
    def test_mode_switching(self, framework):
        """Test mode switching functionality."""
        framework.set_mode("PLAN")
        assert framework.mode == "PLAN"
        
        framework.set_mode("CREATE")
        assert framework.mode == "CREATE"
        
    def test_invalid_mode(self, framework):
        """Test handling of invalid modes."""
        with pytest.raises(ValueError):
            framework.set_mode("INVALID")
            
    @pytest.mark.asyncio
    async def test_async_operation(self, framework):
        """Test async operations."""
        result = await framework.analyze_async("test data")
        assert result is not None

class TestRAGSystem:
    """Test RAG system functionality."""
    
    @pytest.mark.asyncio
    async def test_document_addition(self, rag_service):
        """Test adding documents to RAG system."""
        doc = Document(
            id="test1",
            content="This is a test document."
        )
        doc_id = await rag_service.add_document(doc)
        assert doc_id == "test1"
        assert len(rag_service.documents) == 1
        
    @pytest.mark.asyncio
    async def test_document_query(self, rag_service):
        """Test querying documents."""
        # Add test documents
        docs = [
            Document(id="1", content="Python programming"),
            Document(id="2", content="Machine learning"),
            Document(id="3", content="Web development")
        ]
        for doc in docs:
            await rag_service.add_document(doc)
            
        # Test query
        result = await rag_service.query("python code")
        assert isinstance(result, QueryResult)
        assert len(result.documents) > 0
        
    @pytest.mark.asyncio
    async def test_document_deletion(self, rag_service):
        """Test document deletion."""
        doc = Document(id="test2", content="Delete me")
        await rag_service.add_document(doc)
        success = await rag_service.delete_document("test2")
        assert success
        assert "test2" not in rag_service.documents

class TestErrorHandling:
    """Test error handling functionality."""
    
    def test_error_recovery(self, error_handler):
        """Test error recovery strategies."""
        error_details = {"file_path": "missing.txt"}
        result = error_handler.handle_error(
            "file_not_found",
            error_details,
            "Test context"
        )
        assert result["status"] in ["recovered", "failed"]
        
    def test_api_key_recovery(self, error_handler):
        """Test API key recovery."""
        result = error_handler.recover_api_keys(
            {"key_name": "TEST_API_KEY"},
            "Test context"
        )
        assert isinstance(result, dict)
        assert "success" in result
        
    def test_error_documentation(self, error_handler):
        """Test error documentation."""
        error_doc = {
            "error_type": "test_error",
            "error_details": {"test": True},
            "context": "Test context"
        }
        error_handler.save_error_documentation(error_doc)
        # Verify log file exists
        assert os.path.exists("logs/sdk_errors.log")

class TestIntegration:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    async def test_framework_rag_integration(self, framework, rag_service):
        """Test framework and RAG integration."""
        # Add document to RAG
        doc = Document(id="test3", content="Integration test")
        await rag_service.add_document(doc)
        
        # Query through framework
        framework.rag_service = rag_service
        result = await framework.query_knowledge_base("integration")
        assert result is not None
        
    def test_error_handling_integration(self, framework, error_handler):
        """Test error handling integration."""
        framework.error_handler = error_handler
        
        with pytest.raises(Exception):
            framework.process_invalid_operation()
            
        # Check error was logged
        assert os.path.exists("logs/sdk_errors.log")
        
    @pytest.mark.asyncio
    async def test_full_pipeline(self, framework, rag_service, error_handler):
        """Test full pipeline integration."""
        framework.rag_service = rag_service
        framework.error_handler = error_handler
        
        # Test pipeline steps
        try:
            # 1. Set mode
            framework.set_mode("VAN")
            
            # 2. Add document
            doc = Document(id="pipeline", content="Pipeline test")
            await rag_service.add_document(doc)
            
            # 3. Query
            result = await framework.query_knowledge_base("pipeline")
            assert result is not None
            
            # 4. Process result
            processed = framework.process_query_result(result)
            assert processed is not None
            
        except Exception as e:
            # Should be handled by error handler
            error_handler.handle_error(
                "pipeline_error",
                {"error": str(e)},
                "Pipeline test"
            )
            raise

def test_embedding_model():
    """Test embedding model functionality."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    text = "Test embedding generation"
    embedding = model.encode([text])[0]
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] > 0

@pytest.mark.asyncio
async def test_concurrent_operations(rag_service):
    """Test concurrent operations."""
    # Create multiple documents
    docs = [
        Document(id=str(i), content=f"Document {i}")
        for i in range(5)
    ]
    
    # Add documents concurrently
    tasks = [rag_service.add_document(doc) for doc in docs]
    await asyncio.gather(*tasks)
    
    assert len(rag_service.documents) == 5
    
    # Query concurrently
    query_tasks = [
        rag_service.query(f"Document {i}")
        for i in range(3)
    ]
    results = await asyncio.gather(*query_tasks)
    
    assert all(isinstance(r, QueryResult) for r in results)

class TestAgent(BaseAgent):
    """Test agent implementation"""
    async def execute_task(self, task):
        return {"status": "success", "mode": self.mode}

@pytest.mark.asyncio
async def test_agent_restrictions():
    """Test agent restrictions in different modes"""
    for mode in AgentMode:
        agent = TestAgent(mode)
        
        # Test allowed actions
        for action in agent.restrictions.allowed_actions:
            assert agent.validate_action(action) is True
            
        # Test forbidden actions
        for action in agent.restrictions.forbidden_actions:
            assert agent.validate_action(action) is False

def test_error_handling():
    """Test error handling and recovery"""
    framework = GENXAISFramework()
    
    # Test API key recovery
    error_details = {
        "type": "api_key_missing",
        "key": "OPENAI_API_KEY"
    }
    result = framework.error_handler.handle_error(
        "api_key_missing",
        error_details,
        "Testing error recovery"
    )
    assert result["status"] in ["recovered", "failed"]

@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent task execution"""
    agent = TestAgent(AgentMode.VAN)
    result = await agent.execute_task({"type": "test"})
    assert result["status"] == "success"
    assert result["mode"] == AgentMode.VAN

def test_output_quality_validation():
    """Test output quality validation"""
    agent = TestAgent(AgentMode.VAN)
    
    # Test with meeting thresholds
    metrics = {
        "analysis_coverage": 0.9,
        "validation_accuracy": 0.95,
        "report_quality": 0.9
    }
    assert agent.validate_output_quality(metrics) is True
    
    # Test with failing thresholds
    metrics = {
        "analysis_coverage": 0.7,
        "validation_accuracy": 0.8,
        "report_quality": 0.7
    }
    assert agent.validate_output_quality(metrics) is False
