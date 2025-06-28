"""
RAG System Storage Initialization
Creates all necessary directories and MongoDB collections
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionError, OperationFailure

class RAGStorageInitializer:
    """Initializes all storage structures for the RAG system."""
    
    def __init__(self, mongodb_uri: str = None):
        self.mongodb_uri = mongodb_uri or "mongodb://localhost:27017"
        self.db_name = "genxais_rag"
        self.required_collections = [
            "documents",
            "embeddings",
            "chunks",
            "metadata",
            "indexes",
            "error_logs"
        ]
        
    def init_filesystem(self) -> Dict[str, Any]:
        """Creates necessary directories for RAG storage."""
        
        try:
            # Create main directories
            directories = [
                "storage",
                "storage/documents",
                "storage/embeddings",
                "storage/backup",
                "storage/indexes",
                "storage/temp"
            ]
            
            for directory in directories:
                os.makedirs(os.path.join("rag_system", directory), exist_ok=True)
                
            # Create metadata file
            metadata = {
                "initialized": datetime.now().isoformat(),
                "version": "1.0.0",
                "directories": directories,
                "status": "active"
            }
            
            metadata_path = os.path.join("rag_system", "storage", "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            return {
                "success": True,
                "message": "Filesystem structure created",
                "directories": directories,
                "metadata_path": metadata_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "filesystem_error"
            }
            
    def init_mongodb(self) -> Dict[str, Any]:
        """Initializes MongoDB collections and indexes."""
        
        try:
            client = MongoClient(self.mongodb_uri)
            db = client[self.db_name]
            
            # Create collections with validation
            db.create_collection("documents", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["title", "content", "created_at"],
                    "properties": {
                        "title": {"bsonType": "string"},
                        "content": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                        "metadata": {"bsonType": "object"}
                    }
                }
            })
            
            db.create_collection("embeddings", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["doc_id", "embedding", "created_at"],
                    "properties": {
                        "doc_id": {"bsonType": "objectId"},
                        "embedding": {"bsonType": "array"},
                        "created_at": {"bsonType": "date"}
                    }
                }
            })
            
            db.create_collection("chunks", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["doc_id", "content", "position"],
                    "properties": {
                        "doc_id": {"bsonType": "objectId"},
                        "content": {"bsonType": "string"},
                        "position": {"bsonType": "int"},
                        "metadata": {"bsonType": "object"}
                    }
                }
            })
            
            # Create indexes
            db.documents.create_index("title")
            db.documents.create_index("created_at")
            db.embeddings.create_index("doc_id")
            db.chunks.create_index([("doc_id", 1), ("position", 1)])
            
            # Create metadata collection
            db.metadata.insert_one({
                "initialized": datetime.now(),
                "version": "1.0.0",
                "collections": self.required_collections,
                "status": "active"
            })
            
            return {
                "success": True,
                "message": "MongoDB collections and indexes created",
                "collections": self.required_collections,
                "database": self.db_name
            }
            
        except ConnectionError:
            return {
                "success": False,
                "error": "Could not connect to MongoDB",
                "type": "connection_error"
            }
        except OperationFailure as e:
            return {
                "success": False,
                "error": str(e),
                "type": "operation_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "unknown_error"
            }
            
    def init_error_handling(self) -> Dict[str, Any]:
        """Initializes error handling structures."""
        
        try:
            # Create error log directory
            os.makedirs(os.path.join("rag_system", "storage", "error_logs"), exist_ok=True)
            
            # Initialize error log file
            log_file = os.path.join("rag_system", "storage", "error_logs", "rag_errors.log")
            with open(log_file, 'w') as f:
                f.write(f"# RAG System Error Log\nInitialized: {datetime.now().isoformat()}\n")
                
            return {
                "success": True,
                "message": "Error handling initialized",
                "log_file": log_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "error_handling_init_failed"
            }
            
    def initialize_all(self) -> Dict[str, Any]:
        """Initializes all RAG storage components."""
        
        results = {
            "filesystem": self.init_filesystem(),
            "mongodb": self.init_mongodb(),
            "error_handling": self.init_error_handling()
        }
        
        all_successful = all(r["success"] for r in results.values())
        
        if all_successful:
            print("✅ RAG storage initialization complete!")
        else:
            print("⚠️ Some initialization steps failed!")
            
        return {
            "success": all_successful,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Get MongoDB URI from environment or use default
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Initialize storage
    initializer = RAGStorageInitializer(mongodb_uri)
    result = initializer.initialize_all()
    
    # Print results
    print(json.dumps(result, indent=2)) 