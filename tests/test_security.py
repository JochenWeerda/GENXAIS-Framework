"""
Security tests for the GENXAIS Framework
"""

import pytest
import os
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from core.security import SecurityManager, SecurityConfig

@pytest.fixture
def security_manager():
    """Create security manager instance for testing"""
    config = {
        "key_rotation_days": 1,
        "password_min_length": 8,
        "max_login_attempts": 3,
        "session_timeout_minutes": 30,
        "mfa_required": True
    }
    return SecurityManager(config)

class TestSecurityBasics:
    """Test basic security functionality"""
    
    def test_initialization(self, security_manager):
        """Test security manager initialization"""
        assert security_manager is not None
        assert isinstance(security_manager.config, SecurityConfig)
        assert security_manager.fernet is not None
        
    def test_encryption_key_generation(self, security_manager):
        """Test encryption key generation"""
        key = Fernet.generate_key()
        assert len(key) == 32  # 256 bits
        
    def test_rsa_key_pair_generation(self, security_manager):
        """Test RSA key pair generation"""
        private_key, public_key = security_manager.generate_key_pair()
        assert isinstance(private_key, rsa.RSAPrivateKey)
        assert isinstance(public_key, rsa.RSAPublicKey)
        
class TestPasswordSecurity:
    """Test password security features"""
    
    def test_password_hashing(self, security_manager):
        """Test password hashing"""
        password = "SecurePass123!"
        hash_str = security_manager.hash_password(password)
        assert ":" in hash_str
        salt_hex, key_hex = hash_str.split(":")
        assert len(bytes.fromhex(salt_hex)) == 16
        assert len(bytes.fromhex(key_hex)) == 32
        
    def test_password_verification(self, security_manager):
        """Test password verification"""
        password = "SecurePass123!"
        hash_str = security_manager.hash_password(password)
        assert security_manager.verify_password(password, hash_str)
        assert not security_manager.verify_password("WrongPass123!", hash_str)
        
    def test_password_strength(self, security_manager):
        """Test password strength requirements"""
        assert security_manager.check_password_strength("SecurePass123!")
        assert not security_manager.check_password_strength("weak")
        assert not security_manager.check_password_strength("NoSpecialChars123")
        assert not security_manager.check_password_strength("no-numbers-here!")
        
class TestTokenManagement:
    """Test token management"""
    
    def test_token_generation(self, security_manager):
        """Test JWT token generation"""
        token = security_manager.generate_token("user123", ["admin"])
        assert token is not None
        payload = security_manager.validate_token(token)
        assert payload["sub"] == "user123"
        assert "admin" in payload["roles"]
        
    def test_token_expiration(self, security_manager):
        """Test token expiration"""
        token = security_manager.generate_token("user123", ["admin"])
        # Fast forward time
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(hours=2)
            payload = security_manager.validate_token(token)
            assert not payload  # Token should be expired
            
    def test_invalid_token(self, security_manager):
        """Test invalid token handling"""
        assert not security_manager.validate_token("invalid.token.here")
        
class TestSessionManagement:
    """Test session management"""
    
    def test_session_creation(self, security_manager):
        """Test session creation"""
        token = security_manager.create_session("user123", ["admin"])
        assert token is not None
        assert security_manager.validate_session(token)
        
    def test_session_expiration(self, security_manager):
        """Test session expiration"""
        token = security_manager.create_session("user123", ["admin"])
        # Fast forward time
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(hours=1)
            assert not security_manager.validate_session(token)
            
    def test_session_cleanup(self, security_manager):
        """Test session cleanup"""
        token = security_manager.create_session("user123", ["admin"])
        # Fast forward time
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(hours=1)
            security_manager.cleanup_expired_sessions()
            assert not security_manager.validate_session(token)
            
class TestLoginSecurity:
    """Test login security features"""
    
    def test_failed_login_handling(self, security_manager):
        """Test failed login attempts handling"""
        assert security_manager.handle_failed_login("user123")  # First attempt
        assert security_manager.handle_failed_login("user123")  # Second attempt
        assert security_manager.handle_failed_login("user123")  # Third attempt
        assert not security_manager.handle_failed_login("user123")  # Should be locked
        
    def test_failed_attempts_reset(self, security_manager):
        """Test resetting failed login attempts"""
        security_manager.handle_failed_login("user123")
        security_manager.reset_failed_attempts("user123")
        assert security_manager.handle_failed_login("user123")  # Should work again
        
class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_security_event_logging(self, security_manager):
        """Test security event logging"""
        security_manager.log_security_event(
            "test_event",
            {"test": True},
            "INFO"
        )
        assert os.path.exists("logs/security_audit.log")
        
    def test_severe_event_logging(self, security_manager):
        """Test severe security event logging"""
        security_manager.log_security_event(
            "severe_test",
            {"critical": True},
            "CRITICAL"
        )
        # Check log file content
        with open("logs/security_audit.log", "r") as f:
            log_content = f.read()
            assert "CRITICAL" in log_content
            assert "severe_test" in log_content
            
class TestInputValidation:
    """Test input validation"""
    
    def test_user_id_validation(self, security_manager):
        """Test user ID validation"""
        assert security_manager.validate_input("valid_user", "user_id")
        assert not security_manager.validate_input("x" * 65, "user_id")
        
    def test_role_validation(self, security_manager):
        """Test role validation"""
        assert security_manager.validate_input("admin", "role")
        assert security_manager.validate_input("user", "role")
        assert not security_manager.validate_input("invalid_role", "role")
        
class TestKeyRotation:
    """Test key rotation functionality"""
    
    def test_key_rotation(self, security_manager):
        """Test encryption key rotation"""
        old_key = security_manager.fernet.encryption_key
        security_manager.rotate_encryption_keys()
        assert security_manager.fernet.encryption_key != old_key
        
    def test_key_rotation_logging(self, security_manager):
        """Test key rotation logging"""
        security_manager.rotate_encryption_keys()
        with open("logs/security_audit.log", "r") as f:
            log_content = f.read()
            assert "key_rotation" in log_content
            
@pytest.mark.integration
class TestSecurityIntegration:
    """Test security integration scenarios"""
    
    def test_full_login_flow(self, security_manager):
        """Test complete login flow"""
        # 1. Create user with hashed password
        password = "SecurePass123!"
        hash_str = security_manager.hash_password(password)
        
        # 2. Verify password
        assert security_manager.verify_password(password, hash_str)
        
        # 3. Generate session token
        token = security_manager.create_session("test_user", ["user"])
        
        # 4. Validate session
        assert security_manager.validate_session(token)
        
        # 5. End session
        assert security_manager.end_session(token)
        
    def test_security_breach_scenario(self, security_manager):
        """Test security breach handling"""
        # 1. Multiple failed login attempts
        for _ in range(3):
            security_manager.handle_failed_login("target_user")
            
        # 2. Verify account lockout
        assert not security_manager.handle_failed_login("target_user")
        
        # 3. Check audit log
        with open("logs/security_audit.log", "r") as f:
            log_content = f.read()
            assert "account_locked" in log_content
            assert "target_user" in log_content 