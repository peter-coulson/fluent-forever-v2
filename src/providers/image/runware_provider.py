#!/usr/bin/env python3
"""
Runware Media Provider
Clean implementation for Runware AI image generation with config injection
"""

import json
import re
import time
from pathlib import Path
from typing import Any

import requests

from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult


class RunwareError(Exception):
    """Base Runware provider error"""


class RunwareAuthError(RunwareError):
    """Authentication/authorization error"""


class RunwareRateLimitError(RunwareError):
    """Rate limit exceeded error"""


class RunwareGenerationError(RunwareError):
    """Image generation failed error"""


class RunwareProvider(MediaProvider):
    """Clean Runware media provider for AI image generation"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize provider with config injection"""
        super().__init__(config)

    @property
    def supported_types(self) -> list[str]:
        """Media types supported by Runware provider"""
        return ["image"]

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate Runware provider configuration with fail-fast pattern"""
        required_keys = ["api_key"]
        for key in required_keys:
            if key not in config or not config[key]:
                raise ValueError(f"Missing required Runware config key: {key}")

        # Validate model format if provided
        if "model" in config and not self._is_valid_model(config["model"]):
            raise ValueError(f"Invalid Runware model format: {config['model']}")

        # Validate image size format if provided
        if "image_size" in config and not self._is_valid_size(config["image_size"]):
            raise ValueError(f"Invalid image size format: {config['image_size']}")

    def _setup_from_config(self) -> None:
        """Setup provider from validated configuration"""
        self.api_key = self.config["api_key"]
        self.model = self.config.get("model", "runware:100@1")
        self.image_size = self.config.get("image_size", "512x512")
        self.steps = self.config.get("steps", 20)
        self.guidance = self.config.get("guidance", 7)
        self._rate_limit_delay = self.config.get("rate_limit_delay", 1.0)
        self.timeout = self.config.get("timeout", 30)
        self.batch_size = self.config.get("batch_size", 4)

        # Prepare API session
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        # Base API URL
        self.api_base_url = "https://api.runware.ai/v1"

    def _is_valid_model(self, model: str) -> bool:
        """Validate Runware model format"""
        # Pattern: "runware:ID@version" or similar formats
        pattern = r"^[a-zA-Z0-9]+:[a-zA-Z0-9]+@[a-zA-Z0-9]+$"
        return bool(re.match(pattern, model))

    def _is_valid_size(self, size: str) -> bool:
        """Validate image size format"""
        # Pattern: "WIDTHxHEIGHT"
        pattern = r"^\d+x\d+$"
        return bool(re.match(pattern, size))

    def __repr__(self) -> str:
        """String representation with masked API key"""
        masked_key = f"{self.api_key[:8]}***" if len(self.api_key) > 8 else "***"
        return f"RunwareProvider(api_key={masked_key}, model={self.model})"

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """Generate image using Runware API"""
        if request.type != "image":
            raise ValueError(
                f"RunwareProvider only supports image generation, got: {request.type}"
            )

        # Validate prompt
        if not request.content or request.content.strip() == "":
            raise ValueError("Prompt cannot be empty")

        try:
            # Make API request
            api_response = self._make_api_request(request.content, **request.params)

            # Extract image URL from response
            image_url = api_response["data"]["imageUrl"]

            # Use provided output path
            file_path = request.output_path

            # Download image
            success = self._download_image(image_url, file_path)
            if not success:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="Failed to download generated image",
                )

            # Validate downloaded file
            if not self._validate_downloaded_file(file_path):
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error="Downloaded image validation failed",
                )

            # Extract metadata
            metadata = self._extract_metadata(api_response, request.content)

            return MediaResult(
                success=True, file_path=file_path, metadata=metadata, error=None
            )

        except RunwareAuthError as e:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Authentication error: {str(e)}",
            )
        except RunwareRateLimitError as e:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Rate limit exceeded: {str(e)}",
            )
        except RunwareGenerationError as e:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Image generation failed: {str(e)}",
            )
        except requests.Timeout:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error="Request timeout occurred",
            )
        except json.JSONDecodeError as e:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Invalid JSON response: {str(e)}",
            )
        except Exception as e:
            return MediaResult(success=False, file_path=None, metadata={}, error=str(e))

    def _make_api_request(self, prompt: str, **params: Any) -> dict[Any, Any]:
        """Make API request with retry logic"""
        # Prepare API parameters
        api_params = {
            "model": self.model,
            "prompt": prompt,
            "width": int(self.image_size.split("x")[0]),
            "height": int(self.image_size.split("x")[1]),
            "steps": self.steps,
            "guidance": self.guidance,
        }

        # Override with request-specific parameters
        if "width" in params:
            api_params["width"] = params["width"]
        if "height" in params:
            api_params["height"] = params["height"]
        if "steps" in params:
            api_params["steps"] = params["steps"]
        if "guidance" in params:
            api_params["guidance"] = params["guidance"]

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self._session.post(
                    f"{self.api_base_url}/generate",
                    json=api_params,
                    timeout=self.timeout,
                )

                # Handle HTTP errors
                if response.status_code == 401:
                    raise RunwareAuthError("Invalid API key or unauthorized access")
                elif response.status_code == 429:
                    raise RunwareRateLimitError("API rate limit exceeded")
                elif response.status_code >= 500:
                    # Always call raise_for_status first to maintain compatibility with mocks
                    try:
                        response.raise_for_status()
                    except requests.HTTPError as e:
                        if attempt < max_retries - 1:
                            # Exponential backoff: 1s, 2s, 4s
                            delay = 2**attempt
                            time.sleep(delay)
                            continue
                        else:
                            raise RunwareGenerationError(
                                f"Server error: {str(e)}"
                            ) from e
                else:
                    response.raise_for_status()

                # Parse response
                json_response: dict[Any, Any] = response.json()
                return json_response

            except requests.HTTPError as e:
                # Handle HTTPError from raise_for_status()
                if "500" in str(e):
                    if attempt < max_retries - 1:
                        delay = 2**attempt
                        time.sleep(delay)
                        continue
                    else:
                        raise RunwareGenerationError(f"Server error: {str(e)}") from e
                else:
                    raise RunwareGenerationError(f"HTTP error: {str(e)}") from e
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < max_retries - 1:
                    delay = 2**attempt
                    time.sleep(delay)
                    continue
                else:
                    raise e

        # Should not reach here
        raise RunwareError("Max retries exceeded")

    def _download_image(self, image_url: str, file_path: Path) -> bool:
        """Download and validate generated image"""
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Download the image
            response = self._session.get(image_url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            # Verify content type
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                return False

            # Write image data
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except Exception:
            return False

    def _validate_downloaded_file(self, file_path: Path) -> bool:
        """Validate downloaded image file"""
        try:
            if not file_path.exists():
                return False

            # Check file size (should be reasonable)
            file_size = file_path.stat().st_size
            if file_size < 100:  # Too small
                return False
            if file_size > 50 * 1024 * 1024:  # Too large (>50MB)
                return False

            return True

        except Exception:
            return False

    def _extract_metadata(self, api_response: dict, prompt: str) -> dict:
        """Extract metadata from API response"""
        metadata = {
            "prompt": prompt,
            "model": self.model,
            "image_size": self.image_size,
            "steps": self.steps,
            "guidance": self.guidance,
            "generation_time": time.time(),
        }

        # Add response-specific metadata
        if "data" in api_response:
            data = api_response["data"]
            if "taskId" in data:
                metadata["task_id"] = data["taskId"]
            if "seed" in data:
                metadata["seed"] = data["seed"]
            if "model" in data:
                metadata["model"] = data["model"]
            if "steps" in data:
                metadata["steps"] = data["steps"]
            if "guidance" in data:
                metadata["guidance"] = data["guidance"]

        return metadata

    def generate_batch(self, requests: list[MediaRequest]) -> list[MediaResult]:
        """Generate images for batch requests with rate limiting and chunking"""
        # Process in chunks to respect batch size limits
        chunk_size = self.batch_size
        all_results = []

        for i in range(0, len(requests), chunk_size):
            chunk = requests[i : i + chunk_size]
            chunk_results = self._default_batch_implementation(chunk)
            all_results.extend(chunk_results)

        return all_results

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        """Get cost estimate for batch of requests"""
        # Filter for supported requests
        supported_requests = [
            req for req in requests if req.type in self.supported_types
        ]

        # Runware pricing (example - adjust based on actual pricing)
        # Assuming $0.01 per image as a competitive rate
        per_request = 0.01
        total_cost = per_request * len(supported_requests)

        return {
            "total_cost": total_cost,
            "per_request": per_request,
            "requests_count": len(supported_requests),
        }
