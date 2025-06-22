import time
import logging
from typing import Callable
from ..types import LoggingCallback, P, R

logger = logging.getLogger(__name__)


def create_logged_function(
    original_function: Callable[P, R],
    function_name: str,
    log_function_call: LoggingCallback,
) -> Callable[P, R]:
    def logged_function(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        error = None
        try:
            result = original_function(*args, **kwargs)
            return result
        except Exception as e:
            error = e
            raise
        finally:
            end_time = time.perf_counter()
            diff = end_time - start_time
            execution_time_ms = diff * 1000
            try:
                log_function_call(
                    function_name,
                    list(args),  # Convert args tuple to list
                    kwargs,
                    execution_time_ms=execution_time_ms,
                    error=str(error) if error else None,
                )
            except Exception as e:
                logger.error(f"Error logging function call: {e}")

    return logged_function
