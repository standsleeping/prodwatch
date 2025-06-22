import os.path
import json
from prodwatch.manager.finders.find_module_function import find_module_function
from prodwatch.manager.finders.finder_result import FunctionType


def module_function():
    pass


def test_find_simple_module_function():
    """Finds a function in a simple module path (os.getcwd)"""
    result = find_module_function("os.getcwd")
    assert result.found
    assert result.module.__name__ == "os"
    assert result.function == os.getcwd
    assert result.function_type == FunctionType.REGULAR


def test_find_nested_module_function():
    """Finds a function in a nested module path (os.path.join)"""
    result = find_module_function("os.path.join")
    assert result.found
    assert result.module.__name__ == "posixpath"
    assert result.function == os.path.join
    assert result.function_type == FunctionType.REGULAR


def test_find_builtin_module_function():
    """Finds a function in a builtin module (json.dumps)"""
    result = find_module_function("json.dumps")
    assert result.found
    assert result.module.__name__ == "json"
    assert result.function == json.dumps
    assert result.function_type == FunctionType.REGULAR


def test_find_local_module_function():
    """Finds a function in the current module"""
    result = find_module_function(
        "tests.manager.finders.test_find_module_function.module_function"
    )
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_module_function"
    assert result.function == module_function
    assert result.function_type == FunctionType.REGULAR


def test_nonexistent_module():
    """When the module is not found, it returns not found"""
    result = find_module_function("nonexistent_module.some_function")
    assert not result.found
    assert result.module is None
    assert result.function is None


def test_nonexistent_function():
    """When the function is not found, it returns not found"""
    result = find_module_function("os.nonexistent_function")
    assert not result.found
    assert result.module is None
    assert result.function is None


def test_non_callable_attribute():
    """When the module attribute is not callable, it returns not found"""
    result = find_module_function("os.name")
    assert not result.found
    assert result.module is None
    assert result.function is None


def test_invalid_format():
    """When the format is invalid, it returns not found"""
    result = find_module_function("invalid_format")
    assert not result.found
    assert result.module is None
    assert result.function is None
