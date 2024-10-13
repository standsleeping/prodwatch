import pytest
from unittest.mock import patch, MagicMock
import input_module
import os


@pytest.fixture
def mock_socket():
    with patch("input_module.socket.socket") as mock:
        yield mock


def test_get_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "test input")
    with patch("builtins.print") as mock_print:
        result = input_module.get_user_input()
    assert result == "test input"
    mock_print.assert_called_once_with("You entered: test input")


def test_calculate_sum():
    with patch("builtins.print") as mock_print:
        result = input_module.calculate_sum(2, 3)
    assert result == 5
    mock_print.assert_called_once_with("2 + 3 = 5")


def test_handle_ipc_inject(tmp_path):
    mock_conn = MagicMock()
    mock_conn.recv.side_effect = [b"INJECT:get_user_input", b"STOP"]

    log_file = tmp_path / "log_file.txt"

    with patch.dict(os.environ, {"APP_LOG_FILE": str(log_file)}):
        input_module.handle_ipc(mock_conn)

        # Check if the original get_user_input was replaced
        assert input_module.get_user_input.__name__ == "logged_function"

        # Call the new get_user_input and check if it logs
        with patch("builtins.input", return_value="test input"):
            input_module.get_user_input()

        # Verify the log file contents
        assert log_file.exists()
        log_contents = log_file.read_text()
        assert (
            "Function get_user_input called with args: (), kwargs: {}, result: test input"
            in log_contents
        )


def test_handle_ipc_inject_nonexistent_function(tmp_path):
    mock_conn = MagicMock()
    mock_conn.recv.side_effect = [b"INJECT:nonexistent_function", b"STOP"]

    input_module.handle_ipc(mock_conn)

    mock_conn.send.assert_called_with(b"FUNCTION_NOT_FOUND")
