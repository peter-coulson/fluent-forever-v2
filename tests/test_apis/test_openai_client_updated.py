#!/usr/bin/env python3
"""
Unit tests for updated OpenAI client that inherits from BaseImageClient
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import requests
from apis.openai_client import OpenAIClient
from apis.base_client import APIResponse


class TestUpdatedOpenAIClient:
    """Test the updated OpenAI client implementation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = {
            "apis": {
                "openai": {
                    "api_key": "",
                    "env_var": "OPENAI_API_KEY",
                    "base_url": "https://api.openai.com/v1",
                    "timeout": 60,
                    "cost_per_image": 0.040
                },
                "base": {
                    "user_agent": "FluentForever-v2/1.0",
                    "timeout": 30,
                    "max_retries": 3
                }
            },
            "image_generation": {
                "providers": {
                    "openai": {
                        "model": "dall-e-3",
                        "style": "Studio Ghibli animation style",
                        "width": 1024,
                        "height": 1024,
                        "quality": "standard"
                    }
                }
            },
            "paths": {
                "media_folder": "media"
            }
        }

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-openai-key'})
    def test_client_initialization(self, mock_load_config):
        """Test that OpenAI client initializes correctly with new structure"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        
        assert client.service_name == "openai"  # Note: now lowercase for BaseImageClient
        assert client.api_key == "test-openai-key"
        assert client.base_url == "https://api.openai.com/v1"
        assert "Bearer test-openai-key" in client.session.headers["Authorization"]

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_inherits_from_base_image_client(self, mock_load_config):
        """Test that OpenAI client properly inherits from BaseImageClient"""
        mock_load_config.return_value = self.mock_config
        
        from apis.base_image_client import BaseImageClient
        client = OpenAIClient()
        
        assert isinstance(client, BaseImageClient)
        assert hasattr(client, 'image_config')
        assert hasattr(client, '_get_provider_config')

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_get_service_info_updated(self, mock_load_config):
        """Test service info uses new config structure"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        info = client.get_service_info()
        
        assert info["service"] == "OpenAI DALL-E"
        assert info["model"] == "dall-e-3"  # From image_config, not api_config
        assert info["image_size"] == "1024x1024"
        assert "Studio Ghibli" in info["style"]

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_generate_image_uses_new_config_structure(self, mock_load_config):
        """Test that image generation uses the new provider-specific config"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        
        # Mock successful API response
        mock_response_data = {
            'data': [{'url': 'https://example.com/image.png'}]
        }
        
        with patch.object(client, '_make_request') as mock_request, \
             patch.object(client, '_download_image') as mock_download:
            
            mock_request.return_value = APIResponse(success=True, data=mock_response_data)
            mock_download.return_value = APIResponse(success=True, data={"file_path": "/tmp/test.png"})
            
            response = client.generate_image("test prompt", "test.png")
            
            assert response.success is True
            
            # Verify API request uses new config structure
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "POST"
            assert "images/generations" in args[1]
            
            request_data = kwargs["json"]
            assert request_data["model"] == "dall-e-3"  # From image_config
            assert "Studio Ghibli animation style. test prompt" in request_data["prompt"]
            assert request_data["size"] == "1024x1024"
            assert request_data["quality"] == "standard"

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_generate_image_with_default_quality(self, mock_load_config):
        """Test image generation with default quality when not specified"""
        # Config without quality setting
        config_no_quality = self.mock_config.copy()
        del config_no_quality["image_generation"]["providers"]["openai"]["quality"]
        mock_load_config.return_value = config_no_quality
        
        client = OpenAIClient()
        
        mock_response_data = {
            'data': [{'url': 'https://example.com/image.png'}]
        }
        
        with patch.object(client, '_make_request') as mock_request, \
             patch.object(client, '_download_image') as mock_download:
            
            mock_request.return_value = APIResponse(success=True, data=mock_response_data)
            mock_download.return_value = APIResponse(success=True, data={"file_path": "/tmp/test.png"})
            
            response = client.generate_image("test prompt", "test.png")
            
            # Should use default quality
            request_data = mock_request.call_args[1]["json"]
            assert request_data["quality"] == "standard"

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_estimate_cost_uses_new_config(self, mock_load_config):
        """Test cost estimation uses new config structure"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        cost_info = client.estimate_cost(2)
        
        assert cost_info["model"] == "dall-e-3"  # From image_config
        assert cost_info["images"] == 2
        assert cost_info["cost_per_image"] == "$0.040"  # From api_config
        assert cost_info["total_cost"] == "$0.080"
        assert cost_info["size"] == "1024x1024"

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_provider_config_access(self, mock_load_config):
        """Test access to provider-specific configuration"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        provider_config = client._get_provider_config()
        
        assert provider_config["api_key"] == ""
        assert provider_config["env_var"] == "OPENAI_API_KEY"
        assert provider_config["base_url"] == "https://api.openai.com/v1"
        assert provider_config["cost_per_image"] == 0.040

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_test_connection_unchanged(self, mock_load_config):
        """Test that connection test functionality is preserved"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        
        with patch.object(client, '_make_request') as mock_request:
            # Mock successful response
            mock_request.return_value = APIResponse(success=True, status_code=200)
            
            result = client.test_connection()
            assert result is True
            
            # Verify correct endpoint is called
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "models" in args[1]

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_download_image_unchanged(self, mock_load_config):
        """Test that image download functionality is preserved"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        
        with patch('requests.get', return_value=mock_response), \
             patch('builtins.open', create=True) as mock_open, \
             patch.object(Path, 'mkdir') as mock_mkdir:
            
            response = client._download_image("https://example.com/image.png", "test.png")
            
            assert response.success is True
            assert "test.png" in response.data["file_path"]
            # Uses config path structure
            expected_path = Path(self.mock_config["paths"]["media_folder"]) / "images" / "test.png"
            assert str(expected_path) in response.data["file_path"]

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_missing_api_key_handling(self, mock_load_config):
        """Test handling of missing API key"""
        mock_load_config.return_value = self.mock_config
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception):  # Should raise APIError about missing key
                OpenAIClient()

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_backward_compatibility(self, mock_load_config):
        """Test that the client maintains backward compatibility"""
        mock_load_config.return_value = self.mock_config
        
        client = OpenAIClient()
        
        # All original methods should still exist
        assert hasattr(client, 'test_connection')
        assert hasattr(client, 'get_service_info')
        assert hasattr(client, 'generate_image')
        assert hasattr(client, 'estimate_cost')
        assert callable(client.test_connection)
        assert callable(client.get_service_info)
        assert callable(client.generate_image)
        assert callable(client.estimate_cost)