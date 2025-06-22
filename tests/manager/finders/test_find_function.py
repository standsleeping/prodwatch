from prodwatch.manager.finders.find_function import find_function
from prodwatch.manager.finders.finder_result import FunctionType


# Test fixtures
def regular_function():
    pass


class TestFindFunctionClass:
    def method(self):
        pass

    @property
    def some_property(self):
        return 42


def test_find_regular_function():
    """Finds a regular function in the current module"""
    result = find_function("regular_function")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_function"
    assert result.function == regular_function
    assert result.function_type == FunctionType.REGULAR


def test_find_module_qualified_function():
    """Finds a module-qualified function"""
    result = find_function("os.path.join")
    assert result.found
    assert result.module.__name__ == "posixpath"
    assert result.function == result.module.join
    assert result.function_type == FunctionType.REGULAR


def test_find_class_method():
    """Finds a class method"""
    result = find_function("TestFindFunctionClass.method")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_function"
    assert result.klass == TestFindFunctionClass
    assert result.function.__name__ == "method"
    assert result.function_type == FunctionType.METHOD


def test_find_class_property():
    """Finds a class property"""
    result = find_function("TestFindFunctionClass.some_property")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_function"
    assert result.klass == TestFindFunctionClass
    assert isinstance(result.function, property)
    assert result.function_type == FunctionType.PROPERTY


def test_function_not_found():
    """When function is not found, it returns not found"""
    result = find_function("nonexistent_function")
    assert not result.found
    assert result.module is None
    assert result.function is None


def test_class_method_not_found():
    """When class method is not found, it returns not found"""
    result = find_function("TestFindFunctionClass.nonexistent_method")
    assert not result.found
    assert result.module is None
    assert result.function is None


def test_invalid_module_function():
    """When module-qualified function is not found, it returns not found"""
    result = find_function("nonexistent_module.nonexistent_function")
    assert not result.found
    assert result.module is None
    assert result.function is None


def test_invalid_class_method():
    """When class method is not found, it returns not found"""
    result = find_function("TestFindFunctionClass.nonexistent_method")
    assert not result.found
    assert result.module is None
    assert result.function is None
