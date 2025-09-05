#!/usr/bin/env python3
"""
Unit tests for RunwareClient
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import uuid
import requests
from apis.runware_client import RunwareClient
from apis.base_client import APIResponse


class TestRunwareClient:
    """Test the RunwareClient implementation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = {
            "apis": {
                "runware": {
                    "api_key": "",
                    "env_var": "RUNWARE_API_KEY",
                    "base_url": "https://api.runware.ai",
                    "timeout": 60,
                    "cost_per_image": 0.01
                },
                "base": {
                    "user_agent": "FluentForever-v2/1.0",
                    "timeout": 30,
                    "max_retries": 3
                }
            },
            "image_generation": {
                "providers": {
                    "runware": {
                        "model": "stable-diffusion-xl-base-1.0",
                        "style": "Studio Ghibli style",
                        "negative_prompt": "realistic, blurry",
                        "width": 1024,
                        "height": 1024,
                        "steps": 25,
                        "guidance_scale": 7.0,
                        "sampler": "euler"
                    }
                }
            },
            "paths": {
                "media_folder": "media"
            }
        }

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-runware-key'})
    def test_client_initialization(self, mock_load_config):
        """Test that RunwareClient initializes correctly"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        assert client.service_name == "Runware"
        assert client.api_key == "test-runware-key"
        assert client.base_url == "https://api.runware.ai"
        assert "Bearer test-runware-key" in client.session.headers["Authorization"]

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_get_service_info(self, mock_load_config):
        """Test service info retrieval"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        info = client.get_service_info()
        
        assert info["service"] == "Runware AI"
        assert info["model"] == "stable-diffusion-xl-base-1.0"
        assert info["image_size"] == "1024x1024"
        assert "Studio Ghibli" in info["style"]
        assert info["steps"] == 25
        assert info["guidance_scale"] == 7.0
        assert info["sampler"] == "euler"

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_test_connection_success(self, mock_load_config):
        """Test successful connection test"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        # Mock successful response (HTTP 200)
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(success=True, status_code=200)
            
            result = client.test_connection()
            assert result is True
            mock_request.assert_called_once()

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_test_connection_auth_failure(self, mock_load_config):
        """Test connection test with authentication failure"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        # Mock 401 Unauthorized response
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(success=False, status_code=401, error_message="Unauthorized")
            
            result = client.test_connection()
            assert result is False

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_test_connection_forbidden(self, mock_load_config):
        """Test connection test with forbidden response"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        # Mock 403 Forbidden response
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(success=False, status_code=403, error_message="Forbidden")
            
            result = client.test_connection()
            assert result is False

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_generate_image_success(self, mock_load_config):
        """Test successful image generation"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        # Mock successful API response (match the expected format from implementation)
        mock_response_data = {
            "data": [{
                "taskType": "imageInference",
                "taskUUID": "test-uuid",
                "imageURL": "https://example.com/image.png"
            }]
        }
        
        with patch.object(client, '_make_request') as mock_request, \
             patch.object(client, '_download_image') as mock_download, \
             patch('uuid.uuid4') as mock_uuid:
            
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
            mock_request.return_value = APIResponse(success=True, data=mock_response_data)
            mock_download.return_value = APIResponse(success=True, data={"file_path": "/tmp/test.png"})
            
            response = client.generate_image("test prompt", "test.png")
            
            assert response.success is True
            assert response.data["file_path"] == "/tmp/test.png"
            
            # Verify API request was made correctly
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "POST"
            assert "v1" in args[1]
            
            request_data = kwargs["json"][0]
            assert request_data["taskType"] == "imageInference"
            assert request_data["taskUUID"] == "12345678-1234-5678-1234-567812345678"
            assert "Studio Ghibli style. test prompt" in request_data["positivePrompt"]
            assert request_data["negativePrompt"] == "realistic, blurry"
            assert request_data["model"] == "stable-diffusion-xl-base-1.0"
            assert request_data["width"] == 1024
            assert request_data["height"] == 1024
            assert request_data["steps"] == 25
            assert request_data["CFGScale"] == 7.0
            assert request_data["scheduler"] == "euler"

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_generate_image_api_failure(self, mock_load_config):
        """Test image generation with API failure"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(success=False, error_message="API error")
            
            response = client.generate_image("test prompt", "test.png")
            
            assert response.success is False
            assert "API error" in response.error_message

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_generate_image_empty_response(self, mock_load_config):
        """Test image generation with empty response data"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(success=True, data=[])
            
            response = client.generate_image("test prompt", "test.png")
            
            assert response.success is False
            assert "No image data received" in response.error_message

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_generate_image_error_in_response(self, mock_load_config):
        """Test image generation with error in response data"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        mock_response_data = {
            "data": [{
                "taskType": "error", 
                "error": "Model not available"
            }]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(success=True, data=mock_response_data)
            
            response = client.generate_image("test prompt", "test.png")
            
            assert response.success is False
            assert "Model not available" in response.error_message

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_download_image_success(self, mock_load_config):
        """Test successful image download"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
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
            mock_open.assert_called_once()
            mock_mkdir.assert_called_once()

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_download_image_http_error(self, mock_load_config):
        """Test image download with HTTP error"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('requests.get', return_value=mock_response):
            response = client._download_image("https://example.com/image.png", "test.png")
            
            assert response.success is False
            assert "404" in response.error_message

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'RUNWARE_API_KEY': 'test-key'})
    def test_estimate_cost(self, mock_load_config):
        """Test cost estimation"""
        mock_load_config.return_value = self.mock_config
        
        client = RunwareClient()
        
        cost_info = client.estimate_cost(3)
        
        assert cost_info["model"] == "stable-diffusion-xl-base-1.0"
        assert cost_info["images"] == 3
        assert cost_info["cost_per_image"] == "$0.010"
        assert cost_info["total_cost"] == "$0.030"
        assert cost_info["size"] == "1024x1024"
        assert cost_info["steps"] == 25
        assert cost_info["guidance_scale"] == 7.0

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_missing_api_key(self, mock_load_config):
        """Test initialization without API key"""
        mock_load_config.return_value = self.mock_config
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception):  # Should raise APIError about missing key
                RunwareClient()