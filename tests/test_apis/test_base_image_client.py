#!/usr/bin/env python3
"""
Unit tests for BaseImageClient abstract interface
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from apis.base_image_client import BaseImageClient
from apis.base_client import APIResponse


class TestBaseImageClient:
    """Test the BaseImageClient abstract interface"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = {
            "apis": {
                "test_provider": {
                    "api_key": "",
                    "env_var": "TEST_API_KEY",
                    "base_url": "https://api.test.com",
                    "cost_per_image": 0.01
                },
                "base": {
                    "user_agent": "Test/1.0",
                    "timeout": 30,
                    "max_retries": 3
                }
            },
            "image_generation": {
                "primary_provider": "test_provider",
                "providers": {
                    "test_provider": {
                        "model": "test-model",
                        "style": "test style",
                        "width": 512,
                        "height": 512
                    }
                }
            }
        }

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseImageClient cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseImageClient("test")

    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key'})
    def test_concrete_implementation(self, mock_load_config):
        """Test that a concrete implementation works correctly"""
        mock_load_config.return_value = self.mock_config

        class TestImageClient(BaseImageClient):
            def generate_image(self, prompt: str, filename: str, save_path=None):
                return APIResponse(success=True, data={"file_path": f"/tmp/{filename}"})

            def estimate_cost(self, num_images: int = 1):
                return {"total_cost": num_images * 0.01}

            def test_connection(self):
                return True

            def get_service_info(self):
                return {"service": "Test"}

        client = TestImageClient("test_provider")
        
        # Test that config is loaded correctly
        assert client.image_config["model"] == "test-model"
        assert client.image_config["width"] == 512
        
        # Test provider config access
        provider_config = client._get_provider_config()
        assert provider_config["cost_per_image"] == 0.01
        
        # Test abstract methods are implemented
        response = client.generate_image("test prompt", "test.png")
        assert response.success is True
        
        cost = client.estimate_cost(2)
        assert cost["total_cost"] == 0.02
        
        assert client.test_connection() is True
        assert client.get_service_info()["service"] == "Test"

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_provider_config_retrieval(self, mock_load_config):
        """Test that provider-specific config is retrieved correctly"""
        mock_load_config.return_value = self.mock_config

        class TestImageClient(BaseImageClient):
            def generate_image(self, prompt: str, filename: str, save_path=None):
                return APIResponse(success=True)

            def estimate_cost(self, num_images: int = 1):
                return {}

            def test_connection(self):
                return True

            def get_service_info(self):
                return {}

        with patch.dict('os.environ', {'TEST_API_KEY': 'test-key'}):
            client = TestImageClient("test_provider")
            
            provider_config = client._get_provider_config()
            assert provider_config["api_key"] == ""
            assert provider_config["env_var"] == "TEST_API_KEY"
            assert provider_config["base_url"] == "https://api.test.com"
            assert provider_config["cost_per_image"] == 0.01

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_missing_provider_config(self, mock_load_config):
        """Test handling of missing provider configuration"""
        config_without_provider = {
            "apis": {
                "base": {"user_agent": "Test/1.0", "timeout": 30, "max_retries": 3}
            },
            "image_generation": {
                "providers": {
                    "test_provider": {"model": "test"}
                }
            }
        }
        mock_load_config.return_value = config_without_provider

        class TestImageClient(BaseImageClient):
            def generate_image(self, prompt: str, filename: str, save_path=None):
                return APIResponse(success=True)

            def estimate_cost(self, num_images: int = 1):
                return {}

            def test_connection(self):
                return True

            def get_service_info(self):
                return {}

        with pytest.raises(KeyError):
            TestImageClient("nonexistent_provider")