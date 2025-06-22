import os
import pytest
from unittest.mock import patch
from prodwatch.exceptions import TokenError
from prodwatch.manager import Manager


class TestTokenHandling:
    def test_missing_token(self):
        """Missing token raises appropriate error"""
        if "PRODWATCH_API_TOKEN" in os.environ:
            del os.environ["PRODWATCH_API_TOKEN"]

        with pytest.raises(TokenError) as exc_info:
            Manager("http://test-server.com")

        error_message = "PRODWATCH_API_TOKEN environment variable is required"
        assert error_message in str(exc_info.value)

    def test_empty_token(self):
        """Empty token raises error"""
        os.environ["PRODWATCH_API_TOKEN"] = ""

        with pytest.raises(TokenError) as exc_info:
            Manager("http://test-server.com")

        assert "PRODWATCH_API_TOKEN environment variable is required" in str(
            exc_info.value
        )

    def test_valid_token(self):
        """Valid token is properly set"""
        test_token = "test-token-123"
        os.environ["PRODWATCH_API_TOKEN"] = test_token

        manager = Manager("http://test-server.com")

        assert manager.token == test_token
        assert manager.session.headers["Authorization"] == f"Bearer {test_token}"

    @patch("requests.Session.post")
    def test_requests_include_token(self, mock_post):
        """Requests include the token in headers"""
        test_token = "test-token-123"
        os.environ["PRODWATCH_API_TOKEN"] = test_token

        manager = Manager("http://test-server.com")
        manager.confirm_watcher("test_function")

        # Verify the request was made
        mock_post.assert_called_once()
        # Check that the session headers contain the Authorization token
        assert manager.session.headers["Authorization"] == f"Bearer {test_token}"

    @patch("requests.Session.get")
    def test_get_requests_include_token(self, mock_get):
        """GET requests include the token in headers"""
        test_token = "test-token-123"
        os.environ["PRODWATCH_API_TOKEN"] = test_token

        manager = Manager("http://test-server.com")
        manager.get_pending_function_names()

        # Verify the request was made
        mock_get.assert_called_once()
        # Check that the session headers contain the Authorization token
        assert manager.session.headers["Authorization"] == f"Bearer {test_token}"
