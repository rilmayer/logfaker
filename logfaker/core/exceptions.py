"""Custom exceptions for Logfaker."""


class LogfakerError(Exception):
    """Base exception for all Logfaker errors."""


class ContentGenerationError(LogfakerError):
    """Error raised during content generation with limits.
    
    Used when content generation fails due to exceeding limits
    or other content-specific constraints.
    """

    pass


class ConfigurationError(LogfakerError):
    """Raised when there's an issue with configuration."""

    pass


class GenerationError(LogfakerError):
    """Raised when content generation fails."""

    pass


class SearchEngineError(LogfakerError):
    """Raised when search engine operations fail."""

    pass


class ValidationError(LogfakerError):
    """Raised when data validation fails."""

    pass
