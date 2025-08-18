#!/usr/bin/env python3
"""
Base Image Generation Client
Abstract interface for all image generation providers
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from apis.base_client import BaseAPIClient, APIResponse

class BaseImageClient(BaseAPIClient, ABC):
    """Abstract base class for image generation clients"""
    
    def __init__(self, service_name: str):
        super().__init__(service_name)
        self.image_config = self.config["image_generation"]["providers"][service_name.lower()]
    
    @abstractmethod
    def generate_image(self, prompt: str, filename: str, save_path: Optional[Path] = None) -> APIResponse:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description of desired image
            filename: Name for saved image file  
            save_path: Optional custom path to save image
            
        Returns:
            APIResponse with success status and saved file path
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, num_images: int = 1) -> Dict[str, Any]:
        """
        Estimate cost for generating images
        
        Args:
            num_images: Number of images to generate
            
        Returns:
            Cost information dictionary
        """
        pass
    
    def _get_provider_config(self) -> Dict[str, Any]:
        """Get provider-specific configuration from APIs section"""
        provider_name = self.service_name.lower()
        return self.config["apis"][provider_name]