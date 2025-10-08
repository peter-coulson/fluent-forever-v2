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
    output_path: Path  # Mandatory output path for generated media

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
    """Abstract interface for media generation with configuration injection.

    This class provides a standardized interface for media generation services
    (images, audio, etc.) with constructor-based configuration injection and
    fail-fast validation patterns.

    The configuration flow follows this pattern:
    1. Constructor accepts optional config dictionary
    2. Config is validated through abstract validate_config() method (fail-fast)
    3. Provider is set up using _setup_from_config() method
    4. Provider is ready for use

    Concrete providers must implement:
    - validate_config(): Provider-specific configuration validation
    - supported_types: List of media types this provider supports
    - _generate_media_impl(): Core media generation logic
    - get_cost_estimate(): Cost estimation for batch requests
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize provider with configuration injection.

        Args:
            config: Provider-specific configuration dict. If None, defaults to empty dict.
                   Configuration is validated immediately to fail fast on invalid setup.

        Raises:
            ValueError: If configuration is invalid (raised by validate_config)
            KeyError: If required configuration keys are missing (raised by validate_config)
        """
        self.config = config or {}
        self.logger = get_logger(f"providers.media.{self.__class__.__name__.lower()}")

        # Fail-fast validation pattern - validate config before proceeding
        self.validate_config(self.config)

        # Setup provider from validated configuration
        self._setup_from_config()

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
    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate provider-specific configuration (fail-fast pattern).

        This method implements fail-fast validation of provider configuration.
        It should check all required configuration keys and validate their values
        to ensure the provider can operate correctly.

        The validation should be strict and explicit:
        - Check for required keys and raise KeyError if missing
        - Validate value types and formats, raise ValueError if invalid
        - No silent fallbacks or default substitutions
        - Clear, helpful error messages that guide user to fix issues

        Example implementation pattern:
            ```python
            def validate_config(self, config: dict[str, Any]) -> None:
                if "api_key" not in config or not config["api_key"]:
                    raise ValueError("Missing required config key: api_key")

                if "model" in config and config["model"] not in ["valid-model-1", "valid-model-2"]:
                    raise ValueError(f"Invalid model: {config['model']}")
            ```

        Args:
            config: Configuration dictionary to validate. May be empty dict
                   for backward compatibility with existing providers.

        Raises:
            ValueError: If configuration values are invalid (wrong type, format, etc.)
            KeyError: If required configuration keys are missing
        """
        pass

    def _setup_from_config(self) -> None:  # noqa: B027
        """Setup provider from validated configuration.

        This method is called after configuration validation and should initialize
        any provider-specific state based on the validated configuration.

        The default implementation is a no-op. Override in concrete providers
        that need configuration-based initialization (e.g., setting up API clients,
        configuring rate limiters, initializing caches).

        Note:
            This method is only called if validate_config() passes successfully,
            ensuring that configuration is valid before setup begins.
        """
        # Default no-op implementation - override in concrete providers if needed

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

    def generate_batch(self, requests: list[MediaRequest]) -> list[MediaResult]:
        """Generate media for batch requests with rate limiting

        This method processes multiple media requests efficiently, applying rate limiting
        and error handling. The default implementation processes requests sequentially
        with rate limiting between requests.

        Concrete providers can override this method to implement more efficient
        batch processing (e.g., parallel processing, bulk API calls).

        Args:
            requests: List of MediaRequest objects to process

        Returns:
            List of MediaResult objects corresponding to each request
        """
        return self._default_batch_implementation(requests)

    def _default_batch_implementation(
        self, requests: list[MediaRequest]
    ) -> list[MediaResult]:
        """Default sequential batch processing with rate limiting

        This method provides a default implementation for batch processing that:
        1. Processes requests sequentially to maintain order
        2. Applies rate limiting between requests if configured
        3. Handles individual failures gracefully
        4. Preserves request-to-result correspondence

        Args:
            requests: List of MediaRequest objects to process

        Returns:
            List of MediaResult objects, one for each input request
        """
        import time

        results = []
        for i, request in enumerate(requests):
            # Apply rate limiting (skip delay for first request)
            if (
                i > 0
                and hasattr(self, "_rate_limit_delay")
                and self._rate_limit_delay > 0
            ):
                time.sleep(self._rate_limit_delay)

            # Process individual request
            result = self.generate_media(request)
            results.append(result)

        return results

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
    def generate_image(
        self, prompt: str, output_path: Path, **kwargs: Any
    ) -> MediaResult:
        """Generate image (convenience method)

        Args:
            prompt: Image description
            output_path: Path where generated image will be saved
            **kwargs: Additional parameters

        Returns:
            MediaResult for image generation
        """
        request = MediaRequest(
            type="image", content=prompt, params=kwargs, output_path=output_path
        )
        return self.generate_media(request)

    def generate_audio(
        self, text: str, output_path: Path, **kwargs: Any
    ) -> MediaResult:
        """Generate audio (convenience method)

        Args:
            text: Text to synthesize or word to get pronunciation
            output_path: Path where generated audio will be saved
            **kwargs: Additional parameters

        Returns:
            MediaResult for audio generation
        """
        request = MediaRequest(
            type="audio", content=text, params=kwargs, output_path=output_path
        )
        return self.generate_media(request)
