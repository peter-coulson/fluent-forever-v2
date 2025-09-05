#!/usr/bin/env python3
"""
Unit tests for ImageProviderFactory
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from apis.image_provider_factory import ImageProviderFactory, create_image_client
from apis.openai_client import OpenAIClient
from apis.runware_client import RunwareClient


class TestImageProviderFactory:
    """Test the ImageProviderFactory class"""

    def test_get_available_providers(self):
        """Test getting list of available providers"""
        providers = ImageProviderFactory.get_available_providers()
        
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "runware" in providers

    def test_validate_provider_valid(self):
        """Test provider validation with valid providers"""
        assert ImageProviderFactory.validate_provider("openai") is True
        assert ImageProviderFactory.validate_provider("runware") is True
        assert ImageProviderFactory.validate_provider("OpenAI") is True  # Case insensitive
        assert ImageProviderFactory.validate_provider("RUNWARE") is True

    def test_validate_provider_invalid(self):
        """Test provider validation with invalid providers"""
        assert ImageProviderFactory.validate_provider("invalid") is False
        assert ImageProviderFactory.validate_provider("") is False
        assert ImageProviderFactory.validate_provider("midjourney") is False

    def test_create_openai_client(self):
        """Test creating OpenAI client"""
        mock_client = Mock()
        
        with patch.dict(ImageProviderFactory._PROVIDERS, {'openai': Mock(return_value=mock_client)}):
            client = ImageProviderFactory.create_client("openai")
            assert client == mock_client

    def test_create_runware_client(self):
        """Test creating Runware client"""
        mock_client = Mock()
        
        with patch.dict(ImageProviderFactory._PROVIDERS, {'runware': Mock(return_value=mock_client)}):
            client = ImageProviderFactory.create_client("runware")
            assert client == mock_client

    def test_create_client_case_insensitive(self):
        """Test creating client with case insensitive provider name"""
        mock_client = Mock()
        
        with patch.dict(ImageProviderFactory._PROVIDERS, {'openai': Mock(return_value=mock_client)}):
            # Test various case combinations
            for provider_name in ["OpenAI", "OPENAI", "openAI", "OpEnAi"]:
                client = ImageProviderFactory.create_client(provider_name)
                assert client == mock_client

    def test_create_client_unsupported_provider(self):
        """Test creating client with unsupported provider"""
        with pytest.raises(ValueError) as exc_info:
            ImageProviderFactory.create_client("unsupported")
        
        assert "Unsupported image provider" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)

    def test_create_client_initialization_error(self):
        """Test handling of client initialization errors"""
        mock_class = Mock(side_effect=Exception("API key missing"))
        
        with patch.dict(ImageProviderFactory._PROVIDERS, {'openai': mock_class}):
            with pytest.raises(Exception) as exc_info:
                ImageProviderFactory.create_client("openai")
            
            assert "API key missing" in str(exc_info.value)

    @patch('apis.image_provider_factory.logger')
    def test_create_client_logs_success(self, mock_logger):
        """Test that successful client creation is logged"""
        mock_client = Mock()
        
        with patch.dict(ImageProviderFactory._PROVIDERS, {'openai': Mock(return_value=mock_client)}):
            client = ImageProviderFactory.create_client("openai")
            
            # Check that info log was called (success message)
            mock_logger.info.assert_called()
            log_call = mock_logger.info.call_args[0][0]
            assert "Created openai image client" in log_call

    @patch('apis.image_provider_factory.logger')
    def test_create_client_logs_failure(self, mock_logger):
        """Test that failed client creation is logged"""
        mock_class = Mock(side_effect=Exception("Test error"))
        
        with patch.dict(ImageProviderFactory._PROVIDERS, {'openai': mock_class}):
            with pytest.raises(Exception):
                ImageProviderFactory.create_client("openai")
            
            # Check that error log was called
            mock_logger.error.assert_called()
            log_call = mock_logger.error.call_args[0][0]
            assert "Failed to create openai client" in log_call


class TestCreateImageClientFunction:
    """Test the convenience function create_image_client"""

    @patch.object(ImageProviderFactory, 'create_client')
    def test_create_image_client_delegates_to_factory(self, mock_create_client):
        """Test that create_image_client delegates to factory"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        client = create_image_client("openai")
        
        assert client == mock_client
        mock_create_client.assert_called_once_with("openai")

    @patch.object(ImageProviderFactory, 'create_client')
    def test_create_image_client_passes_through_errors(self, mock_create_client):
        """Test that create_image_client passes through factory errors"""
        mock_create_client.side_effect = ValueError("Invalid provider")
        
        with pytest.raises(ValueError) as exc_info:
            create_image_client("invalid")
        
        assert "Invalid provider" in str(exc_info.value)