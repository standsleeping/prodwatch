import sys
from .finder_result import FinderResult, FunctionType


def find_class_method(method_name: str) -> FinderResult:
    """Find a class method, instance method, static method, or property in any loaded module.

    Args:
        method_name: The name of the method to find, in format 'ClassName.method_name'

    Returns:
        A FinderResult instance containing the module, class, and method if found
    """
    if "." not in method_name:
        return FinderResult.not_found()

    class_name, method_name = method_name.split(".", 1)

    for name, module in sys.modules.items():
        if module is None:
            continue

        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            if not isinstance(cls, type):
                continue

            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                # Check if it's a method, classmethod, staticmethod, or property
                if isinstance(method, property):
                    return FinderResult(
                        module=module,
                        function=method,
                        function_type=FunctionType.PROPERTY,
                        klass=cls
                    )
                elif callable(method):
                    return FinderResult(
                        module=module,
                        function=method,
                        function_type=FunctionType.METHOD,
                        klass=cls
                    )

    return FinderResult.not_found()
