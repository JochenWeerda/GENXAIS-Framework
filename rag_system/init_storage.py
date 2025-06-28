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

    def create_backup(self) -> Dict[str, Any]:
        """Creates a backup of all RAG system data"""
        try:
            # 1. Create backup timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join("rag_system", "storage", "backup", f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)

            # 2. Backup filesystem data
            for dir_name in ["documents", "embeddings", "indexes"]:
                src_dir = os.path.join("rag_system", "storage", dir_name)
                dst_dir = os.path.join(backup_dir, dir_name)
                if os.path.exists(src_dir):
                    os.makedirs(dst_dir, exist_ok=True)
                    for file in os.listdir(src_dir):
                        src_file = os.path.join(src_dir, file)
                        dst_file = os.path.join(dst_dir, file)
                        if os.path.isfile(src_file):
                            with open(src_file, 'rb') as sf, open(dst_file, 'wb') as df:
                                df.write(sf.read())

            # 3. Backup MongoDB collections
            if self.mongodb_uri:
                client = MongoClient(self.mongodb_uri)
                db = client[self.db_name]
                
                for collection in self.required_collections:
                    backup_file = os.path.join(backup_dir, f"{collection}.json")
                    with open(backup_file, 'w') as f:
                        documents = list(db[collection].find({}))
                        # Convert ObjectId to string for JSON serialization
                        for doc in documents:
                            doc['_id'] = str(doc['_id'])
                            if 'doc_id' in doc:
                                doc['doc_id'] = str(doc['doc_id'])
                        json.dump(documents, f, indent=2, default=str)

            # 4. Create backup metadata
            metadata = {
                "backup_time": timestamp,
                "collections_backed_up": self.required_collections,
                "filesystem_backed_up": True,
                "backup_location": backup_dir
            }
            
            with open(os.path.join(backup_dir, "backup_metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)

            return {
                "success": True,
                "message": "Backup created successfully",
                "backup_dir": backup_dir,
                "timestamp": timestamp
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "backup_failed"
            }

    def restore_backup(self, backup_dir: str) -> Dict[str, Any]:
        """Restores RAG system from a backup"""
        try:
            if not os.path.exists(backup_dir):
                return {
                    "success": False,
                    "error": f"Backup directory not found: {backup_dir}",
                    "type": "backup_not_found"
                }

            # 1. Verify backup metadata
            metadata_file = os.path.join(backup_dir, "backup_metadata.json")
            if not os.path.exists(metadata_file):
                return {
                    "success": False,
                    "error": "Backup metadata not found",
                    "type": "invalid_backup"
                }

            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # 2. Restore filesystem data
            for dir_name in ["documents", "embeddings", "indexes"]:
                src_dir = os.path.join(backup_dir, dir_name)
                dst_dir = os.path.join("rag_system", "storage", dir_name)
                if os.path.exists(src_dir):
                    os.makedirs(dst_dir, exist_ok=True)
                    for file in os.listdir(src_dir):
                        src_file = os.path.join(src_dir, file)
                        dst_file = os.path.join(dst_dir, file)
                        if os.path.isfile(src_file):
                            with open(src_file, 'rb') as sf, open(dst_file, 'wb') as df:
                                df.write(sf.read())

            # 3. Restore MongoDB collections
            if self.mongodb_uri:
                client = MongoClient(self.mongodb_uri)
                db = client[self.db_name]
                
                for collection in self.required_collections:
                    backup_file = os.path.join(backup_dir, f"{collection}.json")
                    if os.path.exists(backup_file):
                        with open(backup_file, 'r') as f:
                            documents = json.load(f)
                            if documents:
                                # Clear existing collection
                                db[collection].delete_many({})
                                # Insert backup data
                                db[collection].insert_many(documents)

            return {
                "success": True,
                "message": "Backup restored successfully",
                "restored_from": backup_dir,
                "metadata": metadata
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "restore_failed"
            }

if __name__ == "__main__":
    # Get MongoDB URI from environment or use default
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    # Initialize storage
    initializer = RAGStorageInitializer(mongodb_uri)
    result = initializer.initialize_all()
    
    # Print results
    print(json.dumps(result, indent=2)) 