"""
Error Sanitization Utility

Removes sensitive information from error messages before logging.
Prevents database URLs, API keys, and other secrets from appearing in logs.
"""
import re


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error message to remove sensitive information.

    Args:
        error: The exception to sanitize

    Returns:
        Sanitized error message safe for logging
    """
    error_str = str(error)

    # Remove database connection strings
    # Matches: postgresql://user:password@host:port/db
    error_str = re.sub(
        r'postgresql://[^:]+:[^@]+@[^/]+/\w+',
        'postgresql://[REDACTED]',
        error_str
    )

    # Remove any remaining passwords in URLs
    error_str = re.sub(
        r'://([^:]+):([^@]+)@',
        r'://\1:[REDACTED]@',
        error_str
    )

    # Remove API keys (common patterns)
    # sk-... (OpenAI, DeepSeek)
    error_str = re.sub(
        r'sk-[a-zA-Z0-9]{20,}',
        'sk-[REDACTED]',
        error_str
    )

    # AIza... (Google)
    error_str = re.sub(
        r'AIza[a-zA-Z0-9_-]{35}',
        'AIza[REDACTED]',
        error_str
    )

    # eyJ... (JWT tokens)
    error_str = re.sub(
        r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
        'eyJ[REDACTED]',
        error_str
    )

    # aiveilix_sk_live_... (our API keys)
    error_str = re.sub(
        r'aiveilix_sk_live_[a-zA-Z0-9]+',
        'aiveilix_sk_live_[REDACTED]',
        error_str
    )

    # Remove file paths (might contain usernames)
    error_str = re.sub(
        r'/Users/[^/]+/',
        '/Users/[REDACTED]/',
        error_str
    )
    error_str = re.sub(
        r'/home/[^/]+/',
        '/home/[REDACTED]/',
        error_str
    )

    # Remove IP addresses
    error_str = re.sub(
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        '[IP_REDACTED]',
        error_str
    )

    return error_str


def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitize a dictionary, removing sensitive keys.

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data

    sensitive_keys = {
        'password', 'secret', 'token', 'api_key', 'apikey',
        'database_url', 'db_url', 'connection_string',
        'private_key', 'access_key', 'secret_key'
    }

    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()

        # Check if key contains sensitive info
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value

    return sanitized
