from prodwatch.manager.finders.find_class_method import find_class_method
from prodwatch.manager.finders.finder_result import FunctionType


class TestClass:
    def regular_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

    @property
    def some_property(self):
        return 42


def test_find_regular_method():
    """Finds a regular method"""
    result = find_class_method("TestClass.regular_method")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_class_method"
    assert result.klass == TestClass
    assert result.function.__name__ == "regular_method"
    assert result.function_type == FunctionType.METHOD


def test_find_class_method():
    """Finds a class method"""
    result = find_class_method("TestClass.class_method")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_class_method"
    assert result.klass == TestClass
    assert result.function.__name__ == "class_method"
    assert result.function_type == FunctionType.METHOD


def test_find_static_method():
    """Finds a static method"""
    result = find_class_method("TestClass.static_method")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_class_method"
    assert result.klass == TestClass
    assert result.function.__name__ == "static_method"
    assert result.function_type == FunctionType.METHOD


def test_find_property():
    """Finds a property"""
    result = find_class_method("TestClass.some_property")
    assert result.found
    assert result.module.__name__ == "tests.manager.finders.test_find_class_method"
    assert result.klass == TestClass
    assert isinstance(result.function, property)
    assert result.function_type == FunctionType.PROPERTY


def test_invalid_method_name_format():
    """With no dot, it's not a class method"""
    result = find_class_method("invalid_format")
    assert not result.found
    assert result.module is None
    assert result.klass is None
    assert result.function is None


def test_method_not_found():
    """When the method is not found, it returns not found"""
    result = find_class_method("TestClass.nonexistent_method")
    assert not result.found
    assert result.module is None
    assert result.klass is None
    assert result.function is None
