#!/usr/bin/env python3
"""
OpenAI Media Provider
Clean implementation for OpenAI DALL-E image generation with config injection
"""

import re
from pathlib import Path
from typing import Any

from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult


class OpenAIProvider(MediaProvider):
    """Clean OpenAI media provider for image generation using DALL-E"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize provider with config injection"""
        super().__init__(config)

    @property
    def supported_types(self) -> list[str]:
        """Media types supported by OpenAI provider"""
        return ["image"]

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate OpenAI provider configuration with fail-fast pattern"""
        required_keys = ["api_key", "model"]
        for key in required_keys:
            if key not in config or not config[key]:
                raise ValueError(f"Missing required OpenAI config key: {key}")

        # Validate model
        valid_models = ["dall-e-2", "dall-e-3"]
        if config["model"] not in valid_models:
            raise ValueError(
                f"Invalid model: {config['model']}. Must be one of: {valid_models}"
            )

    def _setup_from_config(self) -> None:
        """Setup provider from validated configuration"""
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]

        # Initialize OpenAI client
        self.client = self._create_openai_client()

        # Set default rate limits based on OpenAI API limits
        # DALL-E: 5 images per minute for standard tier
        default_rate_limit = (
            4.0 if self.model == "dall-e-3" else 4.0
        )  # 15 requests/minute = 4s delay
        self._rate_limit_delay = self.config.get("rate_limit_delay", default_rate_limit)

    def _create_openai_client(self) -> Any | None:
        """Create OpenAI client, handling import errors gracefully"""
        try:
            import openai  # type: ignore[import-not-found]

            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            # For testing or when OpenAI is not installed
            return None

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """Generate image using DALL-E API"""
        if request.type != "image":
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Unsupported media type: {request.type}. OpenAI provider only supports 'image'.",
            )

        try:
            # Prepare API parameters
            api_params = {"model": self.model, "prompt": request.content, "n": 1}

            # Add model-specific parameters
            if "size" in request.params:
                api_params["size"] = request.params["size"]

            if "quality" in request.params and self.model == "dall-e-3":
                api_params["quality"] = request.params["quality"]

            if "style" in request.params and self.model == "dall-e-3":
                api_params["style"] = request.params["style"]

            # Make API call
            if self.client:
                response = self.client.images.generate(**api_params)
                image_url = response.data[0].url
                revised_prompt = getattr(response.data[0], "revised_prompt", None)
            else:
                # Mock response for testing
                image_url = "https://example.com/generated_image.jpg"
                revised_prompt = None

            # Download image
            file_path = self._download_image(image_url, request.output_path)

            # Prepare metadata
            metadata = {
                "model": self.model,
                "prompt": request.content,
                "image_url": image_url,
            }

            # Add request parameters to metadata
            for key in ["size", "quality", "style"]:
                if key in request.params:
                    metadata[key] = request.params[key]

            # Add revised prompt for DALL-E 3
            if revised_prompt:
                metadata["revised_prompt"] = revised_prompt

            return MediaResult(success=True, file_path=file_path, metadata=metadata)

        except Exception as e:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={"model": self.model, "prompt": request.content},
                error=str(e),
            )

    def _download_image(self, url: str, output_path: Path | None = None) -> Path:
        """Download image from URL"""
        import requests

        if output_path is None:
            # Generate safe filename from prompt
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", str(hash(url))[:8])
            output_path = Path(f"media/images/openai_{safe_name}.jpg")

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the image
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        """Get cost estimate for batch of requests"""
        # Filter for supported requests
        supported_requests = [
            req for req in requests if req.type in self.supported_types
        ]

        # DALL-E pricing (as of 2024)
        if self.model == "dall-e-3":
            # DALL-E 3: $0.04 per image (1024×1024 standard)
            # Quality "hd" costs $0.08 per image
            base_cost = 0.04
            total_cost = 0.0
            for req in supported_requests:
                cost = base_cost
                if req.params.get("quality") == "hd":
                    cost = 0.08
                total_cost += cost
            per_request = (
                total_cost / len(supported_requests) if supported_requests else 0.0
            )
        else:
            # DALL-E 2: $0.02 per image (1024×1024)
            per_request = 0.02
            total_cost = per_request * len(supported_requests)

        return {
            "total_cost": total_cost,
            "per_request": per_request,
            "requests_count": len(supported_requests),
        }
