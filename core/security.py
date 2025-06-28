"""
GENXAIS Framework - Security Component
Implements security measures according to BSI and TÜV requirements
"""

import os
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
from cryptography.x509.oid import NameOID
from dataclasses import dataclass
import jwt
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger("GENXAIS.Security")

@dataclass
class SecurityConfig:
    """Security configuration settings according to BSI requirements"""
    key_rotation_days: int = 30
    password_min_length: int = 12
    max_login_attempts: int = 3
    session_timeout_minutes: int = 60
    mfa_required: bool = True
    audit_retention_days: int = 365
    tls_min_version: str = "1.3"
    hash_algorithm: str = "SHA-512"
    encryption_algorithm: str = "AES-256-GCM"
    cert_validation_interval: int = 24  # Hours
    key_backup_interval: int = 7  # Days
    audit_log_encryption: bool = True
    cert_revocation_check: bool = True

class SecurityManager:
    """Central security management component"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security manager"""
        self.config = SecurityConfig(**(config or {}))
        self.fernet = self._init_encryption()
        self.audit_log = self._init_audit_logging()
        self._failed_attempts = {}
        self._session_tokens = {}
        
    def _init_encryption(self) -> Fernet:
        """Initialize encryption"""
        try:
            key = Fernet.generate_key()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Encryption initialization failed: {e}")
            raise
            
    def _init_audit_logging(self) -> logging.Logger:
        """Initialize audit logging"""
        audit_logger = logging.getLogger("GENXAIS.Security.Audit")
        handler = logging.FileHandler("logs/security_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        audit_logger.addHandler(handler)
        audit_logger.setLevel(logging.INFO)
        return audit_logger
        
    def generate_key_pair(self) -> tuple:
        """Generate RSA key pair"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )
            public_key = private_key.public_key()
            return private_key, public_key
        except Exception as e:
            logger.error(f"Key pair generation failed: {e}")
            raise
            
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM"""
        try:
            key = AESGCM.generate_key(bit_length=256)
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)
            return aesgcm.encrypt(nonce, data, None)
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            raise
            
    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        try:
            aesgcm = AESGCM(key)
            nonce = encrypted_data[:12]
            return aesgcm.decrypt(nonce, encrypted_data[12:], None)
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            raise
            
    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2 with SHA-512"""
        try:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=32,
                salt=salt,
                iterations=100000
            )
            key = kdf.derive(password.encode())
            return f"{salt.hex()}:{key.hex()}"
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
            
    def verify_password(self, password: str, hash_str: str) -> bool:
        """Verify password against hash"""
        try:
            salt_hex, key_hex = hash_str.split(":")
            salt = bytes.fromhex(salt_hex)
            key = bytes.fromhex(key_hex)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA512(),
                length=32,
                salt=salt,
                iterations=100000
            )
            
            kdf.verify(password.encode(), key)
            return True
        except Exception:
            return False
            
    def generate_token(self, user_id: str, roles: List[str]) -> str:
        """Generate JWT token"""
        try:
            payload = {
                "sub": user_id,
                "roles": roles,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow().timestamp() + (
                    self.config.session_timeout_minutes * 60
                )
            }
            return jwt.encode(
                payload,
                self.fernet.encryption_key,
                algorithm="HS256"
            )
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise
            
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            return jwt.decode(
                token,
                self.fernet.encryption_key,
                algorithms=["HS256"]
            )
        except InvalidTokenError as e:
            logger.warning(f"Token validation failed: {e}")
            return {}
            
    def check_password_strength(self, password: str) -> bool:
        """Check password strength"""
        if len(password) < self.config.password_min_length:
            return False
            
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])
        
    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "INFO"
    ) -> None:
        """Log security event"""
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "details": details
            }
            self.audit_log.log(
                getattr(logging, severity),
                f"Security Event: {event}"
            )
        except Exception as e:
            logger.error(f"Event logging failed: {e}")
            
    def validate_input(self, input_data: Any, input_type: str) -> bool:
        """Validate input data"""
        try:
            if input_type == "user_id":
                return isinstance(input_data, str) and len(input_data) <= 64
            elif input_type == "password":
                return self.check_password_strength(input_data)
            elif input_type == "token":
                return bool(self.validate_token(input_data))
            elif input_type == "role":
                return isinstance(input_data, str) and input_data in [
                    "admin", "user", "readonly"
                ]
            return False
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return False
            
    def handle_failed_login(self, user_id: str) -> bool:
        """Handle failed login attempt"""
        try:
            if user_id not in self._failed_attempts:
                self._failed_attempts[user_id] = {
                    "count": 0,
                    "last_attempt": datetime.utcnow()
                }
                
            self._failed_attempts[user_id]["count"] += 1
            self._failed_attempts[user_id]["last_attempt"] = datetime.utcnow()
            
            if self._failed_attempts[user_id]["count"] >= self.config.max_login_attempts:
                self.log_security_event(
                    "account_locked",
                    {"user_id": user_id},
                    "WARNING"
                )
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed login handling failed: {e}")
            return False
            
    def reset_failed_attempts(self, user_id: str) -> None:
        """Reset failed login attempts"""
        try:
            if user_id in self._failed_attempts:
                del self._failed_attempts[user_id]
        except Exception as e:
            logger.error(f"Failed attempts reset failed: {e}")
            
    def validate_session(self, token: str) -> bool:
        """Validate session token"""
        try:
            if token not in self._session_tokens:
                return False
                
            session = self._session_tokens[token]
            if (datetime.utcnow() - session["created"]).total_seconds() > (
                self.config.session_timeout_minutes * 60
            ):
                del self._session_tokens[token]
                return False
                
            return True
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return False
            
    def create_session(self, user_id: str, roles: List[str]) -> str:
        """Create new session"""
        try:
            token = secrets.token_urlsafe(32)
            self._session_tokens[token] = {
                "user_id": user_id,
                "roles": roles,
                "created": datetime.utcnow()
            }
            return token
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            raise
            
    def end_session(self, token: str) -> bool:
        """End session"""
        try:
            if token in self._session_tokens:
                del self._session_tokens[token]
                return True
            return False
        except Exception as e:
            logger.error(f"Session end failed: {e}")
            return False
            
    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        try:
            current_time = datetime.utcnow()
            expired_tokens = [
                token for token, session in self._session_tokens.items()
                if (current_time - session["created"]).total_seconds() > (
                    self.config.session_timeout_minutes * 60
                )
            ]
            
            for token in expired_tokens:
                del self._session_tokens[token]
                
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
            
    def rotate_encryption_keys(self) -> None:
        """Rotate encryption keys"""
        try:
            new_key = Fernet.generate_key()
            old_key = self.fernet.encryption_key
            self.fernet = Fernet(new_key)
            
            # Re-encrypt sensitive data with new key
            # Implementation depends on specific data storage
            
            self.log_security_event(
                "key_rotation",
                {"status": "success"},
                "INFO"
            )
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise

    def validate_certificate(self, cert_data: bytes, is_pem: bool = True) -> bool:
        """Validate X.509 certificate according to BSI TR-03145"""
        try:
            # Load certificate
            cert = (load_pem_x509_certificate(cert_data) if is_pem 
                   else load_der_x509_certificate(cert_data))
            
            # Check certificate validity period
            now = datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                logger.warning("Certificate validity period check failed")
                return False
            
            # Check key usage
            try:
                key_usage = cert.extensions.get_extension_for_oid(
                    NameOID.KEY_USAGE
                ).value
                if not key_usage.digital_signature:
                    logger.warning("Certificate key usage check failed")
                    return False
            except Exception:
                logger.warning("Certificate missing required key usage extension")
                return False
            
            # Check algorithm compliance
            if cert.signature_algorithm_oid not in self.get_compliant_algorithms():
                logger.warning("Certificate uses non-compliant algorithm")
                return False
            
            # Additional BSI-specific checks
            if not self.check_bsi_requirements(cert):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return False
        
    def check_bsi_requirements(self, cert) -> bool:
        """Additional BSI-specific certificate checks"""
        try:
            # Check for German Trust List if required
            if self.config.cert_revocation_check:
                if not self.check_revocation_status(cert):
                    return False
            
            # Check key length
            public_key = cert.public_key()
            if isinstance(public_key, rsa.RSAPublicKey):
                if public_key.key_size < 3072:  # BSI minimum requirement
                    return False
            
            return True
        except Exception as e:
            logger.error(f"BSI requirement check failed: {e}")
            return False
        
    def get_compliant_algorithms(self) -> List[str]:
        """Get BSI-compliant algorithms"""
        return [
            "sha256WithRSAEncryption",
            "sha384WithRSAEncryption",
            "sha512WithRSAEncryption",
            "ecdsa-with-SHA256",
            "ecdsa-with-SHA384",
            "ecdsa-with-SHA512"
        ]
    
    def backup_crypto_keys(self) -> None:
        """Backup cryptographic keys according to BSI requirements"""
        try:
            backup_dir = "secure_backup/keys"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup encryption keys
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"keys_backup_{timestamp}.enc")
            
            # Encrypt backup
            backup_key = AESGCM.generate_key(bit_length=256)
            aesgcm = AESGCM(backup_key)
            nonce = os.urandom(12)
            
            # Create encrypted backup
            with open(backup_path, "wb") as f:
                f.write(nonce)
                f.write(aesgcm.encrypt(
                    nonce,
                    self.fernet.encryption_key,
                    None
                ))
            
            # Log backup event
            self.log_security_event(
                "key_backup",
                {"timestamp": timestamp, "location": backup_path},
                "INFO"
            )
        except Exception as e:
            logger.error(f"Key backup failed: {e}")
            raise
        
    def enhanced_audit_logging(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "INFO",
        source_ip: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Enhanced audit logging according to BSI requirements"""
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "details": details,
                "source_ip": source_ip,
                "user_id": user_id,
                "system_info": self.get_system_info()
            }
            
            # Encrypt audit log if required
            if self.config.audit_log_encryption:
                event = self.encrypt_data(str(event).encode())
            
            self.audit_log.log(
                getattr(logging, severity),
                f"Security Event: {event}"
            )
            
            # Additional BSI required logging
            if severity in ["WARNING", "ERROR", "CRITICAL"]:
                self.notify_security_team(event)
        except Exception as e:
            logger.error(f"Enhanced audit logging failed: {e}")
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for audit logging"""
        return {
            "hostname": os.uname().nodename,
            "timestamp": datetime.utcnow().isoformat(),
            "process_id": os.getpid()
        }
        
    def notify_security_team(self, event: Dict[str, Any]) -> None:
        """Notify security team about critical events"""
        # Implementation depends on organization's notification system
        pass 