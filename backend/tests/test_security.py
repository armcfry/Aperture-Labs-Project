"""Tests for security utilities (password hashing)."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.security import hash_password, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_hash_password_not_plaintext(self):
        """Test that hash_password does not return plaintext."""
        password = "mypassword"
        result = hash_password(password)
        assert result != password

    def test_hash_password_different_each_time(self):
        """Test that hash_password produces different hashes (due to salt)."""
        password = "mypassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verify_password returns True for correct password."""
        password = "mypassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verify_password returns False for incorrect password."""
        password = "mypassword"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty(self):
        """Test verify_password with empty password."""
        hashed = hash_password("realpassword")
        assert verify_password("", hashed) is False

    def test_hash_password_special_characters(self):
        """Test hash_password handles special characters."""
        password = "p@$$w0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Test hash_password handles unicode characters."""
        password = "пароль密码"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_password_long_password(self):
        """Test hash_password handles long passwords."""
        password = "a" * 1000
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
