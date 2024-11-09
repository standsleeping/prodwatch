import os
import sys
import types
from unittest.mock import patch, MagicMock
from prodwatch.ipc.server import (
    handle_ipc,
)

from prodwatch.module_loader.loader import add_project_to_path
from prodwatch.injection.function_injector import find_function


def test_inject_existing_function(tmp_path):
    conn = MagicMock()
    conn.recv.side_effect = [b"INJECT:sample_function", b"STOP"]

    # Create dummy module and function
    dummy_module = types.ModuleType("dummy_module")

    def sample_function(x):
        return x * 2

    dummy_module.sample_function = sample_function

    # Add dummy module to sys.modules
    sys.modules["dummy_module"] = dummy_module

    # Set the APP_LOG_FILE environment variable to a temporary file
    log_file = tmp_path / "log_file.txt"
    os.environ["APP_LOG_FILE"] = str(log_file)

    handle_ipc(conn)

    conn.send.assert_called_with(b"SUCCESS")
    assert dummy_module.sample_function != sample_function

    # Call the injected function
    result = dummy_module.sample_function(5)
    assert result == 10

    # Check the log file content
    with open(log_file, "r") as f:
        log_content = f.read()
    expected_log = "Function dummy_module.sample_function called with args: (5,), kwargs: {}, result: 10\n"
    assert expected_log == log_content

    # Delete the dummy module and log file
    del sys.modules["dummy_module"]
    del os.environ["APP_LOG_FILE"]


def test_inject_nonexistent_function():
    conn = MagicMock()
    conn.recv.side_effect = [b"INJECT:nonexistent_function", b"STOP"]
    handle_ipc(conn)
    conn.send.assert_called_with(b"FUNCTION_NOT_FOUND")


def test_handle_ipc_stop_command():
    conn = MagicMock()
    conn.recv.return_value = b"STOP"
    handle_ipc(conn)
    conn.close.assert_called_once()


def test_handle_ipc_malformed_data():
    conn = MagicMock()
    conn.recv.side_effect = [b"", b"STOP"]
    handle_ipc(conn)
    conn.close.assert_called_once()


def test_find_function_existing():
    def sample_function():
        pass

    dummy_module = types.ModuleType("dummy_module")
    dummy_module.sample_function = sample_function
    sys.modules["dummy_module"] = dummy_module

    module, func = find_function("sample_function")

    assert module == dummy_module
    assert func == sample_function

    del sys.modules["dummy_module"]


def test_find_function_nonexistent():
    function_name = "nonexistent_function"
    module, func = find_function(function_name)
    assert module is None
    assert func is None


def test_add_project_to_path(tmp_path):
    project_root = str(tmp_path)
    original_sys_path = sys.path.copy()

    with patch("os.getcwd", return_value=project_root):
        add_project_to_path()

    assert sys.path[0] == project_root

    sys.path = original_sys_path


def calculate_sum(a, b):
    result = int(a) + int(b)
    print(f"{a} + {b} = {result}")
    return result


def test_handle_ipc_inject(tmp_path):
    mock_conn = MagicMock()
    mock_conn.recv.side_effect = [b"INJECT:calculate_sum", b"STOP"]

    log_file = tmp_path / "log_file.txt"

    with patch.dict(os.environ, {"APP_LOG_FILE": str(log_file)}):
        handle_ipc(mock_conn)

        # Call the new calculate_sum and check if it logs
        with patch("builtins.input", return_value="test input"):
            calculate_sum(2, 3)

        # Check if the original calculate_sum was replaced
        assert calculate_sum.__name__ == "logged_function"

        # Verify the log file contents
        assert log_file.exists()
        log_contents = log_file.read_text()
        assert (
            "Function tests.ipc.test_server.calculate_sum called with args: (2, 3), kwargs: {}, result: 5\n"
            in log_contents
        )


def test_handle_ipc_inject_nonexistent_function():
    mock_conn = MagicMock()
    mock_conn.recv.side_effect = [b"INJECT:nonexistent_function", b"STOP"]

    handle_ipc(mock_conn)

    mock_conn.send.assert_called_with(b"FUNCTION_NOT_FOUND")
