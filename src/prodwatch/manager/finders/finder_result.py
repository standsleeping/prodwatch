from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from types import ModuleType
from typing import Any, Callable, Dict


class FunctionType(Enum):
    REGULAR = auto()
    METHOD = auto()
    PROPERTY = auto()


@dataclass
class FinderResult:
    module: ModuleType | None
    function: Callable[..., Any] | property | None
    function_type: FunctionType
    klass: type[Any] | None = None
    found: bool = True

    @classmethod
    def not_found(cls) -> "FinderResult":
        return cls(
            module=None,
            function=None,
            function_type=FunctionType.REGULAR,
            klass=None,
            found=False,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize FinderResult to a dictionary for server transmission."""
        return {
            "found": self.found,
            "function_type": self.function_type.name,
            "module_name": self.module.__name__ if self.module else None,
            "module_file": getattr(self.module, "__file__", None) if self.module else None,
            "function_name": getattr(self.function, "__name__", None) if self.function else None,
            "function_qualname": getattr(self.function, "__qualname__", None) if self.function else None,
            "class_name": self.klass.__name__ if self.klass else None,
            "class_qualname": getattr(self.klass, "__qualname__", None) if self.klass else None,
            "is_property": isinstance(self.function, property),
        }