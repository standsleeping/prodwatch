import pytest
from unittest.mock import Mock, call
import time
from prodwatch.manager.wrappers.logged_function import create_logged_function


def sample_function(x, y=10):
    """Sample function for testing"""
    time.sleep(0.01)  # Small delay to ensure measurable execution time
    return x + y


def test_logged_function_returns_original_result():
    """When the function is called, it returns the same result as the original"""
    mock_logger = Mock()

    logged_func = create_logged_function(
        sample_function,
        "sample_function",
        mock_logger,
    )

    result = logged_func(5, y=15)
    assert result == 20  # 5 + 15


def test_logged_function_passes_args():
    """When the function is called, it passes the args to the original function and the logger"""
    mock_logger = Mock()

    logged_func = create_logged_function(
        sample_function,
        "sample_function",
        mock_logger,
    )

    logged_func(5, y=15)
    mock_logger.assert_called_once()
    call_args = mock_logger.call_args[0]
    assert call_args[0] == "sample_function"  # function_name
    assert call_args[1] == [5]  # args
    assert call_args[2] == {"y": 15}  # kwargs


def test_execution_time_logging():
    """When the function is called, it logs the execution time"""
    mock_logger = Mock()

    logged_func = create_logged_function(
        sample_function,
        "sample_function",
        mock_logger,
    )

    logged_func(5)

    # Check that execution_time_ms was passed and is reasonable
    execution_time = mock_logger.call_args[1]["execution_time_ms"]
    assert execution_time > 0  # Should have some execution time
    assert execution_time > 8  # Should be at least 8ms due to sleep(0.01)
    assert execution_time < 1000  # Shouldn't take more than 1 second


def test_handles_logger_exception():
    """When the logger fails, it doesn't affect the function execution"""

    def failing_logger(*args, **kwargs):
        raise Exception("Logger failed")

    logged_func = create_logged_function(
        sample_function,
        "sample_function",
        failing_logger,
    )

    # Should still execute successfully despite logger failing
    result = logged_func(5)
    assert result == 15  # 5 + 10 (default y)


def test_preserves_function_error():
    """When the function errors, it preserves the error and logs it"""

    def failing_function(*args, **kwargs):
        raise ValueError("Test error")

    mock_logger = Mock()
    logged_func = create_logged_function(
        failing_function,
        "failing_function",
        mock_logger,
    )

    with pytest.raises(ValueError, match="Test error"):
        logged_func(5)

    # Verify that the error was logged
    mock_logger.assert_called_once()
    call_args = mock_logger.call_args
    assert call_args[0][0] == "failing_function"  # function_name
    assert call_args[0][1] == [5]  # args
    assert call_args[0][2] == {}  # kwargs
    assert call_args[1]["error"] == "Test error"
    assert call_args[1]["execution_time_ms"] > 0


def test_multiple_calls_logged():
    """When the function is called multiple times, it logs each call separately"""
    mock_logger = Mock()
    logged_func = create_logged_function(
        sample_function,
        "sample_function",
        mock_logger,
    )

    logged_func(5)
    logged_func(10, y=20)

    assert mock_logger.call_count == 2
    calls = mock_logger.call_args_list

    # Check first call
    assert calls[0][0][0] == "sample_function"
    assert calls[0][0][1] == [5]
    assert calls[0][0][2] == {}

    # Check second call
    assert calls[1][0][0] == "sample_function"
    assert calls[1][0][1] == [10]
    assert calls[1][0][2] == {"y": 20}
