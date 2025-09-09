"""
API Stage Base

Base class for stages that interact with external APIs and services.
"""

from abc import abstractmethod
from typing import Any

from core.context import PipelineContext
from core.stages import Stage, StageResult, StageStatus
from utils.logging_config import ICONS, get_logger


class APIStage(Stage):
    """Base class for external API operations"""

    def __init__(self, provider_key: str, required: bool = True):
        """
        Initialize API stage

        Args:
            provider_key: Key for provider in context (e.g. 'image_provider')
            required: Whether the provider must be available
        """
        self.provider_key = provider_key
        self.required = required
        self.logger = get_logger(f"stages.api.{self.__class__.__name__.lower()}")

    def execute(self, context: PipelineContext) -> StageResult:
        """Execute API stage with provider from context"""
        # Get provider from context
        provider = context.get(f"providers.{self.provider_key}")
        if not provider and self.required:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Provider {self.provider_key} not available",
                data={},
                errors=[f"Missing required provider: {self.provider_key}"],
            )
        elif not provider:
            # Optional provider not available
            self.logger.info(
                f"{ICONS['info']} Provider {self.provider_key} not available, skipping"
            )
            return StageResult(
                status=StageStatus.SUCCESS,
                message=f"Provider {self.provider_key} not available, skipped",
                data={},
                errors=[],
            )

        try:
            return self.execute_api_call(context, provider)
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} API call failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"API call failed: {e}",
                data={},
                errors=[f"API error: {e}"],
            )

    @abstractmethod
    def execute_api_call(self, context: PipelineContext, provider: Any) -> StageResult:
        """
        Execute the API call with provider

        Args:
            context: Pipeline context
            provider: API provider instance

        Returns:
            Stage execution result
        """
        pass
