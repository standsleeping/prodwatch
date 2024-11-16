import pytest
from unittest.mock import patch, MagicMock
from request_injection import watch_function


@pytest.fixture
def mock_socket():
    with patch("request_injection.socket.socket") as mock:
        yield mock


def test_watch_function_success(mock_socket):
    mock_client = MagicMock()
    mock_socket.return_value = mock_client
    mock_client.recv.return_value = b"SUCCESS"

    with patch("builtins.print") as mock_print:
        watch_function("test_function")

    mock_client.connect.assert_called_once_with("/tmp/prd_watch_socket")
    mock_client.send.assert_called_once_with(b"INJECT:test_function")
    mock_client.recv.assert_called_once_with(1024)
    mock_client.close.assert_called_once()
    mock_print.assert_called_once_with("Received response: SUCCESS")


def test_watch_function_function_not_found(mock_socket):
    mock_client = MagicMock()
    mock_socket.return_value = mock_client
    mock_client.recv.return_value = b"FUNCTION_NOT_FOUND"

    with patch("builtins.print") as mock_print:
        watch_function("nonexistent_function")

    mock_client.connect.assert_called_once_with("/tmp/prd_watch_socket")
    mock_client.send.assert_called_once_with(b"INJECT:nonexistent_function")
    mock_client.recv.assert_called_once_with(1024)
    mock_client.close.assert_called_once()
    mock_print.assert_called_once_with("Received response: FUNCTION_NOT_FOUND")


def test_watch_function_connection_error(mock_socket):
    mock_client = MagicMock()
    mock_socket.return_value = mock_client
    mock_client.connect.side_effect = Exception("Connection failed")

    with patch("builtins.print") as mock_print:
        watch_function("test_function")

    mock_client.connect.assert_called_once_with("/tmp/prd_watch_socket")
    mock_client.send.assert_not_called()
    mock_client.recv.assert_not_called()
    mock_client.close.assert_called_once()
    mock_print.assert_called_once_with("Error in watch_function: Connection failed")
