from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from enum import Enum, auto

class ErrorSeverity(Enum):
    """Represents the severity levels of errors."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class BaseErrorReporter(ABC):
    """
    Abstract base class for error reporting and notification mechanisms.
    
    Provides a standardized interface for reporting errors across different
    notification channels while maintaining flexibility and extensibility.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the error reporter with optional custom logger.
        
        Args:
            logger (Optional[logging.Logger]): Custom logger instance. 
                If not provided, a default logger will be created.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def report_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> None:
        """
        Report an error with contextual information and severity.
        
        Args:
            error (Exception): The exception to be reported
            context (Optional[Dict[str, Any]]): Additional context about the error
            severity (ErrorSeverity): Severity level of the error
        """
        pass
    
    def _format_error_message(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a comprehensive error message with context.
        
        Args:
            error (Exception): The exception to format
            context (Optional[Dict[str, Any]]): Additional context information
        
        Returns:
            str: Formatted error message
        """
        context_str = f"\nContext: {context}" if context else ""
        return f"Error: {type(error).__name__} - {str(error)}{context_str}"