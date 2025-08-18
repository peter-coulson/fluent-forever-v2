#!/usr/bin/env python3
"""
Runware API Client
Handles image generation for Spanish vocabulary cards using Runware AI
"""

import os
import uuid
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from apis.base_image_client import BaseImageClient
from apis.base_client import APIResponse, APIError
from utils.logging_config import get_logger, ICONS

logger = get_logger('apis.runware')

class RunwareClient(BaseImageClient):
    """Runware API client for image generation"""
    
    def __init__(self):
        super().__init__("Runware")
        self.api_config = self._get_provider_config()
        self.api_key = self._load_api_key(self.api_config["env_var"])
        
        # Set up authentication
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        self.base_url = self.api_config["base_url"]
        
    def test_connection(self) -> bool:
        """Test Runware API connection without using credits"""
        try:
            # Test with a minimal request that would fail immediately if auth is wrong
            # Using invalid parameters that will error quickly without consuming credits
            data = [{
                "taskType": "imageInference",
                "taskUUID": "test-connection-uuid",
                "positivePrompt": "test",
                # Missing required fields intentionally to trigger quick validation error
            }]
            
            response = self._make_request("POST", f"{self.base_url}/v1", json=data)
            
            # Check response structure
            if response.success:
                # If we get HTTP 200, authentication worked
                # Even if there are validation errors in the data, auth is OK
                self.logger.info(f"{ICONS['check']} Runware API connection and authentication successful")
                return True
            elif response.status_code == 401:
                # Explicit authentication failure
                self.logger.error(f"{ICONS['cross']} Runware API authentication failed: Invalid API key")
                return False
            elif response.status_code == 403:
                # Permission denied
                self.logger.error(f"{ICONS['cross']} Runware API authentication failed: Access forbidden")
                return False
            else:
                # Other error, but not necessarily auth-related
                self.logger.warning(f"{ICONS['warning']} Runware API test returned HTTP {response.status_code}, but auth may be OK")
                return True
                
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Runware API test failed: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get Runware service information"""
        return {
            "service": "Runware AI",
            "model": self.image_config["model"],
            "image_size": f"{self.image_config['width']}x{self.image_config['height']}",
            "style": self.image_config["style"][:50] + "..." if len(self.image_config["style"]) > 50 else self.image_config["style"],
            "steps": self.image_config["steps"],
            "guidance_scale": self.image_config["guidance_scale"],
            "sampler": self.image_config["sampler"]
        }
    
    def generate_image(self, prompt: str, filename: str, save_path: Optional[Path] = None) -> APIResponse:
        """
        Generate image using Runware AI
        
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
            
            # Generate unique task UUID
            task_uuid = str(uuid.uuid4())
            
            # Prepare request data in Runware's array format
            data = [{
                "taskType": "imageInference",
                "taskUUID": task_uuid,
                "positivePrompt": full_prompt,
                "negativePrompt": self.image_config.get("negative_prompt", ""),
                "model": self.image_config["model"],
                "width": self.image_config["width"],
                "height": self.image_config["height"],
                "steps": self.image_config["steps"],
                "CFGScale": self.image_config["guidance_scale"],
                "scheduler": self.image_config["sampler"],
                "outputType": self.image_config.get("output_type", "URL"),
                "outputFormat": self.image_config.get("output_format", "JPG"),
                "numberResults": self.image_config.get("number_results", 1)
            }]
            
            self.logger.info(f"{ICONS['gear']} Generating image: {filename}")
            self.logger.debug(f"Prompt: {prompt}")
            
            # Make API request to Runware
            response = self._make_request("POST", f"{self.base_url}/v1", json=data)
            
            if not response.success:
                return response
            
            # Extract image URL from response
            # Runware returns data in format: {"data": [result1, result2, ...]}
            if not response.data or 'data' not in response.data or len(response.data['data']) == 0:
                return APIResponse(success=False, error_message="No image data received from Runware")
            
            result = response.data['data'][0]
            if result.get("taskType") != "imageInference":
                error_msg = result.get("error", "Unknown error from Runware")
                return APIResponse(success=False, error_message=f"Runware generation failed: {error_msg}")
            
            # Handle different output types
            image_url = None
            if "imageURL" in result:
                image_url = result["imageURL"]
            elif "imageBase64" in result:
                # Handle base64 data (would need different processing)
                return APIResponse(success=False, error_message="Base64 image output not yet supported")
            elif "imageDataURI" in result:
                # Handle data URI (would need different processing)  
                return APIResponse(success=False, error_message="Data URI image output not yet supported")
            else:
                return APIResponse(success=False, error_message="No image data found in response")
            
            if not image_url:
                return APIResponse(success=False, error_message="No image URL in response")
            
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
            "model": self.image_config["model"],
            "images": num_images,
            "cost_per_image": f"${cost_per_image:.3f}",
            "total_cost": f"${total_cost:.3f}",
            "size": f"{self.image_config['width']}x{self.image_config['height']}",
            "steps": self.image_config["steps"],
            "guidance_scale": self.image_config["guidance_scale"]
        }