import time
import logging
from types import ModuleType
from typing import Any, Callable, TypeVar

from ..types import LoggingCallback

logger = logging.getLogger(__name__)

# TypeVar for return type
M = TypeVar("M")


def create_logged_method(
    original_function: Callable[..., M],
    function_name: str,
    log_function_call: LoggingCallback,
) -> Callable[..., M]:
    def logged_method(*args: Any, **kwargs: Any) -> M:
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
                # Convert args to serializable representations
                serializable_args = []
                for arg in args:
                    if isinstance(arg, type):
                        # Class object (for class methods)
                        serializable_args.append(f"<class '{arg.__name__}'>")
                    elif isinstance(arg, (int, float, bool)):
                        # Convert numbers and booleans to their string representation
                        serializable_args.append(str(arg))
                    elif isinstance(arg, str):
                        # Strings are already serializable
                        serializable_args.append(arg)
                    elif arg is None:
                        # Handle None explicitly
                        serializable_args.append("None")
                    elif isinstance(arg, ModuleType):
                        # Handle module objects
                        serializable_args.append(f"<module '{arg.__name__}'>")
                    else:
                        # Instance objects and everything else
                        serializable_args.append(
                            f"<{arg.__class__.__name__} object at {hex(id(arg))}>"
                        )

                log_function_call(
                    function_name,
                    serializable_args,
                    kwargs,
                    execution_time_ms=execution_time_ms,
                    error=str(error) if error else None,
                )
            except Exception as e:
                logger.error(f"Error logging method call: {e}")

    return logged_method
