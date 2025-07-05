from enum import Enum, auto
from typing import Optional


class ErrorSeverity(Enum):
    """Defines the severity levels for ALP loop errors."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class ALPLoopError(Exception):
    """Base exception for Adaptive Learning Process loop errors."""

    def __init__(
        self, 
        message: str, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = True
    ):
        """
        Initialize an ALP loop error.

        Args:
            message (str): Detailed error description
            severity (ErrorSeverity): Error severity level
            recoverable (bool): Whether the error can be recovered from
        """
        super().__init__(message)
        self.severity = severity
        self.recoverable = recoverable


class IterationInterruptionError(ALPLoopError):
    """
    Raised when an iteration needs to be interrupted due to critical issues.
    
    This exception allows controlled interruption of the learning process
    with specific recovery strategies.
    """

    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        fallback_strategy: Optional[str] = None
    ):
        """
        Initialize an iteration interruption error.

        Args:
            message (str): Description of the interruption
            retry_after (Optional[int]): Suggested delay before retry (in seconds)
            fallback_strategy (Optional[str]): Alternative processing strategy
        """
        super().__init__(
            message, 
            severity=ErrorSeverity.HIGH, 
            recoverable=True
        )
        self.retry_after = retry_after
        self.fallback_strategy = fallback_strategy