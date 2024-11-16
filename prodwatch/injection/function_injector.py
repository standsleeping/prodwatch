import os
import sys


def find_function(function_name):
    for name, module in sys.modules.items():
        if module is None:
            continue
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            if callable(func):
                return module, func
    return None, None


class FunctionWatcher:
    def __init__(self, log_file=None):
        self.log_file = log_file or os.environ.get("APP_LOG_FILE", "/app/log_file.txt")

    def inject_function(self, function_name):
        print(f"Injecting {function_name}")
        module, original_function = find_function(function_name)
        print(f"Module: {module}, Original function: {original_function}")

        if not (module and original_function):
            return False

        def logged_function(*args, **kwargs):
            result = original_function(*args, **kwargs)
            try:
                with open(self.log_file, "a") as f:
                    write_string = f"Function {module.__name__}.{function_name} called with args: {args}, kwargs: {kwargs}, result: {result}\n"
                    f.write(write_string)
                print(f"Logged {module.__name__}.{function_name} call")
            except Exception as e:
                print(f"Error writing to log file: {e}")
            return result

        setattr(module, function_name, logged_function)
        return True
