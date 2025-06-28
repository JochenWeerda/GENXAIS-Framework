"""
GENXAIS Framework - Handover System Implementation
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path
import pymongo
from pymongo import MongoClient
from cryptography.fernet import Fernet
from dataclasses import dataclass

from error_handling.framework import SDKErrorHandler

@dataclass
class HandoverError(Exception):
    """Custom error for handover operations"""
    message: str
    error_type: str
    context: Dict[str, Any]

class HandoverSystem:
    """Implements the handover system for seamless mode transitions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.logger = self._setup_logging()
        self.db = self._init_mongodb()
        self.crypto = self._init_encryption()
        self.error_handler = SDKErrorHandler()  # Verwende das zentrale Error-Handling
        self.success_handlers: List[Callable] = []
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        try:
            config_path = Path("config/default_config.json")
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            return {
                "mongodb_uri": "mongodb://localhost:27017/",
                "database": "genxais_handover",
                "encryption_key": Fernet.generate_key().decode(),
                "log_file": "logs/handover.log",
                "retention_days": 30
            }
            
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for handover operations"""
        logger = logging.getLogger("HandoverSystem")
        handler = logging.FileHandler(self.config.get("log_file", "logs/handover.log"))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
        
    def _init_mongodb(self) -> pymongo.database.Database:
        """Initialize MongoDB connection"""
        try:
            client = MongoClient(self.config["mongodb_uri"])
            db = client[self.config["database"]]
            # Ensure indexes
            db.handovers.create_index([("timestamp", pymongo.DESCENDING)])
            db.handovers.create_index([("source", pymongo.ASCENDING)])
            db.handovers.create_index([("target", pymongo.ASCENDING)])
            return db
        except Exception as e:
            self.logger.error(f"MongoDB initialization failed: {e}")
            return self.error_handler.handle_error(
                "db_init_error",
                {"error": str(e)},
                "MongoDB initialization failed"
            )
            
    def _init_encryption(self) -> Fernet:
        """Initialize encryption"""
        try:
            key = self.config["encryption_key"].encode()
            return Fernet(key)
        except Exception as e:
            self.logger.error(f"Encryption initialization failed: {e}")
            return self.error_handler.handle_error(
                "crypto_init_error",
                {"error": str(e)},
                "Encryption initialization failed"
            )
            
    def on_success(self, handler: Callable):
        """Register success handler"""
        self.success_handlers.append(handler)
        return handler
        
    def _notify_success(self, context: Dict[str, Any]):
        """Notify all success handlers"""
        for handler in self.success_handlers:
            try:
                handler(context)
            except Exception as e:
                self.logger.error(f"Success handler failed: {e}")
                self.error_handler.handle_error(
                    "handler_error",
                    {"error": str(e)},
                    "Success handler failed"
                )
                
    def save_context(self, context: Dict[str, Any]) -> bool:
        """Save current context"""
        try:
            # Encrypt sensitive data
            encrypted_data = self.crypto.encrypt(
                json.dumps(context).encode()
            ).decode()
            
            # Prepare document
            doc = {
                "timestamp": datetime.utcnow(),
                "data": encrypted_data,
                "source": context.get("mode"),
                "target": context.get("target_mode"),
                "metadata": {
                    "session_id": context.get("session_id"),
                    "user_id": context.get("user_id"),
                    "artifacts": context.get("artifacts", [])
                }
            }
            
            # Save to MongoDB
            result = self.db.handovers.insert_one(doc)
            
            if result.inserted_id:
                self.logger.info(f"Context saved successfully: {result.inserted_id}")
                self._notify_success(context)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")
            self.error_handler.handle_error(
                "save_error",
                {"error": str(e)},
                "Failed to save context"
            )
            return False
            
    def load_context(self) -> Dict[str, Any]:
        """Load saved context"""
        try:
            # Get latest handover
            doc = self.db.handovers.find_one(
                sort=[("timestamp", pymongo.DESCENDING)]
            )
            
            if not doc:
                return {}
                
            # Decrypt data
            decrypted_data = self.crypto.decrypt(
                doc["data"].encode()
            ).decode()
            
            context = json.loads(decrypted_data)
            self.logger.info("Context loaded successfully")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to load context: {e}")
            self.error_handler.handle_error(
                "load_error",
                {"error": str(e)},
                "Failed to load context"
            )
            return {}
            
    def validate_handover(self, source: str, target: str) -> bool:
        """Validate mode transition"""
        valid_transitions = {
            "VAN": ["PLAN"],
            "PLAN": ["CREATE"],
            "CREATE": ["IMPLEMENT"],
            "IMPLEMENT": ["REFLECT"],
            "REFLECT": ["ARCHIVE", "VAN"]
        }
        
        if source not in valid_transitions:
            self.logger.error(f"Invalid source mode: {source}")
            return False
            
        if target not in valid_transitions[source]:
            self.logger.error(f"Invalid transition: {source} -> {target}")
            return False
            
        return True
        
    def cleanup_old_handovers(self, days: int = None) -> None:
        """Clean up old handover data"""
        try:
            retention_days = days or self.config.get("retention_days", 30)
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            result = self.db.handovers.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            self.logger.info(f"Cleaned up {result.deleted_count} old handovers")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            self.error_handler.handle_error(
                "cleanup_error",
                {"error": str(e)},
                "Failed to clean up old handovers"
            )
            
    def persist_to_filesystem(
        self,
        data: Dict[str, Any],
        path: str = "memory-bank/handover"
    ) -> bool:
        """Persist handover data to filesystem"""
        try:
            # Create directory if not exists
            os.makedirs(path, exist_ok=True)
            
            # Create timestamped filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"handover_{timestamp}.json"
            filepath = os.path.join(path, filename)
            
            # Encrypt and save data
            encrypted_data = self.crypto.encrypt(
                json.dumps(data).encode()
            ).decode()
            
            with open(filepath, "w") as f:
                json.dump({"data": encrypted_data}, f)
                
            self.logger.info(f"Data persisted to filesystem: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Filesystem persistence failed: {e}")
            self.error_handler.handle_error(
                "fs_error",
                {"error": str(e)},
                "Failed to persist to filesystem"
            )
            return False
            
    def persist_to_mongodb(self, data: Dict[str, Any]) -> bool:
        """Persist handover data to MongoDB"""
        try:
            # Encrypt data
            encrypted_data = self.crypto.encrypt(
                json.dumps(data).encode()
            ).decode()
            
            # Prepare document
            doc = {
                "timestamp": datetime.utcnow(),
                "data": encrypted_data,
                "metadata": {
                    "session_id": data.get("session_id"),
                    "type": "persistence"
                }
            }
            
            # Save to MongoDB
            result = self.db.persistent_data.insert_one(doc)
            
            if result.inserted_id:
                self.logger.info(f"Data persisted to MongoDB: {result.inserted_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"MongoDB persistence failed: {e}")
            self.error_handler.handle_error(
                "db_error",
                {"error": str(e)},
                "Failed to persist to MongoDB"
            )
            return False
            
    def recover_last_successful(self) -> Optional[Dict[str, Any]]:
        """Recover last successful handover"""
        try:
            # Get last successful handover
            doc = self.db.handovers.find_one(
                {"metadata.status": "success"},
                sort=[("timestamp", pymongo.DESCENDING)]
            )
            
            if not doc:
                self.logger.warning("No successful handover found")
                return None
                
            # Decrypt data
            decrypted_data = self.crypto.decrypt(
                doc["data"].encode()
            ).decode()
            
            context = json.loads(decrypted_data)
            self.logger.info("Successfully recovered last handover")
            return context
            
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            self.error_handler.handle_error(
                "recovery_error",
                {"error": str(e)},
                "Failed to recover last handover"
            )
            return None
            
    def notify_target_mode(self) -> None:
        """Notify target mode about pending handover"""
        try:
            context = self.load_context()
            target_mode = context.get("target_mode")
            
            if not target_mode:
                self.logger.warning("No target mode specified in context")
                return
                
            # Implementation specific notification logic here
            self.logger.info(f"Notified target mode: {target_mode}")
            
        except Exception as e:
            self.logger.error(f"Target mode notification failed: {e}")
            self.error_handler.handle_error(
                "notification_error",
                {"error": str(e)},
                "Failed to notify target mode"
            ) 