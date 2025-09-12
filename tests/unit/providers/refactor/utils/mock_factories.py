from unittest.mock import Mock


class MockAPIFactory:
    """Factory for creating consistent API mocks."""

    @staticmethod
    def create_openai_success_response(image_urls: list[str]) -> Mock:
        """Create mock OpenAI API success response."""
        mock_response = Mock()
        mock_response.data = [Mock(url=url) for url in image_urls]
        return mock_response

    @staticmethod
    def create_openai_error_response(error_message: str) -> Mock:
        """Create mock OpenAI API error response."""
        mock_response = Mock()
        mock_response.side_effect = Exception(error_message)
        return mock_response

    @staticmethod
    def create_forvo_success_response(audio_data: bytes = b"fake_audio_data") -> Mock:
        """Create mock Forvo API success response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = audio_data
        mock_response.headers = {"Content-Type": "audio/mpeg"}
        return mock_response

    @staticmethod
    def create_forvo_error_response(
        status_code: int = 404, error_message: str = "Not found"
    ) -> Mock:
        """Create mock Forvo API error response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.raise_for_status.side_effect = Exception(error_message)
        return mock_response

    @staticmethod
    def create_http_client_mock(success_response: Mock = None) -> Mock:
        """Create mock HTTP client for API calls."""
        mock_client = Mock()
        if success_response:
            mock_client.get.return_value = success_response
            mock_client.post.return_value = success_response
        return mock_client

    @staticmethod
    def create_file_download_mock(file_content: bytes = b"test_file_content") -> Mock:
        """Create mock for file download operations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = file_content
        mock_response.iter_content = Mock(return_value=[file_content])
        return mock_response

    @staticmethod
    def create_rate_limited_response() -> Mock:
        """Create mock response for rate limiting scenarios."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        return mock_response

    @staticmethod
    def create_openai_dalle_response(
        image_urls: list[str], revised_prompt: str = None
    ) -> Mock:
        """Create realistic OpenAI DALL-E API response."""
        mock_response = Mock()
        mock_data = []

        for url in image_urls:
            image_data = Mock()
            image_data.url = url
            if revised_prompt:
                image_data.revised_prompt = revised_prompt
            mock_data.append(image_data)

        mock_response.data = mock_data
        return mock_response

    @staticmethod
    def create_forvo_pronunciation_response(
        word: str,
        country_code: str = "US",
        audio_url: str = "https://api.forvo.com/audio/test.mp3",
    ) -> Mock:
        """Create realistic Forvo pronunciation API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "word": word,
                    "country": country_code,
                    "pathmp3": audio_url,
                    "rate": 5,
                    "num_votes": 10,
                }
            ]
        }
        return mock_response
