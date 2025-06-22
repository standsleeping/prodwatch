import sys
from .finder_result import FinderResult, FunctionType


def find_module_function(full_name: str) -> FinderResult:
    """Find a function in a specific module.

    Args:
        full_name: The name in format 'module.function' or 'module.submodule.function'

    Returns:
        A FinderResult instance containing the module and function if found
    """
    *module_parts, func_name = full_name.split(".")
    module_name = ".".join(module_parts)

    if module_name in sys.modules:
        module = sys.modules[module_name]
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                return FinderResult(
                    module=module,
                    function=func,
                    function_type=FunctionType.REGULAR
                )
    return FinderResult.not_found()
