"""
Custom exception classes for the LLM engineering module.
"""


class LLMTwinException(Exception):
    """Base exception for LLM-related errors."""
    pass


class ImproperlyConfigured(LLMTwinException):
    """Raised when a required configuration is missing or invalid."""
    pass
