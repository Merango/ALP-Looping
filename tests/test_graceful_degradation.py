import pytest
from typing import Dict, Any

from src.alp.exceptions import ALPLoopError, ErrorSeverity, IterationInterruptionError
from src.alp.graceful_degradation import DegradationStrategy


def test_degradation_strategy_initialization():
    """Test that DegradationStrategy initializes correctly."""
    strategy = DegradationStrategy(name="test_strategy")
    
    assert strategy.name == "test_strategy"
    assert strategy.max_retries == 3
    assert strategy.current_retry_count == 0
    assert strategy.error_threshold == 0.5


def test_handle_error_retry_limit():
    """Test that strategy respects maximum retry limit."""
    
    fallback_called = False
    def mock_fallback_handler(error, context):
        nonlocal fallback_called
        fallback_called = True
        return False

    strategy = DegradationStrategy(
        name="retry_limit_test", 
        max_retries=2,
        fallback_handler=mock_fallback_handler
    )

    error = ALPLoopError("Test error", severity=ErrorSeverity.MEDIUM)

    # Simulate multiple error attempts
    assert strategy.handle_error(error) is True
    assert strategy.current_retry_count == 1

    assert strategy.handle_error(error) is True
    assert strategy.current_retry_count == 2

    # Third attempt should trigger fallback
    assert strategy.handle_error(error) is False
    assert fallback_called is True


def test_critical_non_recoverable_error():
    """Test handling of critical non-recoverable errors."""
    strategy = DegradationStrategy(name="critical_error_test")

    critical_error = ALPLoopError(
        "Critical non-recoverable error", 
        severity=ErrorSeverity.CRITICAL,
        recoverable=False
    )

    # Critical non-recoverable error should immediately return False
    assert strategy.handle_error(critical_error) is False
    assert strategy.current_retry_count == 0


def test_state_recovery():
    """Test state recovery mechanism."""
    recovery_context = {}

    def mock_state_recovery(context: Dict[str, Any]):
        context['recovered'] = True

    strategy = DegradationStrategy(
        name="recovery_test", 
        state_recovery_fn=mock_state_recovery
    )

    error = ALPLoopError("Recoverable error")
    
    assert strategy.handle_error(error, context=recovery_context) is True
    assert recovery_context.get('recovered') is True


def test_strategy_reset():
    """Test strategy reset functionality."""
    strategy = DegradationStrategy(name="reset_test")
    error = ALPLoopError("Test error")

    strategy.handle_error(error)
    assert strategy.current_retry_count == 1

    strategy.reset()
    assert strategy.current_retry_count == 0