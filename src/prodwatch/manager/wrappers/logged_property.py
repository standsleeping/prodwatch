import time
import logging
from typing import Any, Callable, TypeVar

from ..types import LoggingCallback

logger = logging.getLogger(__name__)

# TypeVar for return type
P = TypeVar("P", bound=Any)


def create_logged_property(
    original_function: property, function_name: str, log_function_call: LoggingCallback
) -> Callable[[Any], Any]:
    def logged_property(self: Any) -> Any:
        start_time = time.perf_counter()
        error = None
        try:
            # Use the property's fget attribute to get the actual function
            # Check if fget is callable
            if callable(original_function.fget):
                result = original_function.fget(self)
                return result
            else:
                logger.error(f"Property {function_name} has no callable fget")
                return None
        except Exception as e:
            error = e
            raise
        finally:
            end_time = time.perf_counter()
            diff = end_time - start_time
            execution_time_ms = diff * 1000
            try:
                # For properties, we only pass the instance as an arg
                serializable_args = [
                    f"<{self.__class__.__name__} object at {hex(id(self))}>"
                ]

                log_function_call(
                    function_name,
                    serializable_args,
                    {},  # no kwargs for properties
                    execution_time_ms=execution_time_ms,
                    error=str(error) if error else None,
                )
            except Exception as e:
                logger.error(f"Error logging property call: {e}")

    return logged_property
