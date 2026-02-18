"""
Utility functions for URL Shortener
"""
import random
import string
import validators
from typing import Optional

def generate_short_code(min_length: int = 5, max_length: int = 10) -> str:
    """
    Generate a random short code
    Characters: a-z, A-Z, 0-9
    Length: between min_length and max_length
    """
    length = random.randint(min_length, max_length)
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def is_valid_short_code(code: str) -> bool:
    """
    Validate short code format
    - Length: 5-10 characters
    - Allowed: letters (a-z, A-Z) and digits (0-9)
    """
    if not code:
        return False
    if len(code) < 5 or len(code) > 10:
        return False
    # Check if all characters are alphanumeric
    if not code.isalnum():
        return False
    return True

def format_short_url(base_domain: str, short_code: str) -> str:
    """Format the short URL with proper protocol"""
    # Remove trailing slash from base_domain
    base = base_domain.rstrip('/')
    # Ensure http:// or https:// prefix
    if not base.startswith('http'):
        base = f"http://{base}"
    return f"{base}/{short_code}"

def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate URL format
    Returns (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL is required"
    
    url = url.strip()
    
    # Check if URL is valid
    if not validators.url(url):
        # Try adding https:// prefix if missing
        if not url.startswith(('http://', 'https://')):
            test_url = f"https://{url}"
            if validators.url(test_url):
                return True, test_url
        return False, "Invalid URL format. Please include https:// or http://"
    
    return True, url

def sanitize_custom_code(code: str) -> str:
    """Sanitize custom short code input"""
    if not code:
        return ""
    # Remove whitespace and special characters
    code = code.strip()
    return code