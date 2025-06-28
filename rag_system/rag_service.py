"""
RAG Service for the GENXAIS Framework.

This module provides a Retrieval-Augmented Generation (RAG) service for the GENXAIS Framework,
enabling knowledge retrieval and generation based on document collections.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import asyncio
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("GENXAIS.RAGService")

@dataclass
class Document:
    """Represents a document in the RAG system."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None

@dataclass
class QueryResult:
    """Represents a query result from the RAG system."""
    documents: List[Document]
    query: str
    generated_answer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    similarity_scores: List[float] = field(default_factory=list)


class RAGService:
    """
    Retrieval-Augmented Generation (RAG) service for the GENXAIS Framework.
    
    This service enables knowledge retrieval and generation based on document collections.
    It provides methods for indexing documents, querying the knowledge base, and generating
    answers based on retrieved documents.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the RAG service.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.documents: Dict[str, Document] = {}
        self.embedding_model = self._init_embedding_model()
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.top_k = self.config.get("top_k", 5)
        
        logger.info("RAG Service initialized")
        
    def _init_embedding_model(self) -> SentenceTransformer:
        """Initialize the embedding model."""
        model_name = self.config.get("embedding_model", "all-MiniLM-L6-v2")
        try:
            model = SentenceTransformer(model_name)
            logger.info(f"Embedding model {model_name} loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
            
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]
            
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end > len(text):
                end = len(text)
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
            
        return chunks
        
    async def add_document(self, document: Document) -> str:
        """
        Add a document to the RAG system.
        
        Args:
            document: The document to add
            
        Returns:
            The ID of the added document
        """
        # Chunk document if needed
        chunks = self._chunk_text(document.content)
        
        # Create embeddings for chunks
        try:
            embeddings = self.embedding_model.encode(chunks)
            document.embedding = np.mean(embeddings, axis=0) if len(embeddings) > 1 else embeddings[0]
        except Exception as e:
            logger.error(f"Failed to create embeddings for document {document.id}: {e}")
            raise
            
        self.documents[document.id] = document
        logger.info(f"Document added with ID: {document.id}")
        return document.id
        
    async def query(self, query: str, top_k: Optional[int] = None) -> QueryResult:
        """
        Query the RAG system.
        
        Args:
            query: The query string
            top_k: Optional number of results to return
            
        Returns:
            QueryResult containing matched documents and metadata
        """
        if not self.documents:
            logger.warning("No documents in the system")
            return QueryResult(documents=[], query=query)
            
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Calculate similarities
            similarities = []
            docs = []
            for doc in self.documents.values():
                if doc.embedding is not None:
                    similarity = cosine_similarity(
                        [query_embedding],
                        [doc.embedding]
                    )[0][0]
                    similarities.append(similarity)
                    docs.append(doc)
                    
            # Sort by similarity
            sorted_pairs = sorted(zip(similarities, docs), key=lambda x: x[0], reverse=True)
            top_k = top_k or self.top_k
            top_similarities, top_docs = zip(*sorted_pairs[:top_k])
            
            return QueryResult(
                documents=list(top_docs),
                query=query,
                similarity_scores=list(top_similarities)
            )
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
            
    async def generate_answer(self, query_result: QueryResult) -> str:
        """
        Generate an answer based on retrieved documents.
        
        Args:
            query_result: The query result containing relevant documents
            
        Returns:
            Generated answer string
        """
        try:
            # Prepare context from top documents
            context = "\n\n".join([
                f"Document {i+1}:\n{doc.content}"
                for i, doc in enumerate(query_result.documents)
            ])
            
            # TODO: Implement answer generation using LLM
            # For now, return a placeholder
            answer = f"Based on {len(query_result.documents)} relevant documents..."
            query_result.generated_answer = answer
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise
            
    async def update_document(self, document: Document) -> bool:
        """
        Update an existing document.
        
        Args:
            document: The document to update
            
        Returns:
            True if successful, False otherwise
        """
        if document.id not in self.documents:
            logger.warning(f"Document {document.id} not found")
            return False
            
        try:
            await self.add_document(document)
            return True
        except Exception as e:
            logger.error(f"Failed to update document {document.id}: {e}")
            return False
            
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        if document_id not in self.documents:
            logger.warning(f"Document {document_id} not found")
            return False
            
        try:
            del self.documents[document_id]
            logger.info(f"Document {document_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
            
    async def get_document(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            Document if found, None otherwise
        """
        return self.documents.get(document_id)
        
    async def list_documents(self) -> List[Document]:
        """
        List all documents in the system.
        
        Returns:
            List of all documents
        """
        return list(self.documents.values())
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary containing system statistics
        """
        return {
            "total_documents": len(self.documents),
            "embedding_model": self.config.get("embedding_model"),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k
        }
