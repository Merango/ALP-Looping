import logging
import sys
import os
from typing import Dict, Any, Optional, Callable
from enum import Enum, auto
import traceback
import json
from datetime import datetime

class ErrorSeverity(Enum):
    """Defines the severity levels for errors."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class ErrorReportingManager:
    """
    Comprehensive error reporting and notification system for ALP loop.
    
    Handles error logging, notification, and potential recovery strategies.
    """
    
    def __init__(
        self, 
        log_file: str = 'logs/alp_error.log', 
        notification_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        """
        Initialize the Error Reporting Manager.
        
        Args:
            log_file (str): Path to the log file for error logging.
            notification_callback (Optional[Callable]): Optional callback for custom error notifications.
        """
        # Determine base path - prefer logs directory in project root, fallback to relative path
        potential_base_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs')),
            os.path.abspath(os.path.join(os.getcwd(), 'logs')),
            os.path.dirname(log_file)
        ]
        
        # Find the first existing logs directory or create one
        log_dir = None
        for path in potential_base_paths:
            if os.path.exists(path):
                log_dir = path
                break
        
        # If no logs directory found, create one in the project root
        if not log_dir:
            log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
            os.makedirs(log_dir, exist_ok=True)
        
        # Construct full log file path
        log_file = os.path.join(log_dir, os.path.basename(log_file))
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            filename=log_file, 
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        self.notification_callback = notification_callback
    
    def report_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> Dict[str, Any]:
        """
        Report and log a comprehensive error with context.
        
        Args:
            error (Exception): The exception that occurred.
            context (Optional[Dict]): Additional context about the error.
            severity (ErrorSeverity): Severity level of the error.
        
        Returns:
            Dict[str, Any]: Detailed error report.
        """
        # Prepare error details
        error_report = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'severity': severity.name,
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        # Log the error
        error_log_message = json.dumps(error_report, indent=2)
        self.logger.error(error_log_message)
        
        # Trigger notification if callback is set
        if self.notification_callback:
            try:
                self.notification_callback(error_log_message, error_report)
            except Exception as notification_error:
                self.logger.error(f"Error in notification callback: {notification_error}")
        
        return error_report
    
    def handle_critical_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle critical errors that potentially require system intervention.
        
        Args:
            error (Exception): The critical exception.
            context (Optional[Dict]): Additional context about the error.
        """
        error_report = self.report_error(error, context, severity=ErrorSeverity.CRITICAL)
        
        # Optional: Implement more aggressive error handling
        # For example, you might want to:
        # 1. Send an urgent notification
        # 2. Attempt system recovery
        # 3. Potentially halt the ALP loop
        
        # For demonstration, we'll just print a critical error message
        print(f"CRITICAL ERROR DETECTED: {error_report}", file=sys.stderr)
    
    def recovery_attempt(self, error: Exception, recovery_strategy: Callable[[], bool]) -> bool:
        """
        Attempt to recover from an error using a provided recovery strategy.
        
        Args:
            error (Exception): The error to recover from.
            recovery_strategy (Callable): A function that attempts to recover from the error.
        
        Returns:
            bool: Whether recovery was successful.
        """
        try:
            return recovery_strategy()
        except Exception as recovery_error:
            self.report_error(
                recovery_error, 
                context={'original_error': str(error)},
                severity=ErrorSeverity.HIGH
            )
            return False