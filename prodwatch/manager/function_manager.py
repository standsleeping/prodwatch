import sys
import time


def find_function(function_name):
    for name, module in sys.modules.items():
        if module is None:
            continue
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            if callable(func):
                return module, func
    return None, None


class FunctionManager:
    def __init__(self, log_function_call):
        self.log_function_call = log_function_call

    def watch_function(self, function_name):
        print(f"Watching {function_name}")
        module, original_function = find_function(function_name)
        print(f"Module: {module}, Original function: {original_function}")

        if not (module and original_function):
            return False

        def logged_function(*args, **kwargs):
            start_time = time.perf_counter()
            result = original_function(*args, **kwargs)
            end_time = time.perf_counter()
            diff = end_time - start_time
            execution_time_ms = diff * 1000  # Convert to milliseconds

            try:
                self.log_function_call(
                    function_name, args, kwargs, execution_time_ms=execution_time_ms
                )
                write_string = (
                    f"Function {module.__name__}.{function_name} called with "
                    f"args: {args}, kwargs: {kwargs}, result: {result}, "
                    f"execution time: {execution_time_ms:.2f}ms\n"
                )
                print(write_string)
            except Exception as e:
                print(f"Error writing to log file: {e}")
            return result

        setattr(module, function_name, logged_function)
        return True
