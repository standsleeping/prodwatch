import pytest
from unittest.mock import Mock
import time
from prodwatch.manager.wrappers.logged_property import create_logged_property


class SampleClass:
    def __init__(self, value):
        self._value = value

    @property
    def sample_property(self):
        """A sample property for testing"""
        time.sleep(0.01)  # Small delay to ensure measurable execution time
        return self._value


def test_logged_property_returns_original_result():
    """When the property is called, it returns the same result as the original"""
    mock_logger = Mock()
    test_obj = SampleClass(42)
    logged_prop = property(
        create_logged_property(
            test_obj.__class__.sample_property,
            "sample_property",
            mock_logger,
        )
    )

    # Replace the original property with our logged version
    type(test_obj).sample_property = logged_prop  # type: ignore

    result = test_obj.sample_property
    assert result == 42


def test_logged_property_logs_call():
    """When the property is called, it logs the call"""
    mock_logger = Mock()
    test_obj = SampleClass(42)
    logged_prop = property(
        create_logged_property(
            test_obj.__class__.sample_property,
            "sample_property",
            mock_logger,
        )
    )

    type(test_obj).sample_property = logged_prop  # type: ignore
    _ = test_obj.sample_property

    mock_logger.assert_called_once()
    call_args = mock_logger.call_args[0]
    assert call_args[0] == "sample_property"  # function_name
    assert len(call_args[1]) == 1  # args (should contain only self)
    assert "SampleClass object at" in call_args[1][0]  # Check self representation
    assert call_args[2] == {}  # kwargs should be empty for propertys


def test_execution_time_logging():
    """When the property is called, it logs the execution time"""
    mock_logger = Mock()
    test_obj = SampleClass(42)
    logged_prop = property(
        create_logged_property(
            test_obj.__class__.sample_property,
            "sample_property",
            mock_logger,
        )
    )

    type(test_obj).sample_property = logged_prop  # type: ignore
    _ = test_obj.sample_property

    # Check that execution_time_ms was passed and is reasonable
    execution_time = mock_logger.call_args[1]["execution_time_ms"]
    assert execution_time > 0  # Should have some execution time
    assert execution_time > 8  # Should be at least 8ms due to sleep(0.01)
    assert execution_time < 1000  # Shouldn't take more than 1 second


def test_handles_logger_exception():
    """When the logger fails, it doesn't affect the property access"""

    def failing_logger(*args, **kwargs):
        raise Exception("Logger failed")

    test_obj = SampleClass(42)
    logged_prop = property(
        create_logged_property(
            test_obj.__class__.sample_property,
            "sample_property",
            failing_logger,
        )
    )

    type(test_obj).sample_property = logged_prop  # type: ignore
    result = test_obj.sample_property
    assert result == 42  # Should still return the value even if logging fails


def test_preserves_property_error():
    """When the property errors, it preserves the error and logs it"""

    class ErrorClass:
        @property
        def error_property(self):
            raise ValueError("Property error")

    mock_logger = Mock()
    test_obj = ErrorClass()
    logged_prop = property(
        create_logged_property(
            test_obj.__class__.error_property,
            "error_property",
            mock_logger,
        )
    )

    type(test_obj).error_property = logged_prop  # type: ignore

    with pytest.raises(ValueError, match="Property error"):
        _ = test_obj.error_property

    # Verify error was logged
    assert mock_logger.call_args[1]["error"] == "Property error"


def test_multiple_calls_logged():
    """When the property is called multiple times, it logs each call separately"""
    mock_logger = Mock()
    test_obj = SampleClass(42)
    logged_prop = property(
        create_logged_property(
            test_obj.__class__.sample_property,
            "sample_property",
            mock_logger,
        )
    )

    type(test_obj).sample_property = logged_prop  # type: ignore

    _ = test_obj.sample_property
    _ = test_obj.sample_property
    _ = test_obj.sample_property

    assert mock_logger.call_count == 3
