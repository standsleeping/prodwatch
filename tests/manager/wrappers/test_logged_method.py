import pytest
from unittest.mock import Mock
import time
from typing import Any, ClassVar
from prodwatch.manager.wrappers.logged_method import create_logged_method


class FakeClass:
    class_value: ClassVar[int] = 42

    def __init__(self, value: int) -> None:
        self._value = value

    def instance_method(self, x: int, y: int = 10) -> int:
        return self._value + x + y

    @classmethod
    def class_method(cls, x: int) -> int:
        return cls.class_value + x

    @staticmethod
    def static_method(x: int) -> int:
        return x * 2

    def delayed_method(self, x: int) -> int:
        time.sleep(0.01)  # Small delay to ensure measurable execution time
        return self._value + x

    def error_method(self) -> None:
        raise ValueError("Test error")


def test_logged_instance_method():
    """Test logging an instance method call"""
    mock_logger = Mock()

    test_instance = FakeClass(42)

    logged_method = create_logged_method(
        FakeClass.instance_method,
        "FakeClass.instance_method",
        mock_logger,
    )

    result = logged_method(test_instance, 5, y=15)
    assert result == 62  # 42 + 5 + 15

    # Verify logging
    mock_logger.assert_called_once()
    call_args = mock_logger.call_args[0]
    assert call_args[0] == "FakeClass.instance_method"  # function_name
    assert len(call_args[1]) == 2  # self and x args

    # Instance representation
    assert call_args[1][0].startswith("<FakeClass object at ")
    assert call_args[1][1] == "5"  # x argument
    assert call_args[1][1] == "5"  # x argument
    assert call_args[2] == {"y": 15}  # kwargs


def test_logged_class_method():
    """Test logging a class method call"""
    mock_logger = Mock()

    # Get the raw function from the classmethod
    raw_method = FakeClass.class_method.__get__(None, FakeClass)

    logged_method = create_logged_method(
        raw_method,
        "FakeClass.class_method",
        mock_logger,
    )

    result = logged_method(5)
    assert result == 47  # 42 + 5

    # Verify logging
    mock_logger.assert_called_once()
    call_args = mock_logger.call_args[0]
    assert call_args[0] == "FakeClass.class_method"
    assert len(call_args[1]) == 1  # just x arg since class binding is handled
    assert call_args[1][0] == "5"  # x argument
    assert call_args[2] == {}  # No kwargs


def test_logged_static_method():
    """Test logging a static method call"""
    mock_logger = Mock()
    logged_method = create_logged_method(
        FakeClass.static_method,
        "FakeClass.static_method",
        mock_logger,
    )

    result = logged_method(5)
    assert result == 10  # 5 * 2

    # Verify logging
    mock_logger.assert_called_once()
    call_args = mock_logger.call_args[0]
    assert call_args[0] == "FakeClass.static_method"
    assert len(call_args[1]) == 1  # Just x arg
    assert call_args[1][0] == "5"  # x argument
    assert call_args[2] == {}  # No kwargs


def test_execution_time_logging():
    """Test that execution time is measured and logged"""
    mock_logger = Mock()
    test_instance = FakeClass(42)
    logged_method = create_logged_method(
        FakeClass.delayed_method,
        "FakeClass.delayed_method",
        mock_logger,
    )

    logged_method(test_instance, 5)

    execution_time_ms = mock_logger.call_args[1]["execution_time_ms"]
    assert execution_time_ms > 0  # Should have some execution time
    assert execution_time_ms > 8.0  # Should be at least 8ms due to sleep(0.01)
    assert execution_time_ms < 1000.0  # Shouldn't take more than 1000ms (1 second)


def test_handles_logger_exception():
    """Test that exceptions in the logger don't affect the method execution"""

    def failing_logger(*args: Any, **kwargs: Any) -> None:
        raise Exception("Logger failed")

    test_instance = FakeClass(42)

    logged_method = create_logged_method(
        FakeClass.instance_method,
        "FakeClass.instance_method",
        failing_logger,
    )

    result = logged_method(test_instance, 5)
    assert result == 57  # 42 + 5 + 10 (default y)


def test_preserves_method_error():
    """Test that original method errors are preserved and logged"""
    mock_logger = Mock()

    test_instance = FakeClass(42)

    logged_method = create_logged_method(
        FakeClass.error_method,
        "FakeClass.error_method",
        mock_logger,
    )

    with pytest.raises(ValueError, match="Test error"):
        logged_method(test_instance)

    # Verify that the error was logged
    mock_logger.assert_called_once()
    call_args = mock_logger.call_args
    assert call_args[0][0] == "FakeClass.error_method"  # function_name
    assert len(call_args[0][1]) == 1  # Just self arg
    assert call_args[0][1][0].startswith("<FakeClass object at ")
    assert call_args[0][2] == {}  # No kwargs
    assert call_args[1]["execution_time_ms"] > 0
    assert call_args[1]["error"] == "Test error"


def test_multiple_calls_logged():
    """Test that multiple method calls are logged separately"""
    mock_logger = Mock()

    test_instance = FakeClass(42)

    logged_method = create_logged_method(
        FakeClass.instance_method,
        "FakeClass.instance_method",
        mock_logger,
    )

    logged_method(test_instance, 5)

    logged_method(test_instance, 10, y=20)

    assert mock_logger.call_count == 2
    calls = mock_logger.call_args_list

    # Check first call
    assert calls[0][0][0] == "FakeClass.instance_method"
    assert calls[0][0][1][0].startswith("<FakeClass object at ")
    assert calls[0][0][1][1] == "5"  # x argument as string
    assert calls[0][0][2] == {}

    # Check second call
    assert calls[1][0][0] == "FakeClass.instance_method"
    assert calls[1][0][1][0].startswith("<FakeClass object at ")
    assert calls[1][0][1][1] == "10"  # x argument as string
    assert calls[1][0][2] == {"y": 20}
