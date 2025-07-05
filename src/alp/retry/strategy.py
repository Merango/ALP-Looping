import time
import logging
from typing import Callable, TypeVar, Any, Optional
from functools import wraps
from enum import Enum, auto

class RetryStrategy(Enum):
    """Enumeration of retry strategies."""
    CONSTANT = auto()
    LINEAR = auto()
    EXPONENTIAL = auto()

class TransientErrorRetryHandler:
    """
    A configurable retry mechanism for handling transient errors in machine learning iterations.
    
    Key Features:
    - Multiple retry strategies (constant, linear, exponential backoff)
    - Configurable max retries and delay
    - Flexible error handling
    - Logging support
    """
    
    def __init__(
        self, 
        max_retries: int = 3, 
        initial_delay: float = 1.0, 
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the retry handler.
        
        Args:
            max_retries (int): Maximum number of retry attempts. Defaults to 3.
            initial_delay (float): Initial delay between retries in seconds. Defaults to 1.0.
            strategy (RetryStrategy): Retry delay strategy. Defaults to exponential.
            logger (Optional[logging.Logger]): Custom logger for retry events.
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.strategy = strategy
        self.logger = logger or logging.getLogger(__name__)
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate retry delay based on the chosen strategy.
        
        Args:
            attempt (int): Current retry attempt number.
        
        Returns:
            float: Calculated delay in seconds.
        """
        if self.strategy == RetryStrategy.CONSTANT:
            return self.initial_delay
        elif self.strategy == RetryStrategy.LINEAR:
            return self.initial_delay * attempt
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            return self.initial_delay * (2 ** (attempt - 1))
        return self.initial_delay
    
    def retry(self, 
              exceptions: tuple[type[Exception], ...] = (Exception,), 
              on_retry: Optional[Callable[[int, Exception], None]] = None
             ) -> Callable:
        """
        Decorator for retrying a function with configurable retry logic.
        
        Args:
            exceptions (tuple): Tuple of exception types to catch and retry.
            on_retry (Optional[Callable]): Optional callback for retry events.
        
        Returns:
            Callable: Decorated function with retry mechanism.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(1, self.max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        # Log retry attempt
                        self.logger.warning(
                            f"Retry attempt {attempt}/{self.max_retries} for {func.__name__}: {str(e)}"
                        )
                        
                        # Call custom retry callback if provided
                        if on_retry:
                            on_retry(attempt, e)
                        
                        # Don't delay on the last attempt
                        if attempt < self.max_retries:
                            delay = self._calculate_delay(attempt)
                            time.sleep(delay)
                
                # Raise the last exception if all retries fail
                self.logger.error(
                    f"All retry attempts failed for {func.__name__}"
                )
                raise last_exception
            return wrapper
        return decorator

# Type variable for return type preservation
T = TypeVar('T')