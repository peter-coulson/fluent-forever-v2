"""
Media Provider Interface

Abstract interface for media generation (images, audio, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.logging_config import ICONS, get_logger


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


@dataclass
class MediaResult:
    """Result of media generation"""

    success: bool
    file_path: Path | None
    metadata: dict[str, Any]
    error: str | None = None

    def __post_init__(self) -> None:
        """Validate result after initialization"""
        pass


class MediaProvider(ABC):
    """Abstract interface for media generation"""

    def __init__(self) -> None:
        self.logger = get_logger(f"providers.media.{self.__class__.__name__.lower()}")

    @property
    @abstractmethod
    def supported_types(self) -> list[str]:
        """List of supported media types ('image', 'audio', etc.)

        Returns:
            List of media types this provider can generate
        """
        pass

    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate media from request

        Args:
            request: MediaRequest specifying what to generate

        Returns:
            MediaResult with success status and file path if successful
        """
        self.logger.info(
            f"{ICONS['search']} Requesting {request.type} for: {request.content}"
        )

        if not self.validate_request(request):
            self.logger.error(
                f"{ICONS['cross']} Invalid request for {request.type}: {request.content}"
            )
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Request not supported by {self.__class__.__name__}",
            )

        try:
            # Before API call
            self.logger.debug(f"Making API request for {request.type}...")
            result = self._generate_media_impl(request)

            if result.success:
                self.logger.info(
                    f"{ICONS['check']} {request.type.capitalize()} generated successfully"
                )
            else:
                self.logger.error(
                    f"{ICONS['cross']} {request.type.capitalize()} generation failed: {result.error}"
                )

            return result
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Media request failed: {e}")
            return MediaResult(success=False, file_path=None, metadata={}, error=str(e))

    @abstractmethod
    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """Implementation-specific media generation"""
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
