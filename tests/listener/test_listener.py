import pytest
import threading
from unittest.mock import Mock, patch
from requests.exceptions import RequestException
from prodwatch.listener import Listener


class TestListenerInitialization:
    @pytest.fixture
    def listener(self):
        return Listener("http://test-server.com", poll_interval=0.1)

    def test_initialization(self, listener):
        """Test proper initialization of Listener attributes."""
        assert listener.base_listening_url == "http://test-server.com"
        assert listener.poll_interval == 0.1
        assert listener.polling_thread is None
        assert listener.active is False


class TestListenerConnection:
    """Tests for server connection functionality."""

    def test_check_connection_success(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            listener = Listener("http://test-url")
            assert listener.check_connection() is True

    def test_check_connection_failure_connection_error(self):
        with patch("requests.post") as mock_post:
            mock_post.side_effect = RequestException("Connection refused")
            listener = Listener("http://test-url")
            assert listener.check_connection() is False


class TestListenerWatchRequests:
    """Tests for watch request-related functionality."""

    @pytest.fixture
    def listener(self):
        return Listener("http://test-server.com", poll_interval=0.1)

    @patch("requests.get")
    def test_get_pending_watchers_success(self, mock_get, listener):
        """Test successful retrieval of pending watch requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"function_names": ["func1", "func2"]}
        mock_get.return_value = mock_response

        result = listener._get_pending_watchers()

        assert result == ["func1", "func2"]
        mock_get.assert_called_once_with("http://test-server.com/pending-function-names")

    @patch("requests.get")
    def test_get_pending_watchers_error(self, mock_get, listener):
        """Test error handling when retrieving pending watch requests."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = listener._get_pending_watchers()

        assert result == []
        mock_get.assert_called_once_with("http://test-server.com/pending-function-names")

    @patch("requests.post")
    def test_confirm_watcher(self, mock_post, listener):
        """Test successful reporting of watch request status."""
        listener._confirm_watcher("test_function")

        mock_post.assert_called_once_with(
            "http://test-server.com/confirm-watcher",
            json={
                "function_name": "test_function",
                "status": "success",
            },
        )

    def test_process_pending_watchers(self, listener):
        """Test processing of multiple pending watch requests."""
        listener.watcher.watch_function = Mock(return_value=True)
        listener._confirm_watcher = Mock()

        function_names = ["func1", "func2"]
        listener._process_pending_watchers(function_names)

        assert listener.watcher.watch_function.call_count == 2
        assert listener._confirm_watcher.call_count == 2

        listener.watcher.watch_function.assert_any_call("func1")
        listener.watcher.watch_function.assert_any_call("func2")
        listener._confirm_watcher.assert_any_call("func1")
        listener._confirm_watcher.assert_any_call("func2")


class TestListenerLifecycle:
    """Tests for Listener lifecycle management."""

    @pytest.fixture
    def listener(self):
        return Listener("http://test-server.com", poll_interval=0.1)

    def test_start_stop(self):
        """Test starting and stopping the listener."""
        listener = Listener("http://test-server.com", poll_interval=0.1)

        listener.start()
        assert listener.active is True
        assert isinstance(listener.polling_thread, threading.Thread)
        assert listener.polling_thread.is_alive()

        # Starting again shouldn't create new thread
        original_thread = listener.polling_thread
        listener.start()
        assert listener.polling_thread is original_thread

        listener.stop()
        assert listener.active is False
        assert not listener.polling_thread.is_alive()

        # Stopping again shouldn't raise error
        listener.stop()
        assert listener.active is False

    @patch("requests.get")
    def test_polling_loop_with_exception(self, mock_get, listener):
        """Test error handling in polling loop."""
        mock_get.side_effect = Exception("Test error")

        def stop_after_call(*args):
            listener.active = False

        with patch("time.sleep", side_effect=stop_after_call):
            # TEST that self.logger.error(f"Error polling Prodwatch server: {e}")
            with patch("logging.Logger.error") as mock_error:
                listener.active = True
                listener._polling_loop()
                error_message = "Error polling Prodwatch server: Test error"
                mock_error.assert_called_once_with(error_message)
