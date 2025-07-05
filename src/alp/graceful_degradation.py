import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Union

from .exceptions import ALPLoopError, ErrorSeverity, IterationInterruptionError


@dataclass
class DegradationStrategy:
    """
    Defines a strategy for handling errors during the ALP loop.
    
    Provides configurable approaches to manage different error scenarios
    with customizable recovery and fallback mechanisms.
    """

    name: str
    max_retries: int = 3
    current_retry_count: int = 0
    error_threshold: float = 0.5
    fallback_handler: Optional[Callable] = None
    state_recovery_fn: Optional[Callable] = None
    
    def handle_error(
        self, 
        error: ALPLoopError, 
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Handle an error with intelligent degradation strategy.

        Args:
            error (ALPLoopError): The error encountered
            context (Optional[Dict[str, Any]]): Additional context for error handling

        Returns:
            bool: Whether the error was successfully handled
        """
        # Always ensure context is a dict
        context = context or {}
        logging.error(f"Error in {self.name}: {error}")

        # Skip retries for critical non-recoverable errors
        if (error.severity == ErrorSeverity.CRITICAL and not error.recoverable):
            logging.critical(f"Non-recoverable critical error: {error}")
            return False

        # Check retry limits
        if self.current_retry_count >= self.max_retries:
            logging.warning(f"Max retries exceeded for {self.name}")
            
            # Attempt fallback if available
            if self.fallback_handler:
                try:
                    return self.fallback_handler(error, context)
                except Exception as fallback_error:
                    logging.error(f"Fallback failed: {fallback_error}")
            
            return False

        # Increment retry count
        self.current_retry_count += 1
        
        # Attempt state recovery if possible
        if self.state_recovery_fn:
            try:
                # Call recovery function and modify context in-place
                recovery_result = self.state_recovery_fn(context)
                
                # Ensure 'recovered' is set 
                context['recovered'] = True
                
                # If additional context was returned, update
                if isinstance(recovery_result, dict):
                    context.update(recovery_result)
            except Exception as recovery_error:
                logging.error(f"State recovery failed: {recovery_error}")
                return False

        return True

    def reset(self):
        """Reset the degradation strategy to initial state."""
        self.current_retry_count = 0