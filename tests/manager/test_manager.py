from unittest.mock import Mock, patch
from requests.exceptions import RequestException
from prodwatch.manager.finders.finder_result import FinderResult, FunctionType


class TestManagerInitialization:
    """Tests for Manager initialization."""

    def test_initialization(self, manager):
        """Manager attributes are initialized correctly."""
        assert manager.base_server_url == "http://test-server.com"
        assert manager.poll_interval == 1
        assert manager.polling_thread is None
        assert manager.active is False


class TestManagerConnection:
    """Server connection is established correctly."""

    def test_check_connection_success(self, manager):
        with patch("requests.Session.post") as mock_post:
            mock_post.return_value.status_code = 200
            assert manager.check_connection() is True

    def test_check_connection_failure_connection_error(self, manager):
        with patch("requests.Session.post") as mock_post:
            mock_post.side_effect = RequestException("Connection refused")
            assert manager.check_connection() is False


class TestManagerWatchRequests:
    """Watch requests are processed correctly."""

    @patch("requests.Session.get")
    def test_get_pending_function_names_success(self, mock_get, manager):
        """Pending watch requests are retrieved successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"function_names": ["func1", "func2"]}
        mock_get.return_value = mock_response

        result = manager.get_pending_function_names()

        assert result == ["func1", "func2"]

        mock_get.assert_called_once_with(
            f"{manager.base_server_url}/pending-function-names",
            params={"process_id": str(manager.process_id), "app_name": "test-app"},
            allow_redirects=False,
        )

    def test_skip_already_watched_functions(self, manager):
        """Already watched functions are skipped."""
        # Add a function to watched set
        manager.watched_functions.add("already_watched_func")

        # Create list with both new and already watched functions
        functions_to_watch = ["already_watched_func", "new_func"]

        with patch.object(manager.function_manager, "watch_function") as mock_watch:
            # Make watch_function return (True, FinderResult) to simulate successful watching
            mock_result = FinderResult(
                module=None,
                function=None,
                function_type=FunctionType.REGULAR,
                found=True,
            )

            mock_watch.return_value = (True, mock_result)

            # Process the functions
            manager.process_pending_watchers(functions_to_watch)

            # Verify watch_function was only called for new_func
            mock_watch.assert_called_once_with("new_func")

            # Verify both functions are now in watched set
            assert "already_watched_func" in manager.watched_functions
            assert "new_func" in manager.watched_functions

    def test_only_successful_watches_are_tracked(self, manager):
        """Only successfully watched functions are added to watched set."""
        functions_to_watch = ["success_func", "fail_func"]

        def mock_watch_function(func_name):
            # Simulate success only for success_func
            success = func_name == "success_func"
            mock_result = FinderResult(
                module=None,
                function=None,
                function_type=FunctionType.REGULAR,
                found=success,
            )
            return (success, mock_result)

        with patch.object(manager.function_manager, "watch_function") as mock_watch:
            mock_watch.side_effect = mock_watch_function

            # Process the functions
            manager.process_pending_watchers(functions_to_watch)

            # Verify only successful function is in watched set
            assert "success_func" in manager.watched_functions
            assert "fail_func" not in manager.watched_functions

            # Verify watch_function was called for both functions
            assert mock_watch.call_count == 2

    def test_confirm_watcher_only_called_for_new_watches(self, manager):
        """confirm_watcher is only called for newly watched functions."""
        # Add a function to watched set
        manager.watched_functions.add("already_watched_func")

        functions_to_watch = ["already_watched_func", "new_func"]

        with (
            patch.object(manager.function_manager, "watch_function") as mock_watch,
            patch.object(manager, "confirm_watcher") as mock_confirm,
        ):
            mock_result = FinderResult(
                module=None,
                function=None,
                function_type=FunctionType.REGULAR,
                found=True,
            )
            mock_watch.return_value = (True, mock_result)

            # Process the functions
            manager.process_pending_watchers(functions_to_watch)

            # Verify confirm_watcher was only called for new_func
            # Note: confirm_watcher now takes finder_result.to_dict() as second parameter
            assert mock_confirm.call_count == 1
            call_args = mock_confirm.call_args[0]
            assert call_args[0] == "new_func"

    @patch("requests.Session.get")
    def test_get_pending_function_names_error(self, mock_get, manager):
        """Error handling when retrieving pending watch requests."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = manager.get_pending_function_names()

        assert result == []

        mock_get.assert_called_once_with(
            f"{manager.base_server_url}/pending-function-names",
            params={"process_id": str(manager.process_id), "app_name": "test-app"},
            allow_redirects=False,
        )

    @patch("requests.Session.post")
    def test_confirm_watcher(self, mock_post, manager):
        """Watch request is confirmed correctly."""
        manager.confirm_watcher("test_function")

        mock_post.assert_called_once_with(
            "http://test-server.com/events",
            json={
                "event_name": "confirm-watcher",
                "function_name": "test_function",
                "process_id": str(manager.process_id),
                "app_name": "test-app",
            },
            allow_redirects=False,
        )

    @patch("requests.Session.get")
    def test_process_pending_watchers(self, mock_get, manager):
        """Pending watch requests are processed correctly."""
        mock_result = FinderResult(
            module=None,
            function=None,
            function_type=FunctionType.REGULAR,
            found=True,
        )

        manager.function_manager.watch_function = Mock(return_value=(True, mock_result))
        manager.confirm_watcher = Mock()

        function_names = ["func1", "func2"]
        manager.process_pending_watchers(function_names)

        assert manager.function_manager.watch_function.call_count == 2
        assert manager.confirm_watcher.call_count == 2

        manager.function_manager.watch_function.assert_any_call("func1")
        manager.function_manager.watch_function.assert_any_call("func2")

        # Note: confirm_watcher now takes finder_result.to_dict() as second parameter
        assert manager.confirm_watcher.call_count == 2

    @patch("requests.Session.get")
    def test_polling_loop_with_exception(self, mock_get, manager):
        """Errors are logged in polling loop."""
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

    def test_failed_watcher_reports_failure(self, manager):
        """Failed watcher reports failure correctly."""
        with patch("requests.Session.post") as mock_post:
            mock_post.return_value.status_code = 200

            manager.failed_watcher("test_function")

            mock_post.assert_called_once_with(
                f"{manager.base_server_url}/events",
                json={
                    "event_name": "failed-watcher",
                    "function_name": "test_function",
                    "process_id": str(manager.process_id),
                    "app_name": "test-app",
                },
                allow_redirects=False,
            )

    def test_failed_watcher_handles_errors(self, manager):
        """Failed watcher handles errors correctly."""
        with patch("requests.Session.post") as mock_post:
            mock_post.return_value.status_code = 500

            with patch.object(manager, "handle_error") as mock_handle_error:
                manager.failed_watcher("test_function")

                mock_handle_error.assert_called_once()
