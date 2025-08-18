#!/usr/bin/env python3
"""
Image Provider Factory
Creates appropriate image generation client based on provider configuration
"""

from typing import Dict, Any
from apis.base_image_client import BaseImageClient
from apis.openai_client import OpenAIClient
from apis.runware_client import RunwareClient
from utils.logging_config import get_logger, ICONS

logger = get_logger('apis.factory')

class ImageProviderFactory:
    """Factory for creating image generation clients"""
    
    _PROVIDERS = {
        "openai": OpenAIClient,
        "runware": RunwareClient
    }
    
    @classmethod
    def create_client(cls, provider: str) -> BaseImageClient:
        """
        Create image generation client for specified provider
        
        Args:
            provider: Provider name (openai, runware)
            
        Returns:
            Configured image client instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower()
        
        if provider_lower not in cls._PROVIDERS:
            available = ", ".join(cls._PROVIDERS.keys())
            raise ValueError(f"Unsupported image provider: {provider}. Available: {available}")
        
        try:
            client_class = cls._PROVIDERS[provider_lower]
            client = client_class()
            logger.info(f"{ICONS['check']} Created {provider} image client")
            return client
        except Exception as e:
            logger.error(f"{ICONS['cross']} Failed to create {provider} client: {e}")
            raise
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._PROVIDERS.keys())
    
    @classmethod
    def validate_provider(cls, provider: str) -> bool:
        """Check if provider name is valid"""
        return provider.lower() in cls._PROVIDERS

def create_image_client(provider: str) -> BaseImageClient:
    """
    Convenience function to create image client
    
    Args:
        provider: Provider name
        
    Returns:
        Configured image client
    """
    return ImageProviderFactory.create_client(provider)