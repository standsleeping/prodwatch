import json
from types import ModuleType
from prodwatch.manager.finders.finder_result import FinderResult, FunctionType


def create_mock_module(
    name: str = "test_module",
    file_path: str = "/path/to/test_module.py",
) -> ModuleType:
    """Create a mock module for testing."""
    module = ModuleType(name)
    module.__file__ = file_path
    return module


def create_mock_module_no_file(name: str = "builtin_module") -> ModuleType:
    """Create a mock module without __file__ attribute."""
    module = ModuleType(name)
    # Don't set __file__ to simulate builtin modules
    return module


class MockClass:
    """Mock class for testing."""

    __name__ = "MockClass"
    __qualname__ = "MockClass"

    def method(self):
        pass

    @property
    def prop(self):
        return 42


def mock_function():
    """Mock function for testing."""
    pass


mock_function.__qualname__ = "mock_function"


class TestFinderResultSerialization:
    def test_to_dict_successful_regular_function(self):
        """Serialize a successfully found regular function."""
        result = FinderResult(
            module=create_mock_module(),
            function=mock_function,
            function_type=FunctionType.REGULAR,
            klass=None,
            found=True,
        )

        data = result.to_dict()

        assert data["found"] is True
        assert data["function_type"] == "REGULAR"
        assert data["module_name"] == "test_module"
        assert data["module_file"] == "/path/to/test_module.py"
        assert data["function_name"] == "mock_function"
        assert data["function_qualname"] == "mock_function"
        assert data["class_name"] is None
        assert data["class_qualname"] is None
        assert data["is_property"] is False

    def test_to_dict_successful_method(self):
        """Serialize a successfully found method."""
        result = FinderResult(
            module=create_mock_module(),
            function=MockClass.method,
            function_type=FunctionType.METHOD,
            klass=MockClass,
            found=True,
        )

        data = result.to_dict()

        assert data["found"] is True
        assert data["function_type"] == "METHOD"
        assert data["module_name"] == "test_module"
        assert data["module_file"] == "/path/to/test_module.py"
        assert data["function_name"] == "method"
        assert data["function_qualname"] == "MockClass.method"
        assert data["class_name"] == "MockClass"
        assert data["class_qualname"] == "MockClass"
        assert data["is_property"] is False

    def test_to_dict_successful_property(self):
        """Serialize a successfully found property."""
        result = FinderResult(
            module=create_mock_module(),
            function=MockClass.prop,
            function_type=FunctionType.PROPERTY,
            klass=MockClass,
            found=True,
        )

        data = result.to_dict()

        assert data["found"] is True
        assert data["function_type"] == "PROPERTY"
        assert data["module_name"] == "test_module"
        assert data["module_file"] == "/path/to/test_module.py"
        assert data["function_name"] == "prop"  # Properties do have __name__
        assert data["function_qualname"] is None  # Properties don't have __qualname__
        assert data["class_name"] == "MockClass"
        assert data["class_qualname"] == "MockClass"
        assert data["is_property"] is True

    def test_to_dict_failed_discovery(self):
        """Serialize a failed function discovery."""
        result = FinderResult.not_found()

        data = result.to_dict()

        assert data["found"] is False
        assert data["function_type"] == "REGULAR"
        assert data["module_name"] is None
        assert data["module_file"] is None
        assert data["function_name"] is None
        assert data["function_qualname"] is None
        assert data["class_name"] is None
        assert data["class_qualname"] is None
        assert data["is_property"] is False

    def test_to_dict_module_without_file(self):
        """Serialize when module has no __file__ attribute."""

        result = FinderResult(
            module=create_mock_module_no_file(),
            function=mock_function,
            function_type=FunctionType.REGULAR,
            klass=None,
            found=True,
        )

        data = result.to_dict()

        assert data["module_name"] == "builtin_module"
        assert data["module_file"] is None

    def test_to_dict_function_without_qualname(self):
        """Serialize when function has no __qualname__ attribute."""

        class MockFunctionNoQualname:
            __name__ = "mock_func"
            # Intentionally no __qualname__

            def __call__(self):
                pass

        func_no_qualname = MockFunctionNoQualname()

        result = FinderResult(
            module=create_mock_module(),
            function=func_no_qualname,
            function_type=FunctionType.REGULAR,
            klass=None,
            found=True,
        )

        data = result.to_dict()

        assert data["function_name"] == "mock_func"
        assert data["function_qualname"] is None

    def test_to_dict_class_without_qualname(self):
        """Serialize when class has no __qualname__ attribute."""

        class MockClassNoQualname:
            __name__ = "MockClassNoQualname"
            # Intentionally no __qualname__

            def method(self):
                pass

        result = FinderResult(
            module=create_mock_module(),
            function=MockClassNoQualname.method,
            function_type=FunctionType.METHOD,
            klass=MockClassNoQualname,
            found=True,
        )

        data = result.to_dict()

        assert data["class_name"] == "MockClassNoQualname"
        # Python automatically assigns __qualname__ to classes, so it won't be None
        assert data["class_qualname"] is not None

    def test_to_dict_json_serializable(self):
        """Ensure the returned dict is JSON serializable."""
        result = FinderResult(
            module=create_mock_module(),
            function=mock_function,
            function_type=FunctionType.REGULAR,
            klass=None,
            found=True,
        )

        data = result.to_dict()

        # Should not raise an exception
        json_str = json.dumps(data)
        # Should be able to parse it back
        parsed = json.loads(json_str)

        assert parsed["found"] is True
        assert parsed["function_type"] == "REGULAR"
        assert parsed["module_name"] == "test_module"

    def test_to_dict_real_module_function(self):
        """Test with a real module and function."""
        import os

        result = FinderResult(
            module=os,
            function=os.getcwd,
            function_type=FunctionType.REGULAR,
            klass=None,
            found=True,
        )

        data = result.to_dict()

        assert data["found"] is True
        assert data["function_type"] == "REGULAR"
        assert data["module_name"] == "os"
        assert data["module_file"] is not None  # Should have a file path
        assert data["function_name"] == "getcwd"
        assert data["function_qualname"] == "getcwd"
        assert data["class_name"] is None
        assert data["class_qualname"] is None
        assert data["is_property"] is False
