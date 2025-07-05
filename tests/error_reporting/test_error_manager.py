import os
import pytest
import logging
from src.error_reporting.error_manager import ErrorReportingManager, ErrorSeverity

def test_error_reporting_initialization():
    """Test initialization of ErrorReportingManager."""
    error_manager = ErrorReportingManager()
    assert isinstance(error_manager, ErrorReportingManager)

def test_report_error():
    """Test reporting an error."""
    log_file = 'logs/test_error.log'
    
    # Custom notification callback for testing
    notification_log = []
    def mock_notification_callback(log_message, error_report):
        notification_log.append(error_report)
    
    error_manager = ErrorReportingManager(
        log_file=log_file, 
        notification_callback=mock_notification_callback
    )
    
    try:
        raise ValueError("Test error")
    except ValueError as e:
        error_report = error_manager.report_error(e, {'test_key': 'test_value'})
    
    # Verify error report structure
    assert 'timestamp' in error_report
    assert 'error_type' in error_report
    assert 'error_message' in error_report
    assert 'severity' in error_report
    assert 'traceback' in error_report
    assert 'context' in error_report
    
    # Verify log file was created
    assert os.path.exists(error_manager.log_file)
    
    # Verify notification callback was called
    assert len(notification_log) == 1
    assert notification_log[0]['error_message'] == 'Test error'

def test_handle_critical_error(capsys):
    """Test handling of critical errors."""
    error_manager = ErrorReportingManager()
    
    try:
        raise RuntimeError("Critical system failure")
    except RuntimeError as e:
        error_manager.handle_critical_error(e, {'system': 'ALP Loop'})
    
    # Check if error was printed to stderr
    captured = capsys.readouterr()
    assert "CRITICAL ERROR DETECTED" in captured.err

def test_recovery_attempt():
    """Test error recovery strategy."""
    error_manager = ErrorReportingManager()
    
    # Successful recovery
    def successful_recovery():
        return True
    
    try:
        raise ValueError("Recoverable error")
    except ValueError as e:
        recovery_result = error_manager.recovery_attempt(e, successful_recovery)
    
    assert recovery_result is True
    
    # Failed recovery
    def failed_recovery():
        raise RuntimeError("Recovery failed")
    
    try:
        raise ValueError("Unrecoverable error")
    except ValueError as e:
        recovery_result = error_manager.recovery_attempt(e, failed_recovery)
    
    assert recovery_result is False