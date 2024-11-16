import pytest
from unittest.mock import Mock, patch
import threading
from prodwatch.polling.server import ServerPoller
from requests.exceptions import RequestException


@pytest.fixture
def server_poller():
    return ServerPoller("http://test-server.com", poll_interval=0.1)


def test_server_poller_init(server_poller):
    assert server_poller.server_url == "http://test-server.com"
    assert server_poller.poll_interval == 0.1
    assert server_poller.polling_thread is None
    assert server_poller.active is False


@patch("requests.get")
def test_get_pending_injections_success(mock_get, server_poller):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"function_names": ["func1", "func2"]}
    mock_get.return_value = mock_response

    result = server_poller._get_pending_injections()

    assert result == ["func1", "func2"]
    mock_get.assert_called_once_with("http://test-server.com/pending-injections")


@patch("requests.get")
def test_get_pending_injections_error(mock_get, server_poller):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = server_poller._get_pending_injections()

    assert result == []
    mock_get.assert_called_once_with("http://test-server.com/pending-injections")


@patch("requests.post")
def test_report_injection_success(mock_post, server_poller):
    server_poller._report_injection_success("test_function")

    mock_post.assert_called_once_with(
        "http://test-server.com/injection-status",
        json={
            "function_name": "test_function",
            "status": "success",
        },
    )


def test_process_pending_injections(server_poller):
    server_poller.injector.inject_function = Mock(return_value=True)
    server_poller._report_injection_success = Mock()

    function_names = ["func1", "func2"]
    server_poller._process_pending_injections(function_names)

    assert server_poller.injector.inject_function.call_count == 2
    assert server_poller._report_injection_success.call_count == 2

    server_poller.injector.inject_function.assert_any_call("func1")
    server_poller.injector.inject_function.assert_any_call("func2")
    server_poller._report_injection_success.assert_any_call("func1")
    server_poller._report_injection_success.assert_any_call("func2")


def test_start_stop():
    poller = ServerPoller("http://test-server.com", poll_interval=0.1)

    poller.start()
    assert poller.active is True
    assert isinstance(poller.polling_thread, threading.Thread)
    assert poller.polling_thread.is_alive()

    # Starting again shouldn't create new thread
    original_thread = poller.polling_thread
    poller.start()
    assert poller.polling_thread is original_thread

    poller.stop()
    assert poller.active is False
    assert not poller.polling_thread.is_alive()

    # Stopping again shouldn't raise error
    poller.stop()
    assert poller.active is False


@patch("requests.get")
def test_polling_loop_with_exception(mock_get, server_poller):
    mock_get.side_effect = Exception("Test error")

    def stop_after_call(*args):
        server_poller.active = False

    with patch("time.sleep", side_effect=stop_after_call):
        with patch("builtins.print") as mock_print:
            server_poller.active = True
            server_poller._polling_loop()

            mock_print.assert_called_once_with("Error polling server: Test error")


class TestServerPoller:
    def test_check_connection_success(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            poller = ServerPoller("http://test-url")
            assert poller.check_connection() is True

    def test_check_connection_failure_404(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = RequestException("404 Client Error")
            poller = ServerPoller("http://test-url")
            assert poller.check_connection() is False

    def test_check_connection_failure_connection_error(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = RequestException("Connection refused")
            poller = ServerPoller("http://test-url")
            assert poller.check_connection() is False
