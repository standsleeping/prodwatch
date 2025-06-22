import sys
from .find_module_function import find_module_function
from .find_class_method import find_class_method
from .finder_result import FinderResult, FunctionType


def find_function(function_name: str) -> FinderResult:
    """Find a function or method in any loaded module.

    Handles three cases:
    1. Module-qualified functions (e.g. 'mymodule.myfunction')
    2. Class methods (e.g. 'MyClass.method')
    3. Regular functions (e.g. 'myfunction')

    Args:
        function_name: The name of the function to find

    Returns:
        A FinderResult instance containing the found function details
    """
    if "." in function_name:
        # First, try as a module-qualified function
        result = find_module_function(function_name)
        if result.found:
            return result

        # Then, try as a class method
        result = find_class_method(function_name)
        if result.found:
            return result

    # Finally, try as a regular function
    for name, module in sys.modules.items():
        if module is None:
            continue
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            if callable(func):
                return FinderResult(
                    module=module,
                    function=func,
                    function_type=FunctionType.REGULAR
                )
    return FinderResult.not_found()
