import pytest
import threading
from unittest.mock import Mock, patch
from requests.exceptions import RequestException
from prodwatch.manager import Manager


class TestManagerInitialization:
    @pytest.fixture
    def manager(self):
        return Manager("http://test-server.com", poll_interval=0.1)

    def test_initialization(self, manager):
        """Test proper initialization of Manager attributes."""
        assert manager.base_server_url == "http://test-server.com"
        assert manager.poll_interval == 0.1
        assert manager.polling_thread is None
        assert manager.active is False


class TestManagerConnection:
    """Tests for server connection functionality."""

    def test_check_connection_success(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            manager = Manager("http://test-url")
            assert manager.check_connection() is True

    def test_check_connection_failure_connection_error(self):
        with patch("requests.post") as mock_post:
            mock_post.side_effect = RequestException("Connection refused")
            manager = Manager("http://test-url")
            assert manager.check_connection() is False


class TestManagerWatchRequests:
    """Tests for watch request-related functionality."""

    @pytest.fixture
    def manager(self):
        return Manager("http://test-server.com", poll_interval=0.1)

    @patch("requests.get")
    def test_get_pending_function_names_success(self, mock_get, manager):
        """Test successful retrieval of pending watch requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"function_names": ["func1", "func2"]}
        mock_get.return_value = mock_response

        result = manager.get_pending_function_names()

        assert result == ["func1", "func2"]
        mock_get.assert_called_once_with("http://test-server.com/pending-function-names")

    @patch("requests.get")
    def test_get_pending_function_names_error(self, mock_get, manager):
        """Test error handling when retrieving pending watch requests."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = manager.get_pending_function_names()

        assert result == []
        mock_get.assert_called_once_with("http://test-server.com/pending-function-names")

    @patch("requests.post")
    def test_confirm_watcher(self, mock_post, manager):
        """Test successful reporting of watch request status."""
        manager.confirm_watcher("test_function")

        mock_post.assert_called_once_with(
            "http://test-server.com/events",
            json={
                "event_name": "confirm-watcher",
                "function_name": "test_function",
            },
        )

    def test_process_pending_watchers(self, manager):
        """Test processing of multiple pending watch requests."""
        manager.function_manager.watch_function = Mock(return_value=True)
        manager.confirm_watcher = Mock()

        function_names = ["func1", "func2"]
        manager.process_pending_watchers(function_names)

        assert manager.function_manager.watch_function.call_count == 2
        assert manager.confirm_watcher.call_count == 2

        manager.function_manager.watch_function.assert_any_call("func1")
        manager.function_manager.watch_function.assert_any_call("func2")
        manager.confirm_watcher.assert_any_call("func1")
        manager.confirm_watcher.assert_any_call("func2")


class TestManagerLifecycle:
    """Tests for Manager lifecycle management."""

    @pytest.fixture
    def manager(self):
        return Manager("http://test-server.com", poll_interval=0.1)

    def test_start_stop(self):
        """Test starting and stopping the manager."""
        manager = Manager("http://test-server.com", poll_interval=0.1)

        manager.start()
        assert manager.active is True
        assert isinstance(manager.polling_thread, threading.Thread)
        assert manager.polling_thread.is_alive()

        # Starting again shouldn't create new thread
        original_thread = manager.polling_thread
        manager.start()
        assert manager.polling_thread is original_thread

        manager.stop()
        assert manager.active is False
        assert not manager.polling_thread.is_alive()

        # Stopping again shouldn't raise error
        manager.stop()
        assert manager.active is False

    @patch("requests.get")
    def test_polling_loop_with_exception(self, mock_get, manager):
        """Test error handling in polling loop."""
        mock_get.side_effect = Exception("Test error")

        def stop_after_call(*args):
            manager.active = False

        with patch("time.sleep", side_effect=stop_after_call):
            # TEST that self.logger.error(f"Error polling Prodwatch server: {e}")
            with patch("logging.Logger.error") as mock_error:
                manager.active = True
                manager.polling_loop()
                error_message = "Error polling Prodwatch server: Test error"
                mock_error.assert_called_once_with(error_message)
