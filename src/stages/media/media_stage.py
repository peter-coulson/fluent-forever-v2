"""
Combined Media Generation Stage

Orchestrates both image and audio generation in a single stage.
"""

from src.core.context import PipelineContext
from src.core.stages import Stage, StageResult, StageStatus
from src.utils.logging_config import ICONS, get_logger

from .audio_stage import AudioGenerationStage
from .image_stage import ImageGenerationStage


class MediaGenerationStage(Stage):
    """Generate both images and audio"""

    def __init__(
        self,
        max_new: int = 5,
        skip_images: bool = False,
        skip_audio: bool = False,
        force_regenerate: bool = False,
    ):
        """
        Initialize combined media generation stage

        Args:
            max_new: Maximum new media items to generate total
            skip_images: Skip image generation
            skip_audio: Skip audio generation
            force_regenerate: Force regenerate images even if prompt hash changed
        """
        self.max_new = max_new
        self.skip_images = skip_images
        self.skip_audio = skip_audio
        self.force_regenerate = force_regenerate
        self.logger = get_logger("stages.media.combined")

        # Create sub-stages
        if not skip_images:
            self.image_stage = ImageGenerationStage(
                max_new=max_new, force_regenerate=force_regenerate
            )
        if not skip_audio:
            self.audio_stage = AudioGenerationStage(max_new=max_new)

    @property
    def name(self) -> str:
        return "generate_media"

    @property
    def display_name(self) -> str:
        return "Generate Media (Images & Audio)"

    @property
    def dependencies(self) -> list[str]:
        return []  # Can run independently

    def execute(self, context: PipelineContext) -> StageResult:
        """Execute both image and audio generation"""
        results = {
            "image_result": None,
            "audio_result": None,
            "total_generated": 0,
            "total_skipped": 0,
            "total_failed": 0,
        }
        errors = []

        # Execute image generation
        if not self.skip_images:
            try:
                image_result = self.image_stage.execute(context)
                results["image_result"] = image_result

                if image_result.status != StageStatus.FAILURE:
                    data = image_result.data
                    results["total_generated"] += data.get("generated", 0)
                    results["total_skipped"] += data.get("skipped", 0)
                    results["total_failed"] += data.get("failed", 0)

                errors.extend(image_result.errors)

            except Exception as e:
                error_msg = f"Image generation stage failed: {e}"
                errors.append(error_msg)
                self.logger.error(f"{ICONS['cross']} {error_msg}")

        # Execute audio generation
        if not self.skip_audio:
            try:
                audio_result = self.audio_stage.execute(context)
                results["audio_result"] = audio_result

                if audio_result.status != StageStatus.FAILURE:
                    data = audio_result.data
                    results["total_generated"] += data.get("generated", 0)
                    results["total_skipped"] += data.get("skipped", 0)
                    results["total_failed"] += data.get("failed", 0)

                errors.extend(audio_result.errors)

            except Exception as e:
                error_msg = f"Audio generation stage failed: {e}"
                errors.append(error_msg)
                self.logger.error(f"{ICONS['cross']} {error_msg}")

        # Determine overall status
        image_ok = self.skip_images or (
            results["image_result"]
            and results["image_result"].status != StageStatus.FAILURE
        )
        audio_ok = self.skip_audio or (
            results["audio_result"]
            and results["audio_result"].status != StageStatus.FAILURE
        )

        if not image_ok or not audio_ok:
            status = StageStatus.FAILURE
        elif results["total_failed"] > 0:
            status = StageStatus.PARTIAL
        else:
            status = StageStatus.SUCCESS

        # Create summary message
        parts = []
        if results["total_generated"] > 0:
            parts.append(f"generated {results['total_generated']}")
        if results["total_skipped"] > 0:
            parts.append(f"skipped {results['total_skipped']}")
        if results["total_failed"] > 0:
            parts.append(f"failed {results['total_failed']}")

        if parts:
            message = f"Media generation completed: {', '.join(parts)}"
        else:
            message = "No media generation needed"

        # Store combined results in context
        context.set("media_generation_results", results)

        self.logger.info(f"{ICONS['check']} {message}")

        return StageResult(status=status, message=message, data=results, errors=errors)
