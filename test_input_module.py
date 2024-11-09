from unittest.mock import patch, MagicMock
from prodwatch.prodwatch import handle_ipc
import os


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

        # Check if the original calculate_sum was replaced
        assert calculate_sum.__name__ == "logged_function"

        # Call the new calculate_sum and check if it logs
        with patch("builtins.input", return_value="test input"):
            calculate_sum(2, 3)

        # Verify the log file contents
        assert log_file.exists()
        log_contents = log_file.read_text()
        assert (
            'Function test_input_module.calculate_sum called with args: (2, 3), kwargs: {}, result: 5\n'
            in log_contents
        )


def test_handle_ipc_inject_nonexistent_function():
    mock_conn = MagicMock()
    mock_conn.recv.side_effect = [b"INJECT:nonexistent_function", b"STOP"]

    handle_ipc(mock_conn)

    mock_conn.send.assert_called_with(b"FUNCTION_NOT_FOUND")
