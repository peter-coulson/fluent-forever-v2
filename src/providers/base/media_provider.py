"""
Media Provider Interface

Abstract interface for media generation (images, audio, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MediaRequest:
    """Request for media generation"""

    type: str  # 'image' or 'audio'
    content: str  # Prompt for images, text for audio
    params: dict[str, Any]  # Provider-specific parameters
    output_path: Path | None = None

    def __post_init__(self) -> None:
        """Validate request after initialization"""
        if not self.type:
            raise ValueError("Media request type cannot be empty")
        if not self.content:
            raise ValueError("Media request content cannot be empty")
        if self.params is None:
            self.params = {}


@dataclass
class MediaResult:
    """Result of media generation"""

    success: bool
    file_path: Path | None
    metadata: dict[str, Any]
    error: str | None = None

    def __post_init__(self) -> None:
        """Validate result after initialization"""
        if self.metadata is None:
            self.metadata = {}


class MediaProvider(ABC):
    """Abstract interface for media generation"""

    @property
    @abstractmethod
    def supported_types(self) -> list[str]:
        """List of supported media types ('image', 'audio', etc.)

        Returns:
            List of media types this provider can generate
        """
        pass

    @abstractmethod
    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate media from request

        Args:
            request: MediaRequest specifying what to generate

        Returns:
            MediaResult with success status and file path if successful
        """
        pass

    @abstractmethod
    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        """Get cost estimate for batch of requests

        Args:
            requests: List of media requests to estimate cost for

        Returns:
            Dictionary with cost breakdown and totals
        """
        pass

    def supports_type(self, media_type: str) -> bool:
        """Check if provider supports media type

        Args:
            media_type: Media type to check ('image', 'audio', etc.)

        Returns:
            True if provider supports this media type
        """
        return media_type in self.supported_types

    def validate_request(self, request: MediaRequest) -> bool:
        """Validate that request is supported by this provider

        Args:
            request: MediaRequest to validate

        Returns:
            True if request is valid and supported
        """
        return self.supports_type(request.type)

    # Convenience methods for specific media types
    def generate_image(self, prompt: str, **kwargs: Any) -> MediaResult:
        """Generate image (convenience method)

        Args:
            prompt: Image description
            **kwargs: Additional parameters

        Returns:
            MediaResult for image generation
        """
        request = MediaRequest(type="image", content=prompt, params=kwargs)
        return self.generate_media(request)

    def generate_audio(self, text: str, **kwargs: Any) -> MediaResult:
        """Generate audio (convenience method)

        Args:
            text: Text to synthesize or word to get pronunciation
            **kwargs: Additional parameters

        Returns:
            MediaResult for audio generation
        """
        request = MediaRequest(type="audio", content=text, params=kwargs)
        return self.generate_media(request)
