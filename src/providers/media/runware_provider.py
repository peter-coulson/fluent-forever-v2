"""
Runware Media Provider

Provides image generation using Runware AI API.
"""

import os
import uuid
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from utils.logging_config import get_logger, ICONS

logger = get_logger('providers.media.runware')


class RunwareMediaProvider(MediaProvider):
    """Runware AI-based media generation"""
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """Initialize Runware media provider
        
        Args:
            api_key: Runware API key (if None, loads from environment)
            config: Configuration dictionary (if None, loads from config.json)
        """
        if config is None:
            config = self._load_config()
        
        self.config = config
        self.api_config = config.get("apis", {}).get("runware", {})
        self.image_config = config.get("image_generation", {})
        
        # Load API key
        if api_key is not None:
            self.api_key = api_key
        else:
            env_var = self.api_config.get("env_var", "RUNWARE_API_KEY")
            self.api_key = os.getenv(env_var)
            if not self.api_key:
                # Don't raise error for testing - just log warning
                logger.warning(f"Runware API key not found in environment variable {env_var}")
                self.api_key = "test_key_for_validation"
        
        self.base_url = self.api_config.get("base_url", "https://api.runware.ai")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            config_path = Path(__file__).parent.parent.parent.parent / 'config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("config.json not found, using defaults")
                return {}
        except Exception as e:
            logger.warning(f"Error loading config: {e}, using defaults")
            return {}
    
    @property
    def supported_types(self) -> List[str]:
        """Runware supports image generation"""
        return ['image']
    
    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate image using Runware AI
        
        Args:
            request: MediaRequest with image generation parameters
            
        Returns:
            MediaResult with success status and file path
        """
        if request.type != 'image':
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Unsupported media type: {request.type}"
            )
        
        try:
            # Extract parameters
            filename = request.params.get('filename', 'generated_image.jpg')
            save_path = request.output_path or Path(self.config["paths"]["media_folder"]) / "images"
            
            # Construct full prompt with style
            style_prompt = self.image_config.get("style", "")
            if style_prompt:
                full_prompt = f"{style_prompt}. {request.content}"
            else:
                full_prompt = request.content
            
            # Generate unique task UUID
            task_uuid = str(uuid.uuid4())
            
            # Prepare request data in Runware's array format
            data = [{
                "taskType": "imageInference",
                "taskUUID": task_uuid,
                "positivePrompt": full_prompt,
                "negativePrompt": self.image_config.get("negative_prompt", ""),
                "model": self.image_config.get("model", "runware:101@1"),
                "width": self.image_config.get("width", 1024),
                "height": self.image_config.get("height", 1024),
                "steps": self.image_config.get("steps", 30),
                "CFGScale": self.image_config.get("guidance_scale", 7.5),
                "scheduler": self.image_config.get("sampler", "DPM++ 2M Karras"),
                "outputType": self.image_config.get("output_type", "URL"),
                "outputFormat": self.image_config.get("output_format", "JPG"),
                "numberResults": self.image_config.get("number_results", 1)
            }]
            
            logger.info(f"{ICONS['gear']} Generating image: {filename}")
            logger.debug(f"Prompt: {request.content}")
            
            # Make API request
            response = self._make_api_request(data)
            
            if not response.get('success', False):
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error=response.get('error', 'Unknown API error')
                )
            
            # Extract image URL from response
            response_data = response.get('data', {})
            if not response_data or 'data' not in response_data or len(response_data['data']) == 0:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="No image data received from Runware"
                )
            
            result = response_data['data'][0]
            if result.get("taskType") != "imageInference":
                error_msg = result.get("error", "Unknown error from Runware")
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error=f"Runware generation failed: {error_msg}"
                )
            
            # Handle different output types
            image_url = None
            if "imageURL" in result:
                image_url = result["imageURL"]
            elif "imageBase64" in result:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="Base64 image output not yet supported"
                )
            elif "imageDataURI" in result:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="Data URI image output not yet supported"
                )
            else:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="No image data found in response"
                )
            
            if not image_url:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="No image URL in response"
                )
            
            # Download and save image
            file_path = self._download_image(image_url, filename, save_path)
            
            if file_path:
                logger.info(f"{ICONS['check']} Image generated and saved: {filename}")
                return MediaResult(
                    success=True,
                    file_path=file_path,
                    metadata={
                        'model': data[0]['model'],
                        'size': f"{data[0]['width']}x{data[0]['height']}",
                        'steps': data[0]['steps'],
                        'guidance_scale': data[0]['CFGScale'],
                        'scheduler': data[0]['scheduler'],
                        'task_uuid': task_uuid,
                        'prompt': full_prompt
                    }
                )
            else:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="Failed to download generated image"
                )
            
        except Exception as e:
            error_msg = f"Failed to generate image {filename}: {e}"
            logger.error(f"{ICONS['cross']} {error_msg}")
            return MediaResult(
                success=False,
                file_path=None, 
                metadata={},
                error=error_msg
            )
    
    def _make_api_request(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make API request to Runware"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/v1",
                json=data,
                headers=headers,
                timeout=120  # Runware can be slow for complex images
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response.status_code == 401:
                return {'success': False, 'error': 'Invalid API key'}
            elif response.status_code == 403:
                return {'success': False, 'error': 'Access forbidden'}
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _download_image(self, image_url: str, filename: str, save_path: Path) -> Optional[Path]:
        """Download image from URL and save to file"""
        try:
            # Ensure directory exists
            save_path.mkdir(parents=True, exist_ok=True)
            file_path = save_path / filename
            
            # Download image
            logger.debug(f"Downloading image from: {image_url}")
            img_response = requests.get(image_url, timeout=30)
            
            if img_response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
                
                logger.debug(f"Image saved to: {file_path}")
                return file_path
            else:
                logger.error(f"Failed to download image (HTTP {img_response.status_code})")
                return None
                
        except Exception as e:
            logger.error(f"{ICONS['cross']} Error downloading image: {e}")
            return None
    
    def get_cost_estimate(self, requests: List[MediaRequest]) -> Dict[str, float]:
        """Estimate cost for Runware API calls
        
        Args:
            requests: List of image generation requests
            
        Returns:
            Cost breakdown dictionary
        """
        image_requests = [r for r in requests if r.type == 'image']
        num_images = len(image_requests)
        
        if num_images == 0:
            return {'total_cost': 0.0, 'breakdown': {}}
        
        cost_per_image = self.api_config.get("cost_per_image", 0.002)  # Default Runware price
        total_cost = num_images * cost_per_image
        
        return {
            'total_cost': total_cost,
            'breakdown': {
                'model': self.image_config.get("model", "runware:101@1"),
                'images': num_images,
                'cost_per_image': cost_per_image,
                'size': f"{self.image_config.get('width', 1024)}x{self.image_config.get('height', 1024)}",
                'steps': self.image_config.get('steps', 30)
            }
        }