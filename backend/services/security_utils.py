"""
Security Utilities

Provides utilities for secure handling of sensitive data, including
secret masking for logging and error responses.
"""

import re
from typing import Any, Dict, List, Optional, Union


class SecretMasker:
    """Utility class for masking sensitive information in logs and error messages."""
    
    # Common secret patterns to mask
    SECRET_PATTERNS = [
        # API keys (various formats)
        r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        r'appid["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        r'access[_-]?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9._-]{20,})["\']?',
        r'bearer\s+([a-zA-Z0-9._-]{20,})',
        
        # JWT tokens
        r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
        
        # OAuth tokens
        r'oauth[_-]?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        
        # Database connection strings
        r'(?:postgresql|mysql|sqlite)://[^@]*@[^\s]+',
        r'(?:mongodb|redis)://[^@]*@[^\s]+',
        
        # Private keys
        r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
        
        # Passwords in URLs
        r'://[^:]*:([^@]*)@',
        
        # Credit card numbers (basic pattern)
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        
        # Social security numbers (US)
        r'\b\d{3}-\d{2}-\d{4}\b',
        
        # Phone numbers (basic pattern)
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
    ]
    
    # Fields that should always be masked
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api_key',
        'access_token', 'refresh_token', 'authorization', 'auth',
        'credential', 'private_key', 'secret_key', 'session_id',
        'ssn', 'credit_card', 'card_number', 'phone', 'email'
    }
    
    def __init__(self):
        """Initialize the secret masker with compiled patterns."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SECRET_PATTERNS]
    
    def mask_string(self, text: str, mask_char: str = '*') -> str:
        """
        Mask sensitive information in a string.
        
        Args:
            text: The text to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked text
        """
        if not text:
            return text
        
        masked_text = text
        
        # Apply pattern-based masking
        for pattern in self.compiled_patterns:
            if pattern.groups == 1:
                # Pattern with capture group
                masked_text = pattern.sub(f'{mask_char * 8}', masked_text)
            else:
                # Pattern without capture group
                masked_text = pattern.sub(f'{mask_char * 8}', masked_text)
        
        return masked_text
    
    def mask_dict(self, data: Dict[str, Any], mask_char: str = '*') -> Dict[str, Any]:
        """
        Recursively mask sensitive information in a dictionary.
        
        Args:
            data: Dictionary to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked dictionary
        """
        if not isinstance(data, dict):
            return data
        
        masked_data = {}
        
        for key, value in data.items():
            # Check if key indicates sensitive data
            key_lower = key.lower()
            is_sensitive = any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS)
            
            if is_sensitive:
                if isinstance(value, str):
                    masked_data[key] = f'{mask_char * 8}'
                elif isinstance(value, (dict, list)):
                    masked_data[key] = f'{mask_char * 8}'
                else:
                    masked_data[key] = f'{mask_char * 8}'
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value, mask_char)
            elif isinstance(value, list):
                masked_data[key] = self.mask_list(value, mask_char)
            elif isinstance(value, str):
                masked_data[key] = self.mask_string(value, mask_char)
            else:
                masked_data[key] = value
        
        return masked_data
    
    def mask_list(self, data: List[Any], mask_char: str = '*') -> List[Any]:
        """
        Recursively mask sensitive information in a list.
        
        Args:
            data: List to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked list
        """
        if not isinstance(data, list):
            return data
        
        return [self.mask_data(item, mask_char) for item in data]
    
    def mask_data(self, data: Any, mask_char: str = '*') -> Any:
        """
        Mask sensitive information in any data type.
        
        Args:
            data: Data to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked data
        """
        if isinstance(data, dict):
            return self.mask_dict(data, mask_char)
        elif isinstance(data, list):
            return self.mask_list(data, mask_char)
        elif isinstance(data, str):
            return self.mask_string(data, mask_char)
        else:
            return data


# Global secret masker instance
secret_masker = SecretMasker()


def mask_secrets(data: Any, mask_char: str = '*') -> Any:
    """
    Convenience function to mask secrets in any data type.
    
    Args:
        data: Data to mask
        mask_char: Character to use for masking
        
    Returns:
        Masked data
    """
    return secret_masker.mask_data(data, mask_char)


def sanitize_for_logging(data: Any) -> Any:
    """
    Sanitize data for safe logging by masking secrets.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data safe for logging
    """
    return mask_secrets(data)


def sanitize_error_response(error_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize error response data to remove any sensitive information.
    
    Args:
        error_data: Error response data to sanitize
        
    Returns:
        Sanitized error response
    """
    # Create a copy to avoid modifying the original
    sanitized = error_data.copy()
    
    # Remove potentially sensitive fields from debug information
    if 'debug' in sanitized:
        debug_info = sanitized['debug'].copy()
        # Remove sensitive fields from debug info
        sensitive_debug_fields = {'exception_message', 'traceback', 'stack_trace'}
        for field in sensitive_debug_fields:
            if field in debug_info:
                debug_info[field] = '[REDACTED]'
        sanitized['debug'] = debug_info
    
    # Mask any remaining sensitive data
    return mask_secrets(sanitized)


def is_sensitive_field(field_name: str) -> bool:
    """
    Check if a field name indicates sensitive data.
    
    Args:
        field_name: Name of the field to check
        
    Returns:
        True if the field is sensitive
    """
    field_lower = field_name.lower()
    return any(sensitive in field_lower for sensitive in secret_masker.SENSITIVE_FIELDS)


def create_safe_log_message(message: str, **kwargs) -> str:
    """
    Create a safe log message by masking any sensitive data in kwargs.
    
    Args:
        message: Base log message
        **kwargs: Additional data to include in the message
        
    Returns:
        Safe log message with masked sensitive data
    """
    if not kwargs:
        return message
    
    # Mask sensitive data in kwargs
    safe_kwargs = mask_secrets(kwargs)
    
    # Format the message with safe data
    try:
        return f"{message} | {safe_kwargs}"
    except Exception:
        # Fallback if formatting fails
        return f"{message} | [DATA_MASKED]" 