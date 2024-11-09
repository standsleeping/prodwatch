from unittest.mock import MagicMock
import sys
import os
import types
from prodwatch.prodwatch import handle_ipc


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
    expected_log = 'Function dummy_module.sample_function called with args: (5,), kwargs: {}, result: 10\n'
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
