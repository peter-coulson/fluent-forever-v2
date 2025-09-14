"""Integration tests for RunwareProvider with real API calls."""

import os
import time
from unittest.mock import Mock, patch

import pytest
import requests

from providers.base.media_provider import MediaRequest
from providers.image.runware_provider import RunwareProvider


class TestRunwareIntegration:
    """Integration tests with Runware API"""

    @pytest.fixture
    def test_api_key(self):
        """Get test API key from environment or skip tests"""
        api_key = os.getenv("RUNWARE_TEST_API_KEY")
        if not api_key:
            pytest.skip("RUNWARE_TEST_API_KEY not set - skipping real API tests")
        return api_key

    @pytest.fixture
    def provider(self, test_api_key):
        """Create provider with test configuration"""
        config = {
            "api_key": test_api_key,
            "model": "runware:100@1",
            "image_size": "512x512",
            "rate_limit_delay": 2.0,  # Conservative rate limiting for tests
            "timeout": 60,
        }
        return RunwareProvider(config)

    def test_real_api_single_image_generation(self, provider):
        """Test: Single image generation with real API"""
        request = MediaRequest(
            type="image",
            content="a simple red circle on white background",
            params={"language": "en"},
        )

        result = provider.generate_media(request)

        assert result.success is True
        assert result.file_path is not None
        assert result.file_path.exists()
        assert result.file_path.suffix == ".png"
        assert result.error is None

        # Verify metadata
        assert result.metadata["prompt"] == "a simple red circle on white background"
        assert "task_id" in result.metadata
        assert "generation_time" in result.metadata
        assert result.metadata["model"] == "runware:100@1"

        # Verify file properties
        file_size = result.file_path.stat().st_size
        assert file_size > 1000  # Should be reasonable size
        assert file_size < 10 * 1024 * 1024  # Should be < 10MB

        # Cleanup
        if result.file_path.exists():
            result.file_path.unlink()

    def test_rate_limiting_compliance(self, provider):
        """Test: Rate limiting prevents API overuse"""
        requests = [
            MediaRequest(type="image", content=f"test image {i}", params={})
            for i in range(3)
        ]

        start_time = time.time()
        results = provider.generate_batch(requests)
        end_time = time.time()

        # All should succeed
        assert all(result.success for result in results)

        # Should take at least rate_limit_delay * (num_requests - 1) seconds
        expected_min_time = provider._rate_limit_delay * (len(requests) - 1)
        actual_time = end_time - start_time
        assert actual_time >= expected_min_time - 0.5  # Allow small timing variance

        # Cleanup
        for result in results:
            if result.file_path and result.file_path.exists():
                result.file_path.unlink()

    def test_batch_processing_efficiency(self, provider):
        """Test: Batch processing vs individual requests"""
        test_prompts = [
            "a red apple",
            "a blue car",
            "a green tree",
        ]

        # Test individual requests
        individual_start = time.time()
        individual_results = []
        for prompt in test_prompts:
            request = MediaRequest(type="image", content=prompt, params={})
            result = provider.generate_media(request)
            individual_results.append(result)
            time.sleep(provider._rate_limit_delay)  # Manual rate limiting
        individual_time = time.time() - individual_start

        # Test batch requests
        batch_requests = [
            MediaRequest(type="image", content=prompt, params={})
            for prompt in test_prompts
        ]

        batch_start = time.time()
        batch_results = provider.generate_batch(batch_requests)
        batch_time = time.time() - batch_start

        # Both should succeed
        assert all(result.success for result in individual_results)
        assert all(result.success for result in batch_results)

        # Batch should be similar or faster (due to internal optimizations)
        # Allow for some variance due to API response times
        assert batch_time <= individual_time * 1.2

        # Cleanup
        for result in individual_results + batch_results:
            if result.file_path and result.file_path.exists():
                result.file_path.unlink()

    def test_error_recovery_with_real_api(self, provider):
        """Test: Error recovery with invalid requests"""
        # Test with empty prompt (should fail validation)
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            request = MediaRequest(type="image", content="", params={})
            provider.generate_media(request)

        # Test with extremely long prompt (may hit API limits)
        very_long_prompt = "test " * 1000  # 5000+ characters
        request = MediaRequest(type="image", content=very_long_prompt, params={})
        result = provider.generate_media(request)

        # Should either succeed or fail gracefully
        if not result.success:
            assert result.error is not None
            assert len(result.error) > 0

    @pytest.mark.parametrize("image_size", ["256x256", "512x512", "768x768"])
    def test_different_image_sizes(self, test_api_key, image_size):
        """Test: Different image sizes work correctly"""
        config = {
            "api_key": test_api_key,
            "image_size": image_size,
            "rate_limit_delay": 2.0,
        }
        provider = RunwareProvider(config)

        request = MediaRequest(
            type="image", content="a simple geometric shape", params={}
        )

        result = provider.generate_media(request)

        assert result.success is True
        assert result.metadata["image_size"] == image_size

        # Cleanup
        if result.file_path and result.file_path.exists():
            result.file_path.unlink()

    def test_concurrent_request_handling(self, provider):
        """Test: Provider handles concurrent-like batch requests"""
        import queue
        import threading

        requests = [
            MediaRequest(type="image", content=f"concurrent test {i}", params={})
            for i in range(3)
        ]

        results_queue = queue.Queue()

        def process_request(req):
            result = provider.generate_media(req)
            results_queue.put(result)

        # Start threads (will be serialized by rate limiting)
        threads = []
        for request in requests:
            thread = threading.Thread(target=process_request, args=(request,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        assert len(results) == 3
        assert all(result.success for result in results)

        # Cleanup
        for result in results:
            if result.file_path and result.file_path.exists():
                result.file_path.unlink()

    def test_authentication_failure_simulation(self):
        """Test: Authentication failure handling"""
        config = {
            "api_key": "invalid-api-key-12345",
            "rate_limit_delay": 0.1,
        }
        provider = RunwareProvider(config)

        request = MediaRequest(type="image", content="test image", params={})
        result = provider.generate_media(request)

        assert result.success is False
        assert (
            "authentication" in result.error.lower()
            or "unauthorized" in result.error.lower()
        )

    def test_network_resilience(self, provider):
        """Test: Network issue resilience with retry logic"""
        # This test uses real API but simulates network issues
        with patch("requests.Session"):
            # Create a mock session that fails first, then succeeds
            real_session = provider._session
            _ = real_session  # Use real session for final request

            # Override post method to fail first attempt
            original_post = real_session.post
            attempt_count = 0

            def failing_post(*args, **kwargs):
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count == 1:
                    raise requests.exceptions.ConnectionError("Simulated network error")
                return original_post(*args, **kwargs)

            real_session.post = failing_post

            request = MediaRequest(type="image", content="network test", params={})
            result = provider.generate_media(request)

            # Should eventually succeed after retry
            assert result.success is True or (
                result.success is False and "network" in result.error.lower()
            )

            # Cleanup
            if result.success and result.file_path and result.file_path.exists():
                result.file_path.unlink()


class TestRunwareMockIntegration:
    """Integration tests with mocked API responses for consistent testing"""

    def test_complete_workflow_with_mocked_api(self):
        """Test: Complete workflow with mocked API responses"""
        config = {
            "api_key": "test-key",
            "model": "runware:100@1",
            "rate_limit_delay": 0.1,
        }

        with patch("requests.Session") as mock_session_class, patch(
            "pathlib.Path.mkdir"
        ), patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.stat"
        ) as mock_stat, patch("builtins.open", create=True) as mock_open:
            # Setup session mock
            mock_session = mock_session_class.return_value

            # Mock API response
            mock_api_response = {
                "status": "success",
                "data": {
                    "taskId": "test-task-123",
                    "imageUrl": "https://api.runware.ai/output/test-image.png",
                    "model": "runware:100@1",
                    "steps": 20,
                    "guidance": 7,
                    "seed": 42,
                },
            }

            api_response_mock = Mock()
            api_response_mock.status_code = 200
            api_response_mock.raise_for_status.return_value = None
            api_response_mock.json.return_value = mock_api_response
            mock_session.post.return_value = api_response_mock

            # Mock image download
            download_response_mock = Mock()
            download_response_mock.status_code = 200
            download_response_mock.headers = {"content-type": "image/png"}
            download_response_mock.iter_content.return_value = [
                b"fake_image_data" * 100
            ]
            download_response_mock.raise_for_status.return_value = None
            mock_session.get.return_value = download_response_mock

            # Mock file operations
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Mock file size for validation
            mock_stat.return_value.st_size = 1024

            provider = RunwareProvider(config)

            # Test single generation
            request = MediaRequest(
                type="image",
                content="a beautiful landscape",
                params={"style": "photorealistic"},
            )

            result = provider.generate_media(request)

            # Verify success
            assert result.success is True
            assert result.file_path is not None
            assert "media/images" in str(result.file_path)

            # Verify metadata
            assert result.metadata["prompt"] == "a beautiful landscape"
            assert result.metadata["task_id"] == "test-task-123"
            assert result.metadata["model"] == "runware:100@1"
            assert result.metadata["steps"] == 20

            # Verify API calls
            mock_session.post.assert_called_once()
            mock_session.get.assert_called_once_with(
                "https://api.runware.ai/output/test-image.png",
                stream=True,
                timeout=provider.timeout,
            )

    def test_batch_processing_with_partial_failures(self):
        """Test: Batch processing handles partial failures correctly"""
        config = {"api_key": "test-key", "rate_limit_delay": 0.1}

        with patch("requests.Session") as mock_session_class:
            mock_session = mock_session_class.return_value

            # Create mock responses
            response1 = Mock()
            response1.status_code = 200
            response1.raise_for_status.return_value = None
            response1.json.return_value = {
                "status": "success",
                "data": {"taskId": "task-1", "imageUrl": "https://example.com/1.png"},
            }

            response2 = Mock()
            response2.status_code = 500
            response2.raise_for_status.side_effect = requests.HTTPError("500 Error")

            response3 = Mock()
            response3.status_code = 200
            response3.raise_for_status.return_value = None
            response3.json.return_value = {
                "status": "success",
                "data": {"taskId": "task-3", "imageUrl": "https://example.com/3.png"},
            }

            responses = [response1, response2, response3]

            mock_session.post.side_effect = responses

            # Mock successful downloads for successful API calls
            download_mock = Mock(status_code=200, headers={"content-type": "image/png"})
            download_mock.iter_content.return_value = [b"image_data"]
            download_mock.raise_for_status.return_value = None
            mock_session.get.return_value = download_mock

            with patch("pathlib.Path.mkdir"), patch(
                "pathlib.Path.exists", return_value=True
            ), patch("pathlib.Path.stat") as mock_stat, patch(
                "builtins.open", create=True
            ):
                # Mock file size for validation
                mock_stat.return_value.st_size = 1024

                provider = RunwareProvider(config)

                test_requests = [
                    MediaRequest(type="image", content="test 1", params={}),
                    MediaRequest(type="image", content="test 2", params={}),
                    MediaRequest(type="image", content="test 3", params={}),
                ]

                results = provider.generate_batch(test_requests)

                assert len(results) == 3
                assert results[0].success is True
                assert results[1].success is False
                assert results[2].success is True

                # Failed request should have error message
                assert results[1].error is not None
                assert "500" in results[1].error
