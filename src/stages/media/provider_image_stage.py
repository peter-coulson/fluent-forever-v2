"""
Provider-based Image Generation Stage

Example stage that uses the provider system for image generation.
"""

from pathlib import Path
from typing import Any

from core.context import PipelineContext
from core.stages import StageResult, StageStatus
from providers.base.media_provider import MediaProvider, MediaRequest
from stages.base.api_stage import APIStage
from utils.logging_config import ICONS, get_logger

logger = get_logger("stages.media.provider_image")


class ProviderImageGenerationStage(APIStage):
    """Generate images using provider system"""

    def __init__(self, provider_key: str = "image", required: bool = True):
        """Initialize provider image generation stage

        Args:
            provider_key: Provider key in context (default: 'image')
            required: Whether provider is required
        """
        super().__init__(provider_key, required)

    @property
    def name(self) -> str:
        """Stage identifier"""
        return "provider_image_generation"

    @property
    def display_name(self) -> str:
        """Human-readable stage name"""
        return "Provider Image Generation"

    def execute_api_call(
        self, context: PipelineContext, provider: MediaProvider
    ) -> StageResult:
        """Execute image generation using provider

        Args:
            context: Pipeline context with image generation requests
            provider: Media provider instance

        Returns:
            Stage execution result with generated images
        """
        try:
            # Get image requests from context
            requests = context.get("image_requests", [])
            if not requests:
                return StageResult(
                    status=StageStatus.SUCCESS,
                    message="No image requests to process",
                    data={"generated_images": []},
                    errors=[],
                )

            # Validate provider supports images
            if not provider.supports_type("image"):
                return StageResult(
                    status=StageStatus.FAILURE,
                    message="Provider does not support image generation",
                    data={},
                    errors=[
                        f"Provider {self.provider_key} does not support 'image' type"
                    ],
                )

            # Process each request
            generated_images = []
            errors = []

            for i, request_data in enumerate(requests):
                try:
                    result = self._generate_single_image(
                        provider, request_data, context
                    )
                    if result["success"]:
                        generated_images.append(result)
                        self.logger.info(
                            f"{ICONS['check']} Generated image {i + 1}/{len(requests)}"
                        )
                    else:
                        errors.append(
                            f"Image {i + 1}: {result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    error_msg = f"Image {i + 1}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(f"{ICONS['cross']} {error_msg}")

            # Determine overall status
            success_count = len(generated_images)
            total_count = len(requests)

            if success_count == total_count:
                status = StageStatus.SUCCESS
                message = f"Generated {success_count} images successfully"
            elif success_count > 0:
                status = StageStatus.PARTIAL
                message = f"Generated {success_count}/{total_count} images"
            else:
                status = StageStatus.FAILURE
                message = "Failed to generate any images"

            # Store results in context
            context.set("generated_images", generated_images)

            return StageResult(
                status=status,
                message=message,
                data={
                    "generated_images": generated_images,
                    "success_count": success_count,
                    "total_count": total_count,
                    "provider_used": self.provider_key,
                },
                errors=errors,
            )

        except Exception as e:
            error_msg = f"Image generation stage failed: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=error_msg,
                data={},
                errors=[error_msg],
            )

    def _generate_single_image(
        self,
        provider: MediaProvider,
        request_data: dict[str, Any],
        context: PipelineContext,
    ) -> dict[str, Any]:
        """Generate a single image

        Args:
            provider: Media provider
            request_data: Image request data
            context: Pipeline context

        Returns:
            Result dictionary
        """
        # Extract request parameters
        prompt = request_data.get("prompt", "")
        filename = request_data.get("filename", "generated_image.jpg")
        card_id = request_data.get("card_id", "unknown")

        if not prompt:
            return {"success": False, "error": "No prompt provided", "card_id": card_id}

        # Determine output path
        output_path = None
        if "output_path" in request_data:
            output_path = Path(request_data["output_path"])
        elif context.get("media_output_path"):
            output_path = Path(context.get("media_output_path"))

        # Create media request
        media_request = MediaRequest(
            type="image",
            content=prompt,
            params={
                "filename": filename,
                "card_id": card_id,
                **request_data.get("params", {}),
            },
            output_path=output_path,
        )

        # Generate image
        result = provider.generate_media(media_request)

        if result.success:
            return {
                "success": True,
                "card_id": card_id,
                "filename": filename,
                "file_path": str(result.file_path) if result.file_path else None,
                "prompt": prompt,
                "metadata": result.metadata,
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "card_id": card_id,
                "filename": filename,
                "prompt": prompt,
            }
