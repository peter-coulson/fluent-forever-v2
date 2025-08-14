#!/usr/bin/env python3
"""
OpenAI API Client
Handles DALL-E image generation for Spanish vocabulary cards
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from apis.base_client import BaseAPIClient, APIResponse, APIError
from utils.logging_config import get_logger, ICONS

logger = get_logger('apis.openai')

class OpenAIClient(BaseAPIClient):
    """OpenAI API client for DALL-E image generation"""
    
    def __init__(self):
        super().__init__("OpenAI")
        self.api_config = self.config["apis"]["openai"]
        self.image_config = self.config["image_generation"]
        self.api_key = self._load_api_key(self.api_config["env_var"])
        
        # Set up authentication
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        self.base_url = self.api_config["base_url"]
        
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = self._make_request("GET", f"{self.base_url}/models")
            if response.success:
                self.logger.info(f"{ICONS['check']} OpenAI API connection successful")
                return True
            else:
                self.logger.error(f"{ICONS['cross']} OpenAI API connection failed: {response.error_message}")
                return False
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} OpenAI API test failed: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get OpenAI service information"""
        return {
            "service": "OpenAI DALL-E",
            "model": self.api_config["model"],
            "image_size": f"{self.image_config['width']}x{self.image_config['height']}",
            "style": self.image_config["style"][:50] + "..." if len(self.image_config["style"]) > 50 else self.image_config["style"]
        }
    
    def generate_image(self, prompt: str, filename: str, save_path: Optional[Path] = None) -> APIResponse:
        """
        Generate image using DALL-E
        
        Args:
            prompt: Text description of desired image
            filename: Name for saved image file  
            save_path: Optional custom path to save image (defaults to config media folder)
            
        Returns:
            APIResponse with success status and saved file path
        """
        try:
            # Construct full prompt with style
            style_prompt = self.image_config["style"]
            full_prompt = f"{style_prompt}. {prompt}"
            
            # Prepare request data
            data = {
                "model": self.api_config["model"],
                "prompt": full_prompt,
                "n": 1,
                "size": f"{self.image_config['width']}x{self.image_config['height']}",
                "quality": "standard"
            }
            
            self.logger.info(f"{ICONS['gear']} Generating image: {filename}")
            self.logger.debug(f"Prompt: {prompt}")
            
            # Make API request
            response = self._make_request("POST", f"{self.base_url}/images/generations", json=data)
            
            if not response.success:
                return response
            
            # Extract image URL
            image_url = response.data['data'][0]['url']
            
            # Download and save image
            download_response = self._download_image(image_url, filename, save_path)
            
            if download_response.success:
                self.logger.info(f"{ICONS['check']} Image generated and saved: {filename}")
            
            return download_response
            
        except Exception as e:
            error_msg = f"Failed to generate image {filename}: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def _download_image(self, image_url: str, filename: str, save_path: Optional[Path] = None) -> APIResponse:
        """Download image from URL and save to file"""
        try:
            # Determine save path
            if save_path is None:
                media_folder = Path(self.config["paths"]["media_folder"])
                save_path = media_folder / "images" / filename
            else:
                save_path = save_path / filename
            
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download image
            self.logger.debug(f"Downloading image from: {image_url}")
            img_response = requests.get(image_url, timeout=30)
            
            if img_response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(img_response.content)
                
                self.logger.debug(f"Image saved to: {save_path}")
                return APIResponse(success=True, data={"file_path": str(save_path)})
            else:
                error_msg = f"Failed to download image (HTTP {img_response.status_code})"
                return APIResponse(success=False, error_message=error_msg, status_code=img_response.status_code)
                
        except Exception as e:
            error_msg = f"Error downloading image: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def validate_prompt(self, prompt: str) -> tuple[bool, str]:
        """
        Validate image prompt for content policy compliance
        
        Args:
            prompt: Text prompt to validate
            
        Returns:
            (is_valid, error_message)
        """
        # Basic validation checks
        if not prompt or len(prompt.strip()) == 0:
            return False, "Prompt cannot be empty"
        
        if len(prompt) > 1000:  # DALL-E limit is 1000 characters
            return False, f"Prompt too long ({len(prompt)} chars, max 1000)"
        
        # Check for prohibited content keywords
        prohibited_words = [
            'nude', 'naked', 'sexual', 'violent', 'blood', 'weapon', 'gun', 
            'knife', 'death', 'suicide', 'drug', 'alcohol', 'cigarette',
            'politics', 'politician', 'celebrity'
        ]
        
        prompt_lower = prompt.lower()
        for word in prohibited_words:
            if word in prompt_lower:
                return False, f"Prompt contains prohibited content: {word}"
        
        return True, ""
    
    def estimate_cost(self, num_images: int = 1) -> Dict[str, Any]:
        """
        Estimate cost for generating images
        
        Args:
            num_images: Number of images to generate
            
        Returns:
            Cost information dictionary
        """
        cost_per_image = self.api_config["cost_per_image"]
        total_cost = num_images * cost_per_image
        
        return {
            "model": self.api_config["model"],
            "images": num_images,
            "cost_per_image": f"${cost_per_image:.3f}",
            "total_cost": f"${total_cost:.3f}",
            "size": f"{self.image_config['width']}x{self.image_config['height']}"
        }