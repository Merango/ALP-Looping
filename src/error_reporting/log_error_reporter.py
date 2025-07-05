import logging
from typing import Dict, Any, Optional
from .base_error_reporter import BaseErrorReporter, ErrorSeverity

class LogErrorReporter(BaseErrorReporter):
    """
    Implementation of error reporting that logs errors to a file or console.
    
    Allows configurable logging of errors with different severity levels
    and optional file-based logging.
    """
    
    def __init__(
        self, 
        log_file: Optional[str] = None, 
        log_level: int = logging.INFO
    ):
        """
        Initialize the log-based error reporter.
        
        Args:
            log_file (Optional[str]): Path to log file. If None, logs to console.
            log_level (int): Logging level from the logging module
        """
        super().__init__()
        
        # Configure logging
        if log_file:
            logging.basicConfig(
                filename=log_file, 
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def report_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> None:
        """
        Log an error with specified severity and optional context.
        
        Args:
            error (Exception): The exception to log
            context (Optional[Dict[str, Any]]): Additional error context
            severity (ErrorSeverity): Severity level of the error
        """
        log_message = self._format_error_message(error, context)
        
        # Map severity to logging levels
        severity_map = {
            ErrorSeverity.LOW: logging.DEBUG,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        
        log_level = severity_map.get(severity, logging.WARNING)
        self.logger.log(log_level, log_message)