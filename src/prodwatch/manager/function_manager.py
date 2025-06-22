import logging
from .types import LoggingCallback
from .finders.find_function import find_function
from .finders.finder_result import FunctionType, FinderResult
from .wrappers.logged_function import create_logged_function
from .wrappers.logged_method import create_logged_method
from .wrappers.logged_property import create_logged_property

logger = logging.getLogger(__name__)


class FunctionManager:
    def __init__(self, log_function_call: LoggingCallback) -> None:
        self.log_function_call = log_function_call

    def watch_function(self, function_name: str) -> tuple[bool, FinderResult]:
        logger.info(f"Setting up watch for function: {function_name}")
        result: FinderResult = find_function(function_name)

        if not result.found:
            logger.warning(f"Function {function_name} not found in any module")
            return False, result

        attr_name = function_name.split(".")[-1]
        match result.function_type:
            case FunctionType.REGULAR:
                logger.info(f"Found regular function in module: {result.module}")
                logged_function = create_logged_function(
                    result.function,
                    function_name,
                    self.log_function_call,
                )
                setattr(result.module, attr_name, logged_function)

            case FunctionType.PROPERTY:
                logger.info(f"Found property in class: {result.klass.__name__}")
                logged_property = create_logged_property(
                    result.function,
                    function_name,
                    self.log_function_call,
                )
                setattr(result.klass, attr_name, property(logged_property))

            case FunctionType.METHOD:
                logger.info(f"Found method in class: {result.klass.__name__}")
                logged_method = create_logged_method(
                    result.function,
                    function_name,
                    self.log_function_call,
                )

                # Preserve original method type (classmethod, staticmethod, or instance method)
                if isinstance(result.function, classmethod):
                    logged_method = classmethod(logged_method)
                elif isinstance(result.function, staticmethod):
                    logged_method = staticmethod(logged_method)

                setattr(result.klass, attr_name, logged_method)

        logger.info(f"Successfully set up watch for {function_name}")
        return True, result
