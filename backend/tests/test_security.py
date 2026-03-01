"""Tests for security utilities (password hashing)."""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.security import hash_password, verify_password

# Test passwords - not real credentials  # noqa: S105
TEST_PW = "fake-test-pw-abc"  # noqa: S105
TEST_PW_WRONG = "fake-wrong-pw-xyz"  # noqa: S105
TEST_PW_SPECIAL = "f@k3-t3$t-pw!#$%"  # noqa: S105
TEST_PW_UNICODE = "тест密码fake"  # noqa: S105


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        result = hash_password(TEST_PW)
        assert isinstance(result, str)

    def test_hash_password_not_plaintext(self):
        """Test that hash_password does not return plaintext."""
        result = hash_password(TEST_PW)
        assert result != TEST_PW

    def test_hash_password_different_each_time(self):
        """Test that hash_password produces different hashes (due to salt)."""
        hash1 = hash_password(TEST_PW)
        hash2 = hash_password(TEST_PW)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verify_password returns True for correct password."""
        hashed = hash_password(TEST_PW)
        assert verify_password(TEST_PW, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verify_password returns False for incorrect password."""
        hashed = hash_password(TEST_PW)
        assert verify_password(TEST_PW_WRONG, hashed) is False

    def test_verify_password_empty(self):
        """Test verify_password with empty password."""
        hashed = hash_password(TEST_PW)
        assert verify_password("", hashed) is False

    def test_hash_password_special_characters(self):
        """Test hash_password handles special characters."""
        hashed = hash_password(TEST_PW_SPECIAL)
        assert verify_password(TEST_PW_SPECIAL, hashed) is True

    def test_hash_password_unicode(self):
        """Test hash_password handles unicode characters."""
        hashed = hash_password(TEST_PW_UNICODE)
        assert verify_password(TEST_PW_UNICODE, hashed) is True

    def test_hash_password_max_length(self):
        """Test hash_password handles max length passwords (72 bytes for bcrypt)."""
        max_pw = "a" * 72  # noqa: S105 - bcrypt max is 72 bytes
        hashed = hash_password(max_pw)
        assert verify_password(max_pw, hashed) is True
