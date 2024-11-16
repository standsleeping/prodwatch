import pytest
import threading
from unittest.mock import Mock, patch
from requests.exceptions import RequestException
from prodwatch.polling.server import ServerPoller


class TestServerPollerInitialization:
    @pytest.fixture
    def server_poller(self):
        return ServerPoller("http://test-server.com", poll_interval=0.1)

    def test_initialization(self, server_poller):
        """Test proper initialization of ServerPoller attributes."""
        assert server_poller.server_url == "http://test-server.com"
        assert server_poller.poll_interval == 0.1
        assert server_poller.polling_thread is None
        assert server_poller.active is False


class TestServerPollerConnection:
    """Tests for server connection functionality."""
    
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


class TestServerPollerInjections:
    """Tests for injection-related functionality."""

    @pytest.fixture
    def server_poller(self):
        return ServerPoller("http://test-server.com", poll_interval=0.1)

    @patch("requests.get")
    def test_get_pending_injections_success(self, mock_get, server_poller):
        """Test successful retrieval of pending injections."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"function_names": ["func1", "func2"]}
        mock_get.return_value = mock_response

        result = server_poller._get_pending_injections()

        assert result == ["func1", "func2"]
        mock_get.assert_called_once_with("http://test-server.com/pending-injections")

    @patch("requests.get")
    def test_get_pending_injections_error(self, mock_get, server_poller):
        """Test error handling when retrieving pending injections."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = server_poller._get_pending_injections()

        assert result == []
        mock_get.assert_called_once_with("http://test-server.com/pending-injections")

    @patch("requests.post")
    def test_report_injection_success(self, mock_post, server_poller):
        """Test successful reporting of injection status."""
        server_poller._report_injection_success("test_function")

        mock_post.assert_called_once_with(
            "http://test-server.com/injection-status",
            json={
                "function_name": "test_function",
                "status": "success",
            },
        )

    def test_process_pending_injections(self, server_poller):
        """Test processing of multiple pending injections."""
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


class TestServerPollerLifecycle:
    """Tests for ServerPoller lifecycle management."""

    @pytest.fixture
    def server_poller(self):
        return ServerPoller("http://test-server.com", poll_interval=0.1)

    def test_start_stop(self):
        """Test starting and stopping the poller."""
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
    def test_polling_loop_with_exception(self, mock_get, server_poller):
        """Test error handling in polling loop."""
        mock_get.side_effect = Exception("Test error")

        def stop_after_call(*args):
            server_poller.active = False

        with patch("time.sleep", side_effect=stop_after_call):
            with patch("builtins.print") as mock_print:
                server_poller.active = True
                server_poller._polling_loop()

                mock_print.assert_called_once_with("Error polling server: Test error")