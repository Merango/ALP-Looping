import pytest
import logging
from src.error_handling import (
    ALPBaseError, 
    IterationError, 
    ErrorHandler, 
    ErrorSeverity
)


def test_alp_base_error_creation():
    """Test creating an ALPBaseError with minimal parameters."""
    error = ALPBaseError("Test error")
    assert str(error) == "Test error"
    assert error.severity == ErrorSeverity.MEDIUM
    assert error.context == {}


def test_alp_base_error_with_context():
    """Test creating an ALPBaseError with context and custom severity."""
    context = {"key": "value"}
    error = ALPBaseError(
        "Detailed error", 
        severity=ErrorSeverity.HIGH, 
        context=context
    )
    assert str(error) == "Detailed error"
    assert error.severity == ErrorSeverity.HIGH
    assert error.context == context


def test_iteration_error():
    """Test creating an IterationError."""
    error = IterationError(
        "Iteration failed", 
        iteration_number=5, 
        severity=ErrorSeverity.CRITICAL
    )
    assert str(error) == "Iteration failed"
    assert error.severity == ErrorSeverity.CRITICAL
    assert error.context.get('iteration_number') == 5


def test_error_handler_basic():
    """Test basic error handler functionality."""
    handler = ErrorHandler()
    mock_error = ALPBaseError("Test Handler")
    
    # Should return False without recovery callback
    assert not handler.handle_error(mock_error)


def test_error_handler_recovery():
    """Test error handler with recovery callback."""
    handler = ErrorHandler()
    
    def successful_recovery():
        return True
    
    mock_error = ALPBaseError("Recoverable Error")
    
    # Should return True with successful recovery
    assert handler.handle_error(mock_error, recovery_callback=successful_recovery)


def test_error_handler_max_retries():
    """Test error handler with failing recovery attempts."""
    handler = ErrorHandler(max_retries=2)
    
    retry_count = 0
    def failing_recovery():
        nonlocal retry_count
        retry_count += 1
        raise Exception("Recovery failed")
    
    mock_error = ALPBaseError("Unrecoverable Error")
    
    # Should return False after max retries
    assert not handler.handle_error(mock_error, recovery_callback=failing_recovery)
    assert retry_count == 2


def test_error_logging(caplog):
    """Test that errors are logged with appropriate severity."""
    caplog.set_level(logging.INFO)
    
    error = ALPBaseError(
        "Logging Test", 
        severity=ErrorSeverity.HIGH
    )
    
    handler = ErrorHandler()
    handler.handle_error(error)
    
    assert "ALP Error" in caplog.text
    assert "Logging Test" in caplog.text
    assert "HIGH" in caplog.text