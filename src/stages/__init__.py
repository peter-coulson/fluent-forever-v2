"""
Stages Module - Pluggable Processing Stages

This module provides a library of reusable processing stages that can be
mixed and matched across different pipelines. Stages handle common operations
like file I/O, validation, API calls, and media generation.

Usage:
    from stages import get_stage, list_stages

    # Get a specific stage instance
    stage = get_stage('validate_data', data_key='cards')

    # List all available stages
    available = list_stages()
"""

from typing import Dict, List, Type

from core.stages import Stage

from .base.api_stage import APIStage

# Import all stage classes
from .base.file_stage import FileLoadStage, FileSaveStage
from .base.validation_stage import ValidationStage
from .claude.analysis_stage import WordAnalysisStage
from .claude.batch_stage import BatchPreparationStage
from .claude.ingestion_stage import BatchIngestionStage
from .media.audio_stage import AudioGenerationStage
from .media.image_stage import ImageGenerationStage
from .media.media_stage import MediaGenerationStage
from .sync.card_stage import CardSyncStage
from .sync.media_sync_stage import MediaSyncStage
from .sync.template_stage import TemplateSyncStage
from .validation.data_stage import DataValidationStage
from .validation.ipa_stage import IPAValidationStage
from .validation.media_stage import MediaValidationStage

# Stage registry for easy lookup
STAGE_REGISTRY: dict[str, type[Stage]] = {
    "analyze_words": WordAnalysisStage,
    "prepare_batch": BatchPreparationStage,
    "ingest_batch": BatchIngestionStage,
    "generate_images": ImageGenerationStage,
    "generate_audio": AudioGenerationStage,
    "generate_media": MediaGenerationStage,
    "sync_templates": TemplateSyncStage,
    "sync_cards": CardSyncStage,
    "sync_media": MediaSyncStage,
    "validate_data": DataValidationStage,
    "validate_ipa": IPAValidationStage,
    "validate_media": MediaValidationStage,
    "load_file": FileLoadStage,
    "save_file": FileSaveStage,
}


def get_stage(stage_name: str, **kwargs) -> Stage:
    """Get stage instance by name"""
    if stage_name not in STAGE_REGISTRY:
        raise ValueError(
            f"Unknown stage: {stage_name}. Available stages: {list(STAGE_REGISTRY.keys())}"
        )

    stage_class = STAGE_REGISTRY[stage_name]
    return stage_class(**kwargs)


def list_stages() -> list[str]:
    """List all available stage names"""
    return list(STAGE_REGISTRY.keys())


def get_stage_info(stage_name: str) -> dict[str, str]:
    """Get information about a specific stage"""
    if stage_name not in STAGE_REGISTRY:
        raise ValueError(f"Unknown stage: {stage_name}")

    stage_class = STAGE_REGISTRY[stage_name]
    return {
        "name": stage_name,
        "class": stage_class.__name__,
        "module": stage_class.__module__,
        "docstring": stage_class.__doc__ or "No description available",
    }


# Export the main interface
__all__ = ["get_stage", "list_stages", "get_stage_info", "STAGE_REGISTRY"]
