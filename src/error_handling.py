from enum import Enum, auto
import logging
import traceback
from typing import Optional, Any, Dict, Union


class ErrorSeverity(Enum):
    """
    Defines the severity levels for errors in the Adaptive Learning Process.
    """
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class ALPBaseError(Exception):
    """
    Base custom exception for Adaptive Learning Process errors.
    Provides a standardized error handling mechanism.
    """
    def __init__(
        self, 
        message: str, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an ALP error with detailed information.

        Args:
            message (str): Descriptive error message
            severity (ErrorSeverity): Error severity level
            context (Optional[Dict[str, Any]]): Additional contextual information
        """
        self.message = message
        self.severity = severity
        self.context = context or {}
        super().__init__(self.message)

    def log_error(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Log the error with appropriate severity and context.

        Args:
            logger (Optional[logging.Logger]): Logger to use for error logging
        """
        if logger is None:
            logger = logging.getLogger(__name__)

        log_methods = {
            ErrorSeverity.LOW: logger.info,
            ErrorSeverity.MEDIUM: logger.warning,
            ErrorSeverity.HIGH: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }

        log_method = log_methods.get(self.severity, logger.error)
        
        error_details = {
            'message': self.message,
            'severity': self.severity.name,
            'context': self.context
        }
        
        log_method(f"ALP Error: {error_details}")


class IterationError(ALPBaseError):
    """
    Specific error for issues occurring during learning iterations.
    """
    def __init__(
        self, 
        message: str, 
        iteration_number: Optional[int] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ):
        """
        Initialize an iteration-specific error.

        Args:
            message (str): Descriptive error message
            iteration_number (Optional[int]): Iteration where error occurred
            severity (ErrorSeverity): Error severity level
        """
        context = {'iteration_number': iteration_number} if iteration_number is not None else {}
        super().__init__(message, severity=severity, context=context)


class ErrorHandler:
    """
    Centralized error management and handling strategy for ALP.
    """
    def __init__(
        self, 
        logger: Optional[logging.Logger] = None, 
        max_retries: int = 3
    ):
        """
        Initialize the error handler.

        Args:
            logger (Optional[logging.Logger]): Custom logger, defaults to root logger
            max_retries (int): Maximum number of retry attempts
        """
        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = max_retries

    def handle_error(
        self, 
        error: Union[Exception, ALPBaseError], 
        recovery_callback: Optional[callable] = None
    ) -> bool:
        """
        Handle and potentially recover from an error.

        Args:
            error (Union[Exception, ALPBaseError]): Error to handle
            recovery_callback (Optional[callable]): Optional recovery function

        Returns:
            bool: Whether the error was successfully handled
        """
        try:
            # If it's an ALPBaseError, use its log method
            if isinstance(error, ALPBaseError):
                error.log_error(self.logger)
            else:
                # For standard exceptions, log with traceback
                self.logger.error(
                    f"Unhandled Exception: {str(error)}\n"
                    f"Traceback: {traceback.format_exc()}"
                )

            # Attempt recovery if callback is provided
            if recovery_callback is not None:
                for attempt in range(self.max_retries):
                    try:
                        recovery_result = recovery_callback()
                        self.logger.info(f"Recovery attempt {attempt + 1} successful")
                        return True
                    except Exception as recovery_error:
                        self.logger.warning(
                            f"Recovery attempt {attempt + 1} failed: {recovery_error}"
                        )
                
                self.logger.critical("All recovery attempts failed")
                return False

            return False

        except Exception as handler_error:
            self.logger.critical(f"Error in error handling: {handler_error}")
            return False