from typing import Optional, Any, Dict, Callable
from enum import Enum, auto
import logging
import traceback

class LoopState(Enum):
    """Represents the possible states of the learning loop."""
    RUNNING = auto()
    PAUSED = auto()
    TERMINATED = auto()
    ERROR = auto()

class GracefulDegradationError(Exception):
    """Base exception for graceful degradation errors."""
    pass

class LearningLoopFailure(GracefulDegradationError):
    """Raised when a critical error occurs in the learning loop."""
    pass

class AdaptiveLearningProcessor:
    """
    Manages the adaptive learning process with graceful degradation capabilities.
    
    This class provides a robust mechanism for handling errors during learning iterations,
    ensuring system stability and data integrity.
    """
    
    def __init__(
        self, 
        max_retry_attempts: int = 3, 
        recovery_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Initialize the Adaptive Learning Processor.
        
        Args:
            max_retry_attempts (int): Maximum number of retry attempts on failure.
            recovery_callback (Optional[Callable]): Optional callback for custom recovery logic.
        """
        self._state: LoopState = LoopState.RUNNING
        self._current_iteration: int = 0
        self._max_retry_attempts = max_retry_attempts
        self._recovery_callback = recovery_callback
        self._error_log: Dict[str, Any] = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self._logger = logging.getLogger(__name__)
    
    def process_iteration(self, iteration_func: Callable[[], None]) -> LoopState:
        """
        Process a single learning iteration with robust error handling.
        
        Args:
            iteration_func (Callable): Function representing a single learning iteration.
        
        Returns:
            LoopState: Final state of the learning loop.
        """
        try:
            # Increment iteration counter
            self._current_iteration += 1
            
            # Validate iteration is possible
            if self._state != LoopState.RUNNING:
                raise LearningLoopFailure(f"Cannot process iteration in {self._state} state")
            
            # Execute iteration
            iteration_func()
            
            return LoopState.RUNNING
        
        except Exception as e:
            return self._handle_iteration_error(e)
    
    def _handle_iteration_error(self, error: Exception) -> LoopState:
        """
        Handle errors during learning iterations with a structured approach.
        
        Args:
            error (Exception): The error encountered during iteration.
        
        Returns:
            LoopState: Resulting state after error handling.
        """
        # Log the error
        error_details = {
            'iteration': self._current_iteration,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc()
        }
        self._logger.error(f"Learning iteration failed: {error_details}")
        
        # Store error details
        self._error_log = error_details
        
        # Update state
        self._state = LoopState.ERROR
        
        # Attempt recovery if max retries not reached
        if self._current_iteration <= self._max_retry_attempts:
            try:
                # Optional custom recovery logic
                if self._recovery_callback:
                    self._recovery_callback(error_details)
                
                # Reset state to allow retry
                self._state = LoopState.RUNNING
                self._logger.info("Attempting recovery...")
                return LoopState.RUNNING
            except Exception as recovery_error:
                self._logger.error(f"Recovery failed: {recovery_error}")
        
        # Terminate if retry attempts exhausted
        self._state = LoopState.TERMINATED
        return LoopState.TERMINATED
    
    @property
    def current_state(self) -> LoopState:
        """Get the current state of the learning loop."""
        return self._state
    
    @property
    def iteration_count(self) -> int:
        """Get the current iteration count."""
        return self._current_iteration
    
    @property
    def error_details(self) -> Dict[str, Any]:
        """Retrieve detailed error information."""
        return self._error_log.copy()