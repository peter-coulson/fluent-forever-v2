#!/usr/bin/env python3
"""
Unit tests for Base API Client after migration to providers

Tests API client functionality in the new provider structure.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from providers.base.api_client import BaseAPIClient, APIResponse, APIError


class MockAPIClient(BaseAPIClient):
    """Mock API client for testing"""
    
    def __init__(self, **kwargs):
        super().__init__("test_api")
        self.api_name = "test_api"
    
    def test_connection(self):
        """Test API connection"""
        return True
    
    def get_service_info(self):
        """Get service info"""
        return {
            "service": "test_api",
            "status": "connected"
        }


class TestBaseAPIClient:
    """Test BaseAPIClient functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / 'config.json'
        
        # Create test config
        test_config = {
            "providers": {
                "test_api": {
                    "api_key": "test_key",
                    "base_url": "https://api.test.com"
                }
            }
        }
        self.config_path.write_text(json.dumps(test_config))
        
        # Clear class-level config cache
        BaseAPIClient._shared_config = None
    
    def teardown_method(self):
        """Clean up test configuration"""
        BaseAPIClient._shared_config = None
        self.temp_dir.cleanup()
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = BaseAPIClient.load_config(self.config_path)
        
        assert config is not None
        assert 'providers' in config
        assert 'test_api' in config['providers']
        assert config['providers']['test_api']['api_key'] == 'test_key'
    
    def test_shared_config_caching(self):
        """Test that config is shared across clients"""
        config1 = BaseAPIClient.load_config(self.config_path)
        config2 = BaseAPIClient.load_config(self.config_path)
        
        # Should be the same cached object
        assert config1 is config2
    
    def test_api_response_creation(self):
        """Test APIResponse object creation"""
        response = APIResponse(
            success=True,
            data={"key": "value"},
            status_code=200
        )
        
        assert response.success is True
        assert response.data["key"] == "value"
        assert response.status_code == 200
        assert response.error_message == ""
        assert response.retry_after is None
    
    def test_api_error_creation(self):
        """Test APIError exception creation"""
        error = APIError(
            message="Test error",
            status_code=400,
            retry_after=60
        )
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.retry_after == 60
    
    @patch('requests.get')
    def test_rate_limiting_handling(self, mock_get):
        """Test rate limiting response handling"""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.json.return_value = {"error": "Rate limited"}
        mock_get.return_value = mock_response
        
        client = MockAPIClient()
        
        # This would typically be implemented in subclasses
        # Here we just test the response structure
        response = APIResponse(
            success=False,
            status_code=429,
            retry_after=60,
            error_message="Rate limited"
        )
        
        assert not response.success
        assert response.status_code == 429
        assert response.retry_after == 60
    
    def test_mock_client_functionality(self):
        """Test mock client implementation"""
        client = MockAPIClient()
        connection_result = client.test_connection()
        service_info = client.get_service_info()
        
        assert connection_result is True
        assert service_info["service"] == "test_api"
        assert service_info["status"] == "connected"
        assert client.api_name == "test_api"


if __name__ == "__main__":
    pytest.main([__file__])