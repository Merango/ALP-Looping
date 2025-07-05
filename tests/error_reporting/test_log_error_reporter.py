import os
import logging
import tempfile
import pytest
from src.error_reporting.log_error_reporter import LogErrorReporter
from src.error_reporting.base_error_reporter import ErrorSeverity

class MockException(Exception):
    """A mock exception for testing purposes."""
    pass

def test_log_error_reporter_console_logging(caplog):
    """Test logging errors to console."""
    reporter = LogErrorReporter()
    mock_error = MockException("Test console logging")
    
    # Test logging different severity levels
    reporter.report_error(mock_error, {"test": "context"}, ErrorSeverity.MEDIUM)
    
    assert len(caplog.records) > 0
    assert "Test console logging" in caplog.text

def test_log_error_reporter_file_logging(caplog):
    """Test logging errors to a file."""
    with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_log_file:
        temp_log_path = temp_log_file.name
    
    try:
        reporter = LogErrorReporter(log_file=temp_log_path)
        mock_error = MockException("Test file logging")
        
        reporter.report_error(mock_error, {"test": "file_context"}, ErrorSeverity.HIGH)
        
        with open(temp_log_path, 'r') as log_file:
            log_content = log_file.read()
            
        assert "Test file logging" in log_content
        assert "ERROR" in log_content
    finally:
        # Clean up the temporary log file
        os.unlink(temp_log_path)

def test_log_error_reporter_severity_mapping(caplog):
    """Test severity level mapping to log levels."""
    test_cases = [
        (ErrorSeverity.LOW, logging.DEBUG),
        (ErrorSeverity.MEDIUM, logging.WARNING),
        (ErrorSeverity.HIGH, logging.ERROR),
        (ErrorSeverity.CRITICAL, logging.CRITICAL)
    ]
    
    for severity, expected_level in test_cases:
        caplog.clear()  # Clear previous log records
        reporter = LogErrorReporter()
        mock_error = MockException(f"Test {severity}")
        
        with caplog.at_level(logging.DEBUG):
            reporter.report_error(mock_error, severity=severity)
        
        matching_records = [
            record for record in caplog.records 
            if record.levelno == expected_level and str(mock_error) in record.message
        ]
        
        assert len(matching_records) > 0, f"Failed for severity {severity}"