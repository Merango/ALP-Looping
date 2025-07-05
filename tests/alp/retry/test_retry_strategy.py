import pytest
import time
import logging
from src.alp.retry.strategy import TransientErrorRetryHandler, RetryStrategy

class TestTransientErrorRetryHandler:
    def test_constant_retry_strategy(self):
        """Test constant retry strategy."""
        retry_handler = TransientErrorRetryHandler(
            max_retries=3, 
            initial_delay=0.1, 
            strategy=RetryStrategy.CONSTANT
        )
        
        attempts = 0
        
        @retry_handler.retry(exceptions=(ValueError,))
        def flaky_function():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary error")
            return "Success"
        
        result = flaky_function()
        assert result == "Success"
        assert attempts == 3
    
    def test_linear_retry_strategy(self):
        """Test linear retry strategy."""
        retry_handler = TransientErrorRetryHandler(
            max_retries=3, 
            initial_delay=0.1, 
            strategy=RetryStrategy.LINEAR
        )
        
        attempts = 0
        
        @retry_handler.retry(exceptions=(ValueError,))
        def flaky_function():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary error")
            return "Success"
        
        result = flaky_function()
        assert result == "Success"
        assert attempts == 3
    
    def test_exponential_retry_strategy(self):
        """Test exponential retry strategy."""
        retry_handler = TransientErrorRetryHandler(
            max_retries=3, 
            initial_delay=0.1, 
            strategy=RetryStrategy.EXPONENTIAL
        )
        
        attempts = 0
        
        @retry_handler.retry(exceptions=(ValueError,))
        def flaky_function():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary error")
            return "Success"
        
        result = flaky_function()
        assert result == "Success"
        assert attempts == 3
    
    def test_retry_callback(self):
        """Test custom retry callback."""
        retry_log = []
        retry_handler = TransientErrorRetryHandler(max_retries=3)
        
        def on_retry(attempt, exception):
            retry_log.append((attempt, str(exception)))
        
        @retry_handler.retry(exceptions=(ValueError,), on_retry=on_retry)
        def flaky_function():
            raise ValueError("Temporary error")
        
        with pytest.raises(ValueError):
            flaky_function()
        
        assert len(retry_log) == 3
        assert all(log[0] in range(1, 4) for log in retry_log)
        assert all("Temporary error" in log[1] for log in retry_log)
    
    def test_max_retries_exhausted(self):
        """Test that max retries raises the last exception."""
        retry_handler = TransientErrorRetryHandler(max_retries=2)
        
        attempts = 0
        
        @retry_handler.retry(exceptions=(ValueError,))
        def always_failing_function():
            nonlocal attempts
            attempts += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_failing_function()
        
        assert attempts == 2  # initial + 1 retry
    
    def test_different_exception_types(self):
        """Test retry works with multiple exception types."""
        retry_handler = TransientErrorRetryHandler(max_retries=3)
        
        attempts = 0
        
        @retry_handler.retry(exceptions=(ValueError, TypeError))
        def mixed_error_function():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise ValueError("First attempt")
            elif attempts == 2:
                raise TypeError("Second attempt")
            return "Success"
        
        result = mixed_error_function()
        assert result == "Success"
        assert attempts == 3