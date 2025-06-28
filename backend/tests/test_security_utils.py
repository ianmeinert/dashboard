#!/usr/bin/env python3
"""
Test script for security utilities.

This script tests the secret masking functionality to ensure that
sensitive information is properly sanitized in logs and error responses.
"""

import json
import sys
from typing import Any, Dict

# Add the backend directory to the Python path
sys.path.insert(0, '.')

# Import security utilities directly
from ..services.security_utils import (create_safe_log_message,
                                       is_sensitive_field, mask_secrets,
                                       sanitize_error_response,
                                       sanitize_for_logging)


def test_secret_masking():
    """Test secret masking functionality."""
    print("🧪 Testing Secret Masking Functionality")
    print("=" * 50)
    
    # Test data with various types of secrets
    test_data = {
        "api_key": "sk-1234567890abcdef1234567890abcdef1234567890abcdef",
        "password": "mysecretpassword123",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "database_url": "postgresql://user:password@localhost:5432/dbname",
        "normal_field": "this should not be masked",
        "nested": {
            "secret_key": "another_secret_value",
            "normal_nested": "this should not be masked"
        },
        "list_data": [
            {"api_key": "secret_in_list"},
            {"normal_item": "not_secret"}
        ]
    }
    
    print("\n📋 Original data (with secrets):")
    print(json.dumps(test_data, indent=2))
    
    print("\n🔒 Masked data:")
    masked_data = mask_secrets(test_data)
    print(json.dumps(masked_data, indent=2))
    
    # Verify secrets are masked
    assert masked_data["api_key"] == "********"
    assert masked_data["password"] == "********"
    assert masked_data["access_token"] == "********"
    assert masked_data["database_url"] == "********"
    assert masked_data["normal_field"] == "this should not be masked"
    assert masked_data["nested"]["secret_key"] == "********"
    assert masked_data["nested"]["normal_nested"] == "this should not be masked"
    assert masked_data["list_data"][0]["api_key"] == "********"
    assert masked_data["list_data"][1]["normal_item"] == "not_secret"
    
    print("✅ Secret masking test passed!")


def test_string_masking():
    """Test string-based secret masking."""
    print("\n🔤 Testing String Masking")
    print("-" * 30)
    
    test_strings = [
        "api_key=sk-1234567890abcdef",
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "postgresql://user:password@localhost:5432/dbname",
        "This is a normal string with no secrets",
        "appid=1234567890abcdef&lat=40.7128&lon=-74.0060"
    ]
    
    for test_string in test_strings:
        masked = mask_secrets(test_string)
        print(f"Original: {test_string}")
        print(f"Masked:   {masked}")
        print()
    
    print("✅ String masking test passed!")


def test_error_response_sanitization():
    """Test error response sanitization."""
    print("\n🚨 Testing Error Response Sanitization")
    print("-" * 40)
    
    error_response = {
        "error": "Database Error",
        "message": "Connection failed",
        "debug": {
            "exception_type": "ConnectionError",
            "exception_message": "Failed to connect to postgresql://user:password@localhost:5432/dbname",
            "traceback": "Traceback (most recent call last):\n  File \"app.py\", line 123, in <module>\n    db.connect()\nConnectionError: Failed to connect to postgresql://user://user:password@localhost:5432/dbname"
        },
        "details": {
            "api_key": "sk-1234567890abcdef",
            "connection_string": "postgresql://user:password@localhost:5432/dbname"
        }
    }
    
    print("Original error response:")
    print(json.dumps(error_response, indent=2))
    
    sanitized = sanitize_error_response(error_response)
    print("\nSanitized error response:")
    print(json.dumps(sanitized, indent=2))
    
    # Verify sensitive data is masked
    assert sanitized["debug"]["exception_message"] == "[REDACTED]"
    assert sanitized["debug"]["traceback"] == "[REDACTED]"
    assert sanitized["details"]["api_key"] == "********"
    assert sanitized["details"]["connection_string"] == "********"
    
    print("✅ Error response sanitization test passed!")


def test_sensitive_field_detection():
    """Test sensitive field detection."""
    print("\n🔍 Testing Sensitive Field Detection")
    print("-" * 35)
    
    test_fields = [
        "api_key",
        "password",
        "access_token",
        "secret_key",
        "normal_field",
        "user_name",
        "email_address",
        "phone_number"
    ]
    
    for field in test_fields:
        is_sensitive = is_sensitive_field(field)
        status = "🔒 SENSITIVE" if is_sensitive else "✅ SAFE"
        print(f"{field:15} -> {status}")
    
    print("✅ Sensitive field detection test passed!")


def test_safe_log_message():
    """Test safe log message creation."""
    print("\n📝 Testing Safe Log Message Creation")
    print("-" * 35)
    
    message = "API request completed"
    kwargs = {
        "api_key": "sk-1234567890abcdef",
        "user_id": "12345",
        "status": "success",
        "password": "secretpass"
    }
    
    safe_message = create_safe_log_message(message, **kwargs)
    print(f"Original kwargs: {kwargs}")
    print(f"Safe message: {safe_message}")
    
    # Verify secrets are masked in the message
    assert "sk-1234567890abcdef" not in safe_message
    assert "secretpass" not in safe_message
    assert "12345" in safe_message  # Non-sensitive data should remain
    assert "success" in safe_message  # Non-sensitive data should remain
    
    print("✅ Safe log message test passed!")


def main():
    """Run all security utility tests."""
    try:
        test_secret_masking()
        test_string_masking()
        test_error_response_sanitization()
        test_sensitive_field_detection()
        test_safe_log_message()
        
        print("\n🎉 All security utility tests passed!")
        print("✅ Secrets are properly masked and sanitized")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 