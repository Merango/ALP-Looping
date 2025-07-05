import pytest
from src.graceful_degradation import AdaptiveLearningProcessor, LoopState

def test_normal_iteration():
    """Test a successful iteration."""
    processor = AdaptiveLearningProcessor()
    
    def successful_iteration():
        return True
    
    result = processor.process_iteration(successful_iteration)
    
    assert result == LoopState.RUNNING
    assert processor.current_state == LoopState.RUNNING
    assert processor.iteration_count == 1

def test_failed_iteration_with_recovery():
    """Test a failed iteration with successful recovery."""
    recovery_log = []
    
    def recovery_callback(error_details):
        recovery_log.append(error_details)
    
    processor = AdaptiveLearningProcessor(
        max_retry_attempts=3, 
        recovery_callback=recovery_callback
    )
    
    # Simulate iteration failure
    def failing_iteration():
        raise ValueError("Simulated iteration failure")
    
    result = processor.process_iteration(failing_iteration)
    
    assert result == LoopState.RUNNING
    assert len(recovery_log) == 1
    assert 'error_type' in recovery_log[0]
    assert processor.iteration_count == 1

def test_max_retry_exhausted():
    """Test that the loop terminates after max retry attempts."""
    processor = AdaptiveLearningProcessor(max_retry_attempts=1)
    
    def consistently_failing_iteration():
        raise RuntimeError("Always failing")
    
    # First attempt
    result1 = processor.process_iteration(consistently_failing_iteration)
    assert result1 == LoopState.RUNNING
    
    # Second attempt (which will terminate)
    result2 = processor.process_iteration(consistently_failing_iteration)
    assert result2 == LoopState.TERMINATED
    assert processor.current_state == LoopState.TERMINATED

def test_error_details_capture():
    """Verify that error details are captured correctly."""
    processor = AdaptiveLearningProcessor()
    
    def error_generating_iteration():
        raise TypeError("Specific type error")
    
    processor.process_iteration(error_generating_iteration)
    
    error_details = processor.error_details
    assert error_details['error_type'] == 'TypeError'
    assert error_details['error_message'] == 'Specific type error'

def test_prevent_processing_after_termination():
    """Ensure no iterations can be processed after termination."""
    processor = AdaptiveLearningProcessor(max_retry_attempts=1)
    
    def failing_iteration():
        raise RuntimeError("Simulated failure")
    
    # First attempt fails and attempts recovery
    result1 = processor.process_iteration(failing_iteration)
    assert result1 == LoopState.RUNNING
    
    # Second attempt terminates
    result2 = processor.process_iteration(failing_iteration)
    assert result2 == LoopState.TERMINATED
    
    # Attempting another iteration should remain terminated
    result3 = processor.process_iteration(failing_iteration)
    assert result3 == LoopState.TERMINATED