import pytest
from prodwatch.manager.function_manager import FunctionManager


def sample_function():
    return "test result"


def sample_function_with_args(arg1, arg2, kwarg1=None):
    return f"test result with {arg1}, {arg2}, {kwarg1}"


class TestFunctionWatcher:
    @pytest.fixture
    def mock_logger(self):
        calls = []

        def log_function_call(function_name, args, kwargs, execution_time_ms):
            calls.append(
                {
                    "function_name": function_name,
                    "args": args,
                    "kwargs": kwargs,
                    "execution_time_ms": execution_time_ms,
                }
            )

        return log_function_call, calls

    def test_watch_function_basic(self, mock_logger):
        log_function_call, calls = mock_logger
        watcher = FunctionManager(log_function_call)

        # Watch the test function
        success = watcher.watch_function("sample_function")
        assert success is True

        # Call the function
        result = sample_function()

        # Verify the result
        assert result == "test result"

        # Verify the call was logged
        assert len(calls) == 1
        assert calls[0]["function_name"] == "sample_function"
        assert calls[0]["args"] == ()
        assert calls[0]["kwargs"] == {}

    def test_watch_function_with_arguments(self, mock_logger):
        log_function_call, calls = mock_logger
        watcher = FunctionManager(log_function_call)

        # Watch the test function
        success = watcher.watch_function("sample_function_with_args")
        assert success is True

        # Call the function with arguments
        result = sample_function_with_args("value1", "value2", kwarg1="kwvalue")

        # Verify the result
        assert result == "test result with value1, value2, kwvalue"

        # Verify the call was logged
        assert len(calls) == 1
        assert calls[0]["function_name"] == "sample_function_with_args"
        assert calls[0]["args"] == ("value1", "value2")
        assert calls[0]["kwargs"] == {"kwarg1": "kwvalue"}

    def test_watch_nonexistent_function(self, mock_logger):
        log_function_call, calls = mock_logger
        watcher = FunctionManager(log_function_call)

        # Try to watch a function that doesn't exist
        success = watcher.watch_function("nonexistent_function")

        # Verify that the watch attempt failed
        assert success is False
        assert len(calls) == 0

    def test_log_function_error(self):
        def failing_logger(function_name, args, kwargs):
            raise Exception("Report failed")

        watcher = FunctionManager(failing_logger)
        success = watcher.watch_function("sample_function")
        assert success is True

        # The function should still work even if reporting fails
        result = sample_function()
        assert result == "test result"