from typing import List, Dict, Any, Optional, TypeVar, ParamSpec, Protocol

# For the function itself, we can use ParamSpec and TypeVar
P = ParamSpec("P")
R = TypeVar("R")


class LoggingCallback(Protocol):
    """Protocol for function call logging callbacks."""

    def __call__(
        self,
        function_name: str,
        args: List[Any],
        kwargs: Dict[str, Any],
        execution_time_ms: float,
        error: Optional[str] = None,
    ) -> None: ...
