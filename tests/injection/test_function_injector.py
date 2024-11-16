import pytest
from unittest.mock import patch, MagicMock, mock_open

from prodwatch.injection.function_injector import FunctionWatcher


class TestFunctionWatcher:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.watcher = FunctionWatcher()
        return self.watcher

    def test_watch_function_success(self):
        mock_module = MagicMock()
        mock_function = MagicMock()

        with patch("prodwatch.injection.function_injector.find_function") as mock_find:
            mock_find.return_value = (mock_module, mock_function)

            result = self.watcher.watch_function("test_function")

            assert result is True
            assert hasattr(mock_module, "test_function")

    def test_watch_function_not_found(self):
        with patch("prodwatch.injection.function_injector.find_function") as mock_find:
            mock_find.return_value = (None, None)

            result = self.watcher.watch_function("nonexistent_function")

            assert result is False

    def test_logged_function_writes_to_file(self):
        mock_module = MagicMock(__name__="test_module")
        mock_function = MagicMock(return_value="test_result")
        mock_file = mock_open()

        with patch("prodwatch.injection.function_injector.find_function") as mock_find, patch(
            "builtins.open", mock_file
        ):
            mock_find.return_value = (mock_module, mock_function)

            self.watcher.watch_function("test_function")

            wrapped_function = getattr(mock_module, "test_function")
            wrapped_function("arg1", kwarg1="value1")

            mock_file().write.assert_called_once()
            written_log = mock_file().write.call_args[0][0]
            assert "test_module.test_function" in written_log
            assert "arg1" in written_log
            assert "kwarg1" in written_log
            assert "test_result" in written_log
