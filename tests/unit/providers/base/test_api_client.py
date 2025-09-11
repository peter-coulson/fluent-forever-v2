"""Unit tests for Base API Client."""

import json
from unittest.mock import Mock, patch

import pytest
from src.providers.base.api_client import APIError, APIResponse, BaseAPIClient


class MockAPIClient(BaseAPIClient):
    """Mock implementation of BaseAPIClient for testing."""

    def test_connection(self) -> bool:
        return True

    def get_service_info(self) -> dict:
        return {"service": "test"}


class TestBaseAPIClient:
    """Test cases for BaseAPIClient."""

    @pytest.fixture
    def mock_config_file(self, tmp_path):
        """Create a mock config file."""
        config = {
            "providers": {
                "base": {"user_agent": "TestAgent/1.0", "timeout": 60, "max_retries": 2}
            }
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))
        return config_path

    def test_client_creation(self, mock_config_file):
        """Test API client creation."""
        with patch.object(BaseAPIClient, "load_config") as mock_load:
            mock_load.return_value = {
                "providers": {"base": {"user_agent": "TestAgent/1.0", "timeout": 60}}
            }
            client = MockAPIClient("TestService")
            assert client.service_name == "TestService"
            assert client.timeout == 60

    def test_config_loading_shared(self, mock_config_file):
        """Test config is loaded once and shared."""
        # Clear any existing shared config to ensure clean test
        BaseAPIClient._shared_config = None

        # Load config directly using the test file
        config = BaseAPIClient.load_config(mock_config_file)
        assert config is not None

        # Create clients - they should share the already loaded config
        client1 = MockAPIClient("Service1")
        client2 = MockAPIClient("Service2")

        # Both should have same config reference (shared at class level)
        assert client1.config is client2.config
        assert BaseAPIClient._shared_config is not None

    def test_config_loading_fallback(self, tmp_path):
        """Test fallback when config file doesn't exist."""
        # Clear any existing shared config
        BaseAPIClient._shared_config = None

        # Try to load config from non-existent file
        nonexistent_file = tmp_path / "nonexistent_config.json"

        with pytest.raises(
            FileNotFoundError
        ):  # Should raise when config can't be loaded
            BaseAPIClient.load_config(nonexistent_file)

    @patch.dict("os.environ", {"TEST_API_KEY": "secret123"})
    def test_load_api_key_success(self):
        """Test successful API key loading."""
        with patch.object(BaseAPIClient, "load_config", return_value={}):
            client = MockAPIClient("TestService")
            key = client._load_api_key("TEST_API_KEY")
            assert key == "secret123"

    def test_load_api_key_missing(self):
        """Test API key loading when environment variable is missing."""
        with patch.object(BaseAPIClient, "load_config", return_value={}):
            client = MockAPIClient("TestService")
            with pytest.raises(APIError, match="Missing API key"):
                client._load_api_key("MISSING_API_KEY", allow_testing=False)

    @patch("requests.Session.request")
    def test_successful_request(self, mock_request):
        """Test successful HTTP request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.content = b'{"result": "success"}'
        mock_request.return_value = mock_response

        with patch.object(BaseAPIClient, "load_config", return_value={}):
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert response.success
        assert response.data == {"result": "success"}
        assert response.status_code == 200

    @patch("requests.Session.request")
    def test_non_json_response(self, mock_request):
        """Test handling of non-JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"binary content"
        mock_response.json.side_effect = json.JSONDecodeError("", "", 0)
        mock_request.return_value = mock_response

        with patch.object(BaseAPIClient, "load_config", return_value={}):
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert response.success
        assert response.data == b"binary content"

    @patch("requests.Session.request")
    def test_client_error_no_retry(self, mock_request):
        """Test client error (4xx) doesn't trigger retry."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad request"}
        mock_response.text = '{"error": "Bad request"}'
        mock_request.return_value = mock_response

        with patch.object(
            BaseAPIClient,
            "load_config",
            return_value={"providers": {"base": {"max_retries": 3}}},
        ):
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert not response.success
        assert "Bad request" in response.error_message
        assert response.status_code == 400
        # Should only be called once (no retries for 4xx)
        assert mock_request.call_count == 1

    @patch("requests.Session.request")
    @patch("time.sleep")  # Mock sleep to speed up test
    def test_server_error_retry(self, mock_sleep, mock_request):
        """Test server error (5xx) triggers retry."""
        # First two calls return 500, third succeeds
        mock_responses = []

        # Failed responses
        for _ in range(2):
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Server error"}
            mock_response.text = "Server error"
            mock_responses.append(mock_response)

        # Successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.content = b'{"result": "success"}'
        mock_responses.append(mock_response)

        mock_request.side_effect = mock_responses

        with patch.object(
            BaseAPIClient,
            "load_config",
            return_value={"providers": {"base": {"max_retries": 3}}},
        ):
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert response.success
        assert response.data == {"result": "success"}
        # Should be called 3 times (2 failures + 1 success)
        assert mock_request.call_count == 3

    @patch("requests.Session.request")
    @patch("time.sleep")
    def test_rate_limiting(self, mock_sleep, mock_request):
        """Test rate limiting handling."""
        # Rate limited response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "30"}
        mock_request.return_value = mock_response

        with patch.object(
            BaseAPIClient,
            "load_config",
            return_value={"providers": {"base": {"max_retries": 2}}},
        ):
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert not response.success
        assert "Rate limited" in response.error_message
        assert response.retry_after == 30
        # Should sleep on first retry attempt
        mock_sleep.assert_called_with(30)

    @patch("requests.Session.request")
    def test_connection_error_retry(self, mock_request):
        """Test connection error triggers retry."""
        import requests

        # Simulate connection error then success
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            Mock(
                status_code=200,
                json=lambda: {"result": "success"},
                content=b'{"result": "success"}',
            ),
        ]

        with patch.object(
            BaseAPIClient,
            "load_config",
            return_value={"providers": {"base": {"max_retries": 3}}},
        ), patch("time.sleep"):  # Mock sleep
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert response.success
        assert mock_request.call_count == 2

    @patch("requests.Session.request")
    def test_timeout_error_retry(self, mock_request):
        """Test timeout error triggers retry."""
        import requests

        mock_request.side_effect = [
            requests.exceptions.Timeout("Request timed out"),
            Mock(
                status_code=200,
                json=lambda: {"result": "success"},
                content=b'{"result": "success"}',
            ),
        ]

        with patch.object(
            BaseAPIClient,
            "load_config",
            return_value={"providers": {"base": {"max_retries": 3}}},
        ), patch("time.sleep"):  # Mock sleep
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert response.success
        assert mock_request.call_count == 2

    @patch("requests.Session.request")
    def test_max_retries_exhausted(self, mock_request):
        """Test behavior when max retries are exhausted."""
        import requests

        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        with patch.object(
            BaseAPIClient,
            "load_config",
            return_value={"providers": {"base": {"max_retries": 2}}},
        ), patch("time.sleep"):  # Mock sleep
            client = MockAPIClient("TestService")
            response = client._make_request("GET", "http://example.com/api")

        assert not response.success
        assert "Failed to connect" in response.error_message
        assert "after 2 attempts" in response.error_message
        assert mock_request.call_count == 2

    def test_session_setup_legacy_config(self):
        """Test session setup with legacy config structure."""
        legacy_config = {
            "apis": {"base": {"user_agent": "LegacyAgent/1.0", "timeout": 45}}
        }

        with patch.object(BaseAPIClient, "load_config", return_value=legacy_config):
            client = MockAPIClient("TestService")
            assert client.timeout == 45
            assert client.session.headers["User-Agent"] == "LegacyAgent/1.0"

    def test_session_setup_default_config(self):
        """Test session setup with default config when none provided."""
        with patch.object(BaseAPIClient, "load_config", return_value={}):
            client = MockAPIClient("TestService")
            assert client.timeout == 30  # Default
            assert "FluentForever" in client.session.headers["User-Agent"]


class TestAPIResponse:
    """Test cases for APIResponse."""

    def test_api_response_creation(self):
        """Test APIResponse creation."""
        response = APIResponse(success=True, data={"key": "value"}, status_code=200)

        assert response.success
        assert response.data == {"key": "value"}
        assert response.status_code == 200
        assert response.error_message == ""
        assert response.retry_after is None

    def test_api_response_failure(self):
        """Test APIResponse for failure case."""
        response = APIResponse(
            success=False,
            error_message="Something went wrong",
            status_code=500,
            retry_after=60,
        )

        assert not response.success
        assert response.data is None
        assert response.error_message == "Something went wrong"
        assert response.status_code == 500
        assert response.retry_after == 60


class TestAPIError:
    """Test cases for APIError."""

    def test_api_error_creation(self):
        """Test APIError creation."""
        error = APIError("Test error", status_code=400, retry_after=30)

        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.retry_after == 30

    def test_api_error_minimal(self):
        """Test APIError with minimal parameters."""
        error = APIError("Simple error")

        assert str(error) == "Simple error"
        assert error.status_code is None
        assert error.retry_after is None
